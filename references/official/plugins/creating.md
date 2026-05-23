# Creating Plugins - Claude Code Official Documentation

Source: https://code.claude.com/docs/en/plugins

## When to Use Plugins vs Standalone Configuration

| Approach | Skill names | Best for |
|---|---|---|
| Standalone (`.claude/` directory) | `/hello` | Personal workflows, project-specific customizations, quick experiments |
| Plugins | `/plugin-name:hello` | Sharing with teammates, distributing to community, versioned releases, reusable across projects |

**Use standalone when:**
- Single project customization
- Personal, don't need sharing
- Experimenting before packaging
- Want short skill names

**Use plugins when:**
- Sharing with team or community
- Need same skills across multiple projects
- Version control and easy updates
- Distributing through marketplace
- Okay with namespaced skills

## Plugin Structure Overview

| Directory | Purpose |
|---|---|
| `.claude-plugin/` | Contains `plugin.json` manifest |
| `skills/` | Skills as `<name>/SKILL.md` directories |
| `commands/` | Flat markdown skill files (use `skills/` for new plugins) |
| `agents/` | Custom agent definitions |
| `hooks/` | Event handlers in `hooks.json` |
| `.mcp.json` | MCP server configurations |
| `.lsp.json` | LSP server configurations |
| `monitors/` | Background monitor configurations |
| `bin/` | Executables added to PATH |
| `settings.json` | Default settings when plugin enabled |

## Quickstart: Create Your First Plugin

1. Create plugin directory
2. Create `.claude-plugin/plugin.json` manifest
3. Create `skills/<name>/SKILL.md`
4. Test with `--plugin-dir` flag

## Plugin Manifest (plugin.json)

| Field | Purpose |
|---|---|
| `name` | Unique identifier and skill namespace |
| `description` | Shown in plugin manager |
| `version` | Optional; if set, users only receive updates when bumped |
| `author` | Optional attribution |

## Adding Components

**Skills:** Create `skills/<name>/SKILL.md` with frontmatter and instructions
**Agents:** Add `.md` files to `agents/` directory
**Hooks:** Add `hooks/hooks.json` with event handlers
**MCP Servers:** Add `.mcp.json` with server configurations
**LSP Servers:** Add `.lsp.json` for code intelligence
**Monitors:** Add `monitors/monitors.json` for background watching
**Settings:** Add `settings.json` for default configuration

## Testing Plugins

- Use `--plugin-dir` flag to test locally
- Run `/reload-plugins` to pick up changes
- Use `--plugin-url` for `.zip` archives

## Sharing Plugins

1. Add README with installation instructions
2. Choose versioning strategy
3. Create or use a marketplace
4. Test with others before distribution

## Converting Standalone to Plugin

1. Create plugin structure with `.claude-plugin/plugin.json`
2. Migrate hooks to `hooks/hooks.json`
3. Migrate skills to `skills/` directory
4. Test with `--plugin-dir`

## See Also

- [Plugin Marketplaces](https://code.claude.com/docs/en/plugin-marketplaces)
- [Plugin Submission](https://claude.com/docs/plugins/submit)
- [Discover Plugins](https://code.claude.com/docs/en/discover-plugins)