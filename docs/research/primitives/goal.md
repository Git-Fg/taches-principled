# `/goal` — Keep working toward a condition

**Canonical source:** https://code.claude.com/docs/en/goal

## What it is

Sets a **completion condition** for the session. After each turn, a small fast model checks whether the condition holds. If not, Claude starts another turn instead of returning control. The goal clears automatically once the condition is met.

## How it compares to the other "keep going" mechanisms

| Approach | Next turn starts when | Stops when |
|---|---|---|
| `/goal` | Previous turn finishes | A model confirms the condition |
| `/loop` | A time interval elapses | You stop it, or Claude decides done |
| **Stop hook** | Previous turn finishes | Your own script / prompt decides |

`/goal` and Stop hooks both fire after every turn. `/goal` is session-scoped (one condition active per session); Stop hooks are settings-file scoped (apply to every session in scope) and can run a script for deterministic checks or a prompt for model-evaluated ones.

**`/goal` is a wrapper around a session-scoped prompt-based Stop hook.**

## Use cases the doc names

- Migrating a module to a new API until every call site compiles and tests pass
- Implementing a design doc until all acceptance criteria hold
- Splitting a large file until each piece is under a size budget
- Working through a labeled issue backlog until the queue is empty

## Writing an effective condition

The evaluator judges your condition against **what Claude has surfaced in the conversation** — it doesn't run commands or read files independently. Write the condition as something Claude's own output can demonstrate.

A condition that holds up across many turns usually has:
- **One measurable end state** — test result, build exit code, file count, empty queue
- **A stated check** — how Claude should prove it (`npm test exits 0`, `git status is clean`)
- **Constraints that matter** — what must not change on the way there

Up to 4,000 characters.

**Bound the run:** include a turn or time clause (`or stop after 20 turns`). Claude reports progress against the clause each turn.

## Commands

| Command | Effect |
|---|---|
| `/goal <condition>` | Set or replace the active goal; starts a turn immediately with the condition as directive |
| `/goal` | Show status (condition, duration, turn count, token spend, last evaluator reason) |
| `/goal clear` | Remove active goal (also: `stop`, `off`, `reset`, `none`, `cancel`) |

`/clear` (starting a new conversation) also removes any active goal.

## Resume behavior

Active goals carry over with `--resume` / `--continue`. **Turn count, timer, and token-spend baseline reset on resume.** Already-achieved or cleared goals don't restore.

## Non-interactive

```bash
claude -p "/goal CHANGELOG.md has an entry for every PR merged this week"
```

Runs the loop to completion in a single invocation. Ctrl+C interrupts.

## Auto mode + `/goal` is the productive combo

> "Auto mode on its own approves tool calls within a single turn but doesn't start a new one. Claude stops when it judges the work done. `/goal` adds a separate evaluator that checks your condition after every turn, so completion is decided by a fresh model rather than the one doing the work. The two are complementary: auto mode removes per-tool prompts, and `/goal` removes per-turn prompts."

## Requirements

- Workspace trust dialog must be accepted (evaluator is part of the hooks system)
- Unavailable when `disableAllHooks` or `allowManagedHooksOnly` is set
