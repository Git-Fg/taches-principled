---
name: git-ship
description: Create well-formatted commits with conventional messages and publish pull requests with template-driven bodies
argument-hint: [--no-verify]
---

## Decision Router

IF committing local changes → run branch safety, lint, stage, split, and format
IF creating a pull request → run pre-flight checks, draft title, create with template
IF on main/master branch → ask to create a feature branch before committing
IF changes span multiple concerns → split into atomic commits
IF uncommitted changes exist when creating a PR → suggest committing first
IF --no-verify flag is set → skip pre-commit lint checks
IF no files are staged → auto-stage modified and new files
IF a PR template exists in .github/ → use it for the body
IF work is in progress → create as a draft PR

# Git Ship

Handle the full ship workflow: conventional commits with emoji and automatic lint verification, then pull requests with template-driven bodies. Covers branch safety checks, staging, linting, message formatting, commit splitting, and PR creation.

## Core Principle

Every commit is a logical unit: one concern, one message, one reviewable diff. Every PR is a communication artifact — its title and body must tell the reviewer what changed and why.

## Process

### Commit Workflow

1. **Branch check**: If on `main` or `master`, ask user whether to create a feature branch. Use pattern `<type>/<git-username>/<kebab-case-description>`.
2. **Lint**: Run pre-commit checks unless `--no-verify` is passed.
3. **Stage**: Run `git status`. If 0 files staged, auto-stage modified and new files.
4. **Diff review**: Run `git diff --cached` to understand the changes.
5. **Split**: If changes touch multiple concerns (different types, file patterns, or logical groups), suggest splitting into separate commits.
6. **Message**: For each commit, generate a message using emoji conventional commit format.

#### Commit Message Format

```
<emoji> <type>: <imperative description>
```

| Type | Emoji | When to Use |
|------|-------|-------------|
| feat | ✨ | New feature |
| fix | 🐛 | Bug fix |
| docs | 📝 | Documentation |
| style | 💄 | Formatting, style |
| refactor | ♻️ | Code change with no behavior change |
| perf | ⚡ | Performance improvement |
| test | ✅ | Adding or fixing tests |
| chore | 🔧 | Tooling, configuration, dependencies |
| ci | 🚀 | CI/CD changes |
| revert | ⏪ | Reverting a change |

- Subject line under 72 characters
- Present tense, imperative mood

#### Splitting Guidelines

Split when the diff contains:
- Changes to unrelated parts of the codebase
- Mix of feature work and refactoring in the same set
- Both source code changes and documentation updates
- Changes that would be clearer to review separately

### Pull Request Workflow

1. **Pre-flight**: Run `git status` to check for uncommitted changes. If any exist, suggest committing first.
2. **Template**: Check for `.github/pull_request_template.md` and read it for body structure.
3. **Base branch**: Determine the target branch (typically `main` or `master`).
4. **Title**: Draft using conventional commit format with emoji and scope: `<emoji>(<scope>): <description>`.
5. **Create**:

   ```bash
   gh pr create --draft \
     --title "<emoji>(<scope>): description" \
     --body-file .github/pull_request_template.md \
     --base main
   ```

6. **Verify**: `gh pr view` to confirm the PR was created successfully.

#### PR Title Format

Match emoji and type to the primary change:
- ✨ `feat(scope):` — new feature
- 🐛 `fix(scope):` — bug fix
- 📝 `docs(scope):` — documentation
- ♻️ `refactor(scope):` — refactoring
- 🔧 `chore(scope):` — tooling, config

## Output

- One or more commits on the current or newly-created branch
- Lint verification results
- GitHub PR created on the current branch (draft by default)
- PR URL printed to conversation

## Design Decisions

### Why conventional commits

Standardized messages enable changelog generation, semantic versioning detection, and team-wide consistency. The emoji provides visual scanning cues in terminal and web UI.

### Why draft PR by default

Draft signals work-in-progress to reviewers. Convert to ready for review with `gh pr ready` when complete.

### Why gh CLI over API

The `gh` CLI handles authentication, fork detection, and defaults without requiring tokens or API setup.

### Relationship to development pipeline

Creates the git history and PR artifacts consumed by review, changelog generation, and release workflows downstream.
