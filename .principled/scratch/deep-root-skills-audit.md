# Deep Quality Audit — Root Skills

Date: 2026-05-22 | Auditor: systematic multi-dimension analysis | Total: 22 skills

---

## Summary Table (sorted by urgency: REWRITE > REFACTOR > KEEP)

| Skill | Lines | Router | Delta | P/M | Anti-patterns | Frontmatter | Cross-skill | Completeness | Length | Verdict |
|-------|-------|--------|-------|-----|---------------|-------------|-------------|--------------|--------|---------|
| analyse | 65 | PARTIAL | YES | CLEAN | vague "specific" | VALID | CLEAN | COMPLETE | THIN | REFACTOR |
| kaizen | 88 | MISSING | YES | CLEAN | generic "improvement" | VALID | CLEAN | PARTIAL | THIN | REFACTOR |
| plan-do-check-act | 62 | MISSING | YES | CLEAN | vague success | VALID | CLEAN | COMPLETE | THIN | REFACTOR |
| write-concisely | 62 | MISSING | YES | CLEAN | generic "documentation" | VALID | CLEAN | PARTIAL | THIN | REFACTOR |
| root-cause-analysis | 64 | MISSING | YES | CLEAN | generic trigger phrases | VALID | CLEAN | COMPLETE | THIN | REFACTOR |
| root-cause-tracing | 77 | MISSING | YES | CLEAN | generic "error" | VALID | CLEAN | COMPLETE | THIN | REFACTOR |
| reflexion | 157 | PARTIAL | YES | CLEAN | vague thresholds, generic "high-stakes" | VALID | CLEAN | COMPLETE | OK | KEEP |
| plan-task | 604 | PARTIAL | YES | CLEAN | complex arg parsing table | VALID | CLEAN | COMPLETE | BLOAT | REFACTOR |
| create-prompts | 482 | PARTIAL | PARTIAL | CLEAN | generic "concise" | VALID | CLEAN | COMPLETE | OK | KEEP |
| ideation | 65 | PARTIAL | NO | CLEAN | generic "creative" | VALID | CLEAN | COMPLETE | THIN | REFACTOR |
| code-review | 56 | YES | YES | CLEAN | none | VALID | CLEAN | COMPLETE | THIN | KEEP |
| code-simplify | 293 | YES | YES | CLEAN | verbose anti-patterns | VALID | CLEAN | COMPLETE | OK | KEEP |
| create-skills | 512 | YES | YES | CLEAN | none | VALID | CLEAN | COMPLETE | BLOAT | REFACTOR |
| add-task | 88 | YES | YES | CLEAN | none | VALID | CLEAN | COMPLETE | OK | KEEP |
| create-subagents | 613 | YES | YES | CLEAN | generic spawn example | VALID | CLEAN | COMPLETE | BLOAT | REFACTOR |
| execute-plans | 593 | PARTIAL | YES | CLEAN | vague "architectural" | VALID | BRITTLE | COMPLETE | BLOAT | REFACTOR |
| create-plans | 604 | YES | YES | CLEAN | none | VALID | CLEAN | COMPLETE | BLOAT | REFACTOR |
| analyse-problem | 67 | MISSING | YES | CLEAN | generic "recurring" | VALID | CLEAN | COMPLETE | THIN | REFACTOR |
| implement-task | 568 | YES | YES | CLEAN | none | VALID | CLEAN | COMPLETE | BLOAT | KEEP |
| subagent-orchestration | 306 | YES | YES | CLEAN | generic "high-stakes" | VALID | CLEAN | COMPLETE | OK | KEEP |
| execute-prompts | 296 | PARTIAL | YES | CLEAN | generic "autonomous" | VALID | CLEAN | COMPLETE | OK | KEEP |
| update-docs | 147 | MISSING | YES | CLEAN | generic "user-facing" | VALID | CLEAN | COMPLETE | OK | KEEP |

---

## Individual Skill Audits

### add-task (88 lines)
- **Router**: YES — solid. Clear IF/THEN with specific triggers.
- **Delta**: YES — clean. States what skill adds vs default: "preserves original user prompt verbatim."
- **Policy/Mechanism**: CLEAN — policy in frontmatter (when_to_use), mechanism in body.
- **Anti-patterns**: None found.
- **Frontmatter**: VALID — name, description, argument-hint all present and correct.
- **Cross-skill refs**: CLEAN — no hard-coded skill names.
- **Completeness**: COMPLETE — clear process, output format, design decisions.
- **Length**: OK — 88 lines, appropriate for a simple capture skill.
- **Verdict**: KEEP
- **Specific fixes needed**: None. This is a well-designed focused skill.

