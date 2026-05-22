# Final Review 2: Structural Integrity Audit

**Audited:** 2026-05-22
**Scope:** Full taches-principled ecosystem — manifest, version, directory, cross-reference, and CLAUDE.md integrity

---

## 1. Manifest Verification

### 1.1 Root plugin.json
- **Path:** `/Users/felix/Documents/AutoPluginClaw/taches-principled/.claude-plugin/plugin.json`
- **name:** `taches-principled` -- OK
- **version:** `0.3.0` -- OK
- **description:** Present and accurate -- OK
- **No issues.**

### 1.2 marketplace.json
- **Path:** `/Users/felix/Documents/AutoPluginClaw/taches-principled/.claude-plugin/marketplace.json`
- **Root version:** `0.4.0` -- OK
- **Plugins listed:** 7 entries (root + 6 sub-plugins) -- OK
  - taches-principled v0.3.0, tp-sadd v0.2.0, tp-fpf v0.2.0, tp-git v0.2.0, tp-sdd v0.2.0, tp-tdd v0.2.0, tp-ddd v0.1.0

### 1.3 Sub-plugin plugin.json files

| Plugin | File | name | version | matches marketplace? |
|--------|------|------|---------|---------------------|
| tp-sadd | `plugins/tp-sadd/.claude-plugin/plugin.json` | `tp-sadd` | 0.2.0 | YES |
| tp-fpf | `plugins/tp-fpf/.claude-plugin/plugin.json` | `tp-fpf` | 0.2.0 | YES |
| tp-git | `plugins/tp-git/.claude-plugin/plugin.json` | `tp-git` | 0.2.0 | YES |
| **tp-sdd** | **`plugins/tp-sdd/.claude-plugin/plugin.json`** | **`tp-sdd`** | **0.1.0** | **NO (marketplace says 0.2.0)** |
| tp-tdd | `plugins/tp-tdd/.claude-plugin/plugin.json` | `tp-tdd` | 0.2.0 | YES |
| tp-ddd | `plugins/tp-ddd/.claude-plugin/plugin.json` | `tp-ddd` | 0.1.0 | YES |

**ISSUE 1 (HIGH):** tp-sdd plugin.json version (0.1.0) does not match marketplace entry (0.2.0).

---

## 2. Version Consistency

| Check | Expected | Actual | Verdict |
|-------|----------|--------|---------|
| CHANGELOG latest version = plugin.json version | 0.3.0 | Both 0.3.0 | OK |
| marketplace top-level = root plugin + 1 minor | 0.4.0 | 0.4.0 (= 0.3.0 + 0.1) | OK |
| All plugin versions match marketplace | See Section 1.3 | tp-sdd mismatch | **ISSUE 1** |

---

## 3. Directory Structure Integrity

### 3.1 Plugin existence vs claims

**Plugins that exist on disk (6):**
- tp-ddd (rules only), tp-fpf, tp-git, tp-sadd (skills + references), tp-sdd (skills + references), tp-tdd

**Plugins claimed in CHANGELOG/CLAUDE.md but DO NOT EXIST:**
- tp-reflexion -- skills merged into root `skills/reflexion`
- tp-tech-stack -- never created as separate plugin
- tp-kaizen -- skills merged into root
- tp-review -- skills merged into root
- tp-docs -- skills merged into root

No .gitkeep files found anywhere -- means no intentionally empty directories are being tracked.

### 3.2 Empty directories (3 found)
- `.claude/agent-memory/code-reviewer` -- expected (agent memory populated at runtime, acceptable)
- `.principled/plans/phases/01-analysis` -- completely empty, no files at all
- `skills/create-prompts/references` -- empty directory

### 3.3 SKILL.md distribution

| Location | Count |
|----------|-------|
| Root skills/ | 22 |
| tp-sadd plugin | 9 |
| tp-fpf plugin | 3 |
| tp-git plugin | 4 |
| tp-sdd plugin | 5 |
| tp-tdd plugin | 1 |
| tp-ddd plugin | 0 (rules only) |
| **Total** | **44** |

**ISSUE 2 (MEDIUM):** tp-sadd has 9 skills, not the 10 claimed in CHANGELOG. Missing skill: `do-in-parallel` was claimed but not present as a directory.

