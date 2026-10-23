# Zarvyn TrustCheck

**English** | [Português](README.pt-BR.md)

[![Tests](https://github.com/zar4t/zarvyn-trustcheck/actions/workflows/test.yml/badge.svg)](https://github.com/zar4t/zarvyn-trustcheck/actions/workflows/test.yml)
[![License: Apache-2.0](https://img.shields.io/badge/License-Apache--2.0-blue)](LICENSE)
![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Status](https://img.shields.io/badge/status-experimental-orange)

Turn intended GitHub Actions → AWS trust boundaries into repeatable regression tests.

A misconfigured OIDC trust policy can let any branch, fork or pull request assume
a production role. TrustCheck lets you write down which GitHub identities **should**
and **should not** be able to assume a role, and fails the build when the policy
stops matching that intent.

- Offline: no AWS credentials, network calls, telemetry or runtime dependencies
- Deterministic: same policy and scenarios, same result
- CI-friendly: exit code 0 (all pass), 1 (an expectation failed), 2 (invalid input or UNKNOWN)

## Quick start

Requires Python 3.10+.

```sh
git clone https://github.com/zar4t/zarvyn-trustcheck.git
cd zarvyn-trustcheck
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install .
```

Run the two bundled examples:

```sh
zarvyn-trustcheck --policy examples/restricted-policy.json --scenarios examples/scenarios.json
zarvyn-trustcheck --policy examples/broad-policy.json --scenarios examples/scenarios.json
```

The restricted policy passes all five scenarios (exit 0). The broad policy fails two
negative expectations (exit 1): a feature branch and a pull-request subject both match
its wildcard. These are synthetic policy evaluations, not proof that a real workflow
can mint or exchange those tokens.

Generate a report:

```sh
zarvyn-trustcheck --policy examples/restricted-policy.json --scenarios examples/scenarios.json --format markdown > report.md
```

Formats: `text`, `json` and `markdown`. UNKNOWN takes precedence over FAIL.

Without installing, from the repository root:

```sh
python3 -m trustcheck --policy examples/restricted-policy.json --scenarios examples/scenarios.json
python3 -m unittest discover -s tests -v
```

## Inputs and supported scope

Inputs are **JSON**. Copy `examples/scenarios.json` and supply your exact provider ARN
and complete hypothetical `sub`/`aud` strings. Each case has a unique name and an
expected `ALLOW` or `DENY`. Never supply real tokens or secrets.

Supported: policy version 2012-10-17; explicit Allow/Deny; the exact
`sts:AssumeRoleWithWebIdentity` action; explicit GitHub OIDC provider ARNs in the
commercial `aws` partition; `StringEquals`/`StringLike` on GitHub `sub`/`aud` only.
Condition entries and operators are ANDed; values within an entry are ORed. A matching
explicit Deny overrides Allow; no matching Allow means Deny. `StringLike` is
case-sensitive and supports `*` and `?`; brackets are literal.

Any unsupported statement makes the result UNKNOWN, including unsupported Deny
statements. Variables, `NotAction`, `NotPrincipal`, other operators, providers and
condition keys are unsupported. Duplicate JSON keys and empty suites are rejected.
Absent conditions are unconditional in this model, which does not mean AWS accepts
such a policy. Input files are limited to 1 MiB each.

The examples use legacy subject formats. Supply immutable-ID or customized subjects
literally when applicable; the tool does not discover or generate subject formats.

## Limits: read before interpreting PASS

TrustCheck is **not** a complete IAM simulator, a JWT verifier or a security
certification. PASS means only that a supplied scenario matches its expected decision
in this model.

- No token signature, issuer, expiry or issuance validation
- No inspection of GitHub workflows, branch rules, environment approvals or repository settings
- No evaluation of SCPs, role permissions, resource policies, permission boundaries or effective AWS access
- No live AWS differential tests have been performed yet

Scenario coverage is finite. Validate in an isolated sandbox before relying on results.
TrustCheck complements AWS IAM Access Analyzer and workflow scanners such as zizmor.

## Use it in CI

The bundled workflow (`.github/workflows/test.yml`) runs the tests on Python 3.10 and
3.12 and enforces the example contract, with no AWS secrets and no `id-token`
permission. Point the CLI at your own version-controlled policy and scenarios to gate
trust-policy changes. Do not hide nonzero exit codes with `continue-on-error` or `|| true`.

## Roadmap

- Live comparison against AWS in an isolated sandbox
- Reading scenarios from workflow files
- Optional read-only import of existing trust policies
- Before/after policy comparison in pull requests

Feedback from real use is the most valuable input. Open an issue with a synthetic,
minimal example.

## Contributing and security

See [CONTRIBUTING.md](CONTRIBUTING.md) and [SECURITY.md](SECURITY.md). Report
vulnerabilities privately through GitHub's private vulnerability reporting.

## References

- [GitHub: OpenID Connect in AWS](https://docs.github.com/en/actions/how-tos/secure-your-work/security-harden-deployments/oidc-in-aws)
- [AWS: IAM condition operators](https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_policies_elements_condition_operators.html)
- [AWS: IAM Access Analyzer](https://docs.aws.amazon.com/IAM/latest/UserGuide/what-is-access-analyzer.html)
- [zizmor audits](https://docs.zizmor.sh/audits/)

## License

Apache License 2.0. See [LICENSE](LICENSE). Sample identities are fictitious.

---

Built by [Luan Thales](https://github.com/zar4t) · [LinkedIn](https://www.linkedin.com/in/luanthales)
