---
description: Skills extend Claude with task-specific instructions and auto-invocation
when_to_read: When authoring skills, configuring frontmatter, or understanding load behavior
path: ./official/skills.md
---

# Skills - Claude Code Official Documentation

Source: https://code.claude.com/docs/en/skills

## Overview

Skills extend what Claude can do. Create a SKILL.md file with instructions, and Claude adds it to its toolkit. Claude uses skills when relevant, or you can invoke one directly with `/skill-name`.

Create a skill when you keep pasting the same instructions, checklist, or multi-step procedure into chat, or when a section of CLAUDE.md has grown into a procedure rather than a fact. Unlike CLAUDE.md content, a skill's body loads only when it's used, so long reference material costs almost nothing until you need it.

## Where Skills Live

| Location | Path | Applies to |
|---|---|---|
| Enterprise | See managed settings | All users in your organization |
| Personal | `~/.claude/skills/<skill-name>/SKILL.md` | All your projects |
| Project | `.claude/skills/<skill-name>/SKILL.md` | This project only |
| Plugin | `<plugin>/skills/<skill-name>/SKILL.md` | Where plugin is enabled |

---

## Frontmatter Reference

### Complete Field Reference

| Field | Required | Description |
|---|---|---|
| `name` | No | Display name (max 64 chars, lowercase letters, numbers, hyphens). If omitted, derived from directory name |
| `description` | Recommended | What the skill does and when to use it. Combined with `when_to_use`, truncated at 1,536 characters |
| `when_to_use` | No | Additional trigger phrases (appended to description). Counts toward the 1,536-character cap |
| `argument-hint` | No | Hint shown during autocomplete when invoking the skill |
| `arguments` | No | Named positional arguments for `$name` substitution. Accepts a space-separated string or a YAML list |
| `disable-model-invocation` | No | Set `true` to prevent automatic loading. Skill remains invokable by user but Claude will not suggest it |
| `user-invocable` | No | Set `false` to hide from `/` menu. Claude can still invoke automatically |
| `allowed-tools` | No | Pre-approves tools to skip permission prompts (does not restrict availability). CLI-only — ignored in Agent SDK. Accepts space/comma-separated string or YAML list |
| `disallowed-tools` | No | Removes specific tools from the available pool while skill is active |
| `model` | No | Model override when skill is active. Accepts same values as `/model`, or `inherit` to keep active model |
| `effort` | No | Effort level: `low`, `medium`, `high`, `xhigh`, `max` |
| `context` | No | Set to `fork` to run in a forked subagent context |
| `agent` | No | Which subagent type to use when `context: fork` is set |
| `hooks` | No | Hooks scoped to this skill's lifecycle |
| `paths` | No | Glob patterns limiting when skill activates. Accepts a comma-separated string or a YAML list |
| `shell` | No | Shell type: `bash` (default) or `powershell`. Setting `powershell` requires `CLAUDE_CODE_USE_POWERSHELL_TOOL=1` on Windows |

### Field Details

#### description

The primary routing signal. Combined with `when_to_use`, total length capped at 1,536 characters. Truncation happens from the end — front-load important trigger keywords within the first 200 characters.

**Best practices:**
- Use natural language the user would speak
- Front-load trigger keywords users would naturally say
- Avoid technical jargon that users wouldn't use
- Include specific phrases (5-10) rather than generic words

#### when_to_use

Appended to description for additional trigger phrases. Shares the 1,536-character cap. Use for:
- CONTRAST sections (see below)
- Negative cases (what NOT to match)
- Additional trigger scenarios

#### allowed-tools

Pre-approves tools so Claude can use them without permission prompts when this skill is active. Accepts:
- Space-separated: `Read Edit Bash Write`
- Comma-separated: `Read, Edit, Bash, Write`
- YAML list format
- Bash with command filter: `Bash(git:*)`

**Important:** This does NOT restrict which tools are available. Every tool remains callable; normal permission settings still govern tools not listed. To actively block tools, use `disallowed-tools`.

**CLI-only:** This field only takes effect in Claude Code CLI. When skills are used through the Agent SDK, `allowed-tools` is ignored — the SDK's own `allowedTools` parameter controls permissions instead.

When not specified, tool permissions follow normal settings.

#### disallowed-tools

Removes specific tools from Claude's available pool while this skill is active. Use for autonomous skills that should never call certain tools. The restriction clears when the next message is sent.

Example:
```yaml
disallowed-tools: AskUserQuestion
```

#### model

Override the active model when this skill loads. Options:
- Same values as `/model` command (`sonnet`, `opus`, `haiku-4`, etc.)
- `inherit` — keep the currently active model

#### context: fork

