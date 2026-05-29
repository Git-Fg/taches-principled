---
description: Agent tool parameters for spawning subagents at runtime
when_to_read: When invoking the Agent tool or overriding agent definitions at spawn time
path: ./official/agent-tool-params.md
---

# Agent Tool Parameters Reference

Source: [Claude Code Subagents Documentation](https://code.claude.com/docs/en/sub-agents.md)

## Overview

The `Agent` tool (formerly `Task` in v2.1.63+) invokes subagents at spawn time. Parameters control how the subagent executes, distinct from frontmatter in definition files which configure the agent's persistent behavior.

**Key distinction:** Frontmatter fields in `.claude/agents/*.md` define the agent's baseline configuration. Agent tool parameters override or extend those defaults at spawn time.

---

## All Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `subagent_type` | string | `general-purpose` | Built-in type (`explore`, `plan`, `general-purpose`, `bash`) or custom agent name |
| `description` | string | — | 3-5 word task summary shown in context display and task list |
| `prompt` | string | — | Detailed instructions for the subagent |
| `model` | string | `inherit` | Model override: `haiku`, `sonnet`, `opus`, or full model ID |
| `run_in_background` | boolean | `false` | Run concurrently without blocking main conversation |
| `isolation` | string | — | `worktree` creates isolated git copy for destructive operations |
| `max_turns` | number | — | Safety limit on agentic turns before auto-stop |
| `mode` | string | `default` | Permission mode: `default`, `acceptEdits`, `auto`, `dontAsk`, `bypassPermissions`, `plan` (corresponds to `permissionMode` in definition frontmatter) |
| `initialPrompt` | string | — | Auto-submitted as first user turn for the subagent |

---

## Spawn Prompt Pattern

Template for structured delegation prompts:

```
> Use [agent-type] to [task]
Context: [files, constraints, environment state]
Requirements: [outputs, quality gates, success criteria]
Return: [deliverable format, where to write results]

[Optional: Rollback plan for safety]
```

**Example:**
```
Use a haiku subagent to audit this skill for routing quality.
Context: {baseDir}/skills/diagnose/SKILL.md — frontmatter only
Requirements: Check description length, trigger phrases, CONTRAST sections
Return: JSON findings to .principled/scratch/skill-audit.json
```

---

## When to Use Each Parameter

### model Override

| Model | Use When | Avoid When |
|-------|----------|------------|
| `haiku` | Read-only exploration, fast audits, simple research | Complex reasoning, multi-step planning |
| `sonnet` | Implementation tasks, complex analysis, multi-file changes | Simple lookups, trivial verification |
| `opus` | Architectural decisions, multi-phase reasoning, strategy | Speed-critical tasks, simple commands |
| `inherit` | Default — uses parent's model | When specific capability needed |

**Override triggers:**
- Fast exploration → `haiku`
- Implementation → `sonnet` (default for general-purpose)
- Verification/critique → `haiku` (speed + read-only)
- Strategic planning → `sonnet` or `opus`

### run_in_background

| Scenario | Setting | Reason |
|----------|---------|--------|
| Long-running tests | `true` | Don't block main conversation |
| Multiple independent tasks | `true` | Parallel execution |
| Real-time collaboration | `false` | Need immediate feedback |
| Interactive debugging | `false` | Need conversation continuity |

**Note:** Background subagents auto-deny permission prompts.

### isolation

| Value | Behavior | Use Case |
|-------|----------|----------|
| `worktree` | Git worktree copy, auto-deleted on exit | Destructive refactors, branch experiments |
| — (none) | Operates in same working tree | Safe operations, read-only tasks |

**Example:**
```
isolation: worktree  # For "git reset --hard" type operations
```

### max_turns

| Limit | When to Set | Rationale |
|-------|-------------|-----------|
| 15 | Default safety | Prevents runaway agents |
| 5 | Simple tasks | Quick fixes, single-file edits |
| 30 | Complex workflows | Multi-phase implementation |
| 1 | Single turn only | One-shot commands |

**Rationale:** Prevents infinite loops or excessive spending. Default is unset (unlimited turns).

---

## Agent Tool vs Definition Frontmatter

| Parameter | Spawn-time (Agent tool) | Definition-time (frontmatter) |
|-----------|------------------------|-------------------------------|
| `subagent_type` | Override agent type | Set default agent |
| `model` | Per-spawn override | Set baseline model |
| `run_in_background` | One-shot toggle | Set default behavior |
| `max_turns` | Per-spawn safety | Set global limit |
| `mode` | Per-spawn permissions | Set default mode |
| `description` | Task-specific summary | Agent role description |
| `prompt` | Task instructions | — (definition uses `system`) |
| `isolation` | Per-spawn isolation | Set persistent isolation |

**Key insight:** Spawn parameters override definition defaults. Definition frontmatter provides the baseline; Agent tool parameters adjust per invocation.

---

## Model Override Examples

### Fast Audit (Haiku)

```
Agent tool: model=haiku
Use for: Code quality checks, routing validation, simple searches
```

### Implementation (Sonnet)

```
Agent tool: model=sonnet
Use for: Multi-file refactors, feature implementation, test writing
```

### Strategic Reasoning (Opus)

```
Agent tool: model=opus
Use for: Architecture decisions, multi-phase planning, complex trade-offs
```

### Default (Inherit)

```
Agent tool: model=inherit
Use for: Most tasks — inherits parent session model
```

**Decision tree:**

```
Task complexity?
├── Read-only / fast → haiku
├── Implementation / analysis → sonnet (default)
└── Strategic / architectural → opus

Task risk?
├── Destructive operation → isolation: worktree
└── Safe operation → no isolation
```

---

## Complete Example

```markdown
Agent tool invocation:
- subagent_type: general-purpose
- description: Multi-file refactor with verification
- model: sonnet
- run_in_background: false
- max_turns: 20
- isolation: worktree
- prompt: |
  > Use a sonnet subagent to refactor the auth module
  Context: src/auth/*.ts — current implementation
  Requirements:
    - Extract token validation to separate module
    - Preserve existing API surface
    - Run tests after each major change
  Return: Summary of changes with test results

Spawn-time overrides definition's defaults:
- Definition: model=haiku, max_turns=10
- Here: model=sonnet, max_turns=20
```

---

## Marketplace Conventions (Taches Principled)

### Default Safety Settings

For plugin-level spawns, always include:

```markdown
max_turns: 15    # Safety limit
```

### Background Pattern

For parallel independent tasks:

```markdown
# Spawn multiple in parallel, all background
Agent tool (1): run_in_background=true, description="Audit skill routing"
Agent tool (2): run_in_background=true, description="Check format compliance"
Agent tool (3): run_in_background=true, description="Validate descriptions"

# Main conversation waits for results, aggregates findings
```

### Isolation for Destructive Work

When spawning for git reset, branch operations, or destructive refactors:

```markdown
isolation: worktree
```

The worktree is auto-cleaned on subagent exit.