---
name: context
description: "Attach, replace, and inspect context payloads for Claude Code sessions. Complex structures travel as JSON-serialized strings."
allowed-tools: Read, Bash, Grep, Glob
when_to_use: "Use when invoking the wrapper's `context_*` MCP tools to attach files, knowledge blobs, or task context to a session. Triggers on 'attach context', 'add file', 'load context', 'replace context'. Do NOT use for prompt execution (use execute) or session lifecycle (use session)."
argument-hint: "[attach|list|get|replace|clear] [--session-id <uuid>] [--payload <json-string>]"
---

**Persona:** You are the `context` spoke. You own the attachment of opaque knowledge payloads to a session. The wrapper NEVER interprets payload contents — it only stores, retrieves, and replaces.

## Tool Surface

Five MCP tools. All accept opaque JSON-serialized strings for any non-trivial structure.

| Tool | MCP name | Purpose |
|------|----------|---------|
| `context_attach` | `mcp__claude-cli-wrapper__context_attach` | Append a payload to a session's context. |
| `context_list` | `mcp__claude-cli-wrapper__context_list` | Enumerate context entries by ID. |
| `context_get` | `mcp__claude-cli-wrapper__context_get` | Retrieve a single context entry. |
| `context_replace` | `mcp__claude-cli-wrapper__context_replace` | Swap a context entry's contents in place. |
| `context_clear` | `mcp__claude-cli-wrapper__context_clear` | Remove one or all context entries. |

### Parameters (flat, ≤2 levels)

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `session_id` | string (UUID) | yes (except list) | Target session. MUST match UUID v4. |
| `payload` | string | yes (attach/replace) | JSON-serialized structure. Pass-through; not parsed. |
| `entry_id` | string | no | Opaque identifier for an existing entry. Wrapper assigns on attach. |
| `kind` | enum | no | `file` / `text` / `reference` / `blob`. Default: `text`. |
| `label` | string | no | Human-readable label, never interpreted. |
| `limit` | integer | no (list) | Max entries to return; default 50. |
| `cursor` | string | no (list) | Opaque pagination cursor. |
| `all` | boolean | no (clear) | If true, clear all entries; default false. |

## Mechanism

1. **UUID validation on every tool** that takes `session_id`. Reject before any storage call.
2. **Pass-through principle for `payload`.** The wrapper MUST NOT attempt to parse, validate, or reformat the JSON. It is a string in, a string out.
3. **Size guard.** Reject payloads whose UTF-8 byte length exceeds the configured cap (default 5 MiB). The cap is in `config-file.md`.
4. **Append-only by default.** `context_attach` does NOT overwrite existing entries; use `context_replace` for that.
5. **Pagination.** `context_list` returns opaque `cursor` strings; the wrapper never decodes them.

## Anti-Patterns

- **NEVER parse the `payload` string inside the wrapper** to extract fields, validate schema, or normalize formatting.
- **NEVER accept a `payload` object directly** — the surface is flat strings only. Callers serialize first.
- **NEVER clear all context implicitly.** `context_clear` defaults to one-entry clearing; `all=true` is opt-in.
- **NEVER expose nested `metadata` blocks.** If the caller wants metadata, they encode it inside `payload`.

CONTRAST:
- NOT for: executing prompts (use `execute`).
- NOT for: session creation (use `session`).
- NOT for: reviewing code (use `review`).

## References

You MUST read `references/schema-reference.md` BEFORE introducing any nested object — flat surface is mandatory.
You MUST read `references/config-file.md` for the payload size cap and the storage backend selection.
