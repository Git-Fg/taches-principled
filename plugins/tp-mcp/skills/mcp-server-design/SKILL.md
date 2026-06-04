---
name: mcp-server-design
description: Design an MCP (Model Context Protocol) server that LLM agents can call cleanly. Tool decomposition (1 vs N), equilibrated recursivity (flat schema, deep data via pass-through), output contract (CallToolResult text+JSON), JSON-RPC error code discipline, context budget (≤12 KB total schema), tool annotations, naming, capability negotiation, security best practices. Use when the user says "design an MCP server", "should this be one tool or many", "how to structure tool schemas", "MCP server best practices", "JSON-RPC errors", "tool naming".
when_to_use: |
  - "Should I split this into multiple tools or keep it as one?"
  - "Design an MCP server for X"
  - "What's the right tool decomposition?"
  - "How do I structure tool names and descriptions?"
  - "What's the context budget for tool definitions?"
  - "How should I handle errors in tool responses?"
---

# mcp-server-design

The design hub for an MCP server. Covers the principles, decision frameworks,
and validation criteria that every well-built MCP server should satisfy. For
implementation in Rust, see `mcp-server-implement`. For the JSON Schema
authoring details, see `mcp-tool-surface`.

---

## §1. When this skill fires

**Use this skill when the user says any of:**
- "Design an MCP server"
- "Should this be 1 tool or N tools?"
- "How do I structure tool schemas?"
- "What's the context budget for tool definitions?"
- "MCP server best practices"
- "JSON-RPC error codes for MCP"
- "Tool naming conventions for MCP"
- "What should the tool surface look like?"
- "How do I expose a CLI as MCP tools?"

**DO NOT use this skill for:**
- "Implement an MCP server in Rust" / "rmcp code patterns" → `mcp-server-implement`
- "Write a good JSON Schema" / "tool name conventions" / "schema constraints" → `mcp-tool-surface`
- "I'm building an MCP client" / "tool selection strategy" → (no skill yet, defer)
- "Review my MCP server design" / "is my server Claude-optimal?" → (future `mcp-server-quality` skill)
- "Wrap a CLI as an MCP server" → this skill + `mcp-server-implement` together; the `claude-cli` skill is a worked example

---

## §2. The core design thesis: equilibrated recursivity

**The schema must be flat; the data must be deep.**

- **Tool parameter surface** (what the LLM sees and fills): ≤ 2 nesting levels. Agent-callable schemas must be flat enough for an LLM to construct arguments on the first try.
- **Complex structures** (JSON Schemas, prompts, configuration objects, deep data): passed as serialized strings (`"…JSON-encoded…"`) or file references. The wrapper server validates syntax (JSON parseable, file readable) but not semantics — it passes the blob through.

This is the sweet spot: the agent reasons about simple keys, but the wrapped implementation processes arbitrarily deep content.

**Why it works:** flat schemas fit comfortably in the LLM's prompt, allow accurate tool-selection and argument-fill, and stay under the context budget. The pass-through lets you wrap anything (CLIs, APIs, databases) without trying to make the schema understand the wrapped system.

---

## §3. Tool decomposition: 1 tool vs N tools

**Default rule: decompose by operational domain.** Expose ~6 tools, not 1 mega-tool. If you have 50+ CLI flags, splitting them into 6 thematic tools beats exposing all 50 in one schema.

| Concern | Tool count | Why |
|---|---|---|
| Single, atomic operation | 1 tool | No decomposition needed; e.g., `read_file(path)` |
| Multiple domains in one system | 4-8 tools | Each domain is its own tool: `claude_execute`, `claude_session`, `claude_context`, `claude_review`, `claude_agent`, `claude_config` |
| Action set on one entity | 1 tool with `action` enum | Use a discriminator instead of one tool per action: `session(action="resume" | "continue" | "fork" | "list", ...)` |
| Cross-cutting concern | Consider a single tool | If 3+ tools always need the same 3 params, maybe one tool is right |
| Test framework has 200+ operations | Decompose by lifecycle: `test.run`, `test.coverage`, `test.list`, `test.filter` | Don't dump all 200 into one tool |

**Decomposition rules (when in doubt):**
1. **Context budget dominates.** A 50-param tool eats 5+ KB of tool-definition tokens; 6 tools at 8-10 params each stays under 2 KB each.
2. **Tool-selection accuracy dominates.** LLMs are better at picking between 6 distinct tools than between 1 mega-tool and 4 vague alternatives.
3. **Atomic operations stay together.** Don't split `read + write` if they're always called as a pair; do split `read` from `delete`.
4. **`action` enum beats 5 sibling tools** when the action set is bounded and the args overlap (e.g., `session(action=...)` not `session_resume/session_continue/session_fork`).
5. **The user should be able to describe each tool in one sentence.** If a tool's description needs two sentences, the tool is probably doing two things.

