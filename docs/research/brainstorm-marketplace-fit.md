# Brainstorm: Marketplace Fit Against Dynamic Workflows

**Audience:** taches-principled maintainers
**Date:** 2026-06-02
**Question:** Now that Claude Code ships a first-class orchestration-script runtime, which of our skills/plugins lose relevance, which become wrappers around that runtime, and how do we describe them without citing brittle tool names?

This is a brainstorm — every classification has a rationale and a proposed next-step. None of it is committed code change.

---

## The classification matrix

Verdicts:
- **KEEP** — domain stays ours; the new runtime doesn't compete with this purpose.
- **WRAP** — the skill should now teach Claude to produce an orchestration script with a methodology-shaped phase structure, instead of teaching inline fan-out.
- **REFRAME** — the skill stays load-bearing but its body must shift to teach methodology around the new primitive (when to use it, how to map our discipline onto it).
- **MERGE** — overlaps with another skill enough that they should fold together.

### Skills

| Skill | Plugin | Verdict | Rationale |
|---|---|---|---|
| `archive-plan` | taches-principled | KEEP | File management lifecycle, not orchestration. |
| `claude-headless` | taches-principled | KEEP | Documents non-interactive CLI usage; touch up to note orchestration scripts run from headless too. |
| `create-plans` | taches-principled | KEEP | Strategic planning sits *above* execution. A plan phase may *contain* an orchestration script as its execution mode, not the reverse. |
| `diagnose` | taches-principled | **WRAP** | Pure multi-modal sweep + adversarial-verify shape — exactly the pattern the runtime documents. |
| `execute-plans` | taches-principled | KEEP (with tweak) | Stays as the consumer of PLAN.md, but per-phase execution now picks between inline / subagent / orchestration-script per task scale. |
| `ideation` | taches-principled | **WRAP** | Generator fleet → judge panel → synthesizer is the canonical judge-panel pattern named in the runtime docs. |
| `kaizen` | taches-principled | KEEP | Posture/philosophy skill, not orchestration. |
| `memory-curator` | taches-principled | KEEP | File curation. |
| `multi-agent-patterns` | taches-principled | **REFRAME** | Coordination-pattern selection is methodology the platform docs do not provide. Stays as the authority on which pattern fits which problem shape; adds a mapping table from our patterns to the runtime's API where the runtime can express the pattern directly. |
| `plan-do-check-act` | taches-principled | **WRAP** | The four-stage cycle maps cleanly to a four-phase pipeline. |
| `refine` | taches-principled | **WRAP** | Multi-pass refinement is judge-panel-and-synthesize. |
| `rules-orchestration` | taches-principled | KEEP | Manages CLAUDE.md / `.claude/rules/` lifecycle; not orchestration. |
| `security` | taches-principled | **WRAP** | Multi-dimensional review (auth, input validation, secrets, race conditions, sandbox escapes) with verification fleet — adversarial verify shape. |
| `skill-authoring` | taches-principled | KEEP | Meta-skill about the marketplace's own artifacts. |
| `subagent-orchestration` | taches-principled | **REFRAME** | The platform exposes a new primitive (the orchestration script) but does not teach the methodology around it: spawn-prompt structure, hub-and-spoke discipline, cold-start context handoff, file-disjoint scoping, success criteria, rollback contracts, execution-mode selection. Skill stays authoritative on all of these. Adds: when to escalate from subagents to an orchestration script, and how the runtime's `agent()` / `pipeline()` / `parallel()` shapes map onto the discipline. |
| `task-lifecycle` | taches-principled | KEEP | Lifecycle process; individual stages may invoke an orchestration script but the lifecycle itself is meta-process. |
| `tool-design` | taches-principled | KEEP | MCP / tool design domain — separate from session-side orchestration. |
| `update-docs` | taches-principled | KEEP | Documentation update workflow; size-bounded inline edit. |
| `ddd` | tp-ddd | **WRAP** | Bounded-context analysis is naturally a multi-modal sweep across aggregates / services / event flows / use cases. |
| `fpf` | tp-fpf | **WRAP** | PROPOSE / EXTEND / VERIFY *is* a three-stage pipeline; the agent role definitions already exist in tp-fpf/agents/. |
| `git` | tp-git | KEEP | CLI ops, not multi-agent. SHIP mode can mention setting a completion condition (`PR merged with green CI`) instead of polling manually. |
| `capture` | tp-meta | KEEP | Transcript capture, not orchestration. |
| `session-analytics` | tp-meta | **WRAP** | Behavioral analysis across multiple anti-pattern dimensions = perspective-diverse review fleet. |
| `sadd` | tp-sadd | **WRAP** (most of the body collapses) | Biggest overlap. SADD's COMPETE/JUDGE/VERIFY/EXPLORE/SYNTHESIZE modes are the exact patterns named in the runtime docs. Skill collapses to "for SADD-shaped tasks, write an orchestration script using these canonical role names" — the agent role definitions in tp-sadd/agents/ are the durable value. |
| `test-orchestration` | tp-tdd | **WRAP** | Red-Green-Refactor maps to a three-phase pipeline with per-test parallelism. |

