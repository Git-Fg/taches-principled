---
name: execute
description: "Execute tasks with fresh subagent dispatch: simple dispatch, meta-judge verification with retry loop, or plan-driven execution with code review gates"
when_to_use: |
  When user says 'execute this', 'dispatch subagent', 'launch agent for task', 'implement with verification', 'delegate this', 'implement this plan', 'run in background'. IMMEDIATELY when user wants to delegate focused tasks with context isolation. FIRST when task requires automatic model selection, independent verification, or parallel execution. DO NOT use when the task is a simple one-liner needing only basic dispatch — use a basic subagent launch instead. DO NOT use when the task needs iterative meta-judge verification loops — use verify mode instead.
argument-hint: "Task description [--mode dispatch|verify|plan-driven] [--model opus|sonnet|haiku] [--plan <path>]"
---

## Decision Router

IF single self-contained task with quality verification and iterative refinement needed → VERIFY mode: meta-judge + implementor + judge with retry loop
IF implementing a plan with multiple tasks and code review between them → PLAN-DRIVEN mode: fresh subagent per task, code review as quality gate
IF simple single-task dispatch with context isolation and no verification overhead → DISPATCH mode: auto model selection with CoT prefix and self-critique suffix
IF executing a plan with independent tasks sharing no state → parallel plan mode: spawn one subagent per task simultaneously
IF executing a plan with sequential or dependent tasks → sequential plan mode: spawn one subagent per task in order
IF investigating 3+ unrelated issues without shared state → parallel investigation mode: group by subsystem, spawn per domain
IF tasks share state or files → do NOT parallelize; use sequential with code review between each
IF retries exceed max without passing → escalate to user with failure analysis

# Execute

Execute tasks by dispatching fresh subagents with isolated context. Three modes share a common principle but differ in verification strategy and retry policy.

## Core Principle

Context isolation is the primary benefit of subagents. Each subagent works in a clean context window without accumulated context pollution. The orchestrator owns all cognition; the subagent owns only execution.

## Mode 1: DISPATCH

Simple subagent dispatch with automatic model selection, CoT reasoning, and self-critique verification. No meta-judge overhead.

### When to use

Single focused task needing context isolation without quality verification gates. Best for single requests where a dedicated agent handles implementation, research, or analysis.

### Process

**Phase 1: Task Analysis** — Determine type (implementation, research, documentation, review, architecture, testing, transformation), complexity (high/medium/low), output size (large/medium/small), and domain match.

**Phase 2: Model Selection**

| Profile | Model |
|---------|-------|
| Complex reasoning (architecture, design, critical decisions) | Opus |
| Specialized domain with complexity | Opus + specialized agent |
| Non-complex but long output | Sonnet |
| Simple and short | Haiku |
| Default (uncertain) | Opus |

**Phase 3: Specialized Agent Matching** — Use a specialized agent when the task clearly benefits from domain expertise (developer for code, researcher for investigation, architect for design). Skip specialization for trivial tasks. If no matching specialist exists, use general-purpose.

**Phase 4: Construct Sub-Agent Prompt** — Build with three mandatory components:

1. **CoT Prefix (first):** "Let me understand what is being asked... let me break this down... let me consider what could go wrong... let me verify my approach before proceeding"
2. **Task Body:** Task description, constraints, context, expected output format
3. **Self-Critique Suffix (last):** Generate 5 verification questions specific to this task, answer each with evidence, revise if gaps found. Must not submit until all questions have satisfactory answers.

**Phase 5: Dispatch** — Use the Task tool with selected model. Pass only context relevant to this specific task — never the entire conversation history.

### Output

The subagent returns its work directly. The orchestrator reviews output quality before accepting.

### Why CoT prefix + self-critique suffix

The CoT prefix forces structured reasoning before action, preventing the "rush to implement" failure mode. The self-critique suffix provides a quality gate before submission, catching the most common errors (incomplete requirements, missed edge cases, pattern violations).

### Why auto model selection

Model tiering saves cost without sacrificing quality. Haiku handles ~30% of real-world tasks (mechanical updates, documentation tweaks). Opus reserved for the ~40% that genuinely need reasoning depth.

## Mode 2: VERIFY

Meta-judge verification with judge + retry loop. Uses the meta-judge evaluation pattern for independent quality assessment.

### When to use

Single self-contained task needing implementation with quality verification and iterative refinement. Not for multi-step workflows or parallel targets.

### Process

1. **Task Analysis** — Assess complexity (high/medium/low), risk, and scope. Default model: Opus.
2. **Parallel Dispatch** — Spawn meta-judge AND implementation agent in a single message. Meta-judge MUST be first in dispatch order so it observes the task specification before the implementation agent modifies any files. Meta-judge returns only the YAML specification. Implementation agent receives CoT prefix, task body with expected output, and self-critique suffix producing a Summary section.
3. **Judge Verification** — Extract meta-judge spec YAML and implementation Summary. If pre-existing changes exist in the codebase, include a Pre-existing Changes section so the judge attributes work correctly. Dispatch judge with EXACT meta-judge spec.
4. **Retry Loop** — Score >= 4.0 = PASS. Score >= 3.0 with all low-priority issues = PASS. Score < 4.0 with retries remaining = retry with judge feedback (max 2 retries). Score < 4.0 after max retries = escalate to user with failure analysis.
5. **Final Report** — Task summary, verification history (scores per attempt), files modified, key changes, optional improvements from judge.

