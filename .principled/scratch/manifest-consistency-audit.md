# Manifest Consistency Audit

## Part 1: CLAUDE.md Consistency

### 1. Plugin Management Section

**CLAUDE.md line 316:** `plugins/{tp-sadd,tp-sdd,tp-reflexion,...}/`

**Actual plugins:**
- `plugins/tp-sadd/` (exists)
- `plugins/tp-sdd/` (exists)
- `plugins/tp-fpf/` (exists)
- `plugins/tp-git/` (exists)
- `plugins/tp-tdd/` (exists)
- `plugins/tp-ddd/` (exists)
- `tp-reflexion` is NOT a separate plugin — reflexion skills live in root `skills/`

**Finding:** The ellipsis `...` implies more plugins exist. Actual count is 6. The example mentions `tp-reflexion` which does not exist as a separate plugin.

**Fix:** Update directory structure example to reflect actual 6 plugins: `plugins/{tp-sadd,tp-sdd,tp-fpf,tp-git,tp-tdd,tp-ddd}/`

### 2. Skill Count

**CLAUDE.md line 17:** "22 skills with decision routers"
**marketplace.json line 17:** "22 skills with decision routers"

**Actual root skills count:**
```
add-task, analyse, analyse-problem, code-review, code-simplify,
create-plans, create-prompts, create-skills, create-subagents,
execute-plans, execute-prompts, ideation, implement-task, kaizen,
plan-do-check-act, plan-task, reflexion, root-cause-analysis,
root-cause-tracing, subagent-orchestration, update-docs, write-concisely
```
**Count: 23 skills**

**CHANGELOG says:** "19 root skills" added in v0.3.0

**Finding:** Inconsistent counts — CLAUDE.md/marketplace say 22, actual is 23. CHANGELOG says 19 which predates later additions.

**Fix:** Update to "23 skills" in both CLAUDE.md and marketplace.json.

### 3. Explorer Subagent Protocol Scratchpad Path

**CLAUDE.md line 215:** `.principled/scratch/{topic}.md`

**Actual path:** `.principled/scratch/` exists with files:
- cek-gap-analysis-2026-05-22.md
- ddd-rules-audit-2026-05-22.md
- deep-plugins-audit.md
- fan-out-plan.md
- integration-architecture.md
- plan-artifacts-audit.md
- plugin-investigation.md
- reference-files-audit.md
- skill-benchmark-2026-05-22.md
- synergy-vocabulary-audit.md

**Finding:** Path pattern is correct.

### 4. Version Management Section

**CLAUDE.md line 11:** `**Plugin version** (`0.0.2-alpha`):`

**Actual plugin.json version:** `0.3.0`

**Finding:** Stale example version. CLAUDE.md still shows `0.0.2-alpha` as the example, which was an old alpha version.

**Fix:** Update example to `0.3.0` or remove the specific version example and use placeholder format.

### 5. Artifact Hygiene `.principled/` Path

**CLAUDE.md lines 186-198:** Directory structure listing

**Actual structure:**
```
.principled/
├── plans/
│   ├── phases/
│   │   ├── 00-scaffold/ (SUMMARY.md, 00-01-PLAN.md)
│   │   ├── 01-analysis/ (empty — no SUMMARY.md)
│   │   ├── 01-reflexion/ (SUMMARY.md, 01-01-PLAN.md)
│   │   └── 02-consolidation/ (SUMMARY.md, 02-01-PLAN.md)
│   └── .attic/
├── prompts/ (missing from actual)
├── scratch/ (exists with 10 files)
└── memory/ (exists)
```

**Finding:** Structure mostly correct but:
- `prompts/` directory does not exist under `.principled/`
- `01-analysis/` has no SUMMARY.md (only 01-01-PLAN.md)
- Phase naming inconsistency: `01-analysis` and `01-reflexion` both use "01" prefix

**Fix:** Add missing `prompts/` directory structure or remove from diagram. Verify phase numbering.

---

## Part 2: CHANGELOG.md Consistency

### 1. Version vs plugin.json

**CHANGELOG latest:** `[0.3.0] — 2026-05-22`
**plugin.json version:** `0.3.0`

**Finding:** Consistent.

### 2. Plugin count mismatch

**CHANGELOG line 9:** "8 separate plugins: Ported from context-engineering-kit — tp-reflexion (3 skills), tp-fpf (6 skills), tp-sadd (10 skills), tp-sdd (5 skills), tp-git (7 skills), tp-tdd (3 skills), tp-ddd (14 rules), tp-tech-stack (1 rule)"

**marketplace.json:** Lists only 6 plugins: tp-sadd, tp-fpf, tp-git, tp-tdd, tp-ddd, tp-sdd

**Actual plugins:** tp-sadd, tp-fpf, tp-git, tp-tdd, tp-ddd, tp-sdd (6 plugins)

**Finding:** CHANGELOG claims 8 separate plugins but only 6 exist. tp-reflexion and tp-tech-stack are not separate plugins — their content is integrated into root.

