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
#[schemars(extend("additionalProperties" = false))]
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
#[schemars(extend("additionalProperties" = false))]
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
#[schemars(extend("additionalProperties" = false))]
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
#[schemars(extend("additionalProperties" = false))]
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
#[schemars(extend("additionalProperties" = false))]
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
#[schemars(extend("additionalProperties" = false))]
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

// -----------------------------------------------------------------------------
// Output envelope
// -----------------------------------------------------------------------------
//
// The six tools return a JSON envelope of this shape. The MCP 2025-11-25 spec
// adds an `outputSchema` field to `Tool` and `structuredContent` to
// `CallToolResult` so the model can read the result shape a priori. The
// rmcp 0.3.2 release predates those fields, so the envelope is currently
// delivered as a JSON-encoded `text` content item and the schema is
// declared here for documentation + future upgrade:
//
//     #[schemars(extend("$ref" = "#/definitions/WrapperResultEnvelope"))]
//     output_schema = schemars::schema_for!(WrapperResultEnvelope),
//
// When rmcp 0.4+ lands `Tool::output_schema` support, this struct becomes
// the single source of truth for both the runtime payload and the schema
// the model sees.
#[derive(Debug, Clone, Serialize, Deserialize, JsonSchema)]
#[schemars(extend("additionalProperties" = false))]
#[allow(dead_code)] // schema-only; instantiated once rmcp adds output_schema support
pub struct WrapperResultEnvelope {
    /// Exit code of the underlying `claude` CLI invocation. `0` means the
    /// CLI succeeded; non-zero means the CLI itself returned an error
    /// (which surfaces as `is_error: true` in the CallToolResult, not as
    /// a transport-level `Err`).
    pub exit_code: i32,

    /// Captured stdout from the CLI. For `--output-format json` runs this
    /// is the JSON payload the CLI printed; for `text` runs it's the raw
    /// text output.
    pub stdout: String,

    /// Captured stderr from the CLI. Diagnostic and warning messages only
    /// — the wrapper itself logs to stderr via `tracing` outside the
    /// captured-stderr buffer.
    pub stderr: String,

    /// For JSON-output runs, the parsed JSON object. `None` for text runs
    /// or when the CLI returned non-JSON output.
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub output_parsed: Option<serde_json::Value>,

    /// Convenience: if `output_parsed.session_id` exists, lifted to a
    /// top-level field so callers don't have to dig into the parsed JSON
    /// to continue a session.
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub session_id: Option<String>,
}
