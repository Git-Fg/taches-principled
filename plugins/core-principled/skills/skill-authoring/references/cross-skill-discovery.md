# Cross-Skill Discovery Reference

Skill routing, description patterns, name conventions, and how Claude Code matches skills to tasks.

## How Skill Discovery Works

**Discovery is metadata-only.** Claude decides which skill to load based exclusively on the text pre-injected into its system prompt. At the moment of routing, the skill body is invisible.

**Routing participants — fields only:**
- `description` + `when_to_use` from SKILL.md frontmatter
- Agent `description` (NOT the body prompt)
- Command `description`

---

## Description Writing

### The Description is a Routing Prompt

Write for the model's linguistic reasoning — a good description triggers for "generate a presentation" even without the word "pptx".

### Optimal Description Template

```yaml
description: "[Verb] [artifact] for [domain]. Use when user [trigger1], [trigger2], or [trigger3]."
when_to_use: |
  Do NOT use for [exclusion1], [exclusion2].
```

### Character Limits

| Field | Limit | Why |
|-------|-------|-----|
| description | ≤1,024 chars (max) | Official limit; use the full space |
| description | ≤150 chars (recommended) | Survives truncation in high-context sessions |
| when_to_use | ≤200 chars | Longer = context bloat, not better routing |

### Front-Loading Triggers

**Critical:** Put trigger keywords in the first 200 characters. Descriptions are truncated from the end when context budget is tight.

| Good (trigger at start) | Bad (trigger at end) |
|------------------------|---------------------|
| "Reviews code for bugs. Use when user says 'review', 'check', or 'audit'" | "This skill helps with reviewing code when you want to check for bugs and issues in your PRs and scattered files" |

---

## Trigger Keywords

### User Vocabulary Matters

Describe what the user says, not how the skill works internally:

| Instead of (internal) | Use (user vocabulary) |
|----------------------|----------------------|
| "Uses A3 methodology" | "Documents root causes" |
| "Complete test lifecycle" | "Writes tests first" |
| "Implements CQRS pattern" | "Splits read/write operations" |

### Specific Phrases Over Generic Words

| Generic (triggers everything) | Specific (triggers correctly) |
|------------------------------|------------------------------|
| "improve" | "optimize query performance" |
| "fix" | "fix null pointer" |
| "help" | (avoid entirely) |
| "handle" | "handle authentication errors" |

### Number of Triggers

Include 3-10 specific trigger phrases. Fewer than 3 may miss legitimate uses; more than 10 dilutes signal.

---

## CONTRAST Sections

For skills in overlapping domains, add explicit negative cases:

```yaml
description: "Generates test cases. Use when user asks to 'write tests', 'add test coverage', or 'generate tests'."
when_to_use: |
  Do NOT use for running existing tests or test execution.
```

---

## Name Conventions

### Skill Names

- **Format:** kebab-case, lowercase letters and hyphens only
- **Max length:** 64 characters
- **Forbidden:** XML tags, "claude", "anthropic"
- **Content:** Semantic noun describing what the skill does

| Wrong | Right |
|-------|-------|
| "Helper" | "code-review" |
| "DoTheThing" | "deploy-staging" |
| "complex-workflow-skill" | "plan-execution" |

### Name vs. Description

The name (directory name) sets the command. The `name` frontmatter field sets the display label.

| Location | Name Source | Example |
|----------|-------------|---------|
| `~/.claude/skills/deploy/` | Directory name | `/deploy` |
| `.claude/commands/deploy.md` | File name | `/deploy` |
| `skills/review/SKILL.md` in plugin `my-plugin` | Directory name, namespaced | `/my-plugin:review` |

---

## Routing Anti-Patterns

| Anti-Pattern | Why It Fails | Fix |
|--------------|--------------|-----|
| Technical jargon in description | User won't say "CQRS" | Use user vocabulary |
| Single ambiguous words | Matches everything | Be specific |
| No negative cases | Triggers on similar-but-wrong | Add CONTRAST |
| Missing trigger phrases | Model can't guess | Add explicit phrases |
| Structured syntax ("ACTIVATES:") | Breaks fuzzy semantic matching | Plain text only |
| Overly broad triggers | False positives | Narrow the action verb |
| Description >200 chars | Truncated mid-signal | Front-load triggers |

---

## Routing Validation

### Test Pattern

```bash
# Should match - test multiple phrasings
claude -p "generate a presentation" --output-format stream-json 2>&1 | grep -i "skill-name"
claude -p "make slides" --output-format stream-json 2>&1 | grep -i "skill-name"

# Should NOT match - test false positives
claude -p "what is the weather" --output-format stream-json 2>&1 | grep -i "skill-name"
```

### The Trigger Testing Loop

1. Write candidate description
2. Test with 10+ queries (5 should trigger, 5 should not)
3. Analyze misses and false positives
4. Refine description
5. Repeat until trigger rate >90%, false positive rate <10%

---

## Skill Interaction Patterns

### Hub Skills

Skills that dispatch to internal modes should name the modes explicitly:

```yaml
---
description: "Create or refine project plans. Use when user says 'make a plan', 'plan this', or 'sketch a roadmap'."
---
## Routing

IF creating → load CREATE mode
IF refining → load REFINE mode
```

### Compositional Pairs

Pairs that create then execute should be clearly named:

| Create | Execute |
|--------|---------|
| `create-plans` | `execute-plans` |
| `task-lifecycle` (REFINE mode) | `task-lifecycle` (IMPLEMENT mode) |

### Cross-Skill References

When referencing other skills in body text, use the skill name (not the file path):

| Wrong | Right |
|-------|-------|
| "use the skill-authoring skill for guidance" | "use the skill-authoring skill for guidance" |

---

## Skill Discovery Limitations

### Nesting Limit

Automatic discovery scans only 1 level deep. Skills nested 2+ levels deep require manual Glob scanning:

| Structure | Discoverable | Notes |
|-----------|-------------|-------|
| `skills/skill-name/SKILL.md` | Yes | Standard |
| `skills/category/skill-name/SKILL.md` | **No** | 2 levels deep, requires manual scan |

### Discovery Timing

- Skills load at session start
- Edits to skill files take effect within current session
- New skill directories require session restart to be watched

---

## Skill Priority

When multiple skills could match, Claude Code resolves by:

1. **Enterprise** (org-wide) — highest priority
2. **Personal** (`~/.claude/skills/`)
3. **Project** (`.claude/skills/`)
4. **Plugin** (`skills/` directory) — lowest priority

Plugin skills use namespace prefix to prevent conflicts: `/my-plugin:skill-name`