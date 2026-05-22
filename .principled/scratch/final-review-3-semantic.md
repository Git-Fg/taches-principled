# Final Semantic Audit — Review 3

**Date:** 2026-05-22
**Scope:** Vocabulary consistency, cross-plugin naming, CEK content gaps, DDD rules quality
**Method:** Full file reads with targeted grep verification across all skill files

---

## Task 1: Non-Brittle Cross-Plugin Communication

### Verified Pairs

**sadd-judge → tp-sdd:** CLEAN — no reference to `tp-sdd` (or `sdd`) by name anywhere in the skill body. References `meta-judge-pattern.md` which is within tp-sadd's own references directory.

**implement-task (tp-sdd) → tp-reflexion:** CLEAN — no reference to `tp-reflexion` or `reflexion` by name.

**reflexion → tp-kaizen or tp-sadd:** CLEAN — no reference to any plugin name. Uses general vocabulary: "multi-perspective review", "independent judge", "quality gate".

**code-review → tp-tdd or tp-git:** CLEAN — no reference to any plugin name. Mentions "test coverage" as a concept, not a plugin.

**fpf-propose → other plugins:** CLEAN — no `tp-*` name reference. Decision Router mentions "kaizen root-cause analysis" and "reflection output" — these are general methodology terms, not plugin names. (kaizen is a Japanese management methodology; reflection is a general cognitive process.)

### Comprehensive Plugin Name Scan

Grep for `tp-sadd|tp-sdd|tp-reflexion|tp-kaizen|tp-fpf|tp-tdd|tp-git|tp-ddd|tp-docs|tp-review|taches-principled-` across ALL skill SKILL.md files and DDD rule files:

**RESULT: ZERO matches.** No skill file in the entire ecosystem references another plugin by its `tp-*` name. This is the correct non-brittle pattern.

### Noticed: Root plan-task Line 603

File: `skills/plan-task/SKILL.md` line 603:
> "Operates between task creation (add-task) and implementation (implement-task)."

This names other skills by their SKILL.md name. However, the CLAUDE.md explicitly permits this for compositional pairs ("create-plans/execute-plans are compositional by design"). `add-task` → `plan-task` → `implement-task` is the same compositional workflow chain. Categorized as **ACCEPTABLE** per the established exception.

### Noticed: fpf-propose Decision Router

File: `plugins/tp-fpf/skills/fpf-propose/SKILL.md` lines 12-13:
> "IF combining with kaizen root-cause analysis -> Use kaizen findings as input evidence"
> "IF combining with reflection output -> Use reflection findings to validate hypotheses"

These reference methodology names (kaizen, reflection), not plugin names (tp-kaizen, tp-reflexion). Categorized as **ACCEPTABLE** — they describe workflow stage inputs, not skill invocation.

---

## Task 2: Shared Vocabulary Consistency

### 2a. "implementation artifact" — VOCABULARY GAP

**Declared in:** `.principled/scratch/integration-architecture.md` line 73:
> "**implementation artifact** | Code, config, or docs produced during execution | sadd (judges it), sdd (produces it), review (reviews it)"

**Used in ZERO skill files.** Grep across all plugin skills returned no matches.

The concept exists implicitly (sadd-judge talks about "artifact type", implement-task talks about "non-critical artifacts"), but the compound term "implementation artifact" is never used. The synergy map claims shared vocabulary that the skills do not actually use.

**Severity: MEDIUM** — does not break operation (Claude infers the relationship), but the architecture doc describes vocabulary that doesn't exist in the skills. This is a documentation-claims-vs-reality gap.

### 2b. "judgment criteria" — VOCABULARY GAP

**Declared in:** `.principled/scratch/integration-architecture.md` line 74:
> "**judgment criteria** | Quality standards for evaluating artifacts | sadd (defines and applies), sdd (fulfills), review (checks)"

**Used in ZERO skill files.** Grep across all plugin skills returned no matches.

