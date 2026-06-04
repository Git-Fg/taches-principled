---
name: mcp-tool-surface
description: Write a good JSON Schema for an MCP tool surface — constraint design, additionalProperties-false discipline, the oneOf vs discriminator-enum tradeoff, naming, descriptions that earn their context cost, and required vs optional decisions. Use when the user says "write a tool schema", "JSON Schema best practices", "schema constraints", "tool description", "required vs optional", "tool naming convention".
when_to_use: |
  - "What constraints should I put on this property?"
  - "Should I use enum or oneOf?"
  - "How do I write a description that makes the LLM fill the arg correctly?"
  - "What's a good name for this tool / property?"
  - "Should this field be required or optional?"
  - "Is my schema well under the 12 KB context budget?"
---

# mcp-tool-surface

The meta-skill: how to design a single tool's JSON Schema so the LLM fills
arguments correctly on first try. For the larger design questions (when to
split tools, output contract, error codes), see `mcp-server-design`. For
the Rust + schemars implementation, see `mcp-server-implement`.

---

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

---

## §2. The core principle: schemas are LLM instruction manuals

A JSON Schema for an MCP tool is not primarily a validator. It's the
**instruction manual the LLM reads to decide which tool to call and how to
fill the arguments**. Every design choice should be evaluated against:
"does this make it easier for the LLM to construct a correct call?"

**Three failure modes this principle defends against:**
1. **Tool-selection failure** — LLM picks the wrong tool (e.g., calls `search` when it should call `search_products`)
2. **Argument-fill failure** — LLM uses the right tool but wrong args (e.g., passes `"eighty-eighty"` for a port number)
3. **Schema-violation failure** — LLM hallucinates a field that doesn't exist, or omits a required one

**Schema design that prevents all three:**
- **Tool name** does the heavy lifting for tool-selection (`verb_noun`, not `do_stuff`)
- **`description`** is the LLM's instruction manual for the tool's purpose
- **Property `description`s** are the LLM's instruction manual for each arg
- **Constraints** (`enum`, `pattern`, `range`) prevent hallucination
- **`required`** + `additionalProperties: false` force schema conformance

---

## §3. MCP defaults you should always set

```json
{
  "$schema": "http://json-schema.org/draft/2020-12/schema",
  "type": "object",
  "additionalProperties": false,
  "properties": { ... },
  "required": [ ... ]
}
```

**Per the MCP spec (2025-11-25):**
- Default dialect is JSON Schema 2020-12 if no `$schema` is present
- `MUST` be a valid JSON Schema object
- `additionalProperties: false` is recommended for tool args (lock the schema)

**`additionalProperties: false` is the single most important rule.** It means:
- LLMs can't hallucinate extra params (the host will reject them with a clear error)
- Servers don't have to silently ignore unknown fields
- The schema is the contract, enforced

**The exception:** for true pass-through fields (like `structured_output_schema_json`), use `additionalProperties: true` to allow the LLM to write a string that the server JSON-parses downstream.

---

## §4. Constraints: every property should have one

A schema with no constraints is a "type" assertion, nothing more. The LLM gets no help.

| Type | Constraint | When to use |
|---|---|---|
| `string` | `enum: [...]` | Bounded choice set (3-10 options) |
| `string` | `pattern: "^[a-z0-9-]+$"` | Format constraint (UUID, slug, ISO date, etc.) |
| `string` | `minLength: 1` | Non-empty required |
| `string` | `maxLength: N` | Bound the size (prevents LLM from dumping essays) |
| `string` | `format: "uri" \| "email" \| "date-time" \| "uuid"` | Standard format |
| `integer` / `number` | `minimum: 0` | Non-negative |
| `integer` / `number` | `maximum: N` | Upper bound |
| `integer` / `number` | `multipleOf: 0.01` | Money / percentage |
| `array` | `minItems: N` / `maxItems: N` | Bound the list size |
| `array` | `uniqueItems: true` | Dedupe (rarely needed) |
| `object` | `properties: { ... }` with constraints on each | Nested constraints |
| `object` | `additionalProperties: false` | Lock the object shape |

**The pattern for IDs:**
```json
{
  "session_id": {
    "type": "string",
    "pattern": "^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$",
    "description": "Session UUID. Returned by claude_execute and accepted by claude_session or subsequent claude_execute calls."
  }
}
```

