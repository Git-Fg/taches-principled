---
name: mcp-server-implement
description: Build an MCP server in Rust using rmcp + schemars + tokio. Tool attribute mapping (`#[tool]`, `#[tool_handler]`, `#[tool_router]`), JSON Schema constraint generation, enum/rename/optional idioms, server lifecycle (initialize → capabilities → shutdown), transport choice (stdio vs Streamable HTTP), stderr-only logging, error mapping, testing with the MCP Inspector. Use when the user says "implement an MCP server in Rust", "rmcp + schemars patterns", "build an MCP tool", "Rust MCP server", "transport choice stdio vs HTTP", "MCP server lifecycle".
when_to_use: |
  - "Build me an MCP server in Rust"
  - "Set up rmcp with schemars for tool schemas"
  - "Add a tool to my existing MCP server"
  - "How do I declare capabilities with rmcp?"
  - "How do I handle stdio vs Streamable HTTP?"
  - "How do I log without corrupting the JSON-RPC stream?"
---

# mcp-server-implement

The production side: build an MCP server in Rust with `rmcp` + `schemars`.
For the design principles (when to split tools, output contract, error codes),
see `mcp-server-design`. For the JSON Schema authoring details, see
`mcp-tool-surface`.

---

## §1. When this skill fires

**Use this skill when the user says any of:**
- "Implement an MCP server in Rust"
- "Use rmcp + schemars"
- "Build an MCP tool in Rust"
- "Add a tool to my existing MCP server"
- "Set up an MCP server with stdio / Streamable HTTP"
- "How do I declare capabilities in rmcp?"
- "Map Rust types to JSON Schema for MCP"
- "Implement an MCP tool with structured output"

**DO NOT use this skill for:**
- "Design an MCP server" / "1 tool vs N" / "schema design" → `mcp-server-design`
- "Write a good JSON Schema" / "constraints" / "descriptions" → `mcp-tool-surface`
- "Implement in Python" / "TypeScript" / "Go" → not covered (use SDK-specific docs)
- "Build an MCP client" → not covered (no client skill yet)

---

## §2. Cargo.toml setup

```toml
[package]
name = "my-mcp-server"
version = "0.1.0"
edition = "2024"

[dependencies]
rmcp = { version = "0.16", features = ["server", "transport-io", "transport-streamable-http-server", "macros"] }
tokio = { version = "1", features = ["full"] }
serde = { version = "1", features = ["derive"] }
serde_json = "1"
schemars = "0.8"
anyhow = "1"
thiserror = "2"
tracing = "0.1"
tracing-subscriber = { version = "0.3", features = ["env-filter"] }
async-trait = "0.1"
```

**Feature flags explained:**
- `server` — core server-side functionality
- `transport-io` — stdio transport (always needed for local servers)
- `transport-streamable-http-server` — Streamable HTTP transport (remote servers)
- `transport-sse-server` — legacy HTTP+SSE (only if you must support 2024-11-05 clients)
- `macros` — `#[tool]`, `#[tool_handler]`, `#[tool_router]`, `#[prompt]`, etc.
- `client` — only if you're also building a client in the same crate

---

## §3. The macro cheat sheet

```rust
use rmcp::{
    handler::server::wrapper::Parameters,
    schemars,        // re-exported for convenience
    tool, tool_handler, tool_router,
    ServerHandler, ServiceExt,
    transport::stdio,
    model::*,
};
use schemars::JsonSchema;
use serde::{Deserialize, Serialize};

// 1. Server struct (the "thing" that owns your tools)
#[derive(Clone)]
pub struct MyServer {
    // state goes here (e.g., Arc<Mutex<State>>)
    state: MyState,
}

// 2. Tool input struct (auto-generates the JSON Schema)
#[derive(Debug, Deserialize, Serialize, JsonSchema)]
pub struct MyToolParams {
    #[schemars(description = "First number to add")]
    pub a: i32,
    #[schemars(description = "Second number to add")]
    pub b: i32,
}

// 3. Tool methods on a `#[tool_router]` impl block
#[tool_router]
impl MyServer {
    #[tool(description = "Add two numbers")]
    fn add(&self, Parameters(MyToolParams { a, b }): Parameters<MyToolParams>) -> String {
        (a + b).to_string()
    }

    // Async tool: just make the function async
    #[tool(description = "Fetch a URL")]
    async fn fetch(&self, Parameters(p): Parameters<FetchParams>) -> Result<String, String> {
        // ...
    }
}

