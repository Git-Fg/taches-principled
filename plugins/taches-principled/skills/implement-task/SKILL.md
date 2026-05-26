---
name: implement-task
description: "Execute refined task implementations with automated quality verification. Each step spawns a developer agent, then an independent judge verifies. Iterates until quality threshold is met."
when_to_use: |
  Use when the user says:
  - "implement this task"
  - "build this"
  - "start working on the task"
  - "/implement"
  - "execute the implementation"
  - "run the implementation for X"
  - "start implementing this feature"
  - "begin building this"
  - "carry out the implementation steps"
  - "put this plan into action"
  IMMEDIATELY after a task has been refined and is ready for implementation — verification gates are mandatory.
  CONTRAST with execute-plans: That skill executes PLAN.md files from .principled/plans/; this skill executes refined task files from .specs/tasks/ (todo/, in-progress/, done/).
argument-hint: "[task file] [--continue] [--refine] [--human-in-the-loop] [--target-quality X.X] [--skip-judges]"
---

## Decision Router

IF user needs to implement a refined task → execute implementation steps with per-step verification
IF user needs to continue an interrupted implementation → use `--continue` to resume from last completed step
IF user manually fixed project files → use `--refine` to detect changes and re-verify affected steps
IF user wants human review after each step → use `--human-in-the-loop`
IF user wants fast implementation without verification gates → use `--skip-judges`
IF user is done implementing → verify completion and move task to done

# Implement Task

Orchestrate multi-step task implementation with automated quality verification. Each implementation step spawns a dedicated subagent, then verified by an independent judge subagent. Supports three verification patterns (simple skip, critical panel, per-item judges) plus final Definition of Done verification.

The orchestrator spawns and aggregates but never implements or evaluates directly. Every implementation step gets a dedicated agent. Every verification gets an independent judge. Context protection is paramount — reading artifacts yourself causes context overflow and command loss, which is the most common failure mode in multi-step workflows.

## Core Principle

Context is the orchestrator's most precious resource. Protecting it means delegating everything: implementations to developer agents, evaluations to judge agents, and reading only the task file. The orchestrator that reads artifacts stops being able to orchestrate.

## Configuration

### Argument Definitions

| Argument | Format | Default | Description |
|----------|--------|---------|-------------|
| `task-file` | Path or filename | Auto-detect | Task file to implement. If omitted, auto-select from todo/ or in-progress/. |
| `--continue` | flag | false | Resume from last completed step. Launches judge to verify last incomplete step state, then resumes from there. |
| `--refine` | flag | false | Detect git changes to project files, map to affected implementation steps, re-verify from earliest affected step. |
| `--human-in-the-loop` | `[step,step,...]` | None | Pause for human review after specified steps. Without step numbers, pauses after every step. |
| `--target-quality` | `X.X` or `X.X,Y.Y` | `4.0,4.5` | Single value sets both standard and critical threshold. Two comma-separated values set standard,critical. |
| `--max-iterations` | `N` or `unlimited` | `3` | Maximum fix-to-verify cycles per step. `unlimited` iterates until threshold is met. |
| `--skip-judges` | flag | false | Skip all verification — steps proceed directly after implementation without quality gates |

### Threshold Resolution

- Standard components threshold: default 4.0/5.0. Used for steps not marked as critical.
- Critical components threshold: default 4.5/5.0. Used for steps marked as critical in the task file.
- Single `--target-quality X.X` sets both thresholds to the same value.
- Two values `--target-quality X.X,Y.Y` set standard and critical thresholds separately.

### Usage Examples

```bash
# Implement a specific task
/implement add-validation.feature.md

# Auto-select from todo/ or in-progress/
/implement

# Continue from interruption
/implement add-validation.feature.md --continue

# Refine after manual code edits
/implement add-validation.feature.md --refine

# Human review after every step
/implement add-validation.feature.md --human-in-the-loop

# Higher quality threshold for both standard and critical
/implement critical-api.feature.md --target-quality 4.5
```

## Phase 0: Select Task and Move to In-Progress

