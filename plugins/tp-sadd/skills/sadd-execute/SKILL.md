---
name: sadd-execute
description: "Execute tasks with meta-judge verification: single-task, sequential-steps, parallel-targets, or competitive generation with quality gates"
argument-hint: "Task description [--mode single|steps|parallel|competitive] [--files f1,f2]"
---

## Decision Router

IF single self-contained task needs implementation with quality verification → single mode: parallel meta-judge + implementor, then judge with retry loop
IF task decomposes into ordered steps where each depends on previous → sequential mode: decompose into steps with per-step meta-judge + judge
IF multiple independent targets that can execute simultaneously → parallel mode: independence validation, requirement grouping, parallel dispatch, isolated retries
IF high-stakes best-of-N where quality matters more than speed → competitive mode: 3 generators + meta-judge in parallel, 3 judges, adaptive strategy
IF task is trivial (no verification needed) → use launch-sub-agent instead
IF retries exceed max without passing any mode → escalate to user with failure analysis

# Execute with Verification

Execute tasks using the meta-judge → implement → judge → retry pattern. The orchestrator dispatches, never implements. Four execution modes share this core loop but differ in decomposition strategy, concurrency model, and retry policy.

## Core Principle

The orchestrator dispatches, never implements. Reading files, writing code, or running tools directly violates separation of concerns. The orchestrator's job is coordination, not execution. Quality verification uses independent judges with fresh context to prevent confirmation bias.

## Meta-Judge Verification Pattern

See `meta-judge-pattern.md` in this plugin's references directory for the core loop, YAML specification structure, threshold scoring, and critical constraints.

## Model Selection

| Profile | Model |
|---------|-------|
| Complex reasoning (architecture, design, critical decisions) | Opus |
| Medium complexity, patterned work | Sonnet |
| Simple transformations | Haiku |
| Default (uncertain) | Opus |

For parallel modes (parallel, competitive), use the same model tier for all concurrent agents.

## Mode Selection by Task Structure

### Mode 1: Single Task

Execute one self-contained task with parallel meta-judge + implementor dispatch, then judge verification and retry loop.

**When to use:** Single, self-contained task that produces a coherent output. Not for multi-step workflows or parallel targets.

**Process:**

1. **Task Analysis** — Assess complexity (high/medium/low), risk, and scope. Default model: Opus.
2. **Parallel Dispatch** — Launch meta-judge AND implementation agent in a single message. Meta-judge MUST be first in dispatch order so it observes the task specification before the implementation agent modifies any files. Meta-judge returns only the YAML specification. Implementation agent receives CoT prefix, task body with expected output, and self-critique suffix producing a Summary section.
3. **Judge Verification** — Extract meta-judge spec YAML and implementation Summary. If pre-existing changes exist in the codebase, include a Pre-existing Changes section so the judge attributes work correctly. Dispatch judge with EXACT meta-judge spec.
4. **Retry Loop** — Score >= 4.0 = PASS. Score >= 3.0 with all low-priority issues = PASS. Score < 4.0 with retries remaining = retry with judge feedback (max 2 retries). Score < 4.0 after max retries = escalate to user with failure analysis.
5. **Final Report** — Task summary, verification history (scores per attempt), files modified, key changes, optional improvements from judge.

### Mode 2: Sequential Steps

Decompose a complex task into ordered, dependent subtasks with per-step meta-judge + judge and context passing between steps.

**When to use:** Complex tasks with natural decomposition boundaries and dependency ordering. Not for branching or parallel paths.

**Decomposition patterns:**

| Task Type | Decomposition |
|-----------|--------------|
| Interface change | Interface → Implementation → Consumers → Tests |
| Feature addition | Core logic → Integration → API layer |
| Refactoring | Extract/modify core → Internal references → External references |
| Multi-layer change | Data layer → Business layer → API layer → Client layer |

**Process:**

1. **Task Decomposition** — Identify natural boundaries and dependencies. Output a decomposition table with step number, description, dependencies, complexity, type, and expected output. Include a dependency graph showing sequencing.

