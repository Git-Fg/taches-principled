# Cross-Plugin Synergy Analysis

## Plugin Inventory

| Plugin | Version | Stage | Core Function |
|--------|---------|-------|---------------|
| **taches-principled** | 0.4.0 | Full lifecycle | Planning, execution, prompts, review, analysis, ideation, docs, code simplification |
| **tp-sadd** | 0.2.0 | Execution + Verification | Multi-pattern agent dispatch with judge verification (single, sequential, parallel, competitive) |
| **tp-sdd** | 0.2.0 | Planning + Execution | Task refinement (plan-task) + implementation with verification (implement-task) |
| **tp-fpf** | 0.2.0 | Reasoning | First Principles Framework — hypothesis generation, verification, validation, audit, decision |
| **tp-git** | 0.2.0 | Delivery | Conventional commits, PR creation, branch management |
| **tp-tdd** | 0.2.0 | Testing | Test-driven development (Red-Green-Refactor), test coverage, test repair |
| **tp-ddd** | 0.1.0 | Architecture | Domain-driven design rules — clean architecture, CQRS, error handling |

---

## Communication Gaps

### Gap 1: FPF Decision Output has No Clear Consumer

**Problem:** The `fpf-propose` skill produces "Design Rationale Records" (DRRs) in `.fpf/decisions/` but nothing consumes these decisions as input for planning or execution.

**Expected flow (not implemented):**
```
fpf-propose (decide) → DRR in .fpf/decisions/
    ↓
taches-principled:plan-task or tp-sdd:plan-task (should consume DRR)
    ↓
taches-principled:execute-plans or tp-sadd:sadd-execute (should consume decision)
```

**Current reality:** FPF decisions are standalone artifacts. No skill references FPF output as input. The CLAUDE.md says "feeds into B" but B doesn't accept that format.

### Gap 2: TDD Tests Have No Explicit Contract for Implementation Skills

**Problem:** `tp-tdd:tdd` writes tests, but there's no defined contract specifying:
- Where tests must be located
- What naming convention they must follow
- What the implementation skill (taches-principled:implement-task or tp-sdd:implement-task) expects

**Expected flow:**
```
tp-tdd (write tests) → Test files at known paths
    ↓
taches-principled:implement-task (should verify tests pass as part of its verification)
```

**Current reality:** implement-task skills have their own verification rubrics but don't explicitly consume test output from tp-tdd. The skills are parallel tracks, not integrated.

### Gap 3: Planning Skills Output Different Task Formats

**Problem:** `taches-principled:plan-task` and `tp-sdd:plan-task` produce task files at `.specs/tasks/todo/` but with incompatible internal formats.

- **taches-principled:plan-task**: Outputs to `.specs/tasks/{draft,todo,in-progress,done}/` with 7-phase structure (research, business analysis, architecture, decomposition, parallelize, verifications, promote)
- **tp-sdd:plan-task**: Same structure, identical methodology — they appear to be duplicates with different plugin namespaces

**Issue:** Two plugins with identical purpose (plan-task) producing identically-structured artifacts in the same directory structure. This is redundant.

### Gap 4: Implementation Skills Accept Different Task Formats

**Problem:** `taches-principled:implement-task` and `tp-sdd:implement-task` both:
- Read from `.specs/tasks/todo/`
- Produce to `.specs/tasks/in-progress/`
- Move to `.specs/tasks/done/`
- Use identical patterns (Pattern A/B/C, judge verification, --continue, --refine)

They are functionally identical with different namespaces.

---

## Contract Mismatches

### Mismatch 1: create-plans/execute-plans vs saddle equivalents

**taches-principled:create-plans** outputs:
- `PLAN.md` in `.principled/plans/phases/{id}/`
- Uses `checkpoint:` markers for execution strategy selection
- Outputs `SUMMARY.md` after execution

**tp-sadd:sadd-execute** consumes:
- Task descriptions passed directly (not PLAN.md files)
- Uses `--mode single|steps|parallel|competitive` for execution
- Produces reports to `.specs/reports/`

