# Context Management for Skills

## Sections
- [Core Principle](#core-principle)
- [Context Competition](#context-competition)
- [Thresholds](#thresholds)
- [What Stays in SKILL.md](#what-stays-in-skillmd)
- [What Goes in References](#what-goes-in-references)
- [Skill Self-Contained Rule](#skill-self-contained-rule)
- [Split Signals](#split-signals)

---

Skills share the context window with everything else. Every token competes.

---

## Core Principle

**Skills are on-demand加载.** The SKILL.md body loads into conversation only when triggered. Reference files (`references/`) load only when explicitly accessed.

This means:
- Essential principles → SKILL.md (always available)
- Details, examples, domain knowledge → `references/` (loaded on demand)

---

## Context Competition

When Claude Code starts a session, the context window contains:

1. User's prompt and conversation history
2. Loaded skills (SKILL.md bodies)
3. Project CLAUDE.md and rules
4. MCP server definitions
5. Tool definitions

**A skill that consumes too much context degrades the entire session.**

---

## Thresholds

| Metric | Limit | Why |
|--------|-------|-----|
| Description length | 150 chars max | Truncates at 1,536 combined with `when_to_use` |
| when_to_use length | 200 chars max | Longer = context bloat, not better routing |
| Skill body | 500 lines max | Beyond = principle dilution; split or reference |
| Tools allowed | 7 max (Miller's number) | Beyond = coordination overhead |

---

## What Stays in SKILL.md

- Policy (when to trigger)
- Core mechanism (key insight)
- Anti-Patterns (concrete wrong/right pairs)
- Numeric thresholds with rationale
- One good example, not every edge case

---

## What Goes in References

- Extended examples
- Domain-specific patterns
- Platform-specific details
- Full JSON schemas
- Workflows (step-by-step procedures)

---

## Skill Self-Contained Rule

A skill must be loadable and useful on its own, without any other skill being present.

Cross-skill references create brittle dependency graphs. When skill X is renamed or archived, every skill referencing X must be updated.

**Exception:** Skills explicitly identified as orchestrators (name ends in `-orchestrator`) may reference other skills because their job IS composition.

---

## Split Signals

If a skill needs:
- >7 tools
- >500 lines in body
- Multiple distinct concerns

→ Split into focused skills. Each skill has one job.