---
name: execute-plans
description: "Executes PLAN.md files using intelligent strategies based on checkpoint types. Use when user says 'execute', 'run plan', or 'build it'."
when_to_use: |
  Use when the user says "execute", "run plan", "do it", or "build it".
  IMMEDIATELY when ready to progress from PLAN to SUMMARY.
  Do NOT use for creating plans — use the planning skill instead.
  Do NOT use for planning without execution intent.
  Do NOT use for executing prompt files — use execute-prompts instead.
argument-hint: [path to plan] [--phase N]
---

## Decision Router

IF plan has zero checkpoints or only checkpoint:human-verify → Strategy A: Fully Autonomous
IF plan has checkpoint:human-verify markers → Strategy B: Segmented Execution
IF plan has checkpoint:decision or checkpoint:human-action → Strategy C: Sequential Execution
IF spawning parallel workers → FIRST consult the orchestration patterns for parallel subagent work

For detailed strategy mechanics → read the execution-strategies reference file AFTER selecting strategy

---

## Numeric Thresholds

| Metric | Limit |
|--------|-------|
| Parallel workers | 3-5 |
| Milestone review frequency | Every 2-3 tasks |
| Context overhead target | <30% |
| Spawn prompt tokens | 1500 max |

---

## Token Cost and Scale Limits

**Coordination overhead principle:** If the coordination graph is denser than the work graph, execute sequentially. Multi-agent only when parallelization saves more time than coordination costs.

**Warning signs:** See Numeric Thresholds for worker/context limits.

---

# Execute Plans Skill

Execute PLAN.md files as prompts. Transform planned work into shipped artifacts.

## Core Principle

**Plans are prompts. Execute them exactly.** The PLAN.md is not documentation that gets transformed — it is the instruction Claude follows directly.

---

### Policy vs. Mechanism

**Policy** = when to use which execution strategy (the judgment call)
**Mechanism** = how to structure the execution, deviation handling, and checkpoint protocols (the method)

A skill conflating policy and mechanism produces execution that either skips critical gates or asks for input on every minor decision. Separate policy into the strategy selection; put mechanism into the execution handlers.

---

## Intake

This skill can be invoked directly or after create-plans. If context was already captured (plan exists, execution preference set), skip intake and proceed to strategy selection.

For direct invocation, ensure you have sufficient context to execute:

1. **Understand the goal** — what needs to be achieved
2. **Clarify scope** — what's in and out of bounds
3. **Set execution mode** — fully autonomous or human-in-the-loop at milestones

Use your tool to ask users your questions and prefill answers to gather what you need. Keep it focused — you don't need everything upfront, just enough to proceed confidently.

If execution was interrupted and a handoff file exists, skip the intake and auto-resume from the checkpoint.

---

## Strategy Selection

Before executing, analyze the plan's checkpoint structure:

```bash
grep -E 'checkpoint:|type="checkpoint:' {plan_path}
```

### Strategy A: Fully Autonomous

**Use when:** Plan has zero checkpoints or only `checkpoint:human-verify` markers between autonomous segments.

**Policy:** Executor is an intelligent orchestrator that decomposes the plan, executes independent tasks in parallel, and self-reviews at milestones. No user interaction.

**Core Concept:** The executor reads the plan, analyzes task dependencies and resource conflicts, decomposes into parallelizable vs sequential groups, spawns multiple worker subagents in parallel for independent tasks, spawns single workers for sequential dependency chains, self-criticizes at milestones, aggregates results, and commits.

**How it differs from old implementation:**
- **Before:** Single subagent does everything sequentially
- **After:** Executor analyzes plan, spawns PARALLEL workers for independent tasks, spawns REVIEWER at milestones

**Note:** All agent templates (implementer, critic, researcher, verifier) are in the `agents/` folder — read the relevant template before spawning.

