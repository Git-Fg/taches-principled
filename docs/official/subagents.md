---
description: Complete reference for subagent frontmatter fields and spawn patterns
when_to_read: When creating agents, configuring subagent tools, or understanding spawn patterns
path: ./official/subagents.md
---

# Subagents - Claude Code Official Documentation

Source: https://code.claude.com/docs/en/sub-agents

Subagents are specialized AI assistants that handle specific types of tasks. Use one when a side task would flood your main conversation with search results, logs, or file contents you won't reference again: the subagent does that work in its own context and returns only the summary. Define a custom subagent when you keep spawning the same kind of worker with the same instructions.

Each subagent runs in its own context window with a custom system prompt, specific tool access, and independent permissions. When Claude encounters a task that matches a subagent's description, it delegates to that subagent, which works independently and returns results.

Subagents help you:

- **Preserve context** by keeping exploration and implementation out of your main conversation
- **Enforce constraints** by limiting which tools a subagent can use
- **Reuse configurations** across projects with user-level subagents
- **Specialize behavior** with focused system prompts for specific domains
- **Control costs** by routing tasks to faster, cheaper models like Haiku

## Built-in Agent Types

Claude Code includes built-in subagents that Claude automatically uses when appropriate. Each inherits the parent conversation's permissions with additional tool restrictions.

| Agent | Model | Tools | Purpose |
|-------|-------|-------|---------|
| **Explore** | Haiku | Read-only | File discovery, code search, codebase exploration. Skips CLAUDE.md and git status. |
| **Plan** | Inherit | Read-only | Codebase research for planning. Skips CLAUDE.md and git status. |
| **General-purpose** | Inherit | All | Complex research, multi-step operations, code modifications. |
| **statusline-setup** | Sonnet | — | When you run `/statusline` to configure your status line |
| **claude-code-guide** | Haiku | — | When you ask questions about Claude Code features |

**Explore and Plan** skip your CLAUDE.md files and the parent session's git status to keep research fast and inexpensive. Every other built-in and custom subagent loads both.

When invoking Explore, Claude specifies a thoroughness level: **quick** for targeted lookups, **medium** for balanced exploration, or **very thorough** for comprehensive analysis.

## Frontmatter Fields

Only `name` and `description` are required. All other fields are optional.

### Comprehensive Field Reference

| Field | Required | Type | Valid Values | Default | Description |
|-------|----------|------|-------------|---------|-------------|
| `name` | Yes | string | Lowercase letters, hyphens only | — | Unique identifier. Hooks receive this as `agent_type`. Filename does not need to match. |
| `description` | Yes | string | Natural language | — | When Claude should delegate to this subagent. Include trigger phrases like "proactively" to encourage use. |
| `tools` | No | array | Tool names (e.g., `Read`, `Edit`, `Bash`) | Inherit all | Allowlist of tools. Omit to inherit all. Can use `Agent(name)` for subagent restriction. |
| `disallowedTools` | No | array | Tool names | None | Denylist of tools to remove from inherited/set list. Applied first, then `tools` resolves. |
| `model` | No | string | `sonnet`, `opus`, `haiku`, full ID, or `inherit` | `inherit` | Which AI model to use. `inherit` uses main conversation's model. |
| `permissionMode` | No | string | `default`, `acceptEdits`, `auto`, `dontAsk`, `bypassPermissions`, `plan` | `default` | How the subagent handles permission prompts. Ignored for plugin subagents. |
| `maxTurns` | No | integer | Positive number | Unlimited | Maximum agentic turns before stopping. |
| `skills` | No | array | Skill names | None | Skills to preload at startup. Full content injected, not just description. Cannot preload `disable-model-invocation: true` skills. |
| `mcpServers` | No | array | Server names or inline definitions | None | MCP servers available to this subagent. Ignored for plugin subagents. |
| `hooks` | No | object | Hook definitions | None | Lifecycle hooks scoped to this subagent. Ignored for plugin subagents. |
| `memory` | No | string | `user`, `project`, `local` | None | Persistent memory scope. Enables cross-session learning. |
| `background` | No | boolean | `true`, `false` | `false` | Always run as background task. |
| `effort` | No | string | `low`, `medium`, `high`, `xhigh`, `max` | Inherit | Effort level override when active. |
| `isolation` | No | string | `worktree` | None | Run in a temporary git worktree for isolated repository access. |
| `color` | No | string | `red`, `blue`, `green`, `yellow`, `purple`, `orange`, `pink`, `cyan` | None | Display color in task list and transcript. |
| `initialPrompt` | No | string | Any text | None | Auto-submitted as first user turn when running as main session agent. |

