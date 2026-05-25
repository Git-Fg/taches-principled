# Roadmap: CEK Plugin Integration

## Phase Structure

The integration is organized into 7 phases, each producing a self-contained set of skills that are individually usable and cumulatively synergistic.

### Phase 0: Foundation — Marketplace Structure
Create the plugin marketplace structure under `.claude-plugin/` and establish the integration patterns.
- **Depends on**: Nothing
- **Produces**: Plugin manifests, skill scaffolding, reference index templates

### Phase 1: Reflexion — Reflection & Self-Improvement
Port reflexion (reflect, critique, memorize) — the thinnest, cleanest CEK plugin. Proof of concept for integration patterns.
- **Depends on**: Phase 0
- **Produces**: reflect, critique, memorize skills
- **Synergy with**: kaizen, fpf (reflection feeds improvement)

### Phase 2: Kaizen — Continuous Improvement
Port kaizen (analyse, why, cause-and-effect, pdca, root-cause-tracing, kaizen general). Heavily trim to fit taches-principled style.
- **Depends on**: Phase 1 (mirrors reflexion in improvement cycle)
- **Produces**: 7 kaizen skills (some merged)
- **Synergy with**: reflexion (improve → reflect → improve)

### Phase 3: FPF — First Principles Framework — NOT EXECUTED
Port fpf (query, status, reset, actualize, decay, propose-hypotheses). Clean format, minimal changes needed.
- **Depends on**: Nothing
- **Produces**: 6 fpf skills (tp-fpf plugin)
- **Synergy with**: reflexion, kaizen (reasoning backbone)

### Phase 4: Review & Docs — NOT EXECUTED (merged to root)
Port review (review-pr, review-local-changes + 6 agents) and docs (update-docs, write-concisely).
- **Depends on**: Phase 0
- **Produces**: 4 skills, agents inlined — NOW ROOT-LEVEL (reflexion, kaizen, review, docs merged to root)
- **Synergy with**: sadd, sdd (review gates execution)

### Phase 5: Git & TDD — NOT EXECUTED (separate plugins)
Port git (7 skills) and tdd (3 skills). Consolidate git workflow.
- **Depends on**: Phase 0
- **Produces**: 10 skills — NOW tp-git (7 skills) + tp-tdd (3 skills) as separate plugins
- **Synergy with**: review, sdd (tooling chain)

### Phase 6: SADD — NOT EXECUTED (tp-sadd has 5 skills)
Port sadd (10 skills) — the biggest phase. Extract common meta-judge pattern into a shared reference. Reduce 10,000 lines to ~5,000.
- **Depends on**: Phases 0-5 (heavy consumer of review, tdd patterns)
- **Produces**: ~10 sadd skills — ACTUAL: tp-sadd has 5 skills (judge, do-in-steps, do-in-parallel, judge-with-debate, launch-sub-agent)
- **Synergy with**: sdd, tdd (judge → implement → test)

### Phase 7: SDD — NOT EXECUTED (tp-sdd re-created with 5 skills)
Port sdd (brainstorm, add-task, create-ideas, plan-task, implement-task). Integrates with planning hierarchy.
- **Depends on**: Phase 6 (sadd provides verification for sdd)
- **Produces**: 5-6 sdd skills — ACTUAL: tp-sdd has 5 skills, re-created after original plan
- **Synergy with**: entire ecosystem (SDD is the uppermost layer)

### Phase 8: DDD & Tech-Stack — NOT EXECUTED (tp-ddd separate)
Port ddd rules and tech-stack rules as `.claude/rules/` files, not skills. These are always-active guardrails.
- **Depends on**: Phase 0
- **Produces**: Rules files, no skills — ACTUAL: tp-ddd as separate plugin
- **Synergy with**: all (rules improve code quality across all skills)

## Execution Order

```
Phase 0 (Foundation) — COMPLETED
  ├── Phase 1 (Reflexion) — COMPLETED
  │     └── Phase 2 (Kaizen) — COMPLETED
  │           └── Phase 3 (Hub Consolidation) — COMPLETED (2026-05-24)
  │                 ├── refine hub (5 modes) — absorbed reflexion + write-concisely
  │                 ├── subagents hub (2 modes) — absorbed create-subagents
  │                 ├── tp-sadd consolidated (5→1), tp-git (4→1)
  │                 ├── tp-fpf consolidated (3→1), tp-ddd (3→1)
  │                 └── 34 skills → 20 skills (41% reduction)
  └── Phase 4 (Audit Fixes): Documentation staleness + agent quality
  ├── Phase 4 (FPF) — FOLDED into Phase 3 consolidation
  ├── Phase 5 (Review & Docs) — FOLDED into Phase 3 consolidation
  ├── Phase 6 (Git & TDD) — FOLDED into Phase 3 consolidation
  ├── Phase 7 (SADD) — FOLDED into Phase 3 consolidation
  └── Phase 8 (SDD/DDD) — FOLDED into Phase 3 consolidation
```

Phases 0, 1, 2, 3 completed. Phases 4-8 were planned but not executed as separate phases — their content was consolidated into hubs during Phase 3. Current state: 5 marketplace plugins (tp-ddd, tp-fpf, tp-git, tp-sadd, tp-tdd) each with 1 hub skill, plus 15 root-level skills. Total: 20 skills.

## Quality Gates (Every Phase)

Before marking a phase complete:
- [ ] All skills have decision routers
- [ ] No XML tags remain (use markdown headings)
- [ ] No threatening/unprofessional language
- [ ] No hard cross-skill file paths (use semantic descriptions)
- [ ] Delta principle applied (skill says only what differs)
- [ ] Line count reduced vs. CEK original (eliminate duplication)
- [ ] Standalone usable (read `SKILL.md` alone → you know what to do)
- [ ] Policy/mechanism separation (policy in skill, mechanism in reference)
- [ ] CHANGELOG.md entry