**Severity: LOW** — the concept exists under different names ("evaluation criteria" in sadd, "evaluation rubrics" in plan-task). The specific term "judgment criteria" is just unused.

### 2c. "verification level" — CONSISTENT

Used in both:
- `plugins/tp-sdd/skills/implement-task/SKILL.md` line 30: "## Verification Levels" (table with None/Single Judge/Panel/Per-Item)
- Root `skills/implement-task/SKILL.md`: verification level determination logic
- Root `skills/plan-task/SKILL.md`: "For each implementation step, determine verification level"

**Severity: NONE** — consistent concept and comparable implementation across skills.

### 2d. Evaluation Terminology Variance

| Term | Used In |
|------|---------|
| "evaluation criteria" | tp-sadd skills (sadd-execute, sadd-judge, sadd-tot, do-competitively) |
| "evaluation rubrics" | Root plan-task (stage 6 description) |
| "scoring criteria" | meta-judge-pattern.md, judge-with-debate |
| "<evaluation_criteria>" XML tag | create-prompts |
| "<quality_criteria>" XML tag | create-subagents references |

All describe the same concept (standards for judging work quality). The variance is not architecturally harmful because these skills don't need to share a canonical term — they operate at different stages with different syntax conventions. However, it reduces the strength of semantic synergy claimed in the architecture doc.

**Severity: LOW** — consistent within each plugin/domain, variance across ecosystem.

### 2e. "consensus" — SEMANTICALLY CONSISTENT

| Skill | Meaning |
|-------|---------|
| sadd-judge | Score proximity <=0.5 overall, <=1.0 per criterion, explicit acceptance |
| reflexion | "Target consensus or documented reasonable disagreement" |

Both use consensus to mean "independent evaluators agree." The difference in rigor (quantitative vs. qualitative) is appropriate for their different contexts (formal evaluation vs. reflection).

**Severity: NONE** — consistent meaning, appropriate contextual variation.

### 2f. "target-quality" Argument — CONSISTENT

| Skill | Argument | Default | Semantics |
|-------|----------|---------|-----------|
| root plan-task | `--target-quality X.X` | 3.5 | Weighted score threshold |
| plugin plan-task | `--target-quality X.X` | 3.5 | Threshold (out of 5.0) |
| root implement-task | `--target-quality X.X` or X.X,Y.Y | 4.0/4.5 | Standard/critical thresholds |
| plugin implement-task | `--target-quality X.X` or X.X,Y.Y | 4.0/4.5 | Standard/critical threshold |

**Severity: NONE** — consistent argument name across all four versions, same semantics.

### 2g. "artifact" — OVERLOADED (confirmed from previous audit)

- **plan-task**: "Artifacts Generated" = task file, skill document, scratchpad, analysis
- **implement-task**: implementation output (source code)
- **sadd-execute**: candidate solutions, evaluation reports
- **sadd-judge**: judge reports, synthesis
- **reflexion**: project memory updates

The term "artifact" is used generically across all skills without qualification. Skills use "artifact type" (sadd-judge) or "artifacts" as a catch-all. The previous audit recommended distinguishing specification vs. implementation vs. evaluation artifacts.

**Severity: LOW** — operational (skills work), but precision would improve synergy.

---

## Task 3: CEK Content Gap Check

### 3a. update-docs

File: `skills/update-docs/SKILL.md` — 12,191 bytes, 351 lines

**Present:**
- Multi-agent workflow (analysis / tech-writer / review agents)
- Three agent instruction templates for each role
- Documentation philosophy and quality gates
- README and JSDoc best practices
- Index document update checklists
- Output report template

**Missing vs CEK:** The CEK original was 72,863 bytes (6x larger). The reduction is via delta principle — verbose explanations and examples were removed. Current content covers all behavioral needs.

**Verdict: COMPLETE** for behavioral coverage. Delta principle applied correctly.

### 3b. write-concisely

File: `skills/write-concisely/SKILL.md` — 2,857 bytes, 61 lines

