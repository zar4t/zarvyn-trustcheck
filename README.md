# Zarvyn TrustCheck

Turn intended GitHub → AWS trust boundaries into repeatable regression scenarios.

**v0.1.0 experimental offline prototype.** No AWS credentials, network calls,
telemetry, runtime dependencies or automatic remediation.

## Quick start Python 3.10+

### Install on Linux / WSL

From the extracted project directory, with Python 3.10+ and its `venv` module
installed (on Ubuntu/Debian, install `python3-venv` if needed):

```sh
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install .
zarvyn-trustcheck --policy examples/restricted-policy.json --scenarios examples/scenarios.json
zarvyn-trustcheck --policy examples/broad-policy.json --scenarios examples/scenarios.json
zarvyn-trustcheck --policy examples/restricted-policy.json --scenarios examples/scenarios.json --format markdown > report.md
```

The installed command belongs to the virtual environment. The restricted example
exits with 0; the broad example intentionally exits with 1. Installation may fetch
setuptools. Run `deactivate` when finished.

While the environment is active, the command also works from another directory.
Use absolute paths to the inputs, replacing `/absolute/path/to/project` below:

```sh
zarvyn-trustcheck --policy /absolute/path/to/project/examples/restricted-policy.json --scenarios /absolute/path/to/project/examples/scenarios.json
```

### Run directly without installation

From the extracted project directory:

```sh
python3 -m trustcheck --policy examples/restricted-policy.json --scenarios examples/scenarios.json
python3 -m trustcheck --policy examples/broad-policy.json --scenarios examples/scenarios.json
python3 -m unittest discover -s tests -v
```

The restricted policy passes five scenarios. The broad policy fails two negative
expectations: a feature branch and a pull-request subject match its wildcard.
These are synthetic policy evaluations, not proof that an actual workflow can mint
or exchange those tokens.

```sh
python3 -m trustcheck --policy examples/restricted-policy.json --scenarios examples/scenarios.json --format markdown > report.md
```

Formats: text, JSON and Markdown. Exit codes: 0 all expectations pass; 1 at least
one fails; 2 invalid input or UNKNOWN. UNKNOWN takes precedence over FAIL.
Module execution needs only Python.

## Inputs and scope

v0.1 takes **JSON**, not YAML. Copy examples/scenarios.json and supply your exact
provider ARN and complete hypothetical `sub`/`aud` strings. Each case has a unique
name and an expected ALLOW or DENY. Never supply real tokens or secrets.

Supported: policy version 2012-10-17; explicit Allow/Deny; exact
sts:AssumeRoleWithWebIdentity action; explicit GitHub OIDC provider ARNs in the
commercial aws partition; StringEquals/StringLike on GitHub sub/aud only.
Condition entries and operators are ANDed; values within an entry are ORed.
Explicit matching Deny overrides Allow; no matching Allow implies Deny.
StringLike is case-sensitive and supports * and ?; brackets are literal.

Any unsupported statement makes the result UNKNOWN, including unsupported Deny
statements. Variables, NotAction, NotPrincipal, other operators/providers and other
condition keys are unsupported. Duplicate JSON keys and empty suites are rejected.
Absent conditions are unconditional in this model; that does NOT mean AWS accepts
such a policy when creating/updating a role. Input files are limited to 1 MiB each.

Examples use legacy subjects. Supply immutable-ID or customized subjects literally
when applicable; the tool does not discover or generate repository subject formats.

## Limits — read before interpreting PASS

This is NOT a complete IAM simulator, JWT verifier or security certification.
PASS means only that this supplied scenario matches its expected model decision.

No token signature, issuer, expiry or token issuance validation. No GitHub workflow,
branch rules, environment approvals or repository settings inspection. Matching a
production environment subject does not prove only a specific branch can deploy.
No SCP, role permission, resource policy, permissions-boundary or effective AWS
access evaluation. No live AWS differential tests have been performed.

Scenario coverage is finite. Validate in an isolated sandbox before relying on the
results. It complements AWS Access Analyzer and workflow scanners such as zizmor.

## CI

.github/workflows/test.yml uses a Python 3.10 / 3.12 matrix and runs tests and the example contract without AWS secrets
or id-token permissions. Point the CLI at your own version-controlled inputs to
gate policy changes. Do not hide nonzero exits with continue-on-error or `|| true`.
The bundled workflow passed on GitHub for the initial commit. Check the current
run status at https://github.com/zar4t/zarvyn-trustcheck/actions.

## Portfolio and roadmap

Demonstrate broad policy → failed negative scenarios → restricted policy → passing
scenarios. Explain why, show limitations, and measure actual adoption rather than
claiming incident reduction. Initial code was AI-assisted; review it and reproduce
tests before presenting it as engineering work you understand.

Next: independent review and AWS sandbox comparisons, feedback from actual users,
workflow parsing, optional read-only imports, and before/after policy comparison.
Source repository: https://github.com/zar4t/zarvyn-trustcheck
No package has been published on PyPI.

## References

- https://docs.github.com/en/actions/how-tos/secure-your-work/security-harden-deployments/oidc-in-aws
- https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_policies_elements_condition_operators.html
- https://docs.aws.amazon.com/IAM/latest/UserGuide/what-is-access-analyzer.html
- https://docs.zizmor.sh/audits/

MIT license. Sample identities are fictitious.
