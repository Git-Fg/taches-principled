# Rust Implementation Guidance

The `claude-cli-wrapper` server is implemented in Rust. This document is the authoritative reference for contributors. It captures conventions, crate choices, and module layout that the codebase uses; deviating from them requires a HIGH-severity design review.

## Crate Choices

| Concern | Crate | Why |
|---------|-------|-----|
| MCP protocol | `rmcp` | Idiomatic Rust MCP server with tool registration and transport abstractions. |
| Async runtime | `tokio` (multi-thread) | Industry standard; required by `rmcp`. |
| Serde | `serde` + `serde_json` | Standard JSON. We always use `serde_json::Value` for opaque payloads to avoid re-parsing. |
| UUID | `uuid` (v4 feature) | CSPRNG-backed UUID v4 generation; matches our schema regex. |
| Regex | `regex` | Once-compiled `LazyLock<Regex>` for the session_id pattern. |
| CLI flag parsing | `clap` (derive) | We do not parse Claude Code CLI flags — only the wrapper's own. |
| Errors | `thiserror` | Typed errors per module; the top-level handler maps to MCP error codes. |
| Logging | `tracing` + `tracing-subscriber` | Structured logs; never log full payloads (PII risk). |
| Time | `std::time::Instant` for durations, `chrono` for ISO 8601 timestamps in outputs. |

## Module Layout

```
src/
├── main.rs            # tokio main, MCP server bootstrap
├── lib.rs             # re-exports
├── tools/
│   ├── mod.rs
│   ├── execute.rs     # execute tool
│   ├── session.rs     # session_* tools
│   ├── context.rs     # context_* tools
│   ├── review.rs      # review tool
│   ├── agent.rs       # agent_* tools
│   └── config.rs      # config_* tools
├── schema/
│   ├── mod.rs
│   ├── enums.rs       # Mode, Effort, OutputFormat
│   ├── ids.rs         # SessionId, EntryId, AgentName — newtypes + UUID validation
│   └── error.rs       # ToolError, INVALID_ENUM, INVALID_UUID, etc.
├── runtime/
│   ├── mod.rs
│   ├── spawn.rs       # tokio::process::Command for the CLI binary
│   └── timeout.rs     # timeout enforcement
├── store/
│   ├── mod.rs
│   ├── sessions.rs    # session state
│   ├── context.rs     # context payloads
│   └── config.rs      # config file IO
└── mcp/
    ├── mod.rs
    └── server.rs      # tool registration, request routing
```

## Key Conventions

### Newtype IDs

Session IDs, entry IDs, and agent names are newtypes around `String` with a constructor that validates.

```rust
#[derive(Debug, Clone, PartialEq, Eq, Hash)]
pub struct SessionId(String);

impl SessionId {
    pub fn new(s: &str) -> Result<Self, ToolError> {
        if UUID_V4.is_match(s) {
            Ok(Self(s.to_string()))
        } else {
            Err(ToolError::InvalidUuid { field: "session_id" })
        }
    }

    pub fn generate() -> Self {
        Self(uuid::Uuid::new_v4().to_string())
    }
}
```

Why: catches schema violations at the boundary, not deep in a `match`.

### Enum Validation

Mode, effort, and output_format are `enum`s with `FromStr` and `Default`.

```rust
#[derive(Debug, Clone, Copy, Default, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "lowercase")]
pub enum Mode {
    #[default]
    Code,
    Plan,
    Ask,
}

impl FromStr for Mode {
    type Err = ToolError;
    fn from_str(s: &str) -> Result<Self, Self::Err> {
        match s {
            "code" => Ok(Self::Code),
            "plan" => Ok(Self::Plan),
            "ask" => Ok(Self::Ask),
            _ => Err(ToolError::InvalidEnum {
                field: "mode",
                allowed: &["code", "plan", "ask"],
            }),
        }
    }
}
```

### Pass-Through Payloads

Opaque payloads travel as `String`. They are stored and forwarded as bytes. The wrapper never deserializes them.

```rust
pub struct ContextEntry {
    pub id: EntryId,
    pub session_id: SessionId,
    pub kind: ContextKind,
    pub payload: String,   // JSON-encoded; we do not parse
    pub label: Option<String>,
    pub created_at: DateTime<Utc>,
}
```

### Errors

The wrapper returns `Result<ToolOutput, ToolError>`. `ToolError` has a `code()` method that maps to MCP error codes (`INVALID_ENUM`, `INVALID_UUID`, `TIMEOUT`, `IO`, `INTERNAL`). All errors serialize as a flat object:

```json
{
  "code": "INVALID_ENUM",
  "field": "mode",
  "allowed": ["code", "plan", "ask"]
}
```

### Timeouts

`tokio::time::timeout` around the process spawn. On breach, kill the child (best-effort) and return `TIMEOUT`. The wrapper does not retry; the caller decides.

```rust
let result = tokio::time::timeout(
    Duration::from_secs(params.timeout_seconds),
    child.wait(),
).await;

match result {
    Ok(Ok(status)) => /* map exit code */,
    Ok(Err(e)) => Err(ToolError::Io(e.to_string())),
    Err(_) => {
        let _ = child.start_kill();
        Err(ToolError::Timeout)
    }
}
```

### Idempotency

`session_end` and `agent_stop` are no-ops if the target is already gone.

```rust
pub async fn end(&self, id: &SessionId) -> Result<(), ToolError> {
    let mut store = self.store.lock().await;
    if store.sessions.remove(id).is_none() {
        return Ok(()); // idempotent
    }
    Ok(())
}
```

## Testing

- **Unit tests** for newtypes (UUID regex), enum `FromStr`, and pass-through serialization.
- **Property tests** for ID generation (always valid UUIDs, never collide across N=1000).
- **Integration tests** that spawn the server and exercise each tool via the MCP client SDK.
- **Schema compliance tests** that load every tool's parameter schema and assert the five schema principles (flat, serialized, UUID, enums, pass-through).

## Performance Notes

- The wrapper is I/O bound (process spawn, file IO). Tokio's default thread pool is sufficient.
- The `regex` for UUID validation is compiled once via `LazyLock`; never compile per-call.
- The store is in-memory by default; persistence is opt-in via config (see `config-file.md`).
- For very large contexts, prefer `tokio::fs` async IO and avoid loading the whole payload into memory at once.

## What Rust Is NOT Used For

- Validating caller payloads. The wrapper is transport; it does not parse `payload` strings.
- Implementing review logic. The wrapper shells out to the underlying CLI/reviewer.
- Persisting structured session state beyond the configured store. Anything richer belongs in the caller.
