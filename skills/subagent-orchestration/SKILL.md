---
name: subagent-orchestration
description: "Orchestrate parallel subagents for delegated investigation, self-review, and iterative loops. Use when user says 'delegate', 'run in parallel', 'spawn agents', 'use subagents', 'background', 'investigate with agents', 'orchestrate workers', 'monitor in background', or 'task list'."
when_to_use: |
  Do NOT use for simple single-step tasks or when Claude is already acting as orchestrator without explicit delegation request.
---

# Subagent Orchestration

Orchestrate multiple subagents in parallel, self-review work, iterate with feedback loops, and manage background workers. The orchestrator owns all cognition; subagents own only execution.

## Decision Router

| Situation | Action |
|-----------|--------|
| Single-step, <5 min inline | Do it yourself |
| Multi-file, independent streams | Spawn parallel subagents |
| Sequential dependencies | Pipeline (research → implement) |
| Unknown root cause | Contest pattern |
| Need verification before commit | Maker-checker loop |
| Long-running external process | Monitor or ScheduleWakeup |

## Core Mental Model

Four rules that govern every delegation decision:

1. **Analyze before delegating** — understand the full task graph first
2. **Assign unambiguous scope** — each subagent gets exclusive file ownership
3. **Validate before integrating** — run success criteria, never assume
4. **Persist state to disk** — subagents don't share conversation memory

## Cost-Capability Spectrum

Match the agent type to the task complexity:

| Type | Model | Context | Cost | Use when |
|------|-------|---------|------|----------|
| `Bash` | — | Shell only | Lowest | Git ops, build commands, script execution |
| `Explore` | Haiku | Fresh, read-only | Lowest | Codebase discovery, targeted lookups |
| `Plan` | Sonnet | Fresh, read-only | Low | Architecture analysis, implementation planning |
| `general-purpose` | Inherit | Fresh, configurable | Medium | Custom workflows, complex orchestration |

**Rule:** Never spawn a subagent for a task that fits in a single context window and would take less than 5 minutes inline.

## RACE Framework

Structure every spawn prompt with RACE — see the RACE framework reference for full details.

```
## Role
[What this agent is and what expertise it brings]

## Action
[Concrete, scoped task — imperative form, one clear objective]

## Context
[What the orchestrator has done; what this agent should do next; file ownership boundaries]

## Expectation
[Output format/schema; success criteria; coverage rule]
```

**Key principles:**
- **Positive framing** — tell agents what to do, not what to avoid
- **Minimal high-signal context** — context is currency; every token competes for attention
- **Explicit scope** — define files owned and files forbidden
- **Coverage rule** — specify over-report or curated results

## Five Parallel Patterns

See the orchestration patterns reference for full patterns and use-case examples.

| Pattern | When to use |
|---------|-------------|
| **Horizontal Split** | Split research by dimension (security, perf, style) |
| **Vertical Slice** | Split implementation by layer (frontend, backend, tests) |
| **Pipeline** | Sequential dependencies (research then implement) |
| **Contest** | Unknown root cause — test competing hypotheses |
| **Aggregator Fan-out/Fan-in** | N parallel workers → 1 aggregator synthesizes |

## Self-Review Loop

After implementing a solution, run a maker-checker loop:

```
Orchestrator → Implement → Spawn reviewer (read-only) → [pass] → integrate
                                          ↓ [fail, specific feedback]
                                     Fix → Respawn reviewer → ...
```

The reviewer must report ALL findings including low-confidence ones. A downstream filter ranks severity — don't ask the reviewer to make that judgment.

## Three Automation Layers

Choose by trigger type:

| Tool | Trigger | Best for |
|------|---------|----------|
| Hooks | Tool events | Validate subagent outputs, enforce guardrails |
| ScheduleWakeup / CronCreate | Time | Recurring orchestration, long-poll retries |
| Monitor | External events | Real-time CI/log watching, instant reaction |

**Never poll when you can watch.** ScheduleWakeup fires on a timer regardless of state. Monitor wakes only when output matches — zero cost while silent.

See the automation layers reference for detailed comparison.

## Memory Architecture

Claude Code implements a four-layer memory system:

| Layer | Mechanism | Persistence |
|-------|-----------|-------------|
| `CLAUDE.md` | Human-authored, loaded every session | Global/Project |
| `MEMORY.md` | Learned during sessions, auto-written | Project |
| Subagent Memory | `memory:` frontmatter per agent | Agent-scoped |

**State persistence rules:**
- Must survive compaction → CLAUDE.md or disk artifact
- Must survive session end → disk artifact (orchestrator) or agent-memory (subagent)
- Must be shared between subagents → orchestrator-owned disk artifact

See the memory architecture reference for full details.

## Failure Modes

| Failure Mode | Detection | Recovery Cost | Prevention |
|--------------|-----------|---------------|------------|
| **Over-delegation** | Obvious in hindsight | Low | Default to inline for <5min tasks |
| **Context leakage** | Silent, subtle | High | Non-semantic agent names; explicit subagent type |
| **Tool permission misconfig** | Immediate failure | Medium | Validate YAML; use allowlists |
| **State management failures** | Silent corruption | High | Schema validation at every tool boundary |
| **Blocking anti-patterns** | Appears productive | Very high | Hard iteration limits; don't race |
| **File conflicts** | Git conflicts visible | Medium | Worktree isolation; file-disjoint decomposition |

**Key rule:** Stop and report after 2 retries on the same failure. Never loop silently.

See the failure modes reference for detailed prevention strategies.

## Reference Index

This skill complements `create-subagents`. Key reference files (in the subagent authoring references directory):

- `race-framework.md` — Full RACE prompt structure
- `orchestration-patterns.md` — All five patterns with examples
- `automation-layers.md` — Monitor vs ScheduleWakeup vs Hooks
- `memory-architecture.md` — Four-layer system details
- `failure-modes.md` — Detection, recovery, and prevention
- `context-management.md` — Context hardening strategies
- `gotchas.md` — Common subagent pitfalls