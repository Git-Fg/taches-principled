---
name: git-worktree-manager
description: "Manage git worktrees — create, list, remove, prune, and audit worktree state. Use when the user says 'create a git worktree', 'list worktrees', 'remove a worktree', 'prune stale references', 'audit worktree state', 'set up parallel development environments', 'isolate branches for review'. Pure git-worktree plumbing; release and review are separate (use the `git` skill). NOT for: PR review of changes in a worktree (use `git` skill REVIEW mode or `refine` REVIEW)."
when_to_use: |
  - "Create a git worktree"
  - "List worktrees"
  - "Remove a worktree"
  - "Prune stale worktree references"
  - "Audit a worktree's state"
---

# git-worktree-manager

Create, audit, and remove git worktrees for parallel development. Run
the commands directly via the `Bash` tool — this skill is a reference
for the exact git invocations, not a subagent.

## CONTRAST

- NOT for: commit / push / branch / merge — use the `git` skill
- NOT for: PR review of changes in a worktree — use `refine` REVIEW or spawn `tp-critic` (lens: "review this diff for bug, security, and contract errors")
- NOT for: persistent session isolation — worktrees are git-level, not session-level
- This skill is purely for git-worktree plumbing; release and review are separate

## Available operations

### Create a new worktree

```bash
git worktree add -b <branch> <path> <start-point>
```

Before running, verify:
- The target path does not already exist
- The branch name is not already in use (`git branch --list <branch>`)
- The start-point is a valid commit / branch / tag

### List all worktrees

```bash
git worktree list --porcelain
```

The `--porcelain` flag gives parseable output (one worktree per
record, with branch + commit + path). Use this for any state-reading
code.

### Remove a worktree

```bash
git worktree remove <path>
# or, if the worktree has uncommitted changes:
git worktree remove --force <path>
```

Before removing, check for uncommitted changes:

```bash
git -C <path> status --porcelain
# If non-empty, warn before forcing removal.
```

### Prune stale references

```bash
git worktree prune
```

Use after a worktree's directory is deleted out-of-band (manual `rm`,
crash, etc.) to clean up `.git/worktrees/`.

### Audit a specific worktree

```bash
git -C <path> status --porcelain
git -C <path> log --oneline -5
git -C <path> rev-parse --abbrev-ref HEAD
```

Returns: branch, HEAD, recent commits, uncommitted-changes status.

## After every mutation

Return the full worktree list so the calling agent has current state:

```bash
git worktree list --porcelain
```

## Common pitfalls

- Don't create a worktree at a path inside another worktree
- Don't `git checkout` a branch that's already checked out in another
  worktree — the create will fail with a clear error
- Don't `git worktree remove` a worktree whose directory is on a
  network mount that's currently disconnected — use `--force` only if
  you've confirmed the contents are unrecoverable
- Don't forget that deleting the worktree directory out-of-band
  requires a follow-up `git worktree prune` to clean metadata
