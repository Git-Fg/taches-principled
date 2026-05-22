# Semantic Synergy Audit — taches-principled Ecosystem

**Scope:** 8 skills across planning, execution, verification, and reflection layers.
**Method:** Read-only vocabulary analysis. No execution.
**Date:** 2026-05-22

---

## Per-Skill Vocabulary Table

| Skill | Layer | Key Terms Used |
|-------|-------|----------------|
| `plan-task` | Planning | task file, draft, todo, in-progress, done, phase (2a-6), scratchpad, judgment criteria, weighted rubrics, target-quality, decomposition, parallelization, verification level, human-in-the-loop, Definition of Done |
| `implement-task` | Execution | step, implementation agent, judge, threshold (4.0/4.5), verification pattern (A/B/C), panel of judges, per-item judges, PASS/FAIL, fix-verify cycle, iteration, Definition of Done |
| `sadd-execute` | Execution | meta-judge, judge, implementation agent, YAML specification, rubrics, checklists, scoring criteria, retry loop, verdict, confidence score, parallel dispatch, sequential steps, competitive generation, CoT reasoning |
| `sadd-judge` | Verification | meta-judge, judge, evaluation specification, rubrics, scoring criteria, consensus, debate round, isolated context, confirmation bias, threshold leak, filesystem communication |
| `code-review` | Verification | review agent, bug hunter, security auditor, contracts reviewer, quality reviewer, impact score, confidence, evidence, file:line reference, critical/high/medium/low severity |
| `reflexion` | Reflection | self-critique, complexity triage, severity rating, evidence-based, decision point, verdict, confidence score, independent judge, consensus, cross-examination, root cause, pattern capture |
| `kaizen` | Guardrail/Improvement | continuous improvement, incremental, poka-yoke, standardized work, JIT/YAGNI, error-proofing, type system validation, fail fast, guardrail, design-time constraint |
| `fpf-propose` | Analysis/Decision | hypothesis, abduction, deduction, induction, R_eff (evidence reliability), WLNK (weakest link), Design Rationale Record (DRR), L0/L1/L2 knowledge levels, trust audit, first principles |

---

## Cross-Layer Term Overlaps

### Planning → Execution Handoff Terms

| Term | Used In | Meaning Across Layers |
|------|---------|----------------------|
| **Verification / Verification Level** | plan-task, implement-task, sadd-execute | Step-level quality gate type (None, Single Judge, Panel, Per-Item). Execution skills consume verification levels from planning output. |
| **Definition of Done** | plan-task, implement-task | Task-level completion criteria. Both layers reference same artifact location (task file). |
| **Target-quality / Threshold** | plan-task, implement-task | Minimum score for PASS (plan-task: 3.5 default; implement-task: 4.0/4.5). Consistent numeric contract between planning and execution. |
| **Rubric / Weighted Rubric** | plan-task, implement-task, sadd-execute, sadd-judge | Structured evaluation criteria with weights. Shared artifact format across layers. |
| **Step** | implement-task, sadd-execute | Implementation unit. Both use same concept but sadd-execute uses "sequential steps" as a mode name, not the primary artifact. |
| **Pass/Fail / Verdict** | implement-task, sadd-judge, sadd-execute, reflexion | Binary outcome decision. All verification-adjacent skills use some variant. |

### Verification → Reflection Handoff Terms

| Term | Used In | Meaning Across Layers |
|------|---------|----------------------|
| **Evidence / Evidence-based** | sadd-judge, reflexion, code-review, fpf-propose | Referenced facts supporting a finding. Critical in fpf-propose (R_eff calculation), present in all quality skills. |
| **Severity / Impact** | reflexion, code-review | Rating level for issues. reflexion uses critical/high/medium/low; code-review uses 0-100 mapped to similar scale. |
| **Root cause** | reflexion, kaizen, fpf-propose | Origin of a problem. kaizen says "trace backward"; reflexion "harvest" captures root cause; fpf-propose uses WLNK. |
| **Confidence** | reflexion, sadd-judge, code-review | Assessment reliability. reflexion uses 1-5 scale with explicit confidence calibration; code-review uses confidence-scored filtering. |
| **Decision point / Verdict** | reflexion, sadd-judge, implement-task | Formal conclusion after evaluation. |

