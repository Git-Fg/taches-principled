# TACHES Principled

**Version:** 0.9.0

A Claude Code plugin for building skills, subagents, hooks, and project plans.

**For when** you keep pasting the same instructions into chat, or when CLAUDE.md has grown into a procedure. Each skill teaches you to build better extensions — not by giving you templates and checklists, but by giving you the principles behind them.

## Quick Start

```bash
/plugin marketplace add Git-Fg/taches-principled
/plugin install taches-principled
```

### Try These First

```bash
/debug <issue>        # Debug a problem
/simplify [file]     # Simplify code
/skill create-plans   # Plan a project
```

Most skills load automatically when their description matches your task. Only `/debug`, `/simplify`, and `/whats-next` are explicit slash commands.

## What You Get

### 23 Skills

Skills load on demand and give Claude domain expertise without bloating every conversation.

| Skill | When to Use |
|-------|-------------|
| **skill-authoring** | Building new skills or improving existing ones |
| **create-plans** | Planning projects, phases, or features for Claude to build |
| **create-prompts** | Creating executable prompts for Claude Code sessions |
| **execute-prompts** | Executing prompts via delegated sub-tasks |
| **execute-plans** | Executing PLAN.md files via parallel subagent orchestration |
| **subagent-orchestration** | Designing and orchestrating multi-agent systems |
| **diagnose** | Systematic problem investigation |
| **refine** | Quality improvement (simplify, review, critique, memorize, polish) |
| **ideation** | Generating and refining ideas systematically |
| **add-task** | Capturing a task idea for structured development |
| **implement-task** | Implementing refined task specs with verification |
| **refine-task** | Refining draft specs into implementation-ready tasks |
| **update-docs** | Maintaining project documentation |
| **skill-authoring** | Editing and optimizing existing skills |
| **claude-headless** | Batch and headless Claude Code workflows |
| **tool-design** | Designing agent tools and MCP integrations |
| **security** | Security-first code review and threat modeling |
| **test** | Test strategy and automation patterns |
| **multi-agent-patterns** | Designing multi-agent system architectures |
| **kaizen** | Continuous improvement with multiple methods |
| **plan-do-check-act** | Iterative experimentation cycles |
| **archive-plan** | Archiving completed plan artifacts |
| **rules-orchestration** | Managing CLAUDE.md and rules lifecycle |

### 14 Commands

Slash commands for quick, focused workflows.

| Command | What It Does |
|---------|-------------|
| `/debug` | Apply systematic debugging methodology |
| `/simplify` | Simplify and refine recently modified code |
| `/implement` | Execute task implementation with verification |
| `/critique` | Get independent multi-perspective critique |
| `/learn` | Capture insights into durable project memory |
| `/polish` | Improve prose clarity and conciseness |
| `/orchestrate` | Orchestrate parallel subagent execution |
| `/whats-next` | Create a handoff for the next session |
| `/design-subagents` | Design multi-agent architectures |
| `/ideate` | Enter divergent creative thinking mode |
| `/next-tasks-orchestration` | Implement changes with quality gates |
| `/rules` | Manage CLAUDE.md and rules lifecycle |
| `/archive` | Archive completed plan artifacts |
| `/improve` | Improve the quality of any artifact |

### 13 Agents

Specialized agents for quality, review, and evaluation work.

| Agent | Purpose |
|-------|---------|
| **analyzer** | Synthesizes evaluation results into improvement plans |
| **code-reviewer** | Reviews code for issues that matter |
| **grader** | Evaluates skill teaching effectiveness |
| **implementer** | Quality-gated task implementation |
| **researcher** | Multi-source investigation and synthesis |
| **critic**, **self-critic**, **self-review** | Independent critique and quality verification |
| **skill-auditor**, **subagent-auditor** | Reviews skills and subagents for effectiveness |
| **comparator** | Compares skill versions for delta analysis |
| **prompt-engineer** | Reviews prompts for clarity and effectiveness |
| **debug-tracer** | Systematic debugging and root cause tracing |

### 6 Marketplace Plugins

Six standalone plugins, each independently installable. Each extends the core with specialized capabilities.

