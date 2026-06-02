---
name: orchestrate
description: Orchestrate parallel subagent execution for complex multi-file tasks
argument-hint: [task to orchestrate]
---

$ARGUMENTS

Load the `subagent-orchestration` skill, then orchestrate the work as follows:

1. **Decompose** the work into independent tasks with disjoint file scopes.
2. **Read the scratchpad protocol** at `../skills/execute-plans/references/execution-strategies.md` BEFORE selecting a strategy.
3. **Select a strategy** (A: Fully Autonomous / B: Segmented / C: Sequential) based on the checkpoint structure of the work.
4. **Fan out subagents in parallel** (max 3–5 workers, per `references/execution-strategies.md` numeric thresholds). Each worker MUST have read+write+bash access and MUST write findings to the centralized scratchpad at `.principled/scratch/{plan-id}.md` before returning.
5. **Aggregate** results from the scratchpad (NOT from subagent output text) — see `../skills/execute-plans/SKILL.md` "Implementer Scratchpad Protocol" for the exact protocol.
6. **Run the critic-revise loop** per `../skills/execute-plans/references/evaluation-protocol.md`:
   - Spawn a `tp-critic` subagent (general-purpose with write access) to evaluate the aggregate output.
   - **Hard cap: MAX_ITERATIONS = 3** fix-to-verify cycles. After 3 cycles with remaining HIGH findings, proceed with a warning and log remaining issues.
   - On each cycle: read critic findings from scratchpad, spawn `tp-global-implementer` for fixes, re-verify, re-spawn critic if non-trivial.
7. **Verify completeness** with a final `tp-plan-verifier` pass before declaring done.
8. **Update task status** at milestones; surface status updates to the user, not questions.

Lightweight/solo mode: if the user passes `--solo` or `--lightweight`, skip step 4's fan-out and execute sequentially in main context. See the lightweight-mode section of `subagent-orchestration/SKILL.md` for the full protocol.
