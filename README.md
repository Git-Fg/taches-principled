# TACHES Principled

**Version:** 0.9.0

A principle-based Claude Code plugin for building skills, subagents, hooks, and project plans.

**For when** you keep pasting the same instructions into chat, or when CLAUDE.md has grown into a procedure. Each skill teaches you to build better extensions — not by giving you templates and checklists, but by giving you the principles behind them.

## Quick Start

```bash
# Install from GitHub marketplace
/plugin marketplace add Git-Fg/taches-principled
/plugin install taches-principled
```

### Essential Commands

```bash
# Create a new skill
/skill create-skills

# Plan a project phase
/skill create-plans

# Debug an issue
/debug <issue description>

# Simplify code
/simplify [file-pattern]

# Create a handoff for the next session
/whats-next
```

**Note:** Most skills load automatically when their description matches your task. Only `/debug`, `/simplify`, and `/whats-next` are explicit slash commands. All others route by description.

## What's Inside

### 23 Skills

Skills load on demand and give Claude domain expertise without bloating every conversation.

| Skill | When to Use |
|-------|-------------|
| **create-skills** | Building new skills or improving existing ones |
| **create-plans** | Planning projects, phases, or features for Claude to build |
| **create-prompts** | Creating executable prompts for Claude Code sessions |
| **execute-prompts** | Executing prompts via delegated sub-tasks |
| **execute-plans** | Executing PLAN.md files via parallel subagent orchestration |
| **subagent-orchestration** | Designing and orchestrating multi-agent systems |
| **add-task** | Capturing a task idea for structured development |
| **ideation** | Generating and refining ideas systematically |
| **implement-task** | Implementing refined task specs with verification |
| **diagnose** | Systematic problem investigation |
| **refine** | Quality improvement hub |
| **kaizen** | Continuous improvement with multiple methods |
| **plan-do-check-act** | Iterative experimentation cycles |
| **refine-task** | Refining draft specs into implementation-ready tasks |
| **update-docs** | Maintaining project documentation |
| **skill-creator** | Editing and optimizing existing skills |
| **claude-headless** | Batch and headless Claude Code workflows |
| **tool-design** | Designing agent tools and MCP integrations |
| **multi-agent-patterns** | Designing multi-agent system architectures |
| **security** | Security-first code review and threat modeling |
| **test** | Test strategy and automation patterns |
| **archive-plan** | Archiving completed plan artifacts |
| **rules-orchestration** | Managing CLAUDE.md and rules lifecycle |

### 14 Commands

Slash commands for quick, focused workflows.

| Command | What It Does |
|---------|-------------|
| `/debug` | Apply systematic debugging methodology |
| `/whats-next` | Create a handoff for a fresh session |
| `/simplify` | Simplify and refine recently modified code |
| `/implement` | Execute task implementation with verification |
| `/improve` | Improve the quality of any artifact |
| `/critique` | Get independent multi-perspective critique |
| `/learn` | Capture insights into durable project memory |
| `/polish` | Improve prose clarity and conciseness |
| `/orchestrate` | Orchestrate parallel subagent execution |
| `/design-subagents` | Design multi-agent architectures |
| `/ideate` | Enter divergent creative thinking mode |
| `/next-tasks-orchestration` | Implement changes with quality gates |
| `/rules` | Manage CLAUDE.md and rules lifecycle |
| `/archive` | Archive completed plan artifacts |

### 13 Agents

Specialized agents for quality, review, and evaluation work.

| Agent | Purpose |
|-------|---------|
| **analyzer** | Synthesizes evaluation results into improvement plans |
| **code-reviewer** | Reviews code for issues that matter |
| **comparator** | Compares skill versions for delta analysis |
| **critic** | Independent critique with severity scoring |
| **debug-tracer** | Systematic debugging and root cause tracing |
| **grader** | Evaluates skill teaching effectiveness |
| **implementer** | Quality-gated task implementation |
| **prompt-engineer** | Reviews prompts for clarity and effectiveness |
| **researcher** | Multi-source investigation and synthesis |
| **self-critic** | Self-review with severity scoring |
| **self-review** | Independent quality verification |
| **skill-auditor** | Reviews skills for clarity and routing |
| **subagent-auditor** | Reviews subagents for effectiveness |

### 6 Marketplace Plugins

Six standalone plugins, each independently installable:

| Plugin | Focus |
|-------|-------|
| **tp-sadd** | Structured agent-driven development with meta-judge verification |
| **tp-fpf** | First Principles Framework for hypothesis-driven decisions |
| **tp-git** | Git workflow automation for commits, PRs, and issues |
| **tp-tdd** | Test-driven development with red-green-refactor cycles |
| **tp-ddd** | Domain-driven design guardrails and conventions |
| **tp-force-multiplier** | Hook-driven coaching for subagent and skill usage |

## Installation

### Prerequisites

- Claude Code with plugin support
- Verify with `/version`

### Marketplace (recommended)

```bash
/plugin marketplace add Git-Fg/taches-principled
/plugin install taches-principled
```

### Manual

```bash
# If you cloned the repository
cp -r plugins/taches-principled/skills/* ~/.claude/skills/
cp -r plugins/taches-principled/commands/* ~/.claude/commands/
cp -r plugins/taches-principled/agents/* ~/.claude/agents/

# If you downloaded a release
# Copy skills/, commands/, and agents/ contents to ~/.claude/

# Verify
ls ~/.claude/skills/
```

## Hub-and-Spoke Skills

Some skills bundle related modes under one name:

| Skill | Modes |
|-------|-------|
| **refine** | simplify, review, critique, memorize, polish |
| **subagent-orchestration** | design, orchestrate |
| **diagnose** | A3, five-whys, fishbone, stack-trace, auto |
| **sadd** | compete, execute, judge, design, explore |
| **fpf** | propose, maintain, query |
| **git** | ship, review, issues, advanced |
| **ddd** | architecture, quality, transparency |

## Principles

The old way: prescriptive XML structures and 20-step procedures.

The new way:

1. **Goals over procedures** — State what to achieve, not the steps to get there
2. **Principles over steps** — 3 principles that guide thinking beats a checklist
3. **Trust Claude** — Don't explain what Claude already knows
4. **Concise by default** — Every line competes for context; every line must earn its place
5. **Gotchas, not rules** — "Common mistake: vague descriptions won't route correctly" beats "you must include an objective tag"

This plugin practices what it preaches: skills focus on principles and anti-patterns, not procedures.

## Relationship to taches-cc-resources

This plugin is a direct descendant of [taches-cc-resources](https://github.com/glittercowboy/taches-cc-resources), which introduced valuable structure and organization to Claude Code extensions.

**What changed here:** The prescriptive layer was stripped — the XML templates, the step-by-step procedures, and the complexity theater. What remained are the principles that actually guide good decisions.

If you're migrating from `taches-cc-resources`, this plugin gives you the same mental models with less friction.

## Troubleshooting

- **Command not found?** Run `/skills` to see all available skills.
- **Skill not loading?** Make sure the description matches — skills route by description, not alias.
- **Developer issues?** See [CLAUDE.md](./CLAUDE.md) for contribution guidelines.

## License

MIT