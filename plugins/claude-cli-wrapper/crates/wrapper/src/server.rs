//! MCP stdio server.

use crate::claude_cli;
use crate::tools;
use anyhow::Result;
use rmcp::{
    ServerHandler, ServiceExt,
    handler::server::tool::Parameters,
    model::{Implementation, ServerCapabilities, ServerInfo},
    tool, tool_handler, tool_router,
    transport::stdio,
};
use std::future::Future;
use std::path::PathBuf;
use std::sync::Arc;

use crate::schema::{
    AgentInput, ConfigInput, ContextInput, ExecuteInput, ReviewInput, SessionInput,
};

/// Run the MCP stdio server.
pub async fn run_stdio(claude_path: Option<PathBuf>) -> Result<()> {
    let claude_path = claude_cli::resolve_claude_path(claude_path)?;

    tracing::info!(
        claude_path = %claude_path.display(),
        "claude-cli-wrapper MCP server starting on stdio"
    );

    let server = WrapperServer::new(claude_path);
    let service = server.serve(stdio()).await?;
    service.waiting().await?;
    Ok(())
}

#[derive(Clone)]
pub struct WrapperServer {
    tool_router: rmcp::handler::server::router::tool::ToolRouter<Self>,
    claude_path: Arc<PathBuf>,
}

#[tool_router]
impl WrapperServer {
    fn new(claude_path: PathBuf) -> Self {
        Self {
            tool_router: Self::tool_router(),
            claude_path: Arc::new(claude_path),
        }
    }

    #[tool(
        name = "claude_execute",
        description = "Run a prompt through `claude -p`. Returns a JSON envelope of shape `WrapperResultEnvelope` (fields: exit_code, stdout, stderr, output_parsed, session_id). Use this tool when the user wants Claude to do something: write code, run a command, analyze a file, etc. Pass `session_id` to continue a previous run; pass `continue_session: true` to continue the most recent session in the current directory. Non-zero CLI exits surface as JSON-RPC -32001 with the same envelope in the `data` field.",
        annotations(
            title = "Run a Claude prompt",
            read_only_hint = false,
            destructive_hint = true,
            idempotent_hint = false,
            open_world_hint = true,
        )
    )]
    async fn claude_execute(
        &self,
        params: Parameters<ExecuteInput>,
    ) -> Result<rmcp::model::CallToolResult, rmcp::ErrorData> {
        let result = tools::execute(&self.claude_path, params.0).await?;
        Ok(into_call_tool_result(result))
    }

    #[tool(
        name = "claude_session",
        description = "Session lifecycle: resume/continue/fork/list/info/close a session by `session_id`. The `session_id` returned by `claude_execute` is the input. `list` and `info` take no session_id; `resume`, `info`, `close` require it. Returns a `WrapperResultEnvelope` envelope (exit_code, stdout, stderr, output_parsed).",
        annotations(
            title = "Manage a Claude session",
            read_only_hint = false,
            destructive_hint = true,
            idempotent_hint = false,
            open_world_hint = false,
        )
    )]
    async fn claude_session(
        &self,
        params: Parameters<SessionInput>,
    ) -> Result<rmcp::model::CallToolResult, rmcp::ErrorData> {
        let result = tools::session(&self.claude_path, params.0).await?;
        Ok(into_call_tool_result(result))
    }

    #[tool(
        name = "claude_context",
        description = "Workspace context: add_directory (--add-dir), setup_worktree (--worktree), doctor. Use to grant Claude access to a directory it does not already see, or to spin up an isolated worktree. Returns a `WrapperResultEnvelope`.",
        annotations(
            title = "Adjust session context",
            read_only_hint = false,
            destructive_hint = true,
            idempotent_hint = false,
            open_world_hint = false,
        )
    )]
    async fn claude_context(
        &self,
        params: Parameters<ContextInput>,
    ) -> Result<rmcp::model::CallToolResult, rmcp::ErrorData> {
        let result = tools::context(&self.claude_path, params.0).await?;
        Ok(into_call_tool_result(result))
    }

    #[tool(
        name = "claude_review",
        description = "Code review pass against a target (current branch, branch name, or PR URL). Returns findings with file:line references. Read-only — does not modify files. Use when the user asks for a review. Returns a `WrapperResultEnvelope` (output_parsed is the review's structured findings).",
        annotations(
            title = "Code review pass",
            read_only_hint = true,
            destructive_hint = false,
            idempotent_hint = true,
            open_world_hint = false,
        )
    )]
    async fn claude_review(
        &self,
        params: Parameters<ReviewInput>,
    ) -> Result<rmcp::model::CallToolResult, rmcp::ErrorData> {
        let result = tools::review(&self.claude_path, params.0).await?;
        Ok(into_call_tool_result(result))
    }

    #[tool(
        name = "claude_agent",
        description = "Background agent management. `spawn` requires name+description+prompt; `status` and `terminate` require name; `list` requires nothing. Spawned agents run with bypass-permissions and bare mode (no auto-memory, no hooks). Returns a `WrapperResultEnvelope`.",
        annotations(
            title = "Spawn or manage a background agent",
            read_only_hint = false,
            destructive_hint = true,
            idempotent_hint = false,
            open_world_hint = true,
        )
    )]
    async fn claude_agent(
        &self,
        params: Parameters<AgentInput>,
    ) -> Result<rmcp::model::CallToolResult, rmcp::ErrorData> {
        let result = tools::agent(&self.claude_path, params.0).await?;
        Ok(into_call_tool_result(result))
    }

    #[tool(
        name = "claude_config",
        description = "Runtime config: set_model / set_effort / set_permissions / load_settings. Persists to the user-level settings file. Use to change the model or effort level for the next call, or to apply a settings.json from disk. Returns a `WrapperResultEnvelope`.",
        annotations(
            title = "Persist runtime config",
            read_only_hint = false,
            destructive_hint = true,
            idempotent_hint = false,
            open_world_hint = false,
        )
    )]
    async fn claude_config(
        &self,
        params: Parameters<ConfigInput>,
    ) -> Result<rmcp::model::CallToolResult, rmcp::ErrorData> {
        let result = tools::config(&self.claude_path, params.0).await?;
        Ok(into_call_tool_result(result))
    }
}

