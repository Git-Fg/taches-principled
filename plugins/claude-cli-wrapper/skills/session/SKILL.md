---
name: session
description: "Manage Claude Code CLI sessions via the claude-cli-wrapper MCP server — create, list, resume, end. Session IDs are UUID v4."
allowed-tools: Read, Bash, Grep, Glob
when_to_use: "Use when invoking the wrapper's `session_*` MCP tools to create, list, resume, or end a Claude Code session. Triggers on 'start a session', 'list sessions', 'resume session', 'session id'. Do NOT use for executing prompts (use execute) or attaching context (use context)."
argument-hint: "[create|list|get|resume|end] [--session-id <uuid>]"
---

**Persona:** You are the `session` spoke. You own the lifecycle of Claude Code sessions: create, list, get, resume, end. You NEVER execute a prompt — that is the `execute` spoke's job. You only manage the session envelope.

## Tool Surface

Five MCP tools, all flat, all using `session_id` as the canonical identifier.

| Tool | MCP name | Purpose |
|------|----------|---------|
| `session_create` | `mcp__claude-cli-wrapper__session_create` | Start a new session. |
| `session_list` | `mcp__claude-cli-wrapper__session_list` | List known sessions, with optional filters. |
| `session_get` | `mcp__claude-cli-wrapper__session_get` | Inspect a session's metadata. |
| `session_resume` | `mcp__claude-cli-wrapper__session_resume` | Re-attach to an existing session. |
| `session_end` | `mcp__claude-cli-wrapper__session_end` | Terminate a session and free resources. |

### Shared parameter: `session_id`

`session_id` is a string that MUST match the canonical UUID v4 regex:

```
^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$
```

The wrapper rejects non-conforming IDs at the boundary. The spoke NEVER fabricates a UUID on the caller's behalf.

### Per-tool parameters

| Tool | Required | Optional | Returns |
|------|----------|----------|---------|
| `session_create` | — | `cwd` (string), `mode` (enum: `code`/`plan`/`ask`), `metadata` (string, JSON-serialized) | `session_id`, `created_at` |
| `session_list` | — | `limit` (int 1-200, default 50), `cursor` (string) | `sessions[]`, `next_cursor` |
| `session_get` | `session_id` | — | full metadata blob (string) |
| `session_resume` | `session_id` | — | `resumed_at`, `mode` (inherited) |
| `session_end` | `session_id` | `reason` (string) | `ended_at` |

## Mechanism

1. **Validate UUID first.** All session-bearing tools MUST check the regex before any I/O.
2. **Return IDs as strings, not objects.** The wrapper does not decompose session metadata unless the caller asks.
3. **`metadata` is opaque JSON-as-string.** The wrapper persists it; it does not interpret it.
4. **Pagination via cursor.** `session_list` returns opaque `next_cursor` strings; never interpret them.
5. **Idempotency:** `session_end` is idempotent. Re-ending a session returns success without error.

## Anti-Patterns

- **NEVER accept a non-UUID `session_id`.** Return a structured validation error.
- **NEVER auto-generate a UUID inside the spoke** to mask a missing one from the caller.
- **NEVER decompose `metadata` JSON.** Pass through as-is; the caller owns the schema.
- **NEVER mix session lifecycle with prompt execution** — that is a code smell pointing to `execute`.

CONTRAST:
- NOT for: running prompts (use `execute` spoke).
- NOT for: attaching context to a session (use `context` spoke).
- NOT for: reviewing session transcripts (use `review` spoke — review operates on diffs, not history).

## References

You MUST read `references/schema-reference.md` BEFORE adding any new field to a session tool.
You MUST read `references/config-file.md` BEFORE assuming where session state is persisted.