**ISSUE 3 (LOW):** Empty directory `skills/create-prompts/references` -- appears to be a placeholder that was never populated.

---

## 4. Cross-Reference Integrity

### 4.1 Hard-coded paths in SKILL.md files
- **Zero** hard-coded `plugins/` paths found in any SKILL.md body -- GOOD
- **Zero** absolute `/Users/felix/` paths found in any SKILL.md body -- GOOD
- `{baseDir}` correctly used in 5 SKILL.md files (create-skills, create-subagents, create-plans, execute-plans, execute-prompts) -- GOOD
- Minor: `create-plans/SKILL.md` line 567 references `~/.claude/skills/expertise/` as historical context about the original skill design. This is acceptable as background/intent documentation but technically violates the no-hard-path principle if interpreted strictly.

### 4.2 SKILL_TEMPLATE.md -- MISSING
Referenced at **CLAUDE.md line 329** (`plugins/tp-reflexion/skills/SKILL_TEMPLATE.md`) and in multiple phase plans. **File does not exist anywhere in the project.** It was planned to be moved to root `references/` per Phase 2 consolidation plan but this was never executed.

**ISSUE 4 (HIGH):** SKILL_TEMPLATE.md does not exist at the referenced path or anywhere else.

### 4.3 Stale tp-reflexion references in LIVE files
**CLAUDE.md** (source-of-truth file, NOT historical artifact):
- **Line 314:** `plugins/{tp-sadd,tp-sdd,tp-reflexion,...}/` -- `tp-reflexion` is not a separate plugin directory
- **Line 323:** `All imported/ported plugins use the \`tp-\` prefix: \`tp-reflexion\`, \`tp-sadd\`, \`tp-sdd\`, etc.` -- tp-reflexion is not a plugin
- **Line 329:** `plugins/tp-reflexion/skills/SKILL_TEMPLATE.md` -- neither the directory nor file exists

**CHANGELOG.md line 9:** Claims 8 separate plugins including tp-reflexion and tp-tech-stack -- both are integrated into root, not separate.

**ISSUE 5 (HIGH):** CLAUDE.md has 3 stale tp-reflexion references. CHANGELOG entry 0.3.0 claims 8 separate plugins but only 6 exist.

---

## 5. CLAUDE.md Accuracy

### 5.1 Skill count
Line 316 marketplace description: "22 skills with decision routers" -- refers to the root plugin, which has 22 skills. Correct in context. However, total ecosystem is 44 skills (22 root + 22 plugin).

### 5.2 Stale version example
**CLAUDE.md line 12:** `**Plugin version** (\`0.0.2-alpha\`): Incremented for any content change...` -- Current plugin version is **0.3.0**. The `0.0.2-alpha` example is from over 4 versions ago.

**ISSUE 6 (MEDIUM):** Version management section shows `0.0.2-alpha` as example instead of current version pattern like `0.3.0`.

### 5.3 Stale plugin naming references
- Line 323: tp-reflexion listed as prefix example -- doesn't exist as plugin
- Line 318: Structure diagram shows `agents/` and `rules/` under each plugin -- only tp-ddd has rules/; most plugins have neither agents/ nor rules/

**ISSUE 7 (LOW):** Plugin structure diagram in CLAUDE.md is aspirational rather than accurate.

### 5.4 .principled/ directory structure diagram
**CLAUDE.md lines 186-198** shows:
```
.principled/
├── plans/
│   ├── phases/
│   └── .attic/
├── prompts/
│   ├── analyses/
│   ├── research/
│   ├── completed/
│   └── .attic/
├── scratch/
└── memory/
```

**Actual:**
```
.principled/
├── memory/
├── plans/
│   ├── phases/
│   ├── BRIEF.md
│   ├── ROADMAP.md
│   └── inline-agents-plan.md
└── scratch/
```

Missing entirely: `plans/.attic/`, entire `prompts/` subtree (analyses/, research/, completed/, .attic/)

**ISSUE 8 (MEDIUM):** CLAUDE.md directory structure diagram is inaccurate -- missing `plans/.attic/` and entire `prompts/` tree. Actual has only `memory/`, `plans/`, and `scratch/`.