### Sequential Steps (VERIFY variant)

Decompose a complex task into ordered, dependent subtasks with per-step meta-judge + judge and context passing between steps.

**Decomposition patterns:**

| Task Type | Decomposition |
|-----------|--------------|
| Interface change | Interface → Implementation → Consumers → Tests |
| Feature addition | Core logic → Integration → API layer |
| Refactoring | Extract/modify core → Internal references → External references |
| Multi-layer change | Data layer → Business layer → API layer → Client layer |

For each step in order:
- **Parallel Dispatch**: Spawn meta-judge (step-specific evaluation spec) AND implementation agent in a single message. Meta-judge first. Meta-judge includes overall task, this step's requirements, previous steps context, and artifact type. Implementation agent must end with "Context for Next Steps" section.
- **Judge Verification**: dispatch judge with exact meta-judge spec for this step. Include "Pre-existing Changes" section if previous steps modified files.
- **Verdict**: Score >= 4.0 = PASS. Score >= 3.0 with low-priority issues = PASS. Score < 4.0 with retries remaining = retry with judge feedback (max 3 retries per step). Reuse same meta-judge spec across all retries.
- **Context Passing**: After a step passes, extract only relevant information for remaining steps: files modified, key changes, new interfaces/APIs, decisions affecting later steps, warnings. Keep under 200 words per step. If cumulative context exceeds ~500 words, summarize older steps more aggressively.

### Parallel Targets (VERIFY variant)

Execute multiple independent tasks simultaneously with requirement grouping to minimize agent count, plus isolated retries per target.

1. **Independence Validation** — Verify: no shared files between targets, no target reads another's output, no shared mutable state, execution order does not matter. If any check fails, inform user and recommend sequential mode.

2. **Requirement Grouping:**

   | Grouping | When | Meta-Judges | Judges |
   |----------|------|-------------|--------|
   | REPEATABLE | Same task applied to different targets | ONE shared (reusable spec, generic language) | One per target, SAME reusable spec |
   | SHARED | Interdependent tasks reviewed together | ONE combined (covers all tasks) | ONE for entire group, combined spec |
   | INDEPENDENT | Fully separate, no grouping benefit | One per task | One per task |

   **Decision rule:** Default to INDEPENDENT when uncertain. Over-grouping risks incorrect evaluation specs. Implementation agents are always isolated — one per task, never shared.

3. **Meta-Judge Dispatch (ALL in parallel)** — Spawn one meta-judge per group/independent task. Spawn each implementor immediately after its meta-judge completes (do not wait for all meta-judges).

4. **Parallel Implementation** — Spawn ALL implementation agents in a single message. Each with CoT prefix, task body (target-specific), and self-critique suffix. Each ends with Summary section.

5. **Judge Verification** — After ALL implementors complete, dispatch judges per grouping. Include "Pre-existing or Expected Parallel Changes" section. Parse only structured headers.

6. **Retry Loop** — Isolated retries per target (max 3). For SHARED groups: re-launch only the failing implementor(s), then re-launch shared judge against ALL changes (passed + retried). Failed targets are isolated and do not affect other targets.

### Competitive Generation (VERIFY variant)

High-stakes best-of-N where quality matters more than speed.

1. **Competitive Generation + Meta-Judge** — Spawn 4 agents in a single message. Meta-judge first in dispatch order:
   - **Meta-Judge**: Generates comparative evaluation specification YAML for evaluating across multiple solutions.
   - **3 Generator Agents**: Each receives identical task description and context but works completely independently. Each produces a complete solution saved with unique identifier (solution.a, solution.b, solution.c). Each uses CoT reasoning + self-critique verification internally.

2. **Multi-Judge Evaluation** — Spawn 3 judges in parallel. Each receives ALL candidate solution paths and the EXACT meta-judge specification YAML. Each produces structured report with: VOTE (preferred solution), SCORES per solution, CRITERIA scores, and evidence-based justification.

3. **Adaptive Strategy Selection:**

   | Condition | Strategy | Action |
   |-----------|----------|--------|
   | Unanimous vote (all 3 prefer same) | SELECT_AND_POLISH | Polish winner with targeted improvements from judge feedback. |
   | All avg scores < 3.0 | REDESIGN | Analyze failure modes, regenerate with new constraints. |
   | Split decision (no unanimous, scores >= 3.0) | FULL_SYNTHESIS | Proceed to synthesis phase. |

