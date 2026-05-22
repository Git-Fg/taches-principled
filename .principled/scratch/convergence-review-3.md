# Convergence Review 3 — Semantic Integrity Audit

Date: 2026-05-22
Scope: All skills in `taches-principled/` (base + plugins) plus CLAUDE.md

---

## Task 1: Duplicate Names (user-confirmed: keep tp-sdd)

### Result: EXISTS + VALID — known duplicate pending cleanup

All 3 tp-sdd plugin files exist with valid frontmatter:

| File | name | description | status |
|------|------|-------------|--------|
| `plugins/tp-sdd/skills/plan-task/SKILL.md` | `plan-task` | "Refine draft task specification..." | VALID |
| `plugins/tp-sdd/skills/implement-task/SKILL.md` | `implement-task` | "Execute task implementation steps..." | VALID |
| `plugins/tp-sdd/skills/add-task/SKILL.md` | `add-task` | "Create a draft task file..." | VALID |

**Note:** Base versions (`skills/plan-task/SKILL.md`, `skills/implement-task/SKILL.md`, `skills/add-task/SKILL.md`) have identical `name` and `description` fields. If both are installed simultaneously, Claude would see two skills with identical names and descriptions — creating routing ambiguity. This is the known duplicate flagged in previous review, user confirmed base versions will be removed.

---

## Task 2: Non-Brittle Communication (tp- prefix scan)

### Result: CLEAN — zero tp- prefix references in skill files

Scanned:
- `plugins/*/skills/` — ZERO occurrences
- `skills/` — ZERO occurrences
- `agents/` — ZERO occurrences
- `commands/` — ZERO occurrences
- `**/references/*.md` — ZERO occurrences

**However — known by-design cross-skill name references exist:**
- `skills/create-plans/SKILL.md:20` — names `execute-plans` (intentional compositional pair, documented in CLAUDE.md)
- `skills/create-prompts/SKILL.md:484` — names `execute-prompts` (intentional compositional pair, documented in CLAUDE.md)

These are documented exceptions, not new findings. They are not tp- prefix references.

---

## Task 3: Synergy Vocabulary

### Result: GAP REMAINS — 2 of 8 shared concepts completely unused in skills

The `integration-architecture.md` defines 8 shared vocabulary concepts for cross-plugin communication:

| Concept | In Skill Files? | Details |
|---------|----------------|---------|
| **implementation artifact** | ZERO occurrences | Defined but never used in any skill |
| **judgment criteria** | ZERO occurrences | Defined but never used in any skill |
| **reflection output** | 1 occurrence | `tp-fpf/fpf-propose`: "Use reflection findings to validate hypotheses" |
| **decision record** | 2 occurrences | `tp-fpf/fpf-read`: mentions in description and checklist; `reflexion`: mentions as external input |
| **improvement cycle** | 3 occurrences | `reflexion`: defines the reflect→critique→memorize loop; `analyse`: mentions "improvement cycles" |
| **specification** | Used generically | Appears in many skills but as general term ("task specification", "YAML specification"), not as shared vocabulary |
| **action plan** | Used generically | Appears in create-plans context but not as a shared concept reference |
| **test coverage** | Used generically | Appears in tdd and code-review skills but not as shared vocabulary |

**Critical finding:** This gap was ALREADY IDENTIFIED in the previous convergence review:
- `.principled/scratch/final-review-3-semantic.md` flags both "implementation artifact — VOCABULARY GAP" (line 48) and "judgment criteria — VOCABULARY GAP" (line 59)
- `.principled/scratch/master-audit-synthesis.md` lists "Finding: synergy map defines 'implementation artifact' as shared vocabulary, but not all skills explicitly reference it" (line 119)
- The success criteria in master-audit-synthesis.md requires "All skills that produce/consume shared concepts explicitly use the vocabulary" (line 221)

**These findings were never actioned.** The vocabulary gaps remain unfixed since at least the previous review cycle.

