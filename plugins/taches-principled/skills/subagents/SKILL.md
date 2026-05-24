---
name: subagents
description: "Design and orchestrate Claude Code subagent systems. Use when designing multi-agent architectures (supervisor, swarm, hierarchical patterns) or orchestrating parallel execution (fan-out workers, coordinate agents, spawn subagents for tasks)."
when_to_use: |
  DESIGN mode when the user says "create an agent", "design subagents", "build an agent architecture", "set up automated subagents", "make me an agent for X", or "configure agent hierarchy".
  ORCHESTRATE mode when the user says "delegate this", "run in parallel", "spawn agents", "use subagents", "orchestrate workers", "fan out workers", "coordinate agents", "parallelize this work", or "spawn multiple agents for X".
  Do NOT use for single-step inline tasks, general help, or when direct conversation is faster.
argument-hint: [task or role description]
---

# Subagents Hub

Two modes for subagent work: designing new agent architectures (DESIGN) or orchestrating existing agents (ORCHESTRATE).

## Decision Router

| Situation | Mode |
|-----------|------|
| Creating new subagent definitions | DESIGN |
| Choosing orchestration pattern | DESIGN |
| Spawning agents in parallel | ORCHESTRATE |
| Writing spawn prompts | ORCHESTRATE |
| Multi-agent failure analysis | ORCHESTRATE |
| Token cost budgeting | ORCHESTRATE |

---

# DESIGN Mode

Create specialized subagent definitions with expert guidance.

## What Subagents Are

Subagents enable delegation to specialized agents that operate autonomously, returning final output to the main conversation. They are black boxes that cannot interact with users.

| Can Do | Cannot Do |
|--------|-----------|
| Use tools matching role needs | Use AskUserQuestion |
| Access MCP servers | Present options or wait for input |
| Read source, write findings | Show intermediate steps to user |

## Policy vs. Mechanism

| Concept | Definition | Location |
|---------|-----------|----------|
| **Policy** | When to spawn vs. inline (delegation strategy) | Orchestrator judgment |
| **Mechanism** | How to construct prompts, scope files, define success criteria | Spawn prompts |

## Quick Start

1. Run `/agents` command
2. Select "Create New Agent"
3. Choose scope: project (`.claude/agents/`), user (`~/.claude/agents/`), or plugin
4. Define frontmatter: name, description, tools (by capability), model
5. Write system prompt (3-5 lines, not a manual)

## Frontmatter Fields

```yaml
---
name: subagent-name          # Lowercase/hyphens, unique
description: Purpose and triggers
tools: Describe by role       # What must be accomplished
model: sonnet/haiku/opus/inherit
---
```

### Field Details

**name:** Lowercase letters and hyphens only.

**description:** Natural language with trigger keywords for auto-discovery.

**tools:** Describe by role, not tool name. Omit for full access.

**model:** Sonnet for reasoning, Haiku for execution, Opus for high-stakes, inherit for same as main.

**Plugin scope gotcha:** Plugin subagents ignore `hooks`, `mcpServers`, `permissionMode` frontmatter fields. Copy to project/user scope if needed.

### Additional Fields

| Field | Purpose |
|-------|---------|
| `skills:` | Preload skills at startup |
| `memory:` | Persistent scope (user/project/local) |
| `background:` | Run as background task |
| `maxTurns:` | Guard against runaway agents |
| `isolation:` | Set `worktree` for git worktree isolation |

## Memory Scope Decision

| Scope | Location | Git | Use when |
|-------|----------|-----|----------|
| `project` | `.claude/agent-memory/` | Committed | Team-shared patterns |
| `user` | `~/.claude/agent-memory/` | Not committed | Universal patterns |
| `local` | `.claude/agent-memory.local/` | Gitignored | Sensitive findings |

## Model Selection

| Model | Best For |
|-------|----------|
| Sonnet | Complex reasoning, planning, validation |
| Haiku | Fast execution, bulk processing |
| Opus | Highest-stakes decisions |

### Numeric Thresholds

| Metric | Limit | Why |
|--------|-------|-----|
| Tools per agent | 7 max | Miller's number |
| Spawn prompt | 1500 tokens max | Quality degradation |
| Files per agent | 10 max | Scope creep = quality loss |
| Concurrent workers | 3-5 max | Supervisor saturation |

**Split signal:** Task needs >10 files or >7 tools or >1500 tokens context — decompose first.

**Worker cap:** Add second-tier supervisor rather than overloading one.

## Body Prompt Philosophy

**Rule:** If writing >30 lines of body content, you're duplicating a skill.

| Good Body | Bad Body |
|-----------|----------|
| 3-5 lines | 30+ lines duplicating a skill |
| Role + guardrails | Step-by-step instructions |
| Constraints + output format | Detailed field specs |

## Design Anti-Patterns

| Anti-Pattern | Problem | Fix |
|--------------|---------|-----|
| Tool restriction at birth | Silent failures | Start with full access |
| Too generic | No specialization | Define specific expertise |
| No workflow | May skip steps | Add structured approach |
| Requires user interaction | Subagents cannot | Move to main chat |
| Vague spawn prompt | No scope | Define success criteria |

---

# ORCHESTRATE Mode

Orchestrate multiple subagents in parallel with validation loops.

## Core Mental Model

Four rules governing every delegation:

1. **Analyze before delegating** — understand the full task graph
2. **Assign unambiguous scope** — exclusive file ownership per agent
3. **Validate before integrating** — run success criteria, never assume
4. **Persist state to disk** — subagents don't share conversation memory

