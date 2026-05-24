---
name: orchestration-core
description: Core mental model and orchestrator responsibilities for subagent coordination
---

# Orchestration Core Mental Model

Four rules that govern every delegation decision:

1. **Analyze before delegating** — understand the full task graph first
2. **Assign unambiguous scope** — each subagent gets exclusive file ownership
3. **Validate before integrating** — run success criteria, never assume
4. **Persist state to disk** — subagents don't share conversation memory

---

## Orchestrator Checklist

Before spawning any subagent, verify:

- [ ] Task decomposed into independent, file-disjoint streams
- [ ] Each stream has: scope, context, deliverable, success criteria, rollback
- [ ] Spawn prompt structured with RACE (Role/Action/Context/Expectation)
- [ ] Subagents spawned with appropriate model/tools/background
- [ ] Failure signal format defined for each subagent
- [ ] Results validated against success criteria before integration
- [ ] Failed subagents: root-cause → re-decompose → respawn (never patch in-place)
- [ ] Cross-domain consistency checked before integration
- [ ] Final test suite passes before commit
- [ ] Rollback verified if integration fails
- [ ] Monitor or ScheduleWakeup wired for long-running external processes
- [ ] TaskGet/TaskOutput available for mid-flight inspection

---

## Cost-Capability Spectrum

| Type | Model | Context | Cost | Use when |
|------|-------|---------|------|----------|
| Bash | — | Shell only | Lowest | Git ops, build commands, script execution |
| Explore | Haiku | Fresh, read-only | Lowest | Codebase discovery, targeted lookups |
| Plan | Sonnet | Fresh, read-only | Low | Architecture analysis, implementation planning |
| general-purpose | inherit | Fresh, configurable | Medium | Custom workflows, complex orchestration |

**Rule:** Never spawn a subagent for a task that fits in a single context window and would take less than 5 minutes inline.