---
name: claude-cli
description: Drive the Claude Code CLI as six MCP tools from another agent — claude_execute (run a prompt), claude_session (lifecycle: resume/continue/fork/list/info/close), claude_context (workspace: add dirs, worktrees), claude_review (code review), claude_agent (background agent management), claude_config (runtime tuning: model/effort/permissions/settings). Use when an agent needs to programmatically spawn or orchestrate Claude Code instances, manage their sessions, or run background sub-agents — not for direct user-driven Claude Code use.
---

# claude-cli

The `claude-cli-wrapper` plugin exposes a flat, agent-callable surface over the
Claude Code CLI. This skill is a user-facing map of the 6 tools and when to
reach for which one. For the MCP design principles these tools embody (flat
schema, pass-through, output contract), see `mcp-server-design`. For
implementation details, see `mcp-server-implement`.

---

## §1. When this skill fires

**Use this skill when the user says any of:**
- "Run Claude Code on this prompt" / "spawn a Claude Code agent"
- "Continue / resume / fork a Claude Code session"
- "List my Claude Code sessions"
- "Review this PR with Claude Code"
- "Spawn a background Claude agent"
- "Set the model / effort / permissions for Claude Code"
- "Wrap Claude Code as a tool for my agent"
- "Drive Claude Code programmatically"

**DO NOT use this skill for:**
- "How do I design an MCP server" → `mcp-server-design`
- "How do I implement an MCP server in Rust" → `mcp-server-implement`
- "How do I write a good JSON Schema" → `mcp-tool-surface`
- "How do I write a Claude Code hook" / "slash command" → not covered here

---

## §2. The 6-tool surface

| Tool | Operational domain | When to use |
|---|---|---|
| `claude_execute` | Run a prompt, get structured output | The primary tool — use this 80% of the time |
| `claude_session` | Lifecycle (resume/continue/fork/list/info/close) | Re-using or inspecting a previous Claude Code session |
| `claude_context` | Workspace (add dirs, worktrees, doctor) | Pre-load a workspace before `claude_execute` |
| `claude_review` | Code review (ultrareview) | Code-reviewing a branch or PR |
| `claude_agent` | Background agent management | Spawn a Claude Code sub-agent that runs in the background |
| `claude_config` | Runtime tuning (model/effort/permissions/settings) | Set session-level config without re-running |

**Total: ~41 parameters across 6 tools, each schema < 2 KB serialized.**

This is the **decomposition pattern from the doc** — instead of exposing all 50+ Claude Code CLI flags in one tool, they're split into 6 thematic tools. Tool selection accuracy stays high; each tool's schema stays under the context budget.

---

## §3. `claude_execute` — the primary tool

Run a prompt, get structured output. This is the workhorse.

**Key parameters (out of 18):**
- `prompt` (string, required, max 16384 chars) — the prompt to send
- `mode` (enum: `print` | `interactive`, default `print`) — headless vs TTY
- `output_format` (enum: `text` | `json` | `stream-json`, default `json`) — serialization
- `session_id` (UUID, optional) — resume this specific session
- `continue_session` (boolean, default false) — continue the most recent session in cwd
- `model` (string, optional) — `sonnet`, `opus`, or full name
- `effort` (enum: `low` | `medium` | `high` | `xhigh` | `max`) — reasoning effort
- `max_budget_usd` (number, 0-1000) — spend cap for this invocation
- `allowed_tools` / `disallowed_tools` (array, max 20) — tool allow/deny
- `system_prompt` (string, max 32768) / `append_system_prompt` (max 8192) — override or extend
- `structured_output_schema_json` (string, max 8192) — **pass-through** for JSON Schemas
- `permission_mode` (enum: `acceptEdits` | `auto` | `bypassPermissions` | `default` | `dontAsk` | `plan`)
- `bare_mode` (boolean) — minimal mode, skips hooks/LSP/plugins
- `mcp_configs` / `plugin_dirs` / `strict_mcp_config` — load additional context
- `name` (string, optional) — display name for the session
- `files` (array, max 5) — preloaded file resources
- `context_dirs` (array, max 10) — additional dirs to allow tool access
- `settings_file` (string, max 1024) — JSON settings file or inline JSON

**Key design notes:**
- `prompt` is the only required field. Everything else is optional with sensible defaults.
- `mode` defaults to `print` (headless) because AI agents are the primary consumers.
- `structured_output_schema_json` is a STRING, not a nested object — flat schema, deep data via pass-through (see `mcp-server-design` §2).
- `session_id` uses a strict UUID regex to prevent garbage.
- `continue_session` and `session_id` are mutually meaningful: `session_id` wins if both are set; `continue_session` is "most recent in this dir" shorthand.

