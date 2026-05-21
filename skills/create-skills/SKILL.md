---
name: create-skills
description: "Create Claude Code skills. Use when building new skills, improving existing ones, or understanding skill best practices."
when_to_use: |
  Do NOT use for writing general code, creating subagents, or configuring hooks/MCP servers.
---

## What Skills Are

Skills are prompts that load on demand. They give Claude domain expertise without bloating every conversation. Think of them as specialists you can call in when needed.

A skill is just a `SKILL.md` file. It can be a single file, or a folder with supporting materials (workflows, references, templates, scripts).

### Policy vs. Mechanism

**Policy** = when a skill should trigger (the routing decision)
**Mechanism** = what the skill teaches and how it guides behavior

A skill conflating policy and mechanism produces:
- Skills that are too broad (policy problem — trigger too generic)
- Skills that are too narrow (policy problem — trigger too specific)
- Skills that know WHEN but not HOW (mechanism problem — vague guidance)
- Skills that know HOW but not WHEN (mechanism problem — can't decide when to act)

Good skill design separates:
- Frontmatter: policy (name, description, when_to_use, triggers)
- Body: mechanism (principles, patterns, anti-patterns, examples)

## The Core Insight

**Skills share the context window with everything else.** Every token in your skill competes with the user's request, conversation history, and other loaded content. This changes everything:

- Assume Claude is smart. Don't explain obvious things.
- Put essential principles in SKILL.md—it's always loaded.
- Put details in references—they load only when needed.
- If a line doesn't earn its keep, delete it.

## What Good Looks Like

A well-designed skill:

- Has a clear YAML description (when should Claude use this?)
- Starts with the most important information
- Uses structure that makes sense for the content
- Stays concise—typically under 200 lines
- Includes one good example, not every edge case

### Numeric Thresholds

| Metric | Limit | Why |
|--------|-------|-----|
| Description length | 150 chars max | Truncates at 1,536 combined with when_to_use |
| when_to_use length | 200 chars max | Longer = context bloat, not better routing |
| Skill body | 500 lines max | Beyond = principle dilution; split or reference |
| Tools allowed | 7 max (Miller's number) | Beyond = coordination overhead |

**Split signal:** If a skill needs >7 tools, >500 lines, or covers multiple concerns — split into focused skills.

Example of a focused skill:

```markdown
---
name: code-reviewer
description: Review code for quality, security, and best practices.
---

## What to Check

- Logic errors and edge cases
- Security vulnerabilities (injection, auth issues)
- Performance concerns
- Code organization and readability

## Output Format

For each issue found:
1. File and line number
2. What's wrong
3. How to fix it
4. Severity (critical/high/medium/low)

Start with critical issues, end with suggestions.
```

## When to Use Folders

Simple skills (one focused task) → single SKILL.md file

Complex skills (multiple workflows, extensive domain knowledge) → use folders:

```
skill-name/
├── SKILL.md          # Principles, routing
├── workflows/        # Step-by-step procedures
├── references/       # Domain knowledge
├── templates/        # Output structures
└── scripts/          # Executable code
```

## Common Mistakes

**Over-explaining.** Only explain what's specific to your domain. Don't teach Claude what it already knows.

**Generic descriptions.** "Helps with code" → Claude won't know when to use it. "Reviews Python code for security vulnerabilities" → specific, routable.

**No success criteria.** How does Claude know when it's done? Include what "done" looks like.

**Inconsistent structure.** If you use sections, be consistent. Random organization forces Claude to hunt for information.

**Too many examples.** One good example teaches more than five mediocre ones. Show the pattern, trust Claude to apply it.

## Where Skills Live

- **Project skills**: `.claude/skills/` (version controlled with project)
- **User skills**: `~/.claude/skills/` (available across all projects)

## Testing Your Skill

Invoke it: mention the skill name or topic in conversation. Check that Claude loads it correctly and produces expected results. Iterate.

## Anti-Patterns

### Vague description that won't route
"Helps with coding tasks" — triggers on everything, means nothing.

### Specific description with trigger keywords
"Creates unit tests with edge cases. Use when user asks to 'write tests', 'add test coverage', or 'generate tests'."

### Overloaded skill doing too much
A single skill that handles skill creation, agent configuration, AND hook setup has no clear identity.

### Focused skill with single responsibility
"create-skills" teaches skill creation only. "create-subagents" teaches subagent configuration only. Each has one job.

### Generic frontmatter fields
"name: helper, description: helpful" — provides no routing signal.

### Specific frontmatter
"name: security-audit, description: 'Audits code for OWASP Top 10. Use when user mentions security, vulnerabilities, or XSS.'"

## Reference Index

| Reference | Purpose |
|-----------|---------|
| `references/context-management.md` | Context window principles, SKILL.md vs references/ load strategy |
| `references/skill-self-testing.md` | YAML validation, threshold checks, trigger testing |
| `references/cross-skill-discovery.md` | Skill routing, description patterns, name conventions |

---

## Clarifying Questions

Before creating a skill, ask:

1. **What specific task should Claude accomplish?** (The narrower, the better.)

2. **What does Claude already know about this?** (Don't repeat general knowledge.)

3. **What would make this skill successful?** (Define completion criteria.)
