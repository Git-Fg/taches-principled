---
name: claude-cli
description: "Drive the Claude Code CLI from the Bash tool — headless invocations, multi-turn sessions, model/effort/permission control, structured output, and the code-review subcommand. Use when an agent needs to spawn a headless Claude session, continue a previous session, request structured JSON output from Claude, run a cloud code review, or control the Claude CLI's runtime flags. Not for direct user-driven Claude Code use and not for designing/building MCP servers."
when_to_use: |
  - "Spawn a headless Claude session to run a task"
  - "Continue or resume a previous Claude Code session"
  - "Get structured JSON output from Claude"
  - "Run a cloud-hosted code review"
  - "Change the model, effort, or permission mode for a Claude invocation"
  - "Drive Claude Code programmatically from a Bash command"
---

# claude-cli

The `claude` CLI is the same binary that powers interactive Claude Code. With `-p` (print) it runs headlessly, accepts a prompt, and writes the response to stdout. This skill teaches the flags and patterns for driving it from the Bash tool — covering the six conceptual operations the marketplace has used historically (execute, session, context, review, agent, config), now expressed as native CLI flags rather than as wrapper-tool calls.

For MCP design/implementation/schema patterns (i.e., *building* MCP servers, not *using* the `claude` CLI), see `tp-mcp`'s `mcp-server-design`, `mcp-server-implement`, and `mcp-tool-surface` skills.

---

## §1. When this skill fires

**Use this skill when the request is to drive the `claude` CLI from a Bash invocation:**

- "Run Claude on this prompt headlessly"
- "Spawn a headless Claude session to do X"
- "Continue the Claude session from earlier"
- "Get Claude to return JSON in this schema"
- "Run a code review on this branch"
- "Change the model to opus for this invocation"
- "Drive Claude Code programmatically"

**DO NOT use this skill for:**

- "How do I design an MCP server" → `tp-mcp` `mcp-server-design`
- "How do I implement an MCP server in Rust" → `tp-mcp` `mcp-server-implement`
- "How do I write a good JSON Schema" → `tp-mcp` `mcp-tool-surface`
- "How do I use the Bash tool" → Claude Code's built-in docs
- "How do I run Claude Code interactively" → Claude Code's built-in docs (not headless)

## CONTRAST

- NOT for: spawning in-process subagents within the current Claude Code session — use subagent-orchestration
- NOT for: designing an MCP server from scratch — use `mcp-server-design`
- NOT for: writing a single Claude Code hook — see the official hooks docs
- NOT for: managing installed plugins/MCP servers — use `claude plugin list` / `claude mcp list` directly in Bash

---

## §2. The 6 conceptual operations

The marketplace historically exposed the `claude` CLI as six MCP tools. The wrapper is gone, but the conceptual decomposition is still useful as a mental model. Here's the mapping to native CLI flags:

| Operation | Old MCP tool | Native CLI pattern |
|---|---|---|
| **execute** | `claude_execute` | `claude -p "..." --output-format json` |
| **session** | `claude_session` | `claude --resume <uuid>` or `claude --continue` or `claude --session-id <uuid>` |
| **context** | `claude_context` | `claude --add-dir <path>` or `claude --worktree [name]` or `claude doctor` |
| **review** | `claude_review` | `claude ultrareview [target] --json` |
| **agent** | `claude_agent` | `claude --agent <name> -p "..."` and `claude agents --json` |
| **config** | `claude_config` | per-invocation flags: `--model`, `--effort`, `--permission-mode`, `--settings` |

The rest of this skill teaches the flags themselves.

---

## §3. `execute` — the workhorse

The primary tool. Run a prompt, get output. The `claude -p` form is non-interactive: it reads the prompt, processes it, writes the result to stdout, and exits.

### Minimum viable invocation

```bash
claude -p "What is 2+2?"
```

This works but writes plain text. For an agent caller, you almost always want JSON.

### The canonical invocation

```bash
claude -p "Refactor src/auth.rs to use the newtype pattern" \
  --output-format json \
  --model sonnet \
  --effort high \
  --permission-mode acceptEdits
```

Flags by category:

**Execution mode:**
- `-p, --print` — non-interactive, write response to stdout, exit. This is the universal invocation prefix for headless use.
- `--bare` — minimal mode. Skips hooks, LSP, plugin sync, attribution, auto-memory, background prefetches, keychain reads, and CLAUDE.md auto-discovery. Sets `CLAUDE_CODE_SIMPLE=1`. Use only when you need to bypass plugin/hook machinery for a clean test or sandbox.

**Output:**
- `--output-format text|json|stream-json` — serialization. Default `text`. Use `json` when an agent will parse the response. Use `stream-json` for realtime token-by-token output.
- `--json-schema <schema>` — JSON Schema for structured output validation. Inline string, not a file path. The CLI validates the response against the schema; if it doesn't match, the call fails. **This is the right way to get typed output from Claude** — much better than asking Claude to "please respond in JSON" in the prompt.
- `--input-format text|stream-json` — input format (default `text`). Use `stream-json` for realtime streaming input.
- `--include-partial-messages` — include partial message chunks as they arrive (only with `--print` and `--output-format=stream-json`).
- `--replay-user-messages` — re-emit user messages from stdin back on stdout for acknowledgment (only with `stream-json` input + output).

**Model / effort / budget:**
- `--model <model>` — `sonnet`, `opus`, `haiku`, or a full name like `claude-opus-4-8`. Aliases resolve to the latest version of that family.
- `--fallback-model <model>` — automatic fallback when the default model is overloaded or unavailable. Only works with `--print`.
- `--effort <level>` — `low`, `medium`, `high`, `xhigh`, `max`. Default is whatever's configured in the project. Higher effort = more reasoning, more cost, more time.
- `--max-budget-usd <amount>` — spend cap for this invocation. Only works with `--print`. The CLI exits cleanly when the budget is reached.

**Permissions:**
- `--permission-mode <mode>` — `acceptEdits`, `auto`, `bypassPermissions`, `default`, `dontAsk`, `plan`. **For agent-driven invocations, use `acceptEdits`** so Claude can edit files without prompting the user.
- `--allow-dangerously-skip-permissions` — make `bypassPermissions` available without defaulting to it.
- `--dangerously-skip-permissions` — bypass all permission checks. **Recommended only for sandboxes with no internet access.** Do not use this in shared environments.

**Tool access:**
- `--allowedTools, --allowed-tools <tools...>` — comma- or space-separated allowlist. Example: `Bash(git *),Edit`. Repeatable; multiple values accumulate.
- `--disallowedTools, --disallowed-tools <tools...>` — denylist. Same syntax.
- `--tools <tools...>` — specify the available built-in tools. `""` disables all tools, `"default"` uses the full set, or list names like `Bash,Edit,Read`.

**System prompt:**
- `--system-prompt <prompt>` — override the entire system prompt. Use for forcing a specific persona.
- `--append-system-prompt <prompt>` — extend the default system prompt. Use for adding context (project conventions, role).
- `--exclude-dynamic-system-prompt-sections` — move per-machine sections (cwd, env, memory paths, git status) out of the system prompt into the first user message. Improves cross-user prompt-cache reuse. Only applies with the default system prompt (ignored with `--system-prompt`).

**MCP / extensions:**
- `--mcp-config <configs...>` — load MCP servers from JSON files or inline JSON strings. Space-separated. Each config is independent.
- `--strict-mcp-config` — only use MCP servers from `--mcp-config`, ignoring all other MCP configurations.
- `--plugin-dir <path>` — load a plugin from a directory or .zip for this session only. Repeatable.
- `--plugin-url <url>` — fetch a plugin .zip from a URL for this session only. Repeatable.

**Metadata:**
- `-n, --name <name>` — display name for the session (shown in `/resume` picker and terminal title).
- `--setting-sources <sources>` — comma-separated list of setting sources to load: `user`, `project`, `local`. Default loads all three.

**File preloading:**
- `--file <specs...>` — file resources to download at startup. Format: `file_id:relative_path`. Used for hosted files.

### Example: structured output (the right way to do it)

```bash
claude -p "Classify this support ticket: '$TICKET_TEXT'" \
  --output-format json \
  --json-schema '{"type":"object","properties":{"category":{"type":"string","enum":["bug","feature","question"]},"priority":{"type":"string","enum":["low","medium","high"]}},"required":["category","priority"]}'
```

