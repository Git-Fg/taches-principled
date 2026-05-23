---
name: plan-task
description: "Refine draft tasks into implementation-ready specifications with analysis, architecture, decomposition, and verification rubrics. Multi-phase workflow with independent quality gates."
when_to_use: |
  Use when the user says:
  - "refine this task"
  - "plan this out"
  - "make this actionable"
  - "/plan"
  - "turn this into a spec"
  - "break this down into steps"
  - "refine my task into an implementation plan"
  - "I have a draft task, flesh it out"
  - "make this ready for implementation"
  - "convert this user story to executable steps"
  IMMEDIATELY after a task is drafted — BEFORE implementation begins.
argument-hint: ".specs/tasks/draft/<file>.md [--fast] [--target-quality X.X] [--skip-judges] [--human-in-the-loop phase,phase,...]"
---

## Decision Router

IF user needs to refine a draft task into a detailed specification → run full multi-phase refinement workflow
IF user needs quick refinement with minimal quality gates → use `--fast` mode
IF user wants to resume an interrupted refinement → use `--continue [stage]`
IF user manually edited a task and needs incremental re-refinement → use `--refine`
IF user wants only business analysis no architecture → use `--included-stages business analysis,decomposition`
IF user is done working on this task → proceed to implementation

# Plan Task

Refine a draft task specification through a coordinated multi-phase workflow. The workflow runs parallel analysis (research, codebase impact, business requirements), synthesizes findings into architecture, decomposes into implementation steps, reorganizes for parallel execution, and adds verification rubrics. Each phase includes an independent quality evaluation before the next phase proceeds.

The original user intent is preserved throughout. Refinement adds layers of analysis on top without overwriting what the user asked for.

## Core Principle

Specification quality is a prerequisite for implementation speed. Analysis, architecture, and verification before writing code reduces rework and produces measurably better outcomes. Each phase adds a distinct layer of understanding that downstream phases depend on — research informs architecture, architecture decomposes into steps, steps get verification criteria.

## Configuration

### Argument Definitions

| Argument | Format | Default | Description |
|----------|--------|---------|-------------|
| `task-file` | Path | Required | Path to draft task file in `.specs/tasks/draft/` |
| `--continue` | `[stage]` | None | Resume from a specific stage. If stage name omitted, auto-detect from task file completion markers. |
| `--target-quality` | `X.X` | `3.5` | Minimum weighted score (out of 5.0) for judge pass/fail decisions |
| `--max-iterations` | `N` | `3` | Maximum fix-to-verify cycles per phase before proceeding to next stage |
| `--included-stages` | `stage1,...` | All stages | Comma-separated list of stages to include (all others skipped) |
| `--skip` | `stage1,...` | None | Comma-separated list of stages to exclude |
| `--fast` | flag | N/A | Alias for `--target-quality 3.0 --max-iterations 1 --included-stages business analysis,decomposition,verifications` |
| `--one-shot` | flag | N/A | Alias for `--included-stages business analysis,decomposition --skip-judges` |
| `--human-in-the-loop` | `phase,...` | None | Pause for human review after specified phases. Without phase numbers, pauses after every phase. |
| `--skip-judges` | flag | false | Skip all quality evaluations — phases proceed directly without judge validation |
| `--refine` | flag | false | Incremental refinement mode: detect changes against git and re-run only affected stages (top-to-bottom propagation) |

### Stage Names

| Stage | Phase | Purpose |
|-------|-------|---------|
| `research` | 2a | Gather relevant resources, documentation, libraries, prior art |
| `codebase analysis` | 2b | Identify affected files, interfaces, integration points |
| `business analysis` | 2c | Refine description, create acceptance criteria |
| `architecture synthesis` | 3 | Synthesize research and analysis into architectural overview |
| `decomposition` | 4 | Break into implementation steps with success criteria and risks |
| `parallelize` | 5 | Reorganize steps for maximum parallel execution |
| `verifications` | 6 | Add evaluation rubrics for each implementation step |

### Usage Examples

