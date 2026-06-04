---
name: git-preflight-checker
description: "Run pre-flight validation checks (lint, type-check, tests, build sanity) before commits or PRs. Use before any commit or merge to gate quality. Exits fast with clear pass/fail so the main agent can proceed or abort."
when_to_use: |
  - "Run pre-flight checks before committing"
  - "Lint and type-check before pushing"
  - "Verify the project builds before opening a PR"
  - "Run the test suite on changed files before merge"
---

# git-preflight-checker

Run validation pipelines and return a clear pass/fail verdict before any
commit or merge proceeds. The skill runs the same checks the deleted
`git-preflight-checker` agent used to, but as a skill so the main agent
executes them directly (no subagent context overhead).

## The four checks, in order

Stop on the first failure — no point running type-check if lint already
broke.

1. **Lint** (ESLint, Ruff, Clippy, ShellCheck — whatever the project uses)
2. **Type-check** (TypeScript, MyPy, Rustc — whatever applies)
3. **Unit tests** (focus on the changed files, not full suite)
4. **Build sanity check** (does the project compile/build without errors?)

## How to invoke

Use the `Bash` tool directly with the project's standard commands. The
shape of each check is project-specific; consult the project's
contributing docs or `package.json` / `Cargo.toml` / `pyproject.toml` /
`Makefile` for the canonical command. Examples:

```bash
# Node project
npm run lint && npm run typecheck && npm test -- --changedSince=main && npm run build

# Python project
ruff check . && mypy . && pytest -x --co && python -m build --check

# Rust project
cargo clippy --all-targets -- -D warnings && cargo check --all-targets && cargo nextest run --changed
```

## Report format

On success:
```
PREFLIGHT: PASS (lint, typecheck, tests, build)
```

On failure:
```
PREFLIGHT: FAIL at <step>
  step:    <lint|typecheck|tests|build>
  command: <the command that failed>
  error:   <the first 20 lines of stderr>
  file:    <path:line if the error format is greppable>
```

## Do NOT

- Do not attempt to fix anything — only validate and report
- Do not run the full test suite on every preflight — focus on the
  changed files
- Do not continue past a failure to "see what else breaks" — stop fast
  and report
- Do not install missing tools silently — if `cargo clippy` is not
  installed, report the missing tool and stop