Claude's response is validated against the schema. If it doesn't match, the call fails with a validation error.

---

## §4. `session` — lifecycle

Sessions are how you keep context across multiple invocations. The CLI manages session IDs as UUIDs; you pass them between invocations to resume continuity.

### Resume an existing session

```bash
claude --resume <session-uuid> -p "Continue the refactor: also add tests"
```

The UUID must be valid (8-4-4-4-12 hex). If invalid, the CLI rejects it.

### Open the resume picker (interactive)

```bash
claude --resume
```

With no value, `--resume` opens an interactive session picker. Filter with a search term:

```bash
claude --resume "auth refactor"
```

(The interactive picker is unavailable in non-TTY contexts — for scripted use, pass an explicit UUID.)

### Continue the most recent session in the current directory

```bash
claude --continue -p "Continue the refactor"
```

This is shorthand for "find the most recent session whose CWD matches the current directory and resume it". Use this when you've been iterating and just want to pick up where you left off.

### Use an explicit session ID

```bash
claude --session-id <uuid> -p "Start a new session with this specific ID"
```

The UUID must be valid. Use this when you want to pre-allocate a session ID (e.g., for logging or external tracking) before the first invocation.

### Branch a session

```bash
claude --resume <existing-uuid> --fork-session -p "Try a different approach"
```

`--fork-session` creates a new session ID branched from the existing one. The original session is unchanged. Use this for A/B exploration without polluting the original.

### List sessions

The CLI does not have a dedicated `list-sessions` flag. The two ways to enumerate sessions:

1. **Interactive**: `claude --resume` with no value opens the picker, which lists all known sessions.
2. **Programmatic**: read `~/.claude/sessions/` (or `$CLAUDE_CONFIG_DIR/sessions/`) directly. The CLI stores session metadata as JSONL files.

For a Bash script, the second approach is the only one that works in non-TTY contexts.

### Inspect session metadata

The CLI does not have a dedicated `session-info` flag. To get metadata:

- For an active session: the JSON output of `claude -p --output-format json` includes the session ID.
- For a stored session: parse the session's JSONL file in `~/.claude/sessions/`.

### Close a session

The CLI does not have a dedicated `close-session` flag. Sessions are closed by:

