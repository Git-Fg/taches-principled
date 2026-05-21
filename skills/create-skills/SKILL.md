---
name: create-skills
description: "Create Claude Code skills. Use when building new skills, improving existing ones, or understanding skill best practices."
when_to_use: |
  Do NOT use for writing general code, creating subagents, or configuring hooks/MCP servers.
---

## Decision Router

IF naming or describing a skill → FIRST read `references/cross-skill-discovery.md`
IF skill might exceed 500 lines or 7 tools → IMMEDIATELY read `references/context-management.md`
IF about to commit a new skill → BEFORE commit read `references/skill-self-testing.md`

---

## Success Criteria

A skill succeeds when:
- **Triggers unambiguously**: Description matches only intended inputs, no false positives
- **Skips silently**: Incorrect inputs produce no skill loading
- **Fits in context**: Under 500 lines, under 7 tools, single focus
- **Teaches judgment**: Enables decisions, not just steps

A skill fails when Claude cannot decide whether to load it.

---

## What This Skill Teaches

Skills encode domain-specific judgment — when to act, how to decide, what "done" looks like. This separates domain knowledge from general knowledge:

| General Knowledge (Don't Explain) | Domain Judgment (Teach This) |
|-----------------------------------|------------------------------|
| What skills are, how context works | Trigger patterns for this domain |
| Tool syntax and parameters | Success metrics and completion criteria |
| Claude's capabilities | Decomposition logic and tradeoffs |

If your skill teaches what Claude already knows, it has no value.

---

## Policy vs. Mechanism

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

Tests reveal how code actually fails, not just that it works — edge cases expose the gaps between intended design and real-world input. These categories organize that lens: boundary conditions probe the edges of valid input, error paths verify graceful degradation, and happy/failure paths confirm core logic under expected and unexpected conditions alike.

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

# Specialist Type Subagent

You are a [role] specializing in [domain].

## Role

[Brief description of what this agent does and why it exists]

## Approach

1. [Step 1 with action verb]
2. [Step 2 with action verb]
3. [Step 3 with action verb]

## Focus Areas

- [Area 1]
- [Area 2]
- [Area 3]

## Output Format

Return structured findings:

```markdown
## [Section]

[Content]
```

## Constraints

- [Hard constraint 1]
- [Hard constraint 2]

---

**Spawned by:** [orchestrator name]
**Context provided:** {{context}}
**Scope:** {{scope}}
**Task:** {{task}}
```

The frontmatter provides the routing signal. The H1 title establishes identity. `## Approach` provides numbered steps. `## Focus Areas` scopes the investigation. The footer is a mandatory handoff convention with domain-specific variables.

### Semantic Reference Pattern

When SKILL.md delegates to an agent file, reference it semantically — not with JSON or tool syntax:

> "Delegate to the explorer agent to map the project structure. Read `agents/explorer.md` for the agent briefing and pass it alongside the task context."

The skill body describes intent and scope. The agent file provides the executable prompt. This separation keeps SKILL.md readable and agent prompts portable.

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

**Unifying principle:** All anti-patterns share low routing signal density — they give Claude no basis to distinguish this skill from others. All correct patterns share high routing signal density — they give Claude specific, unambiguous triggers that make routing decisions obvious.

### Vague description that won't route
"Helps with coding tasks" — triggers on everything, means nothing.

WHY: Without specific trigger phrases, Claude has no basis to decide
when to load this skill vs. another. Vague descriptions provide no
routing signal, making the skill invisible to the trigger system.

### Specific description with trigger keywords
"Creates unit tests with edge cases. Use when user asks to 'write tests', 'add test coverage', or 'generate tests'."

WHY: Specific phrases like "'write tests'" and "'add test coverage'" give Claude
concrete anchor points for the trigger matching algorithm. Each phrase maps to a
specific user intent. When a user says "write tests," Claude can route with
confidence. Generic phrases like "helps with coding" match everything and nothing.

### Overloaded skill doing too much
A single skill that handles skill creation, agent configuration, AND hook setup has no clear identity.

WHY: Routing is a classification problem — Claude must decide whether the
current task matches this skill's domain. When a skill covers three unrelated
domains, the trigger description must either enumerate all of them (making it
vague) or focus on one (making it incomplete). Either way, the match score for
any given task becomes ambiguous. Specificity requires bounded scope.

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

WHY: The name "security-audit" is a noun describing a domain, not a verb
describing an action. This allows Claude to match it against any user utterance
mentioning that domain — "check for security issues," "audit this code," "look
for XSS." A name like "helper" or "assistant" has no semantic anchor point.

## Reference Index

Load a reference only when working on that specific aspect — do not load all upfront. The skill body provides what you need for typical cases; references are for deeper dives.

| Reference | Purpose | When to Load |
|-----------|---------|--------------|
| `references/context-management.md` | Context window principles, SKILL.md vs references/ load strategy | If you're about to add content to SKILL.md and suspect it might exceed 500 lines or 7 tools |
| `references/skill-self-testing.md` | YAML validation, threshold checks, trigger testing | If you've finished a draft and want to verify it passes threshold checks before committing |
| `references/cross-skill-discovery.md` | Skill routing, description patterns, name conventions | If your skill's description triggers on things it shouldn't OR fails to trigger on things it should |

---

## Workflow Principle

Skill creation follows phases: requirements → draft → verify → integrate. Each phase is a decision point — proceed when criteria are met, not on a schedule.

**Principle over procedure:** A skill about coordinated work should demonstrate coordination. Frame each phase as a tracked task with clear completion criteria. Trust the agent to determine execution order from the principles, not from scripted steps.

For pre-commit verification of threshold checks, load `references/skill-self-testing.md`.
