//! The six tool handlers, shared between MCP and script surfaces.

use crate::claude_cli;
use crate::schema::{
    AgentAction, AgentInput, ConfigAction, ConfigInput, ContextAction, ContextInput, ExecuteInput,
    ReviewInput, SessionAction, SessionInput,
};
use anyhow::Result;
use serde::Serialize;
use serde_json::{Value, json};

/// A tool result, shape-compatible with `rmcp::model::CallToolResult`.
#[derive(Debug, Clone, Serialize)]
pub struct ToolResult {
    pub content: Vec<ToolContent>,

    #[serde(rename = "isError", skip_serializing_if = "is_false")]
    pub is_error: bool,
}

#[derive(Debug, Clone, Serialize)]
#[serde(tag = "type", rename_all = "lowercase")]
pub enum ToolContent {
    Text {
        text: String,
    },
}

fn is_false(b: &bool) -> bool {
    !*b
}

impl ToolResult {
    pub fn ok(text: impl Into<String>) -> Self {
        Self {
            content: vec![ToolContent::Text { text: text.into() }],
            is_error: false,
        }
    }

    pub fn err(text: impl Into<String>) -> Self {
        Self {
            content: vec![ToolContent::Text { text: text.into() }],
            is_error: true,
        }
    }

    pub fn from_claude(result: &claude_cli::ClaudeInvocationResult) -> Self {
        let mut response = json!({
            "exit_code": result.exit_code,
            "stdout": result.stdout,
            "stderr": result.stderr,
        });

        if let Some(parsed) = &result.output_parsed {
            response["output_parsed"] = parsed.clone();
        }
        if let Some(id) = result
            .output_parsed
            .as_ref()
            .and_then(|p| p.get("session_id"))
            .and_then(|v| v.as_str())
        {
            response["session_id"] = Value::String(id.to_string());
        }

        if result.exit_code == 0 {
            Self::ok(response.to_string())
        } else {
            Self::err(response.to_string())
        }
    }
}

// -----------------------------------------------------------------------------
// `claude_execute`
// -----------------------------------------------------------------------------

pub async fn execute(claude_path: &std::path::PathBuf, input: ExecuteInput) -> Result<ToolResult> {
    let args_json = serde_json::to_value(&input)?;
    let argv = claude_cli::build_execute_argv(claude_path, &args_json)?;
    let result = claude_cli::invoke(argv).await?;
    Ok(ToolResult::from_claude(&result))
}

// -----------------------------------------------------------------------------
// `claude_session`
// -----------------------------------------------------------------------------

pub async fn session(claude_path: &std::path::PathBuf, input: SessionInput) -> Result<ToolResult> {
    let mut argv = vec![claude_path.to_string_lossy().to_string()];

    let needs_session_id = matches!(
        input.action,
        SessionAction::Resume | SessionAction::Info | SessionAction::Close
    );
    if needs_session_id && input.session_id.is_none() {
        anyhow::bail!("`session_id` is required for this action");
    }

    match input.action {
        SessionAction::Resume => argv.push("--resume".to_string()),
        SessionAction::Continue => argv.push("--continue".to_string()),
        SessionAction::Fork => argv.push("--fork-session".to_string()),
        SessionAction::List => argv.push("--list-sessions".to_string()),
        SessionAction::Info => argv.push("--session-info".to_string()),
        SessionAction::Close => argv.push("--close-session".to_string()),
    }
    if let Some(sid) = &input.session_id {
        argv.push(sid.clone());
    }
    if let Some(name) = &input.session_name {
        argv.push("--name".to_string());
        argv.push(name.clone());
    }
    if let Some(term) = &input.search_term {
        argv.push("--search".to_string());
        argv.push(term.clone());
    }
    argv.push("--output-format".to_string());
    argv.push("json".to_string());

    let result = claude_cli::invoke(argv).await?;
    Ok(ToolResult::from_claude(&result))
}

// -----------------------------------------------------------------------------
// `claude_context`
// -----------------------------------------------------------------------------

pub async fn context(claude_path: &std::path::PathBuf, input: ContextInput) -> Result<ToolResult> {
    let mut argv = vec![claude_path.to_string_lossy().to_string()];

    match input.action {
        ContextAction::AddDirectory => {
            let dir = input
                .directory_path
                .as_deref()
                .ok_or_else(|| anyhow::anyhow!("`directory_path` required for add_directory"))?;
            argv.push("--add-dir".to_string());
            argv.push(dir.to_string());
            argv.push("--output-format".to_string());
            argv.push("json".to_string());
        }
        ContextAction::SetupWorktree => {
            let name = input
                .worktree_name
                .as_deref()
                .ok_or_else(|| anyhow::anyhow!("`worktree_name` required for setup_worktree"))?;
            argv.push("--worktree".to_string());
            argv.push(name.to_string());
        }
        ContextAction::Doctor => {
            argv.push("doctor".to_string());
        }
    }

    let result = claude_cli::invoke(argv).await?;
    Ok(ToolResult::from_claude(&result))
}

// -----------------------------------------------------------------------------
// `claude_review`
// -----------------------------------------------------------------------------

