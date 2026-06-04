//! Error types that map cleanly to MCP `ErrorData` JSON-RPC codes.
//!
//! Two error categories, two codes:
//!
//! - `CliNonzeroExit` → JSON-RPC `-32001` (custom code, domain-specific):
//!   the wrapper successfully invoked the `claude` CLI, but the CLI itself
//!   returned a non-zero exit. The full envelope (`exit_code`, `stdout`,
//!   `stderr`, `output_parsed`) is preserved in the error's `data` field
//!   so the caller can still inspect what happened.
//!
//! - `Internal` → JSON-RPC `-32603` (standard `internal_error`):
//!   the wrapper itself failed — binary not found, spawn failed, argv
//!   construction failed, serialization failed, etc. These are real bugs
//!   and should be debugged from the message.

use rmcp::model::{ErrorCode, ErrorData};

#[derive(Debug, thiserror::Error)]
pub enum WrapperError {
    #[error("claude CLI returned exit code {exit_code}: {stderr}")]
    CliNonzeroExit {
        exit_code: i32,
        stdout: String,
        stderr: String,
        output_parsed: Option<serde_json::Value>,
    },

    #[error(transparent)]
    Internal(#[from] anyhow::Error),
}

impl From<WrapperError> for ErrorData {
    fn from(e: WrapperError) -> Self {
        match e {
            WrapperError::CliNonzeroExit {
                exit_code,
                stdout,
                stderr,
                output_parsed,
            } => ErrorData::new(
                ErrorCode(-32001),
                format!("claude CLI returned exit code {exit_code}"),
                Some(serde_json::json!({
                    "exit_code": exit_code,
                    "stdout": stdout,
                    "stderr": stderr,
                    "output_parsed": output_parsed,
                })),
            ),
            WrapperError::Internal(e) => ErrorData::internal_error(e.to_string(), None),
        }
    }
}
