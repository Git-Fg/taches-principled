# BRIEF: rules-orchestration Skill (v0.8.0)

## Vision

A self-contained skill that manages the CLAUDE.md + `.claude/rules/` lifecycle — analyzes conversations for rule-worthy insights, synthesizes proposals, integrates into the rules system, and maintains quality. Complements `learn` (captures to memory) by integrating durable learnings into committed rules.

## Problem

- Insights from skill execution (conventions, anti-patterns, decisions) are lost or manually transcribed
- CLAUDE.md grows bloated without systematic trimming
- No bridge between `learn`/memory captures and the rules system
- Rules aren't updated when new patterns emerge from work

## Scope

### In scope
- New `rules-orchestration` skill (SKILL.md)
- 3 agents: rules-analyzer, rules-auditor, rules-integrator
- 2 references: rule-writing-guide, rule-taxonomy
- ANALYZE, ADD, RESTRUCTURE, REVIEW, SYNC modes
- Integration with existing `learn` command (memory → rules bridge)
- Template: rule-proposal.md

### Out of scope
- New agents subdirectory — reuse existing plugin-level agents
- Scripts directory — validation done via agent review
- Multiple template files — single rule-proposal.md template
- Auto-trigger after skill execution — skills cannot invoke skills
- Modifying managed/enterprise rules at system paths

## Constraints

- Skill body under 300 lines (hub skill with decision router)
- Agents use existing plugin-level agent definitions, not inline subagents
- `{baseDir}` syntax for skill-internal references
- CONTRAST with learn: MEMORIZE captures to memory; this integrates into rules
- Rules are files — use filesystem as source of truth, not message passing

## Success Criteria

1. `/rules-orchestration` command triggers the skill
2. ANALYZE mode extracts actionable insights from conversation/skill output
3. RESTRUCTURE mode audits and reorganizes existing rules without data loss
4. ADD mode creates valid path-scoped rules with proper frontmatter
5. All changes git-committed with conventional messages
6. No managed/enterprise rules modified
7. Version bumped to 0.8.0
