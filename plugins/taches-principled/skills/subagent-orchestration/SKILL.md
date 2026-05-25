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

### Agent Scopes

Agents exist at five scopes, each with different visibility and priority:

| Scope | Location | When to use | Priority |
|-------|----------|-------------|----------|
| **Session** | Inline via `--agents` CLI flag | One-off agent for a single session | 2 |
| **Managed** | Via organization settings | Team-standard agents enforced org-wide | 1 (highest) |
| **Project** | `{project}/.claude/agents/{name}.md` | Agent specific to one workspace | 3 |
| **User** | `~/.claude/agents/{name}.md` | Personal agents across all projects | 4 |
| **Plugin** | Plugin's `agents/` directory | Bundled with installed plugins | 5 (lowest) |

**Scope decision guide:**
```
Is the agent for a specific project only?
  YES → Project scope: {project}/.claude/agents/{name}.md
  NO  → Is it team-standard (should override personal)?
         YES → Managed scope: via /agents UI or org settings
         NO  → Is it personal and cross-project?
               YES → User scope: ~/.claude/agents/{name}.md
               NO  → Session scope: --agents JSON at startup
```

### Core Loop

1. **Scope decision** — project vs user vs managed
2. **Identify purpose** — researcher, analyst, background monitor, etc.
3. **Configure** — skills, memory, hooks, isolation (omit tools/model/effort by default)
4. **Generate** — write the agent file and optional SKILL.md
5. **Validate** — verify file structure and field values

### Frontmatter Fields

| Field | Type | Description |
|-------|------|-------------|
| `name` | string | Unique identifier. Lowercase letters and hyphens only. Required. |
| `description` | string | When Claude should delegate to this subagent. Required. |
| `tools` | list[string] | Tools the subagent can use. Allowlist. Example: `Read, Grep, Glob, Bash` |
| `disallowedTools` | list[string] | Tools to remove from inherited list |
| `model` | string | `sonnet`, `opus`, `haiku`, full model ID, or `inherit` |
| `permissionMode` | string | `default`, `acceptEdits`, `auto`, `dontAsk`, `bypassPermissions`, `plan` |
| `maxTurns` | integer | Max agentic turns before subagent stops |
| `skills` | list[string] | Skills to preload (full content injected at startup, not just description) |
| `mcpServers` | map | MCP servers scoped to this subagent |
| `hooks` | map | Lifecycle hooks scoped to this subagent |
| `memory` | string | Persistent memory scope: `user`, `project`, or `local` |
| `background` | boolean | `true` = always run as background task. Default is `false` — omit this field entirely unless async is required |
| `effort` | string | Effort level: `low`, `medium`, `high`, `xhigh`, `max` |
| `isolation` | string | `worktree` = run in temporary git worktree |
| `color` | string | Display color: `red`, `blue`, `green`, `yellow`, `purple`, `orange`, `pink`, `cyan` |
| `initialPrompt` | string | Auto-submitted as first user turn when agent runs as main session |

### Tool Restriction — Iterative Refinement

**Start with no tool restrictions.** Omit both `tools` and `disallowedTools` from the initial definition. The agent inherits all tools from the parent. Ship it, verify it works, then restrict only if a specific tool causes problems.

**Why start unrestricted:** Premature restriction is the most common cause of silent agent failures — the agent can't complete its task but can't report why either.

**When restrictions are appropriate from the start:** Read-only agents that should never write files (`disallowedTools: [Write, Edit]`).

### Model & Effort — Omit by Default

**Never set `model` or `effort` unless explicitly requested.** Both default to `inherit`, which is correct for 95% of agents. Setting them prematurely locks the agent to a model/effort that may be wrong for the parent's current configuration.

| Model | Only use when |
|-------|----------|
| `inherit` (omit the field) | Default — always correct unless explicitly requested |
| `haiku` | User explicitly requests fastest/cheapest |
| `sonnet` | User explicitly requests balanced |
| `opus` | User explicitly requests deepest reasoning |

### `skills` — Skill Preloading

Subagents **do not inherit skills from the parent** — you must list them explicitly. The `skills` field injects **full SKILL.md content** into the subagent's context at startup.

```yaml
skills:
  - anki-expert
  - subagent-orchestration
```

**Gotchas:**
- Missing or disabled skills are **silently skipped**
- Full content injection consumes context window tokens — preload only what the agent needs
- `disable-model-invocation: true` in skill frontmatter blocks preloading — never set this unless explicitly requested

### `memory` — Persistent Memory