```bash
# Full refinement with all stages
/plan .specs/tasks/draft/add-validation.feature.md

# Fast mode: business analysis, decomposition, verifications only
/plan .specs/tasks/draft/quick-fix.bug.md --fast

# Continue from an interrupted stage
/plan .specs/tasks/draft/complex-api.feature.md --continue architecture synthesis

# High quality with human review after synthesis and decomposition
/plan .specs/tasks/draft/critical-api.feature.md --target-quality 4.5 --human-in-the-loop 3,4

# Incremental refinement after user edits
/plan .specs/tasks/todo/my-task.feature.md --refine

# Minimal refinement, no quality gates
/plan .specs/tasks/draft/simple-change.bug.md --one-shot
```

## Sub-Agent Dispatch

This skill dispatches subagents for each phase. Sub-agents start with fresh context — they have no access to prior conversation history or other subagent outputs.

### Dispatch Requirements

Every phase subagent must receive:
1. **Scope**: the specific phase and task file path
2. **Context**: relevant artifact paths from prior phases (scratchpad files, analysis files)
3. **Artifact directive**: whether to write to scratchpad, update task file, or create a new document
4. **Output format**: what to return (structured report with file paths and findings)
5. **The value of `${CLAUDE_SKILL_DIR}`** if the subagent needs to reference skill-internal paths

### Phase Agent Prompt Structure

```
Phase: [Phase Name]
Task File: <TASK_FILE>
Prior Artifacts: <paths to scratchpad/analysis files from prior phases>

Your task:
<specific actions for this phase>

CRITICAL: Write findings to scratchpad first at .specs/scratchpad/<unique-id>.md.
Only update the task file with validated conclusions.
Do NOT output your analysis inline — write everything to files.

Report: artifact paths created/updated, key findings summary, any issues.
```

**Spawn Footer**
When dispatched as a subagent:
- Your context starts fresh — no access to prior conversation or other subagents' outputs
- Return structured output (file paths, findings, and any artifacts) to the orchestrator
- If you encounter anything unexpected or have any question or doubt, stop and report back
- Do not proceed silently on assumptions.

**Failure Signal**
If unable to complete the task, return: {"status": "failed", "reason": "...", "completed_portion": "...", "retry_possible": true/false}

### Judge Agent Prompt Structure

```
Evaluate artifact at: <artifact_path>

Role: <phase role>
Rubric: <criteria table>

Context: Task File <TASK_FILE>, Phase [Name]

Score each criterion 1-5. Provide chain-of-thought justification BEFORE each score.
Compute weighted overall. Return PASS/FAIL with specific improvements if FAIL.
```

**Spawn Footer**
When dispatched as a subagent:
- Your context starts fresh — no access to prior conversation or other subagents' outputs
- Return structured output (file paths, findings, and any artifacts) to the orchestrator
- If you encounter anything unexpected or have any question or doubt, stop and report back
- Do not proceed silently on assumptions.

**Failure Signal**
If unable to complete the task, return: {"status": "failed", "reason": "...", "completed_portion": "...", "retry_possible": true/false}

### Integrity Rules for Sub-Agents
- If expected files were not created, re-launch the subagent with the same prompt
- If an agent returns a long report instead of writing to files, reject and re-launch
- If a judge returns score 5.0/5.0, treat as hallucination — reject and re-run
- If a judge omits the numerical score, reject and re-run
- Use foreground (synchronous) agents only — background agents introduce timing issues

## Pre-Flight Checks

1. **Validate task file**: Check file exists in `.specs/tasks/draft/` (or `.specs/tasks/todo/` for `--refine` mode). If not found, show error and exit.

2. **Resolve configuration**: Parse flags from arguments. Apply alias shortcuts (`--fast`, `--one-shot`) first, then override with explicit flags. Compute active stages: `INCLUDED_STAGES - SKIP_STAGES`.

3. **Handle `--continue`**: Read the task file for completion markers such as completed phases with content, judge scores, or section headings that indicate work was done. Identify the last completed phase — the most recently filled section with content. Resume from the next incomplete phase. If a stage name was provided, skip directly to that stage. Pre-populate any captured values from existing artifacts so the resumed subagent has context of what was already done.