Runs the skill in an isolated forked subagent context. The skill's full body becomes the subagent's system prompt. Use with:
- `agent` field to specify subagent type (`general-purpose`, `Explore`, `Plan`)
- Skills preloaded via the agent definition's `skills:` field

The forked context has:
- Fresh conversation history
- Access to files specified in the task scope
- The skill body as its primary directive

#### hooks

Hooks scoped to this skill's lifecycle. Format:
```yaml
hooks:
  PostToolUse:
    - skill-hook-name
```

#### paths

Glob patterns limiting when the skill activates. Useful for project-specific skills:
```yaml
paths: "src/**/*.ts"
```
When a matching path is being edited, the skill becomes eligible for auto-invocation.

---

## String Substitutions

| Variable | Description |
|---|---|
| `$ARGUMENTS` | All arguments passed when invoking the skill |
| `$ARGUMENTS[N]` | Access specific argument by 0-based index (0 = first argument) |
| `$N` | Shorthand for `$ARGUMENTS[N]` |
| `$name` | Named argument value from frontmatter `arguments` field |
| `${CLAUDE_SESSION_ID}` | Current session identifier |
| `${CLAUDE_EFFORT}` | Current effort level (`low`, `medium`, `high`, `xhigh`, `max`) |
| `${CLAUDE_SKILL_DIR}` | Absolute path to the directory containing SKILL.md |

**Example with named arguments:**
```yaml
# In frontmatter:
arguments: mode target
---
# In body:
Use $ARGUMENTS to access all: $ARGUMENTS
Use $name for specific: $mode, $target
```

---

## Skill Content Lifecycle

### Load Behavior

When you or Claude invoke a skill, the rendered SKILL.md content enters the conversation as a single message and stays for the rest of the session. Claude Code does not re-read the skill file on later turns.

### Auto-Compaction

When context approaches limits, auto-compaction activates:
- Invoked skills are preserved within a token budget
- First 5,000 tokens of each skill are kept
- Combined pool limit: 25,000 tokens across all preserved skills
- Compaction happens automatically — no manual trigger needed

### Progressive Disclosure Pattern

Skills support lazy loading of internal references:
```
1. Startup: only name + description loaded into system prompt
2. Trigger: full SKILL.md body enters conversation
3. On-demand: docs/ files read only when body explicitly names them
```

This pattern allows skills to stay under the 500-line guideline while providing deep reference material on demand.

---

## Run Skills in a Subagent

### Basic Usage

Add `context: fork` to run the skill in isolation:

```yaml
context: fork
agent: general-purpose
```

The skill content becomes the subagent's system prompt. The subagent executes the skill's instructions independently.

### With Agent Preloading

An agent definition can preload skills at startup:

```yaml
# In agent definition
skills:
  - skill-name
```

When the agent spawns, the named skill's full SKILL.md body loads immediately — no separate skill invocation needed. Use when the agent's role maps directly to a skill's methodology.

### Context Fork Behavior

When `context: fork` is set:
1. A new subagent instance spawns
2. The subagent receives the skill body as its primary prompt
3. Subagent has fresh conversation history (no parent context)
4. Subagent can access files specified in the task scope
5. Parent agent waits for subagent completion before continuing

This is the recommended pattern for autonomous plugin development workflows.

---

## Control Who Invokes

| Config | You can invoke | Claude can invoke |
|---|---|---|
| (default) | Yes | Yes |
| `disable-model-invocation: true` | **NOT FOR AUTONOMOUS USE** — Prevents Claude from invoking this skill; makes it human-only |
| `user-invocable: false` | No | Yes |

---

## Effort Field

Add `effort` to skill frontmatter to signal expected cognitive load:

| Level | Use Case | Examples |
|-------|----------|----------|
| `low` | Simple edits, one-off questions, quick lookups | "Fix this typo", "Find this function", "What does X do?" |
| `medium` | Multi-file changes, research tasks, moderate complexity | "Add error handling", "Refactor this module", "Investigate this bug" |
| `high` | Complex refactoring, architectural decisions, multi-step workflows | "Redesign the auth system", "Plan this feature", "Review this PR" |
| `xhigh` | Large rewrites, multi-system changes | "Migrate to new framework", "Restructure entire codebase" |
| `max` | Full project creation, major migrations | "Create a new project", "Rewrite from scratch" |

---

## Hub Skills

A hub skill aggregates multiple related modes under one skill with a decision router. Use when:
- Multiple modes serve the same purpose but use different methods
- Trigger phrases overlap significantly and a router disambiguates them
- The skill name describes a domain, not a single action

A hub skill is appropriate at 2-7 modes. Beyond 7, routing degrades — split into separate skills.

### Decision Router Pattern

