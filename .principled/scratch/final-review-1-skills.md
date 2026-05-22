# Final Audit Report: taches-principled Skill Ecosystem

**Date:** 2026-05-22
**Auditor:** Independent quality auditor
**Files audited:** 60 (22 core skills + 9 tp-sadd + 3 tp-fpf + 4 tp-git + 5 tp-sdd + 1 tp-tdd + 14 tp-ddd rules + 1 tp-ddd reference + 1 core rules)
**Files expected per brief:** ~45; **actual files read:** 60

---

## Summary

| Severity | Count |
|----------|-------|
| CRITICAL | 0 |
| HIGH | 0 |
| MEDIUM | 9 |
| LOW | 5 |
| **Total** | **14** |

**Verdict: CONDITIONAL PASS** — No critical or high issues found. 9 medium and 5 low issues identified, primarily cross-skill name references and formatting inconsistencies. Correct these before shipping.

---

## Count Discrepancies (Note)

The brief stated "23 core skills" and "15 tp-sadd skills". Actual counts: **22 core skills** and **9 tp-sadd skills**. This suggests either files were removed during refactoring or the brief had stale counts. No orphaned file paths were detected. This does not block the audit.

---

## Medium Issues

### M1: Cross-skill name reference — subagent-orchestration -> create-subagents

**File:** `skills/subagent-orchestration/SKILL.md` lines 298-299
**Detail:** `"This skill complements \`create-subagents\`."`
**Why:** Directly names another skill by identifier. If `create-subagents` is renamed or archived, this reference breaks silently. The `-orchestrator` naming exception does not apply (`-orchestration` vs `-orchestrator`).
**Fix:** Replace with natural language: "This skill complements the subagent authoring skill." or "See the subagent creation workflow for companion subagent definitions."

---

### M2: Cross-skill name reference — subagent-driven-development -> finishing-a-development-branch

**File:** `plugins/tp-sadd/skills/subagent-driven-development/SKILL.md` lines 95, 128
**Detail:** `"Use finishing-a-development-branch skill to verify tests"` (line 95) and similar (line 128)
**Why:** References a skill by name that may not exist in the current ecosystem. Creates brittle dependency.
**Fix:** Replace with natural language: "Use the branch completion workflow to verify tests."

---

### M3: Cross-skill name reference — fpf-maintenance -> fpf-propose

**File:** `plugins/tp-fpf/skills/fpf-maintenance/SKILL.md` line 46
**Detail:** `"Next: Run fpf-propose to start fresh"`
**Why:** Plugin-internal cross-skill name reference. Creates intra-plugin brittleness.
**Fix:** Replace with: "Next: Run the hypothesis proposal workflow to start fresh."

---

### M4: Cross-skill name reference — fpf-read -> fpf-propose (2 occurrences)

**File:** `plugins/tp-fpf/skills/fpf-read/SKILL.md` lines 12, 14
**Detail:** `"Suggest running fpf-propose to create new hypotheses"` (line 12), `"with option to run fpf-propose"` (line 14)
**Why:** Same pattern as M3 — names another skill directly.
**Fix:** Replace with natural language: "Suggest running the hypothesis proposal workflow."

---

### M5: Cross-skill name reference — tp-sdd/add-task -> plan-task

**File:** `plugins/tp-sdd/skills/add-task/SKILL.md` line 12
**Detail:** `"task already exists and needs refinement -> DO NOT use this skill; use plan-task"`
**Why:** Plugin-internal cross-skill name reference.
**Fix:** Replace with: "...use the task refinement workflow instead."

---

### M6: Cross-skill name reference — tp-sdd/plan-task -> implement-task

**File:** `plugins/tp-sdd/skills/plan-task/SKILL.md` line 11
**Detail:** `"task is already implementation-ready -> DO NOT use this skill; use implement-task"`
**Why:** Same pattern as M5.
**Fix:** Replace with: "...use the implementation workflow instead."

---

### M7: create-plans references execute-plans by name (compositional pair exception)

**File:** `skills/create-plans/SKILL.md` line 20
**Detail:** `"Load \`execute-plans\` skill (compositional pair)"` — also line 397
**Why:** The CLAUDE.md explicitly exempts compositional pairs (create-plans/execute-plans, create-prompts/execute-prompts). However, the name `execute-plans` still creates a brittle string dependency if the execution skill is renamed.
**Assessment:** Accepted per CLAUDE.md exception, but flagged for awareness. If `execute-plans` is renamed, `create-plans` and `create-prompts` both break silently.
**Fix (optional):** Use natural language: "Load the plan execution skill."

---

### M8: create-prompts references execute-prompts by name (compositional pair exception)

