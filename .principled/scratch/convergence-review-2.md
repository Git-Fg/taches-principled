# Convergence Review 2 — Structural Audit

**Reviewer:** Convergence reviewer
**Date:** 2026-05-22
**Scope:** Verify all HIGH and MEDIUM fixes from previous audit, plus fresh structural scan.

---

## HIGH Priority Checks (Previously 3 Issues — Marked FIXED)

### H1 — `plugins/tp-sdd/.claude-plugin/plugin.json` version 0.2.0
- **Status:** FIXED
- **Evidence:** Line 4: `"version": "0.2.0"` (was 0.1.0)
- **Detail:** Minor bump from 0.1.0 to 0.2.0. Correct.

### H2 — CLAUDE.md plugin list (previously line ~314, now 309) — no `tp-reflexion`
- **Status:** FIXED
- **Evidence:** Line 309: `plugins/{tp-sadd,tp-sdd,tp-fpf,tp-git,tp-tdd,tp-ddd}/`
- **Detail:** tp-reflexion removed from plugin directory enumeration. List contains exactly the 6 plugin directories that exist on disk.

### H3 — CLAUDE.md naming convention (previously line ~323, now 317) — no `tp-reflexion`
- **Status:** FIXED
- **Evidence:** Line 317: `` `tp-sadd`, `tp-sdd`, `tp-fpf`, `tp-git`, `tp-tdd`, `tp-ddd` ``
- **Detail:** Naming convention examples no longer include `tp-reflexion`.

### H4 — CLAUDE.md Plugin Isolation (previously line ~329, now ~327-333) — no `plugins/tp-reflexion/skills/SKILL_TEMPLATE.md`
- **Status:** FIXED
- **Evidence:** Lines 327-333 contain the Plugin Isolation Principle section. No file path references to tp-reflexion or SKILL_TEMPLATE.md exist in the current CLAUDE.md.

---

## MEDIUM Priority Checks (Previously 4 Issues — Marked FIXED)

### M5 — README.md: version 0.3.0, 22 skills, 6 separate plugins
- **Status:** FIXED
- **Evidence:**
  - Line 3: `"Version: 0.3.0"` — matches plugin.json
  - Line 39: `"22 Skills"` — confirmed by `ls skills/` = exactly 22 directories
  - Lines 93-103: 6 plugins listed (tp-sadd, tp-sdd, tp-fpf, tp-git, tp-tdd, tp-ddd) — matches `plugins/` directory count
- **Detail:** All three claims in README are consistent with on-disk reality.

### M6 — CLAUDE.md stale `0.0.2-alpha` replaced with `0.3.0`
- **Status:** FIXED
- **Evidence:** CLAUDE.md line 11: ``Plugin version (`0.3.0`)``. No instance of `0.0.2-alpha` exists in CLAUDE.md.
- **Detail:** The `0.0.2-alpha` references that remain are confined to:
  - `CHANGELOG.md` lines 95, 101 (historical entries — correct and expected)
  - `.principled/scratch/*.md` (audit trail artifacts — expected content)
  These are appropriate historical records, not stale live references.

### M7 — CLAUDE.md `.principled/` diagram — no `.attic/` or `prompts/` subtrees
- **Status:** FIXED
- **Evidence:** Lines 186-192 show the `.principled/` tree with only three subdirectories: `plans/`, `scratch/`, `memory/`. Neither `.attic/` nor `prompts/` appear in the diagram.
- **Note:** Line 194 mentions `.attic/` in prose (archiving policy: "Skills define when to move content to `.attic/`"). This is a workflow description, not a structural claim — acceptable.

### M8 — `skills/create-prompts/references/` directory removed
- **Status:** FIXED
- **Evidence:** `ls` confirms directory does not exist. No stale reference-files remain for create-prompts.

### M9 — CHANGELOG.md: "8 separate plugins" → "6 separate plugins"? "19 root skills" → "22 root skills"?
- **Status:** PARTIALLY FIXED — count corrected on line 9, but line 17 still wrong
- **Evidence (correct):**
  - Line 8: `"22 root skills"` — confirmed by on-disk count
  - Line 9: `"6 separate plugins"` — matches marketplace.json (1 root + 6 separate = 7 total entries)
- **Evidence (STILL BROKEN):**
  - Line 17: `"marketplace.json: Bumped to 0.4.0, 9 entries (root + 8 separate plugins)"`
  - Actual marketplace.json has **7 entries** (1 root + 6 separate). Claim of "9 entries" and "8 separate" is wrong.
  - Also: the parenthetical on line 9 lists 8 items (tp-reflexion, tp-fpf, tp-sadd, tp-sdd, tp-git, tp-tdd, tp-ddd, tp-tech-stack) after claiming "6 separate plugins". This is internally inconsistent — 2 of the 8 listed items (tp-reflexion, tp-tech-stack) are not separate plugins.

