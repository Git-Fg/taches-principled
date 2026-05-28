# tp-vps-governance

VPS governance plugin for Claude Code. Two focused skills for headless VPS operations: config auditing and memory curation.

## Installation

```bash
cp -r plugins/tp-vps-governance ~/.claude/plugins/
```

Or clone the full repo and symlink.

## Skills

| Skill | Triggers | Purpose |
|-------|----------|---------|
| **config-auditor** | "audit config", "check CLAUDE.md", "optimize rules" | Audit CLAUDE.md hierarchy for conflicts, duplications, and optimization opportunities |
| **memory-curator** | "audit memory", "clean up memory", "memory hygiene" | Discover, deduplicate, and archive stale memory files on long-running VPS instances |

## config-auditor

Scans your CLAUDE.md hierarchy from project root to global, detecting:

- **Conflicts**: contradictory rules at different levels (tabs vs spaces)
- **Duplications**: same rule in multiple files wasting tokens
- **Optimization opportunities**: rules that could be path-scoped, files that could be split

```bash
# Audit current project
/config-auditor audit --dry-run

# Find only conflicts
/config-auditor conflicts

# Get optimization recommendations
/config-auditor optimize
```

## memory-curator

Manages Claude Code memory on long-running VPS instances:

- **Audit**: discover all memory locations, score health (green/yellow/red)
- **Dedup**: find and merge duplicate entries across projects
- **Archive**: move stale entries (>30 days) to archive with recovery manifest
- **Clean**: full maintenance pass (dedup + archive)

```bash
# Audit memory usage
/memory-curator audit --dry-run

# Full cleanup with auto-confirm
/memory-curator clean --yes --days 30
```

## Headless Usage

All skills default to `--dry-run` (read-only). Use `--yes` to apply changes.

```bash
# CI/CD pipeline example
claude -p "/config-auditor audit" --project /work --dry-run
claude -p "/memory-curator audit" --project ~/.claude --dry-run
```

## Requirements

- Claude Code v2.1+
- Python 3.8+ (for memory-curator dedup script)