# Command Format Standard

Commands are lightweight triggers — not mini-skills. The body is plain text, no markdown, one coherent instruction. Trust Claude to figure out the rest.

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
- Tell the outcome, not the method

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