---

### analyse (65 lines)
- **Router**: PARTIAL — IF conditions are specific BUT the trigger phrases are generic ("analyzing code implementation", "workflows, processes") and the "IF the method is already clear" clause creates ambiguity.
- **Delta**: YES — clean delta table showing what skill adds vs default behavior.
- **Policy/Mechanism**: CLEAN — policy at top (routing), mechanism in body.
- **Anti-patterns**: Line 11 says "specific" but criteria are vague. "Analyze code implementation, exploring unfamiliar code" — these are not concrete trigger phrases.
- **Frontmatter**: VALID — name, description, argument-hint all present.
- **Cross-skill refs**: CLEAN — no hard-coded skill names.
- **Completeness**: COMPLETE — three methods well-defined, output format specified.
- **Length**: THIN — 65 lines for a skill that covers three distinct methods. Could be richer.
- **Verdict**: REFACTOR
- **Specific fixes needed**:
  1. Strengthen router trigger phrases — replace "analyzing code implementation" with concrete phrases like "Explore how X works in the codebase" or "Understand the auth flow."
  2. The "IF the method is already clear" clause (line 12) is self-defeating — if clear, no routing needed. Remove or clarify.
  3. Add concrete decision examples for each method selection.
  4. Consider: "IF combining with A3" (line 13) is implementation detail, not routing signal. Move to body.

---

### analyse-problem (67 lines)
- **Router**: MISSING — no decision router at top. First content is a heading "# Analyse Problem" then body text without any IF/THEN routing.
- **Delta**: YES — Core Principle clearly states what A3 adds: "single-page constraint as forcing function."
- **Policy/Mechanism**: CLEAN — policy in body (when to use), mechanism well-defined.
- **Anti-patterns**: Line 10 says "trivial one-line fix" but gives no concrete threshold. "recurring issue" is not a trigger phrase.
- **Frontmatter**: VALID — name, description, argument-hint present.
- **Cross-skill refs**: CLEAN — no hard-coded skill names.
- **Completeness**: COMPLETE — template provided, phases clear, design decisions documented.
- **Length**: THIN — 67 lines. This is a complete skill but could benefit from more concrete guidance.
- **Verdict**: REFACTOR
- **Specific fixes needed**:
  1. **ADD decision router at top** — this is the primary issue. Without IF/THEN at the top, routing is ambiguous.
  2. Add concrete threshold for "trivial" vs. "significant" — e.g., "IF the issue is understood in one sentence and fix is obvious → skip A3."
  3. The "recurring" qualifier (line 10) needs specificity — recurring how many times? Once is recurring.
  4. Line 11: "IF deeper root cause work is needed" — "deeper" is vague. Specify what signals insufficient root cause.

---

### code-review (56 lines)
- **Router**: YES — solid. Two clear paths (PR vs local) with explicit IF conditions and ambiguous fallback.
- **Delta**: YES — clean. Mentions 6 specialized agents and progressive confidence scoring as the delta.
- **Policy/Mechanism**: CLEAN — policy in router, mechanism in body.
- **Anti-patterns**: None found. The "skip if >500 lines" threshold (line 45) is concrete and appropriate.
- **Frontmatter**: VALID — name, description, argument-hint all correct.
- **Cross-skill refs**: CLEAN — no hard-coded references.
- **Completeness**: COMPLETE — multi-agent pattern, phase structure, environment-specific handling.
- **Length**: THIN — 56 lines is appropriately focused for a router skill.
- **Verdict**: KEEP
- **Specific fixes needed**: None. Well-designed.

---

### code-simplify (293 lines)
- **Router**: YES — solid. Clear IF/THEN with specific conditions (compiles, no tests, risky code, active development, one-person project).
- **Delta**: YES — excellent delta table showing default vs. skill behavior.
- **Policy/Mechanism**: CLEAN — policy in router, mechanism (5-stage pipeline) well-defined.
- **Anti-patterns**: Anti-patterns section (lines 140-192) is overly verbose — 50+ lines for anti-patterns. Could be tightened.
- **Frontmatter**: VALID — name, description, when_to_use all present and appropriate.
- **Cross-skill refs**: CLEAN — no hard-coded skill names.
- **Completeness**: COMPLETE — pipeline, thresholds, agent template, success criteria all documented.
- **Length**: OK — 293 lines. Appropriate for a skill with this much mechanism.
- **Verdict**: KEEP
- **Specific fixes needed**:
  1. Anti-patterns section is too long (52 lines). Reduce to ~20 lines — keep only the most impactful anti-patterns with clear wrong/right pairs.
  2. Consider: "Simplify Without Tests" section (lines 111-126) could reference a more detailed external guide rather than duplicating guidance inline.