**Example call (the most common one):**
```json
{
  "prompt": "Find the file in src/ that defines the User struct and add a Display impl",
  "mode": "print",
  "output_format": "json",
  "model": "sonnet",
  "effort": "high",
  "permission_mode": "acceptEdits"
}
```

**Example with structured output (pass-through):**
```json
{
  "prompt": "Analyze this Rust function for bugs",
  "output_format": "json",
  "structured_output_schema_json": "{\"type\":\"object\",\"properties\":{\"bugs\":{\"type\":\"array\",\"items\":{...}},\"severity\":{...}},\"required\":[\"bugs\"]}"
}
```

---

## §4. `claude_session` — lifecycle

Resume, continue, fork, list, info, or close a session.

**Single `action` enum as discriminator** (instead of 6 sibling tools):
```json
{
  "action": {
    "type": "string",
    "enum": ["resume", "continue", "fork", "list", "info", "close"],
    "description": "Session lifecycle action."
  },
  "session_id": {
    "type": "string",
    "pattern": "^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$",
    "description": "Required for resume, continue, fork, info, close. UUID format."
  },
  "session_name": { "type": "string", "maxLength": 64 },
  "search_term": { "type": "string", "maxLength": 128 }
}
```

**Per-action semantics:**
- `resume` + `session_id` — continue an existing session, return its context
- `continue` (no `session_id`) — continue the most recent session in cwd
- `fork` + `session_id` — create a new session branched from the existing one
- `list` (+ `search_term`) — list all known sessions, optionally filtered
- `info` + `session_id` — get metadata about a specific session
- `close` + `session_id` — terminate and clean up a session

**Design note:** the action enum is the discriminator; the server validates cross-field requirements (`session_id` required for most actions).

---

## §5. `claude_context` — workspace

Add directories, set up git worktrees, run diagnostics.

```json
{
  "action": {
    "type": "string",
    "enum": ["add_directory", "setup_worktree", "doctor"]
  },
  "directory_path": { "type": "string", "maxLength": 1024 },
  "worktree_name": {
    "type": "string",
    "maxLength": 64,
    "pattern": "^[a-zA-Z0-9_-]+$"
  }
}
```

**Per-action:**
- `add_directory` + `directory_path` — register a directory for tool access
- `setup_worktree` + `worktree_name` — create an isolated git worktree for the session
- `doctor` — run Claude Code's self-diagnostics, return health report

---

## §6. `claude_review` — code review

```json
{
  "target": {
    "type": "string",
    "maxLength": 256,
    "description": "Review target: 'current' for current branch, PR number/URL, or branch name."
  },
  "base_branch": {
    "type": "string",
    "maxLength": 128,
    "description": "Base branch for comparison. Omit to use repository default."
  },
  "output_format": {
    "type": "string",
    "enum": ["text", "json"],
    "default": "json"
  }
}
```

`target` is required. `base_branch` defaults to the repo's default branch. The review is structured (comments per file, severity per finding, suggested fix) when `output_format=json`.

---

## §7. `claude_agent` — background sub-agents

```json
{
  "action": {
    "type": "string",
    "enum": ["list", "spawn", "status", "terminate"]
  },
  "agent_name": {
    "type": "string",
    "maxLength": 64,
    "pattern": "^[a-zA-Z0-9_-]+$"
  },
  "agent_description": { "type": "string", "maxLength": 256 },
  "agent_prompt": { "type": "string", "maxLength": 8192 }
}
```

**Per-action:**
- `list` — show running and recent background agents
- `spawn` + `agent_name` + `agent_description` + `agent_prompt` — start a new background agent
- `status` + `agent_name` — check progress of a background agent
- `terminate` + `agent_name` — stop a running agent

**Use this when:** you want Claude Code to work in the background while your agent does other things. The agent has its own session, can use tools, and reports back via `status` or `claude_execute(session_id=...)` to retrieve results.

---

## §8. `claude_config` — runtime tuning

```json
{
  "action": {
    "type": "string",
    "enum": ["set_model", "set_effort", "set_permissions", "load_settings"]
  },
  "model_value": { "type": "string", "maxLength": 64 },
  "effort_value": { "type": "string", "enum": ["low", "medium", "high", "xhigh", "max"] },
  "permissions_value": {
    "type": "string",
    "enum": ["acceptEdits", "auto", "bypassPermissions", "default", "dontAsk", "plan"]
  },
  "settings_path": { "type": "string", "maxLength": 1024 }
}
```

**Per-action:**
- `set_model` + `model_value` — change the model for the current session
- `set_effort` + `effort_value` — change the reasoning effort
- `set_permissions` + `permissions_value` — change the permission mode
- `load_settings` + `settings_path` — load a JSON settings file

