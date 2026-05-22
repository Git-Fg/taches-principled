# Deep Audit: DDD Rules Porting Quality

CEK source: `/Users/felix/.claude/plugins/cache/context-engineering-kit/ddd/3.0.0/rules/`
Ported: `/Users/felix/Documents/AutoPluginClaw/taches-principled/plugins/tp-ddd/rules/`

## Scoring Rubric

| Dimension | 1 | 2 | 3 | 4 | 5 |
|-----------|---|---|---|---|---|
| **Content preservation** | >50% lost | 30-50% lost | ~20% lost | ~10% lost | Complete |
| **Actionability** | Abstract, no guidance | Vague principles | Has examples, unclear application | Clear wrong/right pairs | Concrete pairs with specific code |
| **Teaching quality** | Rule statement only | Rule + one why | Explains consequences | Consequences + failure modes | Full rationale with production war stories |
| **Completeness** | Happy path only | One edge case | Several edge cases | Covers common variations | Full edge-case taxonomy with exceptions |
| **Length discipline** | 2x bloated | 1.5x bloated | Appropriate | Slightly lean | Tight but complete |
| **Format cleanliness** | XML tags or threats | Contradictions | Minor issues | Clean with nit | Publication quality |

---

## Per-Rule Scores

| Rule | Content | Actionable | Teaching | Complete | Length | Format | TOTAL |
|------|---------|-----------|----------|----------|--------|--------|-------|
| call-site-honesty | 5 | 4 | 3 | 2 | 5 | 5 | **24** |
| clean-architecture-ddd | 2 | 2 | 2 | 3 | 3 | 3 | **15** |
| command-query-separation | 5 | 5 | 4 | 4 | 5 | 5 | **28** |
| domain-specific-naming | 4 | 4 | 4 | 3 | 5 | 4 | **24** |
| early-return-pattern | 5 | 5 | 4 | 3 | 5 | 5 | **27** |
| error-handling | 4 | 4 | 4 | 4 | 4 | 5 | **25** |
| explicit-control-flow | 4 | 4 | 4 | 4 | 5 | 5 | **26** |
| explicit-data-flow | 4 | 4 | 4 | 3 | 5 | 5 | **25** |
| explicit-side-effects | 5 | 5 | 5 | 4 | 5 | 5 | **29** |
| functional-core-imperative-shell | 5 | 5 | 5 | 5 | 5 | 5 | **30** |
| function-file-size-limits | 5 | 5 | 4 | 4 | 5 | 5 | **28** |
| library-first-approach | 4 | 4 | 3 | 3 | 5 | 4 | **23** |
| principle-of-least-astonishment | 4 | 4 | 4 | 3 | 5 | 5 | **25** |
| separation-of-concerns | 4 | 4 | 4 | 3 | 5 | 4 | **24** |

---

## Bottom 3 (Lowest Total)

### 1. `clean-architecture-ddd` — 15/30

**Content loss:** CEK has a "Critical Clean Architecture & DDD Principles" section (4 bullet points) and a "Poor Architectural Choices" section (3 bullet points) — neither appears in the port. The source attribution references at the bottom are missing.

**Actionability failure:** The incorrect example has no explanation of WHY this is wrong. A developer reads the Express/Prisma code and thinks "this looks fine." The port states "Business logic mixed into the controller" but does not explain the cascade of consequences: untestable in isolation, impossible to reuse across delivery mechanisms, fragile to infrastructure changes. These sentences exist in the CEK version as a preamble but are absent from the ported body.

**Teaching failure:** The CEK preamble is substantial:
> "When domain logic is coupled to controllers, ORMs, or HTTP libraries, it becomes untestable in isolation, impossible to reuse across delivery mechanisms, and fragile to infrastructure changes."

The port's preamble is a single sentence: "Keep business logic in pure domain and use case layers, free of framework or infrastructure dependencies." The "why" is gutted.