**Fix:** Correct CHANGELOG to say "6 separate plugins" and list only actual plugins.

### 3. Date consistency

**CHANGELOG:** `2026-05-22` throughout
**Session context:** `currentDate: 2026-05-22`

**Finding:** Consistent.

### 4. Phase summaries

**CHANGELOG line 13:** Phase summaries exist
**Actual files:**
- `.principled/plans/phases/00-scaffold/SUMMARY.md` — exists
- `.principled/plans/phases/01-reflexion/SUMMARY.md` — exists
- `.principled/plans/phases/02-consolidation/SUMMARY.md` — exists

**Finding:** Most phase summaries present. `01-analysis/` has no SUMMARY.md.

---

## Part 3: Marketplace Consistency

### 1. Root version vs plugin.json

**marketplace.json root version:** `0.4.0`
**plugin.json version:** `0.3.0`

**Finding:** marketplace version is root + 1 minor (0.3.0 → 0.4.0). This matches the stated versioning policy in CLAUDE.md.

### 2. Marketplace top-level version

**marketplace.json version:** `0.4.0` = root 0.3.0 + 1 minor increment

**Finding:** Correct per CLAUDE.md versioning policy.

### 3. Plugin count in marketplace

**marketplace.json plugins array:** 6 entries

**Actual plugins:** 6 (tp-sadd, tp-fpf, tp-git, tp-tdd, tp-ddd, tp-sdd)

**Finding:** Consistent.

### 4. tp-sdd in marketplace

**marketplace.json:** tp-sdd entry exists at lines 56-63

**Finding:** tp-sdd is now present. Previous audit noted it was missing — it has been added.

### 5. Plugin URLs

All plugins point to: `https://github.com/Git-Fg/taches-principled.git`

**Finding:** Consistent.

### 6. marketplace.json description accuracy

**Line 17:** "22 skills with decision routers, plus TypeScript best-practice rules"

**Actual:** 23 root skills, no separate TypeScript rules (tp-ddd has rules but they are DDD-focused, not TypeScript-specific)

**Finding:** Skill count is 23, not 22. "TypeScript best-practice rules" is inaccurate.

**Fix:** Update to "23 skills".

---

## Part 4: Plugin Manifests

### Version Consistency Across Plugins

| Plugin | marketplace.json version | plugin.json version | Consistent |
|--------|--------------------------|---------------------|------------|
| tp-sadd | 0.2.0 | 0.2.0 | Yes |
| tp-fpf | 0.2.0 | 0.2.0 | Yes |
| tp-git | 0.2.0 | 0.2.0 | Yes |
| tp-tdd | 0.2.0 | 0.2.0 | Yes |
| tp-ddd | 0.1.0 | 0.1.0 | Yes |
| tp-sdd | (not in marketplace) | 0.1.0 | No — missing from marketplace |

**Finding:** All plugin versions consistent internally. tp-sdd is missing from marketplace.json.

### Keyword Consistency

All 6 plugins use: `["taches-principled", "claude-code", ...]`

**Finding:** Correct — all use shared "taches-principled" prefix per CLAUDE.md convention.

### Description Uniqueness

All plugin descriptions are unique and plugin-specific.

---

## Summary of Inconsistencies

| # | Location | Issue | Severity | Fix |
|---|----------|-------|----------|-----|
| 1 | CLAUDE.md line 316 | Plugin directory example incomplete/wrong | Medium | Change to 6 actual plugins |
| 2 | CLAUDE.md line 17 | Skill count 22 vs actual 23 | Low | Update to 23 |
| 3 | CLAUDE.md line 11 | Stale version example (0.0.2-alpha) | Low | Update to current or remove |
| 4 | CLAUDE.md lines 186-198 | `.principled/prompts/` doesn't exist | Low | Add directory or remove from diagram |
| 5 | CLAUDE.md | Phase numbering inconsistency (01-analysis vs 01-reflexion) | Low | Clarify phase naming |
| 6 | CHANGELOG line 9 | Claims 8 plugins, only 6 exist | High | Correct to 6 plugins |
| 7 | marketplace.json line 17 | Skill count 22 vs actual 23 | Low | Update to 23 |
| 8 | marketplace.json | tp-sdd missing from plugins array | High | Add tp-sdd entry |

### High Priority Fixes

1. **CHANGELOG line 9:** "8 separate plugins" → "6 separate plugins" with corrected plugin list (tp-reflexion and tp-tech-stack are integrated, not separate)

2. **marketplace.json:** Add missing tp-sdd plugin entry (version 0.1.0)

### Low Priority Fixes

3. Update skill count from 22 to 23 in both CLAUDE.md and marketplace.json

4. Update CLAUDE.md plugin directory structure example to list actual 6 plugins

5. Remove stale version example `0.0.2-alpha` from CLAUDE.md

6. Add missing `.principled/prompts/` directory or remove from CLAUDE.md diagram

7. Verify phase naming consistency (01-analysis vs 01-reflexion both use "01" prefix)