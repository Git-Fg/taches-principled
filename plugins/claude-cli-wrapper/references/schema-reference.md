# Schema Reference

This is the canonical schema documentation for the `claude-cli-wrapper` MCP server. Every tool MUST comply with the five principles below. Any deviation is a HIGH-severity bug.

## 1. Flat Parameter Surface (≤2 Levels)

Tools accept primitives and one level of nesting at most. Deep structures are JSON-serialized strings.

```json
{
  "prompt": "Refactor the auth module",
  "mode": "code",
  "extra_args": "[\"--dangerously-skip-permissions\", \"--verbose\"]"
}
```

**Why:** MCP tool schemas are surfaced to the model as JSON; nested objects balloon context and confuse routing. Flattening at the boundary keeps the surface scannable.

**Rule:** Any parameter whose value would be an object or array of length > 1 MUST be serialized as a JSON-encoded string. The wrapper deserializes internally.

## 2. Serialized Complex Structures as Strings

When a parameter is intrinsically structured (config blobs, glob lists, message arrays, metadata), accept it as a JSON-encoded string. Never accept an object.

```json
{ "include_paths": "[\"src/**/*.ts\", \"!**/*.test.ts\"]" }
```

**Why:** String keeps the tool surface flat, allows pass-through, and lets the caller choose its own serialization (canonical JSON today, msgpack or CBOR tomorrow).

**Rule:** The wrapper MUST NOT parse the string to validate. Pass through; the consumer of the data is responsible for interpretation.

## 3. UUID Regex for `session_id`

Every tool that accepts a session identifier MUST validate against:

```
^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$
```

This is UUID v4 in canonical lowercase form. The wrapper rejects any other form with a structured error and never falls back to "best-effort" parsing.

**Why:** Sessions are externally-issued by the `session_create` tool. Any deviation in the form suggests a caller bug, a stale ID, or a forged request. Failing fast at the boundary is the right call.

**Rule:** The wrapper assigns UUIDs using a CSPRNG and returns them as canonical strings. The spoke never fabricates a UUID to mask a missing one from the caller.

## 4. Enum Validation for `mode`, `effort`, `output_format`

Three fields are closed enums. The wrapper rejects any value not in the documented set.

| Field | Allowed values | Default |
|-------|----------------|---------|
| `mode` | `code`, `plan`, `ask` | `code` |
| `effort` | `low`, `medium`, `high`, `max` | `medium` |
| `output_format` | `text`, `json`, `stream-json` (execute only) | `text` |

**Why:** Enums are how the wrapper contracts with the caller. Adding a new mode silently is a breaking change; failing fast keeps both sides honest.

**Rule:** A value not in the set returns a structured `INVALID_ENUM` error citing the field name and the set of allowed values. No silent coercion.

## 5. Pass-Through Principle for Deep Objects

If the wrapper does not interpret a value (a payload, a config blob, a glob list, metadata), it MUST NOT validate, reformat, normalize, or re-encode it. It accepts a string, stores/forwards the string, and returns the string.

**Why:** The wrapper is a transport, not a validator. Validating the caller's data couples the wrapper to the caller's schema, which is a maintenance hazard.

**Rule:** If you find yourself wanting to parse a string parameter, you are probably in the wrong tool. Move the parsing to the spoke that owns the data.

## Compliance Checklist

Before merging a new tool or parameter, verify:

- [ ] No parameter has more than 2 levels of nesting.
- [ ] Every non-trivial structure is a JSON-encoded string parameter.
- [ ] Every `session_id` parameter is validated against the UUID v4 regex.
- [ ] `mode`, `effort`, and `output_format` use the closed enum sets above.
- [ ] No wrapper code parses a string parameter to extract fields.
- [ ] The tool's SKILL.md cites this file in its `## References` block.