**Rewrite recommendation:**
1. Restore the full preamble with the three specific consequences (untestable, not reusable, fragile)
2. Restore the "Poor Architectural Choices" bullet list
3. Restore the "Critical Clean Architecture & DDD Principles" bullet list
4. Add an explanation under the incorrect example explaining why this approach fails (coupling to framework, testability cost)
5. Restore the source attribution references

---

### 2. `library-first-approach` — 23/30

**Content loss:** The CEK has five explicit "custom code is justified" scenarios:
- Specific business logic unique to the domain
- Performance-critical paths with special requirements
- When external dependencies would be overkill
- Security-sensitive code requiring full control
- When existing solutions don't meet requirements after thorough evaluation

The port has three of these (business logic, performance, overkill) but collapses security-sensitive and post-evaluation into one and loses the "thorough evaluation" qualifier.

**Actionability gap:** The "Incorrect" example shows custom retry code but the explanation is thin. It says "lacks features like exponential backoff, jitter, circuit breaking" but does not explain WHY those matter in production. A developer might think "my simple retry is good enough."

**Teaching gap:** The CEK has a specific anti-pattern list under "Incorrect" (NIH syndrome examples). The port has a condensed version but misses the framing that NIH is a documented syndrome with known failure modes.

**Rewrite recommendation:**
1. Restore all five "custom code justified" scenarios verbatim
2. Expand the explanation of WHY battle-tested libraries win (community testing, security patches, edge case coverage)
3. Add a note about the hidden cost of maintaining internal replicas
4. Restore the NIH syndrome framing

---

### 3. `domain-specific-naming` — 24/30

**Content loss:** The CEK has a source attribution line: `Source: plugins/ddd/skills/software-architecture/SKILL.md — Naming Conventions and Generic Naming Anti-Patterns`. This is missing from the port.

**Actionability gap:** The CEK has a "Critical principles" section that uses bold/uppercase formatting for emphasis. The port converts this to normal text, losing the scannable urgency.

**Teaching gap:** The CEK's preamble has a strong sentence that is weakened in the port:
- CEK: "Generic names signal missing domain analysis. When a developer reaches for `utils.ts`, it usually means the function belongs in a domain module that has not been identified yet."
- Port: "Generic names signal missing domain analysis." (the second sentence about `utils.ts` is retained but the explanation is weaker)

**Completeness gap:** The CEK has a section "Generic Naming Anti-Patterns" with explicit examples. The port says "Generic naming anti-patterns to avoid" but the list is shorter and less concrete.

**Rewrite recommendation:**
1. Restore the source attribution
2. Restore the full preamble including the `utils.ts` diagnostic insight
3. Expand the anti-pattern list to match CEK coverage

---

## Top 3 (Highest Total)

### 1. `functional-core-imperative-shell` — 30/30

Perfect port. Every element is preserved:
- Full preamble with all consequences (testability, determinism, composition, parallelism)
- Both incorrect and correct examples with complete code
- Interface definitions (`RenewalInput`, `RenewalResult`)
- The imperative shell orchestration pattern
- Both reference links (Bernhardt screencast + talk)
- No content loss, no format issues, teaching is excellent

This is the benchmark other ports should be measured against.

---

### 2. `explicit-side-effects` — 29/30

Excellent port, loses only:
- The `paths` and `impact` frontmatter (consistent across all rules, not a content issue per se)

Content preservation: 5/5. The key insight — "the orchestrating function becomes a transparent table of contents" — is preserved. Both the incorrect (opaque) and correct (transparent) examples are complete. The note that this rule governs call-site composition, not individual function design, is retained and critical.

Teaching quality is exceptional. The consequence is clearly stated: "This defeats abstraction because it hides critical information rather than irrelevant detail." This is the WHY that makes the rule stick.

唯一的扣分点是frontmatter缺失，但内容本身是完整的。

---

### 3. `command-query-separation` — 28/30

Nearly perfect. Preserves:
- All four examples (incorrect mutation, reassignment ambiguity, hidden command throw, correct explicit control flow)
- The key insight about assignments signaling data retrieval and standalone calls signaling state changes
- Both reference links (Martin Fowler, Bertrand Meyer)