// 4. ServerHandler impl: declares capabilities and metadata
#[tool_handler(name = "my-mcp-server", version = "1.0.0", instructions = "A simple calculator")]
impl ServerHandler for MyServer {
    // Override default capabilities if needed
    fn get_info(&self) -> ServerInfo {
        ServerInfo {
            protocol_version: ProtocolVersion::V_2025_11_25,
            capabilities: ServerCapabilities::builder()
                .enable_tools()
                .build(),
            server_info: Implementation::from_build_env(),
            instructions: Some("A simple calculator".to_string()),
        }
    }
}

// 5. Main: bind to a transport and serve
#[tokio::main]
async fn main() -> anyhow::Result<()> {
    // Logging MUST go to stderr — stdout is the protocol stream
    tracing_subscriber::fmt()
        .with_writer(std::io::stderr)
        .with_env_filter(
            tracing_subscriber::EnvFilter::try_from_default_env()
                .unwrap_or_else(|_| "info".into())
        )
        .init();

    let server = MyServer { state: MyState::new() };
    let transport = stdio();
    let service = server.serve(transport).await?;
    service.waiting().await?;
    Ok(())
}
```

---

## §4. Attribute mapping (rmcp + schemars → JSON Schema)

| Rust | Attribute | JSON Schema output |
|---|---|---|
| `pub name: String` | (none) | `{ "type": "string" }` |
| `pub n: i32` with `#[schemars(range(min = 0, max = 100))]` | (none) | `{ "type": "integer", "minimum": 0, "maximum": 100 }` |
| `pub s: String` with `#[schemars(length(min = 1, max = 64))]` | (none) | `{ "type": "string", "minLength": 1, "maxLength": 64 }` |
| `pub id: String` with `#[schemars(regex = "^[0-9a-f-]{36}$")]` | (none) | `{ "type": "string", "pattern": "^[0-9a-f-]{36}$" }` |
| `pub tag: String` with `#[serde(default = "default_tag")]` | `default` | `"default": "<value>"` |
| `pub maybe: Option<String>` with `#[serde(skip_serializing_if = "Option::is_none")]` | skip | (omitted from output) |
| `pub items: Vec<String>` with `#[schemars(length(max = 10))]` | length | `{ "type": "array", "items": {...}, "maxItems": 10 }` |
| `pub mode: Mode` where `Mode` is an enum | `#[serde(rename_all = "lowercase")]` | `"enum": ["a", "b", "c"]` |
| `pub mode: Mode` with `#[serde(rename = "stream-json")]` | rename | `"enum": ["stream-json", ...]` |
| `pub nested: Nested` | (auto-recursive) | `{ "$ref": "#/definitions/Nested" }` |