---

### create-plans (604 lines)
- **Router**: YES — excellent. Clear IF/THEN conditions with specific file references and user phrase → action mapping table.
- **Delta**: YES — Core Principle clearly states "PLAN.md IS the prompt." Policy vs. Mechanism section well-defined.
- **Policy/Mechanism**: CLEAN — policy in router, mechanism deferred to references/.
- **Anti-patterns**: None found. The "500-line Mega-Plan" anti-pattern is specific and actionable.
- **Frontmatter**: VALID — name, description, when_to_use all present.
- **Cross-skill refs**: CLEAN — references are natural language, not hard-coded paths.
- **Completeness**: COMPLETE — comprehensive skill covering all aspects of planning.
- **Length**: BLOAT — 604 lines. Exceeds 500-line guideline.
- **Verdict**: REFACTOR
- **Specific fixes needed**:
  1. **Reduce to ~450 lines** — apply the delta principle more aggressively.
  2. Lines 565-577 (Domain Expertise exclusion) is policy commentary that could be cut.
  3. Consider: "Context Scan" section (lines 225-253) is long. Could some of this be deferred to a reference?
  4. The "What Good Looks Like" section (lines 462-511) is comprehensive but could be tightened.

---

### create-prompts (482 lines)
- **Router**: PARTIAL — IF conditions for generation types are present but generic ("coding task", "analysis task", "research task"). No specific trigger phrases.
- **Delta**: PARTIAL — states prompts are XML-structured artifacts, but the "what this skill adds vs default" is implicit, not explicit. Delta table could make this clearer.
- **Policy/Mechanism**: CLEAN — policy in decision router, mechanism in body.
- **Anti-patterns**: Line 396 says "concise" but the prompt patterns are quite verbose. "Be Explicit" says "precision over brevity" which contradicts the skill name.
- **Frontmatter**: VALID — name, description, when_to_use all present and appropriate.
- **Cross-skill refs**: CLEAN — no hard-coded skill names.
- **Completeness**: COMPLETE — adaptive intake, decision gate loop, prompt generation patterns, execution strategies all well-covered.
- **Length**: OK — 482 lines, just under 500-line guideline.
- **Verdict**: KEEP (minor issues)
- **Specific fixes needed**:
  1. Clarify the delta — what does this skill add vs. default prompt behavior? The "what makes this skill different" should be explicit.
  2. "Write Concisely" naming is ironic given the verbose prompt template examples. Consider renaming to "Create Prompts" to match the skill name.
  3. The decision router could be stronger — specific trigger phrases for "I want to create a prompt" vs. "write me a test prompt."

---

### create-skills (512 lines)
- **Router**: YES — excellent. Multiple specific IF conditions with explicit reference file reads.
- **Delta**: YES — Core Principle about "500-line rule is indicative" is well-explained. Categories section clearly defines what each type adds.
- **Policy/Mechanism**: CLEAN — policy in decision router, mechanism in body.
- **Anti-patterns**: None found.
- **Frontmatter**: VALID — name, description, when_to_use all present and appropriate.
- **Cross-skill refs**: CLEAN — uses semantic references ("read references/context-management.md" not hard-coded paths).
- **Completeness**: COMPLETE — categories, examples, anti-patterns, reference index, testing guidance.
- **Length**: BLOAT — 512 lines, exceeds guideline.
- **Verdict**: REFACTOR
- **Specific fixes needed**:
  1. Reduce to ~450 lines. The "Reference Index" section (lines 493-502) could be trimmed.
  2. Lines 43-47 (Pre-Flight Validation Checklist) could be deferred to a reference.
  3. The "Bundled Agents Pattern" section (lines 283-365) is very long — consider if some of this belongs in a reference.

---