### 5.5 README.md is severely outdated
- **Version says 0.2.0** -- current is 0.3.0
- **Claims "8 Skills"** -- root has 22
- **Only lists the original 8 skills** -- missing: add-task, analyse, analyse-problem, code-review, ideation, implement-task, kaizen, plan-do-check-act, plan-task, reflexion, root-cause-analysis, root-cause-tracing, update-docs, write-concisely (14 missing skills)

**ISSUE 9 (MEDIUM):** README.md is drastically out of date -- version, skill count, and skill table all need updating.

### 5.6 CHANGELOG skill count inaccuracies

| Plugin | CHANGELOG Claim | Actual | Match? |
|--------|----------------|--------|--------|
| Root skills | 19 | 22 | **NO** |
| tp-sadd | 10 skills | 9 | **NO** |
| tp-fpf | 6 skills | 3 | **NO** |
| tp-git | 7 skills | 4 | **NO** |
| tp-tdd | 3 skills | 1 | **NO** |
| tp-sdd | 5 skills | 5 | YES |
| tp-ddd | 14 rules | 14 | YES |
| tp-reflexion | Separate plugin | Integrated into root | **NO** |
| tp-tech-stack | Separate plugin | Never created | **NO** |

**ISSUE 10 (LOW):** CHANGELOG 0.3.0 entry contains stale skill counts that do not reflect current reality. The CHANGELOG describes initial porting intent, not final state.

---

## Summary: Issues by Severity

### HIGH (blocks commit)
1. **tp-sdd version mismatch**: plugin.json says 0.1.0, marketplace says 0.2.0
4. **SKILL_TEMPLATE.md missing**: Referenced in CLAUDE.md line 329 but file does not exist anywhere
5. **3 stale tp-reflexion references in CLAUDE.md**: Lines 314, 323, 329 reference a plugin that doesn't exist as a separate entity

### MEDIUM (should fix before commit)
2. **tp-sadd skill count discrepancy**: 9 skills on disk vs 10 claimed in CHANGELOG
6. **Stale version example in CLAUDE.md**: `0.0.2-alpha` example at line 12
8. **Inaccurate .principled/ diagram in CLAUDE.md**: Missing `plans/.attic/` and entire `prompts/` subtree
9. **Outdated README.md**: Version says 0.2.0, skill count says 8 (should be 22), missing 14 skills

### LOW (document for follow-up)
3. **Empty `skills/create-prompts/references/` directory**
7. **Plugin structure diagram in CLAUDE.md line 318 is aspirational** (agents/ and rules/ listed for all plugins)
10. **CHANGELOG 0.3.0 has stale skill counts** (describes initial port intent, not final state)

---

## Remaining Issues from Previous Audit (manifest-consistency-audit.md)

| Previous Finding | Status |
|-----------------|--------|
| CLAUDE.md tp-reflexion references | **NOT FIXED** -- still present at lines 314, 323, 329 |
| CHANGELOG "8 separate plugins" | **NOT FIXED** -- line 9 still claims 8 |
| tp-sdd version mismatch | **NOT FIXED** -- 0.1.0 vs 0.2.0 |
| README severe staleness | **NOT FIXED** -- version, skill count, skill table |
| .principled/ diagram vs reality | **NOT FIXED** -- prompts/ and .attic/ missing |
| Marketplace entries missing: tp-kaizen, tp-review, tp-docs | Resolved by design (integrated into root) |

**Note:** Several issues flagged in the previous manifest-consistency-audit.md remain open. These were identified as "must fix before commit" items that have not been addressed.

---

## Zero-Issue Verification

- plugin.json root: OK
- marketplace.json root version: OK
- tp-sadd plugin.json: OK
- tp-fpf plugin.json: OK
- tp-git plugin.json: OK
- tp-tdd plugin.json: OK
- tp-ddd plugin.json (+ 14 rules): OK
- All 44 SKILL.md files present where expected: OK
- No absolute path references in SKILL.md files: OK
- No hard-coded `plugins/` references in SKILL.md files: OK
- {baseDir} correctly used in 5 root skills: OK
- No stale tp-kaizen/tp-review/tp-docs references in live files: OK
- commands/ directory (3 commands): OK
- agents/ directory (7 agents): OK
- Root rules/typescript-best-practices.md: OK
- tp-ddd has 14 rules files as claimed: OK
