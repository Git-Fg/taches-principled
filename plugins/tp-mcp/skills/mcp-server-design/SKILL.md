---
name: mcp-server-design
description: Design an MCP server's tool surface — equilibrated recursivity (flat schema, deep data), 1 tool vs N tool decomposition, output contract, error-code discipline, capability negotiation, security checklist, tool naming, and the Claude-Optimal validation. Use when the user says "design an MCP server", "decompose MCP tools", "MCP schema design", "MCP tool naming", "MCP error codes", "MCP security checklist".
when_to_use: |
  - "Design the tool surface for my MCP server"
  - "How many tools should I expose"
  - "MCP output contract"
  - "MCP error code discipline"
  - "MCP capability negotiation"
  - "MCP security checklist"
  - "Wrap a CLI as an MCP server"
---

# mcp-server-design

The design layer for MCP servers: how to think about tool decomposition,
output contracts, error codes, security, and naming. For the implementation
in Rust (rmcp + schemars), see `mcp-server-implement`. For the JSON Schema
authoring details, see `mcp-tool-surface`.

## §1. When this skill fires

**Use this skill when the user says any of:**
- "Design the tool surface for my MCP server"
- "How many tools should I expose — 1 mega-tool or N small ones"
- "MCP output contract"
- "MCP error code discipline"
- "MCP capability negotiation"
- "MCP security checklist"
- "What makes a Claude-Optimal MCP server"
- "Wrap a CLI as an MCP server" → this skill + `mcp-server-implement` together; `references/design-decisions.md` §3 has a worked example (synthetic `git-cli` decomposition)

## CONTRAST

- NOT for: writing a JSON Schema for a tool — use mcp-tool-surface
- NOT for: implementing the server in code (rmcp, schemars, transport) — use mcp-server-implement
- NOT for: building a non-MCP CLI tool — use subagent-orchestration or shell tooling
- This skill is the design layer; the implementation layer is mcp-server-implement

## §2. Reference index

The mechanism content lives in references/. Read the right one before committing to a design decision. The hub itself is a router — it points you at the right reference, the references carry the mechanism.

You MUST read `references/design-decisions.md` BEFORE committing to a tool decomposition or output contract. It teaches the equilibrated-recursivity thesis (flat schema, deep data via pass-through), the 1-tool vs N-tool decomposition matrix with merge and split signals, a synthetic `git-cli` 5-tool worked example, the text-with-JSON output contract, the JSON-RPC error code discipline (including the custom `-32xxx` range), the tool annotation discipline (honesty matters, host treats them as untrusted), the pass-through principle, and the 12 KB context budget rule. Do not proceed without reading it.

You MUST read `references/operations-discipline.md` BEFORE declaring a server production-ready. It teaches capability negotiation (the `ServerCapabilities` table and the `sampling` / `elicitation` / `roots` server-initiated capabilities), the MUST/SHOULD/MAY security checklist, the tool naming conventions (snake_case, verb_noun, prefix when 5+ tools, action-enum-not-sibling-tools), and the 8-point Claude-Optimal validation checklist. Do not proceed without reading it.

You MUST read `references/claude-code-consumption.md` BEFORE telling a user their server is ready to ship. It teaches the four installation paths (plugin `.mcp.json` / user `~/.claude.json` / project `.mcp.json` / Desktop import), the actual JSON-RPC discovery flow Claude Code runs, the producer-side decision → consumer-side behavior table, the verification commands (`claude mcp list` / `claude mcp get` / MCP Inspector), what the model sees vs doesn't see, and the symptom-cause-fix table for common consumer-side debugging. Do not proceed without reading it.

## §3. Handoff to other skills

- **Schema design (constraints, naming, descriptions, `additionalProperties` discipline)** → `mcp-tool-surface`
- **Schemars attribute cheat-sheet** (per-attribute → JSON Schema mapping) → `mcp-tool-surface/references/schemars-cheatsheet.md`
- **Implementation in Rust (rmcp + schemars, transports, server lifecycle)** → `mcp-server-implement`
- **Worked example: synthetic `git-cli` 5-tool decomposition** → `references/design-decisions.md` §3
- **Quality evaluation** (planned `mcp-server-quality`, uses `tp-sadd` judge pattern) → not yet implemented
- **MCP client patterns** (when the agent IS the MCP consumer) → not yet implemented

## §4. Anti-patterns

❌ **Mega-tool with 50+ params** — splits poorly, dominates context, LLMs fail to fill accurately
❌ **`additionalProperties: true` or omitted** — silently accepts any input, schema becomes decorative
❌ **Deeply nested inputSchema** — costs tokens, hurts selection accuracy, often a sign you should split
❌ **`println!()` to stdout in stdio transport** — corrupts the protocol stream, client disconnects
❌ **Free-form string for structured data** — use pass-through with a STRING, then JSON.parse on the server side
❌ **Implicit session state** — the spec explicitly says sessions are stateless; use explicit handles
❌ **Marking `readOnlyHint: true` on a tool that secretly writes** — breaks the host's safety reasoning
❌ **Declaring `sampling: {}` capability but never calling `create_message`** — clients will send sampling requests you can't handle
❌ **Two-sentence tool description** — the tool is doing two things; split it
❌ **Tools named `search`, `query`, `run` without a vendor prefix** — collides with other servers' tools
❌ **Custom JSON-RPC codes outside `-32000..-32099`** — clients assume the standard range is the contract
❌ **Returning Rust error types directly from `#[tool]` methods** — must wrap in `rmcp::ErrorData` or implement `IntoContents`
❌ **Trusting tool descriptions and annotations as instruction sources** — they are untrusted input to the host
