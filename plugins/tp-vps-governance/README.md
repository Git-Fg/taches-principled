# tp-vps-governance

VPS operator toolkit for Claude Code headless usage. Governs configuration, propagates rules, and manages agent memory.

## Installation

```bash
git clone https://github.com/Git-Fg/taches-principled ~/.claude/plugins/tp-vps-governance
```

Or manually copy `plugins/tp-vps-governance/` into `~/.claude/plugins/`.

## What It Does

Three governance skills for headless VPS operations:

| Skill | Trigger Phrases | Purpose |
|-------|-----------------|---------|
| **config-auditor** | "audit config", "check CLAUDE.md" | Verify project configuration consistency and CLAUDE.md structure |
| **rule-propagator** | "sync rules", "propagate rules to agents" | Distribute rule updates across agent definitions |
| **memory-curator** | "audit memory", "clean up auto-memory" | Analyze and prune agent memory files |

## Skills Overview

### config-auditor

Scans project configuration for consistency:
- CLAUDE.md structure validation
- Settings.json permission checks
- Skill listing budget analysis

Trigger: `claude -p "audit config" --project /path/to/project`

### rule-propagator

Syncs rule files across the plugin ecosystem:
- Detects stale rules in agent definitions
- Reports rules needing updates
- Validates rule consistency

Trigger: `claude -p "sync rules" --project ~/.claude`

### memory-curator

Manages agent memory lifecycle:
- Identifies stale memory files
- Prunes entries older than threshold
- Reports memory usage by agent

Trigger: `claude -p "audit memory" --project ~/.claude`

## Headless Usage

Run governance checks in CI/CD pipelines:

```bash
# Dry-run mode — report issues without changes
claude -p "audit config" --project /work --dry-run

# Auto-apply fixes (use with caution)
claude -p "sync rules" --project ~/.claude --yes

# Memory cleanup with confirmation
claude -p "clean up auto-memory" --project ~/.claude
```

### Flags

| Flag | Effect |
|------|--------|
| `--dry-run` | Preview changes without applying |
| `--yes` | Auto-confirm all prompts |
| `--output-format stream-json` | Machine-readable output for automation |

## Hooks

### SessionStart

On session begin, checks for:
- Missing CLAUDE.md → suggests init
- Outdated rules → suggests sync
- Memory bloat → suggests audit

Displays coaching message if governance gaps detected.

## Principles

- **Read-only by default**: Audit skills report only unless `--yes` specified
- **Safe execution**: No eval/exec, uses subprocess for shell commands
- **Zero blocking**: Suggestions never prevent operations

## Requirements

- Claude Code v2.1+ with headless mode support
- Python 3.8+ for hook scripts

## Customization

Edit skill files in `skills/` to adjust thresholds, message formats, and trigger phrases.