**Executor (main orchestrator) responsibilities:**
```
1. Analyze plan structure and task relationships
2. Build dependency graph (task → files touched, prerequisites)
3. Pre-execution: spawn critic to challenge the plan (devil's advocate)
4. If critic finds critical issues: fix plan before proceeding
5. Identify conflict-free groups (tasks touching different files)
6. Spawn parallel workers for independent task groups (max 3-5 workers)
   - **Context rule:** Subagents start with FRESH context — no inheritance from orchestrator.
     Every piece of context needed must be in the spawn prompt: file paths, prior findings, constraints, success criteria.
     A subagent cannot reference "as we discussed" or "from earlier" — it has no idea what that means.
     **URL:** https://code.claude.com/docs/en/sub-agents#what-loads-at-startup
7. Spawn sequential workers for dependent chains (ordered execution)
8. At milestone (every 2-3 tasks or phase boundary): spawn CRITIC subagent to review intermediate output
9. If critic finds issues: executor fixes before continuing
10. Aggregate all results
11. Create SUMMARY.md
12. Commit
```

**Parallel execution rules:**
- Two tasks are parallelizable if: they touch different files AND neither depends on output of the other
- Max parallel workers: 3-5 (prevents resource contention, maintains quality)
- Sequential chains execute in order (A → B → C where B needs A output)
- File conflict detection: if two tasks touch the same file, they cannot run in parallel

**Milestone self-review:**
- Trigger: every 2-3 tasks completed, or at phase boundary
- Spawn a CRITIC subagent (haiku, with Write) to review what was done
- Critic checks: correctness, edge cases, regressions, deviation handling
- If critic finds issues: executor fixes before continuing to next milestone
- This is internal review, not user interaction

**Task tracking:**
- Track each parallel worker group as a unit of work — status updates as workers complete
- At milestones, the critic review itself becomes a tracked checkpoint in the execution flow
- Result aggregation updates the parent task status, not the individual workers
- Delegate simple tasks without tracking overhead; only track when multiple workers coordinate or depend on intermediate outputs

**Why:** No user interaction needed. Executor operates as intelligent orchestrator with parallel execution for speed and self-review for quality. Overhead: ~10-15% main context (higher than old single-subagent approach due to coordination, but better quality through parallelism and review).

### Explorer Subagent Protocol

When spawning subagents for investigation (exploring project structure, finding relevant files, understanding codebase organization), follow this protocol:

**Before spawning:**
1. Check centralized scratchpad at `.principled/scratch/{plan-id}.md`
2. Write current execution context to scratchpad (what task, why spawning, expected output)
3. Verify subagent has **Write tool access** — explorer needs to update scratchpad
4. **NEVER** use "native" Explore subagents (Haiku, read-only) for investigation

**Subagent tool requirements for investigation:**
- REQUIRED minimum: read source files, write findings to disk, search project structure, and run shell commands
- Write access is NON-OPTIONAL — findings must be persisted

**After spawning:**
5. Subagent reads scratchpad for any prior findings (avoid duplicate work)
6. Subagent writes findings to scratchpad before returning
7. Orchestrator reads scratchpad after subagents return
8. Consolidate findings before proceeding

**Why:** Prevents telephone-game information degradation. Explorer findings are shared via scratchpad, not passed through summarization rounds.

---