Strict regex on IDs prevents garbage input, makes the LLM copy from previous results, and gives you a single place to validate.

**The pattern for choices:**
```json
{
  "mode": {
    "type": "string",
    "enum": ["print", "interactive"],
    "default": "print",
    "description": "Execution mode. 'print' runs headless and exits. 'interactive' starts a TTY session."
  }
}
```

Enums are MUCH better than free-form strings for things like mode, format, permission level, output type.

**The pattern for bounded sizes:**
```json
{
  "allowed_tools": {
    "type": "array",
    "items": { "type": "string", "maxLength": 32 },
    "maxItems": 20,
    "description": "Tool allowlist. Use 'default' for all built-in tools, or specific names like 'Bash', 'Edit', 'Read'."
  }
}
```

`maxItems: 20` on the array + `maxLength: 32` on items prevents the LLM from constructing a 10,000-element allowlist.

---

## §5. `oneOf` vs discriminator enum: the right call 95% of the time

**The anti-pattern (use `oneOf` for "kinds of X"):**
```json
// DON'T DO THIS
{
  "oneOf": [
    { "type": "object", "properties": { "kind": { "const": "user" }, "user_id": { "type": "string" } }, "required": ["kind", "user_id"] },
    { "type": "object", "properties": { "kind": { "const": "group" }, "group_id": { "type": "string" } }, "required": ["kind", "group_id"] }
  ]
}
```

This works but: harder to describe in a tool's `description`, costs more tokens, and the LLM has to reason about which branch.

**The right pattern (discriminator enum + flat fields):**
```json
{
  "type": "object",
  "properties": {
    "kind": {
      "type": "string",
      "enum": ["user", "group"],
      "description": "Whether to target a user or a group."
    },
    "user_id": { "type": "string", "description": "User ID (required if kind=user)." },
    "group_id": { "type": "string", "description": "Group ID (required if kind=group)." }
  },
  "required": ["kind"],
  "oneOf": [
    { "properties": { "kind": { "const": "user" } }, "required": ["user_id"] },
    { "properties": { "kind": { "const": "group" } }, "required": ["group_id"] }
  ]
}
```

Now the LLM picks `kind` first (easy enum), then fills the right field. The server validates cross-field requirements (oneOf checks).

