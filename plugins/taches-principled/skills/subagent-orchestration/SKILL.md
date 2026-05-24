---
name: subagent-orchestration
description: "Spawn parallel subagents for multi-perspective research, review, and delegated exploration. Orchestrator owns all cognition; subagents own only execution. Not for single-step inline tasks."
argument-hint: [task description]
when_to_use: |
  Use when the user says:
  - "delegate this"
  - "run in parallel"
  - "spawn agents"
  - "use subagents"
  - "investigate with agents"
  - "orchestrate workers"
  - "spawn multiple agents for X"
  - "run these tasks concurrently"
  - "parallelize this work"
  - "I need three agents to tackle X, Y, and Z"
  - "let me spin up some workers for this research"
  IMMEDIATELY when a task spans multiple files or requires independent execution streams.
  Do NOT use for simple single-step tasks or when Claude is already acting as orchestrator without explicit request.
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

## Explorer Subagent Protocol

When spawning subagents for investigation/research/exploration:

### Before Spawning
1. Read existing scratchpad: `.principled/scratch/{topic}.md`
2. Write current questions and context to that scratchpad
3. Include explicit instruction for subagent to UPDATE the scratchpad

### Tool Requirements (NON-OPTIONAL)
- **NEVER** use "native" Explore subagents (Haiku, read-only) for investigation
- **REQUIRED** role: subagent must read source, write findings, search patterns, list directories, and run commands
- Write access is **NON-OPTIONAL** — findings must be persisted to scratchpad

### After Subagents Return
1. Read scratchpad BEFORE synthesizing
2. Merge findings into working context
3. Update scratchpad with synthesis conclusions

**Why:** The telephone game degrades quality by ~50% when orchestrators synthesize without source access. Direct scratchpad access eliminates paraphrase drift.

## Orchestrator Pre-Commit Checklist

Before spawning any subagent, validate:

- [ ] Task is >5 minutes inline work (never delegate trivial tasks)
- [ ] Scope is unambiguous (single file ownership or file-disjoint decomposition)
- [ ] Success criteria are explicit (output format + coverage rule defined)
- [ ] Rollback command is documented (one-command revert for each spawned agent)
- [ ] Failure signal JSON schema is included in prompt
- [ ] Subagent has REQUIRED Write tool access (never spawn read-only for investigation)
- [ ] Scratchpad path is defined (`.principled/scratch/{topic}.md`)
- [ ] Subagent instructed to update scratchpad before returning
- [ ] Orchestrator will read scratchpad before synthesizing (telephone game prevention)
- [ ] No overlapping file ownership between parallel agents
- [ ] Context is minimal high-signal (no speculative background)
- [ ] Iteration limit set (stop after 2 retries, never loop silently)

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

## Rollback
[One-command revert — what to undo if this fails]

## Failure Signal
[Required JSON schema — see below]

## Approach
[Numbered step-by-step methodology]
```

**Key principles:**
- **Positive framing** — tell agents what to do, not what to avoid
- **Minimal high-signal context** — context is currency; every token competes for attention
- **Explicit scope** — define files owned and files forbidden
- **Coverage rule** — specify over-report or curated results

### Failure Signal Schema

Every subagent must return structured JSON on completion:

```json
{"status": "failed" | "success", "reason": "...", "completed_portion": "...", "retry_possible": true/false}
```

Do not guess or produce partial output without flagging it.

### Buffering Gotcha

When using `grep` in pipes for Monitor, **ALWAYS** use `--line-buffered`:

```bash
tail -f app.log | grep --line-buffered "ERROR"
```

**Why:** Unix pipe buffering delays output by minutes. `--line-buffered` forces grep to flush each match immediately. Without it, your monitor may never see events that arrived during the delay window.

## Five Parallel Patterns

See the orchestration patterns reference for full patterns and use-case examples.

| Pattern | When to use |
|---------|-------------|
| **Horizontal Split** | Split research by dimension (security, perf, style) |
| **Vertical Slice** | Split implementation by layer (frontend, backend, tests) |
| **Pipeline** | Sequential dependencies (research then implement) |
| **Contest** | Unknown root cause — test competing hypotheses |
| **Aggregator Fan-out/Fan-in** | N parallel workers → 1 aggregator synthesizes |

### Inspiration Use Cases

1. **Parallel Code Review** — Horizontal split by concern (security, perf, style)
   ```
   Lead → @security "Audit auth/ for vulnerabilities"
        → @perf "Analyze db queries for N+1"
        → @style "Check code style violations"
   ```

2. **Bug Investigation with Competing Theories** — Contest pattern for unknown root cause
   ```
   Lead → @theory-A "Test: race condition in async handler"
        → @theory-B "Test: memory leak in connection pool"
        → @theory-C "Test: deadlocks in goroutine scheduler"
   ```

3. **Multi-Domain Migration** — Vertical slice by layer (data, API, UI)
   ```
   Lead → @service-A "Migrate auth/, own files: auth/*"
        → @service-B "Migrate user/, own files: user/*"
        → @service-C "Migrate order/, own files: order/*"
   ```

4. **Library Evaluation** — Pipeline (research → compare → recommend)
   ```
   Lead → @researcher "Research X alternatives → /tmp/research.json"
   [lead waits, then:]
   └── @implementer "Implement using /tmp/research.json"
   ```

5. **Architecture Review** — Fan-out by subsystem, fan-in for decision
   ```
   Lead → @data-arch "Review data layer: schemas, queries, indexes"
        → @api-arch "Review API layer: endpoints, auth, rate limits"
        → @infra-arch "Review infra: deployment, scaling, monitoring"
   [lead synthesizes: unified recommendations]
   ```

6. **Test Coverage Expansion** — Parallel workers by module, aggregator merges
   ```
   Lead → @unit-tests "Generate tests for src/models/"
        → @unit-tests "Generate tests for src/services/"
        → @unit-tests "Generate tests for src/api/"
   [lead merges: dedupe → combined suite]
   ```

7. **Documentation Audit** — Parallel readers across doc sections
   ```
   Lead → @docs-review "Audit docs/api/ for completeness"
        → @docs-review "Audit docs/guides/ for accuracy"
        → @docs-review "Audit docs/reference/ for consistency"
   ```

8. **Dependency Audit** — Contest (safe vs unsafe upgrade paths)
   ```
   Lead → @safe-upgrade "Test upgrade path: minor versions only"
        → @risky-upgrade "Test upgrade path: major versions with deprecations"
   ```

9. **Performance Profiling** — Horizontal split (CPU, memory, network)
   ```
   Lead → @perf-cpu "Profile CPU usage in src/"
        → @perf-memory "Profile memory allocations"
        → @perf-network "Profile network call latency"
   ```

10. **Refactoring Safety Check** — Fan-out by risk level, aggregator synthesizes
    ```
    Lead → @safe-refactor "Refactor low-risk: utils, helpers"
         → @risky-refactor "Refactor high-risk: core business logic"
    [lead synthesizes: migration plan with risk assessment]
    ```

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

## Delegation Guardrails

### Never Do These
- Delegate <5 min inline tasks
- Spawn read-only agents for investigation (Write is REQUIRED)
- Skip success criteria in spawn prompts
- Omit rollback commands
- Forget iteration limits (stop after 2 retries)
- Assume completion without validation

### Never Delegate These
- Single-context-window tasks
- Tasks requiring conversation memory between steps
- Work requiring real-time synthesis during execution
- Decisions where downstream judgment depends on upstream reasoning
- File edits that require understanding orchestrator's broader context