**Signals to MERGE tools:**
- The agent always calls them in sequence with no independent utility
- Args overlap ≥80% (different action, same params)
- The decomposition is by "version" or "vintage" (anti-pattern: `v1_search`, `v2_search`)

**Signals to SPLIT tools:**
- Two operations are sometimes called independently
- A user would describe them with different verbs
- Combining them costs >1 KB of context for rarely-used args
- One is read-only and the other is destructive (separation helps safety)

---

## §4. Tool decomposition case study: claude-cli-wrapper

The `claude-cli-wrapper` plugin in this marketplace is a real example. It exposes 6 tools, not 1:

| Tool | Operational domain | Approx params |
|---|---|---|
| `claude_execute` | Run a prompt, get structured output | 18 |
| `claude_session` | Lifecycle (resume/continue/fork/list/info/close) | 4 |
| `claude_context` | Workspace (add dirs, worktrees, doctor) | 5 |
| `claude_review` | Code review (ultrareview) | 3 |
| `claude_agent` | Background agent management | 5 |
| `claude_config` | Runtime tuning (model/effort/permissions/settings) | 6 |

Total: ~41 params across 6 tools. Each schema < 2 KB serialized. The wrapper amortizes the context cost of the wrapped CLI (which has 50+ flags) into a manageable per-tool surface.

**Lessons from this decomposition:**
- The `action` enum is used inside `claude_session` and `claude_config` (6 lifecycle actions in one tool)
- `claude_execute` is the high-traffic tool, so it gets the most params; the others are kept lean
- All 6 tools share a `session_id` UUID format (strict regex enforced) for cross-tool continuity

---

## §5. Output contract: CallToolResult text+JSON

MCP tools return `CallToolResult` with `content` items. The dominant pattern is text-with-JSON-payload:

```json
{
  "type": "text",
  "text": "{\"exit_code\": 0, \"stdout\": \"...\", \"stderr\": \"\", \"session_id\": \"uuid\", \"output_parsed\": { ... }}"
}
```

**Fields the text payload typically contains:**
- `exit_code` (for CLI wrappers) or `success` (boolean for pure function tools)
- `stdout` / `output` — raw output (or parsed JSON if `output_format=json`)
- `stderr` / `error` — error stream
- `session_id` — for session continuity
- `output_parsed` — convenience field: pre-parsed JSON when valid
- `error` — error description if non-success

**Why text-with-JSON, not the resource type?** Because tool output is ephemeral execution data, not a persistent file or URI. Text is the most portable across MCP clients.

**Alternative output types (use sparingly):**
- `image` — for vision tools
- `audio` — for speech tools
- `resource` — link to a persistent resource (rare for tool output)

**The hard rules:**
- Tool output MUST be one of the defined `content` types
- Don't return raw non-JSON strings the LLM has to parse
- Don't put secrets in tool output unredacted
- Truncate large outputs (sensible default: 50 KB max, with `[truncated, full output at <URI>]` notice)

---

## §6. JSON-RPC error code discipline

MCP uses JSON-RPC 2.0 over the wire. Use the standard error codes plus your own for domain:

| Code | Name | When |
|---|---|---|
| **-32700** | Parse error | Malformed JSON, invalid UTF-8, missing required fields |
| **-32600** | Invalid Request | Not a valid JSON-RPC request (wrong shape) |
| **-32601** | Method not found | Unknown method (e.g., tool name typo) |
| **-32602** | Invalid params | Tool args failed schema validation (this is the **most common** in practice) |
| **-32603** | Internal error | Wrapper/SDK crash, not a domain error |
| **-32000 to -32099** | Server error | Custom codes — define per server |

**MCP convention (community-observed):**
- `-32602` for any schema violation, including enum mismatch, missing required, type mismatch
- `-32603` ONLY for wrapper/SDK crashes (panic, unhandled exception) — never for "tool returned an error"
- Custom `-32xxx` codes (between -32099 and -32000) for domain-specific failures: e.g., `-32001` for "CLI exited with non-zero", `-32002` for "rate limited", `-32003` for "dependency download failed"
- Always include a `data` field with structured details (string message + optional context object)