### create-subagents (613 lines)
- **Router**: YES — solid. Multiple specific IF conditions with reference file reads.
- **Delta**: YES — "Subagents are black boxes" principle is clear. Policy vs. Mechanism section well-defined.
- **Policy/Mechanism**: CLEAN — policy in body, mechanism in spawn prompt guidance.
- **Anti-patterns**: Lines 462-465: The security reviewer example is good but the spawn prompt itself could be more concrete.
- **Frontmatter**: VALID — name, description, when_to_use all present.
- **Cross-skill refs**: CLEAN — references use natural language.
- **Completeness**: COMPLETE — very comprehensive subagent creation guide.
- **Length**: BLOAT — 613 lines, significantly exceeds guideline.
- **Verdict**: REFACTOR
- **Specific fixes needed**:
  1. **Reduce to ~450 lines** — this is the most bloated skill.
  2. The "Body Prompt Philosophy — The Waste Test" (lines 298-310) could be tightened.
  3. The "Orchestration Patterns" section (lines 320-406) is very long — could defer some to references.
  4. Multi-Agent Gotchas section (lines 536-565) is dense but necessary. Keep but consider if it could be a reference.
  5. The spawn prompt examples (lines 204-243) are helpful but verbose.

---

### execute-plans (593 lines)
- **Router**: PARTIAL — strategy selection is clear but the IF conditions at the top of the skill (lines 9-16) don't have the same concrete specificity as create-plans. The "IF spawning parallel workers" is a compound condition.
- **Delta**: YES — clear. "Plans are prompts. Execute them exactly."
- **Policy/Mechanism**: CLEAN — policy in strategy selection, mechanism in execution handlers.
- **Anti-patterns**: Line 281-283: "architectural changes" is vague. What constitutes "significant"? The numeric thresholds help but could be more specific.
- **Frontmatter**: VALID — name, description, when_to_use all present.
- **Cross-skill refs**: BRITTLE — Line 14 references "orchestration-patterns.md file in the create-plans skill's references" by file path. This is a hard-coded path to another skill's internals. Line 581-582 has same issue. Should use semantic reference.
- **Completeness**: COMPLETE — three strategies well-defined, deviation rules comprehensive.
- **Length**: BLOAT — 593 lines, exceeds guideline.
- **Verdict**: REFACTOR
- **Specific fixes needed**:
  1. **Fix cross-skill reference brittleness** — lines 14, 581-582 reference `{baseDir}/references/orchestration-patterns.md` which is inside create-plans skill. Use semantic reference: "see the orchestration patterns reference for pattern selection."
  2. Reduce to ~450 lines. The "Thought/Action/Observation Anti-Pattern" section (lines 534-550) is detailed but could be a reference.
  3. The deviation rules (lines 227-352) are very comprehensive — could some be deferred?

---

### execute-prompts (296 lines)
- **Router**: PARTIAL — IF conditions are present but generic ("single prompt", "parallel prompts", "sequential prompts"). Missing trigger phrases for when a user would invoke this skill.
- **Delta**: YES — Core Principle clearly states delegation preserves orchestration capacity.
- **Policy/Mechanism**: CLEAN — policy in strategy selection, mechanism in parsing/execution.
- **Anti-patterns**: Line 247-253: "Parallelization Without True Concurrency" — the anti-pattern is clear but the fix could be more specific.
- **Frontmatter**: VALID — name, description, when_to_use all present.
- **Cross-skill refs**: CLEAN — no hard-coded skill references.
- **Completeness**: COMPLETE — execution modes, argument parsing, file resolution, archival workflow all covered.
- **Length**: OK — 296 lines, appropriate for scope.
- **Verdict**: KEEP
- **Specific fixes needed**:
  1. Strengthen decision router — add specific trigger phrases. What would a user say that loads this skill? "Run my prompts", "execute prompts", "launch prompts" should be explicit.
  2. The "Thought/Action/Observation Anti-Pattern" is duplicated from execute-plans. Consider factoring out.

---

