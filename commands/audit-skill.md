---
description: Audit a skill for effectiveness and principle compliance
argument-hint: <skill-path>
---

Evaluate the skill at $ARGUMENTS.

## Goal
Determine if this skill will be effective when invoked. Score each dimension, then provide actionable recommendations.

## Evaluation Rubric

For each criterion, score 1-5 and provide evidence:

| Criterion | Weight | Score (1-5) | Evidence |
|-----------|--------|-------------|----------|
| Description Clarity | 0.20 | | |
| Routability | 0.25 | | |
| Example Quality | 0.20 | | |
| Frontmatter Completeness | 0.15 | | |
| Body Clarity | 0.20 | | |

**Scoring guide:**
- 5 = Excellent — exceeds standard, no changes needed
- 4 = Good — meets all requirements, minor polish only
- 3 = Adequate — acceptable, some improvements beneficial
- 2 = Below average — significant issues need fixing
- 1 = Poor — fundamental problems, rewrite recommended

**Default score is 2.** Upward deviation requires justification.

### Criterion Definitions

**Description Clarity (0.20)**
Does the `description` field state the skill's purpose in one clear sentence? Is the trigger condition specific enough to avoid false positives?

**Routability (0.25)**
Will Claude recognize when to invoke this skill? Are trigger keywords specific and front-loaded? Is `when_to_use` specific rather than generic?

**Example Quality (0.20)**
Do examples show the pattern in practice? Are they concrete (not hypothetical)? Do anti-pattern examples show what's wrong and why?

**Frontmatter Completeness (0.15)**
Does it have `name`, `description`, `when_to_use`? Are frontmatter fields using only documented fields (no made-up fields)?

**Body Clarity (0.20)**
Is the skill body concise? Does it teach principles rather than procedures? Are there clear anti-patterns?

### Anti-Patterns to Check

- Vague description: "Helps with coding" (should be specific)
- Generic name: "helper" vs "security-auditor"
- Missing when_to_use field
- Overloaded skill doing multiple things
- Body that reads like a procedure rather than principles
- No examples or only hypothetical examples

### Output Format

```markdown
## Overall Score
X.X / 5.0 (weighted average)

## Findings

### [Criterion Name]
**Score:** X/5
**Evidence:** [specific quote or observation]
**Recommendation:** [specific actionable change]

## Summary
[1-2 sentence assessment of overall skill quality]

## Specific Changes Recommended
1. [exact change 1 with before/after]
2. [exact change 2 with before/after]
```
