# Convergence Review 1

**Date:** 2026-05-22
**Scope:** Cross-skill name references, XML artifacts, threatening language, frontmatter integrity
**Files examined:** 44 SKILL.md files

---

## Previously Flagged (6 Items)

### 1. `skills/subagent-orchestration/SKILL.md` — cross-ref to create-subagents
**Status: FIXED** -- No mention of "create-subagents" found anywhere in this file. References to subagent creation use natural language (e.g., "spawn a subagent").

### 2. `plugins/tp-sadd/skills/subagent-driven-development/SKILL.md` — ref to finishing-a-development-branch
**Status: FIXED** -- No match for "finishing-a-development-branch" or "finishing.*development.*branch" found. Line 95 says "Finalize the development branch" in plain English -- a step description, not a skill reference.

### 3. `plugins/tp-fpf/skills/fpf-maintenance/SKILL.md` — ref to fpf-propose
**Status: FIXED** -- No mention of "fpf-propose" found. Line 12 uses "fresh propose flow" (lowercase, natural language), line 47 says "fresh hypothesis cycle."

### 4. `plugins/tp-fpf/skills/fpf-read/SKILL.md` — ref to fpf-propose
**Status: FIXED** -- No mention of "fpf-propose" found. Lines 12-13 use "fresh hypothesis cycle" in natural language.

### 5. `plugins/tp-sdd/skills/add-task/SKILL.md` — ref to plan-task
**Status: FIXED** -- No mention of "plan-task" found. Line 11 uses "the refinement workflow" (natural language). Line 65 has template text.

### 6. `plugins/tp-sdd/skills/plan-task/SKILL.md` — ref to implement-task
**Status: FIXED** -- No mention of "implement-task" found in the plugin version (checked via grep).

**All 6 previously flagged items: CLEAN**

---

## New Issues Found

### HIGH

#### 1. Cross-plugin name reference: fpf-propose mentions "kaizen"
- **File:** `plugins/tp-fpf/skills/fpf-propose/SKILL.md:12`
- **Text:** `IF combining with kaizen root-cause analysis -> Use kaizen findings as input evidence`
- **Problem:** The tp-fpf plugin references the `kaizen` skill (root skills, different namespace) by name. The project's non-brittle cross-plugin communication rule states: "Skills must NOT reference other plugins by name. Use shared workflow vocabulary."
- **Fix:** Replace with natural language: "root cause analysis" or "why analysis" throughout the line. Example: `IF combining with root cause analysis findings -> Use root cause analysis output as input evidence`

---

### MEDIUM

#### 2. Intra-pipeline skill name: add-task names "plan-task"
- **File:** `skills/add-task/SKILL.md:11`
- **Text:** `IF combining with refinement workflow → draft will be consumed by plan-task later`
- **Problem:** References "plan-task" by name. Notably, the same line already uses "refinement workflow" as a natural language descriptor -- the reference is inconsistent.
- **Context:** This is intra-plugin (both are root `skills/`), not cross-plugin. But the project convention prefers natural language over skill names.
- **Fix:** `IF combining with refinement workflow → draft will be consumed by the refinement workflow later`

#### 3. Intra-pipeline skill name: add-task names "plan-task" (line 88)
- **File:** `skills/add-task/SKILL.md:88`
- **Text:** `Draft tasks are enriched by the plan-task workflow which adds analysis, architecture, decomposition, and verification sections before moving them to todo/.`
- **Problem:** Same as above -- uses "plan-task" as a qualifier.
- **Context:** This is in a Design Decisions section describing the development pipeline relationship.
- **Fix:** `Draft tasks are enriched by the refinement workflow which adds analysis, architecture, decomposition, and verification sections before moving them to todo/.`

#### 4. Intra-pipeline skill names: plan-task names "add-task" and "implement-task"
- **File:** `skills/plan-task/SKILL.md:603`
- **Text:** `Operates between task creation (add-task) and implementation (implement-task).`
- **Problem:** Uses "add-task" and "implement-task" as named references. Both are skill directory names.
- **Context:** Design Decisions section describing pipeline position.
- **Fix:** `Operates between task creation and implementation.`

---

### NIT

#### 5. Self-contradictory claim in create-prompts
- **File:** `skills/create-prompts/SKILL.md:484`
- **Text:** `**Self-contained:** This skill does not reference other skills by name or invocation pattern. Prompts created by this skill are executed by \`execute-prompts\`.`
- **Problem:** The first sentence claims "no reference to other skills by name," but the very next word names `execute-prompts`. While this IS an exempted compositional pair (per CLAUDE.md), the claim is factually incorrect within the same breath.
- **Suggested fix:** Either soften the claim: `**Self-contained:** This skill is self-contained except for its explicit compositional partnership with the prompt execution workflow.` Or simply remove the claim: `**Self-contained:** Prompts created by this skill are executed by \`execute-prompts\`.`

#### 6. Teaching example in create-skills references create-subagents
- **File:** `skills/create-skills/SKILL.md:463`
- **Text:** `**Good:** "create-skills" teaches skill creation only. "create-subagents" teaches subagent configuration only. Each has one job.`
- **Problem:** Uses "create-subagents" skill name in a teaching example. This is a teaching illustration, not a behavioral cross-reference, so severity is low.
- **Justification for keeping as-is:** The skill names are used as concrete examples of the single-responsibility principle being taught. Removing the names would make the example abstract and less instructive. Acceptable as-is but flagged for awareness.

---

## Cross-Scan Verification

### XML Tags
No accidental XML artifacts found. All XML-like structures are intentional:
- `launch-sub-agent/SKILL.md:92-95`: Template placeholders in sub-agent prompt (`<task>`, `<constraints>`, etc.)
- `create-prompts/SKILL.md:11-13`: Documented prompt pattern (the skill teaches creating XML-structured prompts)
- `sadd-tot/SKILL.md`: Uses XML-like tags for structured output (by design)

**Verdict: CLEAN**

### Threatening Language
No threatening or coercive language found. All "will be" instances are descriptive/predictive:
- "Will be filled in future stages" (template placeholder)
- "They will be deleted, not maintained" (code cleanup policy)
- "will be reviewed" (standard process description)

**Verdict: CLEAN**

### Frontmatter Integrity
All 44 SKILL.md files checked for leading `---` -- all present and correct. No malformed frontmatter detected.

**Verdict: CLEAN**

---

## Summary

| Category | Status |
|----------|--------|
| Previously flagged (6 items) | All 6 FIXED |
| Cross-plugin name references (new) | 1 HIGH found |
| Intra-plugin name references (new) | 3 MEDIUM found |
| XML artifact issues | 0 found -- CLEAN |
| Threatening language | 0 found -- CLEAN |
| Frontmatter integrity | All 44 verified -- CLEAN |

### Final Verdict: ISSUES_REMAIN

**4 new issues found, 1 HIGH priority:**

The HIGH issue (fpf-propose referencing "kaizen" by name cross-plugin) should be fixed before declaring convergence. The 3 MEDIUM issues (intra-pipeline name references in add-task and plan-task) are lower severity since they are intra-plugin, but fixing them would align with the project's natural-language convention. The 2 NIT items are informational.
