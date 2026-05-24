# TÂCHES Principled

**Version:** 0.4.0

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

### 18 Skills

Skills load on demand and give Claude domain expertise without bloating every conversation.

| Skill | When to Use | Enhancements |
|-------|-------------|---------------|
| **create-skills** | Building new skills or improving existing ones | Policy/Mechanism, Anti-Patterns, Thresholds |
| **create-subagents** | Creating specialized agents or configuring the Task tool | Policy/Mechanism, Anti-Patterns, Thresholds |
| **create-plans** | Planning projects, phases, or features for Claude to build | Policy/Mechanism, Anti-Patterns, Thresholds |
| **create-prompts** | Creating executable prompts for Claude Code sessions | Policy/Mechanism, Anti-Patterns, Thresholds |
| **execute-prompts** | Executing prompts via delegated sub-tasks | Policy/Mechanism, Anti-Patterns, Thresholds |
| **execute-plans** | Executing PLAN.md files via parallel subagent orchestration | Policy/Mechanism, Anti-Patterns, Thresholds |
| **subagent-orchestration** | Orchestrating parallel subagents for delegated work with self-review loops | RACE Framework, 5 Parallel Patterns, Three Automation Layers |
| **add-task** | Capturing a task idea for structured development | Standardized folder structure, type classification |
| **ideation** | Generating and refining ideas systematically | Creative sampling, collaborative brainstorming |
| **implement-task** | Implementing refined task specs with LLM-as-Judge verification | Quality-gated implementation |
| **kaizen** | Continuous improvement with multiple Kaizen methods | Gemba Walk, Value Stream, Muda |
| **plan-do-check-act** | Iterative experimentation cycles for systematic improvement | PDCA cycle |
| **refine-task** | Refining draft specs into implementation-ready tasks | Multi-phase refinement, quality gates |
| **reflexion** | Reflecting on past work to extract lasting insights | Agentic Context Engineering |
| **update-docs** | Maintaining project documentation via multi-agent workflow | Tech-writer agents, quality review |
| **write-concisely** | Clear, professional writing for human-readable docs | Writing rules and standards |
| **diagnose** | Systematic problem investigation — Five Whys, A3, Fishbone, Stack Trace | Fishbone, Five Whys, A3, backtracing |
| **refine** | Quality improvement — code review, simplification, and self-critique | Pipeline, Multi-effort review levels |

### 3 Commands

Slash commands for quick, focused workflows.

| Command | What It Does |
|---------|-------------|
| `/debug` | Apply systematic debugging methodology |
| `/whats-next` | Create a handoff for a fresh session |
| `/simplify` | Simplify and refine recently modified code |

### 7 Agents

Specialized agents for quality, review, and evaluation work.

| Agent | Purpose |
|-------|---------|
| **code-reviewer** | Reviews code for issues that matter |
| **prompt-engineer** | Reviews prompts for clarity and effectiveness |
| **skill-auditor** | Reviews skills for clarity and routing |
| **subagent-auditor** | Reviews subagents for effectiveness |
| **grader** | Evaluates skill teaching effectiveness on 4 dimensions |
| **comparator** | Compares skill versions for delta analysis |
| **analyzer** | Synthesizes evaluation results into improvement plans |

### 6 Separate Plugins

Six standalone plugins are hosted under `plugins/`, each independently installable from the marketplace:

| Plugin | Focus |
|--------|-------|
| **tp-sadd** | Subagent-driven development with parallel dispatch, competitive generation, and LLM-as-Judge verification |
| **tp-sdd** | Structured design and development workflow (deprecated, consolidated into root) |
| **tp-fpf** | Hypothesis-driven decision making with evidence lifecycle management |
| **tp-git** | Git workflow automation for commits, PRs, and issue analysis |
| **tp-tdd** | Test-driven development automation with fix workflows |
| **tp-ddd** | Domain-driven design guardrails and conventions |

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
| `create-subagents` | When to spawn vs. delegate | How to construct spawn prompts |
| `create-skills` | When to trigger | What the skill teaches |
| `create-prompts` | What a good prompt contains | How to gather requirements and generate |
| `execute-prompts` | When to use parallel vs. sequential | How to parse, resolve, and execute |
| `execute-plans` | When to use autonomous/segmented/sequential | How to orchestrate parallel workers and milestone reviews |
| `subagent-orchestration` | When to delegate vs. do inline | How to orchestrate parallel subagents and review loops |
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

## Installation

### Marketplace (recommended)

```bash
/plugin marketplace add Git-Fg/taches-principled
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