**Per-field `description`** (the LLM's instruction manual for that param):
```rust
#[schemars(description = "City name to get weather for, e.g., 'London' or 'Paris, FR'")]
pub city: String,
```

**Per-tool `description`** (the LLM's instruction manual for the whole tool):
```rust
#[tool(description = "Get current weather for a city. Use when the user asks about temperature, rain, or forecast.")]
async fn get_weather(&self, Parameters(p): Parameters<WeatherParams>) -> Result<String, String> { ... }
```

---

## §5. Enum and rename idioms

```rust
#[derive(Debug, Serialize, Deserialize, JsonSchema)]
#[serde(rename_all = "lowercase")]
pub enum EffortLevel {
    Low,
    Medium,
    High,
    Xhigh,
    Max,
}
// → "enum": ["low", "medium", "high", "xhigh", "max"]

#[derive(Debug, Serialize, Deserialize, JsonSchema)]
#[serde(rename_all = "camelCase")]
pub enum PermissionMode {
    AcceptEdits,
    Auto,
    BypassPermissions,
    Default,
    DontAsk,
    Plan,
}
// → "enum": ["acceptEdits", "auto", "bypassPermissions", "default", "dontAsk", "plan"]

// Hyphenated variants: use rename
#[derive(Debug, Serialize, Deserialize, JsonSchema)]
pub enum OutputFormat {
    Text,
    Json,
    #[serde(rename = "stream-json")]
    StreamJson,
}
// → "enum": ["text", "json", "stream-json"]
```

**Always provide a discriminator string for action enums** so the LLM can pick the right one:
```rust
#[derive(Debug, Serialize, Deserialize, JsonSchema)]
#[serde(rename_all = "lowercase")]
pub enum SessionAction {
    /// Resume an existing session
    Resume,
    /// Continue the most recent session in this directory
    Continue,
    /// Fork an existing session into a new one
    Fork,
    /// List all known sessions
    List,
}
```

---

## §6. Optional fields and serialization hygiene

**Use `#[serde(skip_serializing_if = "Option::is_none")]` to keep the output JSON clean:**
```rust
#[derive(Debug, Serialize, Deserialize, JsonSchema)]
pub struct MyParams {
    pub prompt: String,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub model: Option<String>,
    #[serde(default, skip_serializing_if = "Vec::is_empty")]
    #[schemars(length(max = 20))]
    pub allowed_tools: Vec<String>,
    #[serde(default)]
    pub debug: bool,
}
```

This produces output where `model` is absent (not `null`) when unset, and `allowed_tools` is absent (not `[]`) when empty. Cleaner output, smaller tokens.

**For `#[serde(default)]` without a value** — uses `Default::default()` for the type. Combine with `skip_serializing_if` when the default is "empty" (empty vec, None, false).

**For required-but-Option-typed fields** — use `#[serde(default)]` so missing JSON deserializes to `None`, but mark them in `description` as optional (don't put in `required`).

---

## §7. State management

If your tools share state (sessions, caches, connections), put it on the server struct behind `Arc<Mutex<...>>` or `Arc<RwLock<...>>`:

```rust
#[derive(Clone)]
pub struct MyServer {
    state: Arc<RwLock<MyState>>,
}

#[derive(Default)]
struct MyState {
    sessions: HashMap<SessionId, SessionData>,
}
```

**Rules:**
- The server struct must be `Clone` (cheap if all fields are `Arc`)
- Lock the mutex briefly; clone what you need; drop the lock
- For long-held state, consider actor patterns (a single tokio task owning the state, tools send commands to it)
- Don't store per-tool-call state on the server struct (stateless tools are simpler to reason about)

---

## §8. Server lifecycle

```
spawn server process
  ↓
initialize handshake
  → client sends protocolVersion + clientInfo + capabilities
  → server responds with protocolVersion + serverInfo + capabilities
  → client sends "initialized" notification
  ↓
MCP requests flow
  → tools/list
  → tools/call
  → resources/list, resources/read
  → prompts/list, prompts/get
  ↓
shutdown
  → stdio: client closes stdin
  → Streamable HTTP: client closes connection
```

**Initialization in rmcp:**
```rust
let service = server.serve(transport).await?;
// service.waiting() drives the request loop until shutdown
service.waiting().await?;
```

**Handling `notifications/initialized`:**
rmcp handles this for you when you use `serve()`. If you implement the lower-level `serve_with_ct` or build the service by hand, remember that `notifications/initialized` is a notification (no response expected).

**Tool list changes (`notifications/tools/list_changed`):**
If your tool set is dynamic, set `listChanged: true` in your capabilities and emit the notification when the set changes:
```rust
service.notify_tool_list_changed().await?;
```

---

## §9. Transport choice

**stdio (default for local tools):**
- One process per client
- No network config
- Fastest latency (microseconds)
- Logging must go to stderr (stdout is the protocol)
- The most common pattern for IDEs and CLI wrappers

```rust
use rmcp::transport::stdio;
let transport = stdio();
let service = server.serve(transport).await?;
```

**Streamable HTTP (remote / multi-client):**
- One process serves many clients
- HTTPS + auth in production
- 10-50ms latency (network overhead)
- Origin header validation required (DNS rebinding protection)
- Mcp-Session-Id header for stateful sessions

```rust
use rmcp::transport::streamable_http_server::tower::StreamableHttpService;
use tower::ServiceBuilder;

let service = StreamableHttpService::new(
    || Ok(MyServer::new()),
    Default::default(),
);
let router = axum::Router::new().nest_service("/mcp", service);
// bind to 0.0.0.0:3000 with TLS termination in production
```

**HTTP+SSE (legacy, only for 2024-11-05 clients):**
- Two endpoints: `/sse` (server stream) and `/messages` (client POST)
- Deprecated in 2025-03-26 spec
- New servers should NOT use this; legacy clients may still expect it

**Decision matrix:**

| Need | Use |
|---|---|
| Local CLI / IDE plugin / single-user | **stdio** |
| Hosted SaaS / multi-tenant | **Streamable HTTP** |
| Need to support 2024-11-05 clients | **HTTP+SSE** alongside Streamable HTTP |
| Need both local and remote | Expose both transports via a flag (one binary, two modes) |

---

## §10. Stderr-only logging

**Critical rule for stdio servers:** anything written to stdout corrupts the JSON-RPC stream and the client disconnects. ALL logs go to stderr.

```rust
use tracing_subscriber::{fmt, prelude::*, EnvFilter};
use tracing;

tracing_subscriber::fmt()
    .with_writer(std::io::stderr)  // ← critical
    .with_env_filter(
        EnvFilter::try_from_default_env()
            .unwrap_or_else(|_| EnvFilter::new("info"))
    )
    .init();

// Usage
tracing::info!("server starting on stdio");
tracing::debug!("got request: {:?}", request);
tracing::error!(?error, "tool call failed");
```

For Streamable HTTP servers, stdout logging is fine (it's not a protocol channel). But stay consistent — use stderr for everything, no matter the transport.

**Common bug:** `println!("debugging: {:?}", state)` in a stdio server. The client silently disconnects. Always use `tracing` or `eprintln!`.

---

## §11. Error mapping

```rust
use rmcp::ErrorData as McpError;

// Wrap domain errors in McpError so they become JSON-RPC error responses
fn map_domain_error(e: anyhow::Error) -> McpError {
    McpError::internal_error(
        "tool_execution_failed",
        Some(serde_json::json!({
            "message": e.to_string(),
            "backtrace": e.backtrace().map(|b| b.to_string()),
        }))
    )
}

// In a tool method
#[tool(description = "Read a file")]
async fn read_file(&self, Parameters(p): Parameters<ReadFileParams>) -> Result<String, McpError> {
    // Security: validate path
    if !is_path_allowed(&p.path) {
        return Err(McpError::invalid_request("access denied: path outside allowed directories", None));
    }
    let content = tokio::fs::read_to_string(&p.path)
        .await
        .map_err(|e| McpError::invalid_request(&format!("read failed: {e}"), None))?;
    Ok(content)
}
```

**MCP error constructors (from `rmcp::ErrorData`):**
- `McpError::invalid_request(msg, data)` → JSON-RPC `-32600`
- `McpError::invalid_params(msg, data)` → JSON-RPC `-32602` (most common for schema violations)
- `McpError::method_not_found(msg, data)` → JSON-RPC `-32601`
- `McpError::internal_error(msg, data)` → JSON-RPC `-32603` (use sparingly — only for true internal errors)
- Custom codes via `McpError::custom(code, msg, data)` for domain errors

**Map your domain error categories to error codes:**
- Validation failed → `-32602` (invalid params)
- Auth failed → custom `-32001`
- Rate limited → custom `-32002`
- Dependency unavailable → custom `-32003`
- Internal bug → `-32603` (with a clear message, since you'll debug from this)

---

## §12. Output construction

```rust
use rmcp::model::{CallToolResult, Content};

// Simple text output
Ok(CallToolResult::success(vec![Content::text("the result")]))

// JSON-serialized output
let data = serde_json::json!({ "status": "ok", "count": 42 });
Ok(CallToolResult::success(vec![Content::text(data.to_string())]))

// Multiple content items (text + image)
Ok(CallToolResult::success(vec![
    Content::text(format!("Weather in {city}: {temp}°C, {condition}")),
    Content::image(encoded_image_bytes, "image/png"),
]))

// Error output
Err(McpError::invalid_request("file not found", Some(json!({ "path": path }))))
```

**For long output**, truncate and return a handle:
```rust
const MAX_INLINE: usize = 50_000;
if content.len() > MAX_INLINE {
    let handle = self.store_blob(content).await;
    Ok(CallToolResult::success(vec![Content::text(format!(
        "[truncated, full output at resource://blobs/{handle}]"
    ))]))
} else {
    Ok(CallToolResult::success(vec![Content::text(content)]))
}
```

---

## §13. Testing

**Unit tests for tool logic (without the MCP layer):**
```rust
#[cfg(test)]
mod tests {
    use super::*;
    #[tokio::test]
    async fn test_add() {
        let server = MyServer::new();
        let result = server.add(Parameters(MyToolParams { a: 2, b: 3 })).await;
        assert_eq!(result, "5");
    }
}
```

**Integration test with the MCP Inspector (the official debug tool):**
```bash
# Build your server
cargo build --release

# Launch the inspector against it
npx @modelcontextprotocol/inspector ./target/release/my-mcp-server
```

The inspector:
- Connects via stdio (or HTTP if you set the URL)
- Lists your tools
- Lets you call each tool with arbitrary args
- Shows the JSON-RPC messages on the wire

**End-to-end test with a real client:**
Use a real MCP host (Claude Code, Cline, Continue) and try the user's actual workflows. This catches tool-selection accuracy problems that unit tests miss.

**Schema validation test:**
```rust
// Use the schemars-generated JSON Schema to validate arbitrary input
let schema = schemars::schema_for!(MyToolParams);
let result = jsonschema::validate(&schema, &json_input);
assert!(result.is_ok());
```

---

## §14. Building and shipping

```bash
# Build a release binary (always release for stdio servers — debug builds have slow startup)
cargo build --release

# Run locally for manual testing
./target/release/my-mcp-server

# Run with debug logging
RUST_LOG=my_mcp_server=debug,rmcp=info ./target/release/my-mcp-server
```

**Binary size optimization** (rmcp servers can be 4-10 MB):
```toml
# Cargo.toml
[profile.release]
strip = "symbols"
lto = "thin"
codegen-units = 1
opt-level = 3
```

**Cross-compilation for distribution** (for stdio servers you ship to users):
```bash
cargo install cross
cross build --release --target x86_64-unknown-linux-gnu
cross build --release --target x86_64-apple-darwin
cross build --release --target aarch64-apple-darwin
cross build --release --target x86_64-pc-windows-msvc
```

---

## §15. Handoff to other skills

- **Why this design works (tool decomposition, error codes, output contract)** → `mcp-server-design`
- **How to write a good JSON Schema (constraints, descriptions, `additionalProperties`)** → `mcp-tool-surface`
- **Worked example: `claude-cli-wrapper` 6-tool decomposition** → `claude-cli` skill
- **Client-side patterns (calling an MCP server from another agent)** → not yet implemented
- **Quality evaluation of an existing server** → planned `mcp-server-quality` skill

---

## §16. Anti-patterns

❌ **`println!()` in a stdio server** — corrupts the JSON-RPC stream, client disconnects
❌ **`eprintln!` without `tracing`** — works but loses structure, no log levels
❌ **Returning a Rust error type directly** — must wrap in `McpError` (or implement `IntoContents`)
❌ **Forgetting `Arc<Mutex<...>>` and getting borrow-checker errors** — the server struct must be `Clone`
❌ **Long-held locks inside async tools** — deadlock risk; clone what you need and drop the lock
❌ **Sync file I/O in async tools** — use `tokio::fs` not `std::fs`
❌ **Block on subprocess without timeout** — use `tokio::process::Command` with `.timeout()`
❌ **Emit `tools/list_changed` for tools that never change** — wastes notifications
❌ **Declare `sampling: {}` capability but never call `create_message`** — clients will send sampling requests you can't handle
❌ **Trust the client's tool-call args without re-validating** — server-side validation is mandatory
❌ **Use `rmcp` 0.1.x or older macro syntax in 0.16+ code** — APIs changed; `tool_box` → `tool_router`, `Parameters` wrapper required
❌ **Skip the `serde` derive on input structs** — rmcp needs both `Deserialize` (for incoming) and `Serialize` (for errors and responses)
❌ **Forgetting to set `protocol_version` in `ServerInfo`** — older protocol versions break with newer features
❌ **Build the binary in debug mode for distribution** — slow startup, large size, debug symbols in stdout sometimes

---

## §17. Key sources

- [1] rmcp Rust SDK — https://github.com/modelcontextprotocol/rust-sdk
- [2] rmcp docs.rs — https://docs.rs/rmcp/latest/rmcp/
- [3] Model Context Protocol specification — https://modelcontextprotocol.io/specification/2025-11-25
- [4] MCP Tools spec — https://modelcontextprotocol.io/specification/draft/server/tools
- [5] MCP Transports spec — https://modelcontextprotocol.io/specification/2025-03-26/basic/transports
- [6] SystemPrompt.io: Build an MCP Server in Rust with rmcp — https://systemprompt.io/guides/build-mcp-server-rust
- [7] HackMD: MCP in Rust: A Practical Guide — https://hackmd.io/@Hamze/SytKkZP01l
- [8] HackMD: A Coder's Guide to the Official Rust MCP Toolkit — https://hackmd.io/@Hamze/S1tlKZP0kx
- [9] mcpcat.io: Build MCP Servers in Rust — https://mcpcat.io/guides/building-mcp-server-rust/
- [10] schemars docs — https://docs.rs/schemars/
- [11] Worked example: `plugins/claude-cli-wrapper` in this marketplace