**Present:**
- 8 composition principles
- Words to watch table (7 pairs)
- Application checklist (5 scanning steps)
- Design decisions section

**Missing vs CEK:** CEK was 22,855 bytes (8x larger) — likely included full Strunk & White text. The skill explicitly states: "Claude already knows these rules — this skill exists to remind you to apply them. Do not explain the rules in your output."

**Verdict: COMPLETE** by design. Delta principle applied correctly.

### 3c. code-review

File: `skills/code-review/SKILL.md` — ~3,000 bytes, 59 lines

**Present (6 agents confirmed):**
- Bug Hunter, Security Auditor, Code Quality Reviewer, Contracts Reviewer, Historical Context Reviewer, Test Coverage Reviewer
- Focus area and key questions for each
- PR review with eligibility check
- Local changes review with staged/unstaged differentiation
- `--json` flag for local changes
- Quality gate (PASS/FAIL)

**Missing vs CEK originals (review-pr + review-local-changes):**
- No false positive examples section (CEK has dedicated section)
- No detailed inline comment template with emoji severity mapping
- No MCP tool usage examples (`mcp__github_inline_comment__create_inline_comment`)
- No phased Haiku agent workflow for review determination
- No review aspects parsing from `$ARGUMENTS`

**Verdict: PARTIAL** — all 6 agents present with correct focus areas, but key CEK content (false positive examples, inline comment templates, agent workflow) is missing. This is a legit behavioral gap, not a delta-principle removal.

### 3d. reflexion

File: `skills/reflexion/SKILL.md` — ~7,000 bytes, 182 lines

**Bias Countermeasure Table: CONFIRMED COMPLETE (7 biases)**
| Bias | How It Distorts You | Countermeasure |
|------|---------------------|----------------|
| Sycophancy | Wanting to say nice things | Praise is forbidden. Your job is rejection. |
| Length bias | Long output = impressive | Penalize verbosity. |
| Authority bias | Confident tone = correct | Verify every claim. |
| Completion bias | Finished = good | Completion equals nothing. |
| Effort bias | Hard work = merit | Judge output, not input. |
| Recency bias | New patterns = better | Established patterns exist for good reasons. |
| Familiarity bias | Seen it before = good | Common is not correct. |

**Fact-Checking Methodology: CONFIRMED COMPLETE (4 categories)**
1. Performance claims — benchmarking data or Big-O analysis
2. Technical facts — official documentation
3. Security assertions — OWASP or equivalent
4. Best practice claims — authoritative source

Red flags: absolute statements, superlatives, specific numbers without context.

**Verdict: COMPLETE** — both bias countermeasure table and fact-checking methodology present and correct.

---

## Task 4: DDD Rules Quality

### Sample: 5 of 14 rules verified

| Rule | Frontmatter | Wrong/Right Pairs | WHY Explanation | Generic Content |
|------|-------------|-------------------|-----------------|-----------------|
| call-site-honesty.md | title, paths (src/**/*), MEDIUM | YES (2 sections) | YES (policy/mechanism) | NONE |
| command-query-separation.md | title, paths (src/**/*), HIGH | YES (2 sections) | YES (call-site deception) | NONE |
| domain-specific-naming.md | title, paths (**/*), HIGH | YES (2+ sections) | YES (behavior table) | NONE |
| early-return-pattern.md | title, paths (**/*), MEDIUM | YES (2 sections) | YES (cognitive load) | NONE |
| error-handling.md | title, paths (src/**/*), HIGH | YES (2 sections) | YES (debugging traceability) | NONE |

**Verdict: ALL PASS** — Every sampled rule has:
- Proper YAML frontmatter with title, paths, and impact level
- At least one Incorrect/Correct wrong/right teaching pair
- Clear WHY explanation (not just WHAT)
- No generic or filler content

---

## NEW CRITICAL ISSUE: Duplicate Skill Names (Root vs Plugin)

