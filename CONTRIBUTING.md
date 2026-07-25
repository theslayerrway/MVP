# Contributing

## Before contributing

Open an issue describing the change before writing code.
This prevents wasted work on contributions that don't align
with the project's direction.

## Scope

- Model-agnostic. No vendor-specific bindings.
- Regression entries are maintained by the maintainer.
- Behavioral guards are maintained by the maintainer, not
  prescribed to contributors.

## Code

- Fork, branch, PR.
- Python 3.9+.
- Keep test fixtures minimal. One project, concrete output.

## Review

PRs are reviewed for:
1. Does it break existing enforcement standards?
2. Does it introduce a hard gate or a soft suggestion?
3. Does it keep the four-phase protocol intact?

PRs that don't align are closed with a specific reason.
Contributors are encouraged to open an issue to discuss
before resubmitting.

## Security

Report vulnerabilities to `theslayerrway@users.noreply.github.com`.
Do not open public issues for security problems.
