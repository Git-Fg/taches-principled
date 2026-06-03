# Configuration File Format

The wrapper reads a single local config file on startup and on `config_reload`. This document is the authoritative reference for its format, location, and lifecycle. Any change to the file's path, format, or schema MUST be reflected here in the same commit.

## Location

Default: `~/.claude-cli-wrapper/config.json`.

Override via the `CLAUDE_CLI_WRAPPER_CONFIG` environment variable (absolute path). `config_path` returns the active path, never invents an alternate.

## Format

JSON. Top-level keys (all optional except where noted):

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `model` | object | — | Default model settings. |
| `modes` | object | — | Per-mode defaults. |
| `effort` | object | — | Per-effort-level defaults. |
| `output` | object | — | Output handling. |
| `storage` | object | — | Where session/context state lives. |
| `timeouts` | object | — | Default and per-tool timeouts. |
| `limits` | object | — | Size and count caps. |
| `logging` | object | — | Tracing configuration. |

Each top-level key is itself an object with a small fixed schema; deep nesting beyond two levels is forbidden by the same flat-surface principle that governs tool parameters. If you need more, you are coupling concerns.

## Example

```json
{
  "model": {
    "default": "claude-sonnet-4-5",
    "alias": {
      "fast": "claude-haiku-4-5",
      "smart": "claude-opus-4-5"
    }
  },
  "modes": {
    "default": "code",
    "plan": {
      "model": "claude-opus-4-5",
      "effort": "high"
    }
  },
  "effort": {
    "default": "medium"
  },
  "output": {
    "default_format": "text",
    "max_body_bytes": 5242880
  },
  "storage": {
    "backend": "memory",
    "memory": {
      "max_sessions": 1000
    }
  },
  "timeouts": {
    "default_seconds": 600,
    "per_tool": {
      "review": 900,
      "execute": 600
    }
  },
  "limits": {
    "max_payload_bytes": 5242880,
    "max_findings": 100,
    "max_sessions": 1000
  },
  "logging": {
    "level": "info",
    "format": "json",
    "redact_payloads": true
  }
}
```

## Key Reference

### `model`

| Subkey | Type | Default | Description |
|--------|------|---------|-------------|
| `default` | string | `claude-sonnet-4-5` | Model used when the tool does not specify one. |
| `alias` | object | — | Map of short names to model identifiers. |

### `modes`

| Subkey | Type | Default | Description |
|--------|------|---------|-------------|
| `default` | enum | `code` | Mode used when `execute` does not specify one. |
| `<mode>` | object | — | Per-mode overrides for `model` and `effort`. |

### `effort`

| Subkey | Type | Default | Description |
|--------|------|---------|-------------|
| `default` | enum | `medium` | Effort used when the tool does not specify one. |

### `output`

| Subkey | Type | Default | Description |
|--------|------|---------|-------------|
| `default_format` | enum | `text` | Output format used when the tool does not specify one. |
| `max_body_bytes` | integer | `5242880` (5 MiB) | Truncate larger bodies; do not error. |

### `storage`

| Subkey | Type | Default | Description |
|--------|------|---------|-------------|
| `backend` | enum | `memory` | `memory` / `file` / `sqlite`. |
| `memory.max_sessions` | integer | `1000` | LRU eviction when exceeded. |
| `file.path` | string | — | Required when `backend=file`. |
| `sqlite.path` | string | — | Required when `backend=sqlite`. |

### `timeouts`

| Subkey | Type | Default | Description |
|--------|------|---------|-------------|
| `default_seconds` | integer | `600` | Wall-clock timeout per tool call. |
| `per_tool.<name>` | integer | — | Override per tool. |

### `limits`

| Subkey | Type | Default | Description |
|--------|------|---------|-------------|
| `max_payload_bytes` | integer | `5242880` | Cap for `context_attach` payload size; reject over. |
| `max_findings` | integer | `100` | Cap for `review` output; truncate with marker. |
| `max_sessions` | integer | `1000` | Mirror of `storage.memory.max_sessions`. |

### `logging`

| Subkey | Type | Default | Description |
|--------|------|---------|-------------|
| `level` | enum | `info` | `error` / `warn` / `info` / `debug` / `trace`. |
| `format` | enum | `json` | `json` / `pretty`. |
| `redact_payloads` | boolean | `true` | Never log full payload bodies. |

## Lifecycle

1. **Read on startup.** The wrapper reads the file once during `main` and parses it. Failure to read or parse → fail fast with a clear error.
2. **`config_get` reads in-memory state.** The file is not re-read on every call.
3. **`config_set` writes atomically.** The wrapper writes to a tmp file, fsyncs, renames. A crash mid-write leaves the previous file intact.
4. **`config_reload` re-reads the file.** Mtime is checked; if unchanged, this is a no-op.
5. **`config_validate` is pure.** It parses the file into a `serde_json::Value` and runs the schema checks, but does not touch the in-memory state.

## Validation Rules

`config_validate` checks:

- File exists and is readable.
- Top-level is an object.
- Every enum value matches the closed set.
- `storage.backend=file` requires `storage.file.path`.
- `storage.backend=sqlite` requires `storage.sqlite.path`.
- All integer limits are positive.
- `timeouts.default_seconds` is in `[1, 86400]`.

It does NOT validate model identifiers (those are catalog values, not enum values).

## Schema Compliance

The config file follows the same five principles as tool parameters:

- **Flat surface** — at most one level of nesting under each top-level key.
- **Serialized structures as strings** — `alias` is the only nested object; deeper config is out of scope.
- **No UUIDs** — config does not carry session IDs.
- **Closed enums** — `modes.default`, `effort.default`, `output.default_format`, `storage.backend`, `logging.level`, `logging.format`.
- **Pass-through** — the wrapper does not interpret model identifiers; the runtime that consumes the config does.

## Anti-Patterns

- **NEVER embed secrets in cleartext in the file.** Use the OS keychain via the wrapper's `secret` subcommand (out of scope for this doc; tracked separately).
- **NEVER add a new top-level key without updating this document first.**
- **NEVER change the file's default location without a deprecation cycle** (env var override, then default, then old default).
- **NEVER parse the file as TOML or YAML.** The format is JSON. Use `serde_json::from_reader`.
