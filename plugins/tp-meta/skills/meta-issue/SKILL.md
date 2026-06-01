---
name: meta-issue
description: "Create GitHub issue from meta-review findings. Replaces manual gh issue create for behavioral reports."
allowed-tools: Read, Bash
when_to_use: "Use when user wants to create a GitHub issue or bug report from meta-review findings."
argument-hint: "[<review-file-path>] [--dry-run]"
---

## Routing Guidance

- FIRST after meta-review produces actionable findings.
- Do NOT use for general issue creation (use gh directly) or code bugs (use code-review).

## Decision Router

IF user provides a meta-review file path → **CREATE** mode
IF user ran meta-review in current session → use its output file → **CREATE** mode
IF user wants to preview the issue body without creating → **DRY-RUN** mode

---

## CREATE Mode

### Prerequisites

1. **Verify `gh` is available** — `which gh`. If missing, tell user to install GitHub CLI.
2. **Verify git remote** — `git remote get-url origin`. If missing, tell user this only works in a git repo with a GitHub remote.
3. **Verify review file exists** — read the meta-review output from `.principled/scratch/`

### Safety Check — Privacy Audit

Before creating any issue, scan the review content for:
- Absolute file paths (except `~/.claude/sessions/` which is generic)
- User prompt text (should be paraphrased, not quoted)
- Environment variable values
- Token or credential strings
- Project-specific file contents

If any sensitive content found: **ABORT** and tell the user what needs to be redacted. Never create an issue with private information.

### Issue Body Construction

Build the issue body from the meta-review file:

```markdown
## What Happened
{1-3 sentence summary of the behavioral pattern}

## Session Context
- Session scope: {marketplace-only | custom-rules | mixed}
- Plugins loaded: {list or NONE}
- Rules active: {list or NONE — use "NONE" for marketplace-only sessions}

## Behavioral Anti-Patterns
{PLUGIN-scope findings only — numbered list with evidence}

## Suggestions
{Concrete improvement proposals — numbered, each with rationale}

## What Went Well
{2-3 positive patterns observed}

## Scope
- Actionable findings: {count}
- Excluded (user-file/environment scope): {count}
- Report status: {advised/not-advised}
```

### Issue Creation

```bash
gh issue create \
  -t "[meta] {1-line summary}" \
  -F {body-file} \
  -l "meta-review"
```

If the `meta-review` label doesn't exist, create it first:
```bash
gh label create "meta-review" --description "Behavioral review from session analysis" --color "1D76DB" 2>/dev/null || true
```

### Post-Creation

Report the issue URL to the user.

---

## DRY-RUN Mode

Build the issue body from the meta-review file (same template as CREATE mode) and print it to stdout with `cat`. Do not invoke `gh issue create`. Return the full body so the user can review before running CREATE.

---

## Scope Exclusion

If the meta-review file has `Report advised: NO` (all findings are USER-FILE/ENVIRONMENT/MODEL scope), tell the user:

> "The review found no actionable plugin-scope findings. All issues trace to user configuration or environment state. Creating a public issue is not recommended — the root cause is outside the plugin's control."

The user can override with explicit confirmation.