#[tool_handler(router = self.tool_router)]
impl ServerHandler for WrapperServer {
    fn get_info(&self) -> ServerInfo {
        ServerInfo {
            server_info: Implementation {
                name: "taches-claude-cli-wrapper".into(),
                version: env!("CARGO_PKG_VERSION").into(),
            },
            capabilities: ServerCapabilities::default(),
            instructions: Some(WRAPPER_INSTRUCTIONS.into()),
            ..Default::default()
        }
    }
}

const WRAPPER_INSTRUCTIONS: &str = r#"
`taches-claude-cli-wrapper` is the optimal wrapper around the `claude` CLI.
Use these six tools when an agent or skill needs to drive Claude Code
programmatically:

- `claude_execute` — run a prompt via `claude -p` and get structured output.
  Use for any "have Claude do X" request.
- `claude_session` — resume, continue, fork, list, info, or close a
  previously-created session. The `session_id` returned by `claude_execute`
  is the input.
- `claude_context` — add directories to a session's allowed scope, set up
  a git worktree, or run `claude doctor`.
- `claude_review` — code review pass against a branch or PR.
- `claude_agent` — spawn, list, status, or terminate a background agent.
- `claude_config` — persist runtime settings (model, effort, permission
  mode, settings file).

When the wrapper's six tools are available, prefer them over raw shell
invocations of `claude` — the wrapper validates input, captures exit codes,
parses output, and returns typed results.

Pass `session_id` to continue a previous run. Pass `continue_session: true`
to continue the most recent session in the current directory.
"#;

fn into_call_tool_result(result: tools::ToolResult) -> rmcp::model::CallToolResult {
    use rmcp::model::Content;
    let content = result
        .content
        .into_iter()
        .map(|c| match c {
            tools::ToolContent::Text { text } => Content::text(text),
        })
        .collect();
    rmcp::model::CallToolResult {
        content,
        is_error: Some(result.is_error),
    }
}
