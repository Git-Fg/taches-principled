# Brief: Enhance Taches Principled with Knowledge & Local Skills

## Vision

Complete the taches-principled marketplace by:
1. Extracting net-new value from references folder into existing skills
2. Integrating the high-value skill-creator skill from ~/.claude/skills/
3. Enhancing existing skills to fill remaining gaps (ddd + API mode)
4. Syncing CLAUDE.md with new state and refining rules

## Why

The marketplace now has 20 solid skills after Phase 3 consolidation. However:
- **5,147 lines of reference content** in references/ folder contains knowledge not yet in skills
- **skill-creator** scores 9.0/10 — teaches meta-level skill authoring patterns the plugin version lacks
- **ddd lacks API mode** — REST contract design is a gap
- **CLAUDE.md and rules need syncing** with the 0.6.0 state

## What Already Exists

**20 skills in marketplace** (within optimal 22-28 range)

**References folder** (~5,147 lines) — most already covered by skills:
- multi-agent-patterns → subagent-orchestration ✅
- subagent-orchestration → subagent-orchestration ✅  
- skill-creator → skill-creator (local) → integrate
- claude-headless → claude-headless ✅
- ai-cli → net-new value for tool-design enhancement
- rules-creator → keep locally (overlaps with plugin)

**Net-new value to extract:**
1. ai-cli patterns → enhance tool-design
2. MCP testing two-phase pattern → enhance claude-headless
3. Effective context ceiling (147K-152K) → enhance subagent-orchestration
4. Reliability metrics table → enhance relevant skills

**Remaining local skills:**
- skill-creator (9.0/10) → INTEGRATE
- rules-creator (8.5/10) → Keep locally
- All others → Keep locally (below threshold)

**Critical gaps filled:**
- Security ✅ (0.6.0)
- Test ✅ (0.6.0)
- API Design → Enhance ddd with REST mode
- Review → Keep in refine (no change)

## Core Goal

> Enhance the marketplace with net-new knowledge WITHOUT adding skills. Strengthen existing skills. Stay within 22-28 range.

**Principle:** Extract value from references into existing skills rather than creating new skills. This avoids routing conflation and token cost while capturing the knowledge.

## Design Decisions

### No New Skills

The plan does NOT create new skills. It enhances existing ones:
- tool-design gets ai-cli patterns (enhancement, not new skill)
- claude-headless gets MCP patterns (enhancement)
- subagent-orchestration gets effective context ceiling (enhancement)
- ddd gets API mode (mode addition, not new skill)

### Skill Creator Integration

skill-creator from ~/.claude/skills/ integrates as a standalone skill:
- Unique teaching: trigger optimization, context:fork patterns, hooks lifecycle
- Does NOT replace plugin's create-skills (different angle)
- Complements: plugin version is surface-level, local version teaches methodology

### CLAUDE.md Sync

After all enhancements:
- Update version references (0.5.0 → 0.6.0) ✓ DONE
- Add skill-creator integration notes
- Add ddd enhancement notes
- Ensure no outdated references

## What Success Looks Like

1. Existing skills enhanced with net-new patterns from references
2. skill-creator integrated as 21st skill
3. ddd has REST API mode
4. CLAUDE.md synced with 0.6.0 state
5. README.md consistent
6. No new skills created (stays within range)