**Best practice: enable memory on every subagent by default.** Without it, each invocation starts from scratch.

| Scope | Directory | Persistence | Git | When to use |
|-------|-----------|-------------|-----|-------------|
| `project` | `~/.claude/projects/{project-path}/memory/<name>/` | All sessions | Committable | **Default** — team-shared knowledge |
| `user` | `~/.claude/agent-memory/<name>/` | All projects | Not in repo | Cross-project expertise |
| `local` | `~/.claude/agent-memory/<name>/` | All sessions | Gitignored | Secrets, sensitive findings |

**Scope selection guide:**
```
Is the knowledge project-specific?
  YES → `memory: project` — commit it for teammates
Is the knowledge universal across all projects?
  YES → `memory: user` — stays on your machine
Does the subagent handle sensitive output?
  YES → `memory: local` — gitignored
```

### Body Prompt Philosophy

The markdown body (after frontmatter) is the subagent's system prompt. Keep it **general and concise** — a short role statement and a few behavioral guardrails.

**Rules:**
- **One paragraph for the role**, then optional short sections only if truly needed
- **Never duplicate content that exists in a skill.** If `skills` frontmatter loads `anki-expert`, the agent already knows card specs — do not repeat them in the body
- **Never enumerate tools or workflows in the body.** The agent discovers tools at runtime
- **If you're writing more than ~30 lines of body content, you're duplicating a skill.** Stop and reference it in the `skills` field instead

**Good body (3-5 lines):**
```
You are the cross-reference specialist. Your job is the canonical lookup
workflow: exam question → master mapping → topic content → verified source.

Never modify files. Report lookups with source verification.
```

### Routing: Description and Invocation

The `description` field is the **routing oracle** — Claude reads it to decide whether to auto-delegate. Write it like a trigger rule: specific conditions, not capability lists.

```
# Weak — too generic
description: Research agent

# Strong — explicit trigger conditions
description: Use when the user asks to find, research, or look up information across the codebase or web
```

**Three ways to invoke:**
| Pattern | How to trigger | Use when |
|---------|---------------|----------|
| **Implicit** | Natural language naming the task | Routine delegation, Claude decides |
| **Explicit @-mention** | `@code-reviewer review the auth module` | You want this specific agent |
| **Via Agent tool** | `Agent("code-reviewer")` with a task prompt | Programmatic or chained workflows |

### File Templates

**Template 1: Researcher**
```yaml
---
name: researcher
description: When user asks to explore unknown codebases, map architecture, trace
  call paths, or find patterns across multiple packages.
maxTurns: 15
memory: project
---

You are the codebase researcher. Explore thoroughly, report precisely.

After each session, update your memory with: file locations discovered,
key architectural patterns, module relationships.
```

**Template 2: Full-Capability Analyst**
```yaml
---
name: full-capability-analyst
description: When user asks for deep analysis of complex bugs, multi-step refactors,
  or cross-package investigation requiring full tool access.
maxTurns: 25
memory: project
---

You are a senior analyst. Investigate thoroughly, reason step by step.

After each session, update your memory with: root causes identified,
files involved, patterns observed.
```

**Template 3: Background Monitor**
```yaml
---
name: deploy-monitor
description: Monitor deploy logs and alert on failures
background: true
memory: local
maxTurns: 100
---

You are a monitoring agent. Watch for failures, anomalies, and patterns.

Update your memory with each incident for your runbook.
```

**Template 4: Worktree-Isolated Explorer**
```yaml
---
name: worktree-explorer
description: Explore repository with full isolation — safe refactoring experiments
  and structural analysis that must not touch the main working tree.
isolation: worktree
maxTurns: 20
---
```

### Fork Mode (v2.1.117+)

By default, subagents start with a **minimal context** — only the delegation prompt plus any preloaded skills. Fork mode creates a subagent that **inherits the full conversation context** and shares the parent's prompt cache.

**When to use fork mode:**
- Subagent needs to understand the full conversation to do its job
- You want cheaper continuation of a complex investigation
- The subagent needs to reference decisions made earlier in the conversation

**When NOT to use fork mode:**
- Independent tasks that don't need conversation context
- Parallel workstreams that should be isolated from each other
- Background tasks where full context would waste tokens

---

## ORCHESTRATE Mode

Orchestrate multiple subagents in parallel, self-review work, iterate with feedback loops, and manage background workers.

### Core Mental Model

Four rules that govern every delegation decision:

1. **Analyze before delegating** — understand the full task graph first
2. **Assign unambiguous scope** — each subagent gets exclusive file ownership
3. **Validate before integrating** — run success criteria, never assume
4. **Persist state to disk** — subagents don't share conversation memory

