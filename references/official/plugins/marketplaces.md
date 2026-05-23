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

## Required Fields

| Field | Type | Description |
|---|---|---|
| `name` | string | Marketplace identifier (kebab-case, no spaces) |
| `owner` | object | Owner info (name required, email optional) |
| `plugins` | array | List of available plugins |

## Optional Fields

| Field | Type | Description |
|---|---|---|
| `description` | string | Brief marketplace description |
| `version` | string | Marketplace manifest version |
| `metadata.pluginRoot` | string | Base directory for relative plugin paths |
| `allowCrossMarketplaceDependenciesOn` | array | Allowed dependency marketplaces |

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

- **GitHub** (recommended): Create repo, add marketplace file, share with `/plugin marketplace add owner/repo`
- **Other git services**: Use full repository URL
- **Private repos**: Support via `gh auth login`, SSH keys, or tokens

## Version Channels

Set up two marketplaces pointing to different refs/SHAs for "stable" and "latest" channels.

## Validation

Run `claude plugin validate .` to check marketplace and plugin formatting.

## Managed Marketplace Restrictions

`strictKnownMarketplaces` in managed settings restricts which marketplaces users can add.

| Value | Behavior |
|---|---|
| Undefined | No restrictions |
| `[]` | Complete lockdown |
| List of sources | Exact match allowlist |

## Troubleshooting

- **Marketplace not loading**: Verify URL accessible, `.claude-plugin/marketplace.json` exists, JSON syntax valid
- **Plugin installation fails**: Verify source URLs accessible
- **Private repo auth fails**: Check `gh auth status`, token permissions
- **Offline environments**: Use `CLAUDE_CODE_PLUGIN_KEEP_MARKETPLACE_ON_FAILURE=1`
- **Git operations timeout**: Increase with `CLAUDE_CODE_PLUGIN_GIT_TIMEOUT_MS`

## See Also

- [Plugins Documentation](https://code.claude.com/docs/en/plugins)
- [Discover Plugins](https://code.claude.com/docs/en/discover-plugins)