**File:** `skills/create-prompts/SKILL.md` line 484
**Detail:** `"Prompts created by this skill are executed by \`execute-prompts\`."`
**Why:** Same compositional pair exception as M7.
**Assessment:** Accepted per CLAUDE.md exception but flagged for awareness.

---

### M9: Skills exceeding 500-line indicative threshold

**Files and line counts:**
- `skills/create-subagents/SKILL.md` — 612 lines
- `skills/create-plans/SKILL.md` — 606 lines
- `skills/plan-task/SKILL.md` — 603 lines
- `skills/execute-plans/SKILL.md` — 592 lines
- `skills/implement-task/SKILL.md` — 568 lines
- `skills/create-skills/SKILL.md` — 511 lines

**Why:** The 500-line threshold is documented as "indicative, not prescriptive" in project memory. These skills are complex orchestration workflows with detailed reference content. However, 6 out of 22 core skills exceed the threshold, which suggests the delta principle may not be fully applied — content that Claude already knows may be inflating these files.
**Assessment:** Not a blocker, but review each for delta principle compliance. Content in these large skills should be scrutinized: does every section change behavior from Claude's default, or is some restating known patterns?

---

## Low Issues

### L1: Decision router lacks blank line before H1 — implement-task

**File:** `skills/implement-task/SKILL.md` line 15
**Detail:** The decision router ends at line 15 and `# Implement Task` starts on the same logical block with no blank line separator.
**Fix:** Insert a blank line between the decision router and the H1 heading.

---

### L2: Decision router lacks blank line before H1 — plan-task

**File:** `skills/plan-task/SKILL.md` line 15
**Detail:** Same pattern as L1 — decision router flows directly into `# Plan Task` heading.
**Fix:** Insert a blank line.

---

### L3: Decision router uses table format instead of IF/THEN — subagent-orchestration

**File:** `skills/subagent-orchestration/SKILL.md` lines 13-21
**Detail:** All other skills use `IF X -> Y` pattern. This skill uses a markdown table with `Situation | Action` columns.
**Why:** While a table is still functional for routing, it breaks consistency with the 50+ other skills. The IF/THEN pattern is specified in the brief's audit criteria.
**Fix:** Convert to IF/THEN pattern for consistency.

---

### L4: Strong self-directed language near-threat — reflexion bias countermeasures

**File:** `skills/reflexion/SKILL.md` lines 58-68
**Detail:** `"Praise is forbidden. Your job is rejection."` and `"You are programmed to be lenient. Fight your nature."`
**Why:** This is strong language directed at the AI itself to counter sycophancy bias. It is intentionally emphatic and not threatening to users. However, it borders on the "threatening/unprofessional" criterion.
**Assessment:** Acceptable for purpose. Style note only — no change required.

---

### L5: Strong self-directed language — tdd Iron Law

**File:** `plugins/tp-tdd/skills/tdd/SKILL.md` lines 32-33
**Detail:** `"Write code before the test? Delete it. Start over. ... Delete means delete."`
**Why:** Emphatic teaching language reinforcing strict TDD discipline. Not threatening to users.
**Assessment:** Acceptable for purpose. Style note only — no change required.

---

## Observations (Non-Issues)

### Skill name collision: core vs tp-sdd

**Files:**
- `skills/add-task/SKILL.md` and `plugins/tp-sdd/skills/add-task/SKILL.md` — both named `add-task`
- `skills/plan-task/SKILL.md` and `plugins/tp-sdd/skills/plan-task/SKILL.md` — both named `plan-task`
- `skills/implement-task/SKILL.md` and `plugins/tp-sdd/skills/implement-task/SKILL.md` — both named `implement-task`

**Detail:** Three skill names are duplicated between the core and tp-sdd plugin. If both are installed, load priority determines which wins (project > plugin). The user may be unaware of these collisions.
**Action:** Verify this is intentional (tp-sdd overrides core versions). If not, rename either the core or plugin versions.

---

### typescript-best-practices.md missing frontmatter

**File:** `rules/typescript-best-practices.md`
**Detail:** This file has no YAML frontmatter at all. It is loaded as a CLAUDE.md-adjacent rule. If it is meant to be a path-scoped rule, it needs `paths` frontmatter. If it is a global rule, the omission is acceptable.
**Action:** Add `paths: ["src/**/*"]` frontmatter if scoping is intended, or leave as-is for global application.

---

### Description length audit (all skills under 150 chars check)

**Status:** All skill descriptions are under 200 chars. Most are under 150 chars. The `create-skills` description at ~160 chars and `subagent-orchestration` at ~230 chars are the longest. Not a violation but worth noting.

---

## Per-Skill Assessment Summary