### Shared Workflow Stage Vocabulary

| Stage Concept | Terms Used Across Ecosystem |
|--------------|----------------------------|
| **Quality gate before proceeding** | plan-task (phase gates), implement-task (judge PASS required), sadd-execute (meta-judge spec before judge), sadd-judge (consensus check before debate rounds) |
| **Iterative refinement** | implement-task (fix-verify cycles), plan-task (max-iterations per phase), reflexion (reflect → critique → memorize cycle), sadd-judge (debate rounds with consensus check) |
| **Context isolation** | sadd-judge (isolated sub-agent context), implement-task (orchestrator never reads artifacts), plan-task (fresh context per phase agent) |
| **Threshold-based routing** | plan-task (score >= threshold → PASS), implement-task (score >= threshold → PASS), sadd-judge (consensus check score proximity), fpf-propose (R_eff trust calculation) |

---

## BRITTLE References Found

**Result: ZERO skill-name citations.** No skill names another skill by name in trigger conditions or body text. This is the correct pattern.

However, one architectural reference exists in `plan-task` SKILL.md line 603:

> "Operates between task creation (add-task) and implementation (implement-task)."

This is a **pipeline position statement**, not a skill invocation. It describes workflow order, not a cross-skill call. The CLAUDE.md reinforces this is intentional compositional pairing ("create-plans/execute-plans are compositional by design"). This is acceptable because it describes workflow position, not implementation coupling.

**No brittle references detected.**

---

## SEMANTIC SYNERGY Confirmed

### Correct Cross-Layer Communication Patterns

1. **Verification level contract (plan-task → implement-task)**
   - `plan-task` Phase 6 adds `#### Verification` sections with explicit level (None/Single Judge/Panel/Per-Item Judges), threshold, and rubric weights
   - `implement-task` Pattern A/B/C selection maps directly from these sections
   - No skill names — only artifact field values flow between layers

2. **Meta-judge pattern (sadd-execute → sadd-judge)**
   - `sadd-execute` generates YAML evaluation specification via meta-judge
   - `sadd-judge` consumes that exact YAML — no modifications, no threshold leak
   - Both describe the pattern identically: "generate spec → pass exact spec → parse only structured header"
   - This is pure semantic agreement on a data format contract

3. **Threshold vocabulary shared across all judge-invoking skills**
   - `plan-task`: 3.5 default threshold
   - `implement-task`: 4.0 standard, 4.5 critical
   - `sadd-execute`: 4.0 pass threshold
   - `sadd-judge`: score proximity check (0.5 for consensus)
   - All use the same 1-5 scoring scale with consistent score labels

4. **Verification artifact format shared**
   - `#### Verification` section format (level, artifact path, threshold, rubric table)
   - Rubric table format: Criterion | Weight | Description
   - Weights sum to 1.0 invariant enforced across all skills
   - This is a cross-layer artifact format contract without skill naming

5. **Context isolation principle shared**
   - `implement-task`: "orchestrator never reads artifacts"
   - `sadd-judge`: "fresh judge sub-agent avoids confirmation bias"
   - `plan-task`: "fresh context per phase agent"
   - All express the same architectural principle differently — not one cites another

### Kaizen Integration Points

`kaizen` is a guardrail skill applied implicitly across all layers:
- Its four pillars (incremental improvement, poka-yoke, standardized work, JIT) shape decisions in planning (one phase at a time), execution (one step at a time), and verification (fail-fast evaluation)
- `plan-task` Decision Router: "use a structured analysis method (tracing backward, asking why iteratively) before taking action" — this references kaizen methods without naming them
- No skill names kaizen — it is absorbed as behavioral constraint

