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
| /submit | Submit completed work |

## Bundled Skills

Claude Code includes bundled skills (marked **Skill** in the purpose column):
- `/code-review` - Review code [INTERACTIVE ONLY — Expects human conversation]
- `/batch` - Batch operations
- `/debug` - Debug issues
- `/loop` - Looping workflows
- `/claude-api` - API interactions

## Creating Custom Commands

Commands can be created as:
1. **Commands** (`.claude/commands/`): Simple `.md` files
2. **Skills** (`.claude/skills/<name>/SKILL.md`): More powerful with frontmatter control

Commands and skills with the same name - the skill takes precedence.

## `/agents` Command [INTERACTIVE ONLY — Opens tabbed UI, not usable in autonomous scripts]

Opens tabbed interface:
- **Running tab**: Shows live subagents, open or stop them
- **Library tab**: View, create, edit, delete subagents

## Model Switching

Use `/model` command to switch between available models. [INTERACTIVE ONLY — Human operator command]

## Permission Commands

- `/permissions` - Manage tool permissions [INTERACTIVE ONLY — Requires human decision-making]
- Permissions can be auto-accepted with `acceptEdits` mode

## Context Management

- `/compact` - Manually trigger context compaction
- `/clear` - Clear conversation context

## Workflow Commands

Grouped by when they are used in the workflow:

### Before you ship
- `/submit` - Submit completed work [INTERACTIVE ONLY — Human review and approval required]

### Between sessions
- `/compact` - Manually trigger context compaction
- `/clear` - Clear conversation context

### When something is wrong
- `/permissions` - Manage tool permissions [INTERACTIVE ONLY — Requires human decision-making]
- `/debug` - Debug issues [INTERACTIVE ONLY — Expects human conversation]

### General
- `/help` - Get help with Claude Code [INTERACTIVE ONLY]
- `/init` - Initialize project with a CLAUDE.md guide [INTERACTIVE ONLY — Expects human input during setup]
- `/model` - Switch between available models

## MCP Prompts

MCP servers can define prompts - reusable prompt templates that Claude can invoke. When an MCP server is configured, its prompts appear in the `/prompts` interface and can be used like any other command.