| Skill | Location | Status |
|-------|----------|--------|
| add-task | core | PASS |
| analyse-problem | core | PASS |
| analyse | core | PASS |
| code-review | core | PASS |
| code-simplify | core | PASS |
| create-plans | core | PASS (see M7) |
| create-prompts | core | PASS (see M8) |
| create-skills | core | PASS (see M9) |
| create-subagents | core | PASS (see M9) |
| execute-plans | core | PASS (see M9) |
| execute-prompts | core | PASS |
| ideation | core | PASS |
| implement-task | core | PASS (L1, M9) |
| kaizen | core | PASS |
| plan-do-check-act | core | PASS |
| plan-task | core | PASS (L2, M9) |
| reflexion | core | PASS (L4) |
| root-cause-analysis | core | PASS |
| root-cause-tracing | core | PASS |
| subagent-orchestration | core | M1, L3 |
| update-docs | core | PASS |
| write-concisely | core | PASS |
| do-competitively | tp-sadd | PASS |
| judge-with-debate | tp-sadd | PASS |
| launch-sub-agent | tp-sadd | PASS |
| sadd-dispatch | tp-sadd | PASS |
| sadd-execute | tp-sadd | PASS |
| sadd-judge | tp-sadd | PASS |
| sadd-patterns | tp-sadd | PASS |
| sadd-tot | tp-sadd | PASS |
| subagent-driven-development | tp-sadd | M2 |
| fpf-maintenance | tp-fpf | M3 |
| fpf-propose | tp-fpf | PASS |
| fpf-read | tp-fpf | M4 |
| git-advanced | tp-git | PASS |
| git-issues | tp-git | PASS |
| git-review | tp-git | PASS |
| git-ship | tp-git | PASS |
| add-task | tp-sdd | M5 |
| brainstorm | tp-sdd | PASS |
| create-ideas | tp-sdd | PASS |
| implement-task | tp-sdd | PASS |
| plan-task | tp-sdd | M6 |
| tdd | tp-tdd | PASS (L5) |
| call-site-honesty | tp-ddd | PASS |
| clean-architecture-ddd | tp-ddd | PASS |
| command-query-separation | tp-ddd | PASS |
| domain-specific-naming | tp-ddd | PASS |
| early-return-pattern | tp-ddd | PASS |
| error-handling | tp-ddd | PASS |
| explicit-control-flow | tp-ddd | PASS |
| explicit-data-flow | tp-ddd | PASS |
| explicit-side-effects | tp-ddd | PASS |
| function-file-size-limits | tp-ddd | PASS |
| functional-core-imperative-shell | tp-ddd | PASS |
| library-first-approach | tp-ddd | PASS |
| principle-of-least-astonishment | tp-ddd | PASS |
| separation-of-concerns | tp-ddd | PASS |
| policy-mechanism (ref) | tp-ddd | PASS |
| typescript-best-practices | rules | PASS (note: no frontmatter) |

---

## Checklist Compliance

| Criterion | Status |
|-----------|--------|
| 1. Valid YAML frontmatter (name, description) | PASS — all 50 skills have valid frontmatter. Exceptions: rules files (14 tp-ddd + 1 typescript) use title/paths/impact instead, which is correct for rules. |
| 2. Decision router present at top (IF/THEN) | PASS — all 50 skills have routers. 1 skill (subagent-orchestration) uses table format instead of IF/THEN (L3). 2 skills lack blank line separator (L1, L2). |
| 3. Delta principle applied | PASS overall — 6 skills exceed 500-line threshold (M9), review for potential restatement. |
| 4. No XML tags | PASS — all XML-style tags are in code block examples only, not operational. |
| 5. No threatening/unprofessional language | PASS — two instances of strong self-directed teaching language found (L4, L5), neither directed at users. |
| 6. Policy/mechanism separation | PASS — 9 skills have explicit Policy/Mechanism sections. Remaining skills implicitly separate concerns. |
| 7. No hard cross-skill file paths | **6 ISSUES (M1-M6)** — skill name references found across core and plugin files. See medium issues. |
| 8. Description specific and actionable | PASS — all descriptions provide clear routing signals. |

---

## Recommended Fix Order (Priority)

1. **M1-M6**: Replace 6 cross-skill name references with natural language (~5 min each)
2. **M7-M8**: Consider converting compositional pair references to natural language (~2 min each)
3. **L1-L2**: Add blank lines between decision router and H1 (~30 sec each)
4. **L3**: Convert table to IF/THEN pattern in subagent-orchestration (~2 min)
5. **M9**: Review 6 oversize skills for delta principle compliance (~15 min per skill)
6. **Skill name collisions**: Resolve core/tp-sdd naming overlaps (~5 min decision)

Total estimated effort: ~2-3 hours for thorough delta principle review; ~30 min for mechanical fixes.
