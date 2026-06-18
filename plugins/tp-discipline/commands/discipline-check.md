---
name: discipline-check
description: Run the tp-discipline audit on the current marketplace and return the verdict + findings. Convenience wrapper around the validate-plugin skill.
argument-hint: "[marketplace-or-plugin-path] [--ci]"
---

Run the discipline audit. Default target: the git repo root (parent of `plugins/`). Default tier: structural (R1+R3+R5, zero false positives).

```bash
python3 scripts/audit.py "$@" 2>&1
```

Flags:
- `--ci` — emit machine-readable JSON; exit non-zero on BLOCKER findings.
- `--strict` — also run stylistic checks (R2 spawn-lens, R4 description quality). Off by default; use for pre-release audits or new-maintainer onboarding.
- `<path>` — audit that path. Otherwise audit the whole marketplace.