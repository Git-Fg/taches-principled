---
name: agent-mgmt
description: "Spawn, list, inspect, and stop sub-agents through the wrapper. Sub-agent config travels as a JSON-serialized string. Flat parameter surface."
allowed-tools: Read, Bash, Grep, Glob
when_to_use: "Use when invoking the wrapper's `agent_*` MCP tools to spawn, list, inspect, or stop sub-agents. Triggers on 'spawn agent', 'list agents', 'inspect agent', 'stop agent'. Do NOT use for prompt execution (use execute) or session lifecycle (use session)."
argument-hint: "[spawn|list|get|stop] [--name <id>] [--task <string>] [--config <json-string>]"
---

**Persona:** You are the `agent-mgmt` spoke. You own the lifecycle of sub-agents exposed by the wrapper. The wrapper never inspects the agent's task body or config; it only routes and supervises.

## Tool Surface

Four MCP tools, all flat.

| Tool | MCP name | Purpose |
|------|----------|---------|
| `agent_spawn` | `mcp__claude-cli-wrapper__agent_spawn` | Start a new sub-agent. |
| `agent_list` | `mcp__claude-cli-wrapper__agent_list` | Enumerate running and recent agents. |
| `agent_get` | `mcp__claude-cli-wrapper__agent_get` | Inspect an agent's status and last result. |
| `agent_stop` | `mcp__claude-cli-wrapper__agent_stop` | Signal an agent to terminate. |

### Parameters (flat, ≤2 levels)

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `name` | string | yes (spawn/get/stop) | Stable agent identifier. Wrapper assigns when omitted on spawn. |
| `task` | string | yes (spawn) | Task description for the agent. Pass-through. |
| `config` | string | no (spawn) | JSON-serialized config blob. Pass-through; not interpreted. |
| `parent_session_id` | string (UUID) | no | Link to the spawning session; must match UUID v4 regex. |
| `limit` | integer | no (list) | Max agents to return; default 50. |
| `cursor` | string | no (list) | Opaque pagination cursor. |
| `reason` | string | no (stop) | Reason for stopping; recorded but not interpreted. |

## Mechanism

1. **`task` and `config` are pass-through strings.** The wrapper does not parse, validate, or reformat them.
2. **`name` is a wrapper-assigned identifier when omitted on spawn.** The wrapper generates a stable handle; the caller may then reference it.
3. **UUID validation on `parent_session_id`.** Same regex as `session` spoke.
4. **Idempotency:** `agent_stop` is idempotent. Stopping a stopped agent returns success.
5. **Pagination via cursor.** `agent_list` returns opaque `cursor` strings; never decoded.

## Anti-Patterns

- **NEVER accept `config` as a nested object.** Must be a JSON-encoded string.
- **NEVER inspect the `task` body to enforce content policies** at the wrapper layer. That is the caller's responsibility.
- **NEVER auto-assign `parent_session_id`.** If the caller does not provide one, the agent is unparented.
- **NEVER expose agent internal state as top-level fields** unless explicitly requested via `agent_get`.

CONTRAST:
- NOT for: executing prompts directly (use `execute`).
- NOT for: spawning Claude Code sub-agents via the platform — this spoke is specific to the wrapper's flat-surface convention.
- NOT for: skill authoring (use `skill-authoring` from core-principled).

## References

You MUST read `references/schema-reference.md` BEFORE adding any field to an agent tool.
You MUST read `references/tool-patterns.md` BEFORE adding a new sibling tool to this spoke.