**Note:** `context: fork` is a **skill frontmatter field only** (not an agent field). Skills use `context: fork` to run in isolated forked subagent context. Agents do not use this field.

### Frontmatter Examples

**Minimal agent:**
```yaml
---
name: reviewer
description: Reviews code for quality and best practices
---
```

**Full-featured agent:**
```yaml
---
name: api-developer
description: Implement API endpoints following team conventions. Use proactively after architecture decisions.
tools: Read, Edit, Bash, Glob, Grep
model: sonnet
permissionMode: acceptEdits
maxTurns: 15
skills:
  - api-conventions
  - error-handling-patterns
memory: local
color: blue
---

You are an API developer. Follow the conventions from preloaded skills.
```

**Agent with MCP server:**
```yaml
---
name: browser-tester
description: Tests features in a real browser using Playwright
tools: Read, Bash
mcpServers:
  - playwright:
      type: stdio
      command: npx
      args: ["-y", "@playwright/mcp@latest"]
---

Use Playwright tools to navigate, screenshot, and interact with pages.
```

**Agent with hook validation:**
```yaml
---
name: db-reader
description: Execute read-only database queries
tools: Bash
hooks:
  PreToolUse:
    - matcher: "Bash"
      hooks:
        - type: command
          command: "./scripts/validate-readonly-query.sh"
---

Execute SELECT queries only. Explain that write operations are not allowed.
```

## Model Resolution Order

When Claude invokes a subagent, the model resolves in this priority order:

1. **`CLAUDE_CODE_SUBAGENT_MODEL`** environment variable (highest)
2. **Per-invocation** `model` parameter passed to `Agent()`
3. **Subagent definition's** `model` frontmatter
4. **Main conversation's** model (default)

