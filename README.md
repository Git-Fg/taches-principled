# TACHES Principled

**Version:** marketplace 0.25.1 · project 1.16.1

A Claude Code plugin marketplace for building skills, subagents, hooks, and project plans — with principle-based guidance that teaches judgment over procedure.

## Quick Start

```bash
# Add the marketplace
claude plugin marketplace add Git-Fg/taches-principled

# Install plugins (run once per plugin)
for p in core-principled tp-sadd tp-fpf tp-git tp-session-audit claude-cli-wrapper tp-mcp tp-rust tp-wiki; do
  claude plugin install "$p@taches-principled" -y
done
```

### Try These First

```bash
/debug <issue>     # Debug a problem systematically
/cc-docs <question> # Ask a Claude Code / Agent SDK / Claude API question
/refine             # Improve any artifact — simplify, review, critique, polish
```

Most skills load automatically when their description matches your task. Only `/debug` and `/cc-docs` are explicit slash commands.

## What You Get

### Marketplace Plugins

Each plugin is independently installable and extends the core with specialized capabilities.

| Plugin | Focus |
|--------|-------|
| **core-principled** | Full development lifecycle — planning, execution, review, root-cause analysis, ideation, code structure, web search |
| **tp-sadd** | Structured agent-driven development with multi-pattern evaluation and meta-judge verification |
| **tp-fpf** | First Principles Framework — hypothesis generation, evidence validation, auditable decisions |
| **tp-git** | Git workflow automation — conventional commits, PRs, issues, worktrees, inline review |
| **tp-session-audit** | Session meta-review, behavioral analysis, and sanitized GitHub issue reporting |
| **claude-cli-wrapper** | MCP wrapper for the Claude Code CLI — six focused tools for executing, reviewing, and managing sessions programmatically |
| **tp-mcp** | MCP server design and implementation — three skills covering the full server lifecycle |
| **tp-rust** | Rust project skills — single hub with SCAFFOLD / WORKSPACE / QUALITY / RELEASE modes, 5 subagents covering the full Rust lifecycle |
| **tp-wiki** | Personal wiki search, lint, and ingest — backed by wiki-searcher, wiki-linter, and wiki-ingester agents |

## Installation

### Per-plugin install

```bash
# Core plugin (required for plan-lifecycle, diagnose, refine, etc.)
claude plugin install core-principled@taches-principled -y

# Optional plugins — install only what you need
claude plugin install tp-sadd@taches-principled -y        # Structured agent-driven dev
claude plugin install tp-fpf@taches-principled -y         # First principles reasoning
claude plugin install tp-git@taches-principled -y         # Git workflow automation
claude plugin install tp-session-audit@taches-principled -y # Session meta-review
claude plugin install claude-cli-wrapper@taches-principled -y # MCP CLI wrapper
claude plugin install tp-mcp@taches-principled -y          # MCP server skills
claude plugin install tp-rust@taches-principled -y         # Rust project skills
claude plugin install tp-wiki@taches-principled -y         # Personal wiki tools
```

### Reinstall / Reset

```bash
# Uninstall all plugins
for p in core-principled tp-sadd tp-fpf tp-git tp-session-audit claude-cli-wrapper tp-mcp tp-rust tp-wiki; do
  claude plugin uninstall "$p@taches-principled" -y
done

# Remove marketplace
claude plugin marketplace remove taches-principled
```

### Plugin Management

```bash
claude plugins list                      # Show installed plugins
claude plugin details <name>            # Show plugin details and token cost
claude plugin uninstall <name>          # Remove a plugin
claude plugin marketplace list           # Show configured marketplaces
claude plugin marketplace remove <name> # Remove a marketplace
```

### Manual (without marketplace)

```bash
# Clone then copy plugin contents to your Claude skills directory
cp -r plugins/core-principled/skills/* ~/.claude/skills/
cp -r plugins/core-principled/commands/* ~/.claude/commands/
cp -r plugins/core-principled/agents/* ~/.claude/agents/
```

Run from repo root after clone, or from extracted release directory.

## Design Philosophy

Skills in this marketplace teach through principles, not procedures. Each skill focuses on what to decide and when to decide it — the how is adapted to your context.

Key ideas:

1. **Goals over procedures** — State what to achieve, not the steps to get there
2. **Principles over steps** — A few guiding principles beats a long checklist
3. **Trust Claude** — Don't explain what Claude already knows
4. **Concise by default** — Every line competes for context; every line must earn its place
5. **Gotchas, not rules** — "Common mistake: X" teaches better than "you must always do Y"

## Origins

This plugin imports and refines from two sources:

**[taches-cc-resources](https://github.com/NeoLabHQ/taches-cc-resources)** — The mental models for skills, subagents, and plans in Claude Code come from here. This plugin takes that structure and streamlines it: same patterns, lighter implementation.

**[Context Engineering Kit](https://github.com/NeoLabHQ/context-engineering-kit)** — The methodology for token economy, subagent orchestration, and progressive disclosure is imported and refined here.

## Troubleshooting

- **Command not found?** Run `/help` to see all available slash commands.
- **Skill not loading?** Skills route by description — make sure your request matches the skill's purpose.
- **Developer issues?** See [CLAUDE.md](./CLAUDE.md) for contribution guidelines.

## License

MIT