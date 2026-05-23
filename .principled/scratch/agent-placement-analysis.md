# Agent Placement Analysis

## All Agents Catalog

### Plugin-Level Agents (auto-discovered, system-wide)

| Name | Location | Trigger | Tools | Standalone? |
|------|----------|---------|-------|--------------|
| `code-reviewer` | `plugins/taches-principled/agents/` | "code review", "PR review", "code quality feedback" | Read, Grep, Glob | Yes |
| `prompt-engineer` | `plugins/taches-principled/agents/` | "create a prompt", "write a prompt", "run a prompt" | Read, Write, Edit, Bash, Grep, Glob | Yes |
| `subagent-auditor` | `plugins/taches-principled/agents/` | "audit subagent", "review subagent configuration" | Read, Grep, Glob | Yes |
| `skill-auditor` | `plugins/taches-principled/agents/` | "audit skill", "review SKILL.md" | Read, Grep, Glob | Yes |
| `grader` | `plugins/taches-principled/agents/` | "grade skill", "evaluate teaching effectiveness" | Read, Grep, Glob | Yes |
| `comparator` | `plugins/taches-principled/agents/` | "compare skill versions", "understand delta" | Read, Grep, Glob | Yes |
| `analyzer` | `plugins/taches-principled/agents/` | "synthesize evaluation", "prioritize recommendations" | Read, Grep, Glob | Yes |

### Skill-Internal Agents (contextual to parent skill)

**create-plans/agents/**

| Name | Trigger | Tools | Scope |
|------|---------|-------|-------|
| `explorer` | Project exploration during planning | Read, Write, Grep, Glob, Bash | create-plans only |
| `architect` | Complex architectural decisions during planning | Read, Grep, Glob | create-plans only |
| `verifier` | Verify implementations against specifications | Read, Bash | create-plans only |
| `researcher` | Research unfamiliar technologies during planning | Read, Grep, Glob | create-plans only |
| `critic` | Milestone reviews during planning | Read, Grep | create-plans only |
| `implementer` | Implementing planned tasks | Read, Edit, Bash | create-plans only |

**execute-plans/agents/**

| Name | Trigger | Tools | Scope |
|------|---------|-------|-------|
| `execute-verifier` | Verify execution outputs | Read, Bash | execute-plans only |
| `execute-researcher` | Research during execution | Read, Grep, Glob | execute-plans only |
| `execute-critic` | Milestone reviews during execution | Read, Grep, Glob | execute-plans only |
| `execute-implementer` | Execute planned tasks | Read, Edit, Bash | execute-plans only |

---

## Current Placement Rationale

### Why Plugin-Level Agents Are There

**Evaluation Pipeline (grader, comparator, skill-auditor, analyzer)**
These four agents form the evaluation pipeline documented in CLAUDE.md. They are invoked by `skill-auditor.md` when performing comprehensive skill audits. They need to be plugin-level because:
- `skill-auditor` spawns `grader` as a subagent during audits
- `skill-auditor` spawns `comparator` for version delta analysis
- `analyzer` synthesizes outputs from all three other evaluation agents
- The pipeline is cross-skill: any skill can be audited, so the agents must be globally accessible

**General-Purpose Tools (code-reviewer, prompt-engineer, subagent-auditor)**
These agents serve roles that are useful independent of any single skill workflow:
- `code-reviewer`: Generic code quality review, triggered by user request
- `prompt-engineer`: Prompt creation/execution, triggered by user request
- `subagent-auditor`: Subagent configuration auditing, triggered when reviewing agent definitions

### Why Skill-Internal Agents Are There

**create-plans/agents/**
The six agents (explorer, architect, verifier, researcher, critic, implementer) are workflow-specific templates for the planning process:
- `explorer`: Maps project structure before planning (read-only)
- `architect`: Evaluates trade-offs for complex decisions (read-only)
- `researcher`: Investigates unfamiliar technologies (read-only)
- `critic`: Challenges the emerging plan before writing (read-only)
- `verifier`: Validates plan against requirements (read-only)
- `implementer`: Implements tasks from the plan (write-capable)

These are template prompts with `{{placeholder}}` variables. The create-plans skill reads the template, fills in the placeholders, and spawns a general-purpose subagent. They only make sense in the context of creating plans.

**execute-plans/agents/**
The four agents (execute-verifier, execute-researcher, execute-critic, execute-implementer) are execution-phase counterparts to the planning agents. They have similar roles but execute-phase naming to avoid confusion when both skills are loaded.

---

## Wrong Placement Candidates

**None identified.** All agents appear to be in their correct location based on the following analysis:

| Agent | Current | Should Be | Verdict |
|-------|---------|-----------|---------|
| code-reviewer | plugin-level | plugin-level | Correct - general purpose, user-triggered |
| prompt-engineer | plugin-level | plugin-level | Correct - general purpose, user-triggered |
| subagent-auditor | plugin-level | plugin-level | Correct - general purpose, user-triggered |
| skill-auditor | plugin-level | plugin-level | Correct - evaluation pipeline component |
| grader | plugin-level | plugin-level | Correct - evaluation pipeline, spawned by skill-auditor |
| comparator | plugin-level | plugin-level | Correct - evaluation pipeline, spawned by skill-auditor |
| analyzer | plugin-level | plugin-level | Correct - evaluation pipeline, synthesizes others |
| create-plans/* | skill-internal | skill-internal | Correct - workflow-specific, planning context only |
| execute-plans/* | skill-internal | skill-internal | Correct - workflow-specific, execution context only |

---

## Decision Criteria for Agent Placement

### Use Plugin-Level (auto-discovered, system-wide) when:

1. **Cross-skill utility**: The agent is invoked by multiple different skills or directly by users
2. **Evaluation/audit role**: The agent evaluates artifacts produced by other skills (skill-auditor, grader, comparator, analyzer)
3. **General-purpose tool**: The agent serves a standalone purpose not tied to a specific workflow phase
4. **User-triggerable**: The agent responds to direct user requests ("review this code", "create a prompt")

**Examples from codebase:**
- `code-reviewer`: invoked by users directly, not tied to any skill
- `skill-auditor`: evaluation pipeline, used across all skills
- `prompt-engineer`: prompt creation is a general activity

### Use Skill-Internal (only when skill loaded) when:

1. **Workflow-specific**: The agent only makes sense within a specific skill's process (e.g., planning-phase explorer)
2. **Template with placeholders**: The agent is a template read and populated by the skill before spawning
3. **Single-skill context**: No other skill would reasonably invoke this agent
4. **Orchestrator-owned**: The agent is an execution hand-off within the skill's internal orchestration

**Examples from codebase:**
- `explorer` in create-plans: only relevant when creating plans
- `execute-critic` in execute-plans: only relevant when executing plans

### The Key Question

> "Could this agent be usefully invoked by a skill OTHER THAN its current parent, or by a user directly?"

- **Yes** → Plugin-level
- **No** → Skill-internal

### Naming Collision Prevention

Note that create-plans and execute-plans both have agents with similar roles (critic, researcher, verifier, implementer). To prevent confusion when both skills are loaded, execute-plans prefixes its agents with "execute-". This is intentional and correct - the naming distinction allows both skill workflows to operate simultaneously without agent name conflicts.

---

## Summary

The agent placement in this codebase follows a consistent pattern:
- **Plugin-level**: Evaluation pipeline agents + general-purpose user-triggered agents
- **Skill-internal**: Workflow-specific template agents with placeholder variables

No refactoring needed. The architecture correctly separates cross-skill evaluation tools from skill-specific execution templates.