**Issue:** These are not interchangeable. create-plans produces structured plan files; sadd-execute expects direct task descriptions. There's no adapter path.

### Mismatch 2: Prompt Creation vs Execution Workflow

**taches-principled:create-prompts** outputs:
- `.principled/prompts/[slug]-[number]-[name].md`

**taches-principled:execute-prompts** consumes:
- Same `.principled/prompts/` directory

**BUT:** There's no tp-sadd equivalent that consumes `.principled/prompts/`. The tp-sadd skills operate on different artifact paths (`.specs/`).

### Mismatch 3: Evaluation Patterns Use Different Report Locations

| Skill | Report Location |
|-------|-----------------|
| taches-principled:implement-task | Writes `[DONE]` markers back to task file |
| tp-sdd:implement-task | Writes `[DONE]` markers back to task file |
| tp-sadd:sadd-judge | `.specs/reports/` with judge debate files |
| tp-sadd:do-competitively | `.specs/reports/` with candidate solutions |
| fpf-propose | `.fpf/decisions/` and `.fpf/evidence/` |

**Issue:** No unified reporting convention. Each plugin maintains its own artifact namespace with no cross-pollination.

---

## Missing Handoffs

### Missing Handoff 1: Plan → Execute (No Direct Path)

**create-plans** says: "When user says 'execute', 'run', 'build it': Load the execution skill to proceed"

**But:** There's no explicit contract that create-plans outputs something execute-plans can consume. The plan is a prompt, but execute-plans reads PLAN.md files from `.principled/plans/phases/`. The create-plans skill creates these, but execute-plans doesn't verify it's reading output from create-plans specifically.

**Gap:** There's no "this plan is ready for execution" marker that execute-plans can verify.

### Missing Handoff 2: plan-task → implement-task (No Quality Gate)

**plan-task** (both tp-sdd and taches-principled) outputs refined tasks to `.specs/tasks/todo/`

**implement-task** consumes from `.specs/tasks/todo/`

**But:** implement-task has its own verification rubrics and judge verification. plan-task also has judge verification at each phase. The task goes through two independent quality gates with no shared criteria format.

**Gap:** No contract specifying that plan-task's output format satisfies implement-task's input expectations. The rubrics are incompatible: plan-task uses phase-based scoring; implement-task uses step-based Pattern A/B/C verification.

### Missing Handoff 3: git-ship Has No Integration Upstream

**tp-git:git-ship** creates commits and PRs, but:
- No skill explicitly calls git-ship after completing work
- The git-ship skill itself says "Relationship to development pipeline: Creates the git history and PR artifacts consumed by review, changelog generation, and release workflows downstream"
- But no upstream skill says "when done, invoke git-ship"

**Gap:** No skill says "commit this work" as a terminal action. The handoff is implied but not encoded.

### Missing Handoff 4: TDD Has No Handoff to Implementation Verification

**tp-tdd:tdd** follows Red-Green-Refactor:
```
RED (write test) → GREEN (write code) → REFACTOR
```

**But:** After TDD completes, there's no explicit handoff to an implementation verification skill. The tests are written, but implement-task skills expect to run their own verification.

**Gap:** The test-first workflow doesn't connect to the step-verification workflow of implement-task.

---

## Conceptual Conflicts

### Conflict 1: Verification Terminology

| Plugin | Term | Meaning |
|--------|------|---------|
| taches-principled:implement-task | **Pattern A/B/C** | Verification levels (None, Single Judge, Panel of 2 Judges) |
| tp-sadd:sadd-judge | **meta-judge + judge** | Two-phase evaluation |
| tp-sadd:do-competitively | **Generate-Critique-Synthesize** | Three-phase competitive |
| fpf-propose | **R_eff, WLNK** | Evidence reliability scores |

**Issue:** "Judge" appears in multiple plugins with different meanings:
- tp-sadd:sadd-judge = evaluation subagent
- tp-sadd:sadd-execute = verification agent in meta-judge pattern
- implement-task = panel judge for step verification

### Conflict 2: Task Lifecycle Terminology

