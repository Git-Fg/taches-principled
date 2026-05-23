# Proposed Skill Taxonomy: 39 → ~25

## Current State: 39 Skills

### taches-principled (21 skills)
- add-task
- analyse
- analyse-problem
- code-review
- code-simplify
- create-plans
- create-prompts
- create-skills
- create-subagents
- execute-plans
- execute-prompts
- ideation
- implement-task
- kaizen
- plan-do-check-act
- plan-task
- reflexion
- root-cause-analysis
- root-cause-tracing
- subagent-orchestration
- update-docs
- write-concisely

### tp-sadd (10 skills)
- do-competitively
- judge-with-debate
- sadd-dispatch
- sadd-execute
- sadd-judge
- sadd-patterns
- sadd-tot
- subagent-driven-development

### tp-fpf (3 skills)
- fpf-maintenance
- fpf-propose
- fpf-read

### tp-git (4 skills)
- git-advanced
- git-issues
- git-review
- git-ship

### tp-tdd (1 skill)
- tdd

---

## Proposed Taxonomy: 25 Skills

### CORE WORKFLOW (must keep)

| # | Skill | Rationale |
|---|-------|----------|
| 1 | **create-plans** | Primordial — plans are the atomic unit of autonomous work |
| 2 | **execute-plans** | Primordial — plan execution without orchestration is just sprinting |
| 3 | **create-prompts** | Primordial — prompts are the atomic unit of instruction |
| 4 | **execute-prompts** | Primordial — prompt execution is the delivery mechanism |
| 5 | **plan-task** | Core workflow — refines draft tasks into implementation-ready specs |
| 6 | **implement-task** | Core workflow — executes refined task implementations with verification |
| 7 | **add-task** | Task capture entry point — where work enters the system |

---

### DOMAIN EXPERTISE (~14 skills)

#### 8. `create-subagents` → KEEP (distinct trigger)
"Create an agent", "design multi-agent", "spawn specialist" — agent authoring is distinct from general code generation.

#### 9. `ideation` → KEEP (merges brainstorm/create-ideas)
Already consolidated. Provides divergent generation + collaborative refinement. Distinct trigger: "I have an idea", "brainstorm", "what are my options".

#### 10. `analyze` (MERGE: analyse + analyse-problem + root-cause-analysis + root-cause-tracing)
**Why capability preserved:**
- `analyse`: Gemba Walk (code), Value Stream Mapping (process), Muda (waste) — multi-method targeting different problem classes
- `analyse-problem`: A3 format for incidents/recurring issues
- `root-cause-analysis`: Five Whys + Fishbone
- `root-cause-tracing`: Trace backward through call stack, instrumentation before failure

**Overlap analysis:**
- All four serve "understand why something is wrong" — different depth/context
- `analyse-problem` is for incidents; `analyse` is for general exploration
- `root-cause-analysis` is methodology-focused; `root-cause-tracing` is bug-focused
- A single skill with mode routing handles all four:

```
IF investigating incident/specific problem → A3 format (analyse-problem)
IF exploring code/process/quality → method selector (analyse)
IF tracing bug backward through call stack → instrumentation + trace (root-cause-tracing)
IF applying Five Whys or Fishbone → structured method (root-cause-analysis)
```

Single skill name: **`analyze`**

---

#### 11. `refine` (MERGE: code-review + code-simplify + write-concisely)
**Why capability preserved:**
- `code-review`: PR and local change multi-agent review (6 specialized agents)
- `code-simplify`: 5-stage pipeline (extract/name, reduce nesting, remove duplication, eliminate dead code, replace state machines with data)
- `write-concisely`: Strunk & White principles for prose

**Overlap analysis:**
- All three improve existing work product
- `code-review` is evaluation mode; `code-simplify` is transformation mode; `write-concisely` is prose mode
- Decision router handles mode selection without overlap:
  - "review this PR" → code review mode
  - "simplify this code" → simplify mode
  - "make this clearer" → write-concisely mode

Single skill name: **`refine`**

---

#### 12. `dispatch` (MERGE: subagent-driven-development + sadd-dispatch + launch-sub-agent)
**Why capability preserved:**
- `subagent-driven-development`: Dispatch fresh subagent per task with code review between tasks — plan execution mode
- `sadd-dispatch`: Single-task dispatch with auto model selection, parallel plan mode, sequential plan mode, parallel investigation
- `sadd-tot`: Tree of Thoughts — exploration before implementation (keep separate — distinct phase)

