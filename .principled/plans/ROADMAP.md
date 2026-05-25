# Roadmap: Knowledge Extraction & Local Skill Integration

## Phase Structure

Each phase enhances existing skills with knowledge from references — no new skills created.

### Phase 1: Knowledge Extraction from References
Enhance existing skills with net-new patterns from ~/Documents/AutoPluginClaw/references/

**Depends on:** Nothing (parallel to other phases)

**Tasks:**
1. Enhance tool-design with ai-cli patterns
   - Source: references/ai-cli/SKILL.md
   - Patterns: zero-transformation returns, hierarchical --help, token efficiency
   - Target: plugins/taches-principled/skills/tool-design/SKILL.md

2. Enhance claude-headless with MCP testing patterns
   - Source: references/claude-headless/SKILL.md
   - Patterns: two-phase MCP testing, hook development, effective context ceiling
   - Target: plugins/taches-principled/skills/claude-headless/SKILL.md

3. Enhance subagent-orchestration with effective context ceiling
   - Source: references/subagent-orchestration/SKILL.md
   - Pattern: effective context window ~147K-152K tokens (not 200K)
   - Target: plugins/taches-principled/skills/subagent-orchestration/SKILL.md

**Quality gate:** All enhanced skills pass self-critique (teaching value preserved)

---

### Phase 2: Local Skill Integration
Integrate skill-creator from ~/.claude/skills/

**Depends on:** Nothing (parallel to Phase 1)

**Tasks:**
1. Copy skill-creator from ~/.claude/skills/skill-creator/ to plugins/taches-principled/skills/skill-creator/
2. Adjust baseDir references
3. Verify trigger distinctiveness from create-skills
4. Self-critique pass

**Quality gate:** skill-creator routes distinctly from create-skills

---

### Phase 3: Existing Skill Enhancement — ddd + API Mode
Enhance ddd with REST API contract mode

**Depends on:** Phase 1 complete

**Tasks:**
1. Add API mode to ddd decision router
2. Cover: REST conventions, breaking changes, versioning, response shapes
3. Cross-reference with refine's Contracts Reviewer
4. Verify routing clarity

**Quality gate:** API mode distinct from architecture/quality/transparency modes

---

### Phase 4: CLAUDE.md & Documentation Sync
Sync all documentation with 0.6.0 state

**Depends on:** Phases 1-3 complete

**Tasks:**
1. Update CLAUDE.md:
   - Version 0.5.0 → 0.6.0 ✓ DONE
   - Add skill-creator integration notes
   - Add ddd API mode notes
   - Verify no outdated references

2. Update README.md:
   - Sync with new skill count (21 skills)
   - Add new skill descriptions

3. Verify CHANGELOG.md:
   - 0.6.0 entry for Phase 0-3 work ✓ DONE

**Quality gate:** No stale references, version accurate

---

### Phase 5: Quality Verification & Commit
Final verification and commit

**Depends on:** Phase 4 complete

**Tasks:**
1. Run subagent audit of all changes
2. Verify no broken cross-references
3. Commit with proper message

---

## Execution Order

```
Phase 1 (Knowledge Extraction) ←─ PARALLEL ──→ Phase 2 (Skill Creator)
        ↓                                          ↓
Phase 3 (ddd + API Mode)                      ←─ DEPENDS ON 1 & 2 ──→
        ↓
Phase 4 (Documentation Sync) ←─ DEPENDS ON 3 ─→
        ↓
Phase 5 (Quality + Commit)  ←─ DEPENDS ON 4 ─→
```

## Quality Gates (Every Phase)

Before marking a phase complete:
- [ ] Enhanced skill has decision router (if hub)
- [ ] Teaching value preserved (judgment, not just procedure)
- [ ] Trigger phrases distinct from other skills
- [ ] baseDir references used (no hard paths)
- [ ] No broken cross-references
- [ ] Self-critique passed or issues documented
- [ ] CHANGELOG entry added

## Current State

| Phase | Status |
|-------|--------|
| Phase 0 (Foundation) | COMPLETED (0.5.0) |
| Phase 1-3 (Knowledge + Integration) | PENDING |
| Phase 4 (Documentation) | PENDING |
| Phase 5 (Quality + Commit) | PENDING |

After completion: **21 skills** (within optimal 22-28 range)