4. **Handle `--refine`**:
   - Check file status: `git status --porcelain -- <TASK_FILE>`
   - `M` (modified) or `MM` (staged + unstaged) → proceed with diff analysis
   - `??` (untracked) → error: file not tracked by git
   - Empty output → no changes, inform user and exit
   - Run `git diff HEAD -- <TASK_FILE>` to get changes since last commit
   - Parse the diff to identify which sections were modified. Look for `//` comment markers in the diff — these indicate user feedback or corrections.
   - Determine the earliest modified section using the section-to-stage mapping. The earliest section dictates which stages to re-run.
   - Set `ACTIVE_STAGES` to include only stages from the determined starting point onward.
   - Pass detected changes and user comments as additional context to subagents. Sub-agents must preserve unchanged content and incorporate feedback.

   **Section-to-Stage Mapping**:

   | Modified Section | Re-run From Stage | Preserved Stages |
   |------------------|-------------------|-----------------|
   | Description / Acceptance Criteria | business analysis | research, codebase analysis |
   | Architecture Overview | architecture synthesis | research, codebase analysis, business analysis |
   | Implementation Steps | decomposition | all earlier stages |
   | Parallelization / Dependencies | parallelize | all earlier stages |
   | Verification sections | verifications | all earlier stages |

5. **Handle `--one-shot`**: Skip all judge evaluation phases. Run only business analysis and decomposition, then promote task.

6. **Initialize progress tracking**: Create todo list for active stages. Exclude stages not in `ACTIVE_STAGES`. Exclude judge todos if `SKIP_JUDGES` is true. Exclude human checkpoint todos if `HUMAN_IN_THE_LOOP_PHASES` is empty.

7. **Ensure directory structure**: Create `.specs/tasks/{draft,todo,in-progress,done}/`, `.specs/scratchpad/`, `.specs/analysis/` if missing.

## Phase 2: Parallel Analysis

Launch three analysis sub-phases in parallel. Each phase uses a dedicated subagent and produces a scratchpad file plus task artifacts. Each phase has an independent judge evaluation.

**Synchronization Point**: Wait for ALL three phases AND their judges to pass before proceeding to Phase 3. If one phase finishes significantly before others (e.g., research completes while business analysis is still running), spawn its judge immediately rather than waiting — this keeps the overall workflow efficient. Do NOT proceed to Phase 3 until all three phase-judge pairs have completed with PASS or MAX_ITERATIONS reached.

### Phase 2a: Research

Spawn a research subagent. The agent reads the project context and task file, then gathers relevant resources.

**Agent task:**
- Search for documentation, existing patterns, and libraries relevant to the task
- Identify common pitfalls, best practices, and reference implementations
- Create a reusable skill document with findings for use by implementation agents
- Write all research to scratchpad first, then create the skill document
- Do NOT output research results inline — write everything to files

**Artifacts:**
- Scratchpad: `.specs/scratchpad/<hex-id>.md`
- Skill document: `.claude/skills/<topic>/SKILL.md` (reusable across tasks)

**Evaluation dimensions (weight):**
- Resource coverage (0.30): documentation and references gathered
- Pattern relevance (0.25): identified patterns are applicable and actionable
- Issue anticipation (0.20): common pitfalls identified with solutions
- Reusability (0.15): skill is general enough for multiple tasks
- Task integration (0.10): task file updated with skill reference

**Edge case**: If research finds no relevant prior art or documentation, the skill document should document this explicitly as a negative finding so architecture later knows no established patterns exist to follow.

**On judge FAIL**: Re-launch a research subagent with judge feedback incorporated. Do not proceed until judge PASS or MAX_ITERATIONS reached.

---

### Phase 2b: Codebase Impact Analysis

Spawn a codebase exploration subagent. The agent analyzes the project structure to identify affected files and integration points.

**Agent task:**
- Identify all files that will be modified, created, or deleted
- Document key functions, classes, and interfaces affected
- Map integration points and dependencies between components
- Assess risk level for each affected area with mitigations
- Write all analysis to scratchpad first, then create the analysis document
- Do NOT output analysis inline — write everything to files

**Artifacts:**
- Scratchpad: `.specs/scratchpad/<hex-id>.md`
- Analysis file: `.specs/analysis/analysis-<name>.md`

**Evaluation dimensions (weight):**
- File identification accuracy (0.35): all affected files identified with specific paths
- Interface documentation (0.25): key functions and classes documented with signatures
- Integration mapping (0.25): integration points identified with impact assessment
- Risk assessment (0.15): high-risk areas identified with mitigations