### ideation (65 lines)
- **Router**: PARTIAL — IF conditions are present but use vague terms ("unformed idea", "vague concept", "creative idea"). "IF user already knows exactly what they want" is ambiguous — when does this trigger vs. skip?
- **Delta**: NO — no explicit statement of what this skill adds vs. default. The "probability-based exploration" is the delta but it's buried in body, not stated in router.
- **Policy/Mechanism**: CLEAN — policy in decision router, mechanism in body.
- **Anti-patterns**: Line 3 description says "generate diverse creative options" but "creative" is not defined. "Probability sampling" is mentioned but not explained. "Refine vague concepts" is vague.
- **Frontmatter**: VALID — name, description, argument-hint present.
- **Cross-skill refs**: CLEAN — no hard-coded skill names.
- **Completeness**: COMPLETE — two modes (brainstorm, create-ideas) well-defined with process and output.
- **Length**: THIN — 65 lines for a skill that describes two distinct modes. Could be richer.
- **Verdict**: REFACTOR
- **Specific fixes needed**:
  1. **ADD explicit delta statement** — what does this skill add vs. default brainstorming?
  2. "Unformed idea or vague concept" — what specific user phrases trigger this? "I want to build something", "I have an idea", "not sure what I want" should be listed.
  3. "Probability-based exploration" needs concrete explanation — what probability distribution? What does "anchors vs. tail explorations" mean in practice?
  4. The "Create Ideas Mode" section (line 62+) is a single paragraph. Needs more substance.

---

### implement-task (568 lines)
- **Router**: YES — excellent. Clear flag-based routing (`--continue`, `--refine`, `--human-in-the-loop`, `--skip-judges`, `--target-quality`) with specific behavior definitions.
- **Delta**: YES — "Context is the orchestrator's most precious resource" clearly states what this skill adds vs. direct implementation.
- **Policy/Mechanism**: CLEAN — policy in decision router and configuration, mechanism in phase execution.
- **Anti-patterns**: None found.
- **Frontmatter**: VALID — name, description, argument-hint all present and appropriate.
- **Cross-skill refs**: CLEAN — no hard-coded skill names.
- **Completeness**: COMPLETE — all phases well-documented, patterns A/B/C clear, evaluation integrity rules explicit.
- **Length**: BLOAT — 568 lines, exceeds guideline.
- **Verdict**: KEEP (significant content)
- **Specific fixes needed**:
  1. Reduce to ~450 lines. The "Usage Walkthrough" (lines 421-472) is helpful but could be a reference.
  2. The "Verification Specifications Reference" (lines 474-529) is very detailed — could some be deferred to a reference?
  3. Consider splitting: Phase 0-5 (orchestration) stays, detailed verification spec becomes a reference.

---

### kaizen (88 lines)
- **Router**: MISSING — no decision router at top. First content is "# Kaizen" heading then body text. The "IF implementing code, refactoring..." (line 9) appears AFTER the heading, not as a preamble.
- **Delta**: YES — Core Principle clearly states four design-time constraints.
- **Policy/Mechanism**: CLEAN — policy well-defined in four pillars.
- **Anti-patterns**: Line 3 says "improvement" but doesn't define what "improvement" means. "Incremental over revolutionary" is a principle, not a trigger. Generic.
- **Frontmatter**: VALID — name, description, argument-hint present.
- **Cross-skill refs**: CLEAN — no hard-coded skill names.
- **Completeness**: PARTIAL — four pillars described but no concrete examples of application. "This skill applies as behavioral constraints" but no specific decision tree.
- **Length**: THIN — 88 lines. Complete conceptually but lacks concrete routing.
- **Verdict**: REFACTOR
- **Specific fixes needed**:
  1. **ADD decision router at top** — this is the primary issue. "IF implementing code, refactoring..." should be the first content, before the heading.
  2. Each pillar needs concrete IF/THEN guidance. "Continuous Improvement" → what specific signal triggers this? "When you see a function >40 lines" is concrete.
  3. The "Red flag" indicators need to be actionable, not just principles.
  4. Consider: this skill reads as principles with examples, but lacks specific "WHEN to apply X" decision points.

---

### plan-do-check-act (62 lines)
- **Router**: MISSING — no decision router at top. First content is the "# Plan-Do-Check-Act" heading, then body text without IF/THEN routing.
- **Delta**: YES — Core Principle clearly states "never implement a change without knowing how you will measure success."
- **Policy/Mechanism**: CLEAN — policy in body, mechanism well-defined.
- **Anti-patterns**: Line 9 says "start a PDCA cycle with a clear success criterion" but doesn't define what "clear" means. "Measurable" appears in line 27 but success criteria should be explicit.
- **Frontmatter**: VALID — name, description, argument-hint present.
- **Cross-skill refs**: CLEAN — no hard-coded skill names.
- **Completeness**: COMPLETE — four phases well-defined, output specified.
- **Length**: THIN — 62 lines. Could be richer with more concrete guidance.
- **Verdict**: REFACTOR
- **Specific fixes needed**:
  1. **ADD decision router at top** — first content should be IF/THEN conditions.
  2. Add explicit success criterion examples — what does a "clear criterion" look like? Give concrete numbers/measurements.
  3. "Stuck after three cycles" (line 13) — what constitutes "stuck"? Define threshold.
  4. Consider: this skill would benefit from a concrete "when to use PDCA vs. A3 vs. root cause analysis" decision tree.

