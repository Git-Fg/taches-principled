//! `claude-cli-wrapper` — optimal MCP wrapper for the Claude Code CLI.
//!
//! # Dual-surface contract
//!
//! This binary serves the same six tool handlers through two transports:
//!
//! 1. **MCP stdio transport** (the default; what `claude mcp serve`-style clients
//!    connect to). Discovered via `.mcp.json` in the plugin root.
//! 2. **Skill-side script invocation** (e.g.
//!    `claude-cli-wrapper mcp-tool claude_execute --prompt "..."`).
//!    Spoke skills call into the same handlers via this path so a missing MCP
//!    transport does not break the skill surface.
//!
//! Both surfaces share the same tool implementations in [`tools`], the same
//! JSON-schema definitions in [`schema`], and the same `claude -p ...` shell-out
//! in [`claude_cli`]. Drift between the two surfaces is impossible because
//! there is only one implementation.

#![deny(unsafe_code)]
#![warn(missing_docs)]

mod claude_cli;
mod error;
mod schema;
mod script;
mod server;
mod tools;

#[cfg(test)]
mod smoke_test;

use clap::{Parser, Subcommand};
use std::path::PathBuf;

/// The `claude-cli-wrapper` CLI.
///
/// When invoked with no subcommand, the binary starts an MCP stdio server
/// (the default surface for `.mcp.json` discovery).
///
/// When invoked with the `mcp-tool` subcommand, the binary runs a single
/// handler in script mode and exits — this is the surface that spoke skills
/// call from a `Bash` tool invocation.
#[derive(Debug, Parser)]
#[command(name = "claude-cli-wrapper", version, about, long_about = None)]
struct Cli {
    /// Path to the `claude` binary. Defaults to whatever `which claude`
    /// returns, or `CLAUDE_CLI_PATH` if set.
    #[arg(long, env = "CLAUDE_CLI_PATH", global = true)]
    claude_path: Option<PathBuf>,

    /// Subcommand. Omit to start the MCP stdio server.
    #[command(subcommand)]
    command: Option<Command>,
}

#[derive(Debug, Subcommand)]
enum Command {
    /// Invoke one of the six tool handlers in script mode. Used by spoke
    /// skills that want to call a wrapper tool without going through the MCP
    /// transport (e.g. when the MCP server is not running, or to avoid
    /// JSON-RPC framing cost on single-shot skill invocations).
    ///
    /// Arguments after the tool name are forwarded as JSON; the tool's
    /// `inputSchema` is enforced. Output is the same `CallToolResult` shape
    /// the MCP surface returns, written to stdout.
    McpTool {
        /// Tool name (`claude_execute`, `claude_session`, `claude_context`,
        /// `claude_review`, `claude_agent`, `claude_config`).
        tool: String,

        /// JSON object matching the tool's `inputSchema`. Pass `-` to read
        /// from stdin.
        args: Option<String>,
    },
}

#[tokio::main]
async fn main() -> anyhow::Result<()> {
    init_tracing();

    let cli = Cli::parse();

    match cli.command {
        // Default: MCP stdio server. This is the surface `.mcp.json` connects to.
        None => server::run_stdio(cli.claude_path).await,

        // Script mode: a single tool invocation. Spoke skills call this.
        Some(Command::McpTool { tool, args }) => {
            script::run_tool(cli.claude_path, &tool, args.as_deref()).await
        }
    }
}

/// Initialize tracing to stderr (stdout is reserved for the MCP stdio
/// transport — anything written to stdout corrupts the JSON-RPC stream).
fn init_tracing() {
    use tracing_subscriber::{EnvFilter, fmt};
    let filter = EnvFilter::try_from_env("CLAUDE_WRAPPER_LOG")
        .unwrap_or_else(|_| EnvFilter::new("info"));
    fmt()
        .with_env_filter(filter)
        .with_writer(std::io::stderr)
        .with_target(false)
        .init();
}
