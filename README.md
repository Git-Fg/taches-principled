# TÂCHES Principled

A principle-based Claude Code plugin for building skills, subagents, hooks, and project plans.

**For when** you keep pasting the same instructions into chat, or when CLAUDE.md has grown into a procedure. Each skill teaches you to build better extensions — not by giving you templates and checklists, but by giving you the principles behind them.

## Quick Start

```bash
# Install from GitHub marketplace
/plugin marketplace add felixhopper/taches-principled
/plugin install taches-principled

# Or manual install
cp -r skills/* commands/* agents/* ~/.claude/
```

```bash
# Create a new skill
/create-skill Review code for security vulnerabilities

# Plan a project phase
/create-plan First phase: user authentication

# Audit an existing skill
/audit-skill ~/.claude/skills/my-skill/SKILL.md
```

## What's Inside

### 4 Skills

Skills load on demand and give Claude domain expertise without bloating every conversation.

| Skill | When to Use |
|-------|-------------|
| **create-skills** | Building new skills or improving existing ones |
| **create-subagents** | Creating specialized agents or configuring the Task tool |
| **create-hooks** | Setting up validation, logging, or notification automation |
| **create-plans** | Planning projects, phases, or features for Claude to build |

### 8 Commands

Slash commands for quick, focused workflows.

| Command | What It Does |
|---------|-------------|
| `/create-skill` | Scaffold a new skill |
| `/create-subagent` | Scaffold a new subagent |
| `/create-hook` | Scaffold a new hook |
| `/create-plan` | Scaffold a project plan |
| `/audit-skill` | Evaluate a skill's effectiveness |
| `/audit-subagent` | Evaluate a subagent's routing quality |
| `/debug` | Apply systematic debugging methodology |
| `/whats-next` | Create a handoff for a fresh session |

### 3 Agents

Specialized agents for quality and review work.

| Agent | Purpose |
|-------|---------|
| **code-reviewer** | Reviews code for issues that matter |
| **skill-auditor** | Reviews skills for clarity and routing |
| **subagent-auditor** | Reviews subagents for effectiveness |

## Skills vs Commands

Both create `/name` shortcuts — **they're the same mechanism under the hood**. Commands are simpler flat files; skills are directories with `SKILL.md` that can add auto-invocation, frontmatter controls, and supporting files. A skill with `disable-model-invocation: true` behaves identically to a command.

## Skill Ecosystem

The four skills form a dependency chain from planning through to auditing:

```
create-plans ──→ create-subagents ──→ create-hooks
     │                                   │
     └───────── audit-skill ◄───────────┘
     │
     └── subagent-auditor
```

**Dependency chain:**
- `create-plans` → `create-subagents`: Plans define what needs building; subagents execute plans
- `create-subagents` → `create-hooks`: Subagents may create hooks as part of their output
- `create-hooks` → audit loop: Hooks can be audited for correctness and security

**Policy vs. Mechanism** is the unifying principle across all skills:

| Skill | Policy | Mechanism |
|-------|--------|-----------|
| `create-plans` | What a good plan looks like | How to decompose tasks |
| `create-subagents` | When to spawn vs. delegate | How to construct spawn prompts |
| `create-hooks` | When to intercept | What the hook script does |
| `create-skills` | When to trigger | What the skill teaches |

## The Principle-Based Approach

The old way: prescriptive XML structures and 20-step procedures.

The new way:

1. **Goals over procedures** — State what to achieve, not the steps to get there
2. **Principles over steps** — 3 principles that guide thinking beats a checklist
3. **Trust Claude** — Don't explain what Claude already knows
4. **Concise by default** — Every line competes for context; every line must earn its place
5. **Gotchas, not rules** — "Common mistake: vague descriptions won't route correctly" beats "you must include an objective tag"

This plugin practices what it preaches: skills focus on principles and anti-patterns, not procedures. Each skill teaches the concept in under 200 lines of body text.

## Installation

### Marketplace (recommended)

```bash
/plugin marketplace add felixhopper/taches-principled
/plugin install taches-principled
```

### Manual

```bash
cp -r skills/* ~/.claude/skills/
cp -r commands/* ~/.claude/commands/
cp -r agents/* ~/.claude/agents/

# Verify
ls ~/.claude/skills/
```

## Relationship to taches-cc-resources

This plugin is a direct descendant of [taches-cc-resources](https://github.com/glittercowboy/taches-cc-resources), which introduced valuable structure and organization to Claude Code extensions. The original `taches-cc-resources` (now archived) established the mental models for skills, subagents, hooks, and plans.

**What changed here:** The prescriptive layer was stripped — the XML templates, the step-by-step procedures, and the complexity theater. What remained are the principles that actually guide good decisions.

**Key differences:**
- Skills stripped to essentials: principles and anti-patterns, not templates
- Commands simplified to single-file slash commands
- Domain expertise system excluded (brittle keyword inference)
- Hooks and plans prioritized over MCP (builds on existing MCP tooling instead)

If you're migrating from `taches-cc-resources`, this plugin gives you the same mental models with less friction.

## License

MIT