pub async fn review(claude_path: &std::path::PathBuf, input: ReviewInput) -> Result<ToolResult> {
    let target_desc = match input.target.as_str() {
        "current" => "the current branch".to_string(),
        t if t.starts_with("http") => format!("the PR at {t}"),
        t => format!("the branch `{t}`"),
    };

    let base_clause = input
        .base_branch
        .as_deref()
        .map(|b| format!(" against base branch `{b}`"))
        .unwrap_or_default();

    let prompt = format!(
        "Perform a code review on {target_desc}{base_clause}. Identify correctness \
         bugs, security issues, logic errors, and test coverage gaps. Cite \
         specific files and line numbers."
    );

    let exec = ExecuteInput {
        prompt,
        mode: crate::schema::ExecutionMode::Print,
        output_format: match input.output_format {
            crate::schema::ReviewOutputFormat::Text => crate::schema::OutputFormat::Text,
            crate::schema::ReviewOutputFormat::Json => crate::schema::OutputFormat::Json,
        },
        context_dirs: vec![],
        model: None,
        effort: None,
        max_budget_usd: None,
        allowed_tools: vec!["Read".into(), "Grep".into(), "Glob".into(), "Bash".into()],
        disallowed_tools: vec![],
        system_prompt: Some(
            "You are a code review agent. Find bugs, security issues, and gaps. \
             Cite file:line. Do not make changes — only report findings."
                .into(),
        ),
        append_system_prompt: None,
        session_id: None,
        continue_session: false,
        fork_session: false,
        settings_file: None,
        structured_output_schema_json: None,
        mcp_configs: vec![],
        strict_mcp_config: false,
        plugin_dirs: vec![],
        bare_mode: false,
        permission_mode: Some(crate::schema::PermissionMode::AcceptEdits),
        name: Some("claude-review".into()),
    };

    execute(claude_path, exec).await
}

// -----------------------------------------------------------------------------
// `claude_agent`
// -----------------------------------------------------------------------------

pub async fn agent(claude_path: &std::path::PathBuf, input: AgentInput) -> Result<ToolResult> {
    let mut argv = vec![claude_path.to_string_lossy().to_string()];

    match input.action {
        AgentAction::List => {
            argv.push("--list-agents".to_string());
        }
        AgentAction::Status => {
            let name = input
                .agent_name
                .as_deref()
                .ok_or_else(|| anyhow::anyhow!("`agent_name` required for status"))?;
            argv.push("--agent-status".to_string());
            argv.push(name.to_string());
        }
        AgentAction::Terminate => {
            let name = input
                .agent_name
                .as_deref()
                .ok_or_else(|| anyhow::anyhow!("`agent_name` required for terminate"))?;
            argv.push("--kill-agent".to_string());
            argv.push(name.to_string());
        }
        AgentAction::Spawn => {
            let name = input
                .agent_name
                .as_deref()
                .ok_or_else(|| anyhow::anyhow!("`agent_name` required for spawn"))?;
            let description = input
                .agent_description
                .as_deref()
                .ok_or_else(|| anyhow::anyhow!("`agent_description` required for spawn"))?;
            let prompt = input
                .agent_prompt
                .as_deref()
                .ok_or_else(|| anyhow::anyhow!("`agent_prompt` required for spawn"))?;

            let exec = ExecuteInput {
                prompt: prompt.to_string(),
                mode: crate::schema::ExecutionMode::Print,
                output_format: crate::schema::OutputFormat::Json,
                context_dirs: vec![],
                model: None,
                effort: None,
                max_budget_usd: None,
                allowed_tools: vec!["default".into()],
                disallowed_tools: vec![],
                system_prompt: Some(prompt.to_string()),
                append_system_prompt: None,
                session_id: None,
                continue_session: false,
                fork_session: false,
                settings_file: None,
                structured_output_schema_json: None,
                mcp_configs: vec![],
                strict_mcp_config: false,
                plugin_dirs: vec![],
                bare_mode: true,
                permission_mode: Some(crate::schema::PermissionMode::BypassPermissions),
                name: Some(name.to_string()),
            };

            tracing::info!(name, description, "spawning agent");
            return execute(claude_path, exec).await;
        }
    }

    argv.push("--output-format".to_string());
    argv.push("json".to_string());
    let result = claude_cli::invoke(argv).await?;
    Ok(ToolResult::from_claude(&result))
}

// -----------------------------------------------------------------------------
// `claude_config`
// -----------------------------------------------------------------------------

pub async fn config(claude_path: &std::path::PathBuf, input: ConfigInput) -> Result<ToolResult> {
    let mut argv = vec![claude_path.to_string_lossy().to_string(), "-p".to_string()];

    let prompt = match input.action {
        ConfigAction::SetModel => {
            let model = input
                .model_value
                .as_deref()
                .ok_or_else(|| anyhow::anyhow!("`model_value` required for set_model"))?;
            format!("Persist model={model} to user settings via --settings.")
        }
        ConfigAction::SetEffort => {
            let effort = input
                .effort_value
                .ok_or_else(|| anyhow::anyhow!("`effort_value` required for set_effort"))?;
            format!("Persist effort={effort:?} to user settings via --settings.")
        }
        ConfigAction::SetPermissions => {
            let perm = input
                .permissions_value
                .ok_or_else(|| anyhow::anyhow!("`permissions_value` required for set_permissions"))?;
            format!("Persist permissions={perm:?} to user settings via --settings.")
        }
        ConfigAction::LoadSettings => {
            let path = input
                .settings_path
                .as_deref()
                .ok_or_else(|| anyhow::anyhow!("`settings_path` required for load_settings"))?;
            argv.push("--settings".to_string());
            argv.push(path.to_string());
            "Print the resolved active settings.".to_string()
        }
    };

    argv.push(prompt);
    argv.push("--output-format".to_string());
    argv.push("json".to_string());

    let result = claude_cli::invoke(argv).await?;
    Ok(ToolResult::from_claude(&result))
}