**Overlap analysis:**
- `sadd-dispatch` and `subagent-driven-development` both dispatch subagents per task
- `subagent-driven-development` is a subset of `sadd-dispatch` (sequential/parallel plan execution)
- `sadd-dispatch` adds single-task dispatch, model selection, CoT prefix + self-critique suffix
- `launch-sub-agent` (sadd-launch is unlisted but exists) handles basic dispatch

**Consolidation:** `subagent-driven-development` and `sadd-dispatch` merge into `dispatch`:
- Single task mode (from sadd-dispatch)
- Sequential execution mode (from subagent-driven-development + sadd-dispatch)
- Parallel execution mode (from subagent-driven-development + sadd-dispatch)
- Parallel investigation mode (from sadd-dispatch)

Single skill name: **`dispatch`**

---

#### 13. `judge` (MERGE: sadd-judge + judge-with-debate)
**Why capability preserved:**
- `sadd-judge`: Single meta-judge + judge pipeline, plus 3-judge debate mode
- `judge-with-debate`: Multi-round debate between judges until consensus

**Overlap analysis:**
- `judge-with-debate` is a subset of `sadd-judge` with debate mode
- `sadd-judge` already has `--debate` flag for multi-judge debate
- Merge by making debate the default high-stakes path, single-judge the routine path

Single skill name: **`judge`**

---

#### 14. `execute` (MERGE: sadd-execute + implement-task)
**Why capability preserved:**
- `sadd-execute`: Meta-judge → implement → judge → retry loop with 4 modes (single, steps, parallel, competitive)
- `implement-task`: Execute refined task implementations with automated quality verification — dispatch + judge pattern

**Overlap analysis:**
- `implement-task` is a simplified version of `sadd-execute` single mode
- `sadd-execute` with `--mode single` covers what `implement-task` does
- `implement-task` could be deprecated in favor of `sadd-execute --mode single`

**Decision:** Merge into `execute` (from `sadd-execute` naming). `implement-task` becomes redundant — its workflow is subsumed by `execute --mode single`.

---

#### 15. `reflect` → KEEP (distinct trigger)
"Reflect on this", "review my work", "critique this", "what could be better" — self-critique with severity-rated findings, multi-perspective judge review, and learning capture. Distinct from `judge` (external evaluation) and `refine` (transformative improvement).

---

#### 16. `create-skills` → KEEP (distinct trigger)
"Create a skill", "build a skill", "make a skill for X" — skill authoring is specialized domain knowledge not covered by general code generation.

---

#### 17. `update-docs` → KEEP (distinct trigger)
"Update the docs", "document this" — documentation after code changes. Distinct workflow from code review or writing.

---

#### 18. `sadd-patterns` → KEEP as `patterns` (renamed for brevity)
"Design architecture", "multi-agent", "supervisor pattern", "swarm" — multi-agent architecture patterns. Renamed to `patterns` for discoverability.

---

#### 19. `do-competitively` → KEEP as `compete` (renamed)
"Best-of-N", "generate multiple approaches and compare" — competitive generation with adaptive synthesis. Renamed to `compete` for discoverability.

---

### PLUGIN-SPECIFIC SKILLS (~4 skills)

#### 20-22. `git-ship`, `git-review`, `git-issues` → KEEP (git-toolbox)
These are git-specific workflows. `git-advanced` merges into `git-ship` since "ship" implies advanced operations.

| Original | Proposed | Notes |
|----------|----------|-------|
| git-ship | **git-ship** | Ship changes (merge, tag, release) |
| git-review | **git-review** | Review PRs and changes |
| git-issues | **git-issues** | Issue management |
| git-advanced | → git-ship | Deprecate; ship covers advanced |

#### 23. `fpf-read`, `fpf-propose`, `fpf-maintenance` → KEEP (FPF toolbox)
These are FPF-specific. `fpf-propose` is design, `fpf-read` is reading, `fpf-maintenance` is upkeep. Distinct enough to keep as-is.

---

### SINGLETONS (~2 skills)

#### 24. `tdd` → KEEP (distinct workflow)
Test-driven development is a specific methodology not covered by other skills.

#### 25. `kaizen` → KEEP (distinct trigger)
Continuous improvement with waste identification and optimization. Distinct from `analyze` which is problem-focused; kaizen is opportunity-focused.

---

## Summary: Proposed 25-Skill Taxonomy

