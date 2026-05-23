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
- System prompt (from agent definition)
- Task message (delegation prompt)
- CLAUDE.md and memory (all levels)
- Git status snapshot
- Preloaded skills (full content)

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