**Pre-execution self-critique (devil's advocate):**

Before spawning workers, spawn a critic subagent to challenge the plan ITSELF — not the workers' output, but the plan's assumptions and structure. Read the critic agent template from the agents folder and spawn the critic with the plan as context.

If critic finds critical issues: fix the plan before spawning workers.
If critic finds minor concerns: note them for milestone review.

**Why:** Milestone self-review catches bad execution. Pre-execution critique catches bad plans. Catching a flawed plan before wasting parallel workers is cheaper than fixing after they complete.

---

## Implementer Scratchpad Protocol

When spawning implementer subagents (Strategy A parallel workers, Strategy B segment workers), use a shared scratchpad for all execution output:

**Location:** `.principled/scratch/{plan-id}-execution.md`

**Before spawning each worker:**
1. Read existing scratchpad for prior implementation context (similar task patterns, resolved blockers)
2. Write the task scope and expected output to scratchpad
3. Include the task's file paths so workers don't collide on same files

**Worker requirements:**
- General-purpose subagent with read, write, search, and shell command access
- Worker writes implementation results to scratchpad before returning
- Worker includes: files modified, verification results, any deviations detected

**Orchestrator after workers return:**
1. Read scratchpad — do NOT rely on subagent output text alone
2. Verify no file conflicts between parallel workers (did two workers touch the same file?)
3. If file conflict detected: spawn critic to resolve merge, fix conflicts, test
4. Aggregate results from scratchpad into milestone review

**Why:** Same telephone-game prevention as the explorer protocol. Implementation details are too easy to paraphrase incorrectly. Reading the scratchpad directly gives the orchestrator ground truth.

---

## Critic-Revise Execution Loop

The executor-critic relationship is a structured loop, not a one-shot check:

### Per-Milestone Loop

```
1. N tasks complete → milestone threshold reached
2. Spawn critic subagent:
   - Reads scratchpad for all worker output
   - Reads PLAN.md for expected outcomes
   - Evaluates: correctness, edge cases, regressions, deviation handling
   - Writes findings to scratchpad (not verbal summary)
3. Orchestrator reads critic findings from scratchpad
4. IF findings have issues:
   - Create fix tasks (1-2 small, targeted)
   - Spawn implementer subagent for each fix
   - Re-verify
   - Re-spawn critic if fix was non-trivial
   - Repeat until critic passes or 2 fix cycles exhausted
5. IF 2 fix cycles exhausted AND still failing:
   - Document remaining issues in SUMMARY.md
   - Log as known limitations
   - Proceed to next milestone (blocking on edge cases wastes throughput)
6. IF critic passes: proceed to next milestone
```

### Per-Task Micro-Loop (for complex tasks)

For tasks that are architecturally significant or touch 5+ files, integrate critic per-task:

```
1. Worker completes task
2. Orchestrator self-review: does output match task spec?
3. If non-trivial deviation: spawn critic for this task only
4. Fix issues → re-verify → continue
```

**Why a loop, not a gate:** A single critic review creates false confidence — the critic might miss issues in the first pass, or the fix might introduce new problems. The loop structure issues diminishing returns naturally: most issues are caught in round 1, edge cases in round 2, and round 3+ catches are noise. Cap at 2 fix cycles for throughput.

---

### Strategy B: Autonomous Segmented Execution

**Use when:** Plan has `checkpoint:human-verify` markers. Each checkpoint separates a coherent autonomous block.

**Policy:** Subagents execute segments between checkpoints. The orchestrator self-verifies checkpoint conditions using CLI commands and automated checks. No user interaction.

**Mechanism:**
```
1. Parse plan into segments (blocks between checkpoints)
2. For each segment:
   - Spawn worker subagent to execute block
   - Worker writes output to scratchpad
   - Orchestrator self-verifies checkpoint conditions:
     * Run verify commands from plan
     * Check file state, test output, build status
     * PASS → log verification, proceed to next segment
     * FAIL → spawn critic subagent, diagnose, fix, re-verify
   - Status update: "Segment [N] complete — [verification result]"
3. Aggregate all segment results
4. Create SUMMARY.md with full audit trail
5. Update ROADMAP.md
6. Commit
```

**Self-verification rules:**
- Run all verify commands from the plan's task definitions
- If verify commands don't exist, use automated checks: file existence, test pass rate, lint status, build success
- If self-verification fails, spawn a critic subagent to diagnose, then fix and re-verify
- If self-verification fails after 2 fix attempts: log remaining issues in SUMMARY.md, proceed to next segment or milestone. Status update: "Segment [N]: 2/2 fix cycles exhausted — [issue] logged in SUMMARY.md"

**Why:** Every verification check that can be automated should be. "Human verify" in practice means "someone should glance at it" — but for CI-able checks, the orchestrator does the glancing. Overhead: ~15-20% main context.

---

### Strategy C: Autonomous Sequential Execution

**Use when:** Plan has `checkpoint:decision` or `checkpoint:human-action` markers. These are the most constrained paths — outcomes affect subsequent task sequencing.

**Policy:** All execution in main context. Each checkpoint type has a self-resolution protocol:

| Checkpoint Type | Autonomy Protocol |
|----------------|------------------|
| `checkpoint:decision` | Use heuristics + plan context to choose. Log the decision and rationale. If genuinely ambiguous (equal trade-offs, no clear signal), choose the simplest path and log. |
| `checkpoint:human-action` | Check for a CLI/API alternative first. If none exists, note the manual step in SUMMARY.md as an "unavoidable manual gate" and continue with a simulated/placeholder value that the user can correct. |

**Heuristic decision rules:**
- **Default to simplest path** — if options are A (complex, flexible) and B (simple, sufficient), choose B
- **Follow plan's recommended option** — if the plan tips its hand ("recommended", "preferred"), follow it
- **Break ties with reversibility** — if two options are equally valid, choose the one that is easier to undo
- **Log every decision** — write to scratchpad with format: `Decision: chose X over Y because [reason]`
- **If genuinely uncertain** — make the best call based on available evidence, document the uncertainty in SUMMARY.md

**Mechanism:**
```
1. Load execution_context and context from plan
2. For each task:
   IF type="auto":
     - Execute in main context or spawn parallel worker
     - Track deviations
   IF checkpoint:decision:
     - Evaluate heuristic rules, choose path
     - Log decision with rationale
     - Status update: "Decision: [choice]"
   IF checkpoint:human-action:
     - Check for CLI alternative
     - If CLI exists: execute via automation
     - If no CLI: placehold, log in SUMMARY.md as unavoidable manual gate
3. Create SUMMARY.md with all decisions documented
4. Update ROADMAP.md
5. Commit
```

**Why:** The overwhelming majority of "decisions" in plans are false dilemmas — either one option is clearly better, or both are equally valid and the choice doesn't matter. Plans are written by the same skill that produced the plan — the context contains enough signal to decide. Overhead: ~25-30% main context.

---

### Strategy Selection

| Checkpoint Types | Strategy | Main Context Usage |
|-----------------|----------|---------------------|
| None | A: Fully Autonomous | ~10-15% |
| human-verify | B: Segmented | ~15-20% |
| decision, human-action | C: Sequential | ~25-30% |

**Decision tree:** See the execution-strategies reference file for full strategy selection flow.

**Target:** Reserve 70%+ context for workspace and implementation.

---

## Deviation Handling

**Deviations are normal, not failures.** Plans are guides, not straitjackets. Apply these rules automatically:

### Deviation Rule 1: Auto-fix bugs

**Trigger:** Code doesn't work as intended (errors, broken behavior, incorrect output)

**Action:** Fix immediately. Document in Summary.

**Examples:**
- Wrong SQL query returning incorrect data
- Logic errors (inverted condition, off-by-one, infinite loop)
- Type errors, null pointer exceptions, undefined references
- Broken validation (accepts invalid input, rejects valid input)
- Security vulnerabilities (SQL injection, XSS, insecure auth)

**Process:** Fix inline → add/update tests → verify → track → continue

---

### Deviation Rule 2: Auto-add missing critical functionality

**Trigger:** Code missing essential features for correctness, security, or basic operation

**Action:** Add immediately. Document in Summary.

**Examples:**
- Missing error handling (no try/catch, unhandled promise rejections)
- No input validation (accepts malicious data)
- Missing null/undefined checks (crashes on edge cases)
- No authentication on protected routes
- Missing authorization checks (users can access others' data)

**Process:** Add inline → add tests → verify → track → continue

---

### Deviation Rule 3: Auto-fix blocking issues

**Trigger:** Something prevents completing current task

**Action:** Fix immediately to unblock. Document in Summary.

**Examples:**
- Missing dependency (package not installed, import fails)
- Wrong types blocking compilation
- Broken import paths (file moved, wrong relative path)
- Missing environment variable (app won't start)

**Process:** Fix blocker → verify task proceeds → continue → track

---

### Deviation Rule 4: Heuristic architectural decisions

**Trigger:** Fix/addition requires significant structural modification

**Action:** Evaluate using heuristic rules, choose the path with best signal. Log decision with rationale. Do NOT ask the user.

**Numeric thresholds for "significant":**
- Schema migration affecting 3+ tables or entities
- API surface change affecting 5+ endpoints
- New file requiring architectural pattern integration
- Dependency addition that changes execution model
- Authentication/authorization model change

**Heuristic decision rules (same as Strategy C):**
- Default to simplest path: minimal surface area change
- Prefer reversible choices: if two options are equally valid, choose the one easier to undo
- Follow the plan's implicit direction: if the plan recommends a library or pattern, follow it
- Log every decision with format: `Deviation R4: chose X over Y because [reason]`

**Examples — IS architectural (still decide heuristically, don't ask):**
- Adding new database table: check if the plan implied it, if yes proceed, if no log as enhancement and defer
- Major schema changes: default to additive changes (add columns, don't restructure existing)
- Dependency addition: check if the dependency provides capabilities already in the stack, if so use existing, if not add
- Breaking API change: default to deprecation+new-approach over breaking changes

**Examples — IS NOT architectural (decide yourself):**
- Which naming to use for a variable
- Where to put a file within an existing structure
- Which color scheme to use
- Minor formatting or style choices

**Process:**
1. Evaluate: is the change genuinely necessary, or is it an enhancement?
2. If necessary (bug fix, blocker removal): proceed with simplest correct approach
3. If enhancement: log as enhancement, continue current task
4. Log decision: `Deviation R4: [choice] because [reason]`
5. Continue execution

**Example log entries:**
- `Deviation R4: added users table because plan implied user data storage`
- `Deviation R4: deferred Supabase edge functions migration because authentication path uses Next.js API routes — simpler to keep unified`
- `Deviation R4: chose deprecation over breaking change for /api/v1/users -> /api/v2/users`

---

### Deviation Rule 5: Log non-critical enhancements

**Trigger:** Improvement that would enhance code but isn't essential now

**Action:** Log to `.principled/plans/ISSUES.md`. Continue task.

**Examples:**
- Performance optimization (works correctly, just slower than ideal)
- Code refactoring (works, but could be cleaner)
- Better naming (works, but variables could be clearer)

**Process:** Create ISSUES.md if missing → add entry with ISS-XXX → notify → continue

---

### Rule Priority

| Priority | Rule | Action |
|----------|------|--------|
| 1 | Architectural changes | Evaluate heuristically, choose simplest correct path, log |
| 2 | Bugs, missing criticals, blockers | Fix automatically, track |
| 3 | Non-critical enhancements | Log to ISSUES.md, continue |

---

## Checkpoint Protocols

These are self-service protocols — the executor resolves checkpoints autonomously using the strategy rules above.

### Verify-Only Checkpoint Resolution

When a plan says "User confirms" or "Verify manually":

1. Check for CLI-based verification first (curl, test command, file check)
2. If CLI check exists: run it, log result, continue
3. If no CLI check exists: verify via automated means (file content check, state inspection, process health)
4. Document verification result in SUMMARY.md
5. Status update: "Verified [check]: PASS/FAIL"

**No user interaction.** Every verification check either has a CLI equivalent or can be verified by inspecting file/system state. The "user confirms" pattern in plans is a legacy convention from when plans were written for humans.

### Decision Checkpoint Resolution

When a plan says "Decision needed" or "Choose:":

1. Read the options from the plan context
2. Apply heuristic rules (Strategy C section above)
3. Choose the path with best signal-to-noise ratio
4. Log decision with rationale
5. Status update: "Decision: chose X over Y — [one-line reason]"

### Human-Action Checkpoint Resolution

When a plan says "You need to" or "Manual step":

1. Check for CLI/API alternative first
2. If CLI exists: execute and proceed
3. If no CLI: generate a placeholder (file, config, or note), log in SUMMARY.md as an unavoidable manual gate with exact instructions

**The gate is documented, not blocked on.** The user can apply the manual step later. The build should not depend on it.

### Auth Gate Protocol (Exception)

Authentication gates are the ONE exception where execution depends on user credentials:

1. Recognize: auth error, not a bug
2. Status: "Waiting for [service] authentication — steps at [URL/doc]"
3. User completes auth flow (out of band)
4. Retry the command that failed
5. If retry succeeds: resume, document in SUMMARY.md as normal flow
6. If retry fails: status update "Still waiting on [service] auth"

**Auth gates are status updates, not questions.** Do not ask "please authenticate" — just state the status. The user sees a waiting state and acts on it.

---

## File Operations

### Creating SUMMARY.md

**Location:** Same directory as PLAN.md, named `{phase}-{plan}-SUMMARY.md`

**Format:**
```markdown
# Phase [X] Plan [Y]: [Name] Summary

## Outcome
[One-liner: what was built, how, key decisions]

## Tasks Completed
1. [Task 1]: [what happened]
2. [Task 2]: [what happened]

## Deviations
- [Rule 1/2/3: what was auto-fixed]
- [Rule 4: architectural decision + heuristic choice]
- [Rule 5: logged to ISSUES.md]

## Authentication Gates
- [Gate 1]: paused for X auth, resumed after Y

## Files Modified
- `src/file1.ts`: [change]
- `src/file2.ts`: [change]

## Verification
- [ ] [check 1]
- [ ] [check 2]

## Next
[Ready for next plan / Phase complete]
```

**One-liner standard:**
- ✅ "JWT auth with refresh rotation using jose library"
- ❌ "Authentication implemented"

---

### Updating ROADMAP.md

**If more plans in phase:**
- Update plan count: "2/3 plans complete"
- Keep phase status as "In progress"

**If last plan in phase:**
- Mark phase complete: status → "Complete"
- Add completion date

---

### Git Commit

```bash
git add .principled/plans/phases/XX-name/{phase}-{plan}-PLAN.md
git add .principled/plans/phases/XX-name/{phase}-{plan}-SUMMARY.md
git add .principled/plans/ROADMAP.md
git add src/  # or relevant code directories
git commit -m "feat({phase}-{plan}): [one-liner from SUMMARY.md]"
```

**Scope pattern:**
- `feat(01-01):` for phase 1 plan 1
- `feat(02-03):` for phase 2 plan 3

---

## Context Efficiency

| Strategy | Execution Context | Domain Context | Overhead |
|----------|-------------------|----------------|----------|
| A: Autonomous | ~500-1k tokens | ~10-15k | 10-15% |
| B: Segmented | ~1-2k tokens | ~10-15k | 15-20% |
| C: Sequential | ~2-3k tokens | ~10-15k | 25-30% |

**Target:** <30% overhead, 70%+ workspace for implementation.

**Optimization:** Load only files explicitly referenced in plan's `<execution_context>` and `<context>` sections. Do not pre-load "might be useful" files.

---

## Execution Gotchas

### Thought/Action/Observation Anti-Pattern

**The Problem:**
When Claude sees code blocks with `Thought:`, `Action:`, `Observation:` patterns, it interprets them as output templates to mimic, not as instructions to execute. Instead of calling Write() tool, it generates text that says "Thought: Let me analyze... Action: Write(...)".

**Why This Happens:**
1. Code blocks look like output format — Claude thinks "this is what my response should look like"
2. Pattern mimicking — The agent copies the structure as text instead of executing
3. Pseudo-code confusion — `Action: Write(...)` looks like code to output, not a command to run

**The Fix:**
Replace all Thought/Action/Observation examples with imperative natural language:
- Instead of: "Thought: I need to read the task file..."
- Write: "First, use the Read tool to load the task file."

**This affects ANY skill that shows tool calls in a demonstrated output format.**

---

## Anti-Patterns

**Full anti-pattern catalog is in the anti-patterns.md file in this skill's references.**

### Skipping verification
Marking a task complete without running the verify command.

### Treating auth gates as errors
Retrying authentication failures instead of pausing for user auth steps.

### Making uninformed architectural choices
Making structural changes without evaluating trade-offs. Always apply heuristic rules: prefer simplest path, reversible choices, and documented rationale.

### Creating vague summaries
"Task completed" vs "JWT refresh rotation implemented using jose library".

### Ignoring context limits
Loading all project files instead of only those referenced in the plan.

---

## Reference Index

IF selecting execution strategy → BEFORE choosing read the execution-strategies reference file
IF checkpoint type is human-verify → BEFORE segment read the checkpoint-protocols reference file
IF checkpoint type is decision → BEFORE presenting read the checkpoint-protocols reference file
IF handling deviations → read the deviation-rules reference file
IF spawning autonomous worker → read the autonomous-execution template from the templates folder
IF spawning segment worker → read the segment-execution template from the templates folder
IF spawning milestone critic → read the critic agent template from the agents folder (name: critic)
IF spawning parallel worker → read the implementer agent template from the agents folder
IF spawning researcher → read the researcher agent template from the agents folder
IF spawning verifier → read the verifier agent template from the agents folder
**Orchestration:** Five parallel patterns for subagent work

---

## Success Criteria

- Correct strategy selected based on checkpoint types
- All tasks executed with deviations tracked
- All verifications passed (or user informed of failures)
- SUMMARY.md created with substantive one-liner
- ROADMAP.md updated with plan count
- Git commit created with proper scope format
- Context usage under 30% overhead