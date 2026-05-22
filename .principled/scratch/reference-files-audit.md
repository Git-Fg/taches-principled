# Reference Files Audit — taches-principled

**Audit date:** 2026-05-22
**Total reference files audited:** 61

---

## Table: File Path | Parent Skill | Referenced by SKILL.md? | Orphaned? | Bloated? | Verdict

| File Path | Parent Skill | Ref'd? | Orphaned? | Bloated? (>300) | Verdict |
|-----------|-------------|--------|----------|-----------------|---------|
| `skills/code-simplify/references/language-patterns.md` | code-simplify | YES | No | YES (335L) | WARN: bloated — large but dense with examples |
| `skills/code-simplify/references/simplification-scope.md` | code-simplify | YES | No | No | OK |
| `skills/create-plans/references/checkpoints.md` | create-plans | YES | No | No | OK |
| `skills/create-plans/references/cli-automation.md` | create-plans | YES | No | No | OK |
| `skills/create-plans/references/milestone-management.md` | create-plans | YES | No | YES (490L) | WARN: bloated — consider split or inlining |
| `skills/create-plans/references/orchestration-patterns.md` | create-plans | YES | No | No | OK |
| `skills/create-plans/references/plan-format.md` | create-plans | YES | No | No | OK |
| `skills/create-plans/references/race-framework.md` | create-plans | YES | No | No | OK |
| `skills/create-plans/references/scope-estimation.md` | create-plans | YES | No | No | OK |
| `skills/create-plans/references/task-model-fit.md` | create-plans | YES | No | No | OK |
| `skills/create-skills/references/context-management.md` | create-skills | YES | No | No | OK |
| `skills/create-skills/references/cross-skill-discovery.md` | create-skills | YES | No | No | OK |
| `skills/create-skills/references/skill-self-testing.md` | create-skills | YES | No | No | OK |
| `skills/create-skills/references/trigger-benchmark.md` | create-skills | YES | No | No | OK |
| `skills/create-skills/references/trigger-testing.md` | create-skills | YES | No | No | OK |
| `skills/create-subagents/references/automation-layers.md` | create-subagents | YES | No | No | OK |
| `skills/create-subagents/references/context-management.md` | create-subagents | YES | No | YES (448L) | WARN: bloated + BROKEN cross-refs |
| `skills/create-subagents/references/error-handling-and-recovery.md` | create-subagents | YES | No | No | OK |
| `skills/create-subagents/references/failure-modes.md` | create-subagents | YES | No | No | OK |
| `skills/create-subagents/references/fault-tolerance.md` | create-subagents | YES | No | YES (310L) | WARN: bloated |
| `skills/create-subagents/references/gotchas.md` | create-subagents | YES | No | No | OK |
| `skills/create-subagents/references/memory-architecture.md` | create-subagents | YES | No | No | OK |
| `skills/create-subagents/references/orchestration-core.md` | create-subagents | YES | No | No | OK |
| `skills/create-subagents/references/scratchpad-protocol.md` | create-subagents | YES | No | No | OK |
| `skills/create-subagents/references/subagents.md` | create-subagents | YES | No | No | OK |
| `skills/create-subagents/references/token-economics.md` | create-subagents | YES | No | No | OK |
| `skills/create-subagents/references/tools-reference.md` | create-subagents | YES | No | No | OK |
| `skills/create-subagents/references/writing-subagent-prompts.md` | create-subagents | YES | No | YES (436L) | WARN: bloated |
| `skills/execute-plans/references/checkpoint-protocols.md` | execute-plans | YES | No | No | OK |
| `skills/execute-plans/references/context-efficiency.md` | execute-plans | YES | No | No | OK |
| `skills/execute-plans/references/deviation-rules.md` | execute-plans | YES | No | No | OK |
| `skills/execute-plans/references/env-variable-pattern.md` | execute-plans | YES | No | No | OK |
| `skills/execute-plans/references/execution-strategies.md` | execute-plans | YES | No | No | OK |
| `skills/execute-plans/references/meta-judge.md` | execute-plans | YES | No | No | OK |
| `skills/create-plans/agents/architect.md` | create-plans | YES | No | No | OK |
| `skills/create-plans/agents/critic.md` | create-plans | YES | No | No | OK |
| `skills/create-plans/agents/explorer.md` | create-plans | YES | No | No | OK |
| `skills/create-plans/agents/implementer.md` | create-plans | YES | No | No | OK |
| `skills/create-plans/agents/researcher.md` | create-plans | YES | No | No | OK |
| `skills/create-plans/agents/verifier.md` | create-plans | YES | No | No | OK |
| `skills/execute-plans/agents/critic.md` | execute-plans | YES | No | No | OK |
| `skills/execute-plans/agents/implementer.md` | execute-plans | YES | No | No | OK |
| `skills/execute-plans/agents/researcher.md` | execute-plans | YES | No | No | OK |
| `skills/execute-plans/agents/verifier.md` | execute-plans | YES | No | No | OK |
| `skills/create-plans/templates/brief.md` | create-plans | YES | No | No | OK |
| `skills/create-plans/templates/issues.md` | create-plans | YES | No | No | OK |
| `skills/create-plans/templates/phase-prompt.md` | create-plans | YES | No | No | OK |
| `skills/create-plans/templates/roadmap.md` | create-plans | YES | No | No | OK |
| `skills/create-plans/templates/summary.md` | create-plans | YES | No | No | OK |
| `skills/execute-plans/templates/autonomous-execution.md` | execute-plans | YES | No | YES (317L) | WARN: bloated |
| `skills/execute-plans/templates/segment-execution.md` | execute-plans | YES | No | No | OK |
| `skills/execute-plans/templates/sequential-execution.md` | execute-plans | YES | No | No | OK |
| `skills/create-plans/workflows/execute-phase.md` | create-plans | YES | No | YES (401L) | WARN: bloated |
| `skills/create-plans/workflows/README.md` | create-plans | YES | No | No | OK |
| `skills/create-prompts/workflows/execute-prompt.md` | create-prompts | YES | No | No | OK |
| `skills/execute-prompts/workflows/execute-prompt.md` | execute-prompts | YES | No | No | OK |
| `skills/create-skills/scripts/run_trigger_benchmark.py` | create-skills | YES | No | No | OK |
| `skills/create-subagents/scripts/coordination.py` | create-subagents | YES | No | No | OK |
| `plugins/tp-sadd/agents/` | tp-sadd | N/A | YES | N/A | ORPHAN: empty dir with .gitkeep only |