**Files affected:**
- `skills/plan-task/SKILL.md` (31,524 bytes) ↔ `plugins/tp-sdd/skills/plan-task/SKILL.md` (2,897 bytes)
- `skills/implement-task/SKILL.md` (21,983 bytes) ↔ `plugins/tp-sdd/skills/implement-task/SKILL.md` (2,909 bytes)
- `skills/add-task/SKILL.md` (3,776 bytes) ↔ `plugins/tp-sdd/skills/add-task/SKILL.md` (2,157 bytes)

**Problem:** Three skill names exist in both the root `skills/` directory (part of the taches-principled plugin) and the `plugins/tp-sdd/skills/` directory (part of the tp-sdd plugin). When both plugins are installed, the same skill name loads twice — undefined behavior whichever loads last wins.

The root versions are the full implementation (10x larger, with complete phase workflows, error handling, design decisions). The plugin versions are condensed stubs. The CHANGELOG does not document which is canonical or why both exist. This appears to be an incomplete migration — content was ported to the plugin structure but the originals were not removed.

**Severity: HIGH** — naming collision with undefined load behavior. Must be resolved by either removing root copies (if plugin is canonical) or removing plugin stubs (if root is canonical).

---

## ISLANDS RESOLVED: execute-plans references

Previous audit (final-review-audit.md) flagged 5 potentially missing files in execute-plans:

| Reference | Status |
|-----------|--------|
| `references/execution-strategies.md` | EXISTS |
| `references/checkpoint-protocols.md` | EXISTS |
| `references/deviation-rules.md` | EXISTS |
| `templates/autonomous-execution.md` | EXISTS |
| `templates/segment-execution.md` | EXISTS |

All files verified present. **NO ISSUE.**

---

## Summary: Issues by Severity

### HIGH (1)
1. **Duplicate root/plugin skill names** — `plan-task`, `implement-task`, `add-task` exist in both `skills/` and `plugins/tp-sdd/skills/`. Naming collision with undefined load behavior. One set must be removed.

### MEDIUM (2)
1. **"implementation artifact" vocabulary gap** — Defined in integration-architecture.md as shared synergy vocabulary but used in ZERO skill files. Architecture doc claims vocabulary that skills don't use.
2. **code-review missing CEK content** — No false positive examples section, no detailed inline comment templates. Present: all 6 agent definitions with correct focus areas.

### LOW (4)
1. **"judgment criteria" vocabulary gap** — Defined in architecture doc, unused in skills. Concept exists under other names.
2. **Evaluation terminology variance** — "evaluation criteria" (sadd) vs "evaluation rubrics" (plan-task) vs "scoring criteria" (meta-judge pattern). Same concept, different terms.
3. **"artifact" overloaded** — Used generically across all skills for different artifact types (spec, code, evaluation, memory).
4. **fpf-propose methodology references** — Names "kaizen" and "reflection" in decision router. Acceptable as general methodology references, but worth noting.

### NONE (all passing)
- **Zero tp-* plugin name references** in any SKILL.md or rule file
- **consensus** terminology consistent across sadd-judge and reflexion
- **verification level** concept consistent across plan-task and implement-task
- **target-quality** argument name consistent across all skills
- **DDD rules quality** — all 5 sampled pass with frontmatter, teaching pairs, and WHY
- **update-docs** CEK content complete
- **write-concisely** CEK content complete (delta principle applied)
- **reflexion** bias countermeasures and fact-checking complete
- **execute-plans** reference files all present

## Binding Verdict

**NOT SEMANTICALLY CLEAN** — 1 HIGH issue (duplicate skill names) and 2 MEDIUM issues (vocabulary gap, code-review gaps) remain. The semantic synergy claim holds for cross-plugin naming and vocabulary consistency across evaluator skills, but the structural duplication of plan-task/implement-task/add-task is a release blocker, and the synergy vocabulary identified in the architecture doc does not yet exist in the actual skill files.
