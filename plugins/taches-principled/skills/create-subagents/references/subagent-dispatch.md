# Subagent Dispatch Reference

Reusable patterns for subagent spawning across any skill that delegates work.

## Spawn Footer (Mandatory)

Append to every subagent prompt:

```
You are a subagent executing a delegated task. Your context starts fresh — you have no access
to prior conversation or other subagents' outputs. When complete, return your full results
(file paths, findings, and any artifacts) to the orchestrator in structured form. If you encounter
anything unexpected or have any question or doubt, stop and report back with what you found
and what is unclear. Do not proceed silently on assumptions.
```

## Failure Signal Schema

Every subagent must return structured JSON on failure:

```json
{"status": "failed", "reason": "...", "completed_portion": "...", "retry_possible": true/false}
```

Do not guess or produce partial output without flagging it.

## Investigation Subagent Requirements

For research/exploration/investigation tasks, Write tool access is strongly recommended. Read-only agents risk the "telephone game" problem — orchestrators synthesize degraded quality without direct source access.

| Requirement | Recommendation |
|-------------|-----------------|
| Tools | Minimum `[Read, Write, Grep, Glob, Bash]` |
| Read-only agents | Avoid for multi-step investigation |
| Findings | Persist to orchestrator-defined scratch location |

If using read-only agents: require them to output structured findings that orchestrator can verify against source.

## Orchestrator Pre-Spawn Checklist

Before spawning any subagent:

- [ ] Task is non-trivial (>5 min inline work)
- [ ] Scope is unambiguous (file-disjoint for parallel agents)
- [ ] Success criteria are explicit (output format + coverage rule)
- [ ] Rollback command is documented (one-command revert)
- [ ] Failure signal schema is included
- [ ] Subagent has required Write tool access for investigation
- [ ] Findings location defined (orchestrator-specific path)
- [ ] Subagent instructed to persist findings before returning
- [ ] Orchestrator will read findings before synthesizing
- [ ] No overlapping file ownership between parallel agents
- [ ] Iteration limit set (stop after 2 retries, never loop silently)

## Coordination Patterns

| Pattern | When |
|---------|------|
| **Sequential** (A → B → C) | Each step depends on previous output |
| **Parallel** (A + B + C) | Independent tasks, file-disjoint scopes |
| **Pipeline** (research → implement) | Upstream output feeds downstream |
| **Fan-out/Fan-in** | N workers → aggregator synthesizes |

## State Persistence Rules

| Must survive | Mechanism |
|-------------|-----------|
| Compaction | CLAUDE.md or disk artifact |
| Session end | Disk artifact (orchestrator) or agent-memory |
| Shared between agents | Orchestrator-owned disk artifact |

**Never rely on conversation history** — subagents start with zero context. All state must be on disk.