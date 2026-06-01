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
| Bash | Inherit | All (Bash-focused) | Terminal operations with full tool access |
| statusline-setup | Sonnet | — | /statusline command |
| claude-code-guide | Haiku | — | Claude Code questions |

**Tool access column:**
- **Read-only**: Read, Glob, Grep, LS, WebSearch (no Write, Edit, Bash)
- **All**: Full tool access per settings
- **All (Bash-focused)**: Full tool access, optimized for terminal operations

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

Full tool access, optimized for terminal operations.

**Examples:**
- Running build commands (`npm run build`, `cargo build`)
- Executing test runners with output capture
- Package manager operations (npm install, pip install)
- Git operations requiring authentication context
- Long-running scripts where terminal output matters

Note: Unlike Explore/Plan, Bash agents do NOT skip CLAUDE.md — they load the full hierarchy.

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
| Read | Yes | Yes | Yes | Yes |
| Write | No | No | Yes | Yes |
| Edit | No | No | Yes | Yes |
| Bash | No | No | Per settings | Yes |
| Glob | Yes | Yes | Yes | Yes |
| Grep | Yes | Yes | Yes | Yes |
| LS | Yes | Yes | Yes | Yes |
| WebSearch | Yes | Yes | Yes | Yes |

**Security implications:**
- Explore/Plan types prevent accidental modifications
- General-purpose respects user permission settings
- Bash has full access but is focused on terminal workflows

### Tools NOT Available to Subagents

Subagents cannot access: Agent (no nested spawning), AskUserQuestion, EnterPlanMode, ExitPlanMode, ScheduleWakeup, CronCreate, CronDelete, CronList, NotebookEdit, Workflow. These are blocked from the subagent tool registry at the implementation level.

### Tool Restriction Semantics

Agent `tools:` is a hard allowlist — only listed tools are available, everything else is blocked. This is fundamentally different from skill `allowed-tools:` which only pre-approves tools without restricting availability.

| Mechanism | Scope | Effect |
|-----------|-------|--------|
| Agent `tools: ["Read", "Grep"]` | Subagent only | Can ONLY use Read and Grep. All other tools blocked (Strictly filtered from the tool registry; C1). |
| Skill `allowed-tools: Read, Grep` | Main conversation | Can use Read and Grep without prompts. Other tools still available per normal permissions. **Warning:** Live verification on v2.1.158 confirms this provides only partial enforcement; while `Write` is blocked, tools like `Edit`, `Agent`, and `Skill` bypass this restriction (C8). |
| Skill `disallowed-tools: Bash` | Main conversation | Bash is completely unavailable while skill is active. |

When choosing tool access for a custom agent, default to the minimum needed. Read-only agents get `["Read", "Grep", "Glob"]`. Implementation agents get the full set. Never grant more access than the agent's role requires.

---

## What Loads at Startup

### CLAUDE.md Inheritance

Not all subagents inherit CLAUDE.md the same way:
- **Explore/Plan**: Skip CLAUDE.md entirely — no instructions loaded
- **General-purpose/Bash**: Load the full hierarchy:
  1. User global: `~/.claude/CLAUDE.md`
  2. Rules: `~/.claude/rules/*.md`
  3. Project: `{project}/CLAUDE.md`
  4. Project rules: `{project}/.claude/rules/*.md`

Subagents do NOT inherit conversation history or parent session context.

### Model Resolution Order

Model is resolved in priority order:
1. `CLAUDE_CODE_SUBAGENT_MODEL` environment variable (highest)
2. Per-invocation `model` parameter in Agent tool call
3. `model` field in agent definition frontmatter
4. Parent session model (inherited default)

### Git Status

Subagents operate in the same working tree as the parent session. Git operations work normally with access to current repository state. Authentication context is inherited from the parent session.

---

## Fork Mode

Fork mode (`CLAUDE_CODE_FORK_SUBAGENT=1`, v2.1.117+) lets a subagent inherit the full conversation history from the parent session, rather than starting cold. This is distinct from normal subagent spawning where context starts fresh.

Fork mode is experimental and should be used only when the subagent genuinely needs awareness of the full conversation state.

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