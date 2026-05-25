# TACHES Principled

**Version:** 0.6.0

A principle-based Claude Code plugin for building skills, subagents, and project plans.

**For when** you keep pasting the same instructions into chat, or when CLAUDE.md has grown into a procedure. Each skill teaches you to build better extensions — not by giving you templates and checklists, but by giving you the principles behind them.

## Quick Start

```bash
# Install from GitHub marketplace
/plugin marketplace add Git-Fg/taches-principled
/plugin install taches-principled

# Or manual install
cp -r skills/* commands/* agents/* ~/.claude/
```

```bash
# Create a new skill
/skill create-skills

# Plan a project phase
/skill create-plans

# Create an executable prompt
/skill create-prompts

# Run a prompt via sub-task
/skill execute-prompts

# Debug an issue
/debug <issue description>

# Create a handoff for the next session
/whats-next

# Simplify code
/simplify [file-pattern]
```

**Note:** Skills are invoked via `/skill <name>` or by description routing — they don't create individual slash commands. The command shortcuts above (`/debug`, `/simplify`, `/whats-next`) are the only flat slash commands. All other skills load on description match.

## What's Inside

### 21 Skills (20 root + 5 marketplace)

Skills load on demand and give Claude domain expertise without bloating every conversation.

| Skill | When to Use |
|-------|-------------|
| **create-skills** | Building new skills or improving existing ones |
| **create-plans** | Planning projects, phases, or features for Claude to build |
| **create-prompts** | Creating executable prompts for Claude Code sessions |
| **execute-prompts** | Executing prompts via delegated sub-tasks |
| **execute-plans** | Executing PLAN.md files via parallel subagent orchestration |
| **subagents** | Designing and orchestrating multi-agent systems (hub: design/orchestrate modes) |
| **add-task** | Capturing a task idea for structured development |
| **ideation** | Generating and refining ideas systematically |
| **implement-task** | Implementing refined task specs with LLM-as-Judge verification |
| **kaizen** | Continuous improvement with multiple Kaizen methods |
| **plan-do-check-act** | Iterative experimentation cycles for systematic improvement |
| **refine-task** | Refining draft specs into implementation-ready tasks |
| **update-docs** | Maintaining project documentation via multi-agent workflow |
| **diagnose** | Systematic problem investigation (hub: A3/Five Whys/Fishbone/Stack Trace/Auto modes) |
| **refine** | Quality improvement hub (hub: simplify/review/critique/memorize/polish modes) |
| **skill-creator** | Editing, improving, or optimizing existing skills |
| **claude-headless** | Batch and headless Claude Code workflows via `claude -p` |
| **tool-design** | Designing agent tools and MCP integrations |
| **multi-agent-patterns** | Designing multi-agent system architectures |
| **security** | Security-first code review and threat modeling |
| **test** | Test strategy, coverage analysis, and test automation patterns |

### 12 Commands

Slash commands for quick, focused workflows.

| Command | What It Does |
|---------|-------------|
| `/debug` | Apply systematic debugging methodology |
| `/whats-next` | Create a handoff for a fresh session |
| `/simplify` | Simplify and refine recently modified code |
| `/implement` | Execute task implementation with verification at each step |
| `/improve` | Improve the quality of any artifact |
| `/critique` | Get independent multi-perspective critique on high-stakes work |
| `/learn` | Capture insights and learnings into durable project memory |
| `/polish` | Improve prose clarity and conciseness |
| `/orchestrate` | Orchestrate parallel subagent execution for complex multi-file tasks |
| `/design-subagents` | Design multi-agent architectures |
| `/ideate` | Enter divergent creative thinking mode for exploration |
| `/next-tasks-orchestration` | Orchestrate subagents to implement changes with quality gates |

### 13 Agents

Specialized agents for quality, review, and evaluation work.

| Agent | Purpose |
|-------|---------|
| **analyzer** | Synthesizes evaluation results into improvement plans |
| **code-reviewer** | Reviews code for issues that matter |
| **comparator** | Compares skill versions for delta analysis |
| **critic** | Independent critique with severity scoring |
| **debug-tracer** | Systematic debugging and root cause tracing |
| **grader** | Evaluates skill teaching effectiveness on 4 dimensions |
| **implementer** | Quality-gated task implementation |
| **prompt-engineer** | Reviews prompts for clarity and effectiveness |
| **researcher** | Multi-source investigation and synthesis |
| **self-critic** | Self-review with severity scoring |
| **self-review** | Independent quality verification |
| **skill-auditor** | Reviews skills for clarity and routing |
| **subagent-auditor** | Reviews subagents for effectiveness |

### 5 Marketplace Plugins

Five standalone plugins are hosted under `plugins/`, each independently installable from the marketplace:

