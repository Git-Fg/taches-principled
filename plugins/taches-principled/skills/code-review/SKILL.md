---
name: code-review
description: "Multi-agent code review for PRs and local changes. Use when user says 'review this PR', 'check my changes', 'review the code', or 'audit this pull request'."
when_to_use: |
  Use when the user says "review this PR", "check my changes", "review the code", or "audit this pull request".
  IMMEDIATELY before merging or committing significant code changes.
  Do NOT use when code needs to be simplified or reduced (use code-simplify), when work was already completed and needs reflection (use reflexion), or for architectural decisions (use create-plans).
argument-hint: "[focus-areas] [--min-impact critical|high|medium|medium-low|low]"
---

## Decision Router

IF user says "PR", "pull request", or names a PR number → PR Review (checks eligibility, posts inline comments on GitHub)
IF user says "local", "uncommitted", "staged", "before commit", or no target specified → Local Changes Review (terminal report with quality gate)
IF ambiguous → ask: "Review a pull request or local uncommitted changes?"

# Code Review

Multi-agent code review that scans for bugs, security vulnerabilities, code quality issues, contract violations, and test coverage gaps. Uses 6 specialized review agents running in parallel, with progressive confidence scoring and impact-based filtering.

## Capability Routing

Six specialized agents run in parallel. Each focuses on a distinct dimension:

| Agent | Focus Area | Key Questions It Answers |
|-------|------------|------------------------|
| **Bug Hunter** | Logic errors, edge cases, race conditions, systemic gaps | Where did the invalid data originate? What architectural gap enabled this? How would this fail under load? |
| **Security Auditor** | OWASP Top 10, auth, injection, secrets exposure, attack vectors | Can this be exploited? What would an attacker do? Does this fail closed or open? |
| **Code Quality Reviewer** | Readability, complexity, naming, duplication, project conventions | Does this follow established patterns? Is the solution simple enough? Would future developers understand this? |
| **Contracts Reviewer** | API contracts, data models, type design, breaking changes | Can illegal states be represented? Are invariants protected? Will this break existing consumers? |
| **Historical Context Reviewer** | Git history, past PRs, recurring patterns, known anti-patterns | What problems occurred before in these files? Have we solved this pattern before? |
| **Test Coverage Reviewer** | Missing tests, untested edge cases, behavioral coverage | What error paths are untested? What regressions could occur? Would this test catch the bug we found? |

## Shared Review Process

### Phase 1: Preparation
1. Identify the change set (git diff or PR diff)
2. Read instruction files if present in `.claude/` or `CLAUDE.md`
3. Check review scope against `--min-impact` threshold

### Phase 2: Multi-Agent Issue Detection
Spawn applicable review agents in parallel. Each produces issues with:
- **Impact score**: 0-100 mapped to critical (81-100), high (61-80), medium (41-60), medium-low (21-40), low (0-20)
- **Confidence**: confidence-scored signal with filterable threshold
- **Evidence**: specific file:line references

Progressive confidence threshold: low-confidence findings are included but marked as such. No automated filtering — the user sees everything with confidence indicators.

### Phase 3: Consolidation
1. Deduplicate by file:line:issue-text
2. Filter to `--min-impact` threshold (default: high)
3. Skip if change set >500 lines (focus on architecture + security only)

## PR Review — Environment-Specific

**Eligibility check**: Skip closed/draft PRs, check PR has description (add one if missing), discover instruction files from base branch.
**Output**: Post inline comments on PR diff with emoji severity indicators. Use MCP GitHub tools when available, fall back to gh API.

## Local Changes Review — Environment-Specific

**Diff source**: Run `git status --short` to identify changed files, differentiate staged vs. unstaged, take action accordingly.
**Output**: Terminal report with quality gate (PASS/FAIL) determined by issue count vs. threshold. JSON output with `--json` flag.
