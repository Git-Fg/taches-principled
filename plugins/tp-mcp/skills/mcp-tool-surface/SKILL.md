---
name: mcp-tool-surface
description: Author LLM-friendly MCP tool schemas — schemas-as-instruction-manuals framing, MCP defaults (additionalProperties: false, required, $schema), constraint discipline (enum, pattern, range), oneOf-vs-discriminator-enum, description writing, property naming, nesting rules, output schemas, and the pitfalls catalog. Use when the user says "write a tool schema", "MCP schema design", "JSON Schema for MCP", "MCP tool naming", "required vs optional in MCP", "tool description writing".
when_to_use: |
  - "Write a tool schema"
  - "What should this property's description say?"
  - "Should I use enum or oneOf?"
  - "How do I make this schema LLM-friendly?"
  - "What's the right draft of JSON Schema?"
  - "Required vs optional in MCP tool args"
  - "Tool naming convention"
  - "How do I keep my schema under the context budget?"
  - "This LLM keeps getting the args wrong — how do I fix the schema?"
---

# mcp-tool-surface

The schema-authoring layer for MCP tools: how to think about a JSON Schema
as the LLM's instruction manual, the defaults you should always set, the
constraint discipline, the oneOf-vs-enum decision, description writing,
naming, nesting, and the pitfalls to avoid. For the higher-level design of
the whole server's tool surface, see `mcp-server-design`. For the Rust
implementation with schemars, see `mcp-server-implement`.

## §1. When this skill fires

**Use this skill when the user says any of:**
- "Write a tool schema"
- "What should this property's description say?"
- "Should I use enum or oneOf?"
- "How do I make this schema LLM-friendly?"
- "What's the right draft of JSON Schema?"
- "Required vs optional in MCP tool args"
- "Tool naming convention"
- "How do I keep my schema under the context budget?"
- "This LLM keeps getting the args wrong — how do I fix the schema?"

## CONTRAST

- NOT for: designing the whole MCP server's tool decomposition — use mcp-server-design
- NOT for: implementing the server in code (rmcp, schemars, transport) — use mcp-server-implement
- NOT for: non-MCP tool schemas (OpenAI function calls, raw JSON Schema) — use the target system's docs
- This skill is the schema-authoring layer; design and implementation are separate skills

**DO NOT use this skill for:**
- "Design the whole MCP server" / "1 tool vs N" / "output contract" → `mcp-server-design`
- "Implement the server in Rust" / "rmcp + schemars attribute mapping" → `mcp-server-implement`
- "JSON Schema for non-MCP purposes" (OpenAPI, function calling, etc.) → most patterns transfer but MCP-specific guidance lives here

## §2. Reference index

The mechanism content lives in references/. Read the right one before committing to a schema design. The hub itself is a router — it points you at the right reference, the references carry the mechanism.

You MUST read `references/schema-foundation.md` BEFORE writing any tool schema. It teaches the "schemas are LLM instruction manuals" principle, the three failure modes it defends against (tool-selection, argument-fill, schema-violation), the MCP defaults that should always be set (`additionalProperties: false`, `required`, `$schema`), the constraint discipline (enum, pattern, range, format, length), the `oneOf`-vs-discriminator-enum decision (95% of the time discriminator enum wins), the required-vs-optional principle, and the description-writing patterns that earn their context cost. Do not proceed without reading it.

You MUST read `references/schema-styling.md` BEFORE finalizing property names or tool names. It teaches the snake_case-vs-camelCase decision, the property naming rules (full words, singular/plural, no vendor prefixes on properties), the 2-level nesting rule (deeper goes through pass-through), defaults that help (booleans default false, arrays default []), the verb_noun tool naming pattern, and the 5+ tool prefix convention. Do not proceed without reading it.

You MUST read `references/outputs-and-pitfalls.md` BEFORE declaring a schema ready to ship. It teaches the `outputSchema` shape for typed clients, and the 14-row pitfalls catalog (additionalProperties:true, no required, vague descriptions, deeply nested objects, free-form strings, oneOf abuse, mixed naming conventions, missing enums, oversized maxLength, boolean form, missing $schema, format-alone, inconsistent id/Id). Do not proceed without reading it.

The schemars attribute cheat-sheet (per-attribute → JSON Schema mapping) lives in `references/schemars-cheatsheet.md` — read it BEFORE writing Rust types for tool input/output. Do not proceed without reading it.

## §3. Handoff to other skills

- **When to split one tool into N** → `mcp-server-design/references/design-decisions.md`
- **Output contract (CallToolResult text+JSON)** → `mcp-server-design/references/design-decisions.md`
- **Error code discipline** → `mcp-server-design/references/design-decisions.md`
- **Implementation: rmcp + schemars attribute mapping** → `mcp-server-implement/references/rmcp-api.md`
- **Tool annotations (readOnlyHint, destructiveHint, idempotentHint)** → `mcp-server-design/references/design-decisions.md`
- **How Claude Code actually discovers and uses the tools** → `mcp-server-design/references/claude-code-consumption.md`

## §4. Anti-patterns

❌ **Schema without `additionalProperties: false`** — silent acceptance of hallucinated fields
❌ **Free-form `string` for structured data** — use type + constraints, or pass-through as JSON string
❌ **Missing `required` field** — LLM doesn't know what's mandatory
❌ **`oneOf` for "kinds of X" instead of discriminator enum** — costs tokens, hurts accuracy
❌ **Deeply nested objects** (>2 levels) — flatten or pass-through
❌ **Empty or vague `description`s** — every description should be LLM-actionable
❌ **No `enum` for bounded choices** — LLM invents values
❌ **Tool names with `v1_` `v2_` prefix** — evolve the schema, don't version the name
❌ **Booleans without verb form** — `is_X` or `enable_X` reads better than bare `X`
❌ **Missing `pattern` for ID fields** — use strict regex to prevent garbage
❌ **`$schema` field missing** — be explicit about the draft you're using
❌ **Inconsistent naming conventions** — pick `snake_case` or `camelCase` and use it everywhere
❌ **Output schemas with `additionalProperties: true`** — that's a hint, not a schema
❌ **`#[schemars(extend("examples" = ...))]` on a free-form string** — LLM echoes the example back verbatim, hurting variety. Examples are best on enums and short constrained fields
❌ **`#[serde(untagged)]` enums in tool input** — schemars emits `oneOf` of all variant shapes; LLMs pick the wrong branch ~40% of the time. Use a discriminator enum with a separate payload field

## §5. Key sources

- [1] JSON Schema draft 2020-12 specification — https://json-schema.org/draft/2020-12/schema
- [2] JSON Schema usage in MCP (official spec) — https://modelcontextprotocol.io/specification/2025-11-25/basic
- [3] MCP Tools spec — https://modelcontextprotocol.io/specification/draft/server/tools
- [4] apxml: Tool Definition Schema — https://apxml.com/courses/getting-started-model-context-protocol/chapter-3-implementing-tools-and-logic/tool-definition-schema
- [5] LeanIX: MCP Tools — https://engineering.leanix.net/blog/mcp-tools/
- [6] Merge: MCP tool schema — https://www.merge.dev/blog/mcp-tool-schema
- [7] Model Context Protocol: Architecture overview — https://modelcontextprotocol.io/docs/learn/architecture
- [8] Tool Design Principles in MCP (the "description is the instruction manual" framing) — derived from community patterns observed in claude-cli-wrapper design doc and MCP server examples
- [9] schemars attribute reference — https://docs.rs/schemars/
- [10] Worked example: the `claude-cli` skill in this marketplace's `claude-cli-wrapper` plugin (6-tool decomposition)
