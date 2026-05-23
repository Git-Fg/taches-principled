# Commands - Claude Code Official Documentation

Source: https://code.claude.com/docs/en/commands

## Overview

Commands control Claude Code from inside a session. They provide a quick way to switch models, manage permissions, clear context, run a workflow, and more.

## How Commands Work

Commands start with `/` and are processed before the message is sent to Claude. Custom commands are now merged into skills - files at `.claude/commands/deploy.md` and `.claude/skills/deploy/SKILL.md` both create `/deploy` and work the same way.

## Command Types

| Type | Description |
|---|---|
| Built-in commands | Fixed logic, execute directly |
| Bundled skills | Prompt-based, detailed instructions for Claude to orchestrate |

## Bundled Skills

Claude Code includes bundled skills (marked **Skill** in the purpose column):
- `/code-review` - Review code
- `/batch` - Batch operations
- `/debug` - Debug issues
- `/loop` - Looping workflows
- `/claude-api` - API interactions

## Creating Custom Commands

Commands can be created as:
1. **Commands** (`.claude/commands/`): Simple `.md` files
2. **Skills** (`.claude/skills/<name>/SKILL.md`): More powerful with frontmatter control

Commands and skills with the same name - the skill takes precedence.

## `/agents` Command

Opens tabbed interface:
- **Running tab**: Shows live subagents, open or stop them
- **Library tab**: View, create, edit, delete subagents

## Model Switching

Use `/model` command to switch between available models.

## Permission Commands

- `/permissions` - Manage tool permissions
- Permissions can be auto-accepted with `acceptEdits` mode

## Context Management

- `/compact` - Manually trigger context compaction
- `/clear` - Clear conversation context

## Workflow Commands

- `/help` - Get help with Claude Code
- `/init` - Analyze codebase for build systems and patterns
- `/submit` - Submit completed work