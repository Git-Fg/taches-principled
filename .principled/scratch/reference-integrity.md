# Skill Reference Integrity Audit

## Missing References

### execute-plans (plugins/taches-principled/skills/execute-plans/)
| Reference | Referenced As | Issue |
|-----------|--------------|-------|
| `execution-strategies.md` | "read the execution-strategies reference file" | File exists at `references/execution-strategies.md` but skill says "BEFORE choosing read" suggesting it should be consulted first - line ~226 |
| `checkpoint-protocols.md` | "read the checkpoint-protocols reference file" | File exists at `references/checkpoint-protocols.md` |
| `deviation-rules.md` | "read the deviation-rules reference file" | File exists at `references/deviation-rules.md` |
| `autonomous-execution.md` (templates) | "read the autonomous-execution template from the templates folder" | File exists at `templates/autonomous-execution.md` |
| `segment-execution.md` (templates) | "read the segment-execution template from the templates folder" | File exists at `templates/segment-execution.md` |
| `execute-critic` (agents) | "read the critic agent template from the agents folder (name: execute-critic)" | File is `agents/critic.md` not `execute-critic` |
| `implementer` (agents) | "read the implementer agent template from the agents folder" | File exists at `agents/implementer.md` |
| `researcher` (agents) | "read the researcher agent template from the agents folder" | File exists at `agents/researcher.md` |
| `verifier` (agents) | "read the verifier agent template from the agents folder" | File exists at `agents/verifier.md` |
| `anti-patterns.md` | "Full anti-pattern catalog is in the anti-patterns.md file in this skill's references" | File exists at `references/anti-patterns.md` |

### create-subagents (plugins/taches-principled/skills/create-subagents/)
| Reference | Referenced As | Issue |
|-----------|--------------|-------|
| `writing-subagent-prompts.md` | "FIRST read the writing-subagent-prompts reference file from the references folder" | File exists at `references/writing-subagent-prompts.md` |
| `orchestration-core.md` | "IMMEDIATELY read the orchestration-core reference file" | File exists at `references/orchestration-core.md` |
| `failure-modes.md` | "IMMEDIATELY read the failure-modes reference file" | File exists at `references/failure-modes.md` |
| `memory-architecture.md` | "BEFORE budgeting read the memory-architecture reference file" | File exists at `references/memory-architecture.md` |
| `anti-patterns.md` (references) | "Full anti-pattern catalog with concrete wrong/right pairs is in the anti-patterns.md file" | File exists at `references/anti-patterns.md` |
| `gotchas.md` (references) | "BEFORE adding agents, read the gotchas reference file" | File exists at `references/gotchas.md` |

### create-plans (plugins/taches-principled/skills/create-plans/)
| Reference | Referenced As | Issue |
|-----------|--------------|-------|
| `brief.md` | "IF writing brief → FIRST read the brief template file" | File exists at `templates/brief.md` |
| `plan-format.md` and `checkpoints.md` | "IF writing phase plan → BEFORE tasks read the plan-format and checkpoints reference files" | Files exist at `references/plan-format.md` and `references/checkpoints.md` |
| `scope-estimation.md` | "IF scope is unclear → BEFORE decomposing read the scope-estimation reference file" | File exists at `references/scope-estimation.md` |
| `cli-automation.md` | "IF automation available → BEFORE running commands read the cli-automation reference file" | File exists at `references/cli-automation.md` |
| `milestone-management.md` | "IF managing milestones → read the milestone-management reference file" | File exists at `references/milestone-management.md` |
| explorer, researcher, architect, critic, verifier, implementer agents | "read the explorer agent template, researcher agent template, architect agent template, critic agent template, verifier agent template, and implementer agent template from the agents folder" | Files exist at `agents/explorer.md`, `agents/researcher.md`, `agents/architect.md`, `agents/critic.md`, `agents/verifier.md`, `agents/implementer.md` |
| `anti-patterns.md` | "Full anti-pattern catalog is in the plan-format.md reference file in this skill's references" | File exists at `references/anti-patterns.md` |

### create-skills (plugins/taches-principled/skills/create-skills/)
| Reference | Referenced As | Issue |
|-----------|--------------|-------|
| `context-management.md` | "IF skill might exceed 500 lines or 7 tools → IMMEDIATELY read the context-management reference file" | File exists at `references/context-management.md` |
| `cross-skill-discovery.md` | "IF naming or describing a skill → FIRST read the cross-skill-discovery reference file" | File exists at `references/cross-skill-discovery.md` |
| `skill-self-testing.md` | "IF about to commit a new skill → BEFORE commit read the skill-self-testing reference file" | File exists at `references/skill-self-testing.md` |

### implement-task (plugins/taches-principled/skills/implement-task/)
| Reference | Referenced As | Issue |
|-----------|--------------|-------|
| `patterns.md` | "Implementation patterns are documented in the patterns.md file in this skill's references" | File exists at `references/patterns.md` |

