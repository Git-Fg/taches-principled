---
name: validate-plugin
description: Audit any Claude Code marketplace or plugin for discipline violations — agent roster cap, spawn-lens contract, fork-skill rationale, description quality, catalog sync. Returns a markdown report with severity-graded findings and per-finding fix recipes. Use when the user says 'audit my marketplace', 'check discipline', 'is my marketplace valid', 'roster check', 'validate before commit', or wants to add a new agent. NOT for: marketplace schema validation (use `claude plugin validate`); NOT for: implementation work (use the relevant domain skill); NOT for: marketplace catalog regeneration (run `scripts/regenerate-marketplace.py` directly).
when_to_use: |
  - User wants to audit a marketplace or plugin for discipline before commit or PR.
  - User says "validate plugin", "check roster", "audit discipline".
argument-hint: "[marketplace-or-plugin-path]"
---

# Validate Plugin

## Decision Router

IF user provides a path → run audit on that path (default).
IF user says "the marketplace" without path → audit `$REPO_ROOT/plugins/`.
IF user passes `--ci` → emit machine-readable JSON for CI consumption.
IF the audit is for a single plugin → audit only that plugin's directory.

## Process

1. **Resolve target path** — read the marketplace path from the user's request; default to `$REPO_ROOT/plugins/` for whole-marketplace audit.
2. **Spawn `tp-roster-auditor`** (background: true) with the resolved path as $ARGUMENTS[0].
3. **Wait for the audit report.**
4. **Synthesize** — translate the auditor's findings into a human-readable markdown report if not already markdown.
5. **Return** the report. Do not modify any file — this skill is read-only.

## Output Format

```markdown
# Discipline Audit Report

**Marketplace:** `<path>`
**Date:** `<ISO-8601>`
**Verdict:** PASS / WARN / FAIL

## Findings

### BLOCKER
- `<file:line>` — `<rule>` — `<detail>`. **Fix:** `<fix>`.

### WARNING
- ...

### NUDGE
- ...
```

If the audit script's `tp-roster-auditor` overrides any finding as a false positive, surface the override explicitly:

```markdown
## Auditor Overrides
- `<rule> @ <file>` — false positive. `<reason with file:line evidence>`.
```

## Reference Index

You MUST read `references/roster-rules.md` BEFORE running the audit. It teaches the canonical 5-rule discipline set: agent roster cap, spawn-lens contract, fork-skill rationale, description quality, catalog sync.

You MUST read `references/fork-rationale.md` BEFORE auditing any `context: fork` skill. It teaches when fork earns its isolation cost and what the required `references/fork-rationale.md` file must contain.

## CONTRAST

NOT for: marketplace schema validation (use `claude plugin validate` from the official CLI — it checks `marketplace.json` schema, duplicate plugin names, source path traversal, and version mismatches).
NOT for: implementation work (use the relevant domain skill — `refine` for code review, `security` for security audits, etc.).
NOT for: marketplace catalog regeneration (run `python3 scripts/regenerate-marketplace.py` directly to sync `plugin.json` versions into `marketplace.json`).
NOT for: ad-hoc code review (use `tp-critic` w/ lens "audit this code for X").