---

### plan-task (604 lines)
- **Router**: PARTIAL — has decision router but conditions use flag names (`--fast`, `--continue`, `--refine`) rather than natural language trigger phrases. Missing: "IF user says 'plan', 'refine', 'continue'."
- **Delta**: YES — "Specification quality is a prerequisite for implementation speed" is a clear delta statement.
- **Policy/Mechanism**: CLEAN — policy in decision router and configuration, mechanism in phases.
- **Anti-patterns**: Line 29-36 (Argument Definitions table) is very dense — 36 rows with descriptions. This is essentially documentation, not decision routing. Flag parsing could be a reference.
- **Frontmatter**: VALID — name, description, argument-hint all present.
- **Cross-skill refs**: CLEAN — no hard-coded skill names.
- **Completeness**: COMPLETE — all 7 phases well-documented with sub-agents, judges, and error handling.
- **Length**: BLOAT — 604 lines, exceeds guideline significantly.
- **Verdict**: REFACTOR
- **Specific fixes needed**:
  1. **Add natural language trigger phrases** — the skill triggers on flag arguments but NOT on natural language like "refine this task" or "plan this feature." Add: "IF user asks to plan, refine, or continue a task specification → use this skill."
  2. Reduce to ~450 lines.
  3. Argument Definitions table (lines 29-36) should be a reference, not inline body. It reads as documentation, not decision guidance.
  4. "Integrity Rules for Sub-Agents" (lines 122-128) could be tightened.
  5. Consider: Phase documentation (2-7) is very thorough. Could some phase descriptions be deferred to references?

---

### reflexion (157 lines)
- **Router**: PARTIAL — IF conditions are present but use vague terms ("self-reviewing completed work", "high-stakes work"). "Confidence threshold" is mentioned but not defined.
- **Delta**: YES — "Reflect → Critique → Memorize" cycle is the clear delta.
- **Policy/Mechanism**: CLEAN — policy in decision router, mechanism in three methods.
- **Anti-patterns**: Lines 33-36: "Target confidence >4.0/5.0" — what does "4.0" mean in practice? What constitutes "deep"? Lines 46-52: Scoring scale is clear but "default score is 2" is arbitrary. "Rare" and "Common" are subjective.
- **Frontmatter**: VALID — name, description, argument-hint all present.
- **Cross-skill refs**: CLEAN — no hard-coded skill names.
- **Completeness**: COMPLETE — Reflect, Critique, Memorize all well-defined with processes and output formats.
- **Length**: OK — 157 lines, appropriate for scope.
- **Verdict**: KEEP
- **Specific fixes needed**:
  1. "Self-reviewing completed work" — what specific signals trigger this? "After completing a task", "after implementation", "before commit"?
  2. "Confidence threshold" argument (line 12) needs concrete examples: what does "confidence threshold 0.7" mean in practice?
  3. "Default score is 2" needs justification — why 2, not 3?
  4. "Genuinely solid work" (line 51) is vague — replace with concrete criterion.

---

### root-cause-analysis (64 lines)
- **Router**: MISSING — no decision router at top. First content is heading then body text. The Five Whys vs. Fishbone decision is in the body, not at top.
- **Delta**: YES — "Every surface symptom is the end of a causal chain" is a clear delta statement.
- **Policy/Mechanism**: CLEAN — policy in body, mechanism well-defined for both methods.
- **Anti-patterns**: Line 11 says "human error" but gives no guidance on how to handle it when found. "Keep digging regardless" is not specific. "IF problem has a clear single causal chain" — what makes it "clear"?
- **Frontmatter**: VALID — name, description, argument-hint present.
- **Cross-skill refs**: CLEAN — no hard-coded skill names.
- **Completeness**: COMPLETE — both methods well-defined with process and output.
- **Length**: THIN — 64 lines. Could benefit from more concrete guidance.
- **Verdict**: REFACTOR
- **Specific fixes needed**:
  1. **ADD decision router at top** — move "IF problem has a clear single causal chain" to before the "# Root Cause Analysis" heading.
  2. "Clear single causal chain" needs definition — what signals indicate clear vs. complex causality?
  3. "Human error" guidance (line 11) needs more specificity — what does "keep digging" mean in practice? What systemic cause should be found?
  4. Add concrete example of Five Whys vs. Fishbone selection.

