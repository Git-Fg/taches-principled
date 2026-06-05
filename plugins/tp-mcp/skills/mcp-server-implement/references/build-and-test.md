# Testing and Shipping MCP Servers

Reference for the test pyramid and the build/distribution pipeline for an MCP server. Read it before declaring a server ready to ship.

## Testing

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

## Building and shipping

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
