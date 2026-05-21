---
name: execute-plans
description: "Execute PLAN.md files using intelligent strategies based on checkpoint types. Use when user says 'execute', 'run plan', 'build it', or wants to progress from PLAN to SUMMARY."
when_to_use: |
  Do NOT use for creating plans — use the planning skill instead.
  Do NOT use for planning without execution intent.
---

## Decision Router

IF plan has zero checkpoints or only checkpoint:human-verify → Strategy A: Fully Autonomous
IF plan has checkpoint:human-verify markers → Strategy B: Segmented Execution
IF plan has checkpoint:decision or checkpoint:human-action → Strategy C: Sequential Execution

For detailed strategy mechanics → read `references/execution-strategies.md` AFTER selecting strategy

---

## Numeric Thresholds

| Metric | Limit |
|--------|-------|
| Parallel workers | 3-5 |
| Milestone review frequency | Every 2-3 tasks |
| Context overhead target | <30% |
| Spawn prompt tokens | 1500 max |

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

**Executor (main orchestrator) responsibilities:**
```
1. Analyze plan structure and task relationships
2. Build dependency graph (task → files touched, prerequisites)
3. Pre-execution: spawn critic to challenge the plan (devil's advocate)
4. If critic finds critical issues: fix plan before proceeding
5. Identify conflict-free groups (tasks touching different files)
6. Spawn parallel workers for independent task groups (max 3-5 workers)
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
- Spawn CRITIC subagent (haiku, read-only) to review what was done
- Critic checks: correctness, edge cases, regressions, deviation handling
- If critic finds issues: executor fixes before continuing to next milestone
- This is internal review, not user interaction

**Task tracking:**
- Track each parallel worker group as a unit of work — status updates as workers complete
- At milestones, the critic review itself becomes a tracked checkpoint in the execution flow
- Result aggregation updates the parent task status, not the individual workers
- Delegate simple tasks without tracking overhead; only track when multiple workers coordinate or depend on intermediate outputs

**Why:** No user interaction needed. Executor operates as intelligent orchestrator with parallel execution for speed and self-review for quality. Overhead: ~10-15% main context (higher than old single-subagent approach due to coordination, but better quality through parallelism and review).

---

**Pre-execution self-critique (devil's advocate):**

Before spawning workers, delegate a critic subagent to challenge the plan ITSELF — not the workers' output, but the plan's assumptions and structure. Read `agents/critic.md` for the agent template and spawn the critic with the plan as context.

If critic finds critical issues: fix the plan before spawning workers.
If critic finds minor concerns: note them for milestone review.

**Why:** Milestone self-review catches bad execution. Pre-execution critique catches bad plans. Catching a flawed plan before wasting parallel workers is cheaper than fixing after they complete.

---

### Strategy B: Segmented Execution

**Use when:** Plan has `checkpoint:human-verify` markers at segment boundaries. Each checkpoint separates a coherent autonomous block.

**Policy:** Subagents execute segments between checkpoints. Main context handles verification gates.

**Mechanism:**
```
1. Parse plan into segments (blocks between checkpoints)
2. For each segment:
```

**Autonomous vs checkpoint handling:**

| Element | Action |
|---------|--------|
| Segment (autonomous block) | Spawn subagent to execute block |
| `checkpoint:human-verify` | Execute in orchestrator context, present to user |
| Verification pass | Continue to next segment |
| Verification fail | STOP, present failure gate |

```
3. Aggregate all segment results
4. Create SUMMARY.md with full audit trail
5. Update ROADMAP.md
6. Commit
```

**Why:** Checkpoints require human judgment. Subagents handle pure execution between gates. Overhead: ~15-20% main context.

---

### Strategy C: Sequential Execution

**Use when:** Plan has `checkpoint:decision` or `checkpoint:human-action` markers. Outcomes affect subsequent task paths.

**Policy:** All execution in main context. User interaction required at each checkpoint.

**Mechanism:**
```
1. Load execution_context and context from plan
2. For each task:
   IF type="auto":
     - Execute in main context
     - Track deviations
   IF checkpoint:decision OR checkpoint:human-action:
     - Execute up to checkpoint
     - Present decision context to user
     - Wait for user choice
     - Continue on chosen path