---

### root-cause-tracing (77 lines)
- **Router**: MISSING — no decision router at top. First content is heading then body text. The "IF an error occurs deep in execution" condition appears in body, not as preamble.
- **Delta**: YES — "Never fix where the error appears. Trace backward" is an excellent delta statement.
- **Policy/Mechanism**: CLEAN — policy in body, mechanism well-defined.
- **Anti-patterns**: Line 11 says "IF unable to trace manually" — what makes manual tracing impossible? "Long call chain" is not concrete enough.
- **Frontmatter**: VALID — name, description, argument-hint present.
- **Cross-skill refs**: CLEAN — no hard-coded skill names.
- **Completeness**: COMPLETE — four phases well-defined with instrumentation guidance.
- **Length**: THIN — 77 lines. Complete but could be richer.
- **Verdict**: REFACTOR
- **Specific fixes needed**:
  1. **ADD decision router at top** — move "IF an error occurs deep in execution" to before the heading.
  2. "Unable to trace manually" needs concrete threshold — call chain depth >10? Missing stack frames?
  3. "Bisect across tests" (line 12) is mentioned but not explained. Add brief guidance.
  4. Consider: "defense-in-depth is part of the fix" (line 76) is important but buried. Could be elevated.

---

### subagent-orchestration (306 lines)
- **Router**: YES — solid. Table format with specific situation → action mapping. Five parallel patterns well-documented.
- **Delta**: YES — "Orchestrator owns all cognition; subagents own only execution" is a clear delta statement.
- **Policy/Mechanism**: CLEAN — policy in decision router, mechanism in body.
- **Anti-patterns**: Line 80 says "high-stakes decisions" but doesn't define what "high-stakes" means. Could be more concrete.
- **Frontmatter**: VALID — name, description, when_to_use all present.
- **Cross-skill refs**: CLEAN — references are natural language.
- **Completeness**: COMPLETE — very comprehensive, covers orchestration patterns, self-review, automation layers, failure modes.
- **Length**: OK — 306 lines, appropriate for a core orchestration skill.
- **Verdict**: KEEP
- **Specific fixes needed**:
  1. "High-stakes" in line 387 needs concrete definition. "Architecture decisions, strategy selection" is helpful but could specify what makes something "high-stakes."
  2. Consider: the "Five Parallel Patterns" section (lines 136-219) could benefit from a summary table at the top for quick reference.

---

### update-docs (147 lines)
- **Router**: MISSING — no decision router at top. First content is heading then body text. The "IF code changes affect user-facing APIs" condition is in body, not at top.
- **Delta**: YES — "Not every code change needs documentation" is a clear delta statement. "Documentation must justify its existence" is the core principle.
- **Policy/Mechanism**: CLEAN — policy in body, mechanism well-defined.
- **Anti-patterns**: Line 9 says "user-facing APIs or workflows" — what constitutes "user-facing"? Internal refactors may or may not need docs. Line 13 "no uncommitted changes" is implementation detail.
- **Frontmatter**: VALID — name, description, argument-hint present.
- **Cross-skill refs**: CLEAN — no hard-coded skill names.
- **Completeness**: COMPLETE — multi-agent workflow well-defined, quality gates specified.
- **Length**: OK — 147 lines, appropriate for scope.
- **Verdict**: KEEP
- **Specific fixes needed**:
  1. **ADD decision router at top** — move the IF conditions before the heading.
  2. "User-facing" needs clearer definition. What specifically triggers documentation update? "Public API signatures changed", "user-visible behavior changed", "workflow steps changed"?
  3. Consider: this skill could benefit from a "documentation decision tree" — when does code change require docs update?

---

