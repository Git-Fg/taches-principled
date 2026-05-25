# BRIEF: Archive-Plan Skill + Quick Fixes (v0.6.0 → v0.7.0)

## Vision

Close the plan lifecycle loop. After create-plans → execute-plans, provide a closure mechanism that archives artifacts and condenses learnings into a cross-session knowledge base. Fix version inconsistencies.

## Problem

- No plan→execute→archive chain — plans pile up without closure
- Scratchpad learnings are lost between sessions
- No knowledge accumulates across planning cycles
- marketplace.json at 0.5.0 while plugin.json at 0.6.0 (pre-existing mismatch)
- tp-tdd plugin.json at 0.2.0 while siblings at 0.3.0

## Scope

### In scope
- New `archive-plan` skill (SKILL.md + 1 reference + 1 template)
- New `/archive` command
- Integration with execute-plans (archive suggestion after SUMMARY.md)
- Integration with whats-next command (archive reference)
- Version bump: taches-principled 0.6.0 → 0.7.0
- marketplace.json aligned to 0.7.0
- Quick fix: tp-tdd version 0.2.0 → 0.3.0

### Out of scope
- Separate archive plugin (archive is a lifecycle stage, not a domain)
- Agent/workflow files (skill body teaches everything; reuse existing plugin agents)
- Pattern mining (v0.7.1+)
- MKT-002 (missing agents in simple plugins — not needed, skills suffice)
- MKT-007 (plugin dependencies — not a real plugin manifest field)
- MKT-008 (brittle skill references — already fixed with CONTRAST sections)
- tp-ddd version (auditor was wrong — it already has version 0.3.0)
- Auto-trigger mechanism (impossible per Claude Code architecture — skills cannot invoke other skills)

## Constraints

- Follow project conventions: {baseDir} paths, no cross-skill file references, no inline tool lists
- Skill body under 300 lines
- Command body: plain text, 1-3 sentences, no markdown
- No auto-trigger — suggest via execute-plans only, user explicitly invokes /archive
- Archive uses `.principled/attic/` (existing convention) not new `.principled/archive/`
- Learnings append to `.principled/memory/learnings.md` (consistent with memory purpose)
- CONTRAST with refine MEMORIZE: MEMORIZE captures general insights from sessions; archive-plan captures plan-specific learnings and bundles plan artifacts

## Success Criteria

1. `/archive` command triggers archive-plan skill
2. Archive bundles created at `.principled/attic/{milestone}/{plan}/`
3. Learnings appended to `.principled/memory/learnings.md`
4. whats-next command includes archive reference when available
5. execute-plans suggests archive after SUMMARY.md creation
6. Version bumped to 0.7.0 in both plugin.json and marketplace.json
7. tp-tdd version aligned to 0.3.0
8. No regressions in existing skills/commands
