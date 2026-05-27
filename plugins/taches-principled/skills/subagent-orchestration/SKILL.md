---
name: subagents
description: "Implement multi-agent orchestration — spawn parallel workers, fan out tasks, coordinate subagents, or manage background agents. Use when delegating work, running in parallel, or orchestrating agent teams."
when_to_use: |
  Do NOT use for single-agent tasks, simple scripts, or non-agent workflows.
---

# Subagents

Design multi-agent architectures and orchestrate parallel execution. Hub skill combining agent definition authoring (DESIGN) and subagent execution (ORCHESTRATE).

## Decision Router

**DESIGN mode** — Agent definition authoring:
When user wants to create, define, or configure a new subagent definition — write its scope, tools/models/memory settings, or generate an agent template.

**ORCHESTRATE mode** — Subagent execution:
When user wants to delegate work, spawn workers, run in parallel, fan out tasks, or manage background agents — load ORCHESTRATE mode.

---

## DESIGN Mode

Create and configure Claude Code subagent definitions. Produces complete agent files ready to use.

### Agent Scopes Principle

Agents exist at five scopes with priority: Managed (org-wide, highest), Session (CLI flag), Project, User, Plugin (lowest). Project scope for workspace-specific agents; User scope for cross-project personal agents.

### Core Loop Principle

1. Determine scope based on agent's intended use
2. Identify purpose and required capabilities
3. Configure skills, memory, isolation (omit tools/model/effort by default)
4. Generate the agent file
5. Validate structure and field values

### Frontmatter Fields

| Field | Type | Description |
|-------|------|-------------|
| `name` | string | Unique identifier. Lowercase letters and hyphens only. Required. |
| `description` | string | When Claude should delegate to this subagent. Required. |
| `tools` | list[string] | Tools the subagent can use. Allowlist. |
| `disallowedTools` | list[string] | Tools to remove from inherited list |
| `model` | string | `sonnet`, `opus`, `haiku`, full model ID, or `inherit` |
| `permissionMode` | string | `default`, `acceptEdits`, `auto`, `dontAsk`, `bypassPermissions`, `plan` |
| `maxTurns` | integer | Max agentic turns before subagent stops |
| `skills` | list[string] | Skills to preload (full content injected at startup) |
| `mcpServers` | map | MCP servers scoped to this subagent |
| `hooks` | map | Lifecycle hooks scoped to this subagent |
| `memory` | string | Persistent memory scope: `user`, `project`, or `local` |
| `background` | boolean | `true` = always run as background task |
| `effort` | string | Effort level: `low`, `medium`, `high`, `xhigh`, `max` |
| `isolation` | string | `worktree` = run in temporary git worktree |
| `color` | string | Display color: `red`, `blue`, `green`, `yellow`, `purple`, `orange`, `pink`, `cyan` |
| `initialPrompt` | string | Auto-submitted as first user turn |

### Tool Restriction — Iterative Refinement Principle

Start with no tool restrictions. Omit both `tools` and `disallowedTools` from the initial definition. Ship it, verify it works, then restrict only if a specific tool causes problems. Premature restriction is the most common cause of silent agent failures.

### Model & Effort Principle

Never set `model` or `effort` unless explicitly requested. Both default to `inherit` — correct for 95% of agents. Setting them prematurely locks the agent to a configuration that may be wrong.

### Skills Preloading Principle

Subagents do not inherit skills from the parent — list them explicitly. The `skills` field injects full SKILL.md content at startup. Missing or disabled skills are silently skipped.

### Memory Architecture Principle

Enable memory on every subagent by default. `project` scope for team-shared knowledge; `user` scope for cross-project expertise; `local` scope for sensitive output (gitignored).

### Body Prompt Philosophy

Keep the markdown body general and concise — a short role statement and behavioral guardrails. If writing more than ~30 lines, you're duplicating a skill. Reference it in the `skills` field instead.

### Routing Principle

The `description` field is the routing oracle — write it like a trigger rule with specific conditions, not capability lists.

### File Templates

See {baseDir}/references/agent-templates.md for reusable agent templates (Researcher, Analyst, Monitor, Explorer).

### Fork Mode Principle

Fork mode creates a subagent that inherits the full conversation context and shares the parent's prompt cache. Use when the subagent needs to understand the full conversation or reference earlier decisions. Do not use for independent tasks or parallel workstreams.

---

## ORCHESTRATE Mode

Orchestrate multiple subagents in parallel, loop critic subagent until no HIGH findings, iterate with feedback loops, and manage background workers.

### Core Mental Model

Four rules govern every delegation decision:

