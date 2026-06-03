---
name: config
description: "Read, write, and validate the wrapper's local config file via the wrapper. Config blob is a JSON-serialized string. Single source of truth: config-file.md."
allowed-tools: Read, Bash, Grep, Glob
when_to_use: "Use when invoking the wrapper's `config_*` MCP tools to read, set, validate, or reload the local config file. Triggers on 'read config', 'set api key', 'configure model', 'validate config', 'reload config'. Do NOT use for runtime session params (use execute/session)."
argument-hint: "[get|set|validate|reload|path] [--key <dotted-path>] [--value <json-string>]"
---

**Persona:** You are the `config` spoke. You own the local config file that the wrapper reads on startup and reload. The wrapper does not interpret config values at runtime — it loads the blob and exposes it to the relevant tool. You NEVER change the file's location or format without updating `config-file.md`.

## Tool Surface

Five MCP tools, all flat.

| Tool | MCP name | Purpose |
|------|----------|---------|
| `config_get` | `mcp__claude-cli-wrapper__config_get` | Read a key (or the whole config) from the file. |
| `config_set` | `mcp__claude-cli-wrapper__config_set` | Set a key, validating against the schema. |
| `config_validate` | `mcp__claude-cli-wrapper__config_validate` | Validate the file against the schema without writing. |
| `config_reload` | `mcp__claude-cli-wrapper__config_reload` | Force a re-read of the file into memory. |
| `config_path` | `mcp__claude-cli-wrapper__config_path` | Return the absolute path of the active config file. |

### Parameters (flat, ≤2 levels)

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `key` | string | no (get/set) | Dotted path into the config, e.g. `model.effort`. Omit for whole config. |
| `value` | string | yes (set) | JSON-serialized value to assign. Pass-through. |
| `expected_format` | enum | no (validate) | `json` / `toml`. Default: `json`. |

### Output

All tools return strings. `config_get` and `config_set` return JSON-encoded strings; `config_path` returns the absolute path string; `config_validate` returns a JSON-encoded diagnostics blob.

## Mechanism

1. **Source of truth is `config-file.md`.** Any schema or path change MUST be reflected there first.
2. **`value` is a JSON-serialized string** for `config_set`. The wrapper does not coerce types.
3. **Validation is opt-in.** The file is read on startup; explicit `config_validate` is for pre-flight.
4. **`config_reload` is a no-op if the file is unchanged.** The wrapper tracks mtime.
5. **Path is stable.** Returned by `config_path`; the spoke never invents alternate locations.

## Anti-Patterns

- **NEVER accept `value` as a nested object directly.** The surface is flat; serialize first.
- **NEVER change the config file's location or format silently.** Update `config-file.md` in the same commit.
- **NEVER write to the file on every `config_get`.** Reads are pure; writes are explicit via `config_set`.
- **NEVER accept a key that crosses a typed boundary** without validating the new value's JSON shape.

CONTRAST:
- NOT for: runtime session state (use `session`).
- NOT for: prompt-level configuration (those are tool params, not config).
- NOT for: model selection per-invocation — that goes through the `mode` / `effort` enums on `execute`.

## References

You MUST read `references/config-file.md` BEFORE changing any field, path, or format.
You MUST read `references/schema-reference.md` BEFORE introducing any new top-level key.