---

## Task 4: Terminology Consistency

### Result: MINOR DRIFT — "verification agent" used inconsistently in one location

#### "judge" vs "review agent" vs "verification agent"

| Term | Count | Where Used |
|------|-------|------------|
| **judge** | ~184 | sadd, sdd, plan-task, implement-task, fpf, reflexion, kaizen, execute-plans |
| **review agent(s)** | 4 | `code-review/SKILL.md`, `update-docs/SKILL.md` (domain-appropriate) |
| **verification agent** | 2 | `tp-tdd/tdd/SKILL.md`, `execute-plans/references/meta-judge.md` |

**Drift finding:** `skills/execute-plans/references/meta-judge.md` line 37 uses "verification agent" — the only reference file to do so. The same reference document uses "judge" and "meta-judge" throughout (lines 5, 10, 12, 18, 20, 29, 30, 36), but switches to "verification agent" at line 37. This is a minor but unnecessary inconsistency.

Context: `meta-judge.md` line 37: "Pass meta-judge's evaluation YAML to the segment's verification agent"

The sadd ecosystem consistently uses "judge" for the same role. The tp-tdd skill also uses "verification agent" — this is domain-appropriate (test coverage verification) but still inconsistent with the broader vocabulary.

#### `--target-quality` consistency

Fully consistent across skill boundaries:
- `skills/plan-task/SKILL.md` and `plugins/tp-sdd/skills/plan-task/SKILL.md` — identical
- `skills/implement-task/SKILL.md` and `plugins/tp-sdd/skills/implement-task/SKILL.md` — identical
- Same flag name, same description, same default values

No drift detected. PASS.

---

## Additional Findings

### Finding A: CLAUDE.md hard path reference (brittle)

CLAUDE.md line 342:
```
See the synergy map in `.principled/scratch/integration-architecture.md` for the full shared vocabulary.
```

This is a hard file-system path to a scratch document. If the integration-architecture.md is ever moved (e.g., to `.principled/references/`), this reference silently breaks. The CLAUDE.md Non-Brittle Principle says to avoid such path references — or at minimum use natural language ("see the integration architecture document in the scratch directory").

**Severity: LOW** — CLAUDE.md is a development guide, but it should still be maintainable.

### Finding B: Plan documents reiterate vocabulary that skills don't use

Multiple `.principled/` planning documents (BRIEF.md, fan-out-plan.md, synergy-vocabulary-audit.md) advocate the shared vocabulary ("implementation artifact", "judgment criteria"), but no skill file has been updated to use these terms. The plans describe a target state that was never implemented.

**Severity: MEDIUM** — The planning documents and the actual codebase are out of sync. The integration-architecture.md describes a mechanism that doesn't actually work yet.

---

## Final Verdict

**SEMANTICALLY CLEAN with 2 noted gaps**

The good:
- Zero tp- prefix references in any skill, reference, agent, or command file
- `--target-quality` fully consistent across boundaries
- 3 of 8 shared vocabulary concepts have at least marginal adoption (reflection output, decision record, improvement cycle)
- All tp-sdd files exist with valid frontmatter
- "judge" is the dominant, consistent term across ~184 occurrences in execution/verification contexts

The remaining issues:

1. **Synergy vocabulary gap (MEDIUM):** "implementation artifact" and "judgment criteria" — the two most critical shared concepts for cross-plugin composition — are defined in integration-architecture.md but used in ZERO skill files. This was flagged in the previous review and never fixed. The synergy mechanism described in the architecture doc does not actually work yet.

2. **Terminology drift in meta-judge.md (LOW):** One instance of "verification agent" in `skills/execute-plans/references/meta-judge.md:37` where "judge" is the consistent term everywhere else.

3. **CLAUDE.md hard path (LOW):** Hard path to `integration-architecture.md` in scratch/ that will break on relocation.
