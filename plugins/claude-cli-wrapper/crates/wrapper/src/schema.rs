//! Tool input/output schemas. Uses `rmcp::schemars::JsonSchema` so the
//! `#[tool]` macro picks up the schema for MCP `inputSchema` generation.

use rmcp::schemars::JsonSchema;
use serde::{Deserialize, Serialize};

// -----------------------------------------------------------------------------
// Enums
// -----------------------------------------------------------------------------

/// Execution mode for `claude -p` calls. `print` is the default for AI agents.
#[derive(Debug, Default, Clone, Copy, Serialize, Deserialize, JsonSchema)]
#[serde(rename_all = "lowercase")]
pub enum ExecutionMode {
    #[default]
    Print,
    Interactive,
}

/// Output serialization for `claude -p`.
#[derive(Debug, Default, Clone, Copy, Serialize, Deserialize, JsonSchema)]
#[serde(rename_all = "kebab-case")]
pub enum OutputFormat {
    Text,
    #[default]
    Json,
    StreamJson,
}

/// Reasoning effort level.
#[derive(Debug, Clone, Copy, Serialize, Deserialize, JsonSchema)]
#[serde(rename_all = "lowercase")]
pub enum EffortLevel {
    Low,
    Medium,
    High,
    Xhigh,
    Max,
}

/// Permission behavior for the session.
#[derive(Debug, Clone, Copy, Serialize, Deserialize, JsonSchema)]
#[serde(rename_all = "camelCase")]
pub enum PermissionMode {
    AcceptEdits,
    Auto,
    BypassPermissions,
    Default,
    DontAsk,
    Plan,
}

// -----------------------------------------------------------------------------
// `claude_execute`
// -----------------------------------------------------------------------------

#[derive(Debug, Clone, Serialize, Deserialize, JsonSchema, Default)]
#[serde(deny_unknown_fields, default)]
pub struct ExecuteInput {
    pub prompt: String,

    #[serde(default)]
    pub mode: ExecutionMode,

    #[serde(default)]
    pub output_format: OutputFormat,

    #[serde(default)]
    pub context_dirs: Vec<String>,

    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub model: Option<String>,

    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub effort: Option<EffortLevel>,

    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub max_budget_usd: Option<f64>,

    #[serde(default)]
    pub allowed_tools: Vec<String>,

    #[serde(default)]
    pub disallowed_tools: Vec<String>,

    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub system_prompt: Option<String>,

    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub append_system_prompt: Option<String>,

    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub session_id: Option<String>,

    #[serde(default)]
    pub continue_session: bool,

    #[serde(default)]
    pub fork_session: bool,

    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub settings_file: Option<String>,

    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub structured_output_schema_json: Option<String>,

    #[serde(default)]
    pub mcp_configs: Vec<String>,

    #[serde(default)]
    pub strict_mcp_config: bool,

    #[serde(default)]
    pub plugin_dirs: Vec<String>,

    #[serde(default)]
    pub bare_mode: bool,

    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub permission_mode: Option<PermissionMode>,

    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub name: Option<String>,
}

// -----------------------------------------------------------------------------
// `claude_session`
// -----------------------------------------------------------------------------

#[derive(Debug, Clone, Serialize, Deserialize, JsonSchema, Default)]
#[serde(deny_unknown_fields, default)]
pub struct SessionInput {
    pub action: SessionAction,

    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub session_id: Option<String>,

    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub session_name: Option<String>,

    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub search_term: Option<String>,
}

#[derive(Debug, Default, Clone, Copy, Serialize, Deserialize, JsonSchema)]
#[serde(rename_all = "lowercase")]
pub enum SessionAction {
    #[default]
    Resume,
    Continue,
    Fork,
    List,
    Info,
    Close,
}

// -----------------------------------------------------------------------------
// `claude_context`
// -----------------------------------------------------------------------------

#[derive(Debug, Clone, Serialize, Deserialize, JsonSchema, Default)]
#[serde(deny_unknown_fields, default)]
pub struct ContextInput {
    pub action: ContextAction,

    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub directory_path: Option<String>,

    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub worktree_name: Option<String>,
}

#[derive(Debug, Default, Clone, Copy, Serialize, Deserialize, JsonSchema)]
#[serde(rename_all = "snake_case")]
pub enum ContextAction {
    #[default]
    AddDirectory,
    SetupWorktree,
    Doctor,
}

// -----------------------------------------------------------------------------
// `claude_review`
// -----------------------------------------------------------------------------

#[derive(Debug, Clone, Serialize, Deserialize, JsonSchema, Default)]
#[serde(deny_unknown_fields, default)]
pub struct ReviewInput {
    pub target: String,

    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub base_branch: Option<String>,

    #[serde(default)]
    pub output_format: ReviewOutputFormat,
}

#[derive(Debug, Default, Clone, Copy, Serialize, Deserialize, JsonSchema)]
#[serde(rename_all = "lowercase")]
pub enum ReviewOutputFormat {
    Text,
    #[default]
    Json,
}

// -----------------------------------------------------------------------------
// `claude_agent`
// -----------------------------------------------------------------------------

#[derive(Debug, Clone, Serialize, Deserialize, JsonSchema, Default)]
#[serde(deny_unknown_fields, default)]
pub struct AgentInput {
    pub action: AgentAction,

    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub agent_name: Option<String>,

    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub agent_description: Option<String>,

    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub agent_prompt: Option<String>,
}

#[derive(Debug, Default, Clone, Copy, Serialize, Deserialize, JsonSchema)]
#[serde(rename_all = "lowercase")]
pub enum AgentAction {
    List,
    #[default]
    Spawn,
    Status,
    Terminate,
}

// -----------------------------------------------------------------------------
// `claude_config`
// -----------------------------------------------------------------------------

#[derive(Debug, Clone, Serialize, Deserialize, JsonSchema, Default)]
#[serde(deny_unknown_fields, default)]
pub struct ConfigInput {
    pub action: ConfigAction,

    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub model_value: Option<String>,

    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub effort_value: Option<EffortLevel>,

    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub permissions_value: Option<PermissionMode>,

    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub settings_path: Option<String>,
}

#[derive(Debug, Default, Clone, Copy, Serialize, Deserialize, JsonSchema)]
#[serde(rename_all = "snake_case")]
pub enum ConfigAction {
    #[default]
    SetModel,
    SetEffort,
    SetPermissions,
    LoadSettings,
}
