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

Design principles for skills:

- **Clear routing signal** — description tells Claude exactly when to act and when not to; vague descriptions trigger on everything and nothing
- **Principle first** — opening lines set the mental model before details compete; if Claude has to infer the point, the skill failed
- **Structure follows purpose** — organize around how the reader thinks, not how the writer organized their notes; coherence aids retention
- **Concision is respect** — every line competes for context space; extraneous words dilute what matters
- **One vivid example** — a concrete case teaches judgment better than ten edge cases that teach pattern-matching

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
name: test-writer
description: "Creates unit tests with edge cases. Use when user asks to 'write tests', 'add test coverage', or 'generate tests'."
when_to_use: |
  Do NOT use for debugging, refactoring, or writing production code.
---

## What to Check

- Edge cases and boundary conditions
- Error handling paths
- Happy path and failure modes
```

## When to Use Folders

Simple skills (one focused task) → single SKILL.md file

Complex skills (multiple workflows, extensive domain knowledge) → use folders:

```
skill-name/
├── SKILL.md          # Principles, routing
├── agents/           # Bundled subagent prompts (for portable delegation)
├── workflows/        # Step-by-step procedures
├── references/       # Domain knowledge
├── templates/        # Output structures
└── scripts/          # Executable code
```

## Bundled Agents Pattern

When a subagent prompt needs to be portable across projects, shared between skills, or version-controlled separately — store it in `agents/` rather than inlining it in SKILL.md.

**When to use agents/ vs inline:**
- Use `agents/` when: the prompt is reused by multiple skills, needs independent versioning, or must be portable (copied to other projects)
- Use inline when: the prompt is single-skill-specific, simple, or tied directly to that skill's body text

### Agent File Anatomy

Agent definitions follow a strict structure:

```markdown
---
name: specialist-type
description: What this agent does and when to use it.
---

You are a [role] specializing in [domain].

## Scope
[What files/areas this agent owns]

## Output Format
[How this agent returns results]

## Constraints
[What this agent MUST NOT do]

---

**Spawned by:** [orchestrator name]
**Context:** {{context}}
**Task:** {{task}}
```

The frontmatter provides the routing signal. The body establishes the agent's identity, scope, and constraints. The footer is a mandatory handoff convention.

### Portable Path Resolution

When SKILL.md references an agent file, the skill's installation path resolves automatically at runtime. This means the agent definition travels with the skill — no hardcoded paths needed. Describe the reference semantically:

> "Read the agent briefing from `agents/[name].md` and pass it as instructions when delegating"

No JSON. No Task tool syntax. Describe the delegation pattern in domain terms.

### Spawn-Footer Convention

Every spawned subagent must receive this footer, appended to its prompt:

> You are a subagent executing a delegated task. Your context starts fresh — you have no access to prior conversation or other subagents' outputs. When complete, return your full results (file paths, findings, and any artifacts) to the orchestrator in structured form. If you encounter anything unexpected or have any question or doubt, stop and report back with what you found and what is unclear. Do not proceed silently on assumptions.

This convention ensures subagents self-report rather than silently making assumptions when they encounter ambiguity.

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

WHY: Without specific trigger phrases, Claude has no basis to decide
when to load this skill vs. another. Vague descriptions provide no
routing signal, making the skill invisible to the trigger system.

### Specific description with trigger keywords
"Creates unit tests with edge cases. Use when user asks to 'write tests', 'add test coverage', or 'generate tests'."

### Overloaded skill doing too much
A single skill that handles skill creation, agent configuration, AND hook setup has no clear identity.

WHY: When one skill tries to be everything, it becomes nothing.
Claude cannot route to a skill that has no coherent scope. Overloaded
skills create ambiguity about when to invoke them and what they cover.
Each skill must own one clearly bounded domain.

### Focused skill with single responsibility
"create-skills" teaches skill creation only. "create-subagents" teaches subagent configuration only. Each has one job.

WHY: Focused skills provide clear routing signals. Claude knows
exactly when to load them and what they cover. Focused skills also
compose naturally — the orchestrator coordinates, the specialists execute.

### Generic frontmatter fields
"name: helper, description: helpful" — provides no routing signal.

WHY: The name is how Claude identifies the skill. "helper" tells
Claude nothing about what the skill does. A generic name means Claude
cannot distinguish this skill from any other. Skill names should be
nouns that describe the domain, not generic helpers.

### Specific frontmatter
"name: security-audit, description: 'Audits code for OWASP Top 10. Use when user mentions security, vulnerabilities, or XSS.'"

## Reference Index

Load a reference only when working on that specific aspect — do not load all upfront. The skill body provides what you need for typical cases; references are for deeper dives.

| Reference | Purpose | When to Load |
|-----------|---------|--------------|
| `references/context-management.md` | Context window principles, SKILL.md vs references/ load strategy | When splitting skills or managing load |
| `references/skill-self-testing.md` | YAML validation, threshold checks, trigger testing | Before committing a new skill |
| `references/cross-skill-discovery.md` | Skill routing, description patterns, name conventions | When naming or describing a new skill |

---

## Clarifying Questions

Before creating a skill, ask:

1. **What specific task should Claude accomplish?** (The narrower, the better.)

2. **What does Claude already know about this?** (Don't repeat general knowledge.)

3. **What would make this skill successful?** (Define completion criteria.)

## Workflow Coordination

The skill creation workflow has natural phases: clarifying questions → draft → self-test → integration check. When building a skill, treat each phase as a tracked task.

**Phase tracking pattern:**
- Clarifying questions: Gather requirements before spawning any drafting subagent
- Draft subagent: Create the skill file with clear scope
- Self-test: Verify the skill loads and triggers correctly
- Integration check: Confirm it works within the existing skill ecosystem

**Why track here:**
Skill creation is itself a multi-step workflow. When you spawn a subagent to draft a skill, you're delegating a task that has dependencies (requirements must be clear before drafting). Tracking makes the dependency explicit.

**Parallel drafting:**
If multiple skill ideas surface simultaneously, you can spawn parallel drafting subagents — but the orchestrator must track each one and wait for all before moving to integration check.

**Principle:** A skill about coordinated work should demonstrate coordination in its own workflow. Even if you don't spawn subagents for skill creation, framing each phase as a tracked task clarifies what must complete before what.

**For tracking implementation**, load `references/skill-self-testing.md` — it provides YAML validation, threshold checks, and pre-commit verification steps.
