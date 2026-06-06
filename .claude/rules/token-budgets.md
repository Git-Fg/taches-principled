---
name: token-budgets
description: Silent truncation is the primary quality failure mode. Budgets are hard limits.
---

# Rule: MUST keep loaded content under silent truncation threshold

**Why:** When total loaded SKILL.md content approaches ~10,000 tokens, earlier loaded skills are silently truncated. The model remembers the opening and closing, but invents the middle. This failure mode is silent and devastating.

## Rule

- Hub skills: <500 tokens (router only, no domain logic)
- Domain skills: <2,000 tokens each
- Total loaded context: <10,000 tokens for all loaded skills + references
- Any single skill must not exceed 5,000 tokens (official ceiling)
- Craft as if Claude starts zero-context: every skill body must standalone

## Verification

When total loaded content nears 10,000 tokens: load fewer skills simultaneously (max 2-3), move deep content to `references/` (loaded on imperative citation only).

## Bad / Good

**Bad:** Hub at 4,000 tokens + Rust domain at 3,000 + Pharma domain at 3,000 = 10,000 tokens — truncation begins silently.
**Good:** Hub at 400 tokens + domain at 1,800 + domain at 1,600 = 3,800 tokens — well within safe range.

**Bad:** Inlining 5 reference files worth of mechanism content into SKILL.md body.
**Good:** SKILL.md is pure router (<500 tokens); `references/` contain mechanism, loaded on imperative citation only.
