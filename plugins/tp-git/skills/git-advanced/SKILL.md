---
name: git-advanced
description: "Attach metadata to commits without rewriting history and work on multiple branches simultaneously with worktrees."
when_to_use: "Use when the user says 'git notes', 'add note to commit', 'annotate commit', 'attach metadata', or 'worktree'. IMMEDIATELY when the user asks to 'work on multiple branches', 'switch branches without stashing', 'checkout multiple branches', 'parallel branches', or 'branch in parallel'. BEFORE stashing changes to switch contexts — offer worktree as an alternative."
---

## Decision Router

IF annotating a commit post-hoc → use `git notes add`
IF accumulating metadata over time → use `git notes append` (not `add -f`)
IF notes must be shared with the team → push the notes ref explicitly
IF notes disappear after rebase → configure `notes.rewrite.rebase true`
IF working on multiple branches simultaneously → use worktrees instead of stashing
IF reviewing a PR while actively developing → create a temporary review worktree
IF running long-running tests → use a detached worktree to keep the main tree clean
IF comparing implementations across branches → create worktrees and diff directly
IF user requests both notes and worktrees in same message → handle both in sequence

# Git Advanced

Power-user git utilities: attach metadata to commits without changing their SHA, and check out multiple branches simultaneously in separate directories. These are independent workflows that share no state — route by keyword.

## Git Notes

Attach metadata to git commits without changing their SHA. Notes live in separate refs (`refs/notes/commits` by default) and display alongside commit messages in `git log` and `git show`.

### Core Principle

Add information to commits after creation without rewriting history. Non-invasive, shareable, namespaceable.

### Quick Reference

| Task | Command |
|------|---------|
| Add note | `git notes add -m "message" <sha>` |
| View note | `git notes show <sha>` |
| Append | `git notes append -m "message" <sha>` |
| Remove | `git notes remove <sha>` |
| Namespace | `git notes --ref=<name> add -m "..." <sha>` |
| Show in log | `git log --notes=<name>` |
| Push notes | `git push origin refs/notes/<name>` |
| Fetch notes | `git fetch origin refs/notes/<name>:refs/notes/<name>` |
| Preserve on rebase | `git config notes.rewrite.rebase true` |

### Workflow Patterns

#### Code Review Tracking

```bash
git notes --ref=reviews add -m "Reviewed-by: Alice <alice@example.com>" abc1234
git notes --ref=reviews append -m "Approved with minor suggestions" abc1234
git log --notes=reviews --oneline
```

#### Test Results Annotation

```bash
git notes --ref=testing add -m "Tests passed: 2024-01-15 | Coverage: 85%" abc1234
git log --notes=testing --oneline
```

#### Audit Trail

```bash
git notes --ref=audit add -m "Security review: PASSED | Ticket: SEC-456" abc1234
```

#### Sharing Notes with the Team

```bash
git push origin refs/notes/reviews
git fetch origin refs/notes/reviews:refs/notes/reviews
```

### Common Mistakes

| Mistake | Fix |
|---------|-----|
| Notes not showing in log | Use `git log --notes=<name>` or configure `notes.displayRef` |
| Notes lost after rebase | Run `git config notes.rewrite.rebase true` before rebasing |
| Notes not on remote | Push explicitly: `git push origin refs/notes/commits` |
| "Note already exists" | Use `append` instead of `add`, or `add -f` to overwrite |

### Output

- Notes stored in `.git/refs/notes/` — viewable via `git log --notes` and `git show`
- Pushable to remotes for team-wide access

### Design Decisions

#### Why separate namespaces

Namespaces organize notes by purpose (reviews vs testing vs audit) and let you selectively share only what is needed.

## Git Worktrees

Check out multiple branches simultaneously in separate directories, sharing one Git object database. Switch contexts by changing directories, not branches.

### Core Principle

One worktree per active branch. Never stash, never clone again.

### Quick Reference

| Task | Command |
|------|---------|
| Create (new branch from HEAD) | `git worktree add -b <branch> <path>` |
| Create (existing branch) | `git worktree add <path> <branch>` |
| Create (from remote) | `git worktree add --track -b <branch> <path> origin/<branch>` |
| Create (detached) | `git worktree add --detach <path> <commit>` |
| List all | `git worktree list` |
| Remove | `git worktree remove <path>` |
| Force remove | `git worktree remove --force <path>` |
| Move | `git worktree move <old> <new>` |
| Prune stale metadata | `git worktree prune` |
| Repair after manual move | `git worktree repair` |
| Lock | `git worktree lock <path>` |

#### Conventions

- Create worktrees as sibling directories: `../project-feature`
- Name by purpose: `project-hotfix`, `project-review`
- Each branch can only be checked out in ONE worktree at a time

### Workflow Patterns

#### Context Switching (Feature + Hotfix)

```bash
git worktree add -b hotfix-456 ../project-hotfix origin/main
cd ../project-hotfix   # fix, commit, push
cd ../project
git worktree remove ../project-hotfix
```

#### PR Review While Developing

```bash
git fetch origin pull/123/head:pr-123
git worktree add ../project-review pr-123
cd ../project-review   # review, run tests
cd ../project
git worktree remove ../project-review && git branch -d pr-123
```

#### Isolated Testing

```bash
git worktree add --detach ../project-test HEAD
cd ../project-test && npm test &
cd ../project   # continue working in parallel
```

#### Comparing Branches Side-by-Side

```bash
git worktree add ../project-v1 v1.0.0
git worktree add ../project-v2 v2.0.0
diff -rq ../project-v1/src ../project-v2/src
```

#### Selective File Merge

```bash
# From any worktree, cherry-pick files across branches
git checkout feature-branch -- path/to/file.js
git checkout -p feature-branch -- path/to/file.js  # interactive hunk selection
```

### Common Mistakes

| Mistake | Fix |
|---------|-----|
| `rm -rf` to delete a worktree | Always use `git worktree remove`, then prune if needed |
| "Branch is already checked out" | Run `git worktree list` to find which worktree has it |
| Stale metadata after manual deletion | Run `git worktree prune` |
| Moved worktree directory manually | Use `git worktree move` or run `git worktree repair` |

### Output

- Additional working directories at sibling level, all sharing one object database
- No branch switching or stashing required to work on parallel streams

### Design Decisions

#### Why worktrees over multiple clones

Worktrees share the Git object database — zero disk duplication, instant creation, no need to push/pull between working copies.

#### Why sibling directories

Keeps the main project tree clean. Worktrees are independent working copies, not subdirectories.

#### Relationship to development pipeline

Enables parallel development workflows: feature work, hotfixes, PR reviews, and experiments can coexist without context-switching overhead.
