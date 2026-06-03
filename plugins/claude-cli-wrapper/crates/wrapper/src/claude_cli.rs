//! Shell-out to the `claude` CLI.

use anyhow::{Context, Result};
use std::path::PathBuf;
use std::process::Stdio;
use tokio::process::Command;

/// Locate the `claude` binary.
pub fn resolve_claude_path(explicit: Option<PathBuf>) -> Result<PathBuf> {
    if let Some(p) = explicit {
        return Ok(p);
    }

    if let Ok(output) = std::process::Command::new("which").arg("claude").output() {
        if output.status.success() {
            let path = String::from_utf8_lossy(&output.stdout).trim().to_string();
            if !path.is_empty() {
                return Ok(PathBuf::from(path));
            }
        }
    }

    for candidate in [
        "/usr/local/bin/claude",
        "/opt/homebrew/bin/claude",
        "/home/linuxbrew/.linuxbrew/bin/claude",
    ] {
        if std::path::Path::new(candidate).exists() {
            return Ok(PathBuf::from(candidate));
        }
    }

    anyhow::bail!(
        "claude binary not found. Set --claude-path or $CLAUDE_CLI_PATH, \
         or install Claude Code (https://docs.claude.com)."
    )
}

/// Build the `claude -p ...` argv for a `claude_execute` invocation.
pub fn build_execute_argv(
    claude_path: &PathBuf,
    json_args: &serde_json::Value,
) -> Result<Vec<String>> {
    let mut argv = vec![
        claude_path.to_string_lossy().to_string(),
        "-p".to_string(),
        "--output-format".to_string(),
        "json".to_string(),
    ];

    let prompt = json_args
        .get("prompt")
        .and_then(|v| v.as_str())
        .context("`prompt` is required and must be a string")?;
    argv.push(prompt.to_string());

    if let Some(model) = json_args.get("model").and_then(|v| v.as_str()) {
        argv.push("--model".to_string());
        argv.push(model.to_string());
    }
    if let Some(effort) = json_args.get("effort").and_then(|v| v.as_str()) {
        argv.push("--effort".to_string());
        argv.push(effort.to_string());
    }
    if let Some(budget) = json_args.get("max_budget_usd").and_then(|v| v.as_f64()) {
        argv.push("--max-budget-usd".to_string());
        argv.push(budget.to_string());
    }
    if let Some(perm) = json_args.get("permission_mode").and_then(|v| v.as_str()) {
        argv.push("--permission-mode".to_string());
        argv.push(perm.to_string());
    }
    if json_args
        .get("bare_mode")
        .and_then(|v| v.as_bool())
        .unwrap_or(false)
    {
        argv.push("--bare".to_string());
    }
    if let Some(session_id) = json_args.get("session_id").and_then(|v| v.as_str()) {
        argv.push("--session-id".to_string());
        argv.push(session_id.to_string());
    }
    if json_args
        .get("continue_session")
        .and_then(|v| v.as_bool())
        .unwrap_or(false)
    {
        argv.push("--continue".to_string());
    }
    if let Some(name) = json_args.get("name").and_then(|v| v.as_str()) {
        argv.push("--name".to_string());
        argv.push(name.to_string());
    }
    if let Some(schema) = json_args
        .get("structured_output_schema_json")
        .and_then(|v| v.as_str())
    {
        argv.push("--json-schema".to_string());
        argv.push(schema.to_string());
    }
    if let Some(settings) = json_args.get("settings_file").and_then(|v| v.as_str()) {
        argv.push("--settings".to_string());
        argv.push(settings.to_string());
    }
    if let Some(extra_dirs) = json_args.get("context_dirs").and_then(|v| v.as_array()) {
        for d in extra_dirs.iter().filter_map(|v| v.as_str()) {
            argv.push("--add-dir".to_string());
            argv.push(d.to_string());
        }
    }
    if let Some(allowed) = json_args.get("allowed_tools").and_then(|v| v.as_array()) {
        for tool in allowed.iter().filter_map(|v| v.as_str()) {
            argv.push("--allowedTools".to_string());
            argv.push(tool.to_string());
        }
    }
    if let Some(disallowed) = json_args.get("disallowed_tools").and_then(|v| v.as_array()) {
        for tool in disallowed.iter().filter_map(|v| v.as_str()) {
            argv.push("--disallowedTools".to_string());
            argv.push(tool.to_string());
        }
    }

    Ok(argv)
}

/// Execute `claude -p ...` and capture the result.
pub async fn invoke(argv: Vec<String>) -> Result<ClaudeInvocationResult> {
    let mut cmd = Command::new(&argv[0]);
    cmd.args(&argv[1..])
        .stdout(Stdio::piped())
        .stderr(Stdio::piped());

    let output = cmd.output().await.context("failed to spawn claude")?;

    let stdout = String::from_utf8_lossy(&output.stdout).to_string();
    let stderr = String::from_utf8_lossy(&output.stderr).to_string();
    let output_parsed = serde_json::from_str(&stdout).ok();

    Ok(ClaudeInvocationResult {
        exit_code: output.status.code().unwrap_or(-1),
        stdout,
        stderr,
        output_parsed,
    })
}

/// Result of a `claude -p ...` invocation.
#[derive(Debug, Clone)]
pub struct ClaudeInvocationResult {
    pub exit_code: i32,
    pub stdout: String,
    pub stderr: String,
    pub output_parsed: Option<serde_json::Value>,
}
