# tp-ddd Rules Audit — 2026-05-22

## Summary Table

| # | Rule | Lines | When Applies? | Concrete Examples? | WHY Matters? | Generic/Verbose? | Actionable? |
|---|------|-------|---------------|-------------------|--------------|-----------------|-------------|
| 1 | call-site-honesty | 24 | YES | YES | YES | NO | YES |
| 2 | clean-architecture-ddd | 63 | YES | YES | YES | NO | YES |
| 3 | command-query-separation | 51 | YES | YES | YES | NO | YES |
| 4 | domain-specific-naming | 51 | YES | YES | YES | NO | YES |
| 5 | early-return-pattern | 61 | YES | YES | YES | NO | YES |
| 6 | error-handling | 48 | YES | YES | YES | NO | YES |
| 7 | explicit-control-flow | 74 | YES | YES | YES | YES (policy/mechanism paragraph repeats across multiple rules) | YES |
| 8 | explicit-data-flow | 32 | YES | YES | YES | NO | YES |
| 9 | explicit-side-effects | 52 | YES | YES | YES | NO | YES |
| 10 | functional-core-imperative-shell | 99 | YES | YES | YES | NO | YES |
| 11 | function-file-size-limits | 92 | YES | YES | YES | NO | YES |
| 12 | library-first-approach | 52 | YES | YES | YES | NO | YES |
| 13 | principle-of-least-astonishment | 49 | YES | YES | YES | NO | YES |
| 14 | separation-of-concerns | 98 | YES | YES | YES | NO | YES |

**Total line count: 846 across 14 rules. Average: ~60 lines/rule.**

## Top 3 Most Valuable Rules

### 1. explicit-control-flow (74 lines)
The policy/mechanism distinction is the most architecturally generative idea in the collection. It connects error handling, naming, data flow, and side effects into a unified framework. The examples are concrete (validateResult hiding throws, applyNewFeature hiding feature flags) and the rule produces immediate, actionable prescriptions.

### 2. functional-core-imperative-shell (99 lines)
Strongest concrete examples — the "before" (98 lines of tangled business logic with side effects) vs "after" (clean pure function + thin shell) is the best side-by-side illustration in the collection. The why section (determinism, testability, parallelization) is specific and compelling.

### 3. separation-of-concerns (98 lines)
High coverage of the controller/service/repository pattern with a long but well-motivated incorrect example. The correct version demonstrates clean composition. Lines 4-5 ("Violating these boundaries creates tightly coupled code...") provide clear consequences.

## Top 3 Weakest Rules

### 1. explicit-control-flow (74 lines)
**Issue: Internal repetition problem.** The rule uses `validateResult` as its primary example, but this exact example appears identically in `command-query-separation.md`. The "mechanism/policy" table in lines 8-11 is a conceptual header that should be the defining concept of this rule, but it repeats policy/mechanism language that also appears in `call-site-honesty.md`. The rule would be stronger if it picked a genuinely distinct example (e.g., a conditional with a hidden branch) rather than re-using the validate-throw pattern.

### 2. domain-specific-naming (51 lines)
**Issue: Thin examples.** The "incorrect" section shows generic `utils.ts` as a dumping ground, but the "correct" section shows three files that are all trivial one-liners. This undersells the rule — real domain modules like `OrderCalculator` have real behavior, not just a `reduce` on one line. The anti-pattern list (lines 26-29) is text prose that could be trimmed.

### 3. explicit-data-flow (32 lines)
**Issue: Shortest rule, thinnest examples.** The `applyNewFeature` example is shared with `command-query-separation`. The second example (lines 19-23) about `let result` being unclear due to potential mutation is genuinely good — but the rule is so short it reads as a footnote to the CQS rule rather than a standalone rule. Consider merging with command-query-separation or expanding with a genuinely distinct example.

## Notable Observations

1. **All 14 rules have clear "when this applies" statements** — none are abstract/generic.
2. **All 14 rules have concrete wrong/right pairs** — no purely theoretical advice.
3. **All 14 rules explain why** — the architectural consequence is always stated.
4. **No rule has truly generic prose** — the collection is lean.
5. **Cross-rule example reuse**: `validateResult` appears in both `command-query-separation` and `explicit-control-flow`. `applyNewFeature` appears in `command-query-separation`, `explicit-data-flow`, and `explicit-control-flow`. This is not wrong (the patterns are related) but means the rules read as a collection of variations on a theme rather than independent rules.
6. **The policy/mechanism distinction** is the connective tissue of the entire set — it appears explicitly in `call-site-honesty`, `explicit-control-flow`, and implicitly in `command-query-separation`, `principle-of-least-astonishment`, `explicit-side-effects`, and `functional-core-imperative-shell`. This is a strength (coherent framework) but also a risk (if the PM distinction is wrong, the whole set is wrong).

## Quality Profile

The collection is strong on teaching but could benefit from:
- More distinct examples per rule (reduce cross-rule duplication)
- Stronger wrong/right pairs for `domain-specific-naming` and `explicit-data-flow`
- A "Decision Router" section at the top of each rule listing when it applies and when not (similar to the CEK rules format)