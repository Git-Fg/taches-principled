---
name: orchestration-contracts
description: Subagent spawning patterns, tool scoping, and output contracts. The #1 runtime failure mode is agents trying to spawn other agents.
---

# Rule: MUST NOT nest agent spawning; orchestration lives in skills with context:fork

**Why:** The `Agent` tool is strictly removed from the subagent tool registry. Any nested spawning directive in an agent definition results in runtime failure. Skills with `context: fork` provide isolated subagent contexts that CAN spawn further agents or invoke skills.

## Rule

- Agent definitions (`agents/*.md`) MUST NEVER contain spawn, fan-out, or delegation instructions.
- Orchestration belongs in skill bodies with `context: fork` frontmatter, not in agent definitions.
- Subagents CAN invoke skills using the `Skill` tool (v2.1.133+).
- Subagent→Skill and Forked→Inline workflows are structurally supported.
- Default to subagents for non-trivial work. Inline is the exception.

## Spawn Pattern (for skill bodies)

```markdown
## Execution Mode
**Default: subagent delegation.** For [task type], spawn a [role] subagent.
- Scope: [specific files/questions]
- Role: [explorer/implementer/researcher/critic/etc.]
- Output: [what the subagent must return]
After subagent returns: synthesize, then spawn verification/critique subagents. Loop until no HIGH findings.
```

## Bad / Good

**Bad:** Agent body: "Spawn an explorer subagent to investigate..." — runtime error.
**Good:** Skill body with `context: fork`: "Spawn an explorer subagent with scope X."

**Bad:** "If the task is complex, consider using subagents." — optional language.
**Good:** "Spawn subagents for exploration, implementation, research, and critique." — declarative.

**Bad:** Main agent performs 5-file exploration inline.
**Good:** Main agent spawns explorer subagent, synthesizes results, spawns critic for verification.