---

## Orphaned Reference Files (can be deleted)

| File | Reason |
|------|--------|
| `plugins/tp-sadd/agents/` | Empty directory with only `.gitkeep`. No agent definitions exist. This directory should either contain agent definitions or be removed entirely. |

---

## Bloated Reference Files (need trimming — >300 lines)

| File | Lines | Issue |
|------|-------|-------|
| `skills/create-plans/references/milestone-management.md` | 490 | Largest reference; covers greenfield/brownfield planning with extensive examples. Content is largely instructional — much could be trimmed to core principles. |
| `skills/create-subagents/references/context-management.md` | 448 | Dense but wide coverage; significant content overlap with `memory-architecture.md` and `gotchas.md` |
| `skills/create-subagents/references/writing-subagent-prompts.md` | 436 | Extensive examples section; could be split or condensed |
| `skills/create-plans/workflows/execute-phase.md` | 401 | Largest workflow; the deviation rules are fully inlined here (Rules 1-5 with full examples) |
| `skills/execute-plans/templates/autonomous-execution.md` | 317 | Large template with extensive spawn prompt structure documentation |

---

## Broken Cross-References

| File | Line | Broken Reference | Issue |
|------|------|------------------|-------|
| `skills/create-subagents/references/context-management.md` | 415 | `` {baseDir}/references/gotchas.md `` | Resolves to `create-subagents/references/references/gotchas.md` — does not exist. Should be `{baseDir}/../create-subagents/references/gotchas.md` |
| `skills/create-subagents/references/context-management.md` | 449 | `` {baseDir}/references/token-economics.md `` | Resolves to `create-subagents/references/references/token-economics.md` — does not exist. Should be `{baseDir}/../create-subagents/references/token-economics.md` |

Note: `execute-plans/references/execution-strategies.md` correctly uses `{baseDir}/../create-subagents/references/gotchas.md` (line 56) — that one is fine.

---

## Stale Content Indicators

No files with explicitly stale content were identified. All reference files appear current with the current skill behavior. However:

- `cli-automation.md` contains a "Railway deprecated" note (Railway discontinued 2024) — this is correctly flagged as deprecated in the reference, but worth verifying the alternative guidance (Vercel, Fly.io, Render) is still current.

---

## Format Quality

All files reviewed for markdown cleanliness:

- **No threatening language detected** across any file
- **No XML tags** found in body text (some frontmatter uses XML-safe `---` YAML delimiters, which is correct)
- **Minor markdown issues:** Some agent files use `<role>`, `<workflow>` XML-style tags in body text alongside markdown headings — this appears intentional for agent definition formatting and is acceptable within that context

---

## Summary

| Metric | Value |
|--------|-------|
| Total reference files | 61 |
| Referenced by parent SKILL.md | 60/61 (98.4%) |
| Orphaned (no reference) | 1 (plugins/tp-sadd/agents/) |
| Bloated (>300 lines) | 5 |
| Broken cross-references | 2 |
| Format issues | 0 |

**% properly justified:** 98.4% (60 of 61 files are referenced by their parent SKILL.md)

**Priority fixes:**
1. Fix 2 broken cross-references in `create-subagents/references/context-management.md` (lines 415, 449)
2. Consider trimming or splitting `milestone-management.md` (490 lines — largest reference)
3. Empty `plugins/tp-sadd/agents/` directory should be removed or populated
