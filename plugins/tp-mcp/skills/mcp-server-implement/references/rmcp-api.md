# rmcp API: Cargo.toml + Macros + Schemars

Reference for the Rust MCP server API surface. Covers the dependency setup, the macro cheat sheet for `#[tool]` / `#[tool_handler]` / `#[tool_router]`, the attribute mapping from `schemars` derive attributes to JSON Schema fields, and the enum/rename idioms that come up when designing tool inputs.

This is the load-bearing reference for §3 (macros) and §4 (attribute mapping) of the parent skill. Read it before writing tool input structs or wiring up the server struct.

## §1. Cargo.toml setup

```toml
[package]
name = "my-mcp-server"
version = "0.1.0"
edition = "2021"

[dependencies]
# rmcp 0.3 — feature names changed from the 0.16 era
rmcp = { version = "0.3", features = ["server", "macros", "transport-io", "schemars"] }
tokio = { version = "1", features = ["full"] }
serde = { version = "1", features = ["derive"] }
serde_json = "1"
schemars = "1.0"            # only needed if you DON'T enable rmcp's `schemars` re-export
anyhow = "1"
thiserror = "1"
tracing = "0.1"
tracing-subscriber = { version = "0.3", features = ["env-filter"] }
async-trait = "0.1"

# For Streamable HTTP transport (optional, only if not using stdio):
# rmcp = { version = "0.3", features = ["server", "macros", "transport-streamable-http-server"] }
# axum = "0.7"
# tower = "0.5"
```

**Feature flags (rmcp 0.3):**
- `server` — core server-side types and `ServerHandler` trait
- `macros` — `#[tool]`, `#[tool_handler]`, `#[tool_router]`, `#[prompt]`
- `transport-io` — stdio transport
- `transport-streamable-http-server` — Streamable HTTP transport (remote / multi-client)
- `transport-sse-server` — legacy HTTP+SSE (only if you must support 2024-11-05 clients)
- `schemars` — re-exports `schemars` so you can `use rmcp::schemars::JsonSchema;` and avoid adding `schemars` as a direct dep
- `client` — only if you're also building a client in the same crate

> **Version drift warning:** the rmcp API has broken between 0.1, 0.2, 0.3, and 0.16+ releases.
> The examples in this skill are validated against the version that ships in
> the `claude-cli-wrapper` plugin in this marketplace (rmcp 0.3.2). If you pin a different minor, expect
> macro and import differences.

## §2. The macro cheat sheet

```rust
use rmcp::{
    ServerHandler, ServiceExt,
    handler::server::tool::Parameters,
    model::{Implementation, ServerCapabilities, ServerInfo},
    tool, tool_handler, tool_router,
    transport::stdio,
};
use rmcp::schemars::JsonSchema;   // re-exported when you enable the `schemars` feature
use serde::{Deserialize, Serialize};

// 1. Server struct — must own a `ToolRouter<Self>` for the macros to work
#[derive(Clone)]
pub struct MyServer {
    tool_router: rmcp::handler::server::router::tool::ToolRouter<Self>,
    state: MyState,
}

// 2. Tool input struct (auto-generates the JSON Schema)
#[derive(Debug, Deserialize, Serialize, JsonSchema)]
#[serde(deny_unknown_fields, default)]
pub struct MyToolParams {
    #[schemars(description = "First number to add")]
    pub a: i32,
    #[schemars(description = "Second number to add")]
    pub b: i32,
}

// 3. Tool methods on a `#[tool_router]` impl block
#[tool_router]
impl MyServer {
    // Constructor is just a regular method (the `Self::tool_router()` call
    // wires up the `#[tool]`-annotated methods declared on this impl).
    fn new(state: MyState) -> Self {
        Self {
            tool_router: Self::tool_router(),
            state,
        }
    }

    // Sync tool: return type goes straight into CallToolResult
    #[tool(description = "Add two numbers")]
    fn add(&self, Parameters(MyToolParams { a, b }): Parameters<MyToolParams>)
        -> Result<rmcp::model::CallToolResult, rmcp::ErrorData>
    {
        Ok(rmcp::model::CallToolResult::success(vec![
            rmcp::model::Content::text((a + b).to_string())
        ]))
    }

    // Async tool: just make the function async
    #[tool(description = "Fetch a URL")]
    async fn fetch(&self, Parameters(p): Parameters<FetchParams>)
        -> Result<rmcp::model::CallToolResult, rmcp::ErrorData>
    {
        // ...
    }
}

// 4. ServerHandler impl — `#[tool_handler(router = self.tool_router)]` wires
//    up the #[tool] method dispatch. The `name` / `version` / `instructions`
//    fields live in the ServerInfo returned by get_info(), NOT as macro args.
#[tool_handler(router = self.tool_router)]
impl ServerHandler for MyServer {
    fn get_info(&self) -> ServerInfo {
        ServerInfo {
            server_info: Implementation {
                name: "my-mcp-server".into(),
                version: env!("CARGO_PKG_VERSION").into(),
            },
            capabilities: ServerCapabilities::default(),  // builder() also fine
            instructions: Some("A simple calculator".into()),
            ..Default::default()
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

    let server = MyServer::new(MyState::new());
    let service = server.serve(stdio()).await?;
    service.waiting().await?;
    Ok(())
}
```

**Key API shape (rmcp 0.3) — what the macros actually expect:**
- `#[tool_router]` impl **must** define a field `tool_router: ToolRouter<Self>` on the struct; the constructor calls `Self::tool_router()` to initialize it.
- `#[tool_handler(router = self.tool_router)]` is the only supported macro form. The older `#[tool_handler(name = "...", version = "...", instructions = "...")]` form **does not exist** in 0.3 — `name` / `version` / `instructions` belong in `ServerInfo`.
- `#[tool(description = "...")]` — the tool's `name` defaults to the method name (e.g. `add`); pass `name = "my_tool"` to override.
- Return type is `Result<CallToolResult, rmcp::ErrorData>` — the `McpError` alias and 3-arg `internal_error("code", data)` shape from older docs do not apply.

## §3. Attribute mapping (rmcp + schemars → JSON Schema)

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

## §4. Enum and rename idioms

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

## §5. Optional fields and serialization hygiene

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

## §6. State management

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
