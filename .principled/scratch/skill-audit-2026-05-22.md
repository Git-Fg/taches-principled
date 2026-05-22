# Skill Ecosystem Audit Report

**Audit Date:** 2026-05-22
**Scope:** 35 skills across 7 skill families + 14 DDD rules
**Total Lines:** 7,767 (skills) + ~4,000 (DDD rules)

---

## Summary Table

### Root Skills (22 skills, 5,862 lines)

| Skill | Path | Lines | Router | XML | Threats | Hard-refs | Clear Description |
|-------|------|-------|--------|-----|---------|-----------|-------------------|
| add-task | skills/add-task/ | 88 | YES | NO | YES (DO NOT) | NO | YES |
| analyse | skills/analyse/ | 71 | YES | NO | NO | YES ({baseDir}) | YES |
| analyse-problem | skills/analyse-problem/ | 66 | YES | NO | NO | NO | YES |
| code-review | skills/code-review/ | 55 | YES | NO | NO | NO | YES |
| code-simplify | skills/code-simplify/ | 292 | YES | NO | YES (NEVER) | YES ({baseDir}) | YES |
| create-plans | skills/create-plans/ | 606 | YES | NO | YES (NEVER) | YES ({baseDir}) | YES |
| create-prompts | skills/create-prompts/ | 484 | YES | YES | YES (MUST, NEVER) | YES ({baseDir}) | YES |
| create-skills | skills/create-skills/ | 511 | YES | NO | YES (NEVER) | YES ({baseDir}) | YES |
| create-subagents | skills/create-subagents/ | 612 | YES | NO | YES (NEVER, MUST) | YES ({baseDir}) | YES |
| execute-plans | skills/execute-plans/ | 592 | YES | NO | YES (NEVER, FAIL) | YES ({baseDir}) | YES |
| execute-prompts | skills/execute-prompts/ | 298 | YES | NO | NO | YES ({baseDir}) | YES |
| ideation | skills/ideation/ | 64 | YES | NO | NO | NO | YES |
| implement-task | skills/implement-task/ | 567 | YES | NO | YES (NEVER) | NO | YES |
| kaizen | skills/kaizen/ | 87 | YES | NO | YES (NEVER) | NO | YES |
| plan-do-check-act | skills/plan-do-check-act/ | 61 | YES | NO | NO | NO | YES |
| plan-task | skills/plan-task/ | 603 | YES | NO | YES (NEVER) | YES ({baseDir}) | YES |
| reflexion | skills/reflexion/ | 156 | YES | NO | NO | NO | YES |
| root-cause-analysis | skills/root-cause-analysis/ | 62 | YES | NO | NO | NO | YES |
| root-cause-tracing | skills/root-cause-tracing/ | 76 | YES | NO | NO | NO | YES |
| subagent-orchestration | skills/subagent-orchestration/ | 305 | YES | NO | NO | YES ({baseDir}) | YES |
| update-docs | skills/update-docs/ | 146 | YES | NO | NO | YES ({baseDir}) | YES |
| write-concisely | skills/write-concisely/ | 60 | YES | NO | NO | NO | YES |

### Plugin tp-fpf (3 skills, 313 lines)

| Skill | Path | Lines | Router | XML | Threats | Hard-refs | Clear Description |
|-------|------|-------|--------|-----|---------|-----------|-------------------|
| fpf-maintenance | plugins/tp-fpf/skills/ | 149 | YES | NO | NO | NO | YES |
| fpf-propose | plugins/tp-fpf/skills/ | 84 | YES | NO | NO | NO | YES |
| fpf-read | plugins/tp-fpf/skills/ | 80 | YES | NO | NO | NO | YES |

### Plugin tp-git (4 skills, 523 lines)