### Step 0.1: Resolve Task File

If the user provides a task file name or path as the first positional argument:
- Search in order: `in-progress/`, `todo/`, `done/`
- Set `TASK_FOLDER` to the matching folder
- Error if not found in any folder

If argument is empty or contains only flags:
- Check `in-progress/` first: `ls .specs/tasks/in-progress/*.md`
  - If exactly 1 file: select it as the task
  - If multiple files: list them and ask user which to continue
  - If no files: continue to check `todo/`
- Check `todo/`: `ls .specs/tasks/todo/*.md`
  - If exactly 1 file: select it
  - If multiple files: list them and ask user which to implement
  - If no files: report "No tasks available. Create one first." and stop

### Step 0.2: Move to In-Progress

If task is in `todo/`:
```bash
git mv .specs/tasks/todo/<TASK_FILE> .specs/tasks/in-progress/
# Fallback: mv .specs/tasks/todo/<TASK_FILE> .specs/tasks/in-progress/
```

If task is already in `in-progress/`, keep it there.

### Step 0.3: Handle --continue Mode

1. Parse the task file for `[DONE]` markers on step titles (e.g., `### Step 2: Create Service [DONE]`)
2. Find the highest step number marked `[DONE]` — this is `LAST_COMPLETED_STEP`
3. If `LAST_COMPLETED_STEP > 0`:
   - Launch a judge subagent to verify the artifacts from that completed step
   - If judge PASS: set `RESUME_FROM = LAST_COMPLETED_STEP + 1`
   - If judge FAIL: set `RESUME_FROM = LAST_COMPLETED_STEP` (re-implement the step)
4. If `LAST_COMPLETED_STEP == 0`: set `RESUME_FROM = 1`
5. In Phase 2, skip all steps before `RESUME_FROM`

### Step 0.4: Handle --refine Mode

