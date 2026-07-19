# Contributing

evolve-mvp improves through its **regression log**, not just code. Two ways to help:

## 1. Extend the failure log (highest value)
Edit `evolve_mvp/LESSONS.json` (or the `DEFAULT_LESSONS` in `core.py`) with a real
failure mode you've seen:
```json
{"date": "2026-07-19", "mode": "short-id", "cause": "what killed it", "fix": "what prevents it"}
```
De-dupe by `mode`. This makes the engine smarter for everyone.

## 2. Code
- Fork, branch, PR.
- Python 3.9+. `pip install -e .` to dev.
- Keep the Tier0 security standard: no secrets in repo, read-only by default, keys from env only.

## Principles
- Model-agnostic. No vendor lock-in.
- Self-evolving via regression, not manual hand-holding.
- Behavioral guards are non-negotiable (scope/sunk-cost/perfectionism).
- The product is a shipped MVP, not a document.