**Edge case**: For tasks that span multiple packages or modules, identify cross-boundary impacts explicitly. Integration points at package boundaries carry higher risk.

**Edge case**: If the task involves creating new files that do not yet exist, the analysis should identify where they belong based on project conventions and existing directory structure.

**On judge FAIL**: Re-launch a codebase analysis subagent with judge feedback. Do not proceed until PASS or MAX_ITERATIONS reached.

---

### Phase 2c: Business Analysis

Spawn a business analysis subagent to refine the task description and create comprehensive acceptance criteria. Uses a scratchpad-first methodology: all analysis happens in a scratchpad file, and only verified findings are copied to the task file.

**Agent task — mandatory stages (perform each in order):**

**Stage 1: Setup Scratchpad.** Before any analysis, create a scratchpad file. The scratchpad captures the entire thinking process. Only the final validated output goes into the task file. Structure the scratchpad with sections for each analysis stage below.

**Stage 2: Requirements Discovery.** Work through the problem definition step by step in the scratchpad. Do not accept the surface-level description at face value — probe deeper:

If the task file has an empty Description (placeholders only), then the user prompt is the only source of requirements. Extract as much signal as possible from it. Note any ambiguities explicitly for downstream resolution.

If the user prompt itself is ambiguous (e.g., "make it better"), identify what information is missing and document the assumptions you make rather than blocking on clarification.

```
Step 1: What is the surface-level user request?
Step 2: What is the user actually trying to accomplish?
Step 3: What is the business value or user value?
Step 4: Who benefits from this change and how?
Step 5: What constraints or considerations exist?
Therefore, the root problem is: <synthesis>
```

Define scope boundaries clearly:
- What is included in this task?
- What is explicitly NOT included?
- What are the boundary cases?

**Stage 3: Concept Extraction.** Identify the core elements of the feature or change:

```
Actors: Who interacts with this?
Actions/Behaviors: What does the system do?
Data Entities: What data is involved?
Constraints: What limitations exist?
Implicit Assumptions: What is assumed but not stated?
```

**Stage 4: Requirements Analysis.** Break requirements into functional and non-functional categories. For each functional criterion, verify testability:

- Is this specific enough for a QA engineer to write a test case without asking questions?
- Does it have clear Given/When/Then components?
- Is the outcome measurable and verifiable?

Document primary flow, alternative flows, and error scenarios. Remove criteria that fail testability or merge them into testable ones.

**Stage 5: Synthesis.** Distill findings into a refined description and acceptance criteria. Lead with the problem, then the solution, then boundaries. Write for a developer who needs to understand WHY before WHAT. The refined description should be 2-3 paragraphs covering what is being built, why it is needed, who benefits, and key constraints.

**Stage 6: Update Task File.** Read the current task file, then update it with:
- Refined Description section covering what/why/who/constraints
- Scope section (included, excluded)
- User scenarios (primary flow, alternatives, error handling)
- Acceptance Criteria section with functional and non-functional requirements using testable format
- Preserve frontmatter and original user prompt unchanged

**Stage 7: Self-Critique Loop (mandatory).** In the scratchpad, verify against these questions:

```
| # | Question | Reasoning | Rating |
|---|----------|-----------|--------|
| 1 | Requirements completeness: are all functional requirements captured including edge cases? | | COMPLETE/PARTIAL/MISSING |
| 2 | Scope clarity: explicit boundaries with out-of-scope list? | | COMPLETE/PARTIAL/MISSING |
| 3 | Acceptance criteria testability: can a QA engineer write tests without clarifying questions? | | COMPLETE/PARTIAL/MISSING |
| 4 | Business value traceability: does every requirement trace to a stated goal? | | COMPLETE/PARTIAL/MISSING |
| 5 | No implementation details: is the spec free of tech choices, APIs, code structure? | | COMPLETE/PARTIAL/MISSING |
```

Check for common failure modes:
- Vague terms like "quickly", "properly", "correctly" without metrics
- Happy-path-only scenarios with no error cases
- Implementation details in acceptance criteria instead of WHAT
- Untestable criteria
- Unclear scope boundaries

Fix all critical and high-priority gaps before completing. Document gaps found and revisions made in the scratchpad.