```markdown
## Decision Router

Based on the user's request, determine which mode applies:

1. **Mode A** — When user says X or describes Y
2. **Mode B** — When user says P or describes Q
3. **Mode C** — When user says M or describes N

If none apply, ask for clarification.
```

### Example: Refine Skill

```markdown
description: Improve code quality — simplify complexity, review for bugs, polish prose
when_to_use: |
  Use when you want to simplify, reduce complexity, review, critique, or polish text.
  CONTRAST with create-plans: create-plans produces new artifacts; refine improves existing ones.
  CONTRAST with diagnose: diagnose investigates broken code; refine improves working code.

## Decision Router

| User says | Mode |
|-----------|------|
| "simplify", "reduce complexity" | SIMPLIFY |
| "review", "check my changes", "critique" | REVIEW |
| "polish", "make clearer", "write more concisely" | POLISH |
| "memorize", "capture this learning" | MEMORIZE |
| Otherwise | Default to SIMPLIFY |
```

### Hub vs Separate Skills

| Pattern | When to Use |
|---------|-------------|
| **Hub-and-spoke** | One domain, different methods, overlapping triggers |
| **Separate skills** | Distinct workflow stages, clear boundaries |

Compositional pairs should remain separate:
- `create-plans` + `execute-plans`
- `create-prompts` + `execute-prompts`
- `refine-task` + `implement-task`

---

## Cross-Skill References

Do NOT reference other skills' internal files with hardcoded paths. Use natural language naming the skill:

| Instead of | Use |
|------------|-----|
| `../../create-plans/docs/X.md` | "see X.md in the create-plans skill" |
| `skills/diagnose/SKILL.md` | "the diagnose skill teaches this method" |
| File paths to other skills | Natural language description |

This is because plugins install to different paths depending on the installation method. Natural language references work regardless of installation location.

### Cross-Skill Reference Patterns

**In CONTRAST sections (preferred):**
```markdown
CONTRAST with diagnose: This skill improves existing code; diagnose finds bugs.
```

**For capability hints:**
```markdown
For quality verification, spawn a critic subagent.
```

**For skill loading:**
```markdown
Load the refine skill for guidance on this task.
```

### Synergy Tiers

| Scope | Reference Pattern |
|-------|-------------------|
| Same skill | Reference freely |
| Same plugin | Reference by name with conditional framing |
| Different plugin | Reference by role, not plugin name |

---

## Skill-Internal References

Use `{baseDir}` for all skill-internal file references:

| Pattern | Example |
|---------|---------|
| Skill-internal | `{baseDir}/agents/critic.md` |
| **Wrong** | `agents/critic.md` |
| **Wrong** | `skills/my-skill/agents/critic.md` |
| **Wrong** | `../../agents/critic.md` |

`{baseDir}` resolves to the skill's directory at load time, regardless of installation location.

### When to Use {baseDir}

- Referencing agents/ templates
- Referencing docs/ files
- Referencing scripts/
- Any internal file within the same skill directory

### When Natural Language Is Appropriate

For conceptual guidance without specific file targets:
- "spawn a critic subagent" (no path needed)
- "follow the reviewer agent template" (generic reference)
- "refer to the format guide" (assumed to be in scope)

---

## CONTRAST Sections

For skills with overlapping trigger phrases, add CONTRAST sections to disambiguate routing.

### Location

CONTRAST sections belong in `when_to_use`, not in the skill body. This keeps routing logic in the routing metadata.

### Format

```yaml
when_to_use: |
  Use when you want to [primary trigger].
  CONTRAST with other-skill: This skill does X; other-skill does Y. Use this when [condition].
  CONTRAST with another-skill: [similar pattern]
```

### Examples

**Simple contrast:**
```yaml
CONTRAST with diagnose: This skill improves existing code; diagnose finds root causes.
```

**With condition:**
```yaml
CONTRAST with create-plans: create-plans produces new artifacts from scratch;
refine improves existing artifacts. Use refine when code already exists.
```

**Multiple contrasts:**
```yaml
CONTRAST with diagnose: This skill improves working code; diagnose investigates broken code.
CONTRAST with create-plans: create-plans makes new things; refine makes existing things better.
```

### When to Add CONTRAST

Add CONTRAST when:
- Two skills could reasonably handle the same trigger
- The trigger phrase is ambiguous
- Users might invoke the wrong skill without guidance

Skip CONTRAST when:
- Skills serve completely different purposes
- Trigger phrases don't overlap
- The overlap is obvious from descriptions alone

---

## Argument Hints

Always add `argument-hint` for skills accepting arguments:

```yaml
argument-hint: "[mode] [target] [--flag value]"
```

### Format Conventions

| Format | Use |
|--------|-----|
| `[value]` | Optional argument |
| `[value1] [value2]` | Multiple optional arguments |
| `value` | Required or positional |
| `--flag value` | Flag with value |