### Commands

| Command | Verdict | Rationale |
|---|---|---|
| `archive` | KEEP | Pointer to skill. |
| `critique` | **WRAP** | Pure adversarial-verify shape. |
| `debug` | **WRAP** (pointer) | Becomes a pointer to diagnose-as-orchestration. |
| `design-subagents` | **KEEP** | Designing the subagent definition (body, role, tool allowlist, model) is independent of how it's invoked. Definitions are the durable role library both inline subagents and the orchestration runtime compose from. |
| `ideate` | **WRAP** (pointer) | Pointer to ideation-as-orchestration. |
| `implement` | KEEP | Task-scale-aware. Picks execution mode per task. |
| `improve` | **WRAP** | Judge-panel refinement. |
| `learn` | KEEP | Memory capture. |
| `orchestrate-solo` | **MERGE into `orchestrate`** | The solo/team split was specific to hand-rolled orchestration. The runtime makes it unnecessary as a separate command — solo is one mode option among inline / subagents / orchestration script. |
| `orchestrate` | **REFRAME** | Becomes the execution-mode selector: reads task scale and shape, picks inline / subagents / orchestration script, dispatches. Mode selection is the value the platform doesn't provide. |
| `polish` | **WRAP** | Multi-pass refinement (Strunk & White as the lens for each pass). |
| `rules` | KEEP | Meta-management. |
| `simplify` | **WRAP** | Multi-perspective simplification + judge. |
| `whats-next` | KEEP | Handoff document generation. |
| `meta-issue` | KEEP | Single artifact generation. |
| `meta-review` | **WRAP** | Calls session-analytics; becomes orchestration-script pointer. |
| `session-inspect` | KEEP | Pure parsing — single agent. |

### Agents

Nearly all agents KEEP as role definitions because orchestration scripts dispatch to them by `agentType`. Specifically:

- All `tp-sadd/agents/` (judge, meta-judge, generator, expander, explorer, synthesizer) → canonical role library
- All `tp-fpf/agents/` (hypothesis-generator, evidence-validator, logic-verifier, trust-auditor) → canonical role library
- `tp-meta/agents/meta-reviewer` → canonical role
- `taches-principled/agents/tp-*` (critic, grader, debug-tracer, code-reviewer, explorer, researcher, plan-architect, plan-verifier, skill-auditor, subagent-auditor, test-strategist, comparator, analyzer, global-implementer) → canonical role library

The orchestration runtime composes these by name. The role definitions are the **durable artifact**; the inline orchestration that used to invoke them is what gets replaced.

---

## Proposed orchestration shapes (the WRAP candidates)

For each WRAP candidate, the script the skill should now teach Claude to write. Phase titles are illustrative; the methodology determines the canonical names.

### `diagnose`
Phases: **Sweep → Refute → Conclude**
- Sweep: 4–6 finder agents, each with a distinct lens (stack trace, recent commits, similar past bugs, system state, dependency changes, configuration drift). Each returns a hypothesis with evidence pointers.
- Refute: per hypothesis, fan out 3 skeptic agents prompted to refute with the bias to mark refuted=true if uncertain. Hypothesis survives only with ≥2 of 3 votes.
- Conclude: one synthesis agent gathers surviving hypotheses, ranks by evidence strength, returns a structured diagnosis.