2. **Per-Step Execution** — For each step in order:
   - **Parallel Dispatch**: Launch meta-judge (step-specific evaluation spec) AND implementation agent in a single message. Meta-judge first. Meta-judge includes overall task, this step's requirements, previous steps context, and artifact type. Implementation agent must end with "Context for Next Steps" section.
   - **Judge Verification**: Dispatch judge with exact meta-judge spec for this step. Include "Pre-existing Changes" section if previous steps modified files.
   - **Verdict**: Score >= 4.0 = PASS. Score >= 3.0 with low-priority issues = PASS. Score < 4.0 with retries remaining = retry with judge feedback (max 3 retries per step). Reuse same meta-judge spec across all retries.
   - **Context Passing**: After a step passes, extract only relevant information for remaining steps: files modified, key changes, new interfaces/APIs, decisions affecting later steps, warnings. Keep under 200 words per step. If cumulative context exceeds ~500 words, summarize older steps more aggressively.

3. **Final Summary** — Report task, total steps, per-step results (model, judge score, retries, status), files modified, key decisions, verification summary. Judge reports in `.specs/reports/`.

**Error handling:** Max retries = STOP and escalate with failure analysis. Context missing = re-examine previous step output or dispatch clarification sub-agent. Step conflicts = stop, analyze decomposition correctness, options include re-ordering, combining, or adding a reconciliation step.

### Mode 3: Parallel Targets

Execute multiple independent tasks simultaneously with requirement grouping to minimize agent count, plus isolated retries per target.

**When to use:** Multiple independent targets with no shared files or state. Not for interdependent tasks.

**Process:**

1. **Target Identification** — Extract targets from `--files`, `--targets`, or infer from task description.

2. **Independence Validation** — Verify: no shared files between targets, no target reads another's output, no shared mutable state, execution order does not matter. If any check fails, inform user and recommend sequential mode.

3. **Requirement Grouping** — Group tasks to minimize agent count:

   | Grouping | When | Meta-Judges | Judges |
   |----------|------|-------------|--------|
   | REPEATABLE | Same task applied to different targets | ONE shared (reusable spec, generic language) | One per target, SAME reusable spec |
   | SHARED | Interdependent tasks reviewed together | ONE combined (covers all tasks) | ONE for entire group, combined spec |
   | INDEPENDENT | Fully separate, no grouping benefit | One per task | One per task |

   **Decision rule:** Default to INDEPENDENT when uncertain. Over-grouping risks incorrect evaluation specs. Implementation agents are always isolated — one per task, never shared.

4. **Meta-Judge Dispatch (ALL in parallel)** — Launch one meta-judge per group/independent task. Launch each implementor immediately after its meta-judge completes (do not wait for all meta-judges).

5. **Parallel Implementation** — Launch ALL implementation agents in a single message. Each with CoT prefix, task body (target-specific), and self-critique suffix. Each ends with Summary section.

6. **Judge Verification** — After ALL implementors complete, dispatch judges per grouping. Include "Pre-existing or Expected Parallel Changes" section. Parse only structured headers.

7. **Retry Loop** — Isolated retries per target (max 3). For SHARED groups: re-launch only the failing implementor(s), then re-launch shared judge against ALL changes (passed + retried). Failed targets are isolated and do not affect other targets.

8. **Output Summary** — Per-target results (grouping, model, judge score, retries, status), overall completion stats, files modified, any failed targets with options.

### Mode 4: Competitive Generation

Generate 3 competing solutions in parallel, evaluate with 3 judges, then adaptively select the best strategy for final output.

**When to use:** High-stakes tasks where quality matters more than speed or cost. Not when a single good solution suffices.

**Process:**

1. **Competitive Generation + Meta-Judge** — Launch 4 agents in a single message. Meta-judge first in dispatch order:
   - **Meta-Judge**: Generates comparative evaluation specification YAML for evaluating across multiple solutions. Instructions that 3 solutions will be compared.
   - **3 Generator Agents**: Each receives identical task description and context but works completely independently. Each produces a complete solution saved with unique identifier (solution.a, solution.b, solution.c). Each uses CoT reasoning + self-critique verification internally.

