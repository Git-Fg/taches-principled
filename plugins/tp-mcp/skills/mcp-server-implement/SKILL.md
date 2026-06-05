---
name: mcp-server-implement
description: Build an MCP server in Rust — tool attributes, server lifecycle (initialize → capabilities → shutdown), transport choice (stdio vs Streamable HTTP), stderr-only logging, error mapping, and testing with the MCP Inspector in CLI mode (no browser). Use when the user says "implement an MCP server in Rust", "build an MCP tool", "Rust MCP server", "transport choice stdio vs HTTP", "MCP server lifecycle".
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

## CONTRAST

- NOT for: designing an MCP server's tool decomposition or output contract — use mcp-server-design
- NOT for: writing the JSON Schema for a single tool — use mcp-tool-surface
- NOT for: MCP server implementation in Python / TypeScript / Go — use the SDK-specific docs
- This skill covers Rust implementation (rmcp + schemars + tokio) only; the design and schema layers are separate skills
- "Build an MCP client" → not covered (no client skill yet)

## §2. Reference index

The mechanism content lives in references/. Read the right one before implementing the corresponding phase. The hub itself is a router — it tells you which reference to load, not how to implement.

You MUST read `references/rmcp-api.md` BEFORE writing the `Cargo.toml`, the server struct, or any `#[tool]`-annotated methods. It teaches the rmcp 0.3 feature flags, the macro cheat sheet for `#[tool]` / `#[tool_handler]` / `#[tool_router]`, the attribute mapping from `schemars` derive attributes to JSON Schema fields, the enum and rename idioms, the optional-field serialization hygiene, and the state management rules. Do not proceed without reading it.

You MUST read `references/lifecycle-and-transport.md` BEFORE choosing a transport or wiring up initialization. It teaches the MCP server lifecycle (spawn → initialize → requests → shutdown), the stdio vs Streamable HTTP vs HTTP+SSE trade-offs, the decision matrix, and the `notify_tool_list_changed` pattern for dynamic tool sets. Do not proceed without reading it.

You MUST read `references/runtime-contracts.md` BEFORE writing any tool that logs, surfaces errors, or returns structured output. It teaches the stderr-only logging rule (stdout corrupts the JSON-RPC stream), the `rmcp::ErrorData` constructors and the error-code → category mapping, the output construction idioms for text/JSON/multi-content, and the long-output truncation pattern. Do not proceed without reading it.

You MUST read `references/build-and-test.md` BEFORE shipping the server. It teaches the test pyramid (unit / integration with the MCP Inspector in CLI mode (no browser) / end-to-end with a real client / schema validation), the release build optimization, and the cross-compilation matrix for distribution. Do not proceed without reading it.

## §3. Handoff to other skills

- **Why this design works (tool decomposition, error codes, output contract)** → `mcp-server-design`
- **How to write a good JSON Schema (constraints, descriptions, `additionalProperties`)** → `mcp-tool-surface`
- **Worked example: `claude-cli-wrapper` 6-tool decomposition** → `claude-cli` skill
- **Client-side patterns (calling an MCP server from another agent)** → not yet implemented
- **Quality evaluation of an existing server** → planned `mcp-server-quality` skill

## §4. Anti-patterns

❌ **`println!()` in a stdio server** — corrupts the JSON-RPC stream, client disconnects
❌ **`eprintln!` without `tracing`** — works but loses structure, no log levels
❌ **Returning a Rust error type directly** — must wrap in `rmcp::ErrorData` (or implement `IntoContents`)
❌ **Forgetting `Arc<Mutex<...>>` and getting borrow-checker errors** — the server struct must be `Clone`
❌ **Long-held locks inside async tools** — deadlock risk; clone what you need and drop the lock
❌ **Sync file I/O in async tools** — use `tokio::fs` not `std::fs`
❌ **Block on subprocess without timeout** — use `tokio::process::Command` with `.timeout()`
❌ **Emit `tools/list_changed` for tools that never change** — wastes notifications
❌ **Declare `sampling: {}` capability but never call `create_message`** — clients will send sampling requests you can't handle
❌ **Trust the client's tool-call args without re-validating** — server-side validation is mandatory
❌ **Use the 0.1.x `tool_box` macro or the 0.16 `tool_handler(name=…, version=…)` form in 0.3+ code** — APIs changed; rmcp 0.3 expects `#[tool_handler(router = self.tool_router)]` and the `name` / `version` / `instructions` live in `ServerInfo`
❌ **Skip the `serde` derive on input structs** — rmcp needs both `Deserialize` (for incoming) and `Serialize` (for errors and responses)
❌ **Call `ErrorData::internal_error("code", Some(data))` with a domain "code" string as the first arg** — the first arg is the human-readable `message`, not a code. Use `ErrorData::custom(code, msg, data)` if you need a non-standard code
❌ **Build the binary in debug mode for distribution** — slow startup, large size, debug symbols in stdout sometimes

## §5. Key sources

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
- [11] Worked example: the `claude-cli` skill in this marketplace's `claude-cli-wrapper` plugin
