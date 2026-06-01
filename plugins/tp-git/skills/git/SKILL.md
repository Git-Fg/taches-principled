---
name: git
description: "Git operations: ship commits, post PR comments, load issues, manage branches. Modes: SHIP, REVIEW, ISSUES, ADVANCED."
allowed-tools: Bash(git *), Bash(gh *)
---

## Decision Router

IF committing changes with conventional messages → SHIP mode
IF posting line-specific PR review comments → REVIEW mode
IF loading issues or creating technical specs → ISSUES mode
IF using git notes or worktrees → ADVANCED mode

# Mode: SHIP

Create well-formatted commits with conventional messages and publish pull requests.

## Commit Workflow

1. **Branch check:** If on `main`/`master`, create feature branch (`<type>/<scope>/<description>`)
2. **Lint:** Run pre-commit checks unless `--no-verify`
3. **Stage:** Auto-stage if no files staged
4. **Split:** If changes touch multiple concerns, split into atomic commits
5. **Message:** Generate with emoji + conventional commit format

| Type | Emoji |
|------|-------|
| feat | ✨ |
| fix | 🐛 |
| docs | 📝 |
| style | 💄 |
| refactor | ♻️ |
| perf | ⚡ |
| test | ✅ |
| chore | 🔧 |
| ci | 🚀 |

## PR Workflow

1. **Pre-flight:** Check for uncommitted changes
2. **Template:** Use `.github/pull_request_template.md` if exists
3. **Title:** Emoji + type + scope: `✨(scope): description`
4. **Create:** Draft PR by default, convert to ready when complete

**Spawn Directives:**
- **ALWAYS spawn a subagent to run pre-flight checks (lint, type-check) in parallel while main agent prepares commit message**

---

# Mode: REVIEW

Post line-specific comments on PR diffs. Supports single comments and batched multi-file reviews.

## Quick Reference

| Goal | Command |
|------|---------|
| Single inline comment | `gh api repos/{owner}/{repo}/pulls/{pr}/comments -f body='...' -f commit_id='<sha>' -f path='<file>' -F line=<n> -f side='RIGHT'` |
| Multi-comment review | `echo '{ "event": "COMMENT", "body": "...", "comments": [...] }' \| gh api repos/{owner}/{repo}/pulls/{pr}/reviews --input -` |
| Get latest commit SHA | `gh api repos/{owner}/{repo}/pulls/{pr} --jq '.head.sha'` |

## Batch Review

Group related comments into one review to reduce notification noise. Review events: COMMENT, APPROVE, REQUEST_CHANGES.

**Spawn Directives:**
- **ALWAYS fan out subagents to review each changed file in parallel — main agent synthesizes findings**

---

# Mode: ISSUES

Load all open issues from GitHub and create structured technical specifications.

## Load Issues

```bash
gh issue list --limit 100
gh issue view <number> --json number,title,body,state,createdAt,updatedAt,author,labels,assignees,url
mkdir -p ./specs/issues
# Save as <NNN>-<kebab-case-title>.md
```

## Analyze Issue

1. Locate or fetch issue from `./specs/issues/`
2. Review related code and project structure
3. Create technical specification with problem statement, technical approach, implementation plan
4. Save as `*.specs.md`

Bug fixes: emphasize test plan and reproduction. Features: emphasize technical approach.

**Spawn Directives:**
- **ALWAYS spawn parallel subagents when loading multiple issues — one subagent per issue**

---

# Mode: ADVANCED

Power-user git: attach metadata to commits without changing SHA, work on multiple branches simultaneously.

## Git Notes

| Task | Command |
|------|---------|
| Add note | `git notes add -m "message" <sha>` |
| Append | `git notes append -m "message" <sha>` |
| View | `git notes show <sha>` |
| Namespace | `git notes --ref=<name> add -m "..." <sha>` |
| Push | `git push origin refs/notes/<name>` |

Namespaces organize notes by purpose (reviews, testing, audit). Use `git config notes.rewrite.rebase true` to preserve on rebase.

## Git Worktrees

```bash
git worktree add -b <branch> <path>           # new branch from HEAD
git worktree add <path> <branch>              # existing branch
git worktree add --track -b <branch> <path> origin/<branch>  # from remote
git worktree list                             # list all
git worktree remove <path>                    # remove
```

Use worktrees instead of stashing when switching contexts. One worktree per active branch.

**Spawn Directives:**
- **ALWAYS spawn subagents for parallel worktree setup or multi-worktree operations**

---

## Output

SHIP: Commits on feature branch + draft PR URL
REVIEW: Posted comments on GitHub PR
ISSUES: Issue files in `./specs/issues/` + specification documents
ADVANCED: Notes in `.git/refs/notes/` + additional working directories