## Pre-Spawn Checklist

- [ ] Task >5 minutes inline (never delegate trivial tasks)
- [ ] Scope unambiguous (file-disjoint decomposition)
- [ ] Success criteria explicit (output format + coverage rule)
- [ ] Rollback documented (one-command revert)
- [ ] Write tool access required (never read-only for investigation)
- [ ] Scratchpad defined (`.principled/scratch/{topic}.md`)
- [ ] No overlapping file ownership between parallel agents
- [ ] Iteration limit set (stop after 2 retries)
- [ ] Context minimal high-signal (no speculative background)

## Explorer Subagent Protocol

When spawning for investigation/research:

### Before Spawning
1. Read existing scratchpad: `.principled/scratch/{topic}.md`
2. Write current questions and context
3. Include explicit instruction to UPDATE scratchpad

### Tool Requirements (NON-OPTIONAL)
- **NEVER** use Explore subagents (Haiku, read-only) for investigation
- **REQUIRED:** Read source, write findings, search patterns, run commands
- Write access is NON-OPTIONAL — findings must persist

### After Subagents Return
1. Read scratchpad BEFORE synthesizing
2. Merge findings into working context
3. Update scratchpad with synthesis conclusions

**Why:** The telephone game degrades quality ~50% without source access.

## RACE Framework

Structure every spawn prompt:

```
## Role
[What this agent is and its expertise]

## Action
[Concrete, scoped task — imperative form, one objective]

## Context
[What orchestrator did; file ownership boundaries]

## Expectation
[Output format/schema; success criteria; coverage rule]

## Rollback
[One-command revert]

## Failure Signal
[Required JSON: {"status": "success/failed", "reason": "...", "retry_possible": bool}]
```

**Key principles:**
- **Positive framing** — tell agents what to do
- **Minimal context** — tokens compete for attention
- **Explicit scope** — files owned and forbidden
- **Coverage rule** — specify over-report or curated results

### Failure Signal Schema

Every subagent must return:

```json
{"status": "success" | "failed", "reason": "...", "completed_portion": "...", "retry_possible": true/false}
```

Never guess or produce partial output without flagging.

## Parallel Patterns

| Pattern | Use when |
|---------|---------|
| **Horizontal Split** | Split by dimension (security, perf, style) |
| **Vertical Slice** | Split by layer (frontend, backend, tests) |
| **Pipeline** | Sequential dependencies (research then implement) |
| **Contest** | Unknown root cause — test competing hypotheses |
| **Fan-out/Fan-in** | N workers → 1 aggregator synthesizes |

### Pattern Examples

**Parallel Review:**
```
Lead → @security "Audit auth/ for vulnerabilities"
     → @perf "Analyze db queries for N+1"
     → @style "Check code style violations"
```

**Bug Investigation:**
```
Lead → @theory-A "Test: race condition"
     → @theory-B "Test: memory leak"
     → @theory-C "Test: deadlocks"
```

**Multi-Domain Migration:**
```
Lead → @service-A "Migrate auth/, own: auth/*"
     → @service-B "Migrate user/, own: user/*"
     → @service-C "Migrate order/, own: order/*"
```

**Architecture Review:**
```
Lead → @data-arch "Review data layer"
     → @api-arch "Review API layer"
     → @infra-arch "Review infra"
[lead synthesizes: unified recommendations]
```

## Self-Review Loop

After implementing, run maker-checker:

```
Orchestrator → Implement → Spawn reviewer (read-only) → [pass] → integrate
                                          ↓ [fail]
                                     Fix → Respawn → ...
```

Reviewer reports ALL findings. Downstream filter ranks severity.

## Automation Layers

| Tool | Trigger | Best for |
|------|---------|----------|
| Hooks | Tool events | Validate subagent outputs |
| ScheduleWakeup / CronCreate | Time | Recurring orchestration |
| Monitor | External events | Real-time CI/log watching |

**Never poll when you can watch.** Zero cost while silent.

### Buffering Gotcha

When using `grep` in pipes for Monitor, **ALWAYS** use `--line-buffered`:

```bash
tail -f app.log | grep --line-buffered "ERROR"
```

Without `--line-buffered`, output delays by minutes.

## Memory Architecture

| Layer | Mechanism | Persistence |
|-------|-----------|-------------|
| CLAUDE.md | Human-authored, loaded every session | Global/Project |
| MEMORY.md | Learned during sessions | Project |
| Subagent Memory | `memory:` frontmatter | Agent-scoped |

**State persistence:**
- Survive compaction → CLAUDE.md or disk artifact
- Survive session end → orchestrator disk or subagent memory
- Shared between agents → orchestrator-owned disk artifact

## Failure Modes

| Failure Mode | Detection | Recovery Cost | Prevention |
|--------------|-----------|---------------|------------|
| Over-delegation | Obvious | Low | Inline for <5min tasks |
| Context leakage | Silent | High | Non-semantic names |
| Tool permission misconfig | Immediate | Medium | YAML validation |
| State management failures | Silent corruption | High | Schema validation |
| Blocking anti-patterns | Appears productive | Very high | Hard iteration limits |
| File conflicts | Git conflicts | Medium | Worktree isolation |

**Key rule:** Stop and report after 2 retries. Never loop silently.

## Reference Index

See the design references for:
- Writing subagent prompts
- Anti-patterns catalog
- Configuration details

See the orchestration references for:
- Orchestration core patterns
- Failure mode details
- Memory architecture
- Gotchas from production
- Automation layers