### Cost-Capability Spectrum

| Type | Model | Context | Cost | Use when |
|------|-------|---------|------|----------|
| `Bash` | — | Shell only | Lowest | Git ops, build commands, script execution |
| `Explore` | Haiku | Fresh, read-only | Lowest | Codebase discovery, targeted lookups |
| `Plan` | Sonnet | Fresh, read-only | Low | Architecture analysis, implementation planning |
| `general-purpose` | Inherit | Fresh, configurable | Medium | Custom workflows, complex orchestration |

**Rule:** Never spawn a subagent for a task that fits in a single context window and would take less than 5 minutes inline.

### Delegation Protocol

#### Step 1 — Decompose

Break the task into independent workstreams. Each stream must:
- Own its file set exclusively (no overlapping edits)
- Have a clear deliverable (file path + format)
- Have passing success criteria (test, lint, type-check)
- Have a one-command rollback

#### Step 2 — Context Harden (RACE Framework)

Structure every spawn prompt with RACE:

```
## Role
[What this agent is and what expertise it brings]

## Action
[Concrete, scoped task — imperative form, one clear objective]

## Context
[What the orchestrator has done; what this agent should do next; file ownership boundaries]

## Expectation
[Output format/schema; success criteria; coverage rule (comprehensive vs curated)]
```

**Key constraints:**
- **Positive framing** — tell agents what to do, not what to avoid
- **Minimal high-signal context** — context is currency
- **Explicit scope** — define files owned and files forbidden
- **Coverage rule** — specify whether to err on side of over-reporting or curated results

**Failure signal:** If you cannot complete the task, return:
```
{"status": "failed" | "success", "reason": "...", "completed_portion": "...", "retry_possible": true/false}
```
Do not guess or produce partial output without flagging it.

**Schema fields:**
- `status`: "failed" or "success" — unambiguous signal
- `reason`: Root cause description — enables retry decision
- `completed_portion`: What was finished before failure — enables partial recovery
- `retry_possible`: Boolean — prevents infinite loops on unfixable failures

#### Step 3 — Spawn with Constraints

```
Agent(
  description = "Security-focused code reviewer for Kotlin extensions",
  subagentType = "general-purpose",
  model = "sonnet",
  tools = ["Read", "Grep", "Bash"],
  disallowedTools = ["Write", "Edit"],
  background = true,
)
```

**Model selection:**
- `haiku` — fast read-only tasks, simple transformations
- `sonnet` — balanced analysis and implementation
- `opus` — deep reasoning, complex architectural decisions

**Tool scoping:** Prefer allowlists over denylists. Scoped permissions reduce blast radius.

#### Step 4 — Collect and Validate

**TaskGet — inspect mid-flight:**
```
TaskGet(taskId = "agent-id")
```
Returns full subagent details: status, errors, progress. Use when subagent is taking longer than expected.

**TaskOutput — read results without blocking:**
```
TaskOutput(taskId = "agent-id", block = false, timeout_ms = 0)
```
Returns subagent's accumulated output file directly.

**SendMessage — resume a subagent:**
```
SendMessage(to = "agent-id", message = "Continue the previous work")
```
Resume a background subagent via its ID from TaskList output.

**Workflow with inspection:**
```
Agent spawned (background=true)
→ After expected time, TaskGet(taskId) to check status
  → If stuck: TaskStop + respawn with corrected prompt
  → If failed: TaskGet for error details → root-cause → re-decompose
  → If running: wait or continue other work
```

**Explicit failure signal:**
```
{"status": "failed" | "success", "reason": "...", "completed_portion": "...", "retry_possible": true/false}
```

#### Step 5 — Synthesize

Cross-domain consistency check + full integration test before presenting results.

### Self-Review Loop

After implementing a solution, run a maker-checker loop:

```
Orchestrator → Implement → Spawn reviewer (read-only) → [pass] → integrate
                                          ↓ [fail, specific feedback]
                                     Fix → Respawn reviewer → ...
```

The reviewer must report ALL findings including low-confidence ones. A downstream filter ranks severity — don't ask the reviewer to make that judgment.

### Parallel Patterns

**Pattern 1: Horizontal Split (Investigation)**
```
Orchestrator
├── @security "Audit auth/ for OWASP Top 10"
├── @perf "Analyze db queries for N+1"
└── @style "Review code style violations"
```
**When NOT to use:** Tasks with shared dependencies or where findings depend on each other's output.