**Example error response:**
```json
{
  "jsonrpc": "2.0",
  "id": 42,
  "error": {
    "code": -32001,
    "message": "CLI exited with non-zero status",
    "data": { "exit_code": 2, "stderr": "command not found: foo" }
  }
}
```

---

## §7. Tool annotations

MCP tools can declare behavior hints via annotations. The host (Claude Code, etc.) uses these for safety prompts, UI hints, and tool-selection:

| Annotation | Type | Meaning |
|---|---|---|
| `title` | string | Human-readable tool name (default: name) |
| `readOnlyHint` | boolean | Tool only reads, never modifies state |
| `destructiveHint` | boolean | Tool modifies or deletes state (used by `Auto` mode permissions) |
| `idempotentHint` | boolean | Repeated calls with same args have the same effect |
| `openWorldHint` | boolean | Tool interacts with external systems (network, filesystem, etc.) |

**Annotation discipline:**
- `readOnlyHint: true` for queries, searches, reads
- `destructiveHint: true` for deletes, writes, sends
- `idempotentHint: true` for `set_X(value)` if calling it 3 times = calling it once
- `openWorldHint: true` for anything that hits network, file system, subprocess
- **Honesty matters:** these are TRUST signals. If you mark `readOnlyHint: true` but the tool secretly writes to a cache, the host's safety reasoning is broken.

**The MCP spec notes (2025 spec):** hosts must consider tool descriptions and annotations as untrusted unless from a trusted server. So don't rely on the host to gate based on these — gate in your own auth/permission layer.

---

## §8. The pass-through principle

For any wrapped feature that requires deep nesting (JSON Schemas, complex settings, agents configs, etc.), the MCP tool accepts it as a **serialized string or file path**. The wrapper validates syntax (JSON parseable, file readable) but not semantics.

**Example — `claude_execute.structured_output_schema_json`:**
```json
{
  "structured_output_schema_json": {
    "type": "string",
    "maxLength": 8192,
    "description": "JSON-encoded JSON Schema for structured output validation. The schema itself is validated by Claude Code, not this server."
  }
}
```

The actual schema is a deep object (could be 100+ lines, nested `anyOf`, `oneOf`, etc.). The LLM fills a STRING; the server forwards the string; Claude Code parses and validates. The tool schema stays flat.

**When to pass-through:**
- JSON Schemas for structured output
- Settings/permissions JSON
- Agent role definitions
- Tool definitions themselves (when wrapping a tool framework)
- Any "deep config" the wrapped system needs

**When NOT to pass-through:**
- Things the LLM should reason about (file paths, IDs, choices)
- Things that need server-side validation (auth tokens, rate limits)
- Things where a flat representation exists and is more useful

---

## §9. Context budget: keep total schema under 12 KB

**Rule of thumb:** all tool definitions combined should be < 12 KB serialized, which keeps the tool-definition token cost under 3k tokens (cheap for the LLM to carry per turn).

**Calculation:**
- Each tool definition has: name, description, inputSchema (JSON Schema)
- A well-designed tool: ~300-800 bytes serialized
- 6 tools at 500 bytes each: 3 KB
- 12 tools at 800 bytes each: 9.6 KB
- Beyond 12 tools or so, every additional tool costs more in selection noise than it saves in decomposition

**If you're over budget:**
1. Shorten descriptions (use action verbs, drop examples that fit in `description` of the property)
2. Trim `description` on properties (one sentence each)
3. Move long descriptions to `references/` files (rarely the right move for tool defs)
4. Decompose one fat tool into 2-3 thin tools (decomposing itself can save context because unused tool defs can be selectively omitted by the host)

---

## §10. Capability negotiation

Every MCP server declares what it supports in its `ServerCapabilities` during the `initialize` handshake:

| Capability | What you expose | How to declare |
|---|---|---|
| `tools` | Callable functions | `tools: {}` or `tools: { listChanged: true }` (if you notify on changes) |
| `resources` | URI-addressed read-only data | `resources: {}` or `resources: { subscribe: true, listChanged: true }` |
| `prompts` | Reusable prompt templates | `prompts: {}` or `prompts: { listChanged: true }` |
| `logging` | Server can emit log messages | `logging: {}` |
| `completions` | Server supports argument completion | `completions: {}` |
| `tasks` (experimental) | Server can run long-running tasks | `tasks: {}` (not yet standardized) |

**Server-initiated capabilities (from server to client):**
- `sampling` — server can ask the host to run an LLM completion (enables agentic loops)
- `elicitation` — server can ask the host to request user input (consent flows, structured forms)
- `roots` — server can ask the host about filesystem boundaries

