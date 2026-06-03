//! Script-mode invocation.

use crate::claude_cli;
use crate::schema::{
    AgentInput, ConfigInput, ContextInput, ExecuteInput, ReviewInput, SessionInput,
};
use crate::tools;
use anyhow::{Context, Result};
use std::path::PathBuf;

/// Run a single tool in script mode.
pub async fn run_tool(
    claude_path: Option<PathBuf>,
    tool: &str,
    args: Option<&str>,
) -> Result<()> {
    let claude_path = claude_cli::resolve_claude_path(claude_path)?;
    let json = match args {
        Some("-") | None => {
            let mut buf = String::new();
            std::io::Read::read_to_string(&mut std::io::stdin(), &mut buf)
                .context("reading args from stdin")?;
            buf
        }
        Some(s) => s.to_string(),
    };

    let value: serde_json::Value = serde_json::from_str(&json)
        .with_context(|| format!("parsing args as JSON: {json}"))?;

    let result = match tool {
        "claude_execute" => {
            let input: ExecuteInput = serde_json::from_value(value)?;
            tools::execute(&claude_path, input).await?
        }
        "claude_session" => {
            let input: SessionInput = serde_json::from_value(value)?;
            tools::session(&claude_path, input).await?
        }
        "claude_context" => {
            let input: ContextInput = serde_json::from_value(value)?;
            tools::context(&claude_path, input).await?
        }
        "claude_review" => {
            let input: ReviewInput = serde_json::from_value(value)?;
            tools::review(&claude_path, input).await?
        }
        "claude_agent" => {
            let input: AgentInput = serde_json::from_value(value)?;
            tools::agent(&claude_path, input).await?
        }
        "claude_config" => {
            let input: ConfigInput = serde_json::from_value(value)?;
            tools::config(&claude_path, input).await?
        }
        other => {
            anyhow::bail!(
                "unknown tool: {other}. Valid: claude_execute, claude_session, \
                 claude_context, claude_review, claude_agent, claude_config."
            );
        }
    };

    let serialized = serde_json::to_string_pretty(&result)?;
    println!("{serialized}");

    if result.is_error {
        std::process::exit(1);
    }
    Ok(())
}
