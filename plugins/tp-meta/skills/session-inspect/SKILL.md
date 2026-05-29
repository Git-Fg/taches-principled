---
name: session-inspect
description: "Parse Claude Code session transcripts (JSONL) into structured data — tool calls, errors, cost, loaded plugins, and behavioral events."
allowed-tools: Read, Glob, Grep, Bash
when_to_use: |
  Use when the user says:
  - "inspect session"
  - "parse transcript"
  - "analyze session log"
  - "what happened in this session"
  - "session metrics"
  - "parse jsonl"
  - "read the session transcript"
  FIRST when any meta-review or behavioral analysis needs raw session data.
  Do NOT use for reviewing code (use code-review) or diagnosing bugs (use diagnose).
argument-hint: "[latest|<session-id>] [--full|--summary] [--filter errors|tools|cost]"
---

## What This Skill Changes

**Default behavior:** Claude reads raw session JSONL ad-hoc — field extraction by grep, inconsistent error handling, no standardized output format, and no systemic privacy scrub.

**With this skill:** Standardized three-mode extraction (SUMMARY / FULL / FILTER) with explicit output formats, behavioral-only data retention, and a privacy protocol that strips credentials and paths automatically. Session analysis becomes comparable across runs.

**Why privacy matters:** Session logs contain file paths, user prompts, environment variables, and tool arguments — information that must not leak into public reports or cross-session memory. This skill enforces that boundary automatically.

---

## Decision Router

IF user wants a quick overview of recent session → **SUMMARY** mode (default)
IF user wants complete structured extraction → **FULL** mode
IF user wants specific event filtering → **FILTER** mode

---

## Session Discovery

Claude Code stores session transcripts at `~/.claude/sessions/{uuid}/raw-transcript.jsonl`.

### Finding the Right Session

1. **Latest session**: `ls -t ~/.claude/sessions/ | head -1` → use that UUID
2. **By ID**: user provides the UUID directly
3. **By content**: grep across sessions for a keyword the user remembers

If no session ID provided and latest session is empty or still running, try the previous one.

---

## SUMMARY Mode

Read `raw-transcript.jsonl` and extract:

1. **Session metadata** — `session_id`, `duration_ms`, `total_cost_usd`, `stop_reason`
2. **Environment loaded** — from `system.init` event: plugins, hooks, rules, skills that were active
3. **Tool call count** — total, by tool name, error count
4. **Error events** — `tool_result` with `subtype: error`, with error messages
5. **Result** — final `result` event with cost and token usage

Output format:
```
Session: {uuid}
Duration: {ms}ms | Cost: ${cost}
Tools: {count} calls ({errors} errors)
Plugins: {list or NONE}
Rules: {list or NONE}
Hooks: {list or NONE}
Result: {success|error} — {stop_reason}
```

---

## FULL Mode

Same as SUMMARY plus:

6. **Every tool call** — tool name, arguments (sanitized), result status, duration
7. **Assistant messages** — count and length (no content — too large)
8. **Init event details** — full environment snapshot
9. **Git state** — if git operations occurred, capture branch and diff stats

Output as structured JSON to `.principled/scratch/session-inspect-{uuid}.json`.

---

## FILTER Mode

Accepts `--filter` with one of:
- `errors` — only error events with context
- `tools` — only tool_use and tool_result events
- `cost` — only result events with cost breakdown
- `skills` — only skill loading events

Pipes through jaq if available, otherwise uses Bash text filtering.
