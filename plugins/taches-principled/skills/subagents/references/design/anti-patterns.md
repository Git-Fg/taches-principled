# Anti-Patterns in Subagent Design

## Tool Restriction at Birth

**Critical anti-pattern:** Starting with tool restrictions.

Start with **no tool restrictions**. Omit both `tools` and `disallowedTools` from the initial definition. The agent inherits all tools from the parent.

**Why:** Premature restriction is the most common cause of silent agent failures. An agent that can't complete its task but can't report why is worse than a working unrestricted agent.

**Iterative refinement workflow:**
1. Ship the agent with no restrictions
2. Verify it works correctly across multiple delegations
3. If a specific tool causes problems, add ONE restriction and re-verify
4. `disallowedTools` (blocklist) — prefer this over allowlists

**When restrictions ARE appropriate from the start:**
- Read-only agents: `disallowedTools: [Write, Edit]`
- Agents for narrow purpose where extra tools create noise

## Too Generic

```markdown
You are a helpful assistant that helps with code.
```

This provides no specialization. The subagent won't know what to focus on.

## No Workflow

```markdown
You are a code reviewer. Review code for issues.
```

Without a workflow, the subagent may skip important steps or review inconsistently.

## Requires User Interaction

**Critical**: Subagents cannot interact with users.

```markdown
---
name: intake-agent
description: Gathers requirements from user
tools: AskUserQuestion
---

<workflow>
1. Ask user about their requirements using AskUserQuestion
2. Follow up with clarifying questions
3. Return finalized requirements
</workflow>
```

**Why this fails:** Subagents execute in isolated contexts. They cannot use AskUserQuestion.

**Correct approach:** Move user interaction to main chat.

## Missing Constraints

Without constraints, subagents might modify code they shouldn't, run dangerous commands, or skip important steps.

## Unclear Trigger

The `description` field is critical for automatic invocation.

Bad: `description: Helps with testing`
Good: `description: Creates comprehensive test suites. Use when new code needs tests or test coverage is insufficient.`

## Vague Spawn Prompt

"Implement the feature and make sure it's good" — no scope, no success criteria, no rollback.

## Specific Spawn Prompt

"Implement POST /api/users in src/api/users.ts. Verify: npx jest --testPathPattern=users. Rollback: git checkout -- src/api/users.ts"

## Over-Permissioned Tools

Granting write, edit, and execution tools to a read-only analysis agent.

## Least-Privilege Tools

Read-only analysis: `Read, Grep, Glob`. Code implementation: `Read, Edit, Bash`. No extra tools.

## Generic Subagent Name

"name: helper" — provides no specialization signal to the orchestrator.

## Specific Subagent Name

"name: security-reviewer" — orchestrator knows exactly what this agent does.

## No Rollback Plan

Spawn prompt without stated rollback = no recovery path if agent goes wrong.

## Explicit Rollback

"At any failure: stop, report, do not continue. Rollback: git checkout -- <file>"