### `ideation`
Phases: **Generate → Judge → Synthesize**
- Generate: N ideators in parallel, each given a different starting angle (user-first, risk-first, constraint-first, opportunity-first, MVP-first).
- Judge: panel of independent scorers; each rates every idea on multiple dimensions; returns structured scores.
- Synthesize: winner-take-most synthesizer grafts the best ideas from runners-up.

### `plan-do-check-act`
Phases: **Plan → Do → Check → Act**
- Plan: 1 planner returns hypothesis + change list + success criteria.
- Do: per change, an implementer agent (parallel).
- Check: verification fleet (lint, type, test, behavioral assertions).
- Act: synthesizer decides standardize vs adjust vs revert.

### `refine`
Phases: **Critique → Score → Revise**
- Critique: multiple critics with distinct lenses (clarity, structure, accuracy, completeness).
- Score: each critic scores the artifact along its lens.
- Revise: one revision agent produces the next draft incorporating only critiques above a threshold.

Loop-until-dry across passes (stop when no critic returns substantive findings two rounds in a row).

### `security`
Phases: **Sweep → Verify → Triage**
- Sweep: dimension-per-agent (auth flows, input validation, secrets, race conditions, sandbox escapes, dependency CVEs).
- Verify: per finding, 2–3 verifiers attempt to reproduce; finding survives only if reproducible.
- Triage: severity-classification synthesizer returns a prioritized list.

### `ddd`
Phases: **Discover → Cross-check → Propose**
- Discover: 4 explorers in parallel — one per modality (by aggregate, by service, by event flow, by use case).
- Cross-check: judge fleet looks for inconsistencies between the four maps.
- Propose: synthesizer outputs a bounded-context proposal with explicit reconciliation.

### `fpf`
Phases: **Propose → Extend → Verify**
- Propose: hypothesis-generator agents in parallel produce competing first-principles hypotheses.
- Extend: per hypothesis, logic-verifier + evidence-validator agents in parallel.
- Verify: trust-auditor synthesizes R_eff scores and decision readiness.

### `test-orchestration` (TDD)
Phases: **Red → Green → Refactor**
- Red: failing-test author per feature, parallel.
- Green: minimal-implementation author per test, parallel.
- Refactor: refactor agent per file with the test as a guardrail.

### `sadd`
The orchestration body collapses. Skill becomes a thin pointer:
> For competitive generation, judge-panel evaluation, tree-of-thoughts exploration, or any multi-candidate evaluation pattern, have Claude write an orchestration script using these canonical role names: `generator`, `judge`, `meta-judge`, `explorer`, `expander`, `synthesizer`. The role definitions in this plugin's `agents/` directory are the canonical prompts; the orchestration script dispatches to them by name.

### `session-analytics`
Phases: **Slice → Review → Triage**
- Slice: one parser agent extracts structured events (tool calls, errors, hooks).
- Review: dimension-per-agent (tool misuse, skipped verification, instruction-following failures, plan adherence, cost efficiency).
- Triage: severity-classifier synthesizer outputs ranked findings.

---

## What reframes, what merges — and why no orchestration skill collapses

Earlier drafts of this brainstorm proposed collapsing `subagent-orchestration`, `multi-agent-patterns`, and the `orchestrate` / `orchestrate-solo` / `design-subagents` commands because the platform now ships a workflow primitive. That was wrong. Here is why:

**The platform provides a primitive; our skills provide the methodology around it.** Those are different layers and neither replaces the other.

What the platform's orchestration runtime + its docs DO provide:
- Named patterns (adversarial verify, judge panel, loop-until-dry, perspective-diverse verify, multi-modal sweep, completeness critic)
- Script API (`agent`, `pipeline`, `parallel`, `phase`, `log`, `budget`, `workflow`)
- Concurrency caps and resume semantics
- A comparison page on when to use which primitive

