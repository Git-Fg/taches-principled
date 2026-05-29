---
description: Built-in agent types (Explore, Plan, General-purpose, Bash) and their use cases
when_to_read: When choosing agent types or understanding model/tool implications
path: ./official/agent-types.md
---

# Agent Types Reference

Source: [Claude Code Subagents Documentation](https://code.claude.com/docs/en/sub-agents.md)

---

## Built-in Agent Types

| Agent | Model | Tools | Purpose |
|-------|-------|-------|---------|
| Explore | Haiku | Read-only | Fast codebase exploration |
| Plan | Inherit | Read-only | Plan mode research |
| general-purpose | Inherit | All | Complex read/write tasks |
| Bash | Inherit | Bash only | Terminal isolation |
| statusline-setup | Sonnet | — | /statusline command |
| claude-code-guide | Haiku | — | Claude Code questions |

**Model column meaning:**
- **Haiku/Inherit/Sonnet**: Specific model or inherits from parent session
- **Read-only**: Read, Glob, Grep, LS, WebSearch (no Write, Edit, Bash)
- **All**: Full tool access per settings
- **Bash only**: Bash tool only, isolated from file operations

---

## When to Use Each Type

### Explore Agent

Fast, read-only codebase investigation.

**Examples:**
- Mapping directory structure and file organization
- Finding patterns across multiple files (searching for function usage)
- Reading documentation to understand existing patterns
- Discovering which files implement a specific feature
- Quick grep-based audits without modifications

### Plan Agent

Research phase of planning workflows. Read-only for investigation.

**Examples:**
- Investigating dependencies and architecture before planning
- Researching similar implementations for reference
- Exploring external APIs or libraries being considered
- Gathering context about existing patterns before design
- Background research for feature planning

### General-Purpose Agent

Complex tasks requiring full tool access.

**Examples:**
- Implementing feature changes across multiple files
- Running test suites and fixing failures
- Refactoring with confidence (can verify and iterate)
- Building new components with verification
- Multi-step workflows requiring read/write/execute

### Bash Agent

Isolated command execution without file access.

**Examples:**
- Running build commands (`npm run build`, `cargo build`)
- Executing test runners with output capture
- Package manager operations (npm install, pip install)
- Git operations requiring authentication context
- Long-running scripts where terminal output matters

---

## Model Implications

| Model | Cost | Latency | Override When |
|-------|------|---------|---------------|
| Haiku | Low | Fast | Fast exploration, read-only tasks, quick audits |
| Sonnet | Medium | Medium | Complex reasoning, multi-file changes, planning |
| Opus | High | Slower | Very complex multi-step reasoning, architectural decisions |
| Inherit | Parent's model | Parent's speed | Default for most tasks — use when no specific capability needed |

**Guidelines:**
- Default to Haiku for read-only exploration and research
- Use Inherit (general-purpose) for tasks requiring reasoning beyond Haiku's capacity
- Override with Sonnet when the task involves complex decision-making
- Reserve Opus for architectural decisions or multi-phase reasoning

---

## Built-in vs Custom Agents

| Criteria | Built-in Agents | Custom Agents |
|----------|-----------------|---------------|
| Scope | Generic capabilities | Domain-specific roles |
| Definition | Claude Code provides | Defined in `.claude/agents/` |
| Auto-discovery | Yes | Yes (when in agents/ directory) |
| Custom system prompt | No | Yes |
| Skill pre-loading | Per agent type | Configurable in definition |
| Use for | Common patterns | Specialized behavior |

**When to use built-in:**
- Fast exploration, simple read-only research
- Terminal isolation with Bash
- Standard orchestration without special role

**When to create custom:**
- Domain-specific evaluation criteria (critic, grader)
- Pre-loaded skill for specialized methodology
- Consistent team role across multiple tasks

---

## Fork vs Named Agents

| Aspect | `context: fork` | Named Agent |
|--------|-----------------|-------------|
| System prompt | Agent definition body + CLAUDE.md | Full agent definition |
| Skills | None (unless `skills:` field) | Configurable per definition |
| CLAUDE.md | Inherited from parent session | Inherited from parent session |
| Use case | Quick task-specific prompts | Reusable role templates |

**When to use `context: fork`:**
- One-off task with specific instructions
- Minimal overhead for simple tasks
- Ad-hoc subagent for immediate feedback

**When to use named agent:**
- Repeated execution of same role
- Domain-specific evaluation criteria
- Skills pre-loading for methodology
- Team patterns (critic, reviewer, verifier)

---

## Tool Access by Type

| Tool | Explore | Plan | General-Purpose | Bash |
|------|---------|------|------------------|------|
| Read | Yes | Yes | Yes | No |
| Write | No | No | Yes | No |
| Edit | No | No | Yes | No |
| Bash | No | No | Per settings | Yes |
| Glob | Yes | Yes | Yes | No |
| Grep | Yes | Yes | Yes | No |
| LS | Yes | Yes | Yes | No |
| WebSearch | Yes | Yes | Yes | No |

**Security implications:**
- Explore/Plan types prevent accidental modifications
- Bash-only isolation prevents file tampering
- General-purpose respects user permission settings

---

## What Loads at Startup

### CLAUDE.md Inheritance

All subagents inherit the full CLAUDE.md hierarchy:
1. User global: `~/.claude/CLAUDE.md`
2. Rules: `~/.claude/rules/*.md`
3. Project: `{project}/CLAUDE.md`
4. Project rules: `{project}/.claude/rules/*.md`

Subagents do NOT inherit conversation history or parent session context.

### Git Status

Subagents operate in the same working tree as the parent session. Git operations work normally with access to current repository state. Authentication context is inherited from the parent session.

---

## Spawn Vocabulary

| Pattern | Usage |
|---------|-------|
| `spawn a [role] subagent` | Primary pattern for creating subagents |
| `spawn an explorer subagent` | Read-only investigation |
| `spawn a general-purpose subagent` | Full tool access tasks |
| `spawn a Bash subagent` | Terminal isolation |
| `dispatch` | Deprecated — avoid in new documentation |
| `launch` | Deprecated — avoid in new documentation |

**Canonical form:** Always pair "spawn" with role designation:
- Spawn an explorer subagent
- Spawn a critic subagent
- Spawn a verification subagent

**Avoid:** "spawn critic" (missing subagent designation) or "launch an agent" (vague, no role).

---

## Quick Reference

```markdown
# Spawn patterns by use case

# Fast read-only exploration
spawn an explorer subagent with file-deletion investigation

# Complex implementation
spawn a general-purpose subagent for multi-file refactoring

# Isolated commands
spawn a Bash subagent to run test suite

# Domain-specific evaluation
spawn a critic subagent for code review
```