1. **Detect changed project files** (not task file — the project's source files):

   ```bash
   STAGED=$(git diff --cached --name-only)
   UNSTAGED=$(git diff --name-only)
   ```

   Determine comparison mode:

   | Staged | Unstaged | Compare Against | Command |
   |--------|----------|-----------------|---------|
   | Yes | Yes | Unstaged only | `git diff --name-only` |
   | Yes | No | Last commit | `git diff HEAD --name-only` |
   | No | Yes | Last commit | `git diff HEAD --name-only` |
   | No | No | No changes, inform user | - |

2. **Load the task file** and extract step-to-file mapping from each step's "Expected Output" section, subtask descriptions mentioning file paths, and `#### Verification` artifact paths.

3. **Map changed files to steps**: for each changed file, find which step(s) created or modified it. Build a set of affected step numbers.

4. **Determine scope**: `REFINE_FROM` = minimum of affected step numbers. All steps from `REFINE_FROM` onwards need re-verification. Steps before `REFINE_FROM` are preserved as-is.

5. **Pass context**: Provide the git diff output for affected files as `USER_CHANGES_CONTEXT` to both judge and implementation subagents. Sub-agents must build upon user fixes, not overwrite them.

### Step 0.5: Display Configuration

```markdown
| Setting | Value |
|---------|-------|
| **Task File** | `<path>` |
| **Standard Threshold** | X.X/5.0 |
| **Critical Threshold** | Y.Y/5.0 |
| **Max Iterations** | N |
| **Human Checkpoints** | `<steps or None>` |
| **Skip Judges** | true/false |
| **Continue Mode** | true/false |
| **Refine Mode** | true/false |
```

## Phase 1: Load and Analyze Task

This is the ONLY phase where the orchestrator reads a file. After this, all implementation details come from subagent reports.

1. **Read the task file once** — extract the `## Implementation Process` section
2. **Parse all steps** with their dependencies, parallel annotations (`Parallel with:`), and `#### Verification` sections
3. **Classify each step's verification level**:

| Level | When | Judge Config |
|-------|------|--------------|
| None | Simple ops (mkdir, delete, config) | Skip (Pattern A) |
| Single Judge | Non-critical artifacts | 1 judge, standard threshold (Pattern B) |
| Panel of 2 Judges | Critical artifacts | 2 judges, median voting, critical threshold (Pattern B) |
| Per-Item Judges | Multiple similar items | 1 judge per item, parallel (Pattern C) |

4. **Create progress tracking todo list** for all steps

## Phase 2: Execute Implementation Steps

Execute steps in dependency order. Steps marked `Parallel with:` run simultaneously. Each step follows one of three patterns.

### Pattern A: Simple Step (No Verification)

Used for: directory creation, configuration changes, deletions, and other straightforward operations.

**Spawn implementation subagent:**

```
Implement Step [N]: [Step Title]

Task File: <TASK_PATH>
Step Number: [N]

Execute ONLY Step [N]: [Step Title]. Do NOT execute any other steps.

Follow the Expected Output and Success Criteria exactly.

When complete, report:
1. Files created/modified (paths)
2. Confirmation that success criteria are met
3. Any issues encountered
```

**Spawn Footer**
When spawned as a subagent:
- Your context starts fresh — no access to prior conversation or other subagents' outputs
- Return structured output (file paths, findings, and any artifacts) to the orchestrator
- If you encounter anything unexpected or have any question or doubt, stop and report back
- Do not proceed silently on assumptions.

**Failure Signal**
If unable to complete the task, return: {"status": "failed", "reason": "...", "completed_portion": "...", "retry_possible": true/false}

**After completion:**
- Use the agent's report to know what was created — do NOT read the created files
- Mark step complete: update task file with `[DONE]` on step title, subtasks as `[X]`
- Update progress tracking

---

### Pattern B: Critical Step (Panel of 1 or 2 Judges)

Used for: artifacts requiring evaluation confidence. Single judge for non-critical, panel of 2 for critical.

**1. Spawn implementation subagent** (same as Pattern A with self-critique added):

```
Implement Step [N]: [Step Title]

Task File: <TASK_PATH>
Step Number: [N]

Execute ONLY Step [N]. Follow Expected Output and Success Criteria exactly.

When complete, report:
1. Files created/modified (paths)
2. Confirmation of completion
3. Self-critique summary (what could be improved)
```

**Spawn Footer**
When spawned as a subagent:
- Your context starts fresh — no access to prior conversation or other subagents' outputs
- Return structured output (file paths, findings, and any artifacts) to the orchestrator
- If you encounter anything unexpected or have any question or doubt, stop and report back
- Do not proceed silently on assumptions.

**Failure Signal**
If unable to complete the task, return: {"status": "failed", "reason": "...", "completed_portion": "...", "retry_possible": true/false}

**2. After completion**, receive the agent's report and note artifact paths. Do NOT read artifacts.

**3. Spawn judge subagent(s):**

For Single Judge (standard threshold): launch 1 judge.
For Panel of 2 Judges (critical threshold): launch 2 judges in parallel.

Each judge receives:
```
Evaluate artifact at: <artifact_path from implementation report>

Rubric: <paste from step's #### Verification section>

Context:
- Task File: <TASK_PATH>
- Verify Step [N] ONLY: [Step Title]
- Threshold: <threshold for step type>

Score each criterion 1-5 with chain-of-thought justification BEFORE the score.
You can run tests, check imports, validate syntax to verify the artifact.

Return: scores per criterion with evidence, overall weighted score, PASS/FAIL, specific improvements if FAIL.
```

**Spawn Footer**
When spawned as a subagent:
- Your context starts fresh — no access to prior conversation or other subagents' outputs
- Return structured output (file paths, findings, and any artifacts) to the orchestrator
- If you encounter anything unexpected or have any question or doubt, stop and report back
- Do not proceed silently on assumptions.

**Failure Signal**
If unable to complete the task, return: {"status": "failed", "reason": "...", "completed_portion": "...", "retry_possible": true/false}

**4. Aggregate results (panel of 2):**
- Median per criterion = average of both scores
- Flag high-variance criteria (difference > 2.0)
- Weighted overall = sum(criterion_median x weight)
- PASS if overall >= threshold

**5. On FAIL:**
- Re-launch a implementation subagent with judge feedback
- Re-verify with judge(s)
- Iterate until PASS or MAX_ITERATIONS reached
- If MAX_ITERATIONS reached and still failing, log warning and proceed to next step

**6. On PASS:** Mark step complete. If step is in HUMAN_IN_THE_LOOP_STEPS, trigger human-in-the-loop checkpoint.

---

### Pattern C: Multi-Item Step (Per-Item Judges)

Used for: steps creating multiple similar items (validators, handlers, endpoints, test cases).

**1. Spawn implementation subagents in parallel** — one per item:

```
Implement Step [N], Item: [Item Name]

Task File: <TASK_PATH>
Step Number: [N]
Item: [Item Name]

Create ONLY [Item Name] from Step [N]. Do NOT create other items or steps.

When complete, report:
1. File path created
2. Confirmation of completion
3. Self-critique summary
```

**Spawn Footer**
When spawned as a subagent:
- Your context starts fresh — no access to prior conversation or other subagents' outputs
- Return structured output (file paths, findings, and any artifacts) to the orchestrator
- If you encounter anything unexpected or have any question or doubt, stop and report back
- Do not proceed silently on assumptions.

**Failure Signal**
If unable to complete the task, return: {"status": "failed", "reason": "...", "completed_portion": "...", "retry_possible": true/false}

**2. After all complete**, collect reports and artifact paths. Do NOT read artifacts.

**3. Spawn evaluation subagents in parallel** — one per item:

Each judge:
```
Evaluate artifact at: <item_path>

Rubric: <paste from step's #### Verification section>

Context:
- Task File: <TASK_PATH>
- Step [N]: [Step Title]
- Verify ONLY this item: [Item Name]
- Threshold: <threshold>

Score each criterion 1-5 with chain-of-thought justification BEFORE the score.

Return: scores with evidence, overall score, PASS/FAIL, improvements if FAIL.
```

**Spawn Footer**
When spawned as a subagent:
- Your context starts fresh — no access to prior conversation or other subagents' outputs
- Return structured output (file paths, findings, and any artifacts) to the orchestrator
- If you encounter anything unexpected or have any question or doubt, stop and report back
- Do not proceed silently on assumptions.

**Failure Signal**
If unable to complete the task, return: {"status": "failed", "reason": "...", "completed_portion": "...", "retry_possible": true/false}

**4. Aggregate results:** items_passed / items_total

**5. On any FAIL:**
- Re-implement only the failing items with judge feedback
- Re-verify only failing items
- Iterate until ALL PASS or MAX_ITERATIONS reached

**6. On ALL PASS:** Mark step complete. If step is in HUMAN_IN_THE_LOOP_STEPS, trigger human-in-the-loop checkpoint.

---

### Human-in-the-Loop Checkpoint

Triggered after a step PASSES (not on FAIL) if the step number is in `HUMAN_IN_THE_LOOP_STEPS` (or if ALL steps are enabled):

```markdown
---
## Human Review Checkpoint - Step [N]

**Step:** [Step Title]
**Step Type:** standard/critical
**Judge Score:** X.X/[threshold]
**Status:** PASS

**Artifacts Created/Modified:**
- <artifact_path>

**Judge Feedback:**
<feedback summary>

> Continue? [Y/n/feedback]:
---
```

If user provides feedback: incorporate into next step or re-implement current step with feedback.
If user says "n": pause workflow, report current progress.

### Verification Level Determination

When a step's `#### Verification` section specifies:
- **None** → Pattern A (skip verification)
- **Single Judge** → Pattern B with 1 judge, standard threshold
- **Panel of 2 Judges** → Pattern B with 2 judges, critical threshold
- **Per-Item Judges** → Pattern C, standard threshold

If the step is marked as critical in the task file metadata, always use the critical threshold regardless of verification level.

## Phase 3: Final Verification (Definition of Done)

After all implementation steps complete and pass their per-step verification:

1. **Spawn a DoD verification subagent**:

```
Verify all Definition of Done items in the task file.

Task File: <TASK_PATH>

Your task:
1. Read the "## Definition of Done (Task Level)" section
2. Go through each checkbox item one by one
3. For each item, verify by: running tests, checking compilation, verifying file existence, checking patterns and linting
4. Mark each passed item with [X] in the task file
5. Return structured report:

| Item | Status | Evidence |
|------|--------|----------|
| <item> | PASS/FAIL/BLOCKED | <evidence> |
| ... | ... | ... |

Overall pass rate: X/Y
Failing items with specific reasons.
```

**Spawn Footer**
When spawned as a subagent:
- Your context starts fresh — no access to prior conversation or other subagents' outputs
- Return structured output (file paths, findings, and any artifacts) to the orchestrator
- If you encounter anything unexpected or have any question or doubt, stop and report back
- Do not proceed silently on assumptions.

**Failure Signal**
If unable to complete the task, return: {"status": "failed", "reason": "...", "completed_portion": "...", "retry_possible": true/false}

2. **Review results**: If all items PASS, verify that `[X]` markers were written by checking the end of the task file.

3. **On any FAIL**: Launch fix subagents for each failing item with the failure details. After fixes, re-launch the DoD verification (step 1). Iterate until all PASS.

## Phase 4: Move Task to Done

After DoD verification passes:

```bash
git mv .specs/tasks/in-progress/<TASK_FILE> .specs/tasks/done/
# Fallback: mv .specs/tasks/in-progress/<TASK_FILE> .specs/tasks/done/
```

## Phase 5: Report

Generate the implementation summary:

```markdown
### Implementation Summary

| Step | Title | Status | Verification | Score | Iterations |
|------|-------|--------|--------------|-------|------------|
| 1 | [Title] | PASS | Skipped | N/A | 1 |
| 2 | [Title] | PASS | Panel (2) | 4.5/5 | 1 |
| ... | ... | ... | ... | ... | ... |

### Verification Summary

| Metric | Value |
|--------|-------|
| Total steps | X |
| Verified steps | Y |
| Passed first try | Z |
| Required iteration | W |
| Total fix-verify cycles | V |

### Definition of Done

| Item | Status | Evidence |
|------|--------|----------|
| <DoD item> | PASS | <evidence> |

**Task Status:** DONE — `.specs/tasks/done/<filename>`
```

Task complete. Consider reviewing changes with `refine simplify` or capturing learnings from this implementation session via `refine memorize`.

## Usage Walkthrough

### Example: Implementing a Feature with Verification

```
User: /implement add-validation.feature.md

Phase 0: Task selected: .specs/tasks/todo/add-validation.feature.md
         Moving to in-progress...

Phase 1: Task loaded. 4 steps identified:
  Step 1: Create directories (None)
  Step 2: Create ValidationService (Panel of 2 Judges)
  Step 3: Create validators (Per-Item Judges, 3 items)
  Step 4: Integration test (Single Judge)

Phase 2: Executing...

Step 1: Developer agent → directories created. Marked DONE.

Step 2: Developer agent → service + tests created.
  Judge 1: 4.3/5.0 PASS | Judge 2: 4.5/5.0 PASS
  Panel: 4.4/5.0 ✅ Marked DONE.

Step 3: 3 developer agents (parallel) → 3 validators created.
  3 judges (parallel) → 2 PASS, 1 FAIL (weak edge case coverage)
  Fix + re-judge → ALL PASS ✅ Marked DONE.

Step 4: Developer agent → integration test.
  Judge → 4.2/5.0 PASS ✅ Marked DONE.

Phase 3: DoD verification → 5/5 items PASS ✅

Phase 4: Moved to .specs/tasks/done/

Phase 5: Summary generated.
```

### Example: Handling Verification Failure with Iteration

```
Step 3: ValidationService implementation complete.
Launching 2 judges...

Judge 1: 3.5/5.0 FAIL | Judge 2: 3.2/5.0 FAIL
Issues: Missing edge case tests (2.5/5), custom Result type instead of project standard (3.0/5)

Iteration 1: Developer agent fixes issues...
Re-launching judges...
Judge 1: 4.2/5.0 PASS | Judge 2: 4.4/5.0 PASS
Panel: 4.3/5.0 ✅ Marked DONE.
```

## Verification Specifications Reference

Task files define verification requirements in `#### Verification` sections within each implementation step.

### Section Structure

```markdown
#### Verification

**Level:** None | Single Judge | Panel of 2 Judges | Per-Item Judges
**Artifact:** `<file_path>`, `<file_path>`, ...
**Threshold:** X.X/5.0 (optional — defaults to standard or critical threshold)

**Rubric:**

| Criterion | Weight | Description |
|-----------|--------|-------------|
| <Name> | 0.XX | <What to evaluate, specific and measurable> |
| ... | ... | ... |
```

### Rubric Requirements
- Weights MUST sum to 1.0
- Each criterion has a clear, measurable description
- Typically 3-6 criteria per rubric
- Descriptions use concrete terms (file paths, function names, behaviors)

### Scoring Scale (per criterion)

| Score | Label | Meaning |
|-------|-------|---------|
| 1 | Poor | Missing essential elements, fundamental misunderstanding |
| 2 | Below Average | Some correct elements, significant gaps |
| 3 | Adequate | Meets basic requirements, functional but minimal |
| 4 | Good | Meets all requirements, few minor issues |
| 5 | Excellent | Exceptional quality, exceeds expectations |

## Evaluation Integrity Rules

- **Score 5.0/5.0 is a hallucination** — reject and re-run the judge. Perfect scores are practically impossible in rigorous evaluation.
- **Missing numerical score** — reject and re-run the judge.
- **Excessively long reports** instead of structured evaluation — reject and re-run.
- **Use thresholds from configuration**, not hardcoded values.
- **After MAX_ITERATIONS reached**: proceed to next step with warning — do not block indefinitely.
- **Chain-of-thought required**: judges must provide justification BEFORE the score for each criterion, not after.

## Panel Voting Algorithm (Pattern B with 2 Judges)

1. **Collect**: table with each criterion and both judge scores
2. **Median**: average of both scores per criterion
3. **High variance check**: if |score1 - score2| > 2.0, flag for potential disagreement
4. **Weighted overall**: sum(median x weight) for all criteria
5. **Pass/fail**: overall >= threshold

If high variance is detected: present both evaluators' reasoning to the user and ask for resolution. If user declines, use the median (conservative).

## Error Handling

### Implementation Sub-Agent Failure
If a developer agent reports failure: present the failure details to the user, ask clarifying questions that could help resolve, then re-launch the subagent with clarifications incorporated.

### Judge Returns FAIL
Automatic retry: re-launch the implementation subagent with judge feedback included. The implementation subagent must address the specific failing criteria.

If the step is in HUMAN_IN_THE_LOOP_STEPS: trigger human checkpoint after the re-implementation but before the next judge retry.

After MAX_ITERATIONS (default 3) reached: proceed to next step automatically. Log a warning in the final summary. Do not ask permission unless the step is in HUMAN_IN_THE_LOOP_STEPS.

### Judge Disagreement (difference > 2.0)
Present both perspectives with evidence. Ask the user to resolve: "Judges disagree on [criterion]. Your decision?" Proceed based on user response.

### Refine Mode Edge Cases
- **No changes detected**: "No project file changes detected since last commit. Make edits first, then run --refine again."
- **Changes do not map to steps**: "Changed files don't match any implementation step's expected outputs. Verify manually or run without --refine."

## Design Decisions

**Implementation patterns are documented in {baseDir}/references/patterns.md.**

### Separate standard and critical thresholds
Using a higher threshold for critical paths (4.5 vs 4.0) focuses quality effort where it matters most.

### Refine mode preserves user changes
When users manually edit source files, `--refine` detects changes and re-verifies consistency.

### Continue mode for resilience
`--continue` detects where work stopped and resumes including re-verifying the boundary step.