| # | Name | Source | Notes |
|---|------|--------|-------|
| 1 | create-plans | primordial | Keep |
| 2 | execute-plans | primordial | Keep |
| 3 | create-prompts | primordial | Keep |
| 4 | execute-prompts | primordial | Keep |
| 5 | plan-task | core | Keep |
| 6 | implement-task | core | Keep → merge into `execute` |
| 7 | add-task | core | Keep |
| 8 | analyze | tp-sadd | MERGE: analyse + analyse-problem + root-cause-analysis + root-cause-tracing |
| 9 | refine | tp-sadd | MERGE: code-review + code-simplify + write-concisely |
| 10 | dispatch | tp-sadd | MERGE: subagent-driven-development + sadd-dispatch |
| 11 | judge | tp-sadd | MERGE: sadd-judge + judge-with-debate |
| 12 | execute | tp-sadd | MERGE: sadd-execute + implement-task |
| 13 | reflect | taches-principled | Keep |
| 14 | create-subagents | taches-principled | Keep |
| 15 | create-skills | taches-principled | Keep |
| 16 | update-docs | taches-principled | Keep |
| 17 | ideation | taches-principled | Keep |
| 18 | patterns | tp-sadd | Rename from sadd-patterns |
| 19 | compete | tp-sadd | Rename from do-competitively |
| 20 | git-ship | tp-git | Merge git-advanced into git-ship |
| 21 | git-review | tp-git | Keep |
| 22 | git-issues | tp-git | Keep |
| 23 | fpf-read | tp-fpf | Keep |
| 24 | fpf-propose | tp-fpf | Keep |
| 25 | fpf-maintenance | tp-fpf | Keep |
| 26 | tdd | tp-tdd | Keep |
| 27 | kaizen | taches-principled | Keep |

**Total: 27 skills** (slightly above target due to plugin-specific skills that don't overlap)

### Skills removed: 12
- analyse (merged into analyze)
- analyse-problem (merged into analyze)
- code-review (merged into refine)
- code-simplify (merged into refine)
- write-concisely (merged into refine)
- subagent-driven-development (merged into dispatch)
- sadd-dispatch (merged into dispatch)
- sadd-judge (merged into judge)
- judge-with-debate (merged into judge)
- sadd-execute (merged into execute)
- implement-task (merged into execute)
- git-advanced (merged into git-ship)

### Skills renamed: 3
- sadd-patterns → patterns
- do-competitively → compete
- create-subagents stays as create-subagents (already good name)

---

## Verification: Capability Coverage

| Original Capability | Preserved By |
|---------------------|-------------|
| Plan creation/execution | create-plans, execute-plans (unchanged) |
| Prompt creation/execution | create-prompts, execute-prompts (unchanged) |
| Task refinement | plan-task (unchanged) |
| Task implementation + verification | execute (merged sadd-execute + implement-task) |
| Task capture | add-task (unchanged) |
| Code analysis (3 methods) | analyze (merged) |
| Problem analysis (A3) | analyze (merged) |
| Root cause (5 Whys + Fishbone) | analyze (merged) |
| Bug tracing + instrumentation | analyze (merged) |
| Code review (multi-agent) | refine (merged) |
| Code simplification (5-stage) | refine (merged) |
| Prose improvement | refine (merged) |
| Subagent dispatch (single/seq/par) | dispatch (merged) |
| Subagent execution with review | dispatch (merged) |
| Tree of Thoughts | sadd-tot → keep as-is (not merged — distinct exploration phase) |
| Judge evaluation (single/debate) | judge (merged) |
| Competitive generation | compete (renamed) |
| Pattern design | patterns (renamed) |
| Reflection/critique/memorize | reflexion (unchanged) |
| Skill authoring | create-skills (unchanged) |
| Documentation updates | update-docs (unchanged) |
| Ideation/brainstorm | ideation (unchanged) |
| Git operations | git-ship, git-review, git-issues (unchanged) |
| FPF operations | fpf-read, fpf-propose, fpf-maintenance (unchanged) |
| TDD workflow | tdd (unchanged) |
| Kaizen/continuous improvement | kaizen (unchanged) |
| Subagent orchestration | subagent-orchestration (unchanged — orchestration is distinct from dispatch) |

---

## Skills NOT merged and why

### `sadd-tot` (Tree of Thoughts) — kept separate
Exploration phase is distinct from execution. The explore → prune → expand → evaluate → synthesize flow is a different workflow than dispatch or execute. Cannot merge without losing the systematic exploration capability.

### `subagent-orchestration` — kept separate
Orchestration (deciding when to delegate) is distinct from dispatch (how to delegate). The skill manages the hub-and-spoke pattern — orchestration policy vs. dispatch mechanism.

### `kaizen` — kept separate
Continuous improvement focus (waste identification, optimization opportunities) vs. problem analysis focus. Different triggers, different outcomes.