# Tool Patterns

Patterns and anti-patterns for designing MCP tools in the `claude-cli-wrapper` server. The schema principles (flat surface, serialized strings, UUID enums, pass-through) are non-negotiable. The patterns below show what they look like in practice.

## Pattern 1: One Tool, One Job

Each tool does one thing. If the description has "and" in it ("attaches and validates context"), split the tool.

**Good:** `context_attach`, `context_validate` — separate.
**Bad:** `context_attach_and_validate` — coupled concerns; tests have to mock both paths.

## Pattern 2: Stable, Stable, Stable Identifiers

`session_id`, `entry_id`, `agent_name` are stable across calls. The wrapper assigns them on creation and never reuses them.

```
session_create → { session_id: "550e8400-e29b-41d4-a716-446655440000" }
session_get(session_id) → uses the same ID
session_end(session_id) → same ID, idempotent
```

**Anti-pattern:** Generating a fresh ID on every call (defeats lookup).
**Anti-pattern:** Reusing IDs across sessions (defeats audit).

## Pattern 3: Enums Over Flags

Use closed enums instead of overlapping booleans.

**Good:** `mode: "code" | "plan" | "ask"`.
**Bad:** `read_only: true, dry_run: false, no_exec: true` — three flags for one concept.

## Pattern 4: Pagination via Opaque Cursors

Lists return `cursor` strings. The wrapper does not decode them.

```json
{
  "sessions": [...],
  "next_cursor": "eyJwYWdlIjoyfQ=="
}
```

The caller passes the cursor back verbatim. The wrapper advances. Done.

**Anti-pattern:** Offset/limit pagination. The cursor encodes the snapshot; offsets can skip or duplicate under concurrent writes.

## Pattern 5: Errors as Data

Every tool returns errors as a structured result, not a thrown exception that the caller has to catch.

```json
{
  "success": false,
  "error": {
    "code": "INVALID_ENUM",
    "field": "mode",
    "allowed": ["code", "plan", "ask"]
  }
}
```

**Anti-pattern:** Throwing a string. Throwing an exception. Returning HTTP-style status codes in a string field.

## Pattern 6: Idempotency Where It Matters

`session_end` and `agent_stop` are idempotent. They return success on the first call, success on the Nth call, and never error.

**Why:** Callers retry on network failure. Non-idempotent terminations make retries expensive.

**Anti-pattern:** Idempotency for `session_create` (it would silently swallow duplicate IDs). Idempotency is for terminators and updaters, not creators.

## Pattern 7: Timeouts Are Caller-Set

`execute` accepts `timeout_seconds` (default 600). The wrapper enforces it and returns a `TIMEOUT` error code on breach. The wrapper does not silently extend.

**Anti-pattern:** Wrapper-internal timeout that's longer than the caller's wall clock. Now the caller has given up but the wrapper keeps working.

## Pattern 8: Config Is a Blob, Params Are Enums

- **Config** (`config_set`): JSON-encoded strings, opaque, pass-through.
- **Params** (`execute.mode`): closed enums, validated, normalized.

The boundary is: "does the wrapper need to know what this is?" If yes → enum. If no → string.

## Pattern 9: Naming Conventions

| Tool family | Naming style | Example |
|-------------|--------------|---------|
| Lifecycle | `verb_noun` | `session_create`, `agent_stop` |
| Read | `noun_get` / `noun_list` | `config_get`, `session_list` |
| Mutate | `verb_noun` or `noun_verb` | `context_attach`, `context_replace` |

All tool names are lowercase, snake_case, no abbreviations beyond common ones (`id`, `cwd`).

## Anti-Pattern Catalog

| Anti-pattern | Why it's wrong | Fix |
|--------------|----------------|-----|
| `config: { key: value, nested: { ... } }` | Breaks flat surface; caller can't serialize predictably. | `config: "{...}"` (JSON string) |
| `mode: "auto"` | Adds a magic value that hides caller intent. | Use `ask` for ambiguous tasks. |
| `output_format: "yaml"` | New formats need schema support, not just labels. | Use `json` or `text`. |
| `session_id: "abc123"` | Free-form string. Caller typo is silent. | Enforce UUID v4 regex. |
| `payload: { ... }` | Object. Wrapper is forced to inspect. | `payload: "{...}"` (string). |
| `agent_name: ""` | Empty string is not a stable identifier. | Either provide a name or let the wrapper assign. |
| Returning nested error objects | Forces caller to traverse. | Flat error codes. |

## Reviewer Checklist

Before merging a new tool, verify:

- [ ] Tool does one job.
- [ ] Identifiers are stable strings; UUIDs are validated.
- [ ] Enums are closed; non-enum fields are flat.
- [ ] Lists paginate via opaque cursors.
- [ ] Errors are structured results, not exceptions.
- [ ] Terminators are idempotent.
- [ ] Timeouts are caller-set and enforced.
- [ ] Name follows `verb_noun` or `noun_get` style.
- [ ] SKILL.md cites `schema-reference.md` and this file.
