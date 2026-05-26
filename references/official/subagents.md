# Subagents - Claude Code Official Documentation

Source: https://code.claude.com/docs/en/sub-agents

## Overview

Subagents are specialized AI assistants that handle specific types of tasks. Each subagent runs in its own context window with a custom system prompt, specific tool access, and independent permissions.

## Built-in Subagents

- **Explore** (Haiku, read-only): File discovery, code search, codebase exploration
- **Plan** (planning-focused): Architecture analysis, implementation planning
- **General-purpose**: Default subagent for general tasks
- **Other**: Model-specific configurations

## Subagent Scope & Priority

| Location | Scope | Priority |
|---|---|---|
| Managed settings | Organization-wide | 1 (highest) |
| `--agents` CLI flag | Current session | 2 |
| `.claude/agents/` | Current project | 3 |
| `~/.claude/agents/` | All projects | 4 |
| Plugin `agents/` directory | Where plugin enabled | 5 (lowest) |

## Frontmatter Fields

| Field | Required | Description |
|---|---|---|
| `name` | Yes | Unique identifier (lowercase, hyphens) |
| `description` | Yes | When to delegate to this subagent |
| `tools` | No | Tools subagent can use |
| `disallowedTools` | No | Tools to deny |
| `model` | No | `sonnet`, `opus`, `haiku`, full ID, or `inherit` |
| `permissionMode` | No | `default`, `acceptEdits`, `auto`, `dontAsk`, `bypassPermissions`, `plan` |
| `maxTurns` | No | Max agentic turns before stopping |
| `skills` | No | Skills to preload at startup |
| `mcpServers` | No | MCP servers for this subagent |
| `hooks` | No | Lifecycle hooks |
| `memory` | No | `user`, `project`, or `local` for persistent memory |
| `background` | No | Run as background task |
| `effort` | No | Effort level override |
| `isolation` | No | `worktree` for isolated git copy |
| `color` | No | Display color |
| `initialPrompt` | No | Auto-submitted first user turn |

## Fork vs Named Subagent

| Aspect | Fork | Named Subagent |
|---|---|---|
| Context | Full conversation history | Fresh context |
| System prompt | Same as main session | From definition |
| Model | Same as main session | From `model` field |
| Permissions | Prompts surface in terminal | Auto-denied when background |
| Prompt cache | Shared with main session | Separate cache |

## Work with Subagents

**Use main conversation when:**
- Task needs frequent back-and-forth
- Multiple phases share context
- Quick, targeted change
- Latency matters

**Use subagents when:**
- Task produces verbose output
- Need tool restrictions
- Self-contained work returning summary

## What Loads at Startup

A non-fork subagent's initial context contains:
- System prompt (agent's own prompt plus environment details that Claude Code appends, not the full Claude Code system prompt)
- Task message (delegation prompt)
- CLAUDE.md and memory (all levels)
- Git status snapshot
- Preloaded skills (full content)

**The exception is a fork, which inherits the parent conversation instead of starting fresh.** Explore and Plan agents skip CLAUDE.md and git status regardless.

## Preload Skills

Use `skills` field to inject skill content at startup. Cannot preload skills with `disable-model-invocation: true`.

## Persistent Memory

| Scope | Location |
|---|---|---|
| `user` | `~/.claude/agent-memory/<name>/` |
| `project` | `.claude/agent-memory/<name>/` |
| `local` | `.claude/agent-memory-local/<name>/` |

## Model Selection

Order: `CLAUDE_CODE_SUBAGENT_MODEL` env → per-invocation `model` → subagent definition → main conversation model

## Control Capabilities

- **tools**: Allowlist specific tools
- **disallowedTools**: Denylist specific tools (applied first, then tools resolves)
- **permissionMode**: `bypassPermissions`, `acceptEdits`, `auto`, `dontAsk`, `default`, `plan`

## Background vs Foreground

- **Foreground**: Blocks main conversation, permission prompts pass through
- **Background**: Runs concurrently, auto-denies permission prompts

## Common Patterns

1. **Isolate high-volume operations** (tests, logs, docs)
2. **Parallel research** (multiple subagents simultaneously)
3. **Chain subagents** (sequence with context passing)

---

## Marketplace Conventions (Taches Principled)

These conventions go beyond official Claude Code docs for the taches-principled plugin ecosystem.

### Recommended Agent Fields

For all plugin-level agents, include these fields:

```yaml
maxTurns: 15    # Safety limit — stops runaway agents
memory: local    # Persistent local memory during session
```

### Skills Preloading

Use `skills` field to preload the parent skill for agent evaluation:
```yaml
skills: [skill-name]
```
This eliminates duplicated methodology in agent prompts — the agent evaluates against the skill's framework directly.

### Spawn Vocabulary

Use canonical "spawn a [role] subagent" pattern:
- ✅ "spawn a critic subagent"
- ✅ "spawn a researcher subagent"
- ❌ "dispatch an agent"
- ❌ "launch a worker"
- ❌ "fire off a subagent"

### Spawn Footer

All agents should include a footer acknowledging their subagent role:

```
You are a subagent executing a delegated task. Your context starts fresh — no access to
prior conversation or other subagents' outputs. When complete, return your full results
(file paths, findings, and any artifacts) to the orchestrator in structured form.
If you encounter anything unexpected or have any question or doubt, stop and report back
with what you found and what is unclear. Do not proceed silently on assumptions.
```

### Subagent Directory Structure

Plugin-level agents (discovered system-wide): `plugins/<plugin>/agents/<name>.md`
Skill-internal agents (workflow-specific): `plugins/<plugin>/skills/<skill>/agents/<name>.md`

Skill-internal agents are prompt templates for that workflow only. Plugin-level agents are available system-wide when the plugin is enabled.

### When to Use Fork vs Named Subagent

| Use fork when | Use named subagent when |
|-------------|----------------------|
| Inheriting parent conversation is correct | Need fresh context |
| Speed matters, context reuse is beneficial | Isolation is required |
| Task is an extension of current work | Task is independent |

Fork is default for skill-based agents (the skill IS the context). Named subagent for standalone capability dispatch.