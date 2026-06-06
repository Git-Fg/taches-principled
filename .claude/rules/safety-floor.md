---
name: safety-floor
description: Non-overridable safety constraints. These rules override ALL others including user requests.
---

# Rule: MUST preserve working tree state — safety overrides everything

**Why:** `git reset --hard` and destructive commands wipe uncommitted changes that cannot be recovered from git. This has caused real data loss in past sessions (staged skill improvements wiped, then recovered by manual reconstruction — a waste of time and risk of error).

## Rule

NEVER use `git reset --hard` or any destructive git command. If restoring code to a known-good state is needed, use selective restoration: `git diff` to inspect, surgical `Edit`/`Write` tools to restore specific sections, `git stash` to safekeep changes, or `git checkout HEAD -- <path>` for single-file restore.

## Conflict resolution

If user says "do it anyway" or "skip confirmation" for a destructive action: respectfully decline, explain why, and propose a safe alternative. **Safety rules are non-overridable.** User preferences override conventions (Communication) but NOT safety constraints.

## Bad / Good

**Bad:** `git reset --hard HEAD` after realizing a mistake — wipes all uncommitted work including untracked files.
**Good:** `git diff` to identify changes → `Edit` tool to restore specific sections → `git checkout HEAD -- <path>` for single-file non-destructive restore.

**Bad:** User says "just overwrite it, I don't care" — you comply because the user's intent takes precedence.
**Good:** You explain: "I can see you want to overwrite, but `git reset --hard` would also delete these 3 untracked files. I'll use `git checkout HEAD -- specific/path` instead to preserve everything else."