3. Create SUMMARY.md
4. Update ROADMAP.md
5. Commit
```

**Why:** Decision-dependent execution cannot be safely delegated. User choices alter the execution path. Overhead: ~25-30% main context.

---

### Strategy Selection

| Checkpoint Types | Strategy | Main Context Usage |
|-----------------|----------|---------------------|
| None | A: Fully Autonomous | ~10-15% |
| human-verify | B: Segmented | ~15-20% |
| decision, human-action | C: Sequential | ~25-30% |

**Decision tree:** See `references/execution-strategies.md` for full strategy selection flow.

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

### Deviation Rule 4: Ask about architectural changes

**Trigger:** Fix/addition requires significant structural modification

**Action:** STOP. Present as `checkpoint:decision`. Use AskUserQuestion. Wait for decision.

**Numeric thresholds for "significant":**
- Schema migration affecting 3+ tables or entities
- API surface change affecting 5+ endpoints
- New file requiring architectural pattern integration
- Dependency addition that changes execution model
- Authentication/authorization model change

**Examples — IS architectural:**
- Adding new database table (not just column)
- Major schema changes (changing primary key, splitting tables)
- Introducing new service layer or architectural pattern
- Switching libraries/frameworks
- Breaking API change

**Examples — IS NOT architectural (decide yourself):**
- Which naming to use for a variable
- Where to put a file within an existing structure
- Which color scheme to use
- Minor formatting or style choices

**Process:**
1. STOP current task
2. Present as `checkpoint:decision`:
   ```
   type: checkpoint:decision
   label: Architectural Decision Required
   what: [describe what was found]
   proposed: [what you propose to do]
   options:
     A. Proceed with proposed change
     B. Different approach (describe what)
     C. Defer this decision
   ```
3. Use AskUserQuestion with structured options:
   - option A: "Proceed with proposed change"
   - option B: "Use a different approach"
   - option C: "Defer this decision"
4. WAIT for user choice
5. On choice, proceed accordingly

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
| 1 | Architectural changes | STOP, ask |
| 2 | Bugs, missing criticals, blockers | Fix automatically, track |
| 3 | Non-critical enhancements | Log to ISSUES.md, continue |

---

## Checkpoint Protocols

### Verify-Only Checkpoint

```markdown
## Checkpoint: Verify Migration

Before continuing, verify:
- [ ] Migration ran without errors
- [ ] Users table exists in dashboard
- [ ] Row count > 0

User confirms: [type "done" when verified]
```

**Protocol:**
1. Present verification checklist
2. Wait for user confirmation
3. Continue to next segment
4. Document verification in Summary

---

### Decision Checkpoint

```markdown
## Checkpoint: Auth Strategy Decision

Current approach: Session-based auth

Options:
1. Continue with session-based auth
2. Switch to JWT (stateless, better for mobile)
3. Hybrid (sessions + JWT refresh)

Choose: [1/2/3] or describe different approach
```

**Protocol:**
1. Present decision context clearly
2. Wait for user choice
3. Execute chosen path
4. Document decision in Summary

---

### Human-Action Checkpoint

```markdown
## Checkpoint: Manual Verification Needed

I cannot verify this automatically. You need to:

1. Open https://dashboard.example.com
2. Navigate to Users → API Keys
3. Copy the public key shown

Paste the key here when done.
```

**Protocol:**
1. Present clear instructions for manual action
2. Wait for user to complete action
3. Receive confirmation + any required output
4. Continue using provided information
5. Document the manual gate in Summary

---

## Authentication Gates

**Authentication errors are not failures — they are expected workflow gates.**

**Recognition:**
- CLI returns: "Not authenticated", "Not logged in", "Unauthorized"
- API returns: "Authentication required", "Invalid API key"
- Command fails with: "Please run {tool} login"

**Protocol:**
```
1. RECOGNIZE: This is an auth gate, not a bug
2. STOP: Current task execution pauses
3. PRESENT: Exact steps for user to authenticate
4. WAIT: Let user complete auth flow
5. VERIFY: Test credentials are valid
6. RETRY: Resume automation where it left off
7. CONTINUE: Normal execution resumes
```

**In Summary:** Document authentication gates as normal flow, not deviations.

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
- [Rule 4: architectural decision + user choice]
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

## Anti-Patterns

### ❌ Skipping verification
Marking a task complete without running the verify command. Verification is mandatory — it is the only proof the task actually succeeded.

### ❌ Treating auth gates as errors
Retrying authentication failures repeatedly instead of pausing and presenting the auth steps clearly to the user.

### ❌ Continuing past Rule 4
Attempting to proceed with an architectural change without user input. Rule 4 requires STOP + ASK + WAIT.

### ❌ Creating vague summaries
"Task completed" tells nothing. "JWT refresh rotation implemented using jose library with 15-minute access token expiry" tells everything.

### ❌ Ignoring context limits
Loading all project files instead of only those referenced in the plan. Context pressure degrades execution quality.

---

## Reference Index

| Reference | Purpose |
|-----------|---------|
| `references/execution-strategies.md` | Detailed strategy selection criteria |
| `references/checkpoint-protocols.md` | Checkpoint type templates and protocols |
| `references/deviation-rules.md` | Extended deviation handling with examples |
| `templates/autonomous-execution.md` | Template for Strategy A subagent prompts |
| `templates/segment-execution.md` | Template for Strategy B segment handoffs |
| `agents/critic.md` | Self-critique subagent for milestone reviews |

---

## Success Criteria

- Correct strategy selected based on checkpoint types
- All tasks executed with deviations tracked
- All verifications passed (or user informed of failures)
- SUMMARY.md created with substantive one-liner
- ROADMAP.md updated with plan count
- Git commit created with proper scope format
- Context usage under 30% overhead