2. **Multi-Judge Evaluation** — Launch 3 judges in parallel. Each receives ALL candidate solution paths and the EXACT meta-judge specification YAML. Each produces structured report with: VOTE (preferred solution), SCORES per solution, CRITERIA scores, and evidence-based justification. Parse only structured headers.

3. **Adaptive Strategy Selection** — Analyze judge vote headers:

   | Condition | Strategy | Action |
   |-----------|----------|--------|
   | Unanimous vote (all 3 prefer same) | SELECT_AND_POLISH | Polish winner with targeted improvements from judge feedback. Cherry-pick 1-2 elements from runner-ups if praised. |
   | All avg scores < 3.0 | REDESIGN | Analyze failure modes across all solutions, extract lessons learned, regenerate with new constraints and guidance |
   | Split decision (no unanimous, scores >= 3.0) | FULL_SYNTHESIS | Proceed to Phase 4 |

4. **Synthesis (FULL_SYNTHESIS only)** — Launch one synthesis agent receiving ALL candidate solutions and ALL evaluation reports. Copies superior sections when one solution wins, combines approaches when hybrid is better, fixes identified issues. Documents every decision with rationale. Must create something new, not rewrite entirely.

**Output artifacts:**

| Artifact | Location |
|----------|----------|
| Candidate solutions | `{solution}.[a\|b\|c].{ext}` |
| Evaluation reports | `.specs/reports/{name}-{date}.[1\|2\|3].md` |
| Final solution | `{output_path}` |

## Design Decisions

### Why parallel meta-judge + implementation (not sequential)
The meta-judge only needs the task description — not the implementation output — to generate evaluation criteria. Running both in parallel saves one round-trip per task or step without sacrificing judge quality. This compounds across multiple steps or targets.

### Why reuse meta-judge spec on retries (not regenerate)
The evaluation criteria for a task are invariant. If the criteria changed between attempts, scores would be incomparable and the retry agent would aim at a moving target. Reusing the same spec ensures consistent measurement across all attempts.

### Why context isolation matters for the judge
The judge must evaluate the work without being influenced by the reasoning that produced it. A fresh sub-agent with only the work and criteria provides unbiased assessment, catching blind spots the implementation agent's self-critique missed.

### Why 3 generators for competitive mode (not 2 or 5)
Three is the minimum for meaningful diversity and tie-breaking. Two solutions can differ without indicating which approach is better. Three provides enough variety to cover different solution-space regions while keeping agent count manageable. Five shows diminishing returns.

### Why adaptive strategy for competitive mode (not always full synthesis)
Full synthesis is the most expensive phase. When judges unanimously agree, synthesis wastes cost and risks degrading a superior solution by blending in inferior elements. Adaptive selection saves ~15-20% on average.

### Why requirement grouping for parallel mode (not one meta-judge per task always)
A repeatable task applied to 5 targets needs 1 meta-judge, not 5. A shared group of 2 interdependent tasks needs 1 judge, not 2. Grouping reduces total agent count by 30-60% without reducing evaluation quality.

### Why per-step meta-judge for sequential mode (not one for all steps)
Each step evaluates different criteria: interfaces check correctness and completeness; callers check consistency and lack of regressions. A single specification cannot capture these different requirements.

### Why implementation agents are always isolated (never shared in parallel mode)
Sharing an implementation agent between targets would require it to hold multiple file contexts in a single window, defeating context isolation. Meta-judges and judges can be shared because they evaluate, not implement — their contexts are about criteria, not files.

### Why failures are isolated in parallel mode (not stop-on-first-fail)
In parallel execution, one failing target should not delay or block other targets. They are independent by design. Isolated failures mean other targets complete and verify normally while only the failed target is retried or escalated.

### Why context filtering between sequential steps (not full passthrough)
Implementation agents produce detailed internal reasoning that is irrelevant to downstream steps. Passing only what is needed (interfaces, file paths, decisions) keeps sub-agent contexts clean and focused. Downstream agents can read files directly if they need implementation details.