| Plugin | Focus |
|-------|-------|
| **tp-sadd** | Structured agent-driven development with meta-judge |
| **tp-fpf** | First Principles Framework for hypothesis-driven decisions |
| **tp-git** | Git workflow automation |
| **tp-tdd** | Test-driven development with red-green-refactor |
| **tp-ddd** | Domain-driven design guardrails |
| **tp-force-multiplier** | Hook-driven coaching for subagent and skill usage |

## Installation

### Prerequisites

- Claude Code with plugin support (`claude --version` >= 2.1)
- Verify with `claude --version`

### Full Marketplace Setup

Install the marketplace and all plugins in one go:

```bash
# Add the marketplace
claude plugin marketplace add anthropics/claude-plugins-official
claude plugin marketplace add Git-Fg/taches-principled

# Install all plugins
claude plugin install claude-md-management
claude plugin install code-simplifier
claude plugin install typescript-lsp
claude plugin install taches-principled
claude plugin install tp-ddd
claude plugin install tp-fpf
claude plugin install tp-git
claude plugin install tp-sadd
claude plugin install tp-tdd
```

### Individual Plugin Installation

Install only the plugins you need:

```bash
# Core plugin (required)
claude plugin install taches-principled

# Optional plugins
claude plugin install tp-ddd     # Domain-driven design
claude plugin install tp-fpf     # First principles reasoning
claude plugin install tp-git     # Git workflow automation
claude plugin install tp-sadd   # Structured agent-driven development
claude plugin install tp-tdd    # Test-driven development
```

### Reinstall / Reset

To fully reinstall from scratch:

```bash
# Uninstall all plugins
claude plugin uninstall claude-md-management code-simplifier typescript-lsp
claude plugin uninstall taches-principled tp-ddd tp-fpf tp-git tp-sadd tp-tdd

# Remove marketplaces
claude plugin marketplace remove claude-plugins-official
claude plugin marketplace remove taches-principled

# Re-add and reinstall (from Full Marketplace Setup above)
```

### Plugin Management Commands

```bash
claude plugins list                    # Show installed plugins
claude plugin details <name>           # Show plugin details and token cost
claude plugin uninstall <name>        # Remove a plugin
claude plugin marketplace list         # Show configured marketplaces
claude plugin marketplace remove <name> # Remove a marketplace
claude plugin prune                    # Clean up unused dependencies
```

### Manual (without marketplace)

```bash
cp -r plugins/taches-principled/skills/* ~/.claude/skills/
cp -r plugins/taches-principled/commands/* ~/.claude/commands/
cp -r plugins/taches-principled/agents/* ~/.claude/agents/
```

Run from repo root after clone, or from extracted release directory.

## Design Philosophy

Skills in this plugin teach through principles, not procedures. Each skill focuses on what to decide and when to decide it — the how is adapted to your context.

Key ideas:

1. **Goals over procedures** — State what to achieve, not the steps to get there
2. **Principles over steps** — A few guiding principles beats a long checklist
3. **Trust Claude** — Don't explain what Claude already knows
4. **Concise by default** — Every line competes for context; every line must earn its place
5. **Gotchas, not rules** — "Common mistake: X" teaches better than "you must always do Y"

## Origins

This plugin imports and refines from two sources:

**taches-cc-resources** — The mental models for skills, subagents, and plans in Claude Code come from here. This plugin takes that structure and streamlines it: same patterns, lighter implementation.

**[Context Engineering Kit](https://github.com/NeoLabHQ/context-engineering-kit)** — The methodology for token economy, subagent orchestration, and progressive disclosure is imported and refined here.

This plugin is an import and refinement of these two sources: the structure from taches-cc-resources, the methodology from the Context Engineering Kit.

If you're coming from `taches-cc-resources`, you'll recognize the patterns. This plugin is designed to feel familiar while reducing friction.

## Troubleshooting

- **Command not found?** Run `/skills` to see all available skills.
- **Skill not loading?** Skills route by description — make sure your request matches the skill's purpose.
- **Developer issues?** See [CLAUDE.md](./CLAUDE.md) for contribution guidelines.

## License

MIT