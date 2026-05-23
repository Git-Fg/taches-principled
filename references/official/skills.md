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

## Frontmatter Reference

| Field | Required | Description |
|---|---|---|
| `name` | No | Display name (max 64 chars, lowercase letters, numbers, hyphens) |
| `description` | Recommended | What the skill does and when to use it |
| `when_to_use` | No | Additional trigger phrases (appended to description) |
| `argument-hint` | No | Hint shown during autocomplete |
| `arguments` | No | Named positional arguments for `$name` substitution |
| `disable-model-invocation` | No | Set `true` to prevent automatic loading |
| `user-invocable` | No | Set `false` to hide from `/` menu |
| `allowed-tools` | No | Tools Claude can use without prompting |
| `model` | No | Model override when skill is active |
| `effort` | No | Effort level: `low`, `medium`, `high`, `xhigh`, `max` |
| `context` | No | Set to `fork` to run in a forked subagent context |
| `agent` | No | Which subagent type to use when `context: fork` is set |
| `hooks` | No | Hooks scoped to this skill's lifecycle |
| `paths` | No | Glob patterns limiting when skill activates |
| `shell` | No | `bash` (default) or `powershell` |

## String Substitutions

| Variable | Description |
|---|---|
| `$ARGUMENTS` | All arguments passed when invoking the skill |
| `$ARGUMENTS[N]` | Access specific argument by 0-based index |
| `$N` | Shorthand for `$ARGUMENTS[N]` |
| `$name` | Named argument from frontmatter |
| `${CLAUDE_SESSION_ID}` | Current session ID |
| `${CLAUDE_EFFORT}` | Current effort level |
| `${CLAUDE_SKILL_DIR}` | Directory containing SKILL.md |

## Skill Content Lifecycle

When you or Claude invoke a skill, the rendered SKILL.md content enters the conversation as a single message and stays for the rest of the session. Claude Code does not re-read the skill file on later turns.

Auto-compaction carries invoked skills forward within a token budget (first 5,000 tokens of each, 25,000 combined pool).

## Run Skills in a Subagent

Add `context: fork` to run in isolation. The skill content becomes the prompt for the subagent.

## Control Who Invokes

| Config | You can invoke | Claude can invoke |
|---|---|---|
| (default) | Yes | Yes |
| `disable-model-invocation: true` | Yes | No |
| `user-invocable: false` | No | Yes |

## Bundled Skills

Claude Code includes bundled skills: `/code-review`, `/batch`, `/debug`, `/loop`, `/claude-api`. Bundled skills are prompt-based (give Claude detailed instructions) vs built-in commands (execute fixed logic).

Three bundled skills work together: `/run` (launch app), `/verify` (build and confirm), `/run-skill-generator` (teach /run and /verify how to build/launch).

## Share Skills

- **Project skills**: Commit `.claude/skills/` to version control
- **Plugins**: Create `skills/` directory in your plugin
- **Managed**: Deploy organization-wide through managed settings

## Troubleshooting

- **Skill not triggering**: Check description includes keywords users would naturally say
- **Skill triggers too often**: Make description more specific, add `disable-model-invocation: true`
- **Descriptions cut short**: Budget scales at 1% of context window; use `skillListingBudgetFraction` or `maxSkillDescriptionChars` settings