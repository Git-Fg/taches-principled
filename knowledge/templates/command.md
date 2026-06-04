# Command Format Standard

Commands are lightweight triggers — not mini-skills. The body is plain text, no markdown, one coherent instruction. Commands are auto-invoked by default by Claude Code — like skills, they are discovered through description matching without prior conversation context.

## Frontmatter

```
---
name: <kebab-case>
skill: <skill-name>
description: <one-line purpose, no markdown>
argument-hint: [<hint>]    # optional
---
```

## Body Rules

- No markdown syntax: no `#`, `**`, `- `, `1. `, `` ` ``
- No numbered steps or bullet lists
- No bold/italic labels
- No usage examples (redundant with argument-hint)
- 1-3 sentences, single paragraph
- Use `$ARGUMENTS` to inject user input
- Tell the outcome, not the method. "Outcome" means what the command achieves (native capabilities like "fan out subagents", "create a task list"). "Method" means the skill's internal methodology (like "apply A3 with fishbone"). Commands name what to do at the capability level — they don't restate skill internals.

## Conditional Skill Hints

Commands may include conditional hints pointing to useful skills, subagents, or tools — but must always default to semantic meaning and generalistic phrasing.

```
Use the skill <name> if you have access to it.
Spawn a <role> subagent if you have access to one.
Start by using web search if you have access to it.
```

The "if you have access to" framing preserves high trust and high freedom — the hint is advisory, not required. The command must still read as a coherent instruction without the conditional clauses.

## Rationale

Commands are user-invoked explicitly — they don't need when_to_use or progressive disclosure. The skill owns method; the command is just a trigger. High trust means leaving how to the skill. High freedom means no structural decomposition of the task.

## Trigger Acceleration vs Method Carriers

**Never evaluate a command by comparing its body to the skill's body.** A command that seems redundant may be teaching the trigger while the skill teaches the method. Structural overlap analysis misses the value.

**What commands do:**
- Teach the mental frame ("when you see a bug, think root cause")
- Provide a memorable trigger phrase shorter than the skill description
- Add semantic framing the skill can't provide without being bloated

**What commands don't need to do:**
- Carry unique logic the skill doesn't have
- Restate the skill's methodology in fewer words
- Add information the skill already teaches

**Anti-pattern:** Deleting commands because their body overlaps with the skill body. A command that says "Find the root cause" teaches a different trigger than "Apply systematic debugging methodology" — even if both ultimately route to the same skill.

**When a command IS hollow:** It adds nothing to the trigger. `$ARGUMENTS` alone is valid if the description provides the trigger signal. But even a bare `$ARGUMENTS` pass-through is acceptable when the description + frontmatter teaches the frame.
