# Spawn Pattern Consistency Analysis

## Spawn Pattern by Skill

| Skill | Model Selection | Tools Specified | Spawn Method | RACE Usage | Has Spawn Footer | Has Failure Signal |
|-------|-----------------|-----------------|--------------|------------|-------------------|-------------------|
| `create-plans` | Unspecified | Read, Write, Grep, Glob, Bash (min for exploration) | Generic "spawn" + agent templates | RACE defined in references, agent templates use it | Yes (in agent templates) | No explicit failure schema |
| `execute-plans` | Sonnet for orchestrator, Haiku for workers | Read, Edit, Bash (implementer) | Templates + agent templates | Yes (RACE in templates) | Yes (explicit in autonomous-execution.md) | Rollback commands documented |
| `implement-task` | Opus/Sonnet/Haiku (implicit via thresholds) | Not explicitly specified | Task tool with role-based prompts | No (inline prompts lack RACE structure) | No explicit footer in spawn prompts | Retry loop documented |
| `plan-task` (tp-sdd) | Unspecified | Read, Write, Grep, Bash (minimum) | Generic "spawn subagent" | No (inline prompts lack RACE structure) | No | Judge FAIL triggers re-launch |
| `sadd-dispatch` | Opus/Sonnet/Haiku auto-selection | Not specified | Task tool | CoT prefix + self-critique suffix (not RACE) | No explicit footer | Verification questions before submission |
| `sadd-execute` | Opus/Sonnet/Haiku auto-selection | Not specified | Task tool (parallel dispatch) | CoT prefix + self-critique suffix (not RACE) | No explicit footer | Retry loop with max iterations |
| `launch-subagent` | Opus/Sonnet/Haiku auto-selection | Not specified | Task tool | CoT prefix + self-critique suffix (RACE-like but not named) | No explicit footer | Self-critique verification |
| `subagent-driven-development` | Unspecified | Write, Bash (assumed) | Task tool | No structured format | No | Re-launch with feedback |
| `fpf-propose` | Unspecified | Not specified | Generic "spawn a subagent" | No | No | No explicit failure handling |

## Inconsistencies Found

### 1. Spawn Verb Inconsistency
- **"spawn a subagent"**: create-plans, plan-task, execute-plans, fpf-propose
- **"dispatch a subagent"**: sadd-dispatch, subagent-driven-development, implement-task
- **"launch a subagent"**: launch-subagent
- **"dispatch subagents"**: sadd-execute, create-plans (some references)

The personal-conventions rule specifies "spawn" as canonical, but many skills still use "dispatch" and "launch".

### 2. Model Selection Inconsistency

| Task Type | create-plans | execute-plans | sadd-dispatch | sadd-execute | implement-task |
|-----------|--------------|---------------|---------------|--------------|----------------|
| Complex reasoning | Unspecified | Sonnet (orchestrator) | Opus | Opus | Unspecified |
| Standard work | Unspecified | Haiku (workers) | Sonnet | Sonnet | Unspecified |
| Simple tasks | Unspecified | Haiku (workers) | Haiku | Haiku | Unspecified |

**Issue**: Model selection is explicit only in tp-sadd skills. execute-plans hardcodes Sonnet for orchestrator, Haiku for workers. create-plans and implement-task leave model unspecified entirely.

### 3. RACE Framework Usage Inconsistency

- **Uses RACE**: execute-plans (via templates and agent files), create-plans (reference documentation, agent templates)
- **Does NOT use RACE**: implement-task, plan-task, sadd-dispatch, sadd-execute, launch-subagent

The RACE framework is documented but not universally adopted. Skills that spawn subagents with structured prompts (create-plans agents, execute-plans templates) use RACE, but inline spawn prompts in many skills do not.

### 4. CoT Prefix Usage

| Skill | CoT Prefix | Self-Critique Suffix |
|-------|------------|---------------------|
| sadd-dispatch | Yes (detailed) | Yes (5 verification questions) |
| sadd-execute | Yes (implied) | Yes (self-critique verification) |
| launch-subagent | Yes (structured) | Yes (mandatory) |
| implement-task | No | No |
| plan-task | No | No |
| create-plans | No (uses agent templates) | Agent templates include critique |

### 5. Spawn Footer Inconsistency

The personal-conventions rule mandates a spawn footer. Only execute-plans has it explicitly documented:

```
You are a subagent executing a delegated task. Your context starts fresh — you have no access to prior conversation or other subagents' outputs. When complete, return your full results...
```

Other skills either omit it or have it only in agent templates (create-plans) but not in inline spawn prompts.

### 6. Tool Specification Inconsistency

- **create-plans**: Explicitly specifies minimum tools for exploration subagents (Read, Write, Grep, Glob, Bash)
- **execute-plans templates**: Specifies tools per agent (implementer: Read, Edit, Bash)
- **implement-task**: No tool specification in spawn prompts
- **plan-task**: Only in "REQUIRED minimum" note for explorer subagents
- **sadd-dispatch/execute**: No tool specification

## Missing Mandatory Elements

### Skills Missing Spawn Footer in Inline Prompts

1. **implement-task** — Spawn prompts at lines 179-194, 207-221, 268-282 do not include spawn footer
2. **plan-task** — Phase agent prompts (lines 94-107) do not include spawn footer
3. **sadd-dispatch** — Single mode dispatch (lines 46-52) lacks spawn footer
4. **sadd-execute** — Meta-judge and implementation agent dispatch lacks spawn footer
5. **subagent-driven-development** — Lines 43-82 dispatch prompts lack spawn footer
6. **fpf-propose** — Lines 27-57 lack spawn footer

### Skills Without Explicit Failure Signal Schema

- **create-plans**: Mentions re-launch but no structured failure schema
- **execute-plans**: Has rollback commands but no structured failure signal beyond "re-spawn with feedback"
- **implement-task**: Retry loop exists but no formal failure signal contract
- **plan-task**: FAIL triggers re-launch but no structured schema

## Recommended Standardization

### 1. Unify Spawn Verbs
Replace all "dispatch" and "launch agent" with "spawn a [role] subagent" per personal-conventions.

### 2. Make Model Selection Explicit
Every skill that spawns subagents should have explicit model selection criteria, either:
- Inline (like launch-subagent's decision tree)
- Reference to auto-selection pattern

### 3. Adopt RACE for All Inline Spawn Prompts
RACE should be used for ALL spawn prompts, not just those in agent template files. Skills with inline prompts (implement-task, plan-task, sadd-*) should adopt RACE structure.

### 4. Mandate Spawn Footer
Every spawn prompt should end with:
```
You are a subagent executing a delegated task. Your context starts fresh — you have no access to prior conversation or other subagents' outputs. Return structured output to the orchestrator. If you encounter anything unexpected or have questions, stop and report back.
```

### 5. Standardize Tool Requirements
Follow create-plans' pattern of explicitly listing required tools for subagent type:
```
Required tools: [Read, Write, Grep, Glob, Bash]
```

### 6. Add Structured Failure Signal
Every spawn should document:
- What constitutes failure
- Retry behavior
- Rollback mechanism

### 7. Consolidate Self-Critique Pattern
The CoT prefix + self-critique suffix pattern from launch-subagent/sadd-dispatch should be the standard for ALL implementation-type subagents, not just some skills.