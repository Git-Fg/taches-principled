# Scheduled Tasks — `/loop` and Cron

**Canonical source:** https://code.claude.com/docs/en/scheduled-tasks
**Scope:** Local, session-scoped scheduling. Re-runs a prompt on an interval or at a one-shot time, lives in the current conversation, stops when you start a new one.

## `/loop` modes

| Provided | Example | Behavior |
|---|---|---|
| Interval + prompt | `/loop 5m check the deploy` | Fixed cron schedule |
| Prompt only | `/loop check the deploy` | **Dynamic interval — Claude picks the wait after each iteration** (1 min to 1 hour) |
| Interval only or nothing | `/loop` | Built-in maintenance prompt (or your `loop.md` if present) |

You can also chain commands: `/loop 20m /review-pr 1234` re-runs a saved command each iteration.

## Customizing the default prompt

Drop a `loop.md` at:
- `.claude/loop.md` — project-level, wins when both exist
- `~/.claude/loop.md` — user-level

When neither exists, `/loop` (no prompt) uses the built-in maintenance prompt: continue unfinished work → tend the branch's PR → run cleanup passes. Irreversible actions only proceed when they continue something the transcript already authorized.

## Underlying tools

| Tool | Purpose |
|---|---|
| `CronCreate` | Schedule a new task. Takes 5-field cron, prompt, recurring flag |
| `CronList` | List all scheduled tasks with IDs, schedules, prompts |
| `CronDelete` | Cancel by 8-char ID |
| `ScheduleWakeup` | Used by `/loop` dynamic mode — schedules the next iteration after the current turn |

Session cap: 50 scheduled tasks.

## Jitter (the deterministic-offset gotcha)

To avoid every session hitting the API at the same wall-clock moment:
- **Recurring** tasks fire up to 30 minutes after the scheduled time (or up to half the interval for sub-hourly). Hourly `:00` jobs may fire anywhere up to `:30`.
- **One-shot** tasks scheduled for the top or bottom of the hour fire up to 90 seconds early.
- Offset is derived from the task ID — same task, same offset.

**Workaround:** pick a non-`:00`/`:30` minute (`3 9 * * *`) and the one-shot jitter does not apply.

## Hard limits

- Recurring tasks auto-expire **7 days** after creation. Final fire then deletion.
- Starting a fresh conversation clears all session-scoped tasks
- Resuming with `--resume` / `--continue` restores tasks that haven't expired
- Background bash and monitor tasks are NEVER restored on resume

## Disable

`CLAUDE_CODE_DISABLE_CRON=1` removes `/loop` and the cron tools entirely.

## ScheduleWakeup — the dynamic /loop primitive

A `/loop` without an interval uses `ScheduleWakeup(delaySeconds, reason, prompt)`. The runtime clamps to `[60, 3600]`. After each iteration the prompt picks the next delay based on what it observed (short while CI is finishing, long when nothing is pending). The chosen delay and rationale are printed at the end of each iteration.

The seven-day expiry still applies, but the jitter rules do **not** apply to dynamic loops.

## Picking `delaySeconds`

From the `ScheduleWakeup` tool's own guidance: the Anthropic prompt cache has a 5-minute TTL. Sleeping past 300 seconds means the next wake-up reads your full conversation context uncached — slower and more expensive.

- **Under 5 min (60s–270s)**: cache stays warm. Right for actively polling external state.
- **5 min to 1 hour (300s–3600s)**: pay the cache miss. Right when there's no point checking sooner.
- **Don't pick 300s.** Worst-of-both — cache miss without amortizing it. Either drop to 270s (stay in cache) or commit to 1200s+.
- **Default for idle ticks:** 1200s–1800s (20–30 min).

This guidance applies the same way against a custom endpoint as long as the endpoint also implements prompt caching with a similar TTL — verify with your provider.

## Monitor tool (the alternative to polling)

The doc names this explicitly: **when you ask for a dynamic `/loop` schedule, Claude may use the Monitor tool directly instead.** Monitor runs a background script and streams each output line back as it appears — no polling, more token-efficient, more responsive.