**Negotiation rules:**
- Only declare what you actually implement (don't claim `sampling` if you never call `create_message`)
- `listChanged: true` means you'll send `notifications/tools/list_changed` when the tool set changes
- The host uses your declared capabilities to know which requests to send

---

## §11. Security: the MUST/SHOULD/MAY checklist

**MUST (per spec):**
- Validate all input against your JSON Schema (server-side, regardless of client-side validation)
- Obtain explicit user consent before invoking any tool that takes a destructive action
- Never expose user data to a server without consent
- Validate the `Origin` header on every Streamable HTTP connection (DNS rebinding protection)
- Use `additionalProperties: false` on your tool schemas (don't accept undocumented params)
- Treat tool descriptions and annotations as untrusted input (don't let them inject instructions)

**SHOULD:**
- Add authentication to remote servers (OAuth 2.0 Resource Server, since June 2025 spec)
- Use HTTPS for Streamable HTTP in production
- Rate-limit clients
- Sanitize paths against traversal attacks
- Bound resource consumption (memory, CPU, file handles, subprocess count)
- Log to stderr only (stdout is the protocol stream)
- Log enough to debug, not so much it leaks secrets

**MAY:**
- Cache responses
- Support both stdio and Streamable HTTP transports
- Send progress notifications for long-running operations
- Implement cancellation for in-flight tool calls

**Anti-pattern: hidden state in tool calls.** MCP has no protocol-level session. If your tool needs state, return an explicit handle from a creation tool, then accept that handle as an argument on subsequent tools. Don't rely on implicit per-connection state.

---

## §12. Tool naming conventions

The MCP spec says tool names SHOULD be 1-128 characters, case-sensitive, only:
- Uppercase and lowercase ASCII letters (A-Z, a-z)
- Digits (0-9)
- Underscore (`_`), hyphen (`-`), dot (`.`)

**Best practices:**
- `snake_case` for multi-word names (matches Python/JSON convention): `read_file`, `create_issue`
- `verb_noun` pattern: `search_products`, `move_application`, not just `products` or `application`
- Group by domain with a prefix when you have many tools from one vendor: `github_create_issue`, `github_list_repos` (when you have 5+ tools, the prefix helps selection)
- Avoid generic names that conflict with other servers' tools: `search`, `query`, `run`
- For tools with an `action` enum, the tool name describes the entity, the action is the discriminator: `session(action="resume")`, not `resume_session`

**Test for clarity:** a user who sees the tool name in a list should be able to guess what it does. `get_weather(city)` ✓ vs `gw(city)` ✗.

---

## §13. Validation: the Claude-Optimal checklist

A server passes when:

1. **Tool discovery works** — all tools load in Claude Code (or other hosts) without `Invalid input: expected "object"` errors.
2. **Single-shot accuracy** ≥ 90% — in `--print --output-format json` mode, the LLM generates valid tool arguments on the first attempt in ≥ 90% of test invocations.
3. **Context efficiency** — total serialized schema < 12 KB, per-tool < 2 KB.
4. **Pass-through integrity** — complex blobs (JSON Schemas, settings) round-trip through your tool without mutation.
5. **Session continuity** — `session_id` from one tool works in another without manual transformation.
6. **Headless reliability** — the wrapper never hangs waiting for TTY. `mode: "interactive"` is rejected or sandboxed when stdin is not a TTY.
7. **Error distinction** — JSON-RPC `-32602` for schema violations, custom codes for domain failures, `-32603` only for wrapper crashes.
8. **Schema hygiene** — `additionalProperties: false` on every object schema, `description` on every property, `required` for non-optional args.

**Worked example: `claude-cli-wrapper` v0.2.0 in this marketplace** meets all 8 criteria (verifiable in its marketplace description).

---

## §14. Consuming in Claude Code

The schema design work above is producer-side. This section is the
consumer-side view: once your server ships, **how does Claude Code
actually discover, present, and use your tools?** Most of the §1–§13
decisions show up here as observed behavior.

### Installation paths

**1. Plugin-shipped `.mcp.json` (recommended for skills/plugins):**
Place a `.mcp.json` in the plugin root and Claude Code auto-loads it
when the plugin is enabled:
```json
{
  "my-server": {
    "command": "./bin/my-mcp-server",
    "args": [],
    "env": {}
  }
}
```
No `"type": "stdio"` needed — stdio is the default. Adding it
explicitly is harmless but redundant.

**2. User-level `~/.claude.json` (for personal servers):**
Use `claude mcp add --transport stdio my-server -- ./bin/my-mcp-server`.
Equivalent JSON lands under `mcpServers` in the user config.

**3. Project-scoped `.mcp.json` (for repos the team shares):**
Place in the repo root and commit it. Each teammate gets the same
servers when they `claude` into the project. The `--strict-mcp-config`
flag freezes the project config so a teammate's personal `~/.claude.json`
additions don't leak in.

**4. `claude mcp add-from-claude-desktop`:** one-shot import from a
Desktop config. Useful for moving from Claude Desktop into Claude Code.

### The discovery flow (what Claude Code actually does)

```
claude -p "..." (or interactive session start)
  ↓
load user mcpServers + project .mcp.json + plugin .mcp.json
  ↓
for each server: spawn child process, capture stdio
  ↓
JSON-RPC initialize handshake
  → server returns: protocolVersion, serverInfo, capabilities, instructions
  ↓
client sends notifications/initialized
  ↓
client sends tools/list
  → server returns: list of { name, description, inputSchema, annotations? }
  ↓
client prepends server instructions to the system prompt (if any)
client prepends each tool's description + JSON schema to the model context
  ↓
[per turn]
  → model emits a tool_use block (tool name + arguments)
  → client sends tools/call
  → server returns: { content: [...], isError: bool }
  → model sees the result, continues
  ↓
shutdown
  → stdio: client closes the child process's stdin
```

**Where your design choices land in this flow:**

| Producer-side decision | Consumed by Claude Code as |
|---|---|
| `ServerInfo::instructions` | Prepended to system prompt (cached per session) |
| `ServerInfo::capabilities.tools` | Tells client it can request `tools/list` and `tools/call` |
| `#[tool(description = "...")]` | Per-tool description in model context (selects and triggers tool use) |
| `inputSchema` (from `JsonSchema` derive) | The argument schema the model must satisfy when emitting `tool_use` |
| `#[tool(annotations(...))]` | Hints the host's safety layer reads to decide confirmation prompts, parallelism, retry |
| Server name (`my-server` in `.mcp.json`) | Becomes the `serverName` prefix in tool identifiers; affects how the model disambiguates `my-server__my_tool` vs another `my_tool` |

### Verifying discovery and behavior

```bash
# See what Claude Code thinks is installed
claude mcp list

# Get verbose connection + handshake output
claude mcp get my-server

# Test a tool call without the model in the loop
npx @modelcontextprotocol/inspector ./bin/my-mcp-server
# → Inspector speaks JSON-RPC over stdio directly
# → Lets you call tools/list, tools/call with arbitrary args
# → Shows every request/response frame on the wire
```

**The Inspector is the ground truth** for what your schema actually looks
like on the wire. If the model is calling the tool with wrong args, the
first debugging step is: does the Inspector show the schema you thought
you wrote?

### What the model sees (and doesn't)

The model sees:
- Each tool's `name` and `description` verbatim
- The full `inputSchema` as compact JSON (this is the §9 12 KB context cost)
- The server's `instructions` once per session
- Annotations indirectly (the host's safety layer reads them; the model itself doesn't see them as text)

The model does NOT see:
- The Rust type names or struct definitions
- The `#[serde(rename = "...")]` aliases — it sees the renamed output
- The `#[schemars(description = "...")]` for fields NOT in the schema (e.g. `Option<T>` fields with `skip_serializing_if` set so they're absent)
- The `inputSchema`'s `examples` unless the host surfaces them
- Tool names from other servers unless those servers are also loaded

### Common consumer-side debugging

| Symptom | Likely cause | Fix |
|---|---|---|
| Tool not showing up in `claude` session | Server crashed at handshake; check stderr | `RUST_LOG=debug claude` and re-run |
| Model never picks the tool | Description is too generic or collides with another tool | Rename to `verb_noun`; sharpen the description's trigger conditions |
| Model picks the tool but fills args wrong | Schema is too loose, or `description` is vague | Add constraints (`enum`, `range`, `regex`); rewrite descriptions with "Use when…" framing |
| Model sends a hallucinated field | Missing `additionalProperties: false` / `deny_unknown_fields` | Add both |
| Model calls a "destructive" tool without confirmation | `destructiveHint` is missing or `false` | Add `annotations(destructive_hint = true)` |
| Server returns content but model ignores it | Output format is `String` where a typed envelope would be better | Return a JSON envelope; see `claude-cli-wrapper` tools for the pattern |
| Random disconnects mid-session | `println!` somewhere in your tool impl | Replace with `tracing` to stderr; see `mcp-server-implement` §10 |

> **Iterative loop:** change the schema → rebuild → restart Claude Code
> (or use a plugin dev mode that hot-reloads) → repeat the same prompt →
> watch whether the model's tool call improved. The first version is
> never the right version.

---

## §15. Handoff to other skills

- **Schema design (constraints, naming, descriptions, `additionalProperties` discipline)** → `mcp-tool-surface`
- **Schemars attribute cheat-sheet** (per-attribute → JSON Schema mapping) → `mcp-tool-surface` §14
- **Implementation in Rust (rmcp + schemars, transports, server lifecycle)** → `mcp-server-implement`
- **Worked example: wrapping Claude Code CLI as 6 tools** → `claude-cli` skill
- **Quality evaluation** (planned `mcp-server-quality`, uses `tp-sadd` judge pattern) → not yet implemented
- **MCP client patterns** (when the agent IS the MCP consumer) → not yet implemented

---

## §16. Anti-patterns

❌ **Mega-tool with 50+ params** — splits poorly, dominates context, LLMs fail to fill accurately
❌ **`additionalProperties: true` or omitted** — silently accepts any input, schema becomes decorative
❌ **Deeply nested inputSchema** — costs tokens, hurts selection accuracy, often a sign you should split
❌ **`println!()` to stdout in stdio transport** — corrupts the protocol stream, client disconnects
❌ **Free-form string for structured data** — use pass-through with a STRING, then JSON.parse on the server side
❌ **Implicit session state** — the spec explicitly says sessions are stateless; use explicit handles
❌ **Logging to stdout** — only stderr
❌ **`destructiveHint: false` on a tool that secretly writes** — destroys trust in annotations
❌ **Generic tool names** (`search`, `query`) — collide with other servers, ambiguous selection
❌ **One tool per "version"** (`v1_search`, `v2_search`) — use `action` enum or evolve the schema
❌ **Returning a stream of partial results when the host expects a final answer** — use notifications/progress for streaming, not the result
❌ **Skipping the schema's `required` field** — without it, the LLM doesn't know what's mandatory
❌ **Treating tool annotations as user-facing promises** — they're hints to the host's safety reasoning, not guarantees
❌ **Skipping `claude mcp list` after install** — the "is it connected?" check takes 2 seconds; you save 20 minutes of "why isn't the tool appearing" debugging
❌ **Returning a 200-character text blob from a tool that should return structured data** — the model has to do extra work to extract fields. Return a JSON envelope; see `claude-cli-wrapper` for the pattern

---

## §17. Key sources

- [1] Model Context Protocol specification (2025-11-25) — https://modelcontextprotocol.io/specification/2025-11-25
- [2] MCP architecture overview — https://modelcontextprotocol.io/docs/learn/architecture
- [3] JSON Schema usage in MCP — https://modelcontextprotocol.io/specification/2025-11-25/basic
- [4] MCP Tools spec — https://modelcontextprotocol.io/specification/draft/server/tools
- [5] MCP Transports spec — https://modelcontextprotocol.io/specification/2025-03-26/basic/transports
- [6] Auth0: MCP Spec Updates June 2025 (OAuth Resource Servers) — https://auth0.com/blog/mcp-specs-update-all-about-auth/
- [7] Data Science Dojo: Definitive Guide to MCP in 2025 — https://datasciencedojo.com/blog/guide-to-model-context-protocol/
- [8] MCP Best Practices: Architecture & Implementation — https://modelcontextprotocol.info/docs/best-practices/
- [9] apxml Tool Definition Schema — https://apxml.com/courses/getting-started-model-context-protocol/chapter-3-implementing-tools-and-logic/tool-definition-schema
- [10] LeanIX: MCP Tools — https://engineering.leanix.net/blog/mcp-tools/
- [11] Merge: MCP tool schema — https://www.merge.dev/blog/mcp-tool-schema
- [12] CodiLime: MCP explained — https://codilime.com/blog/model-context-protocol-explained/
- [13] WebFuse MCP Cheat Sheet (2026) — https://www.webfuse.com/mcp-cheat-sheet
- [14] Kimi brainstorm: "Optimal MCP Schema for a Claude Code CLI Wrapper" (the doc the user shared) — internal
- [15] Worked example in this marketplace: `plugins/claude-cli-wrapper` (the 6-tool decomposition)
