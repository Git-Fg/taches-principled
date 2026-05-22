# Deep Plugin Skills Audit — 2026-05-22

Scope: all plugin skills under `plugins/{tp-sadd,tp-fpf,tp-git,tp-tdd,tp-sdd}/skills/*/SKILL.md`

---

## Audit Framework

| Dimension | What It Measures |
|-----------|-----------------|
| **Decision Router** | IF/THEN at top? Specific trigger phrases vs generic? |
| **Delta Principle** | Only documents what differs from default behavior? |
| **Policy/Mechanism** | Policy in body, mechanism deferred to references/ ? |
| **Cross-Skill Refs** | Semantic vocabulary, no hard-coded skill names? |
| **Meta-Judge Deduplication** | SADD: shared pattern via reference, not copy-pasted? |
| **Description Quality** | Specific trigger phrases vs generic descriptions? |
| **Clean Tone** | No XML, no threats, professional prose? |

---

## tp-sadd — 5 skills

| Skill | Router | Delta | P/M | Cross-Skill | Meta-Judge | Description | Tone |
|-------|--------|-------|-----|-------------|------------|-------------|------|
| sadd-dispatch | Strong | Partial | Partial | Clean | N/A (dispatch) | Specific triggers | Clean |
| sadd-execute | Strong | FAIL | FAIL | Clean | **DUPLICATED** | Specific triggers | Clean |
| sadd-judge | Strong | Partial | Partial | Clean | **DUPLICATED** | Specific triggers | Clean |
| sadd-patterns | Strong | Partial | Partial | Clean | N/A (patterns) | Specific triggers | Clean |
| sadd-tot | Strong | FAIL | FAIL | Clean | **DUPLICATED** | Specific triggers | Clean |

### Meta-Judge Deduplication Issues

**Critical finding:** The meta-judge evaluation pattern appears to be copy-pasted in full into three skills: `sadd-execute`, `sadd-judge`, and `sadd-tot`. This is the same ~40-line pattern that was the primary source of 4,000+ lines of duplication in CEK. None of the SADD skills use a shared reference file.

#### Pattern as it appears in each skill:

**sadd-execute** (lines 24-33):
> All four modes follow this core loop:
> 1. Meta-Judge: One or more meta-judges generate YAML evaluation specifications
> 2. Implementation: One or more agents implement the work using CoT reasoning
> 3. Judge Verification: Independent judge(s) evaluate output against the exact meta-judge specification
> 4. Retry Loop: If score < 4.0 with retries remaining, retry implementation with judge feedback

**sadd-judge** (lines 23-33):
> This pattern is shared by both evaluation modes:
> 1. Dispatch a meta-judge (Opus) to generate a YAML evaluation specification
> 2. Pass the EXACT meta-judge specification YAML to one or more independent judges
> 3. Parse only the structured header (VERDICT/SCORE/ISSUES/IMPROVEMENTS) from judge output
> 4. On retry, reuse the same meta-judge specification — never re-run meta-judge

**sadd-tot** references the meta-judge pattern implicitly at line 34 ("Follow the standard meta-judge evaluation pattern") but duplicates the evaluation loop structure in lines 48-56.

**Deduplication opportunity:** Extract the shared meta-judge pattern into `plugins/tp-sadd/references/meta-judge-pattern.md`. Each skill should contain only: "Follow the standard meta-judge evaluation pattern (see references/meta-judge-pattern.md)" with zero duplication.

### Other Issues for tp-sadd

**Delta failures — sadd-execute:**
- Lines 35-44 repeat model selection that is already described in sadd-dispatch. The model selection table is nearly identical.
- Lines 156-185 (Design Decisions) restate reasoning that applies generically to multi-agent verification, not specifically to execution mode differences.
- The skill is 186 lines. After removing duplicated meta-judge pattern (~35 lines) and generic model selection (~10 lines), it would be ~140 lines.

**Delta failures — sadd-tot:**
- Phase 1.5 (lines 30-34) and Phase 3.5 (lines 49-50) are nearly identical — both dispatch a meta-judge "in parallel with the agent phase." This parallelism pattern is duplicated.
- The Exploration + Pruning + Expansion structure is very similar across phases — there is residual duplication that could be collapsed.

