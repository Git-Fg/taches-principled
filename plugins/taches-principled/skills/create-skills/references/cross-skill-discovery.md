# Cross-Skill Discovery

## Sections
- [Discovery Mechanism](#discovery-mechanism)
- [Description-Based Routing](#description-based-routing)
- [when_to_use Exclusion](#when_to_use-exclusion)
- [Skill Name Conventions](#skill-name-conventions)
- [Orchestrator Skills](#orchestrator-skills)
- [Skill Directories](#skill-directories)
- [Self-Contained Principle](#self-contained-principle)
- [Discovery Testing](#discovery-testing)
- [Skill Priority](#skill-priority)
- [What Belongs in Skills](#what-belongs-in-skills)

---

How skills are discovered, routed, and composed.

---

## Discovery Mechanism

Skills load via trigger methods (OR'd):

1. **Explicit:** `/skill-name` or `Skill` tool call
2. **Auto-match:** Fuzzy description ≈ user query (model decides relevance)
3. **Path-scoped:** `paths` glob matches current file being edited
4. **Model invocation:** Skill loads unless `disable-model-invocation: true`

---

## Description-Based Routing

The `description` field is the primary routing signal.

**Format:**
```
"[Verb] [artifact] for [domain]. Use when [trigger1], [trigger2]."
```

**Example:**
```yaml
description: "Create Claude Code skills. Use when building new skills, improving existing ones, or understanding skill best practices."
```

Claude reads this and decides: "This matches a request about creating skills."

---

## when_to_use Exclusion

The `when_to_use` field clarifies boundaries:

```yaml
when_to_use: |
  Do NOT use for writing general code, creating subagents, or configuring hooks/MCP servers.
```

This prevents misrouting to wrong skills.

---

## Skill Name Conventions

**Good:** `create-skills`, `security-auditor`, `code-reviewer`
- Clear role signal
- Predictable naming pattern

**Bad:** `helper`, `assistant`, `do-stuff`
- No specialization
- Triggers on everything

---

## Orchestrator Skills

Only skills ending in `-orchestrator` should reference other skills.

**Why:** Orchestrators compose. Other skills should be self-contained.

**Example:** An orchestrator skill can reference multiple design/orchestration skills because its job IS composition.

**Non-orchestrator rule:** A skill should NOT mention other skill names in its body text or references — that creates a dependency that breaks when skills are renamed.

---

## Skill Directories

```
skill-name/
├── SKILL.md              # Principles, routing (required)
├── workflows/            # Step-by-step (optional)
├── references/          # Domain knowledge (optional)
├── templates/            # Output structures (optional)
└── scripts/             # Executable code (optional)
```

Simple skills → single SKILL.md file
Complex skills → directories with supporting materials

---

## Self-Contained Principle

**A skill must be loadable and useful on its own.**

If you remove all other skills from the system, this skill should still make sense. It should not rely on reading other skill files to understand what it does.

---

## Discovery Testing

To verify a skill is discoverable:

```bash
# Test 1: Does skill trigger on matching input?
claude -p --dangerously-auto-accept --system PromptFromSkill \
  "I want to create a new skill" \
  2>/dev/null | grep -i "create-skills"

# Test 2: Does off-topic input avoid trigger?
claude -p --dangerously-auto-accept --system PromptFromSkill \
  "fix my css styling" \
  2>/dev/null | grep -c "create-skills"
# Should return 0
```

---

## Skill Priority

When multiple skills match, priority order:

1. Enterprise (organization-managed)
2. Personal (`~/.claude/skills/`)
3. Project (`.claude/skills/`)
4. Plugin (`{plugin}/skills/`)

Higher priority wins conflicts.

---

## What Belongs in Skills

**Yes:**
- Policy (when to trigger)
- Core mechanism (key insight)
- Anti-Patterns (concrete examples)
- Numeric thresholds with rationale
- One good example

**No:**
- References to other skills' internal files with paths (e.g., `skills/create-plans/references/X.md`)
- Step-by-step procedures (use workflows instead)
- Enumeration of tool names (descriptions over lists)
- Invented frontmatter fields