**When `oneOf` IS the right call:**
- The variants are genuinely different shapes (e.g., a `value` field that's a string OR a number OR an array, depending on `type`)
- The discriminator enum doesn't work (e.g., the user might pass the right shape but the wrong type)
- You're matching against an external schema (e.g., a third-party API)

**The 95/5 rule:** use a discriminator `enum` for 95% of "kind of X" cases; use `oneOf` for 5% where the variants truly have different structures.

---

## §6. Required vs optional

**Default to required** for things the tool cannot function without.
**Default to optional** for things that have sensible defaults.

```json
{
  "properties": {
    "prompt": { "type": "string", "description": "..." },     // required, tool can't run without
    "model": { "type": "string", "default": "sonnet" },        // optional, has default
    "max_budget_usd": { "type": "number", "minimum": 0, "maximum": 1000 }  // optional
  },
  "required": ["prompt"]
}
```

**The pattern for "one of these must be set":**
Use `anyOf` with a top-level required constraint:
```json
{
  "type": "object",
  "properties": {
    "user_id": { "type": "string" },
    "group_id": { "type": "string" }
  },
  "anyOf": [
    { "required": ["user_id"] },
    { "required": ["group_id"] }
  ]
}
```

**The "all optional" trap:** if everything is optional, the LLM is unsure which to fill. If you have 5 optional fields and the LLM should always fill 1 of them, mark that one as `default` and the others as truly optional (rare combinations).

---

## §7. Description writing: earn your context cost

Every description in your schema costs tokens for the LLM to read on every tool call. Wasted words = wasted money + noise. Use the budget wisely.

**Bad description (waste of tokens):**
```json
{
  "description": "The name of the file to read."
}
```

**Good description (LLM-actionable):**
```json
{
  "description": "Path to the file to read. Absolute path preferred; relative paths resolve against the server's working directory. Must be within the allowed_directories list."
}
```

**Recipe for good descriptions:**
1. **What it is** (1 short clause)
2. **Format/shape** (e.g., "absolute path", "ISO 8601 timestamp", "comma-separated")
3. **Constraints** (e.g., "must be one of [a, b]", "max 10 items")
4. **Side effects or safety rails** (e.g., "do NOT include 'DROP' or 'DELETE'")

**Tool-level description formula:**
```
[Verb phrase describing what the tool does]. [When to use it]. [When NOT to use it].
```

```json
{
  "description": "Read a file's contents. Use when you need to inspect a file before editing. Do NOT use for binary files (use read_binary instead)."
}
```

**When-to-use guidance in tool description is high-leverage** — it's the main thing the LLM uses for tool selection.

---

## §8. Property naming

| Convention | Example | When |
|---|---|---|
| `snake_case` | `user_id`, `max_budget_usd` | Default for MCP tool args (matches JSON conventions) |
| `camelCase` | `userId`, `maxBudgetUsd` | Only if your wrapper auto-converts (most don't) |
| `verb_noun` (params) | `search_query`, `file_path` | When the name should hint at usage |
| `noun` (data) | `query`, `path` | When it's obvious from context |
| Prefix with domain | `github_repo`, `jira_issue` | When you have many tools from one domain (5+) |

**The "`s` suffix" trap:**
```json
// BAD: ambiguous
{ "type": "array", "items": { "type": "string" }, "description": "files" }

// GOOD: explicit
{ "type": "array", "items": { "type": "string" }, "description": "List of file paths to read, one per line. Each path must be within allowed_directories." }
```

**The boolean `is_*` prefix:** most LLM-friendly:
```json
{ "is_recursive": { "type": "boolean", "description": "If true, recurse into subdirectories." } }
```
vs
```json
{ "recursive": { "type": "boolean", "description": "Recurse into subdirectories." } }
```

Both work. `is_*` is more explicit; the second is more idiomatic. Pick one and be consistent.

---

## §9. Nested objects: avoid when possible

**The problem with nesting:** the LLM has to reason about "is this field under `.input` or under `.input.user`?" Costs context, hurts accuracy.

**Pattern: flatten with a prefix**
```json
// AVOID
{
  "input": {
    "type": "object",
    "properties": {
      "user": { "type": "object", "properties": { "id": { "type": "string" }, "name": { "type": "string" } } }
    }
  }
}

// PREFER
{
  "user_id": { "type": "string" },
  "user_name": { "type": "string" }
}
```

**When nesting IS the right call:**
- The grouping has semantic meaning (e.g., `pagination: { page, per_page }` — the LLM should fill them together)
- The nested object is from a third-party schema (you have to match it)
- You're inside a `oneOf` variant (the variant is by definition nested)

**The 2-level rule:** MCP tool schemas should have at most 2 levels of nesting (root object → properties). 3+ levels means split into multiple tools or pass the deep bit as a JSON string.

---

## §10. Defaults that help

```json
{
  "max_results": { "type": "integer", "minimum": 1, "maximum": 100, "default": 10 },
  "sort_order": { "type": "string", "enum": ["asc", "desc"], "default": "asc" },
  "include_metadata": { "type": "boolean", "default": false }
}
```

**When to set `default`:**
- The value is what the LLM would default to anyway
- It saves the LLM from thinking about the field
- It makes the tool's behavior predictable

**When NOT to set `default`:**
- The LLM should explicitly choose (e.g., `permission_mode` — bad to default silently)
- The default depends on user context (use server-side config instead)
- The default would mask a bug (e.g., `verify_ssl: true` — should be explicit, not defaulted)

---

## §11. Tool name = verb + noun

The tool name is the LLM's first signal for tool selection. It should be:
- **Self-describing** — `read_file`, not `rf`
- **Action-oriented** — `create_issue`, not `issue`
- **Distinct from other tools** — `list_repos` and `search_repos` are both fine, `repos_list` and `repos_search` are too similar
- **Within 1-128 chars** (MCP spec requirement)
- **snake_case or kebab-case** (don't mix)

**Length sweet spot:** 8-30 chars. Shorter = less informative. Longer = harder to scan in tool lists.

**The "tool list prefix" pattern** (when you have 5+ tools from one domain):
```
github_list_repos
github_get_repo
github_create_issue
github_search_issues
github_list_pull_requests
```

The `github_` prefix helps the LLM scope its tool selection. Don't use it for 2-3 tools; the prefix eats more context than it saves.

**Bad names (and why):**
- `process` — too generic, conflicts with other servers
- `v2_search` — version in the name is an anti-pattern; evolve the schema instead
- `do_thing` — vague
- `repo-tool-1` — meaningless

---

## §12. Schemas for outputs (outputSchema)

MCP supports an optional `outputSchema` for tools, declaring the shape of the successful response:

```json
{
  "name": "get_weather",
  "outputSchema": {
    "type": "object",
    "properties": {
      "temperature_c": { "type": "number" },
      "condition": { "type": "string" },
      "humidity": { "type": "integer", "minimum": 0, "maximum": 100 }
    },
    "required": ["temperature_c", "condition"]
  }
}
```

**Why use outputSchema:**
- The host can validate the response
- The LLM can use the response directly (no need to re-parse natural language)
- Tests can assert the response shape

**When NOT to use outputSchema:**
- The response is truly free-form (e.g., a tool that returns arbitrary text)
- The response is large and variable (e.g., a log dump)
- You'd be tempted to use `additionalProperties: true` — then don't bother

**The `additionalProperties: true` smell:** if your outputSchema needs `additionalProperties: true`, you don't have a schema — you have a hint. Use `description` to document the expected fields instead.

---

## §13. Common pitfalls catalog

| Pitfall | What goes wrong | Fix |
|---|---|---|
| `additionalProperties: true` | LLM hallucinates fields; server silently ignores | Set to `false` unless you have a real reason |
| No `required` field | LLM doesn't know what's mandatory; produces incomplete calls | Always include `required: [...]` with the truly mandatory fields |
| Missing `description` on properties | LLM has to guess what each field is; gets them wrong | Every property gets a `description` — non-negotiable |
| Vague descriptions ("the name of X") | LLM doesn't know format/constraints | Add format, constraints, examples |
| Deeply nested objects (>2 levels) | LLM loses track of where it is; produces malformed calls | Flatten or pass-through as JSON string |
| Free-form string for structured data | LLM produces ambiguous parsable-but-wrong content | Use type + constraints; pass-through deep stuff as JSON string |
| `oneOf` for "kinds of X" instead of discriminator enum | LLM has to reason about branches; higher failure rate | Discriminator `enum` + flat fields + cross-field validation via `oneOf` |
| Tool name in `kebab-case` mixed with `snake_case` | LLM doesn't know what to expect | Pick one convention, be consistent |
| Missing `enum` for "kind" fields | LLM invents values | Always enum, never free string for bounded choices |
| `maxLength: 1000000` on text fields | LLM dumps huge outputs; server gets bloated responses | Reasonable maxLength (1-100 KB depending on use) |
| Boolean `*_enabled` instead of verb-form | Less clear semantically | `enable_X: true` is more explicit than `x_enabled: true` |
| Missing `$schema` field | Default is 2020-12, but explicit is better | `"$schema": "http://json-schema.org/draft/2020-12/schema"` |
| Using `format: "uuid"` alone | `format` is informational only — the schema doesn't enforce | Combine `format: "uuid"` with `pattern: "^[0-9a-f-]{36}$"` |
| Inconsistent naming (mix of `id` and `Id`) | LLM has to remember two patterns | Pick one (`id` for snake_case, `Id` for camelCase) and stick to it |

---

## §14. Schemars attribute cheat-sheet

The full attribute vocabulary, serde cross-effects, escape hatches, and MCP-flavored decision rules are in `references/schemars-cheatsheet.md`. You MUST read it BEFORE writing Rust types for tool input/output. Do not proceed without reading it.

---

## §15. Handoff to other skills

- **When to split one tool into N** → `mcp-server-design` §3
- **Output contract (CallToolResult text+JSON)** → `mcp-server-design` §5
- **Error code discipline** → `mcp-server-design` §6
- **Implementation: rmcp + schemars attribute mapping** → `mcp-server-implement` §4
- **Tool annotations (readOnlyHint, destructiveHint, idempotentHint)** → `mcp-server-design` §7
- **How Claude Code actually discovers and uses the tools** → `mcp-server-design` §14 (Consuming in Claude Code)

---

## §16. Anti-patterns

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

---

## §17. Key sources

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