### write-concisely (62 lines)
- **Router**: MISSING — no decision router at top. First content is heading then body text. IF conditions are in body, not at top.
- **Delta**: YES — "Claude already knows these rules" is an honest delta statement. The skill exists to trigger application, not teach rules.
- **Policy/Mechanism**: CLEAN — policy in body, mechanism in principles.
- **Anti-patterns**: Line 8 says "documentation for human readers" — "human readers" is vague. "Clearer, stronger, more professional" are generic adjectives. "Active voice, positive form" are well-known but the skill states them without examples of the wrong/right pairs.
- **Frontmatter**: VALID — name, description, argument-hint present.
- **Cross-skill refs**: CLEAN — no hard-coded skill names.
- **Completeness**: PARTIAL — principles listed but application guidance is thin. "Do not enumerate which rules you applied" is a constraint, not guidance.
- **Length**: THIN — 62 lines. Could be richer with concrete application examples.
- **Verdict**: REFACTOR
- **Specific fixes needed**:
  1. **ADD decision router at top** — move IF conditions before heading.
  2. "Documentation for human readers" needs specificity — what specific user phrases trigger this? "Make this clearer", "improve the docs", "write docs for X"?
  3. Add 2-3 concrete wrong/right examples. "The code was written by John" vs. "John wrote the code" would make the active voice rule actionable.
  4. "Apply the full set of composition principles" — what specifically triggers "full set" vs. partial application?

---

## Priority Fixes (Top 5 per urgency)

### REWRITE Priority (Skills needing significant structural work)

1. **execute-plans** (593 lines) — Cross-skill brittle references (lines 14, 581-582 pointing to create-plans internals). Fix natural language references. Reduce length.
2. **plan-task** (604 lines) — Missing natural language triggers, relies only on flag parsing. Add "IF user says 'plan this task'" routing. Reduce length.
3. **analyse-problem** (67 lines) — Missing decision router entirely. Add IF/THEN at top.
4. **kaizen** (88 lines) — Missing decision router. Add IF/THEN at top before heading.
5. **root-cause-analysis** (64 lines) — Missing decision router. Add IF/THEN at top.

### REFACTOR Priority (Skills needing targeted fixes)

1. **create-subagents** (613 lines) — Reduce to ~450 lines. Trim body prompt philosophy, orchestration patterns sections.
2. **create-plans** (604 lines) — Reduce to ~450 lines. Trim context scan, what good looks like.
3. **implement-task** (568 lines) — Reduce to ~450 lines. Move usage walkthrough to reference.
4. **plan-do-check-act** (62 lines) — Add decision router at top.
5. **root-cause-tracing** (77 lines) — Add decision router at top.

### KEEP Priority (No or minor fixes needed)

1. **add-task** — Well-designed, keep as-is.
2. **code-review** — Well-designed, keep as-is.
3. **code-simplify** — Trim anti-patterns section (52 lines → ~20).
4. **subagent-orchestration** — Minor: define "high-stakes" more concretely.
5. **execute-prompts** — Strengthen trigger phrases in decision router.
6. **update-docs** — Add decision router at top.

---

## Cross-Cutting Observations

### Missing Decision Routers (5 skills)
These skills have no IF/THEN at top — the routing decision is buried in body text:
- analyse-problem
- kaizen
- plan-do-check-act
- root-cause-analysis
- root-cause-tracing
- update-docs

All of these have valid bodies but lack the preamble-level routing signal that makes trigger decisions unambiguous.

### Length Issues (8 skills >500 lines)
- create-subagents (613)
- create-plans (604)
- plan-task (604)
- execute-plans (593)
- implement-task (568)
- create-skills (512)

The 500-line rule is a heuristic, not a law. But these skills should apply the delta principle more aggressively to reduce mechanical length without losing substance.

### Cross-Skill Brittleness (1 skill)
execute-plans references `{baseDir}/references/orchestration-patterns.md` which is inside the create-plans skill. This creates a hard dependency. Use semantic reference: "see the orchestration patterns reference."

### Vague Trigger Phrases (Common pattern)
Many skills use generic terms where concrete phrases would be better:
- "analyzing code implementation" vs. specific user phrases
- "high-stakes work" vs. concrete criteria
- "user-facing" vs. specific change types
- "clear" vs. measurable threshold

### Thin Skills (6 skills <100 lines)
These could benefit from more substance:
- analyse (65 lines)
- analyse-problem (67 lines)
- ideation (65 lines)
- kaizen (88 lines)
- plan-do-check-act (62 lines)
- write-concisely (62 lines)

---

*Audit complete. Next: apply fixes prioritized by impact (cross-skill brittleness first, then missing routers, then length reduction).*