**Note:** these set the session-level config without re-running `claude_execute`. Use this for tweaking mid-session.

---

## §9. Output contract

All 6 tools return `CallToolResult` with text containing a JSON object:

```json
{
  "exit_code": 0,
  "stdout": "...",
  "stderr": "",
  "session_id": "uuid",
  "output_parsed": { ... },
  "error": null
}
```

**Fields:**
- `exit_code` — Claude Code process exit code (0 = success)
- `stdout` — raw stdout (or pre-parsed JSON if `output_format=json`)
- `stderr` — error stream
- `session_id` — UUID for continuity with subsequent calls
- `output_parsed` — convenience: pre-parsed JSON when valid
- `error` — error description if `exit_code != 0`

**Errors use JSON-RPC codes:**
- `-32602` (invalid params) — schema violation, bad UUID, missing required
- `-32001` (custom) — Claude Code exited non-zero
- `-32002` (custom) — rate limited or budget exceeded
- `-32603` (internal error) — wrapper crash (rare; indicates a bug)

---

## §10. Common workflows

**Workflow 1: One-shot task**
```json
claude_execute({
  "prompt": "Refactor user.rs to use the newtype pattern",
  "mode": "print",
  "permission_mode": "acceptEdits"
})
```

**Workflow 2: Multi-turn session with continuity**
```json
// Turn 1
claude_execute({ "prompt": "Start a refactor of the auth module" })
// → response.session_id = "abc-123-..."

// Turn 2 (later)
claude_execute({ "prompt": "Continue: also add tests", "session_id": "abc-123-..." })
```

**Workflow 3: Background agent + polling**
```json
// Spawn
claude_agent({
  "action": "spawn",
  "agent_name": "doc-writer",
  "agent_description": "Writes module-level docs",
  "agent_prompt": "Generate rustdoc for src/parser.rs"
})
// → response.agent_id = "..."

// Poll
claude_agent({ "action": "status", "agent_name": "doc-writer" })
// → response.status = "running" | "done" | "error"
```

**Workflow 4: Code review of a PR**
```json
claude_review({
  "target": "https://github.com/owner/repo/pull/123",
  "output_format": "json"
})
```

**Workflow 5: Structured output for downstream parsing**
```json
claude_execute({
  "prompt": "Classify this support ticket",
  "output_format": "json",
  "structured_output_schema_json": "{\"type\":\"object\",\"properties\":{\"category\":{\"type\":\"string\",\"enum\":[\"bug\",\"feature\",\"question\"]},\"priority\":{\"type\":\"string\",\"enum\":[\"low\",\"medium\",\"high\"]}},\"required\":[\"category\",\"priority\"]}"
})
```

---

## §11. Anti-patterns

❌ **Calling `claude_execute` 50 times for 50 small tasks** — use `claude_session` to maintain context, or use `claude_agent` to spawn a background agent for long-running work
❌ **Forgetting `permission_mode: "acceptEdits"`** — Claude Code will ask before every edit, blocking on your agent
❌ **Setting `bare_mode: true` for production work** — you lose hooks, LSP, plugins, all the safety rails
❌ **Using `output_format: "text"` when you need to parse the result** — use `"json"` so the server pre-parses for you
❌ **Spamming `claude_agent.spawn` in a loop** — these are real Claude Code instances, expensive; use `claude_session` to keep one
❌ **Putting a JSON Schema as a nested object** — it's a STRING (pass-through). The schema gets passed to `--json-schema`, validated by Claude Code itself
❌ **Setting `disallowed_tools: ["Read", "Edit"]`** — these are core; you're effectively turning the agent into a chat-only instance
❌ **Forgetting `mcp_configs` when you need a different MCP setup** — Claude Code uses its default MCP configs; override per-call if needed

---

## §12. Handoff

- **MCP design principles** (why this surface looks like this) → `mcp-server-design`
- **Implementation details** (rmcp + schemars attribute mapping, error code mapping) → `mcp-server-implement`
- **JSON Schema authoring details** (constraints, descriptions, `additionalProperties`) → `mcp-tool-surface`
- **Wrapping a different CLI as MCP** (the pattern this plugin is an instance of) → `mcp-server-design` §4

---

## §13. Key sources

- [1] Kimi brainstorm: "Optimal MCP Schema for a Claude Code CLI Wrapper" (the design doc) — internal
- [2] `claude-cli-wrapper` plugin source — `plugins/claude-cli-wrapper/` in this marketplace
- [3] Claude Code CLI documentation — https://docs.claude.com/en/docs/claude-code
- [4] MCP spec for tool surface patterns — https://modelcontextprotocol.io/specification/2025-11-25
- [5] Marketplace entry — `marketplace.json` in this repo
