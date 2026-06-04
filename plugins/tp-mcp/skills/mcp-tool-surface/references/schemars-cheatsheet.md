# Schemars attribute cheat-sheet

`schemars` derives JSON Schema from your Rust types. The attribute vocabulary maps 1:1 to JSON Schema keywords — most have a Rust-idiomatic form plus a raw `extend("keyword" = value)` escape hatch when you need a keyword schemars doesn't wrap.

| Attribute | JSON Schema | When to use |
|---|---|---|
| `#[schemars(description = "...")]` | `"description": "..."` | Per-field or per-variant description. The LLM's instruction manual for this property. |
| `#[schemars(range(min = 0, max = 100))]` | `"minimum": 0, "maximum": 100` | Numeric bounds. `min` and `max` are inclusive. |
| `#[schemars(range(min = 0))]` | `"minimum": 0` | One-sided bound. Omit `max` for "no upper limit". |
| `#[schemars(length(min = 1, max = 64))]` | `"minLength": 1, "maxLength": 64` | String and array length bounds. |
| `#[schemars(length(max = 20))]` | `"maxItems": 20` (for `Vec<T>`) | Array-size cap. LLM can't dump 1000 items if the schema says 20. |
| `#[schemars(regex = "^[0-9a-f-]{36}$")]` | `"pattern": "^[0-9a-f-]{36}$"` | String pattern. Anchors are implicit in JSON Schema — write the pattern as if it had `^(?:...)$` around it. |
| `#[schemars(unique_items)]` | `"uniqueItems": true` | Array elements must be unique. |
| `#[schemars(extend("format" = "uri"))]` | `"format": "uri"` | Format hint (`date-time`, `email`, `uri`, `uuid`, `ipv4`, …). LLM and validators may use the format. |
| `#[schemars(extend("const" = "draft"))]` | `"const": "draft"` | Constant value — field must be exactly this. Useful for type discriminators. |
| `#[schemars(extend("default" = json!([])))]` | `"default": []` | Default value (the `#[serde(default)]` form is usually simpler — see below). |
| `#[schemars(extend("examples" = [...]))]` | `"examples": [...]` | In-schema examples. Some clients surface them to the LLM. |
| `#[schemars(extend("additionalProperties" = false))]` | `"additionalProperties": false` | Lock the schema. The single most important rule (see §3 of the SKILL). |
| `#[schemars(extend("propertyNames" = ...))]` | `"propertyNames": {...}` | Restrict the keys of an object map. |
| `#[schemars(schema_with = "fn_name")]` | custom | Last resort — call a function that returns a `Schema`. Use when the keyword you need has no attribute form. |

## `serde` attributes that affect the schema (commonly forgotten)

| Attribute | Effect on JSON Schema |
|---|---|
| `#[serde(default)]` on a field | field becomes **optional** (omitted from `required`) |
| `#[serde(default = "fn_name")]` on a field | field becomes optional + gets `"default": <fn return>` |
| `#[serde(rename_all = "lowercase")]` on enum | variants become `"lowercase"` strings |
| `#[serde(rename_all = "kebab-case")]` on enum | variants become `"kebab-case"` strings (`stream-json`) |
| `#[serde(rename_all = "camelCase")]` on enum | variants become `"camelCase"` strings (`bypassPermissions`) |
| `#[serde(rename = "x-id")]` on variant | one-off override of the rename rule |
| `#[serde(tag = "type")]` on enum | **adjacent tagging** — the variant discriminator becomes a property; the variant data becomes siblings. Often wrong for MCP — use a plain `enum` action field instead. |
| `#[serde(untagged)]` on enum | **no discriminator in schema** — schemars will emit a `"oneOf"` of the variants' shapes. Token-expensive; almost always use a discriminator instead. |
| `#[serde(deny_unknown_fields)]` on struct | locks the input — pairs with `additionalProperties: false` (which schemars derives from this on `deny_unknown_fields` structs) |
| `#[serde(skip_serializing_if = "Option::is_none")]` | only affects output serialization; the schema still shows the field as `Option<T>`. Use `#[serde(default)]` to make it optional in input. |

## Two escape hatches for keywords schemars doesn't wrap directly

```rust
// 1. extend("keyword" = value) — most keywords
#[schemars(extend("format" = "uri"))]
pub url: String,

#[schemars(extend("examples" = [
    json!({ "city": "Paris" }),
    json!({ "city": "London" }),
]))]
pub query: WeatherQuery,

// 2. schema_with = "fn" — full custom Schema
fn string_with_min_length_3(_: &mut schemars::SchemaGenerator) -> schemars::Schema {
    schemars::json_schema!({
        "type": "string",
        "minLength": 3,
    })
}
#[derive(JsonSchema)]
struct MyInput {
    #[schemars(schema_with = "string_with_min_length_3")]
    pub name: String,
}
```

## The MCP-flavored decision rules (when to reach for which attribute)

- **The LLM hallucinates field values** → add `#[schemars(regex = ...)]` or an `enum`, not a free-form `String`
- **The LLM dumps a 5000-line array** → `#[schemars(length(max = N))]` on the `Vec<T>`
- **The LLM sends negative numbers where it shouldn't** → `#[schemars(range(min = 0))]`
- **The LLM sends string IDs that don't match your DB format** → `#[schemars(regex = "...")]`
- **The LLM doesn't know which enum variant to pick** → add a per-variant `///` doc comment (schemars pulls doc comments into the variant's description in the schema)
- **The LLM sends extra fields you never asked for** → `#[serde(deny_unknown_fields)]` on the struct, which yields `additionalProperties: false` in the schema

> **Token cost reminder (§9 of the SKILL):** every `#[schemars(extend("examples" = ...))]` example costs context tokens for every model call, forever. Two or three compact examples beats a full payload. Skip examples for fields that are self-evident from their type and description.