**Policy/Mechanism mixing — sadd-dispatch:**
- Lines 44-48 describe how to construct the sub-agent prompt (mechanism) in the body rather than deferring to references/.
- This is a borderline case — the "how" of prompt construction is specific to dispatch, not general.

---

## tp-fpf — 3 skills

| Skill | Router | Delta | P/M | Cross-Skill | Description | Tone |
|-------|--------|-------|-----|-------------|-------------|------|
| fpf-propose | Strong | PASS | PASS | Clean | Specific triggers | Clean |
| fpf-read | Strong | PASS | PASS | Clean | Specific triggers | Clean |
| fpf-maintenance | Strong | PASS | PASS | Clean | Specific triggers | Clean |

**Assessment:** tp-fpf is the cleanest plugin reviewed. All three skills pass delta principle. Decision routers are strong with specific trigger phrases. No cross-skill brittleness. The FPF skills use natural semantic references ("use kaizen findings as input evidence") without naming the kaizen plugin.

**Minor note:** fpf-maintenance line 140 references `/fpf:fpf-maintenance` with an explicit slash command — this is a plugin-internal command reference, not a cross-plugin name, so it is acceptable. However, strictly speaking, slash command syntax could be considered a form of hard-coded naming. For forward compatibility, "run the FPF maintenance skill" would be more portable.

---

## tp-git — 4 skills

| Skill | Router | Delta | P/M | Cross-Skill | Description | Tone |
|-------|--------|-------|-----|-------------|-------------|------|
| git-advanced | Strong | PASS | PASS | Clean | Specific triggers | Clean |
| git-issues | Strong | PASS | PASS | Clean | Specific triggers | Clean |
| git-review | Strong | PASS | PASS | Clean | Specific triggers | Clean |
| git-ship | Strong | PASS | PASS | Clean | Specific triggers | Clean |

**Assessment:** tp-git is very clean. All skills pass delta principle. Strong decision routers with specific IF/THEN conditions. git-ship has a minor issue (line 117: "downstream implementation processes") but this is vague semantic language, not a hard plugin name.

**Note on git-review:** The description says "prefer MCP inline comment tools when available" — this references MCP infrastructure. The project CLAUDE.md states "No MCP references (plugin is MCP-free)." This is a minor contradiction, but the skill itself doesn't add MCP tooling, it merely notes it as an availability-based preference.

---

## tp-tdd — 1 skill

| Skill | Router | Delta | P/M | Cross-Skill | Description | Tone |
|-------|--------|-------|-----|-------------|-------------|------|
| tdd | Strong | PASS | PASS | Clean | Specific triggers | Clean |

**Assessment:** tdd passes all audits. Clean decision router. The "Iron Law" (no production code without failing test first) is a strong policy statement in the body. Anti-patterns table is concrete with consequence explanations. No cross-skill brittleness.

**Minor delta observation:** The Agent Templates section (lines 87-116) contains three sub-agent prompt templates. These are quite detailed — if the templates were needed by other skills, they could be deferred to references/. Currently they are not referenced externally, so this is acceptable as in-body content.

---

## tp-sdd — 5 skills

| Skill | Router | Delta | P/M | Cross-Skill | Description | Tone |
|-------|--------|-------|-----|-------------|-------------|------|
| add-task | Strong | PASS | PASS | Clean | Specific triggers | Clean |
| brainstorm | Strong | PASS | PASS | Clean | Specific triggers | Clean |
| create-ideas | Strong | FAIL | PASS | Clean | Specific triggers | Clean |
| implement-task | Strong | FAIL | PASS | Clean | Specific triggers | Clean |
| plan-task | Strong | FAIL | PASS | Clean | Specific triggers | Clean |

### Delta Failures — tp-sdd

**create-ideas** (33 lines):
- The 6-response strategic sampling process is described at lines 19-25. This same probabilistic sampling framing appears in brainstorm (lines 26-30) and create-ideas. The "first 3 high probability >0.80, last 3 low probability <0.10" instruction is repeated across both skills.
- At 33 lines, this is very short — the duplication is minor, but the sampling instruction could be a shared reference.