**Artifacts:**
- Scratchpad: `.specs/scratchpad/<hex-id>.md`
- Updated task file with Description, Scope, User Scenarios, and Acceptance Criteria sections

**Evaluation dimensions (weight):**
- Description clarity (0.30): what/why clearly explained, scope boundaries defined
- Acceptance criteria quality (0.35): criteria are specific, testable, use Given/When/Then for complex cases
- Scenario coverage (0.20): primary flow documented, error scenarios considered
- Scope definition (0.15): in-scope/out-of-scope explicit, no implementation details in description

## Phase 3: Architecture Synthesis

Spawn an architecture subagent after all Phase 2 phases and judges pass. Synthesize research, codebase analysis, and business requirements into an architectural overview.

**Agent task:**
- Read scratchpad and analysis files from Phase 2a, 2b, 2c
- Define the solution strategy and approach with reasoning
- Document key architectural decisions and trade-offs
- Specify components, responsibilities, and interfaces
- List expected file changes (create/modify/delete) consistent with codebase analysis
- Reference research findings and analysis artifacts
- Update task file with Architecture Overview section
- Only include sections relevant to task complexity — do not add boilerplate sections

**Artifacts:**
- Scratchpad: `.specs/scratchpad/<hex-id>.md`
- Updated task file with Architecture Overview section

**Evaluation dimensions (weight):**
- Solution strategy clarity (0.30): approach clearly explained, decisions documented with reasoning, trade-offs stated
- Reference integration (0.20): links to research and analysis files, insights from both integrated
- Section relevance (0.25): only relevant sections included (not all), appropriate for task complexity
- Expected changes accuracy (0.25): files to create/modify listed, consistent with codebase analysis

## Phase 4: Decomposition

Spawn a decomposition subagent after Phase 3 passes. Break the architecture into ordered implementation steps.

**Agent task:**
- Define ordered implementation steps with clear dependencies
- Each step must have: clear goal, expected output files, success criteria, subtasks
- No step larger than the large estimate threshold — split oversized steps
- Identify blockers, risks, and mitigations for each step
- Organize in phases: Setup, Foundational, User Stories, Polish
- Include Definition of Done section at task level listing completion criteria
- Include implementation summary table
- Write to scratchpad first, then update the task file

**Artifacts:**
- Scratchpad: `.specs/scratchpad/<hex-id>.md`
- Updated task file with Implementation Process section

**Evaluation dimensions (weight):**
- Step quality (0.30): each step has clear goal, output, success criteria; ordered by dependency; no step too large
- Success criteria testability (0.25): criteria specific and verifiable, use actual file paths, subtasks actionable
- Risk coverage (0.25): blockers identified with resolutions, risks with mitigations
- Completeness (0.20): all architecture components have corresponding steps, Definition of Done included

## Phase 5: Parallelize

Spawn a parallelization subagent after Phase 4 passes. Reorganize implementation steps for maximum parallel execution.

**Agent task:**
- Reorganize steps with explicit dependency chains
- Identify steps that can run in parallel (no transitive dependencies between them)
- Assign appropriate agent difficulty levels to each step (more complex work gets more capable agents, simpler work uses lighter agents)
- Generate a parallelization diagram showing execution order and parallel tracks
- Add parallel execution directive with MUST requirements for each parallel group
- Only parallelize within the current task scope — do not plan or create tasks for future work
- Write to scratchpad first, then update the task file

**Artifacts:**
- Scratchpad: `.specs/scratchpad/<hex-id>.md`
- Updated task file with parallelization annotations and agent assignments

**Evaluation dimensions (weight):**
- Dependency accuracy (0.35): step dependencies correctly identified, no false or missing dependencies
- Parallelization maximization (0.30): parallelizable steps correctly identified, diagram is logical
- Agent selection correctness (0.20): agent levels appropriate for output complexity
- Execution directive present (0.15): subagent execution directive with MUST requirements clear

## Phase 6: Verifications

Spawn a verification subagent after Phase 5 passes. Add evaluation rubrics for each implementation step.

**Agent task:**
- For each implementation step, determine verification level:

| Level | When to Use | Configuration |
|-------|-------------|---------------|
| None | Simple operations (mkdir, delete, config changes) | Skip verification entirely |
| Single Judge | Non-critical artifacts | 1 judge, threshold from task context |
| Panel of 2 Judges | Critical artifacts (business logic, security, data) | 2 judges, median voting, higher threshold |
| Per-Item Judges | Multiple similar items (validators, handlers, endpoints) | 1 judge per item, parallel execution |

