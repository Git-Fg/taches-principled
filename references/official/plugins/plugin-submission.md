# Plugin Submission - Claude Official Documentation

Source: https://claude.com/docs/plugins/submit

## Getting Your Plugin to Users

Three ways to distribute plugins:

1. **Direct install** - Install specific plugins yourself or guide users
2. **Own plugin marketplace** - Serve your own marketplace to opted-in users
3. **Submit to Claude plugin directory** - Made available to all Cowork and Claude Code users

## Plugin Directory: Community vs Anthropic Verified

> [HUMAN TRUST GUIDANCE — Not applicable to autonomous dev]

- Plugins submitted by developers and creators
- Anthropic performs basic automated review before adding
- **Anthropic Verified** badge = additional quality/safety review
- No guarantees any community plugin becomes verified
- Only install plugins from developers you trust

## What Makes a Good Plugin

Best plugins bundle related capabilities into a coherent package solving a specific job function end-to-end. A good plugin combines:

- **Skills** - Task-specific instructions Claude activates dynamically
- **MCP connectors** - Connections to external tools and data sources
- **Slash commands** - User-invoked commands for specific workflows
- **Sub-agents** - Custom agent definitions for delegating complex work

Example: A sales plugin might bundle a CRM connector, a skill teaching Claude your sales process, slash commands for prospect research and call follow-ups, and a sub-agent for competitive analysis.

## Plugin Components

### SETUP.md Skill

Plugins can include a `SETUP.md` skill to guide Claude through configuring MCP servers.

### MCP Connectors

Use connectors from the Connectors Directory or well-known developers to increase verification likelihood.

## Security Best Practices

- Review plugin source code before installing
- Check which MCP connectors are included and their permissions
- Prefer Anthropic Verified plugins for production
- Report suspicious activity to Anthropic

## Submitting Your Plugin

> [HUMAN-ONLY WORKFLOW — Manual validation + in-app form submission]

Requirements:
- Public GitHub repo (closed-source not accepted)
- Run `claude plugin validate` to check formatting
- Submit via in-app form at claude.ai/settings/plugins/submit or platform.claude.com/plugins/submit

## Directory Terms & Conditions

> [LEGAL COMPLIANCE — For human reviewers]

All plugins must comply with security and content policies.

## See Also

- [Plugin Marketplaces](https://code.claude.com/docs/en/plugin-marketplaces)
- [Discover Plugins](https://code.claude.com/docs/en/discover-plugins)