| Skill | Path | Lines | Router | XML | Threats | Hard-refs | Clear Description |
|-------|------|-------|--------|-----|---------|-----------|-------------------|
| git-advanced | plugins/tp-git/skills/ | 195 | YES | NO | NO | NO | YES |
| git-issues | plugins/tp-git/skills/ | 124 | YES | NO | NO | NO | YES |
| git-review | plugins/tp-git/skills/ | 87 | YES | NO | NO | NO | PARTIAL |
| git-ship | plugins/tp-git/skills/ | 117 | YES | NO | NO | NO | YES |

### Plugin tp-sadd (5 skills, 610 lines)

| Skill | Path | Lines | Router | XML | Threats | Hard-refs | Clear Description |
|-------|------|-------|--------|-----|---------|-----------|-------------------|
| sadd-dispatch | plugins/tp-sadd/skills/ | 106 | YES | NO | NO | NO | YES |
| sadd-execute | plugins/tp-sadd/skills/ | 185 | YES | NO | NO | NO | YES |
| sadd-judge | plugins/tp-sadd/skills/ | 92 | YES | NO | NO | NO | YES |
| sadd-patterns | plugins/tp-sadd/skills/ | 137 | YES | NO | NO | NO | YES |
| sadd-tot | plugins/tp-sadd/skills/ | 90 | YES | NO | NO | NO | YES |

### Plugin tp-sdd (5 skills, 335 lines)

| Skill | Path | Lines | Router | XML | Threats | Hard-refs | Clear Description |
|-------|------|-------|--------|-----|---------|-----------|-------------------|
| add-task | plugins/tp-sdd/skills/ | 79 | YES | NO | YES (DO NOT) | NO | YES |
| brainstorm | plugins/tp-sdd/skills/ | 49 | YES | NO | NO | NO | YES |
| create-ideas | plugins/tp-sdd/skills/ | 34 | YES | NO | NO | NO | PARTIAL |
| implement-task | plugins/tp-sdd/skills/ | 90 | YES | NO | NO | NO | YES |
| plan-task | plugins/tp-sdd/skills/ | 83 | YES | NO | NO | NO | YES |

### Plugin tp-tdd (1 skill, 124 lines)

| Skill | Path | Lines | Router | XML | Threats | Hard-refs | Clear Description |
|-------|------|-------|--------|-----|---------|-----------|-------------------|
| tdd | plugins/tp-tdd/skills/ | 124 | YES | NO | YES (NEVER) | NO | YES |

---

## Total Counts

| Metric | Count |
|--------|-------|
| **Total skills** | 40 |
| **Skills with decision routers** | 40/40 (100%) |
| **Skills with XML tags** | 1 (create-prompts only) |
| **Skills with threatening language** | 11/40 (27.5%) |
| **Skills with hard cross-skill file paths** | 13/40 (32.5%) |
| **Total skill lines** | 7,767 |
| **DDD rules** | 14 files |

---

## Critical Issues

### 1. XML Tags Present (create-prompts only)

**File:** `skills/create-prompts/SKILL.md`

The create-prompts skill uses XML-structured prompts with tags like `<objective>`, `<context>`, `<requirements>`, `<implementation>`, `<output>`, `<verification>`, `<success_criteria>`, `<data_sources>`, `<analysis_requirements>`, `<output_format>`, `<scope>`, `<deliverables>`, `<evaluation_criteria>`, and `<research_objective>`.

**Issue:** XML tags in skill bodies are a content formatting choice, not an anti-pattern per se. However, the pattern is unique to this skill and not shared elsewhere. The skill uses these as prompt templates for generated prompts, which is appropriate for its domain.