What the platform's docs DO NOT provide (and our skills do):
- **Spawn-prompt structure** — scope, context, deliverable, success criteria, rollback (the canonical five-element contract).
- **Hub-and-spoke discipline** — orchestrator owns cognition, subagents own execution; no peer-to-peer between subagents.
- **Cold-start context handoff** — subagents have no conversation history; every spawn must be self-contained.
- **File-disjoint scoping** — partitioning work so parallel agents don't collide on the same files.
- **Quality gates** — pre-dispatch independence check, receipt validation, integration check.
- **Execution-mode selection** — when to stay inline, when to subagent, when to write an orchestration script, when to add recurring checks + push channels.
- **The Transformer Mandate** — AI generates and scores; human decides on structural choices. The orchestration runtime delegates decision-making to the script by default; the methodology skills teach Claude to stay in proposal mode rather than auto-execute structural rewrites.

Subagents and orchestration scripts coexist as primitives. The runtime composes orchestration scripts *out of* subagent spawns — every `agent()` call in a script is a subagent. A skill teaching good subagent design feeds the runtime directly, not redundantly.

### Revised verdicts

| Skill / command | Verdict | What changes |
|---|---|---|
| `subagent-orchestration` | **REFRAME** | Stays authoritative on spawn-prompt structure, hub-and-spoke discipline, context handoff, success criteria, rollback. Adds: when to escalate from subagents to an orchestration script, and how the runtime's API maps onto the discipline. |
| `multi-agent-patterns` | **REFRAME** | Stays authoritative on coordination-pattern selection. Adds a mapping table from our patterns to the runtime's API where the runtime expresses the pattern directly. |
| `design-subagents` command | **KEEP** | Designing subagent definitions is independent of invocation mode — definitions are the durable role library both inline subagents and the orchestration runtime compose from. |
| `orchestrate` command | **REFRAME** | Becomes the execution-mode selector: reads task scale and shape, picks inline / subagents / orchestration script, dispatches. Mode selection is the value the platform doesn't provide. |
| `orchestrate-solo` command | **MERGE into `orchestrate`** | The solo/team split was specific to hand-rolled orchestration. Solo becomes one mode option in the unified selector. |

**Net deletions: 0. Net merges: 1 (`orchestrate-solo` → `orchestrate`). Net reframes: 4 (the rest).**

The orchestration skills become *more* load-bearing now, not less, because there are now more primitives Claude can pick the wrong one of.

---

## Semantic-language guide — vocabulary that survives tool renames

The Task→Agent rename already burned skills that hardcoded "Use the Task tool." Same shape of failure will happen again. Treat tool names as platform-internal identifiers and describe **outcomes and roles** instead.

### Substitutions for orchestration directives

| Brittle | Semantic |
|---|---|
| "Use the Workflow tool to..." | "Write an orchestration script that..." |
| "spawn N parallel Task agents" | "fan out across N independent investigators" |
| "spawn N parallel Agent agents" | "delegate to N workers in parallel" |
| "use pipeline() to chain" | "thread each item through verification stages without barriers" |
| "use parallel() with a barrier" | "fan out and await all results before synthesizing" |
| "with `schema:`" | "returning a structured object conforming to [schema]" |
| "with `model: 'haiku'`" | "delegated to a fast, lightweight worker" |
| "with `isolation: 'worktree'`" | "delegated in an isolated branch copy" |
| "the Workflow runtime" | "the orchestration runtime" |
| "the /workflows command" | "the orchestration-run view" |

### Substitutions for tool-name citations

| Brittle | Semantic |
|---|---|
| "Use the Write tool" | "Persist the artifact" / "Write the file" |
| "Use the Edit tool" | "Apply the change" / "Modify the file" |
| "Use the Read tool" | "Read [path]" (the verb alone is fine) |
| "Use the Bash tool" | "Run the command" / "Execute [command]" |
| "Use the Grep tool" | "Search the codebase" / "grep for X" (the verb alone) |
| "Use the Glob tool" | "Find files matching X" |
| "Use the Skill tool" | "Invoke the [skill-name] skill" / "Activate [skill-name]" |
| "Use the WebFetch tool" | "Fetch the page" / "Read the URL" |
| "the Hooks system" | "the deterministic event handler layer" |
| "the ScheduleWakeup mechanism" | "schedule the next iteration" / "set a follow-up check" |
| "CronCreate" | "schedule a recurring prompt" |
| "the /loop command" | "set up a recurring check" |
| "the /goal command" | "set a completion condition" |

