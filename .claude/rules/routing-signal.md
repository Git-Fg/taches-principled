---
name: routing-signal
description: Skill metadata must route correctly within 200 chars. Truncation and overlap are the primary failure modes.
---

# Rule: MUST front-load trigger phrases within 200 chars, then stop

**Why:** Metadata-only gate — Claude routes based exclusively on the 200-char prefix of `description`. Anything later is silently truncated in high-context sessions. Methodology leaking into description causes misrouting or silent truncation.

## Rule

- Skill `description` ≤200 chars, trigger phrases in first 200 chars.
- Use user vocabulary, not technical methodology (no "A3", "TDD", "CQRS").
- `when_to_use` ≤200 chars. Combined ≤1536 chars.
- Adjacent-domain skills must have mutually exclusive trigger sets.
- CONTRAST section required for adjacent domains.

## Clarify vs Act (resolves contradiction with Actionability)

**Act immediately** when: user request is clear and has sufficient info.
**Clarify before acting** when: ambiguity would materially change the output (e.g., "fix this" without specifying which file).

## Bad / Good

**Bad:** "Uses A3 methodology to document root causes." — methodology leaks, no trigger phrase until mid-sentence.
**Good:** "Find and solve recurring problems or failures." — user vocabulary, trigger-loaded, no jargon.

**Bad:** "Complete test lifecycle — Red-Green-Refactor TDD" — methodology in description.
**Good:** "Write tests first, then implementation." — user vocabulary, clear trigger.

**Bad:** Two skills whose descriptions can be paraphrased to mean the same thing — they will misroute.
**Good:** If "compare options" could match either `fpf` or `sadd`, reword: `fpf` → "reason from first principles", `sadd` → "generate and judge competing solutions".