1. **Analyze before delegating** — understand the full task graph first
2. **Assign unambiguous scope** — each subagent gets exclusive file ownership
3. **Validate before integrating** — run success criteria, never assume
4. **Persist state to disk** — subagents don't share conversation memory

### Cost-Capability Spectrum

| Type | Model | Best for |
|------|-------|----------|
| `Bash` | — | Git ops, build commands, script execution |
| `Explore` | Haiku | Codebase discovery, targeted lookups |
| `Plan` | Sonnet | Architecture analysis, implementation planning |
| `general-purpose` | Inherit | Custom workflows, complex orchestration |

### Delegation Protocol

#### Decompose

Break the task into independent workstreams. Each stream must:
- Own its file set exclusively (no overlapping edits)
- Have a clear deliverable (file path + format)
- Have passing success criteria (test, lint, type-check)
- Have a one-command rollback

#### Context Harden (RACE Framework)

Structure every spawn prompt with RACE:
```
## Role: [What this agent is and what expertise it brings]
## Action: [Concrete, scoped task — imperative form, one clear objective]
## Context: [What the orchestrator has done; what this agent should do next; file ownership boundaries]
## Expectation: [Output format/schema; success criteria; coverage rule]
```

Key constraints: Positive framing (tell agents what to do), minimal high-signal context, explicit scope boundaries, coverage rule (comprehensive vs curated).

**Failure signal:** Return structured JSON with status, reason, completed_portion, retry_possible.

#### Spawn and Collect

Spawn with appropriate model/tools/background. Use TaskGet for mid-flight inspection, TaskOutput for reading results, SendMessage to resume background agents.

#### Synthesize

Cross-domain consistency check + full integration test before presenting results.

### Self-Review Loop

Implement → Spawn reviewer (read-only) → [pass] → integrate → [fail] → Fix → Respawn reviewer

The reviewer must report ALL findings including low-confidence ones. A downstream filter ranks severity.

### Parallel Patterns

**Horizontal Split** — Investigation streams run in parallel (security, perf, style). Not for shared dependencies.

**Vertical Slice** — Each team owns their service end-to-end (frontend, backend, tests). Not for features requiring mid-implementation coordination.

**Pipeline** — Chained execution where one stage must complete before the next. Not for parallelizable work.

**Contest** — Competing hypotheses tested simultaneously. Not when one hypothesis is already strongly supported.

**Fan-out/Fan-in** — N parallel subagents then 1 aggregator. Only justified when N > 5 or synthesis requires cross-domain reasoning.

### Background Subagents

Spawn with `background: true` when the orchestrator can proceed without the result. Use for long-running tasks (monitoring, polling) or parallel independent workstreams.

### Iteration Principle

After 2 retries on the same failure: stop, report back with findings. Never loop silently.

### Three Automation Layers

| Tool | Best for |
|------|----------|
| Hooks | Validate subagent outputs, enforce guardrails |
| ScheduleWakeup / CronCreate | Recurring orchestration, long-poll retries |
| Monitor | CI/log watching, real-time reaction |

Never poll when you can watch. Monitor fires only on matching output (free while silent). ScheduleWakeup fires every N seconds regardless of state.

### Anti-Patterns

Never:
- Spawn subagents that edit overlapping files — git conflicts
- Delegate without success criteria — unverifiable failure
- Assume subagent completed without validation — silent failures
- Let orchestrator implement while waiting — deadlock
- Skip rollback plan — broken state with no recovery
- Use RACE for one-liner tasks — coordination overhead exceeds benefit
- Negative framing — prefer positive framing ("do A instead")

Never delegate:
- Destructive operations without explicit approval
- Tasks requiring conversation history
- Simple single-step tasks
- Overlapping file scopes

### Reference: Orchestration Use Cases

| Scenario | Pattern | Why |
|----------|---------|-----|
| PR with multi-file changes | Horizontal Split | Independent analysis streams |
| Production bug, root cause unknown | Contest | Competing hypotheses tested |
| Migrate services | Vertical Slice | Each team owns their service |
| Add feature with unfamiliar library | Parallel Research + Implement | Research feeds implementation |
| Long CI run, continue work | Background Monitor | Zero-cost watching |
| Implemented fix, want verification | Self-Review Loop | Maker-checker catches gaps |
| Parse HTML from multiple sites | Iterative Pipeline | Structured extraction per source |
| Generate edge-case tests | Contest | Multiple perspectives catch gaps |
| Major refactor | Horizontal Split + Specialist | Dedicated expert attention |
| Ongoing maintenance | Background Monitor | Proactive improvement |
