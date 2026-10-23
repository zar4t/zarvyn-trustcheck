# Contributing

Thanks for helping improve Zarvyn TrustCheck.

## Before you open a pull request

- Run the tests: `python3 -m unittest discover -s tests -v`
- Include a minimal synthetic policy and scenario, the expected and actual
  behavior, documentation and a regression test with each fix.
- Unsupported semantics must stay UNKNOWN until implemented and tested.
- Never submit secrets, real tokens or confidential infrastructure information.

## Developer Certificate of Origin (DCO)

Every commit must be signed off, certifying that you wrote the change or have
the right to submit it under the project's license
([developercertificate.org](https://developercertificate.org)):

```sh
git commit -s -m "fix: describe the change"
```

This adds a `Signed-off-by: Your Name <you@example.com>` line to the commit.

## Review

Every pull request is reviewed by the maintainer before merge. Workflows run
without repository secrets for pull requests from forks.