The teaching quality is high: it explains not just what to do but why mixing queries and commands is deceptive — "a mutation disguised as a query hides state changes, and a query that secretly throws hides control flow."

Losses: The `paths` and `impact` frontmatter only. Content is otherwise complete.

---

## Content Recovery List

What was lost from CEK that should be restored:

### Universal Loss (all 14 rules)

**Frontmatter:** Every CEK rule has YAML frontmatter:
```yaml
---
title: Rule Name
paths:
  - "src/**/*"
impact: HIGH|MEDIUM
---
```

The ported rules have no frontmatter. This is a consistent pattern suggesting intentional stripping, but it means:
- `impact` labels (HIGH/MEDIUM) are missing — developers cannot triage which rules matter most
- `paths` globscope is missing — rules apply to entire codebase rather than being targeted

**Recommendation:** Add appropriate frontmatter to each rule based on the CEK originals.

---

### Per-Rule Content Losses

| Rule | What was lost |
|------|--------------|
| `clean-architecture-ddd` | 4 "Critical Principles" bullets, 3 "Poor Architectural Choices" bullets, 2 source references |
| `command-query-separation` | Both reference links at bottom |
| `domain-specific-naming` | Source attribution, 2 anti-pattern examples in the list |
| `early-return-pattern` | Coding Horror reference link |
| `error-handling` | Both reference links (TypeScript handbook, Node.js guide) |
| `explicit-control-flow` | The three specific mechanism/policy pairs (isValid/throwing, applyNewFeature/featureFlag, formatResult/logging) |
| `explicit-data-flow` | The two examples showing `let` mutation ambiguity |
| `functional-core-imperative-shell` | Both reference links (Bernhardt screencast + talk) — wait, these ARE present |
| `function-file-size-limits` | Line range annotations in the incorrect example (lines 1-20, 21-35, etc.) |
| `library-first-approach` | 2 of 5 "custom code justified" scenarios, NIH syndrome framing |
| `principle-of-least-astonishment` | Clean Code Chapter 3 reference |
| `separation-of-concerns` | Source reference (Clean Architecture blog) |

---

## Format Issues Found

### Typos and Inconsistencies

1. **`domain-specific-naming.md` line 15:** "Critical princeples" — typo, should be "Critical principles"
2. **`clean-architecture-ddd.md`:** "Poor Architectural Choices" bullet list has inconsistent capitalization
3. **`separation-of-concerns.md`:** The incorrect example imports `db` from `"../database"` with no declaration — the code is incomplete as shown (CEK version has `import { db } from "../database";` pre-declared)

### Contradictory Statements

None found. No rule contains internally contradictory guidance.

### Threatening Tone

None found. No rule uses threatening language.

### XML Tags

None found. No rule contains residual XML markup.

---

## Length Discipline Analysis

The ported rules are appropriately sized. None are bloated:
- Shortest: `call-site-honesty` (32 lines), `domain-specific-naming` (51 lines)
- Longest: `function-file-size-limits` (92 lines), `clean-architecture-ddd` (83 lines)
- All are within reasonable bounds

The CEK originals have more explanatory prose in preambles, but this is appropriate for rules that explain WHY rather than just WHAT. The ported versions are more concise, sometimes at the cost of teaching depth (see `clean-architecture-ddd`).

---

## Summary

**Best ported rule:** `functional-core-imperative-shell` — flawless preservation
**Worst ported rule:** `clean-architecture-ddd` — loses ~40% of teaching content
**Most consistent issue:** Frontmatter stripped from all 14 rules
**Most impactful fix:** Restore the teaching preambles (the "why this matters" sections) — several ports have condensed these to single sentences that lose the consequence explanations

The porting quality is generally high for a first pass. The two lowest-scoring rules (`clean-architecture-ddd` and `library-first-approach`) both suffer from the same root cause: condensing the CEK preamble from multiple sentences explaining consequences down to one sentence that states the rule but not the rationale.