| Plugin | Term | Location |
|--------|------|----------|
| taches-principled | **draft → todo → in-progress → done** | `.specs/tasks/` |
| tp-sadd | **.specs/reports/** | Evaluation outputs |
| fpf-propose | **L0 → L1 → L2 → invalid** | Hypothesis knowledge layers |

**Issue:** Three different lifecycle stage systems. The same artifact could be in multiple states simultaneously with no translation layer.

### Conflict 3: "Subagent" vs "Agent" Terminology

| Plugin | Term | Context |
|--------|------|---------|
| tp-sadd | **launch-sub-agent**, subagent-driven-development, sadd-dispatch | "launch a sub-agent" |
| taches-principled | **subagent-orchestration** | "spawn a [role] subagent" |

**Issue:** Both use "subagent" but with different dispatch vocabulary. The CLAUDE.md says "spawn a [role] subagent" but tp-sadd skills use "launch", "dispatch", "spawn" interchangeably.

### Conflict 4: Quality Threshold Defaults

| Skill | Default Threshold |
|-------|-------------------|
| plan-task (taches-principled) | 3.5/5.0 |
| plan-task (tp-sdd) | 3.5/5.0 |
| implement-task (taches-principled) | 4.0/5.0 (standard), 4.5/5.0 (critical) |
| implement-task (tp-sdd) | 4.0/5.0 (standard), 4.5/5.0 (critical) |
| sadd-judge | No default stated |
| do-competitively | 3.0/5.0 (adaptive strategy thresholds differ) |

**Issue:** Different default thresholds across skills. A task refined at 3.5 might be rejected by an implementation at 4.0.

---

## Named Plugin References (Violations)

**Result:** No violations found.

Grep for `tp-sadd`, `tp-sdd`, `tp-fpf`, `tp-git`, `tp-tdd`, `tp-ddd` across all skill files returned no matches. The isolation principle is being followed — no skill names another plugin by prefix.

However, there are implicit coupling issues:
- taches-principled skills reference "the execution skill" or "the planning skill" without specifying which plugin's execution or planning
- The compositional pairs (create-plans/execute-plans, create-prompts/execute-prompts) are within the same plugin, not cross-plugin

---

## Additional Findings

### Finding 1: Significant Overlap Between tp-sdd and taches-principled

Both plugins have:
- `plan-task` skill (identical 7-phase refinement workflow)
- `implement-task` skill (identical Pattern A/B/C + judge verification)
- `brainstorm` / `ideation` (both have brainstorming skills)

**Assessment:** These are duplicates. The only difference is the plugin namespace. Either:
1. tp-sdd should be removed as redundant
2. Or tp-sdd should be specialized for a different purpose (e.g., faster with fewer phases)

### Finding 2: No Plugin Consumes FPF Output

The First Principles Framework produces decisions but no planning or execution skill references these decisions as input. This makes FPF a standalone reasoning tool that doesn't integrate into the workflow.

**Recommendation:** fpf-propose should output a machine-readable decision summary that plan-task can ingest as context.

### Finding 3: TDD is Orphaned

tp-tdd:tdd is a complete test-first workflow but has no explicit handoff to implementation or verification. It's self-contained but disconnected.

### Finding 4: git-ship is Terminal-Only

git-ship creates commits and PRs but no upstream skill says "when done, invoke git-ship". The delivery step is implicit, not orchestrated.

---

## Summary

| Category | Count |
|----------|-------|
| Communication gaps | 4 |
| Contract mismatches | 3 |
| Missing handoffs | 4 |
| Conceptual conflicts | 4 |
| Named plugin violations | 0 |

**Key issues:**
1. **tp-sdd is a near-duplicate of taches-principled** — both have plan-task and implement-task with identical structure
2. **FPF decisions are not consumed by any planning skill** — reasoning is disconnected from action
3. **No unified artifact namespace** — each plugin maintains its own `.specs/`, `.fpf/`, `.principled/` paths
4. **Verification terminology is inconsistent** — "judge" means different things in different contexts