**implement-task** (89 lines):
- Lines 40-48 (Orchestrator Role table) restate the "dispatch and aggregate only" principle that appears in exactly the same form in plan-task (lines 40-48). This is verbatim duplication of the prohibited-actions table.
- The verification levels table (lines 31-38) duplicates content from plan-task's verification structure.

**plan-task** (81 lines):
- Lines 40-48 (Orchestrator Role table) is verbatim duplicate of implement-task's same-named section.
- Lines 72-78 (Critical Rules) restate threshold rules that implement-task also states.
- The stage workflow diagram (lines 47-70) is detailed but internal to the skill — acceptable.

**Cross-skill duplication between implement-task and plan-task:**
Both skills contain identical text:
> **You are dispatch and aggregate only — you do not do the work.**
> | Prohibited | Why | Instead |
> |------------|-----|---------|
> | Read implementation outputs | Context bloat | Sub-agent reports |
> | Evaluate code quality yourself | Causes forgetting | Launch judge agent |
> | Skip verification | Quality collapse | Launch judge anyway |

This ~8-line table appears in both skills at the same position (lines 40-48). This is a deduplication opportunity — extract to `plugins/tp-sdd/references/orchestrator-principles.md`.

---

## Cross-Plugin Brittleness Assessment

**Overall finding: No hard-coded cross-plugin skill names detected.** All skills use semantic vocabulary as required.

- tp-fpf references "kaizen findings" and "reflection findings" without naming kaizen/reflexion plugins
- tp-git references "downstream implementation processes" generically
- tp-sdd references "downstream improvement processes" in brainstorm

No instances of brittle patterns like "use tp-sadd:judge" or "feeds into tp-kaizen:analyse".

---

## Summary of Deduplication Opportunities

| Priority | Plugin | Opportunity | Est. Lines Saved |
|----------|--------|-------------|------------------|
| **Critical** | tp-sadd | Extract shared meta-judge pattern to references/ | ~100 lines across 3 skills |
| High | tp-sdd | Extract orchestrator-principles table to references/ | ~16 lines across 2 skills |
| Medium | tp-sdd | Collapse duplicate probabilistic sampling instruction | ~6 lines across 2 skills |
| Low | tp-fpf | Consider replacing `/fpf:fpf-maintenance` with "FPF maintenance skill" | 0 lines, phrasing only |

---

## Specific Fix Recommendations

### 1. tp-sadd — Meta-Judge Pattern Deduplication (Critical)

**Create:** `plugins/tp-sadd/references/meta-judge-pattern.md`

Content: the shared pattern (~35 lines) currently copy-pasted in sadd-execute (lines 24-33), sadd-judge (lines 23-33), and implicitly in sadd-tot.

**In each affected skill, replace the duplicated block with:**
> Follow the standard meta-judge evaluation pattern (see `references/meta-judge-pattern.md`).

**sadd-tot additionally:** Phase 1.5 and Phase 3.5 both dispatch a meta-judge "in parallel with the agent phase" — these could be unified into a single reference to the parallelism pattern.

### 2. tp-sdd — Orchestrator Principles Deduplication (High)

**Create:** `plugins/tp-sdd/references/orchestrator-principles.md`

Content: the "dispatch and aggregate only" prohibited-actions table (~8 lines) currently in both implement-task (lines 40-48) and plan-task (lines 40-48).

**In each affected skill, replace with:**
> Follow the standard orchestrator principles (see `references/orchestrator-principles.md`).

### 3. tp-sdd — Probabilistic Sampling (Medium)

The "first 3 high probability >0.80, last 3 low probability <0.10" instruction appears in both brainstorm and create-ideas. Consider extracting to `references/probabilistic-sampling.md` and referencing it from both skills.

### 4. tp-fpf — Command Reference (Low)

**fpf-maintenance line 140:** `/fpf:fpf-maintenance` → "run the FPF maintenance skill"

---

## Skills Assessed as Clean

The following require no changes:
- tp-fpf: fpf-propose, fpf-read, fpf-maintenance — all pass delta principle, strong routers, no brittleness
- tp-git: git-advanced, git-issues, git-review, git-ship — all pass delta principle, strong routers
- tp-tdd: tdd — passes all audits
- tp-sadd: sadd-dispatch, sadd-patterns — pass, with minor delta notes above
- tp-sdd: add-task, brainstorm — pass, with minor delta notes above