**Pattern 2: Vertical Slice (Implementation)**
```
Orchestrator
├── @frontend "Implement UI in src/ui/"
├── @backend "Implement API in src/api/"
└── @tests "Write integration tests in tests/"
```
**When NOT to use:** Features requiring shared data models where slices must be coordinated mid-implementation.

**Pattern 3: Pipeline (Chained)**
```
Orchestrator
├── @researcher "Research library X → /tmp/research.json"
[orchestrator waits, then:]
└── @implementer "Implement using /tmp/research.json"
```
**When NOT to use:** Tasks that could run in parallel — pipeline adds sequential latency and a failed first stage blocks all downstream stages.

**Pattern 4: Contest (Competing Hypotheses)**
```
Orchestrator
├── @theory-A "Bug is in auth. Trace execution X. Report as JSON."
└── @theory-B "Bug is in caching. Check metrics Y. Report as JSON."
```
**When NOT to use:** When you already have signal pointing to one hypothesis — contest wastes resources on known-wrong paths.

**Pattern 5: Aggregator Fan-out/Fan-in**
```
Orchestrator
├── Spawn N parallel subagents (each handles one slice)
├── Waits for all to complete
├── Spawns 1 aggregator subagent
└── Returns aggregator's synthesized result
```
**When NOT to use:** Simple parallel tasks that need no synthesis — aggregator overhead is only justified when N > 5 or synthesis requires cross-domain reasoning.

### Background Subagents

Spawn in background for concurrent work:
```
Agent(description = "...", background = true)
```

**Use background when:**
- Orchestrator can proceed without the result
- Task is long-running (monitoring, polling)
- Parallel independent workstreams

### Iteration and Looping

**Retry rules:**
- Non-deterministic failure (network, transient) → retry with same prompt
- Logic failure (agent misunderstood) → retry with corrected prompt
- After 2 retries on same failure → stop, report back with findings

**Never loop silently** — if a subagent fails twice with the same root cause, re-decompose the task before respawning.

### Three Automation Layers

| Tool | Trigger | Best for |
|------|---------|----------|
| Hooks | Tool events | Validate subagent outputs, enforce guardrails |
| ScheduleWakeup / CronCreate | Time | Recurring orchestration, long-poll retries |
| Monitor | External events | Real-time CI/log watching, instant reaction |

**Rule:** Never poll when you can watch.

- **ScheduleWakeup** — external system has no event output (simple polling)
- **Monitor** — process emits structured output (logs, CI lines, test results)

### Monitor — Event-Driven Watching

Monitor streams shell command stdout as real-time events. Each matching line wakes Claude to react. Zero cost while silent.

```
Monitor(
  description = "CI failure detector",
  command = "tail -f /tmp/ci.log | grep --line-buffered -E 'FAILED|ERROR|Build failed'",
  timeout_ms = 3600000,
  persistent = true
)
```

**Monitor vs ScheduleWakeup:**
- ScheduleWakeup: fires every N seconds regardless of state (wastes tokens polling)
- Monitor: fires only when output matches (free while silent, instant reaction)

**Always use `grep --line-buffered`** in pipes — without it, pipe buffering delays events by minutes.

**Filter aggressively** — every stdout line becomes a conversation message. Too many events triggers auto-stop.

**Pattern — CI failure watching:**
```
Monitor(
  description = "CI failure detector",
  command = "tail -f /tmp/ci.log | grep --line-buffered 'FAILED|ERROR'",
  persistent = true
)
```
[Claude reacts to failures instantly while CI runs]

**Pattern — Dev server error catching:**
```
Monitor(
  description = "dev server errors",
  command = "tail -f server.log | grep --line-buffered 'ERROR\\|panic'",
  timeout_ms = 7200000
)
```
[Claude notified the instant a server error appears]

### Failure Modes Reference

| Failure Mode | Detection | Recovery Cost | Prevention |
|--------------|-----------|---------------|------------|
| **Over-delegation** | Obvious in hindsight | Low (do inline) | Default to inline for <5min tasks |
| **Context leakage** | Silent, subtle | High (full audit) | Non-semantic agent names; explicit subagent type |
| **Tool permission misconfig** | Immediate failure | Medium (reconfigure) | Validate YAML; use allowlists |
| **State management failures** | Silent corruption | High (validate outputs) | Schema validation at every tool boundary |
| **Blocking anti-patterns** | Appears productive | Very high (terminate all) | Hard iteration limits; don't race |
| **File conflicts** | Git conflicts visible | Medium (manual merge) | Worktree isolation; file-disjoint decomposition |
| **Rollback failures** | Broken state visible | High (manual revert) | Always specify rollback; verify before marking done |