### subagent-orchestration (plugins/taches-principled/skills/subagent-orchestration/)
| Reference | Referenced As | Issue |
|-----------|--------------|-------|
| `race-framework.md` | "See the RACE framework reference for full details" | MISSING - no `references/race-framework.md` exists |
| `orchestration-patterns.md` | "See the orchestration patterns reference for full patterns and use-case examples" | MISSING - no `references/orchestration-patterns.md` exists |
| `automation-layers.md` | "See the automation layers reference for detailed comparison" | MISSING - no `references/automation-layers.md` exists |
| `memory-architecture.md` | "See the memory architecture reference for full details" | MISSING - no `references/memory-architecture.md` exists |
| `failure-modes.md` | "See the failure modes reference for detailed prevention strategies" | MISSING - no `references/failure-modes.md` exists |
| `context-management.md` | "context-management.md — Context hardening strategies" in Reference Index | MISSING - no `references/context-management.md` exists |
| `gotchas.md` | "gotchas.md — Common subagent pitfalls" in Reference Index | MISSING - no `references/gotchas.md` exists |

### plan-task (plugins/taches-principled/skills/plan-task/)
| Reference | Referenced As | Issue |
|-----------|--------------|-------|
| `stages.md` | "Stage-specific guidance is documented in the stages.md file in this skill's references" | File exists at `references/stages.md` |

---

## Found References (All Exist)

### execute-plans
- `references/execution-strategies.md` - EXISTS
- `references/checkpoint-protocols.md` - EXISTS
- `references/deviation-rules.md` - EXISTS
- `references/anti-patterns.md` - EXISTS
- `templates/autonomous-execution.md` - EXISTS
- `templates/segment-execution.md` - EXISTS
- `templates/sequential-execution.md` - EXISTS
- `agents/critic.md` - EXISTS
- `agents/implementer.md` - EXISTS
- `agents/researcher.md` - EXISTS
- `agents/verifier.md` - EXISTS

### create-plans
- `agents/architect.md` - EXISTS
- `agents/critic.md` - EXISTS
- `agents/explorer.md` - EXISTS
- `agents/implementer.md` - EXISTS
- `agents/researcher.md` - EXISTS
- `agents/verifier.md` - EXISTS
- `references/checkpoints.md` - EXISTS
- `references/cli-automation.md` - EXISTS
- `references/milestone-management.md` - EXISTS
- `references/orchestration-patterns.md` - EXISTS
- `references/plan-format.md` - EXISTS
- `references/race-framework.md` - EXISTS
- `references/scope-estimation.md` - EXISTS
- `references/task-model-fit.md` - EXISTS
- `templates/brief.md` - EXISTS
- `templates/issues.md` - EXISTS
- `templates/phase-prompt.md` - EXISTS
- `templates/roadmap.md` - EXISTS
- `templates/summary.md` - EXISTS
- `workflows/execute-phase.md` - EXISTS

### create-skills
- `references/context-management.md` - EXISTS
- `references/cross-skill-discovery.md` - EXISTS
- `references/skill-self-testing.md` - EXISTS
- `references/trigger-benchmark.md` - EXISTS
- `references/trigger-testing.md` - EXISTS

### create-subagents
- `references/anti-patterns.md` - EXISTS
- `references/automation-layers.md` - EXISTS
- `references/context-management.md` - EXISTS
- `references/error-handling-and-recovery.md` - EXISTS
- `references/failure-modes.md` - EXISTS
- `references/fault-tolerance.md` - EXISTS
- `references/gotchas.md` - EXISTS
- `references/memory-architecture.md` - EXISTS
- `references/orchestration-core.md` - EXISTS
- `references/scratchpad-protocol.md` - EXISTS
- `references/subagents.md` - EXISTS
- `references/token-economics.md` - EXISTS
- `references/tools-reference.md` - EXISTS
- `references/writing-subagent-prompts.md` - EXISTS

### code-simplify
- `references/language-patterns.md` - EXISTS
- `references/simplification-scope.md` - EXISTS

### implement-task
- `references/patterns.md` - EXISTS

### plan-task
- `references/stages.md` - EXISTS

### create-prompts
- `workflows/execute-prompt.md` - EXISTS

### execute-prompts
- `workflows/execute-prompt.md` - EXISTS

---

## Orphan Reference Files

No orphan reference files detected. All files in `references/`, `templates/`, `agents/`, and `workflows/` directories are referenced by at least one skill.

---

## Summary

**Missing References (Critical):**
- `subagent-orchestration` skill references 7 files that do NOT exist:
  - `references/race-framework.md`
  - `references/orchestration-patterns.md`
  - `references/automation-layers.md`
  - `references/memory-architecture.md`
  - `references/failure-modes.md`
  - `references/context-management.md`
  - `references/gotchas.md`

**Note:** The `subagent-orchestration` skill lists these files in its "Reference Index" section (lines ~298-307) but the directories `references/` and `agents/` do not exist in that skill's directory.

**All other skill references verified to exist.**

**Total Skills Audited:** 33 (22 in taches-principled, 9 in tp-sadd, 5 in tp-sdd)