### Examples

| Skill purpose | hint |
|---------------|------|
| Review code changes | `[file or directory]` |
| Run in specific mode | `[mode] [target]` |
| Create with options | `[name] [--template template-name]` |
| Search with filters | `[query] [--lang language] [--limit N]` |
| Transform content | `[input] [output] [--format json]` |

### Tips

- Use bracketed format for clarity
- Be specific — the hint shows during autocomplete
- Keep hints concise — they're meant to guide, not document
- Place required arguments before optional ones

---

## Bundled Skills

> **Note:** These are CLI slash commands for interactive sessions. For autonomous plugin development, use `context: fork` subagents (see "Run Skills in a Subagent" section).

Claude Code includes bundled skills: `/code-review`, `/batch`, `/debug`, `/loop`, `/claude-api`. Bundled skills are prompt-based (give Claude detailed instructions) vs built-in commands (execute fixed logic).

Three bundled skills work together: `/run` (launch app), `/verify` (build and confirm), `/run-skill-generator` (teach /run and /verify how to build/launch).

---

## Share Skills

- **Project skills**: Commit `.claude/skills/` to version control
- **Plugins**: Create `skills/` directory in your plugin
- **Managed**: Deploy organization-wide through managed settings

---

## Skill Listing Budget

Claude Code v2.1.129+ enforces a skill listing budget that affects how skills appear in the system prompt.

### Budget Mechanics

| Setting | Default | Purpose |
|---------|---------|---------|
| `skillListingBudgetFraction` | 0.01 (1%) | Caps total skill metadata at this fraction of context window |
| `skillListingMaxDescChars` | 1536 | Per-skill description character cap |

When budget is exceeded:
1. Descriptions longer than cap are truncated from the end
2. If still over budget, lowest-priority skills lose descriptions entirely
3. Skills may be silently dropped

### Mitigations

- **Compress descriptions**: Target ≤150 characters per description
- **Front-load triggers**: First 50 characters contain primary keywords
- **Use `name-only`**: Set low-priority skills to minimal display in `skillOverrides`
- **Project-scoped**: Move skills to project `.claude/skills/` instead of user `~/.claude/skills/`

---

## Marketplace Conventions (Taches Principled)

These conventions go beyond official Claude Code docs for consistency across the taches-principled marketplace.

### Shell Field

Add `shell: bash` to skill frontmatter for explicit shell specification:
```yaml
shell: bash
```

Even though bash is the default, explicit declaration improves clarity for marketplace plugins.

### Command Format

Commands are lightweight trigger accelerators, not method carriers. Command bodies should:
- Be 1-3 sentences maximum
- Name native capabilities directly (fan out subagents, create a task list, use web search)
- Avoid markdown formatting
- State the outcome, not the method

```bash
# Correct: direct language
Fan out subagents to explore in parallel. Create a task list tracking all items.

# Incorrect: vague language
Divide into independent streams of work. Maintain a visible record of progress.
```

### Skill Budget Checklist

Before shipping any skill to the marketplace:
- [ ] All descriptions ≤150 characters
- [ ] Front-loaded triggers in first 50 characters
- [ ] No skills dropped or truncated (run `/doctor`)
- [ ] Routing tested with real queries

### Artifact Hygiene

All generated artifacts live in `.principled/` — never pollute the codebase:
```
.principled/
├── plans/           # Plans, briefs, roadmaps, phases
├── scratch/        # Debug sessions, temp artifacts
└── memory/         # Architecture state, cross-session notes
```

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Skill not triggering | Check description includes keywords users would naturally say |
| Skill triggers too often | Make description more specific, add `disable-model-invocation: true` |
| Descriptions cut short | Budget scales at 1% of context window; use `skillListingBudgetFraction` or `maxSkillDescriptionChars` settings |
| Skill content not updating | Context re-reads only on invocation; re-invoke the skill to load changes |
| Subagent doesn't see skill changes | Each subagent spawn is fresh; changes apply on next spawn |

---

## Best Practices Summary

1. **Front-load descriptions** — Truncation happens from the end
2. **Use natural language** — Describe what users would say, not technical implementation
3. **Add effort levels** — Help Claude scope expectations
4. **Include argument hints** — Guide users during skill invocation
5. **Use {baseDir}** — For all skill-internal file references
6. **Natural language for cross-skill** — Never hardcode paths to other skills
7. **CONTRAST for disambiguation** — Place in `when_to_use`, not body
8. **Hub skills for related modes** — Use decision routers for 2-7 modes
9. **Context: fork for isolation** — Use for autonomous workflows
10. **Test routing** — Verify skills trigger correctly with real queries