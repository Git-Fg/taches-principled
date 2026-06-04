# claude-cli-wrapper

Optimal MCP wrapper for the Claude Code CLI. Exposes six tools
(`claude_execute`, `claude_session`, `claude_context`, `claude_review`,
`claude_agent`, `claude_config`) as both MCP stdio tools and skill-callable
scripts.

## Install

The plugin ships a `bin/claude-cli-wrapper` launcher script. On first
invocation, the launcher picks the right binary for your host:

1. **Prebuilt binary** matching `$(uname -sm)` (e.g. `darwin-arm64`)
2. **Cached build** at `target/release/claude-cli-wrapper`
3. **Builds from source** via `cargo build --release` — requires the
   Rust toolchain on PATH. One-time cost: ~2-3 minutes. Cached after.

Apple Silicon (arm64-darwin) hosts use a prebuilt checked into
`bin/claude-cli-wrapper.darwin-arm64`. All other supported hosts build
from source on first use.

## Source

The Rust source is in `crates/wrapper/`. Build manually with:

```bash
cargo build --release
```

The resulting binary at `target/release/claude-cli-wrapper` is what the
launcher uses after a manual build.

## Cross-platform status

| Host | Status |
|---|---|
| darwin-arm64 (Apple Silicon) | Prebuilt shipped; no build needed |
| darwin-x86_64 (Intel Mac) | Builds from source on first use |
| linux-x86_64 | Builds from source on first use |
| linux-aarch64 | Builds from source on first use |
| windows-* | Not yet supported (toolchain assumes Unix shells in scripts) |

Adding prebuilts for additional platforms is on the roadmap; see
[the binary-arch CI guardrail issue](#) (TODO: file as follow-up).

## License

MIT. See `Cargo.toml`.