### M10 — CHANGELOG.md: tp-sadd count updated?
- **Status:** STILL_BROKEN
- **Evidence:** CHANGELOG line 9 says `"tp-sadd (15 skills)"`. Actual count from `find SKILL.md` in `plugins/tp-sadd/skills/` = **9 skills**.
- **Detail:** Discrepancy of 6 skills. This was presumably accurate at the time of the 0.3.0 port from context-engineering-kit, but either the count was inflated at that time or skills were consolidated since. Regardless, the published CHANGELOG entry is now misleading.
- **Note:** Other skill counts on line 9 are also wrong:
  - `tp-fpf (6 skills)` → actual: **3 skills**
  - `tp-git (7 skills)` → actual: **4 skills**
  - `tp-tdd (3 skills)` → actual: **1 skill**
  - Only `tp-sdd (5 skills)` and `tp-ddd (14 rules)` match current state.

---

## New Scan Items

### N1 — `.claude-plugin/marketplace.json`: tp-sdd at 0.2.0?
- **Status:** CORRECT
- **Evidence:** Line 48-49: `"name": "tp-sdd", "version": "0.2.0"` — matches the plugin.json for tp-sdd.

### N2 — Actual root skills count vs declared
- **Status:** CONSISTENT
- **Evidence:** `ls skills/` = 22 directories. README line 39 claims "22 Skills". Match.
- **Breakdown of 22 root skills:**
  add-task, analyse, analyse-problem, code-review, code-simplify, create-plans, create-prompts, create-skills, create-subagents, execute-plans, execute-prompts, ideation, implement-task, kaizen, plan-do-check-act, plan-task, reflexion, root-cause-analysis, root-cause-tracing, subagent-orchestration, update-docs, write-concisely.

### N3 — tp-sdd skills directory structure after duplicate removal
- **Status:** CLEAN
- **Evidence:** `plugins/tp-sdd/skills/` contains 5 skill directories: add-task, brainstorm, create-ideas, implement-task, plan-task. No duplicates. Matches the 5 skills declared in README. Matches the 5 skills declared in marketplace description.

---

## Summary of Findings

| ID | Item | Status |
|----|------|--------|
| H1 | tp-sdd plugin.json version 0.2.0 | FIXED |
| H2 | CLAUDE.md plugin list — no tp-reflexion | FIXED |
| H3 | CLAUDE.md naming convention — no tp-reflexion | FIXED |
| H4 | CLAUDE.md plugin isolation — no broken path reference | FIXED |
| M5 | README.md version/counts/plugins | FIXED |
| M6 | CLAUDE.md stale 0.0.2-alpha | FIXED |
| M7 | CLAUDE.md .principled/ diagram | FIXED |
| M8 | create-prompts/references/ removed | FIXED |
| M9 | CHANGELOG.md 8→6 plugins, 19→22 skills | PARTIALLY FIXED |
| M10 | CHANGELOG.md tp-sadd count | STILL_BROKEN |
| N1 | marketplace.json tp-sdd at 0.2.0 | CORRECT |
| N2 | Root skills count (22) | CONSISTENT |
| N3 | tp-sdd skills structure | CLEAN |

### Remaining Issues

1. **CHANGELOG.md line 17 (MEDIUM):** Claims "9 entries (root + 8 separate plugins)" for marketplace.json v0.4.0. Actual count is 7 entries (root + 6 separate). Off by 2 — likely from counting tp-reflexion and tp-tech-stack as separate plugins when they were integrated into root.

2. **CHANGELOG.md line 9 (MEDIUM):** Lists 8 items in parenthetical after claiming "6 separate plugins" — tp-reflexion and tp-tech-stack are not separate plugins. Also, skill counts for tp-sadd (15), tp-fpf (6), tp-git (7), tp-tdd (3) don't match current on-disk state (9, 3, 4, 1 respectively). These are either historically inaccurate or stale since the 0.3.0 release.

3. **`.principled/scratch/` artifacts (LOW):** Multiple scratch files (manifest-consistency-audit.md, final-review-2-structure.md, plan-artifacts-audit.md) document the same issues that are now fixed. These are audit trail artifacts and not structural defects, but they will become increasingly misleading over time.

### Verdict

**STRUCTURALLY CLEAN — 2 minor inconsistencies in CHANGELOG.md**

All 4 HIGH issues are fully resolved. The 4 MEDIUM issues have 3 fully resolved and 2 partially resolved (line 9 count inconsistency, line 17 marketplace count). The remaining defects are confined to CHANGELOG.md historical entries and do not affect functionality, routing, or user experience.

The two actionable fixes needed:
1. CHANGELOG.md line 17: Change "9 entries (root + 8 separate plugins)" to "7 entries (root + 6 separate plugins)"
2. CHANGELOG.md line 9: Either update the parenthetical counts to match current state, or clarify that these were the counts at time of port (version 0.3.0) from context-engineering-kit
