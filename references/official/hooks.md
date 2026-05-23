# Hooks Reference - Claude Code Official Documentation

Source: https://code.claude.com/docs/en/hooks

## Overview

Hooks are user-defined shell commands, HTTP endpoints, or LLM prompts that execute automatically at specific points in Claude Code's lifecycle.

## Hook Lifecycle Events

| Event | When it fires |
|---|---|
| `SessionStart` | When a session begins or resumes |
| `Setup` | When starting with `--init-only`, `--init`, or `--maintenance` in `-p` mode |
| `UserPromptSubmit` | When you submit a prompt, before Claude processes it |
| `UserPromptExpansion` | When a user-typed command expands into a prompt |
| `PreToolUse` | Before a tool call executes |
| `PermissionRequest` | When a permission dialog appears |
| `PermissionDenied` | When a tool call is denied by auto mode classifier |
| `PostToolUse` | After a tool call succeeds |
| `PostToolUseFailure` | After a tool call fails |
| `PostToolBatch` | After a full batch of parallel tool calls resolves |
| `Notification` | When Claude Code sends a notification |
| `SubagentStart` | When a subagent is spawned |
| `SubagentStop` | When a subagent finishes |
| `TaskCreated` | When a task is being created via TaskCreate |
| `TaskCompleted` | When a task is being marked as completed |
| `Stop` | When Claude finishes responding |
| `StopFailure` | When the turn ends due to an API error |
| `TeammateIdle` | When an agent team teammate is about to go idle |
| `InstructionsLoaded` | When CLAUDE.md or rules file is loaded |
| `ConfigChange` | When a configuration file changes |
| `CwdChanged` | When the working directory changes |
| `FileChanged` | When a watched file changes on disk |
| `WorktreeCreate` | When a worktree is being created |
| `WorktreeRemove` | When a worktree is being removed |
| `PreCompact` | Before context compaction |
| `PostCompact` | After context compaction completes |
| `Elicitation` | When an MCP server requests user input |
| `ElicitationResult` | After user responds to MCP elicitation |
| `SessionEnd` | When a session terminates |

## Hook Locations

| Location | Scope | Shareable |
|---|---|---|
| `~/.claude/settings.json` | All projects | No |
| `.claude/settings.json` | Single project | Yes |
| `.claude/settings.local.json` | Single project | No (gitignored) |
| Managed policy settings | Organization-wide | Yes |
| Plugin `hooks/hooks.json` | When plugin enabled | Yes |
| Skill or agent frontmatter | While component active | Yes |

## Matcher Patterns

| Matcher | Evaluated as |
|---|---|
| `*`, `""`, omitted | Match all |
| Letters, digits, `_`, `\|` only | Exact string or `\|`-separated list |
| Contains other characters | JavaScript regular expression |

### Per-Event Matcher Values

Some events have specific matcher values:
- **SessionStart**: `startup`, `resume`, `clear`, `compact`
- **StopFailure**: Error type strings (e.g., `rate_limit`, `api_error`, `timeout`)

## Common Input Fields

All hooks receive these fields in the JSON input:

| Field | Description |
|---|---|
| `session_id` | Unique session identifier |
| `transcript_path` | Path to session transcript file |
| `cwd` | Current working directory |
| `permission_mode` | Current permission mode (auto/ask/allow/deny) |
| `hook_event_name` | Name of the hook event fired |
| `effort` | Estimated effort level for the operation |

## Hook Filtering Fields

Granular filtering options for hook execution:

| Field | Purpose |
|---|---|
| `once` | Boolean — if true, hook fires only once then disables |
| `timeout` | Maximum execution time in seconds |
| `if` | Condition expression — hook runs only if true |

## Hook Handler Types

1. **Command hooks**: Shell scripts receiving JSON on stdin
2. **HTTP hooks**: Endpoints receiving POST requests
3. **Prompt hooks**: LLM prompts for decision-making
4. **Agent hooks**: Full agents for complex decisions
5. **MCP tool hooks**: MCP server tool hooks for external integrations

## Exit Codes

| Exit Code | Behavior |
|---|---|
| 0 | No decision, continue normal flow |
| 1 | Unknown error |
| 2 | Block/deny the operation (blocking behavior varies by event type) |
| Other | Decision from JSON output |

## Decision Control

Return JSON to control flow:

- **PreToolUse**: `{hookSpecificOutput: {permissionDecision: "allow"|"deny", additionalContext: {...}}}` — controls whether the tool executes
- **Other events with decision control**: Top-level `decision` field (values vary by event)
- **Adding context**: `hookSpecificOutput.additionalContext` object

Common decision fields:
- `retry: true` — Allow retry after PermissionDenied
- `continue: true` — Allow operation to continue

## Events with No Matcher Support

Always fire on every occurrence (no matcher filtering):
- `UserPromptSubmit`, `PostToolBatch`, `Stop`, `TeammateIdle`
- `TaskCreated`, `TaskCompleted`, `CwdChanged`
- `WorktreeCreate`, `WorktreeRemove`, `PreCompact`, `PostCompact`
- `SessionEnd`, `Notification`, `Elicitation`, `ElicitationResult`

## Security Best Practices

- Review plugin source code before installing
- Check MCP connector permissions
- Prefer Anthropic Verified plugins for production
- Report suspicious activity to Anthropic