4. **Synthesis (FULL_SYNTHESIS only)** — Spawn one synthesis agent receiving ALL candidate solutions and ALL evaluation reports. Must create something new, not rewrite entirely.

### Why parallel meta-judge + implementation

The meta-judge only needs the task description — not the implementation output — to generate evaluation criteria. Running both in parallel saves one round-trip per task or step without sacrificing judge quality.

### Why reuse meta-judge spec on retries

The evaluation criteria for a task are invariant. If the criteria changed between attempts, scores would be incomparable. Reusing the same spec ensures consistent measurement across all attempts.

### Why requirement grouping for parallel mode

A repeatable task applied to 5 targets needs 1 meta-judge, not 5. Grouping reduces total agent count by 30-60% without reducing evaluation quality.

## Mode 3: PLAN-DRIVEN

Plan-based dispatch with code review as quality gate. Fresh subagent per task with review between tasks.

### When to use

Implementing a plan with multiple tasks. Each subagent gets clean context focused on its specific task, avoiding context pollution from accumulated session state.

### Sequential Execution

1. Load plan and create task tracking
2. For each task in order:
   - Dispatch a fresh subagent with exact task specification from the plan, relevant context, and expected output format
   - Sub-agent implements with CoT reasoning and self-critique, then reports back with summary
   - Dispatch a code review subagent to check the work against plan requirements
   - Fix any Critical or Important issues before proceeding
3. Final review after all tasks complete — validate overall architecture and plan completeness

### Parallel Execution

1. Load plan and group tasks by dependency
2. Dispatch one subagent per independent task simultaneously — each receives focused scope, clear goals, and output constraints
3. Review all outputs after all agents return — check for conflicts, run full test suite
4. Fix integration issues if found

### Parallel Investigation

1. Group failures by file or subsystem — each domain must be independent
2. Each agent gets specific scope (one file/subsystem), clear goal (fix these tests), constraints (don't change other code)
3. All agents run concurrently
4. Review summaries, verify no conflicts, run full suite

### Why code review between tasks

Catching issues immediately prevents cascading failures where later tasks build on broken foundations. The cost of fixing an issue grows with each downstream task that depends on it.

## Model Selection (all modes)

| Profile | Model |
|---------|-------|
| Complex reasoning (architecture, design, critical decisions) | Opus |
| Medium complexity, patterned work | Sonnet |
| Simple transformations | Haiku |
| Default (uncertain) | Opus |

For parallel modes, use the same model tier for all concurrent agents.

## Quality Gates

- Review output after each task (sequential) or after batch (parallel)
- Fix Critical issues immediately, Important issues before next task
- Run full test suite after integration
- Stop and ask for help when: a blocker is hit mid-task, plan has critical gaps, verification fails repeatedly, or instructions are unclear

## Failure Signal

```json
{"status": "failed" | "success", "reason": "...", "completed_portion": "...", "retry_possible": true/false}
```

| status | reason | completed_portion | retry_possible |
|--------|--------|-------------------|----------------|
| `failed` | `subagent-timeout` | Task partially completed | `true` (relaunch with same spec) |
| `failed` | `subagent-invalid-output` | Output missing required structure or summary | `true` (relaunch with stricter output constraints) |
| `failed` | `meta-judge-timeout` | No evaluation spec produced | `true` |
| `failed` | `meta-judge-invalid-spec` | Malformed or unparseable YAML spec | `true` (relaunch meta-judge) |
| `failed` | `implementation-failed` | Implementor crashed or produced no output | `true` (relaunch with same spec) |
| `failed` | `verification-failed` | Score < 4.0 after max retries | `false` (escalate to user) |
| `failed` | `retry-exhausted` | Max retries reached without passing | `false` (escalate with failure analysis) |
| `failed` | `parallel-conflict` | Two subagents modified same file | `false` (revert and execute sequentially) |
| `failed` | `code-review-failed` | Code reviewer crashed or produced invalid report | `true` (relaunch code reviewer) |
| `failed` | `model-selection-failed` | Model unavailable or API error | `true` (retry with fallback model) |
| `failed` | `context-overflow` | Task scope exceeds model context limits | `false` (decompose task manually) |
| `failed` | `parallel-target-failed` | One or more targets failed isolated retry | `true` (already retried, escalate failed targets) |
| `failed` | `step-timeout` | Sequential step exceeded expected duration | `true` (relaunch step with timeout) |
| `failed` | `context-passing-error` | Required context missing for next step | `true` (re-examine previous step output) |
| `failed` | `plan-load-failed` | Plan file unreadable or malformed | `false` (user must fix plan) |
| `failed` | `task-unclear` | Task specification missing or contradictory | `false` (user must clarify) |

**Fields:**
- `status`: `"failed"` when task cannot complete; `"success"` when task verified and complete
- `reason`: Specific failure mode from the options above
- `completed_portion`: What portion completed (e.g., "N/N tasks complete, M code reviews passed")
- `retry_possible`: `true` if recoverable with targeted retry; `false` if requires structural change or manual intervention