### Substitutions for role descriptions (these survive even when role tool API changes)

| Brittle (cites API or specific subagent name) | Semantic (describes role and outcome) |
|---|---|
| "spawn a tp-critic agent" | "delegate adversarial review to a critic" |
| "agent(prompt, {agentType: 'judge'})" | "have a judge score against the rubric" |
| "use the tp-debug-tracer agent" | "delegate root-cause tracing to a worker that walks the call stack backward" |
| "with the tp-explorer agent" | "delegate exploration to a read-only investigator" |
| "use the synthesizer agent" | "merge findings into a single ranked output" |

The pattern: cite the **role** by domain noun (critic, judge, debugger, explorer, synthesizer, verifier). The orchestration runtime's `agentType` registry will resolve the noun to the right implementation regardless of what the file is named.

### The two-rule semantic discipline

1. **Verbs over tool names.** "Read the file" instead of "use the Read tool." The model has a tool registry; it knows which tool reads files.
2. **Roles over agent identifiers.** "Delegate adversarial review to a critic" instead of "spawn a tp-critic agent." The orchestration runtime resolves role nouns from its registry.

If a skill body cannot be expressed without naming a specific tool or specific agent file, the design has too much coupling — the skill should describe outcomes the model can satisfy with whatever primitives the platform provides this week.

---

## How this changes CLAUDE.md

The current subagent-first contract teaches *spawn subagents for non-trivial work*. The new contract is task-scale-aware:

| Task scale | Default execution mode | Language we use |
|---|---|---|
| Trivial (1-file edit, single search) | Inline | "do it directly" |
| Non-trivial single-context (3–10 files, single methodology) | Subagents | "delegate to a worker / fan out across a few investigators" |
| Multi-stage non-trivial (fan-out → verify → synthesize) | Orchestration script | "have Claude write an orchestration script with these phases" |
| Codebase-wide / many-file / multi-methodology | Orchestration script with explicit phase structure | "compose an orchestration with phases A → B → C" |
| Long-running with external triggers | Orchestration + recurring checks + push channels | "set up the long-running run with completion condition X" |

The skill's job at any scale: **describe the role and outcome, not the API call.**

---

## What I'd ship from this brainstorm (in priority order)

1. **REFRAME `subagent-orchestration` and `multi-agent-patterns`** — edit the SKILL.md bodies to add the execution-mode selection table and the mapping from our patterns to the runtime's API. They stay load-bearing; they teach methodology the platform docs do not.
2. **REFRAME the `orchestrate` command** as the execution-mode selector and **MERGE `orchestrate-solo`** into it as one mode option.
3. **Rewrite the WRAP skills** (`diagnose`, `ideation`, `plan-do-check-act`, `refine`, `security`, `ddd`, `fpf`, `test-orchestration`, `sadd`, `session-analytics`) to teach the methodology's phase structure and role assignments instead of inline orchestration mechanics.
4. **Update CLAUDE.md** with the task-scale-aware execution-mode table above.
5. **Audit every remaining skill body** against the two-rule semantic discipline: verbs over tool names, roles over agent identifiers. Any sentence that names a specific tool or specific agent file is a candidate for rewording.
6. **Keep all agent definitions** — they are the durable role library the orchestration runtime composes.

**Important framing:** This brainstorm lives in `docs/research/` which is **maintainer-only context** — a Claude Code session that installs this marketplace as an end-user never reads it. End-user Claude only sees skill descriptions (pre-loaded), skill bodies (loaded on trigger), agent definitions (loaded at spawn), and command bodies (loaded on invocation). Every recommendation above must ultimately materialize as edits to those files. The brainstorm is the maintainer's working notebook; the deliverable is the diff to `plugins/`.