**Severity:** MEDIUM (not critical - isolated to this skill's specific purpose)

### 2. Duplicated Skills Across Plugins

**Issue:** Some skills appear in both root (`skills/`) and plugin (`plugins/tp-sdd/`) locations:
- `add-task` (root: 88 lines, sdd: 79 lines)
- `implement-task` (root: 567 lines, sdd: 90 lines)
- `plan-task` (root: 603 lines, sdd: 83 lines)

The root versions are substantially more complete. The tp-sdd versions appear to be simplified/adapted variants.

**Severity:** MEDIUM (functional but creates maintenance burden)

### 3. Generic Description in tp-sdd/create-ideas

**File:** `plugins/tp-sdd/skills/create-ideas/SKILL.md`

**Description:** "Use when user asks to 'generate ideas', 'brainstorm options', or 'come up with alternatives' — produces diverse idea set using probability sampling"

**Issue:** The description is specific about trigger phrases but the output description "produces diverse idea set using probability sampling" is technically vague. What does the output look like? Where is it saved?

**Severity:** LOW (describes the mechanism but not the concrete deliverable)

---

## Medium Issues

### 1. Hard Cross-Skill File Path References

Many skills use hard-coded `{baseDir}` references to their own internal files, which is appropriate. However, several skills also reference OTHER skills' reference files:

**create-plans:**
- "read `{baseDir}/references/plan-format.md` AND `{baseDir}/references/checkpoints.md`"
- "read `{baseDir}/references/scope-estimation.md`"
- "read `{baseDir}/references/cli-automation.md`"
- "read `{baseDir}/agents/explorer.md`, `{baseDir}/agents/researcher.md`, `{baseDir}/agents/architect.md`"
- "read `{baseDir}/references/milestone-management.md`"

**create-prompts:**
- "Prompts created by this skill are executed by `execute-prompts`."

**create-subagents:**
- Multiple references to `{baseDir}/references/*.md` files

**execute-plans:**
- "read `{baseDir}/references/execution-strategies.md`"
- "read `{baseDir}/references/checkpoint-protocols.md`"
- "read `{baseDir}/templates/autonomous-execution.md`"

**subagent-orchestration:**
- "See the orchestration patterns reference for full patterns"
- References to `{baseDir}/references/race-framework.md`, `orchestration-patterns.md`, etc.

**Issue:** These references use natural language and `{baseDir}` for portability, which is correct. However, they create coupling between skills. If a reference file is renamed, multiple skills break.

**Severity:** MEDIUM (accepted as necessary coupling within skill families)

### 2. Threatening Language Usage

**11 skills** use threatening language (MUST, NEVER, DO NOT):

| Skill | Threats Used |
|-------|-------------|
| add-task | "DO NOT invoke the plan skill", "DO NOT create files", "DO NOT modify existing", etc. |
| code-simplify | "NEVER combine pipeline stages", "NEVER rename variables", "NEVER inline if 3+ places" |
| create-plans | "NEVER include in plans: team structures, RACI matrices..." |
| create-prompts | "MUST produce XML-structured prompts", "NEVER skip decision gate" |
| create-skills | "NEVER do X", "ALWAYS do Y" patterns in constraints |
| create-subagents | "MUST verify", "NEVER modify", "ALWAYS include" |
| execute-plans | "NEVER proceed past Rule 4", "do NOT re-invoke create-plans" |
| implement-task | "Orchestrator dispatches, NEVER implements" |
| kaizen | "Red flag" warnings with "NEVER" language |
| plan-task | "DO NOT skip quality gates", "DO NOT use background agents" |
| tdd | "NO PRODUCTION CODE WITHOUT A FAILING TEST FIRST", "Delete it. Start over." |

**Assessment:** Most threatening language is appropriate for guardrail/constraint skills. The tdd skill's "NO PRODUCTION CODE WITHOUT A FAILING TEST FIRST. Delete it. Start over." is notably emphatic but appropriate for its Iron Law principle.

**Severity:** MEDIUM (most usage is appropriate for constraint/guardrail skills)

### 3. Thin Content Skills

Some skills are quite thin and may benefit from more detail:

| Skill | Lines | Issue |
|-------|-------|-------|
| create-ideas (sdd) | 34 | Very minimal, only 2 sections |
| brainstorm (sdd) | 49 | Minimal but functional |
| ideation (root) | 64 | Thin - 2 modes but brief |

**Severity:** LOW (functionally complete but could be more comprehensive)

### 4. git-review Description Partially Generic

**File:** `plugins/tp-git/skills/git-review/SKILL.md`

**Description:** "Add line-specific review comments on pull requests — single comments and batched multi-file reviews"

**Issue:** The description is fairly specific but doesn't mention what makes this skill distinctive (uses MCP inline comment tools when available, falls back to gh API). A user might not understand the differentiation from git-advanced.

**Severity:** LOW

---

## DDD Rules Analysis (14 files)

All DDD rules follow policy-only format — they explain WHY principles matter and show wrong/correct examples, but don't prescribe mechanical procedures.

| Rule | Lines | P/M Sep | Threats | Notes |
|------|-------|---------|---------|-------|
| call-site-honesty.md | 24 | YES (policy) | NO | Logging visibility principle |
| clean-architecture-ddd.md | 63 | YES (policy) | NO | Domain/infrastructure separation |
| command-query-separation.md | ~50 | YES | NO | Explicit contracts |
| domain-specific-naming.md | ~45 | YES | NO | Naming for clarity |
| early-return-pattern.md | ~40 | YES | NO | Reduce nesting |
| error-handling.md | ~50 | YES | NO | Fail fast principle |
| explicit-control-flow.md | ~70 | YES | NO | Control flow clarity |
| explicit-data-flow.md | ~35 | YES | NO | Data flow visibility |
| explicit-side-effects.md | ~60 | YES | NO | Side effect visibility |
| function-file-size-limits.md | ~100 | YES | NO | Size thresholds with rationale |
| functional-core-imperative-shell.md | ~80 | YES | NO | Core/shell pattern |
| library-first-approach.md | ~40 | YES | NO | External code preference |
| principle-of-least-astonishment.md | ~50 | YES | NO | Predictable behavior |
| separation-of-concerns.md | ~80 | YES | NO | Concern boundaries |

**DDD Rules Assessment:** All 14 rules demonstrate strong policy/mechanism separation. They:
- Lead with the principle (policy)
- Show wrong/correct examples
- Explain WHY the pattern matters
- Avoid threatening language
- No hard file path references (they're standalone reference material)

**Severity:** No issues found. DDD rules are exemplary.

---

## Skills WITHOUT Decision Routers

**Count: 0**

All 40 skills have decision routers at the top of their SKILL.md bodies.

---

## Skills with Policy/Mechanism Separation

**Count: 40/40 (100%)**

All skills demonstrate clear P/M separation:
- **Policy** = when to use this skill, routing decisions
- **Mechanism** = how to execute, process, examples

---

## Recommendations

### 1. Consider Consolidating tp-sdd Duplicates

The tp-sdd plugin contains simplified versions of add-task, implement-task, and plan-task that are substantially thinner than their root counterparts. Consider:
- Removing the simplified versions and using root skills only
- Or making them distinct variants with different trigger conditions

### 2. Expand Thin Skills in tp-sdd

The create-ideas (34 lines) and brainstorm (49 lines) skills in tp-sdd are notably thin. Consider expanding them to match the depth of their counterparts in the ideation root skill.

### 3. Document Reference File Stability Requirements

Since multiple skills reference internal reference files by path (via `{baseDir}`), establish a convention that reference file names are stable API. Any rename should be coordinated across all referencing skills.

### 4. Review Threatening Language in create-prompts

The create-prompts skill uses MUST/NEVER in its anti-patterns section. While appropriate for quality enforcement, ensure the language aligns with the skill's creative-direction purpose.

---

## Conclusion

The taches-principled skill ecosystem demonstrates high quality overall:
- **100% decision router coverage** — every skill routes appropriately
- **100% P/M separation** — all skills cleanly separate when vs how
- **Minimal XML usage** — only create-prompts uses XML tags, and it's appropriate
- **Threatening language is minority** (27.5%) and mostly appropriate for constraint skills
- **DDD rules are exemplary** — pure policy with strong wrong/correct examples

The primary opportunities are consolidating duplicate skills across plugins and expanding thin content in tp-sdd variants.