| Plugin | Focus |
|--------|-------|
| **tp-sadd** | Subagent-driven development with parallel dispatch, competitive generation, and LLM-as-Judge verification (hub: compete/execute/judge/design/explore modes) |
| **tp-fpf** | Hypothesis-driven decision making with evidence lifecycle management (hub: propose/maintain/query modes) |
| **tp-git** | Git workflow automation for commits, PRs, and issue analysis (hub: ship/review/issues/advanced modes) |
| **tp-tdd** | Test-driven development automation with fix workflows |
| **tp-ddd** | Domain-driven design guardrails and conventions (hub: architecture/quality/transparency/api modes) |

## Skills vs Commands

Both create `/name` shortcuts — **they're the same mechanism under the hood**. Commands are simpler flat files; skills are directories with `SKILL.md` that can add auto-invocation, frontmatter controls, and supporting files. A skill with `disable-model-invocation: true` behaves identically to a command.

## Teaching Patterns

Each skill teaches through three layers:

1. **Policy vs. Mechanism** — The organizing principle. Separates what to do (policy) from how to do it (mechanism).
2. **Anti-Patterns** — Concrete wrong/right pairs showing what not to do and why.
3. **Numeric Thresholds** — Actionable limits (not arbitrary) with rationale from cognitive science.

This replaces the old approach of step-by-step procedures and prescriptive templates.

## Developer Guide

For those contributing to this plugin, see [CLAUDE.md](./CLAUDE.md) for development practices, skill anatomy standards, and operational rules.

**Policy vs. Mechanism** is the unifying principle across all skills:

| Skill | Policy | Mechanism |
|-------|--------|-----------|
| `create-plans` | What a good plan looks like | How to decompose tasks |
| `create-skills` | When to trigger | What the skill teaches |
| `create-prompts` | What a good prompt contains | How to gather requirements and generate |
| `execute-prompts` | When to use parallel vs. sequential | How to parse, resolve, and execute |
| `execute-plans` | When to use autonomous/segmented/sequential | How to orchestrate parallel workers and milestone reviews |
| `subagents` | When to delegate vs. do inline | How to orchestrate parallel subagents and review loops |
| `diagnose` | When to use which investigation method | How to apply A3, Five Whys, Fishbone, Stack Trace |
| `refine` | When to simplify vs leave alone | The 5-stage simplification pipeline |

## The Principle-Based Approach

The old way: prescriptive XML structures and 20-step procedures.

The new way:

1. **Goals over procedures** — State what to achieve, not the steps to get there
2. **Principles over steps** — 3 principles that guide thinking beats a checklist
3. **Trust Claude** — Don't explain what Claude already knows
4. **Concise by default** — Every line competes for context; every line must earn its place
5. **Gotchas, not rules** — "Common mistake: vague descriptions won't route correctly" beats "you must include an objective tag"

This plugin practices what it preaches: skills focus on principles and anti-patterns, not procedures. Each skill teaches the concept in under 200 lines of body text.

## Hub-and-Spoke Pattern

Several skills consolidate related capabilities into single hub skills with distinct modes:

- **refine** (5 modes): simplify, review, critique, memorize, polish
- **subagents** (2 modes): design, orchestrate
- **diagnose** (5 modes): A3, five-whys, fishbone, stack-trace, auto
- **sadd** (5 modes): compete, execute, judge, design, explore
- **fpf** (3 modes): propose, maintain, query
- **git** (4 modes): ship, review, issues, advanced
- **ddd** (4 modes): architecture, quality, transparency, api

## Installation

### Marketplace (recommended)

```bash
/plugin marketplace add Git-Fg/taches-principled
/plugin install taches-principled
```

### Manual

```bash
cp -r plugins/taches-principled/skills/* ~/.claude/skills/
cp -r plugins/taches-principled/commands/* ~/.claude/commands/
cp -r plugins/taches-principled/agents/* ~/.claude/agents/

# Verify
ls ~/.claude/skills/
```

## Relationship to taches-cc-resources

This plugin is a direct descendant of [taches-cc-resources](https://github.com/glittercowboy/taches-cc-resources), which introduced valuable structure and organization to Claude Code extensions. The original `taches-cc-resources` established the mental models for skills, subagents, and plans.

**What changed here:** The prescriptive layer was stripped — the XML templates, the step-by-step procedures, and the complexity theater. What remained are the principles that actually guide good decisions.

**Key differences:**
- Skills stripped to essentials: principles and anti-patterns, not templates
- Commands simplified to single-file slash commands
- Domain expertise system excluded (brittle keyword inference)
- Focus on skills, subagents, and plans (hooks are a separate concern)

If you're migrating from `taches-cc-resources`, this plugin gives you the same mental models with less friction.

## License

MIT