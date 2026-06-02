---
name: orchestrate
description: Select the execution mode for a task — inline, subagents, or orchestration script — and dispatch
argument-hint: [task to orchestrate]
---

$ARGUMENTS

Load the `subagent-orchestration` skill, then pick the execution mode by task scale (see the skill's execution-mode selection table) and dispatch.

**Pick the mode first.** Read the task, estimate the scope, then choose one tier:

- **Inline** when the work is trivial, a single file or search, or when `--solo` / `--lightweight` is passed, or when context usage is above 70%. Execute directly in the main context; self-verify against the task's success criteria; document decisions inline.
- **Subagents** when the work is non-trivial and single-context (3–10 files, one methodology) but the orchestration shape is one-off. Decompose into independent workstreams with disjoint file scopes, fan out 3–5 workers with RACE-structured spawn prompts (per `subagent-orchestration` references), aggregate from the scratchpad at `.principled/scratch/{plan-id}.md`, then run the critic-revise loop with MAX_ITERATIONS=3 cycles.
- **Orchestration script** when the work is multi-stage with fan-out → verify → synthesize, codebase-wide, multi-methodology, or worth codifying because the shape repeats. Have Claude compose a script that holds the phase structure; the conversation only holds the final answer. Use the runtime-API mapping in `subagent-orchestration` to translate the methodology's pattern (judge panel, adversarial verify, loop-until-dry, multi-modal sweep) into script-level fan-out, pipelines, and structured-output schemas.
- **Orchestration script + recurring + push channels** when the run is long-running or reacts to external triggers (CI, alerts, scheduled events).

**At every tier, apply the same verification gates** — verify commands from the plan, success criteria, file state checks. The gate moves between inline self-verify, a critic subagent, and a script's verification phase depending on the mode; the discipline is the same.

**Demotion signals** — any of these collapses to a lower tier: task touches ≤3 files and has no checkpoint types; user passes `--solo` or `--lightweight`; context budget below 30%; task is exploratory (research, spike, prototype).

**Escalation signals** — any of these forces a higher tier: task touches more than 10 files; cross-cutting concerns; high-stakes code (auth, payments, data integrity); user says "thorough" / "careful" / "with critique"; the orchestration shape will repeat across future tasks; the work outgrows what one conversation can coordinate.

Surface status updates and the selected mode to the user, not questions.
