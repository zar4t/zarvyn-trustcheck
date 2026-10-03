"""Evaluate a documented subset, never claim effective AWS authorization."""
import re

PREFIX = 'token.actions.githubusercontent.com:'
KEYS = {PREFIX + 'sub', PREFIX + 'aud'}
PROVIDER = re.compile(r'arn:aws:iam::[0-9]{12}:oidc-provider/token\.actions\.githubusercontent\.com\Z')


def strings(value):
    values = [value] if isinstance(value, str) else value
    if not isinstance(values, list) or not values or not all(isinstance(x, str) and x for x in values):
        raise ValueError('Expected a nonempty string or list of nonempty strings')
    if any('${' in x for x in values):
        raise ValueError('Policy variables are not supported')
    return values


def validate_policy(policy):
    if not isinstance(policy, dict) or set(policy) - {'Version', 'Id', 'Statement'}:
        raise ValueError('Unsupported policy structure')
    if policy.get('Version') != '2012-10-17':
        raise ValueError('Only policy version 2012-10-17 is supported')
    if 'Id' in policy and not isinstance(policy['Id'], str):
        raise ValueError('Id must be a string')
    statements = policy.get('Statement')
    if isinstance(statements, dict):
        statements = [statements]
    if not isinstance(statements, list) or not statements:
        raise ValueError('A nonempty Statement collection is required')
    for s in statements:
        if not isinstance(s, dict) or set(s) - {'Sid', 'Effect', 'Principal', 'Action', 'Condition'}:
            raise ValueError('Unsupported statement field (including NotAction/NotPrincipal)')
        if 'Sid' in s and not isinstance(s['Sid'], str):
            raise ValueError('Sid must be a string')
        if s.get('Effect') not in ('Allow', 'Deny'):
            raise ValueError('Effect must be Allow or Deny')
        if strings(s.get('Action')) != ['sts:AssumeRoleWithWebIdentity']:
            raise ValueError('Only the exact sts:AssumeRoleWithWebIdentity action is supported')
        p = s.get('Principal')
        if not isinstance(p, dict) or set(p) != {'Federated'}:
            raise ValueError('Only an explicit Federated GitHub OIDC principal is supported')
        if not all(PROVIDER.fullmatch(x) for x in strings(p['Federated'])):
            raise ValueError('Only exact GitHub OIDC provider ARNs in the aws partition are supported')
        conditions = s.get('Condition', {})
        if not isinstance(conditions, dict):
            raise ValueError('Condition must be an object')
        for op, entries in conditions.items():
            if op not in ('StringEquals', 'StringLike') or not isinstance(entries, dict) or not entries:
                raise ValueError('Only nonempty StringEquals and StringLike conditions are supported')
            for key, value in entries.items():
                if key not in KEYS:
                    raise ValueError('Only GitHub OIDC sub and aud condition keys are supported')
                strings(value)
    return statements


def wildcard(pattern, value):
    # IAM string wildcards are * and ?, not shell bracket expressions.
    expr = ''.join('.*' if c == '*' else '.' if c == '?' else re.escape(c) for c in pattern)
    return re.fullmatch(expr, value, flags=re.DOTALL) is not None


def evaluate(policy, provider, claims):
    try:
        statements = validate_policy(policy)
    except ValueError as exc:
        return {'decision': 'UNKNOWN', 'reason': str(exc), 'matched': []}
    if not isinstance(provider, str) or not PROVIDER.fullmatch(provider):
        return {'decision': 'UNKNOWN', 'reason': 'Invalid or unsupported scenario provider', 'matched': []}
    if not isinstance(claims, dict) or set(claims) != {'sub', 'aud'} or not all(isinstance(v, str) and v for v in claims.values()):
        return {'decision': 'UNKNOWN', 'reason': 'Scenario must supply nonempty string sub and aud', 'matched': []}
    matched = []
    for index, s in enumerate(statements):
        if provider not in strings(s['Principal']['Federated']):
            continue
        matches = True
        for op, entries in s.get('Condition', {}).items():
            for key, wanted in entries.items():
                actual = claims[key.removeprefix(PREFIX)]
                check = (lambda p: p == actual) if op == 'StringEquals' else (lambda p: wildcard(p, actual))
                matches = matches and any(check(p) for p in strings(wanted))
        if matches:
            matched.append({'index': index, 'sid': s.get('Sid', ''), 'effect': s['Effect']})
    effects = {m['effect'] for m in matched}
    decision = 'DENY' if 'Deny' in effects or 'Allow' not in effects else 'ALLOW'
    reason = 'Explicit deny matched' if 'Deny' in effects else 'Allow matched' if 'Allow' in effects else 'No allow matched (implicit deny)'
    return {'decision': decision, 'reason': reason, 'matched': matched}


def run_suite(policy, suite):
    if not isinstance(suite, dict) or set(suite) != {'provider', 'scenarios'}:
        raise ValueError('Suite requires exactly provider and scenarios')
    scenarios = suite['scenarios']
    if not isinstance(scenarios, list) or not scenarios:
        raise ValueError('Suite requires at least one scenario')
    names = set()
    results = []
    for case in scenarios:
        if not isinstance(case, dict) or set(case) != {'name', 'claims', 'expect'}:
            raise ValueError('Each scenario requires exactly name, claims and expect')
        if not isinstance(case['name'], str) or not case['name'].strip() or case['name'] in names:
            raise ValueError('Scenario names must be nonempty and unique')
        names.add(case['name'])
        if case['expect'] not in ('ALLOW', 'DENY'):
            raise ValueError('expect must be ALLOW or DENY')
        result = evaluate(policy, suite['provider'], case['claims'])
        results.append({'name': case['name'], 'expected': case['expect'], **result,
                        'status': 'UNKNOWN' if result['decision'] == 'UNKNOWN' else 'PASS' if result['decision'] == case['expect'] else 'FAIL'})
    return results