### FPF Integration Points

`fpf-propose` Decision Router line 13:
> "IF combining with reflection output → Use reflection findings to validate hypotheses"

This describes behavior: reflection produces findings, FPF can consume them. No skill name cited — only output type.

---

## Vocabulary Normalization Opportunities

### 1. Inconsistent Threshold Naming

| Skill | Term Used |
|-------|-----------|
| plan-task | `--target-quality X.X` |
| implement-task | `--target-quality X.X` (single value) or `X.X,Y.Y` (standard,critical) |
| sadd-execute | score >= 4.0 (PASS threshold mentioned in text, not a named flag) |
| sadd-judge | "score proximity check" but no explicit threshold flag |

**Recommendation:** Consider a shared term `quality-threshold` or `qt` for the numeric pass/fail boundary. Currently each skill invents slightly different argument names for the same concept.

### 2. "Judge" vs "Verification Agent" vs "Review Agent"

Three different skills use three different terms for the same role (independent quality evaluator):

| Skill | Term |
|-------|------|
| implement-task | judge |
| sadd-execute | judge |
| sadd-judge | judge |
| code-review | review agent |
| reflexion | independent judge |

All refer to the same pattern: dispatch an isolated sub-agent to evaluate work against criteria. The ecosystem would benefit from a canonical term — either all converge on "judge" (already dominant) or "evaluator" (more neutral).

### 3. "Meta-judge" is Named but Not Defined

`sadd-execute` and `sadd-judge` both reference "meta-judge" as a shared concept. `plan-task` has no meta-judge equivalent — it uses per-phase judges. Neither skill defines what a meta-judge IS in isolation; they assume the reader infers from shared context.

**Recommendation:** If meta-judge is a reusable pattern worth naming, document its role in one place. If it's an implementation detail of sadd-execute/sadd-judge only, keep as-is. Currently it's a named shared concept without an authoritative definition.

### 4. "Consensus" Used Differently

| Skill | Meaning |
|-------|---------|
| sadd-judge | 3 judges reach agreement through debate rounds |
| reflexion | "reasonable disagreement" documented when consensus not reached |

`sadd-judge` requires consensus; `reflexion` accepts persistent disagreement as a valid outcome. Both use "consensus" but with opposite urgency. This is not a bug — different verification contexts warrant different standards — but worth noting for vocabulary coherence.

### 5. "Artifact" Overloaded

All skills produce "artifacts" but mean different things:
- `plan-task`: task file, skill document, scratchpad, analysis file
- `implement-task`: created/modified source files (implementation output)
- `sadd-execute`: candidate solutions, evaluation reports
- `sadd-judge`: judge reports, synthesis reports
- `reflexion`: project memory updates

No layer explicitly defines what "artifact" means. It's used generically. For precision, skills could distinguish between "specification artifact" (plan output), "implementation artifact" (code output), and "evaluation artifact" (judgment output).

---

## Summary

**Semantic synergy: CONFIRMED.** Skills communicate through shared workflow vocabulary without naming each other.

**Key findings:**
- Zero skill-name citations in trigger conditions or body text — all cross-layer communication is via artifact formats and shared workflow stage vocabulary
- The meta-judge → judge pipeline is the strongest semantic contract — shared YAML format flows from `sadd-execute` generation to `sadd-judge` consumption
- Verification levels, rubrics, thresholds, and PASS/FAIL verdicts are consistent across all quality-adjacent skills
- Kaizen and FPF integrate without being named — absorbed as behavioral constraints and workflow input respectively
- Normalization opportunities exist in threshold argument naming, "judge" terminology, and "artifact" disambiguation — but these are polish-level, not architectural violations

**Recommended actions:**
1. Standardize `--target-quality` argument across all skills (currently plan-task and implement-task use it, but sadd-execute only mentions it in prose)
2. Consider adopting "judge" as the canonical term for independent quality evaluators across all skills
3. Document the meta-judge pattern once if it is to be reused beyond sadd-* plugins