If none specified, defaults to `inherit` (main conversation's model).

## Tools Never Available

The following tools depend on the main conversation's UI or session state and are never available to subagents, even when listed in `tools`:

| Tool | Reason |
|------|--------|
| `Agent` | Cannot spawn other subagents. Use `Agent(name)` in tools field to restrict which subagents can be spawned. |
| `AskUserQuestion` | Requires main conversation UI |
| `EnterPlanMode` | Requires main conversation UI |
| `ExitPlanMode` | Requires main conversation UI (unless `permissionMode: plan`) |
| `ScheduleWakeup` | Requires main conversation UI |
| `WaitForMcpServers` | Requires main conversation UI |

## Subagent Scope & Priority

When multiple subagents share the same name, the higher-priority location wins.

| Location | Scope | Priority | Creation |
|----------|-------|----------|----------|
| Managed settings | Organization-wide | 1 (highest) | Deployed via managed settings |
| `--agents` CLI flag | Current session | 2 | JSON passed when launching |
| `.claude/agents/` | Current project | 3 | Interactive or manual |
| `~/.claude/agents/` | All projects | 4 | Interactive or manual |
| Plugin `agents/` directory | Where plugin enabled | 5 (lowest) | Installed with plugins |

**Project subagents** (`.claude/agents/`) are ideal for subagents specific to a codebase. Check into version control for team sharing.

**User subagents** (`~/.claude/agents/`) are available in all projects.

**Plugin subagents** appear in `/agents` alongside custom subagents. Use scoped names: `my-plugin:review:security` for subfolders.

**Security note:** Plugin subagents do not support `hooks`, `mcpServers`, or `permissionMode` frontmatter fields. These are ignored when loading from a plugin.

## Fork vs Named Subagent

A fork inherits everything the main session has at the moment it spawns. A named subagent starts from its own definition.

| Aspect | Fork | Named Subagent |
|--------|------|----------------|
| Context | Full conversation history | Fresh context with the prompt you pass |
| System prompt | Same as main session | From the subagent's definition file |
| Tools | Same as main session | From `tools` field (or inherit all) |
| Model | Same as main session | From `model` field (or inherit) |
| Permissions | Prompts surface in terminal | Auto-denied when running in background |
| Prompt cache | Shared with main session | Separate cache |
| CLAUDE.md | Inherited | Loaded fresh |
| Git status | Inherited | Loaded fresh |

**Forks share the parent's prompt cache**, making them cheaper than spawning a fresh subagent for tasks that need the same context.

**When to use fork:**
- Skill uses `context: fork` (the skill IS the context)
- Inheriting parent conversation is correct
- Speed matters, context reuse is beneficial
- Task is an extension of current work

**When to use named subagent:**
- Need fresh context
- Isolation is required
- Task is independent
- Standalone capability dispatch

Forks require `CLAUDE_CODE_FORK_SUBAGENT=1` environment variable (v2.1.117+).

## Complete Use Cases

### Explore Agent Use Cases

| Use Case | Why Explore | Example |
|----------|-------------|---------|
| File discovery | Read-only, fast, skips CLAUDE.md | "Find all test files in the src directory" |
| Code search | Optimized for grep/glob patterns | "Search for all uses of the auth function" |
| Codebase mapping | Skip git status for speed | "Map the project structure and key modules" |
| Dependency analysis | Read-only exploration | "List all dependencies and their versions" |
| Import tracing | Fast file reading | "Find where the database module is imported" |
| Configuration auditing | Skip CLAUDE.md for clean context | "Audit all config files for security issues" |
| API documentation search | Read-only access | "Find all API endpoint definitions" |
| Test coverage analysis | Parallel-friendly | "Analyze test coverage across all packages" |

### Plan Agent Use Cases

| Use Case | Why Plan | Example |
|----------|----------|---------|
| Pre-implementation research | Read-only, prevents nesting | "Research the codebase before planning changes" |
| Architecture analysis | Skips CLAUDE.md for speed | "Analyze the current architecture for improvements" |
| Impact assessment | Read-only before plan mode | "Assess what files need modification" |
| Dependency planning | No subagent nesting allowed | "Plan database migration approach" |
| Refactoring scope | Fresh context for planning | "Scope the refactoring requirements" |
| Risk identification | Read-only analysis | "Identify risks in the proposed changes" |
| Change estimation | Quick research | "Estimate effort for the requested feature" |
| Architecture comparison | No context pollution | "Compare current vs proposed architecture" |

### General-Purpose Agent Use Cases

| Use Case | Why General-Purpose | Example |
|----------|---------------------|---------|
| Complex multi-step tasks | Both exploration and action | "Refactor the authentication module with tests" |
| Implementation tasks | Full tool access | "Implement the new feature end-to-end" |
| File modifications | Edit/Write access | "Update all API handlers to use new format" |
| Multi-file refactoring | Complex reasoning | "Restructure the codebase into packages" |
| Test implementation | Full tool access | "Add unit tests for all new functions" |
| Documentation generation | Both read and write | "Generate API docs from code annotations" |
| Build automation | Bash access needed | "Set up the CI/CD pipeline configuration" |
| Data processing | Complex operations | "Process and transform the dataset files" |

### Custom Agent Use Cases

| Use Case | Why Custom | Example |
|----------|-----------|---------|
| Code review specialist | Focused prompt, restricted tools | "Review code for security vulnerabilities" |
| Debugging expert | Root cause analysis focus | "Debug the failing test and fix it" |
| Documentation writer | Domain-specific prompt | "Write technical documentation for APIs" |
| Database analyst | Read-only with validation | "Query and analyze the database" |
| Security auditor | Tool restrictions critical | "Audit for security issues and secrets" |
| Test writer | Domain-specific guidance | "Write comprehensive test suites" |
| Performance profiler | Specialized analysis | "Profile and optimize slow functions" |
| Migration assistant | Step-by-step guidance | "Migrate the codebase to new framework" |

### Bash Agent Use Cases

| Use Case | Why Bash Subagent | Example |
|----------|-------------------|---------|
| Long-running commands | Isolated context | "Run the build and report results" |
| Test execution | Verbose output isolation | "Execute test suite and summarize failures" |
| File processing | Heavy shell operations | "Process all log files and extract errors" |
| Deployment automation | Isolated execution | "Deploy to staging and verify health" |
| Data transformation | Batch operations | "Transform CSV files into JSON format" |

## Permission Modes Reference

| Mode | Behavior | Use When |
|------|----------|----------|
| `default` | Standard permission checking with prompts | Normal subagent execution |
| `acceptEdits` | Auto-accept file edits for working directory | Trusted implementation tasks |
| `auto` | Background classifier reviews commands | Eliminate prompts for routine ops |
| `dontAsk` | Auto-deny permission prompts | Background tasks, untrusted code |
| `bypassPermissions` | Skip all permission prompts | Trusted automation (dangerous) |
| `plan` | Read-only exploration | Research and planning only |

**Warning:** `bypassPermissions` skips all prompts including `.git`, `.claude`, `.vscode` writes. Root/home removals (`rm -rf /`) still prompt as circuit breaker.

**Parent precedence:** If parent uses `bypassPermissions` or `acceptEdits`, subagent cannot override. If parent uses `auto`, subagent inherits auto mode and frontmatter `permissionMode` is ignored.

## Memory Scopes

| Scope | Location | Use When |
|-------|----------|----------|
| `user` | `~/.claude/agent-memory/<name>/` | Cross-project knowledge |
| `project` | `.claude/agent-memory/<name>/` | Project-specific, version-controlled |
| `local` | `.claude/agent-memory-local/<name>/` | Project-specific, not committed |

Memory enables:
- First 200 lines or 25KB of `MEMORY.md` loaded at startup
- Instructions for curation when exceeded
- Automatic Read/Write/Edit tool enablement

## What Loads at Startup

**Non-fork subagent's initial context:**

| Component | Included | Notes |
|-----------|----------|-------|
| System prompt | Yes | Agent's prompt plus environment details (not full Claude Code system) |
| Task message | Yes | Delegation prompt from parent |
| CLAUDE.md | Yes | All levels (global, project, rules). Explore/Plan skip this. |
| Git status | Yes | Snapshot of parent session. Explore/Plan skip this. |
| Preloaded skills | Yes | Full content of listed skills |
| Conversation history | No | Fresh context |
| Already-read files | No | Fresh context |
| Already-loaded skills | No | Only preloaded ones |

**Fork subagent's initial context:** Inherits full parent conversation instead of above.

## CLI Definition (--agents flag)

Subagents can be passed as JSON when launching Claude Code. They exist only for that session.

```bash
claude --agents '{
  "code-reviewer": {
    "description": "Expert code reviewer. Use proactively after code changes.",
    "prompt": "You are a senior code reviewer...",
    "tools": ["Read", "Grep", "Glob", "Bash"],
    "model": "sonnet"
  }
}'
```

Accepted fields: `description`, `prompt`, `tools`, `disallowedTools`, `model`, `permissionMode`, `mcpServers`, `hooks`, `maxTurns`, `skills`, `initialPrompt`, `memory`, `effort`, `background`, `isolation`, `color`. Use `prompt` instead of markdown body.

## Hook Events for Subagents

| Event | Matcher Input | When It Fires |
|-------|--------------|---------------|
| `PreToolUse` | Tool name | Before the subagent uses a tool |
| `PostToolUse` | Tool name | After the subagent uses a tool |
| `Stop` | None | When subagent finishes (converted to `SubagentStop`) |

**Project-level hooks** (in `settings.json`):

```json
{
  "hooks": {
    "SubagentStart": [{ "matcher": "db-agent", "hooks": [...] }],
    "SubagentStop": [{ "hooks": [...] }]
  }
}
```

## Common Patterns

1. **Isolate high-volume operations**: Tests, logs, docs produce verbose output — keep it in subagent context
2. **Parallel research**: Multiple subagents work simultaneously on independent areas
3. **Chain subagents**: Sequence with context passing between steps
4. **Domain specialization**: Focused prompts for code review, debugging, etc.
5. **Tool restrictions**: Grant only necessary permissions for security

**Subagents cannot spawn other subagents.** For nested delegation, use Skills or chain from main conversation.

---

## Marketplace Conventions (Taches Principled)

These conventions extend official Claude Code documentation for the taches-principled plugin ecosystem.

### Recommended Agent Fields

For all plugin-level agents, include these fields:

```yaml
maxTurns: 15    # Safety limit — stops runaway agents
memory: local    # Persistent local memory during session
```

### Skills Preloading

Use `skills` field to preload evaluation frameworks. The agent evaluates against the skill's framework directly, eliminating duplicated methodology in agent prompts:

```yaml
skills: [skill-name]
```

**When to preload:**
- Evaluation agents (critics, graders, auditors) that judge output against a framework
- Preload the framework the agent evaluates against

**When NOT to preload:**
- Execution agents orchestrated by a skill (the skill owns the methodology, agent executes)
- Skills with `disable-model-invocation: true`

Cannot preload skills with `disable-model-invocation: true`.

### Spawn Vocabulary

Use canonical "spawn a [role] subagent" pattern:
- "spawn a critic subagent"
- "spawn a researcher subagent"
- "spawn a verification subagent"

### Spawn Footer

All agents should include a footer acknowledging their subagent role:

```
You are a subagent executing a delegated task. Your context starts fresh — no access to
prior conversation or other subagents' outputs. When complete, return your full results
(file paths, findings, and any artifacts) to the orchestrator in structured form.
If you encounter anything unexpected or have any question or doubt, stop and report back
with what you found and what is unclear. Do not proceed silently on assumptions.
```

### Agent Directory Structure

| Type | Location | Availability |
|------|----------|--------------|
| Plugin-level | `plugins/<plugin>/agents/<name>.md` | System-wide when plugin enabled |
| Skill-internal | `plugins/<plugin>/skills/<skill>/agents/<name>.md` | Only when skill loaded |

Plugin-level agents are available system-wide. Skill-internal agents are prompt templates for that workflow only.

### Agent Tool Contract

**An agent's declared tools MUST match its stated capabilities.**

When an agent claims to write findings to disk, it needs the Write tool. When it claims to execute shell commands, it needs Bash. If the capability exists in the description but the tools field is missing, the agent cannot fulfill its contract.

### Subagent-First Execution

The default execution mode for complex tasks is subagent delegation, not inline execution. Skills should teach:

- Spawn explorer subagents for exploration
- Spawn researcher subagents for research
- Spawn critic subagents for review
- Spawn verification subagents for testing

The main agent synthesizes results; it never performs the work inline for non-trivial tasks.

### Agent Description Pattern

Agent descriptions should use natural language sentences, not structured syntax. Describe WHAT the agent is and WHEN it activates, not procedural instructions.

Good: "Invokes automatically after any artifact is created — verifies correctness, completeness, and clarity before delivery"

Bad: "ACTIVATES: after any artifact creation\nLOOP: until no HIGH findings\nOutput: severity-ranked findings"

### Context Handoff

Subagents start cold — no shared conversation history. Pass all needed context in the spawn prompt. Persist state to disk; subagents read from it rather than receiving it inline.

### Quality Gates

1. **Pre-dispatch**: Confirm tasks are independent; subagents must not write to overlapping files
2. **Receipt**: Run success criteria. If fail, root-cause analysis, re-decompose, respawn
3. **Integration**: Cross-domain consistency check plus full test suite

### No Inline Tool Lists

When a skill body describes spawning a subagent, never include a specific tool list. Describe the role and outcome instead:

| Instead of | Use |
|------------|-----|
| "Spawn a subagent (Haiku, tools: Read, Write, Grep, Glob, Bash)" | "Spawn an explorer subagent to map project structure" |
| "Spawn a researcher (Sonnet, WebSearch, Read, Write)" | "Spawn a researcher subagent to investigate patterns" |

Agent definitions already configure tools per role. Inline lists duplicate this and break when tools change.

### Version Considerations

- **Plugin version**: Incremented for any content change
- **Marketplace version**: Incremented for collective updates across plugins

When adding new agents, bump the plugin version in `.claude-plugin/plugin.json`.