- Exiting the interactive session (Ctrl-C, Ctrl-D, or natural end of conversation).
- Letting the session expire (the CLI's default retention policy is 30 days; configurable via `--setting-sources` and project settings).
- Using `--no-session-persistence` to opt out of persistence entirely (sessions are not saved to disk and cannot be resumed).

### Resume a session linked to a PR

```bash
claude --from-pr                    # interactive picker
claude --from-pr 123                # session linked to PR #123
claude --from-pr https://github.com/owner/repo/pull/123
```

Resumes a session that was started in the context of a specific PR. The session picker accepts an optional search term.

---

## §5. `context` — workspace

Tell Claude about the working directory and any additional context it should have access to.

### Add directories to the tool access list

```bash
claude -p "Refactor this" --add-dir /path/to/lib --add-dir /path/to/tests
```

`--add-dir` is repeatable. The CLI grants tool access to each additional directory. Without it, Claude is sandboxed to the current working directory.

For the common case of "let Claude read the current directory", `claude -p` in the target dir is enough — `--add-dir` is for adding extras.

### Use a git worktree

```bash
claude -p "Refactor in a clean worktree" --worktree
# or with a name:
claude -p "Refactor in a clean worktree" --worktree auth-refactor
```

`--worktree` creates a new git worktree for the session. The session runs in the worktree; changes are isolated until you merge. Optional `[name]` for the worktree branch.

Combine with `--tmux` to run the work in a tmux session (or iTerm2 native panes):

```bash
claude -p "Refactor in a worktree" --worktree --tmux
```

### Diagnose the Claude Code installation

```bash
claude doctor
```

Runs health checks on the Claude Code auto-updater. Reports whether updates are available, and whether the installation is healthy. The workspace trust dialog is skipped; stdio servers from `.mcp.json` are spawned for health checks. Use only in directories you trust.

For deeper diagnostics (session analytics, hook events), use the `tp-session-audit` plugin.

---

## §6. `review` — code review

The CLI has a dedicated `ultrareview` subcommand for cloud-hosted multi-agent code reviews. This is the right way to do code review from the CLI — it's not a prompt pattern, it's a real subcommand with structured output.

### Run a review of the current branch

```bash
claude ultrareview
```

Reviews the current branch's diff against the default branch. Prints findings to stdout.

### Review a specific PR

```bash
claude ultrareview 123                  # PR number
claude ultrareview https://github.com/owner/repo/pull/123   # PR URL
claude ultrareview feature-branch       # branch name (compared to default branch)
```

### Get structured findings (JSON)

```bash
claude ultrareview --json
```

Prints the raw `bugs.json` payload instead of the formatted findings. Use this when an agent will parse the findings.

### Set a timeout

```bash
claude ultrareview --timeout 60         # wait up to 60 minutes
```

Default timeout is 30 minutes. The review aborts and prints partial findings on timeout.

### Review as a prompt pattern (no ultrareview)

If you need a quick, local review (not cloud-hosted, no multi-agent), use the prompt pattern:

```bash
claude -p "Review the changes in this branch for bugs, security issues, and code quality. Be specific: cite file:line for each finding. Do not propose architectural rewrites — focus on what's actually wrong in the diff." \
  --output-format json \
  --add-dir .
```

The structured-output skill (`--json-schema`) can enforce a finding-shape contract:

```bash
claude -p "Review the changes in this branch" \
  --output-format json \
  --json-schema '{"type":"object","properties":{"findings":{"type":"array","items":{"type":"object","properties":{"file":{"type":"string"},"line":{"type":"integer"},"severity":{"type":"string","enum":["blocker","warning","suggestion"]},"description":{"type":"string"}},"required":["file","line","severity","description"]}}}}'
```

Prefer `claude ultrareview` for serious reviews. The prompt pattern is a fallback for "I just want a quick sanity check" cases.

---

## §7. `agent` — background management

The `claude` CLI has two ways to spawn agents:

1. **Per-invocation agent selection** (`--agent <name>`) — pick an agent for the current session
2. **Background agent view** (`claude agents`) — manage agents that are running in the background

### Spawn an agent for the current session

```bash
claude -p "Run a security review of this codebase" --agent security-reviewer
```

The agent is selected for the current session only. If `--agent` is not specified, the default agent is used (or whatever the `agent` setting resolves to).

### Define an inline custom agent

```bash
claude -p "Review this PR" \
  --agents '{"reviewer": {"description": "Reviews code for security and quality issues", "prompt": "You are a code reviewer focused on security. For each finding, cite file:line and explain the exploit."}}'
```

`--agents` is a JSON object defining custom agents for this session. The keys are agent names; the values have `description` and `prompt` fields.

### Manage background agents

```bash
claude agents                      # open the interactive agent view
claude agents --json               # list live background sessions as JSON, exit
claude agents --cwd /path/to/proj  # filter by starting directory
```

`claude agents --json` is the right pattern for an agent caller that needs to enumerate running sessions. The output is a JSON array of session metadata.

### Set defaults for dispatched sessions

When using the agent view, you can set defaults that apply to all sessions dispatched from it:

```bash
claude agents --model opus                          # default model
claude agents --effort high                         # default effort
claude agents --permission-mode acceptEdits         # default permissions
claude agents --mcp-config /path/to/config.json     # default MCP config
claude agents --add-dir /extra/dir                  # additional directories
```

### Terminate a background agent

The CLI does not have a `--kill-agent` flag. To terminate a background agent:

- In the interactive agent view (`claude agents`): use the keyboard shortcut to terminate the selected session.
- From a script: send the process a signal. The session is a regular OS process; `kill <pid>` works but is unclean. Prefer the interactive view or letting the agent complete naturally.
- Set a max budget with `--max-budget-usd` so the agent stops itself at the spend cap.

For agent-runtime semantics (subagent orchestration, parallel dispatch, etc.), see `subagent-orchestration`. The CLI flags here are the surface; the orchestration pattern is the marketplace's separate concern.

---

## §8. `config` — runtime tuning

There is no "set config" command in the CLI. The model, effort, permission mode, and settings are all set as per-invocation flags, then re-invoked with different values as needed.

### Model

```bash
claude -p "Quick classification" --model haiku      # cheap, fast
claude -p "Hard reasoning task" --model opus --effort max
claude -p "Default work" --model sonnet --effort high
```

### Effort

```bash
claude -p "..." --effort low      # fast, cheap, may be wrong
claude -p "..." --effort medium   # default
claude -p "..." --effort high     # more reasoning
claude -p "..." --effort xhigh    # significantly more reasoning
claude -p "..." --effort max      # the most reasoning the model will do
```

### Permission mode

```bash
claude -p "..." --permission-mode acceptEdits       # auto-accept file edits
claude -p "..." --permission-mode plan              # enter plan mode first
claude -p "..." --permission-mode dontAsk           # don't ask; reject by default
claude -p "..." --permission-mode bypassPermissions  # bypass all checks
```

For agent-driven invocations, `acceptEdits` is almost always what you want — it lets Claude edit files without prompting the user (who isn't there to respond).

### Settings file

```bash
claude -p "..." --settings /path/to/settings.json
claude -p "..." --settings '{"permissions":{"allow":["Bash"]}}'   # inline JSON
```

`--settings` accepts either a path to a JSON file or an inline JSON string. The settings merge with the user/project/local settings per `--setting-sources`.

### Control which setting sources are loaded

```bash
claude -p "..." --setting-sources user,project
claude -p "..." --setting-sources project                    # only project settings
claude -p "..." --setting-sources ""                          # no settings
```

By default, all three sources (user, project, local) are loaded. Use this flag to scope which sources apply for a given invocation.

### Verbose / debug

```bash
claude -p "..." --verbose
claude -p "..." --debug api,hooks          # enable debug mode with category filter
claude -p "..." --debug-file /tmp/debug.log
```

`--debug` with no value enables all categories; with a value, filters to those categories. `--debug-file` writes debug logs to a file (implicitly enables debug mode).

---

## §9. Output contract

The CLI's output contract is much simpler than the old wrapper's. Here's what an agent caller needs to know.

### Plain text output

```bash
$ claude -p "What is 2+2?"
4
```

Plain text on stdout. Easy to capture; hard to parse programmatically.

### JSON output

```bash
$ claude -p "What is 2+2?" --output-format json | jq .
{
  "type": "result",
  "subtype": "success",
  "is_error": false,
  "duration_ms": 1234,
  "duration_api_ms": 1100,
  "num_turns": 1,
  "result": "4",
  "session_id": "abc-1234-...",
  "total_cost_usd": 0.0023,
  "usage": { ... }
}
```

The JSON envelope includes:
- `result` (string) — Claude's response
- `session_id` (UUID) — the session that was used or created
- `is_error` (boolean) — whether the call failed
- `duration_ms` / `duration_api_ms` (numbers) — wall-clock and API-only time
- `num_turns` (number) — how many model turns the call used
- `total_cost_usd` (number) — actual cost
- `usage` (object) — token usage breakdown

**`session_id` is inside the JSON output, not lifted to a top-level field.** If you need to resume the session, parse the JSON, extract `session_id`, and pass it to `--resume` on the next call.

```bash
SESSION_ID=$(claude -p "..." --output-format json | jq -r '.session_id')
claude --resume "$SESSION_ID" -p "Continue: also add tests"
```

### Exit codes

- `0` — success
- non-zero — failure (check stderr for the reason)

The CLI uses raw Unix exit codes, not JSON-RPC codes. If you need a structured error, parse the JSON output and check `is_error`.

### Stream-json output

```bash
claude -p "..." --output-format stream-json
```

Writes newline-delimited JSON events as they happen. Each line is a typed event (assistant message, tool use, tool result, etc.). Use this for realtime UI or for piping into another agent's input stream.

---

## §10. Common workflows

**Workflow 1: One-shot task**

```bash
claude -p "Refactor user.rs to use the newtype pattern" --permission-mode acceptEdits
```

**Workflow 2: Multi-turn session with continuity**

```bash
# Turn 1
SESSION_ID=$(claude -p "Start a refactor of the auth module" --output-format json | jq -r '.session_id')

# Turn 2 (later)
claude --resume "$SESSION_ID" -p "Continue: also add tests"
```

**Workflow 3: Background agent + polling**

```bash
# Spawn (in a separate process / Bash background)
claude -p "Generate rustdoc for src/parser.rs" --output-format json > /tmp/doc-gen.json 2>&1 &

# Poll the result
while kill -0 $! 2>/dev/null; do sleep 5; done
cat /tmp/doc-gen.json | jq -r '.result'
```

Or use the agent view:

```bash
# List running agents
claude agents --json | jq '.[] | {name: .name, status: .status}'
```

**Workflow 4: Code review of a PR**

```bash
claude ultrareview 123 --json | jq '.findings[]'
```

**Workflow 5: Structured output for downstream parsing**

```bash
claude -p "Classify this ticket: '$TICKET_TEXT'" \
  --output-format json \
  --json-schema '{"type":"object","properties":{"category":{"type":"string","enum":["bug","feature","question"]},"priority":{"type":"string","enum":["low","medium","high"]}},"required":["category","priority"]}' \
  | jq '{category: .result | fromjson | .category, priority: .result | fromjson | .priority}'
```

Or use `--json-schema` together with a prompt that tells Claude to populate the result with the structured object directly:

```bash
claude -p "Classify this ticket. Respond with a JSON object that matches the schema." \
  --output-format json \
  --json-schema '...' \
  | jq -r '.result' | jq .
```

The exact path depends on whether the model returns a JSON string (which it usually does) or a pre-parsed object.

**Workflow 6: Headless capture into a session for later review**

```bash
SESSION_ID=$(claude -p "Run a security audit" --output-format json | jq -r '.session_id')
# Later, resume and ask follow-ups:
claude --resume "$SESSION_ID" -p "Drill into the auth findings"
```

---

## §11. Anti-patterns

❌ **Looping `claude -p` 50 times for 50 small tasks** — use `--continue` to maintain context, or batch related tasks into a single prompt. Each `-p` invocation is a fresh model call; the session_id is the only state that persists.

❌ **Forgetting `--permission-mode acceptEdits`** — Claude will refuse to edit files (or ask the user, who isn't there). The call appears to hang. Always set the permission mode for agent-driven invocations.

❌ **Using `--dangerously-skip-permissions` in shared environments** — this bypasses all safety checks. Only use in sandboxes with no internet access.

❌ **Using `--output-format text` when you need to parse the result** — use `json` and parse with `jq`. Don't try to regex-match plain text.

❌ **Putting a JSON Schema as a nested object** — `--json-schema` takes a STRING. The CLI passes it to the model verbatim.

❌ **Setting `--disallowed-tools "Read,Edit"`** — these are core tools; you're effectively turning Claude into a chat-only instance.

❌ **Using `--bare` in production** — you lose hooks, LSP, plugin sync, attribution, auto-memory, keychain reads, and CLAUDE.md auto-discovery. Only use for clean test environments.

❌ **Hardcoding a full model name like `claude-opus-4-8`** — prefer aliases (`sonnet`, `opus`, `haiku`) so the call tracks the latest model. Hardcoded names break when models are deprecated.

❌ **Resuming a session without verifying the UUID format** — invalid UUIDs cause the CLI to error. Validate with a regex check or use `--continue` (no UUID needed).

❌ **Forgetting `--add-dir` when Claude needs to read files outside the cwd** — without it, Claude is sandboxed to the current working directory and will fail to read external files.

---

## §12. Handoff

- **MCP design principles** (why some tools decompose the way they do) → `tp-mcp` `mcp-server-design`
- **MCP implementation in Rust with rmcp + schemars** → `tp-mcp` `mcp-server-implement`
- **JSON Schema authoring details** → `tp-mcp` `mcp-tool-surface`
- **Subagent orchestration patterns** (parallel dispatch, scratchpad, critic loops) → `subagent-orchestration`
- **Session analytics and behavioral review** → `tp-session-audit`

---

## §13. Key sources

- [1] Claude Code CLI documentation — https://docs.claude.com/en/docs/claude-code
- [2] Decomposition patterns (why 6 tools vs 1) — `tp-mcp/skills/mcp-server-design/references/design-decisions.md` §3
- [3] Structured output with `--json-schema` — official Claude Code docs on JSON Schema validation
- [4] Marketplace entry — `.claude-plugin/marketplace.json` in this repo