- Create role-specific weighted rubrics for each step with measurable criteria
- Weights must sum to 1.0 for each rubric
- Set context-appropriate thresholds (higher for critical paths, lower for experimental work)
- Include a verification summary table at the end of the task file
- Write to scratchpad first, then update the task file

**Artifacts:**
- Scratchpad: `.specs/scratchpad/<hex-id>.md`
- Updated task file with `#### Verification` sections for each step

**Evaluation dimensions (weight):**
- Level appropriateness (0.30): verification levels match artifact criticality
- Rubric quality (0.30): criteria specific to artifact type, weights sum to 1.0, descriptions clear and measurable
- Threshold appropriateness (0.20): thresholds reasonable for context (higher for critical, lower for experimental)
- Coverage completeness (0.20): every step has a verification section, summary table present

## Phase 7: Promote

After all phases complete, move the refined task from draft to todo:

```bash
git mv <TASK_FILE> .specs/tasks/todo/
# Fallback: mv <TASK_FILE> .specs/tasks/todo/
```

Update any references in research and analysis files if paths changed.

---

## Evaluation Pattern

Every phase follows the same evaluation structure. The judge is an independent subagent with no connection to the phase implementation agent.

### Judge Prompt Structure

Each judge receives:
1. The phase artifact path (skill document, analysis file, or updated task file)
2. A role-specific rubric with weighted criteria
3. The configured quality threshold

The judge must:
1. Read the artifact at the specified path
2. Evaluate each rubric criterion, providing chain-of-thought justification BEFORE the numerical score
3. Compute the weighted average across all criteria
4. Return: criterion scores with evidence, overall weighted score, PASS/FAIL verdict, specific improvements on FAIL

### Scoring Scale (per criterion)

| Score | Label | Meaning |
|-------|-------|---------|
| 1 | Poor | Missing essential elements, fundamental misunderstanding |
| 2 | Below Average | Some correct elements, significant gaps |
| 3 | Adequate | Meets basic requirements, functional but minimal |
| 4 | Good | Meets all requirements, few minor issues |
| 5 | Excellent | Exceptional quality, exceeds expectations |

### Decision Logic

- **PASS** (score >= THRESHOLD): Phase complete, proceed to next phase
- **FAIL** (score < THRESHOLD): Re-launch phase with judge feedback incorporated into the subagent prompt
- **MAX_ITERATIONS reached**: Proceed to next phase regardless of score, log warning

### Retry Flow

```
Phase Implementation Agent
  → Judge Evaluation
    → PASS (score >= THRESHOLD) → Next Phase
    → FAIL (score < THRESHOLD)
      → Re-implement with judge feedback
        → Judge Evaluation
          → PASS → Next Phase
          → FAIL → Re-implement (up to MAX_ITERATIONS)
            → MAX_ITERATIONS reached → Next Phase (with warning)
```

If phase is in HUMAN_IN_THE_LOOP_PHASES: trigger human checkpoint after re-implementation but before the next judge retry.

### Evaluation Integrity Rules

- Score 5.0/5.0 is a hallucination — reject and re-run the judge. Perfect scores are practically impossible in rigorous evaluation.
- Missing numerical score — reject and re-run the judge.
- Excessively long reports that do not follow the structured evaluation format — reject and re-run.
- Do not proceed to next phase until judge passes, unless MAX_ITERATIONS reached or SKIP_JUDGES is true.
- Use the configured THRESHOLD value (default 3.5) — never hardcode a threshold value.

## Human-in-the-Loop Checkpoints

When a phase number is in `HUMAN_IN_THE_LOOP_PHASES`, pause after the judge passes (or after MAX_ITERATIONS is reached) to get human review:

```markdown
---
## Human Review Checkpoint - Phase [N]

**Phase:** <phase name>
**Judge Score:** X.X/THRESHOLD
**Status:** PASS / PROCEEDED (max iter)

**Artifacts:**
- <artifact_path_1>
- <artifact_path_2>

**Judge Feedback:**
<summary of key findings>

**Action Required:** Review the above artifacts and provide feedback or continue.

> Continue? [Y/n/feedback]:
---
```

