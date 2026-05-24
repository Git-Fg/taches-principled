---
name: plan-do-check-act
description: Four-phase iterative PDCA cycle: plan a change, implement at small scale, measure results, then standardize or adjust based on evidence.
when_to_use: |
  Use when the user says "let's try an experiment", "test this hypothesis", "run a PDCA cycle", "try this and measure it", "design a test", "plan an experiment", "A/B test this", or "measure improvement".
  IMMEDIATELY when solving problems where outcomes need measurement — BEFORE concluding, standardizing, or shipping.
  FIRST after a failed fix — validate the root cause was correct before closing the issue.
  DO NOT use for debugging (use diagnose instead), for code style decisions (use write-concisely or refine), or for architectural design (use kaizen or ideation).
  CONTRAST with kaizen: kaizen prevents bad patterns; PDCA tests changes that might improve things.
argument-hint: "[improvement goal or problem to address] [--cycle N]"
---

## Decision Router

IF testing a hypothesis to solve a problem or improve a process → start a PDCA cycle with a clear success criterion
IF an experiment produced unexpected results → begin a new cycle with an adjusted hypothesis and measurement plan
IF an experiment succeeded → standardize the change in the Act phase and close the cycle
IF an experiment partially succeeded → standardize what worked and start a new cycle for what did not
IF stuck after three cycles on the same problem → revisit the root cause analysis before continuing

# Plan-Do-Check-Act

Four-phase iterative cycle for systematic experimentation and continuous improvement. Each cycle tests one hypothesis with measurable success criteria.

## Core Principle

Never implement a change without knowing how you will measure success. Never conclude without comparing results against the baseline. Every cycle either produces a standardized improvement or a validated learning that feeds the next cycle.

## Process

### Phase 1: Plan
1. Define the problem or improvement goal with baseline metrics
2. Identify root causes using deep analysis before hypothesizing
3. State the hypothesis explicitly: "If we change X, Y will improve by Z"
4. Design the experiment: what to change, how to measure, success criteria
5. **Verification:** Success criteria are numeric and measurable, not subjective

### Phase 2: Do
1. Implement the change at small scale first
2. Document what was actually done and any deviations from plan
3. Collect data throughout — include unexpected observations
4. **Verification:** The experiment ran as designed (deviations are documented, not hidden)

### Phase 3: Check
1. Measure results against success criteria
2. Compare to baseline: before vs. after
3. Did the hypothesis hold? If not, why?
4. Document learnings and insights, not just data
5. **Verification:** Analysis is objective — success or failure of the hypothesis, not judgment on effort

### Phase 4: Act
- **If successful:** Standardize the change — update documentation, train the team, add automation or monitoring
- **If unsuccessful:** Understand why the hypothesis failed, refine it, start a new cycle
- **If partially successful:** Standardize what worked, plan next cycle for remaining issues
- **Verification:** The Act phase outcome is explicit — either "cycle closed with standardization" or "cycle N+1 started with adjusted hypothesis"

## Output

Either: (1) a standardized improvement with documentation, monitoring, and team training, or (2) a validated learning that refines the hypothesis for the next cycle. Multiple cycles are normal — two to three cycles per problem is typical.

## Design Decisions

### Start small, escalate scope
Phase 2 always begins at small scale. Full rollout only after the Check phase confirms success. This prevents wasting effort on changes that do not produce results.

### Failed experiments are learning, not failure
The Act phase for an unsuccessful outcome does not trigger rollback — it triggers refinement. The learning from a failed hypothesis is as valuable as the learning from a successful one. The only true failure is not documenting why.
