---
name: git
description: "Handle version control tasks: commit changes, review pull requests, and manage issues or branches. Use when user says 'commit', 'PR', 'issue', or 'branch'."
allowed-tools: Bash(git *), Bash(gh *)
when_to_use: |
  - User wants to commit code with conventional messages or publish a PR.
  - User needs to post line-specific comments on a pull request.
  - User wants to load GitHub issues or create technical specs from them.
  - User needs to manage git worktrees or notes.
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
5. **Message:** Generate with emoji + conventional commit format.

### Commit Conventions
You MUST read `references/commit-conventions.md` BEFORE generating commit messages to ensure compliance with conventional commit types and emojis.

## PR Workflow

1. **Pre-flight:** Check for uncommitted changes
2. **Template:** Use `.github/pull_request_template.md` if exists
3. **Title:** Emoji + type + scope: `✨(scope): description`
4. **Create:** Draft PR by default, convert to ready when complete

**Spawn Directives:**
- **ALWAYS spawn `git-preflight-checker` to run pre-flight checks (lint, type-check) in parallel while the main agent prepares the commit message**

---

# Mode: REVIEW

Post line-specific comments on PR diffs. Supports single comments and batched multi-file reviews.

### Review Commands
You MUST read `references/review-commands.md` BEFORE executing PR reviews to use the correct `gh api` commands and review event types.

## Batch Review

Group related comments into one review to reduce notification noise. Review events: COMMENT, APPROVE, REQUEST_CHANGES.

**Spawn Directives:**
- **ALWAYS fan out `git-pr-reviewer` agents to review each changed file in parallel — spawn one `git-pr-reviewer` per changed file, main agent synthesizes findings**

---

# Mode: ISSUES

Load all open issues from GitHub and create structured technical specifications.

## Load Issues

1. List issues using `gh issue list`.
2. View specific issues using `gh issue view`.
3. Save structured data to `./specs/issues/`.

## Analyze Issue

1. Locate or fetch issue from `./specs/issues/`
2. Review related code and project structure
3. Create technical specification with problem statement, technical approach, implementation plan
4. Save as `*.specs.md`

Bug fixes: emphasize test plan and reproduction. Features: emphasize technical approach.

**Spawn Directives:**
- **ALWAYS spawn parallel `git-issue-analyzer` agents when loading multiple issues — one `git-issue-analyzer` per issue**

---

# Mode: ADVANCED

Power-user git: attach metadata to commits without changing SHA, work on multiple branches simultaneously.

### Advanced Operations
You MUST read `references/advanced-git.md` BEFORE performing advanced git operations to ensure correct usage of git notes and worktrees.

**Spawn Directives:**
- **ALWAYS spawn `git-worktree-manager` for parallel worktree setup or multi-worktree operations**

---

## Output

SHIP: Commits on feature branch + draft PR URL
REVIEW: Posted comments on GitHub PR
ISSUES: Issue files in `./specs/issues/` + specification documents
ADVANCED: Notes in `.git/refs/notes/` + additional working directories
