# Skill Consolidation Candidates

Analysis date: 2026-05-23

## Summary

Current count: 38 skills across all plugins. Target: ~25 skills through strategic merging.

---

## Category 1: Problem Analysis Cluster

**Candidates:**
- `analyse` — auto-selects improvement method (Gemba Walk, VSM, Muda)
- `analyse-problem` — A3 format structured documentation
- `root-cause-analysis` — Five Whys and Fishbone methods
- `root-cause-tracing` — backward call stack tracing for debugging

**Rationale for merge:**
These four skills fragment problem investigation across incompatible taxonomies. They share a common purpose (understand what went wrong and why) but use different frameworks. A single skill with mode routing would reduce cognitive load on the routing system.

**Proposed new skill: `diagnose`**
```
Modes:
- INVESTIGATE (analyse + root-cause-analysis): Structured methods for recurring issues
- DOCUMENT (analyse-problem): A3 format for significant incidents
- TRACE (root-cause-tracing): Call stack debugging for bugs
```

**Expected reduction:** 4 skills → 1 skill (saves 3)

**Interaction with existing skills:**
- `code-simplify`: independent (complexity reduction, not problem finding)
- `code-review`: independent (quality assessment, not root cause)

---

## Category 2: Execution Dispatch Cluster

**Candidates:**
- `implement-task` (taches-principled) — developer + judge pattern with refine/continue
- `sadd-execute` (tp-sadd) — single/sequential/parallel/competitive with meta-judge
- `sadd-dispatch` (tp-sadd) — single task + plan-driven with code review gates

**Rationale for merge:**
All three do the same thing: dispatch subagents with quality verification. They differ in:
- Mode naming (single vs sequential vs parallel)
- Verification approach (judge vs meta-judge vs code review)
- Configuration complexity

The `implement-task` skill is the most sophisticated (refine/continue/human-in-the-loop). It should absorb the simpler dispatch patterns from tp-sadd skills.

**Proposed new skill: `execute`**
```
Modes:
- SINGLE: One task, one implementation, one judge
- SEQUENTIAL: Ordered steps with per-step verification
- PARALLEL: Independent targets with isolated retries
- COMPETITIVE: Best-of-N generation with judge consensus

Flags: --refine, --continue, --human-in-the-loop, --target-quality
```

**Implementation note:** This is essentially `implement-task` absorbing `sadd-execute`/`sadd-dispatch` patterns. The tp-sadd skills would become thin wrappers or be deprecated.

**Expected reduction:** 3 skills → 1-2 skills (saves 1-2)

---

## Category 3: Planning/Execution Pairs

**Current state:**
- `create-plans` + `execute-plans` — compositional pair (documented in CLAUDE.md as intentional)
- `create-prompts` + `execute-prompts` — compositional pair (documented in CLAUDE.md as intentional)
- `plan-task` — standalone refinement skill

**Observation:** The create/execute pairs are already compositional by design. No changes recommended.

**Potential simplification:** `plan-task` could become a mode of `create-plans` since both produce structured specifications. However, the separation is clean and intentional — no action needed.

---

## Category 4: Subagent Creation vs Subagent Execution

**Candidates:**
- `create-subagents` (taches-principled) — creates agent definition files, design-time
- `subagent-driven-development` (tp-sadd) — executes plans via subagent dispatch, runtime
- `sadd-dispatch` (tp-sadd) — dispatches subagents with CoT reasoning

**Rationale for separation:** These are actually different concerns:
- `create-subagents`: Design-time skill for creating agent definitions
- `subagent-driven-development`: Runtime skill for executing via subagents

The confusion arises because they share "subagent" in the name but serve different purposes. Keep separate.

**Note:** `launch-sub-agent` was deleted (shows D in git status) — this confirms tp-sadd is consolidating around `sadd-dispatch` and `subagent-driven-development`.

---

## Category 5: Reflexion — Already a Multi-Mode Skill

**Status:** `reflexion` is the canonical example of the multi-mode pattern we want to encourage.

```
Three modes in one skill:
- REFLECT: Self-critique with severity scoring
- CRITIQUE: Multi-judge consensus review
- MEMORIZE: Learning capture into project memory
```

**Recommendation:** Use `reflexion` as the template for other consolidations. The skill demonstrates that modes can share infrastructure (scoring rubric, bias countermeasures, output format) while providing distinct behaviors.

---

## Category 6: Ideation — Consolidation Already Done

**Status:** `brainstorm` was already merged into `ideation`. The SKILL.md explicitly states: "Brainstorm functionality is now consolidated into this skill — use ideation for all collaborative refinement."

**Implication:** This proves the consolidation strategy works. Other similar clusters can follow the same pattern.

---

## Category 7: kaizen, plan-do-check-act, write-concisely

**Analysis:**
- `kaizen`: Design-time constraints (incremental, poka-yoke, standardized, YAGNI)
- `plan-do-check-act`: Four-phase iterative PDCA cycle
- `write-concisely`: Writing improvement (Strunk & White)

**Recommendation:** These are orthogonal concerns. No consolidation needed. Each serves a distinct workflow stage.

---

## Category 8: do-competitively, judge-with-debate, sadd-tot

**Candidates:**
- `do-competitively` — competitive generation with meta-judge
- `judge-with-debate` — multi-round judge debate
- `sadd-tot` — Tree of Thoughts (ideate, prune, expand)

**Observation:** These are specialized evaluation/generation modes. They could potentially become modes of a single `evaluate` skill, but their differences (competitive, debate, ToT) suggest they serve distinct niches.

**Recommendation:** Leave as separate unless a future `evaluate` skill emerges that can naturally absorb them.

---

## Consolidated Recommendations

| Action | Skills Involved | New Skill | Savings |
|--------|-----------------|-----------|---------|
| **Merge** | `analyse` + `analyse-problem` + `root-cause-analysis` + `root-cause-tracing` | `diagnose` | 3 |
| **Absorb** | `sadd-execute` + `sadd-dispatch` into | `implement-task` (expand modes) | 1-2 |
| **No action** | `create-subagents` / `subagent-driven-development` | — | 0 |
| **No action** | Planning pairs (create-plans/execute-plans) | — | 0 |
| **No action** | kaizen, plan-do-check-act, write-concisely | — | 0 |

**Total estimated reduction:** 4-5 skills

**Resulting count:** ~33-34 skills (approaching but not at 25 target)

---

## Why 25 May Be Unrealistic

The current skill count reflects genuine functional diversity:
- Create vs execute lifecycle (create-plans/execute-plans)
- Planning vs refinement vs implementation stages
- Different verification strategies (judge, meta-judge, code review, ToT)
- Different problem types (code quality, process, incidents, bugs)

Further reduction would require either:
1. **Loss of capability** — collapsing distinct workflows into ambiguous handlers
2. **Over-abstraction** — generic skills that route to sub-skills but provide little value themselves

The more realistic target is ~30 skills with the above consolidations.

---

## Implementation Priority

1. **High value, low risk:** Merge the problem analysis cluster (4→1). The skills share purpose and have clear mode boundaries.

2. **Medium value, medium risk:** Expand `implement-task` to absorb tp-sadd dispatch patterns. Requires careful backward compatibility handling.

3. **Low value, high risk:** Attempt further merges. Likely to produce fragile routing or capability loss.