**Key rule:** Stop and report after 2 retries on the same failure. Never loop silently.

### Memory Architecture

| Layer | Mechanism | Persistence |
|-------|-----------|-------------|
| `CLAUDE.md` | Human-authored, loaded every session | Global/Project |
| `MEMORY.md` | Learned during sessions, auto-written | Project |
| Subagent Memory | `memory:` frontmatter per agent | Agent-scoped |

**State persistence rules:**
- Must survive compaction → CLAUDE.md or disk artifact
- Must survive session end → disk artifact (orchestrator) or agent-memory (subagent)
- Must be shared between subagents → orchestrator-owned disk artifact

### Context Window Discipline

**Effective ceiling:** ~147K-152K tokens (not the nominal 200K). Auto-compaction triggers at ~64-75% capacity and removes "less important" content — which may include critical context.

**MCP server costs:** Each MCP server consumes 2K-10K tokens before any subagent logic runs. Disable unused servers.

**Targeted reads:** Use `Read lines 40-90 of file.ts` rather than full files in debugging loops. Every context dollar spent on irrelevant content is one less spent on signal.

**Survival rule:** Critical information must live in CLAUDE.md or disk artifacts — not inline conversation where compaction can remove it.

### Anti-Patterns

**Never:**
- Spawn subagents that edit overlapping files — **consequence: git conflicts and manual merge resolution**
- Delegate without success criteria — **consequence: unverifiable failure, no way to know if task completed correctly**
- Assume subagent completed without validation — **consequence: silent failures propagate downstream, corrupting results**
- Let orchestrator implement while waiting for subagents — **consequence: deadlock, orchestrator blocked indefinitely**
- Skip rollback plan — **consequence: broken state with no recovery path**
- Context stuff — **consequence: token waste, signal-to-noise degrades, agent misses critical details**
- Use RACE framework for simple one-liner tasks — **consequence: coordination overhead exceeds task cost, net negative**
- Negative framing ("don't do X") — **consequence: cognitive load, obscure correct behavior — prefer positive framing ("do A instead")**

**Never delegate:**
- Destructive operations without explicit approval
- Tasks requiring conversation history (subagents start fresh)
- Simple single-step tasks (coordination overhead > benefit)
- Overlapping file scopes to parallel agents

### Orchestrator Checklist

- [ ] Task decomposed into independent, file-disjoint streams
- [ ] Each stream has: scope, context, deliverable, success criteria, rollback
- [ ] Spawn prompt structured with RACE (Role/Action/Context/Expectation)
- [ ] Subagents spawned with appropriate model/tools/background
- [ ] Failure signal format defined for each subagent
- [ ] Results validated against success criteria before integration
- [ ] Failed subagents: root-cause → re-decompose → respawn (never patch in-place)
- [ ] Cross-domain consistency checked before integration
- [ ] Final test suite passes before commit
- [ ] Rollback verified if integration fails
- [ ] Monitor or ScheduleWakeup wired for long-running external processes
- [ ] TaskGet/TaskOutput available for mid-flight inspection

### Reference: 10 Orchestration Use Cases

| # | Scenario | Pattern | Why this beats alternatives |
|---|----------|---------|----------------------------|
| 1 | PR with multi-file changes across security, performance, style | Horizontal Split | Independent analysis streams run in parallel |
| 2 | Production bug, root cause unknown | Contest | Competing hypotheses tested simultaneously |
| 3 | Migrate 3 services from REST to GraphQL | Vertical Slice | Each team owns their service end-to-end |
| 4 | Add feature requiring unfamiliar library | Parallel Research + Implement | Research feeds implementation without blocking |
| 5 | Long CI run, continue other work | Background Monitor | Zero-cost watching, instant reaction on failure |
| 6 | Implemented fix, want independent verification | Self-Review Loop | Maker-checker catches what the author missed |
| 7 | Parse HTML from multiple sites | Iterative Pipeline | Structured extraction per source, aggregated results |
| 8 | Generate edge-case tests for a function | Contest | Multiple perspectives catch different gaps |
| 9 | Major refactor touching multiple layers | Horizontal Split + Specialist | Each layer has dedicated expert attention |
| 10 | Ongoing maintenance, proactive fixes | Background Monitor | Proactive improvement without blocking main work |

**Rule of thumb:** When uncertain which pattern fits, default to Horizontal Split. When findings will influence each other, switch to Pipeline. When hypothesis is unclear, use Contest.