If user provides feedback, incorporate into the next phase or iterate on the current one. If user says no, pause the workflow.

## Error Handling

### Phase Sub-Agent Failure
If a phase agent fails unexpectedly (exception, crash, permission error): report the failure with the agent output, ask clarifying questions from the user that could help resolve the issue, then re-launch the phase subagent with the questions and answers incorporated.

### Judge Returns FAIL
Automatic retry: re-launch the phase implementation subagent with the judge feedback included in the prompt. The implementation subagent must address each failing criterion specifically.

If the phase is in HUMAN_IN_THE_LOOP_PHASES: trigger the human checkpoint after the re-implementation but before the next judge retry — the user may have context that clarifies what feedback to prioritize.

After MAX_ITERATIONS (default 3) reached: proceed to the next phase automatically. Log a warning in the completion summary. Do not ask the user for permission unless the phase is in HUMAN_IN_THE_LOOP_PHASES.

### Refine Mode Edge Cases
- **No changes detected**: Inform user: "No changes detected in task file. Edit the file first, then run --refine."
- **Untracked file**: Inform user: "File not tracked by git, cannot detect changes. Commit the file first, then run --refine."

## Completion

After all executed phases, judges, and the promotion step are complete:

1. Stage the task file, skill document, analysis file, and scratchpad files via git
2. Display the completion summary:

```markdown
### Task Refined

| Property | Value |
|----------|-------|
| **Original File** | `.specs/tasks/draft/<filename>` |
| **Final Location** | `.specs/tasks/todo/<filename>` |
| **Title** | `<task title>` |
| **Type** | `<feature/bug/refactor/test/docs/chore/ci>` |
| **Implementation Steps** | `<count>` |
| **Parallelization Depth** | `<max parallel agents>` |
| **Total Verifications** | `<count>` |

### Quality Gates Summary

| Phase | Judge Score | Verdict |
|-------|-------------|---------|
| Phase 2a: Research | X.X/5.0 | PASS / PROCEEDED (max iter) / SKIPPED |
| Phase 2b: Codebase Analysis | X.X/5.0 | PASS / PROCEEDED (max iter) / SKIPPED |
| Phase 2c: Business Analysis | X.X/5.0 | PASS / PROCEEDED (max iter) / SKIPPED |
| Phase 3: Architecture Synthesis | X.X/5.0 | PASS / PROCEEDED (max iter) / SKIPPED |
| Phase 4: Decomposition | X.X/5.0 | PASS / PROCEEDED (max iter) / SKIPPED |
| Phase 5: Parallelize | X.X/5.0 | PASS / PROCEEDED (max iter) / SKIPPED |
| Phase 6: Verifications | X.X/5.0 | PASS / PROCEEDED (max iter) / SKIPPED |

**Threshold used:** X.X/5.0

### Artifacts Generated

```
.specs/
├── tasks/
│   ├── draft/        <-- (source, now empty for this task)
│   └── todo/
│       └── <name>.<type>.md   <-- Complete task specification (ready for impl)
├── analysis/
│   └── analysis-<name>.md     <-- (if codebase analysis ran)
└── scratchpad/
    └── <hex-id>.md            <-- Thinking scratchpad

.claude/
└── skills/
    └── <topic>/
        └── SKILL.md           <-- Reusable skill doc (if research ran)
```

### Next Steps

1. Review the refined task at `.specs/tasks/todo/<filename>`
2. Edit directly for corrections — add `//` comments for clarification, then run `--refine` to propagate changes
3. Begin implementation when ready
```

## Design Decisions

**Stage-specific guidance is documented in the stages.md file in this skill's references.**

### Parallel analysis before synthesis
Running research, codebase analysis, and business analysis in parallel is faster than sequential. This prevents the common failure mode of designing architecture without understanding business requirements or codebase constraints.

### Independent judges per phase
Separate judge subagents prevent confirmation bias. Independent judges provide objective quality signals and catch blind spots.

### Threshold defaults
3.5/5.0 balances quality and speed. The configurable threshold allows trade-offs depending on task criticality.

### Scratchpad-first methodology
All analysis goes to a scratchpad before the task file. This prevents premature commitment to unverified findings.
