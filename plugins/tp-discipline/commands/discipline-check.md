---
name: discipline-check
description: Run the tp-discipline audit on the current marketplace and return the verdict + findings. Convenience wrapper around the validate-plugin skill.
argument-hint: "[marketplace-or-plugin-path] [--ci]"
---

Run the discipline audit. Default target: the git repo root (parent of `plugins/`).

```bash
python3 scripts/audit.py "$@" 2>&1
```

If `--ci` is passed, emit machine-readable JSON; exit non-zero on BLOCKER findings.

If a path is passed, audit that path. Otherwise audit the whole marketplace.