---
description: Plugin marketplace configuration, plugin sources, and distribution
when_to_read: When creating marketplaces, adding plugins, or managing version channels
path: ./official/plugins/marketplaces.md
---

# Plugin Marketplaces - Claude Code Official Documentation

Source: https://code.claude.com/docs/en/plugin-marketplaces

## Overview

A plugin marketplace is a catalog that distributes plugins to others. Marketplaces provide centralized discovery, version tracking, automatic updates, and support for multiple source types.

## Creating a Marketplace

1. **Create plugins** with skills, agents, hooks, MCP servers, or LSP servers
2. **Create marketplace file** defining `marketplace.json`
3. **Host the marketplace** on GitHub/GitLab
4. **Share** with users via `/plugin marketplace add`

## Marketplace File Location

`.claude-plugin/marketplace.json` in repository root

## Plugin Sources

| Source | Fields | Notes |
|---|---|---|
| Relative path | string | Must start with `./` |
| GitHub | `repo`, `ref?`, `sha?` | |
| URL | `url`, `ref?`, `sha?` | Git URL |
| git-subdir | `url`, `path`, `ref?`, `sha?` | Subdirectory in git repo |
| npm | `package`, `version?`, `registry?` | Via npm install |

## Relative Paths

`./plugins/my-plugin` resolves relative to marketplace root. Do NOT use `../` to reference paths outside marketplace root.

## Strict Mode

| Value | Behavior |
|---|---|
| `true` (default) | `plugin.json` is authority; marketplace entry can supplement |
| `false` | Marketplace entry is entire definition |

## Plugin Version Resolution

1. `version` in plugin's `plugin.json`
2. `version` in marketplace entry
3. Git commit SHA

## Host & Distribution

> [INTERACTIVE CLI — Human invokes /plugin marketplace add]

- **GitHub** (recommended): Create repo, add marketplace file, share with `/plugin marketplace add owner/repo`
- **Other git services**: Use full repository URL
- **Private repos**: Support via `gh auth login`, SSH keys, or tokens

## Version Channels

> [HUMAN DECISION — Channel selection]

Set up two marketplaces pointing to different refs/SHAs for "stable" and "latest" channels.

## Validation

Run `claude plugin validate .` to check marketplace and plugin formatting.

## Managed Marketplace Restrictions

> [PLATFORM ADMIN — Not relevant for plugin developers]

`strictKnownMarketplaces` in managed settings restricts which marketplaces users can add.

| Value | Behavior |
|---|---|
| Undefined | No restrictions |
| `[]` | Complete lockdown |
| List of sources | Exact match allowlist |

## Troubleshooting

> [INTERACTIVE SESSION — User-interactive auth commands]

- **Marketplace not loading**: Verify URL accessible, `.claude-plugin/marketplace.json` exists, JSON syntax valid
- **Plugin installation fails**: Verify source URLs accessible
- **Private repo auth fails**: Check `gh auth status`, token permissions
- **Offline environments**: Use `CLAUDE_CODE_PLUGIN_KEEP_MARKETPLACE_ON_FAILURE=1`
- **Git operations timeout**: Increase with `CLAUDE_CODE_PLUGIN_GIT_TIMEOUT_MS`

## See Also

- [Plugins Documentation](https://code.claude.com/docs/en/plugins)
- [Discover Plugins](https://code.claude.com/docs/en/discover-plugins)

---

## Taches Principled Marketplace Architecture

The taches-principled repository uses a **monolithic marketplace-centric model** — all plugins share a single `marketplace.json` for distribution, but remain architecturally independent at runtime.

### Monolithic Marketplace Model

### Plugin Structure

This marketplace uses a **monolithic model with `strict: false`** — all plugin metadata is in `marketplace.json`, no per-plugin `plugin.json` is needed.

| Aspect | Behavior |
|--------|----------|
| **Catalog** | Single `marketplace.json` contains all plugin metadata |
| **Distribution** | Users install one marketplace, receive all plugins |
| **Version management** | One place to bump, one push, all plugins updated |

The key insight: **bundling is a distribution convenience, not a runtime coupling**. Users get everything with one install, but each plugin functions as if installed standalone.

### Plugin Independence (Runtime)

Each plugin in this marketplace is **fully independent**:

```
plugins/
├── tp-git/          # Git workflow automation — zero dependencies on other plugins
├── tp-sadd/         # Structured agent-driven dev — zero dependencies
├── tp-fpf/          # First-principles reasoning — zero dependencies
└── tp-vps-governance/  # Memory management — zero dependencies
```

**What this means:**
- Each plugin's skills, agents, and commands work standalone
- No plugin imports or references another plugin's files
- Users can enable/disable individual plugins via `/plugin enable/disable`
- If one plugin breaks, others continue working
- Cross-plugin features use capability-based routing, not file imports

**The rule:** Plugins share only the marketplace catalog. They share no code, no imports, no file paths. Coexistence in the same repository is purely for distribution efficiency.

### Synergy Without Coupling

Cross-plugin collaboration uses **semantic routing**, not direct imports:

| Instead of | Use |
|------------|-----|
| `import { diagnose } from 'tp-diagnose'` | "use diagnose instead" in skill routing |
| `read ../../tp-diagnose/skills/diagnose/SKILL.md` | Natural language: "the diagnose skill handles this" |
| File path references to other plugins | Capability names and role descriptions |

This allows plugins to suggest collaboration without creating dependencies. If the target plugin exists, routing finds it. If not, the skill degrades gracefully.

### Version Alignment

| Version | Source | Purpose |
|---------|--------|---------|
| **Plugin version** | `marketplace.json` | Per-plugin release tracking |
| **Marketplace version** | `marketplace.json` | Collective release tracking |

**Schema:** The marketplace uses a flat schema optimized for catalog display:
- `description` at root: marketplace-level summary (max 200 chars)
- `description` per plugin: one-line catalog entry (max 150 chars)
- This marketplace uses `strict: false` — marketplace.json is the sole source of truth

### Rationale

**Why monolithic distribution:**
1. **Simplified version management** — one push updates all plugins
2. **No sync drift** — single source of truth, no plugin.json/marketplace.json mismatches
3. **User convenience** — one install command gets everything
4. **Consistent updates** — plugins evolve together, reducing compatibility issues

**Why plugin independence:**
1. **Fault isolation** — one broken plugin doesn't cascade
2. **Selective enablement** — users pick what they need
3. **No lock-in** — any plugin could theoretically be extracted to standalone
4. **Clean architecture** — forces good separation from the start

The monolithic model gives you distribution simplicity without runtime complexity.

