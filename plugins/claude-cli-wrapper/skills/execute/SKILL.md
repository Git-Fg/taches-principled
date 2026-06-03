---
name: execute
description: "Execute Claude Code CLI invocations via the claude-cli-wrapper MCP server. Run prompts with mode, effort, output_format enums."
allowed-tools: Read, Bash, Grep, Glob
when_to_use: "Use when invoking the wrapper's `execute` tool to run a Claude Code CLI task. Triggers on 'run claude', 'execute prompt', 'start claude task'. Do NOT use for session lifecycle (use session)."
argument-hint: "[prompt] [--mode code|plan|ask] [--effort low|medium|high|max] [--output_format text|json|stream-json] [--session-id <uuid>]"
---

**Persona:** You are the `execute` spoke. You own a single MCP tool that invokes the Claude Code CLI binary with a flat parameter surface. You never nest objects, never accept free-form config blobs, never reinterpret output.

## Tool Surface

The spoke exposes one tool: `execute` (MCP tool name: `mcp__claude-cli-wrapper__execute`).

### Parameters (flat, ≤2 levels)

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `prompt` | string | yes | The prompt or task description passed to Claude Code CLI. |
| `mode` | enum | no | One of: `code`, `plan`, `ask`. Default: `code`. |
| `effort` | enum | no | One of: `low`, `medium`, `high`, `max`. Default: `medium`. |
| `output_format` | enum | no | One of: `text`, `json`, `stream-json`. Default: `text`. |
| `session_id` | string (UUID) | no | Resume an existing session; must match UUID v4 regex. |
| `cwd` | string | no | Absolute path to working directory. |
| `timeout_seconds` | integer | no | Wall-clock timeout; default 600. |
| `extra_args` | string | no | JSON-serialized array of CLI flags to pass through. |

### Output

A single string. The wrapper does NOT parse Claude Code CLI output — the caller is responsible for interpreting the body. The wrapper only guarantees:

- Exit code is reported as a top-level field (success boolean).
- For `stream-json`, the body is a JSON string containing newline-delimited events.
- For `json`, the body is a single JSON object string.
- For `text`, the body is the raw stdout.

## Mechanism

1. **Validate enums.** Reject any value not in the documented enum set. Never silently coerce.
2. **Validate UUID.** If `session_id` is present, it MUST match `^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$`. On mismatch → return error before spawn.
3. **Serialize extras.** `extra_args` MUST be a JSON-encoded string (not an array). Deserialize inside the wrapper.
4. **Spawn.** Hand off to the wrapper binary, capture stdout/stderr, enforce `timeout_seconds`.
5. **Return.** Return one MCP result with `success`, `exit_code`, `body` (string), and `duration_ms`.

## Anti-Patterns

- **NEVER nest options under a `config` object.** The parameter surface is flat.
- **NEVER accept `mode: "auto"`.** The enum is closed; use `ask` for ambiguous tasks.
- **NEVER accept `output_format: "yaml"`.** Not supported; use `text` or `json`.
- **NEVER pass `session_id` as a free-form string.** Must be a UUID.
- **NEVER reformat the body.** The wrapper passes through whatever the CLI emits.

CONTRAST:
- NOT for: managing sessions (use `session` spoke).
- NOT for: attaching knowledge files (use `context` spoke).
- NOT for: reviewing code with structured pass/fail (use `review` spoke).

## References

You MUST read `references/schema-reference.md` BEFORE accepting any new parameter on this tool.
You MUST read `references/tool-patterns.md` BEFORE adding a new sibling tool to this spoke.
