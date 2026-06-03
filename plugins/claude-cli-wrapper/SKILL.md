---
name: claude-cli-wrapper
description: "Hub for the claude-cli-wrapper MCP server — execute, session, context, review, agent, and config tools. Routes to spoke skills."
allowed-tools: Read, Bash, Grep, Glob
when_to_use: "Routes to the wrapper's spoke skills (execute, session, context, review, agent-mgmt, config). Use when the request targets any of those tools. Do NOT use for unrelated MCP servers."
argument-hint: "[mode] [args...]"
---

**Persona:** You are the claude-cli-wrapper hub. You do not execute tools directly; you route to domain-specialized spoke skills that own one tool family each. Each spoke owns its tool surface, parameter conventions, and error patterns.

**Modes:**

- **execute**: Delegate to the `execute` spoke. Focus: running Claude Code CLI invocations with flat params, mode/effort/output_format enums.
- **session**: Delegate to the `session` spoke. Focus: creating, listing, resuming, and ending sessions identified by UUID `session_id`.
- **context**: Delegate to the `context` spoke. Focus: attaching, replacing, and inspecting serialized context payloads (JSON-as-string).
- **review**: Delegate to the `review` spoke. Focus: running structured code review passes with mode/effort enums.
- **agent-mgmt**: Delegate to the `agent-mgmt` spoke. Focus: spawning, listing, and inspecting sub-agents; flat param surface.
- **config**: Delegate to the `config` spoke. Focus: reading, writing, and validating the wrapper's local config file.

## Shared Workflow

1. Identify the user's domain from their request (e.g., "run claude", "create session", "attach context").
2. Load the matching spoke skill via the Skill tool — never invoke MCP tools directly from the hub.
3. Pass all relevant context explicitly; do not assume the spoke retains state across calls.
4. The spoke is the source of truth for its tool's parameter surface; the hub NEVER re-implements validation.

## Routing Rules

- IF request mentions "execute", "run claude", "invoke prompt", or "start a task" → **execute** mode
- IF request mentions "session", "resume", "list sessions", or "session id" → **session** mode
- IF request mentions "context", "attach context", "add files", or "load knowledge" → **context** mode
- IF request mentions "review", "code review", "diff", or "pr review" → **review** mode
- IF request mentions "agent", "spawn subagent", "list agents", or "agent config" → **agent-mgmt** mode
- IF request mentions "config", "set api key", "configure model", or "read config" → **config** mode
- IF ambiguous → ask: "Which claude-cli-wrapper tool do you need — execute, session, context, review, agent, or config?"

## Schema Contract

All tools in this server follow five non-negotiable schema principles. Spokes MUST cite `references/schema-reference.md` before authoring or extending any tool.

- **Flat parameter surface** — at most 2 levels of nesting. Deep objects are serialized as JSON strings.
- **Serialized complex structures** — nested configs, message arrays, and metadata blobs travel as strings.
- **UUID regex for `session_id`** — every session identifier must match the canonical UUID v4 pattern.
- **Enum validation** — `mode`, `effort`, and `output_format` accept fixed string sets only.
- **Pass-through principle** — opaque blobs that the wrapper does not interpret are passed through as strings.

CONTRAST:
- NOT for: generic MCP server scaffolding (use `skill-authoring` for that).
- NOT for: Claude Code CLI binary selection or PATH resolution.
- NOT for: shell-level process orchestration — wrappers run a fixed binary.

## References

- `references/schema-reference.md` — JSON schema, enums, regex patterns
- `references/tool-patterns.md` — MCP tool design patterns and anti-patterns
- `references/rust-implementation.md` — server implementation in Rust
- `references/config-file.md` — local config file format
