# Source: Week 22 Release Notes (May 25–29, 2026)

**URL:** https://code.claude.com/docs/en/whats-new/2026-w22
**Why this matters:** Dynamic Workflows shipped this week. The release notes give us the launch context.

## Major items shipped in Week 22

### 1. Opus 4.8 as the new default
Opus 4.8 is now the default on Max, Team Premium, Enterprise pay-as-you-go, and the Anthropic API. Defaults to high effort; use `/effort xhigh` for harder tasks. Requires v2.1.154+.

```
> /model claude-opus-4-8
```

### 2. Dynamic Workflows

> "A workflow is an orchestration script Claude writes for your task and runs across many subagents in the background. Use one when a task is too large for one conversation to coordinate: a codebase-wide audit, a large migration, a research question that needs cross-checking. Manage runs with `/workflows`."

Trigger with the keyword:
```
> create a workflow that migrates every internal fetch() call to the new HttpClient wrapper
```

### 3. Security-guidance plugin

> "The security-guidance plugin reviews Claude's code changes for vulnerabilities and fixes them in the same session. It runs a fast pattern check on each edit, a model review at the end of each turn, and a deeper agentic review on commit or push."

Install: `/plugin install security-guidance@claude-plugins-official` then `/reload-plugins`.

### 4. Fast mode on Opus 4.8
$10/$50 per MTok (2× standard rate for ~2.5× speed). Opus 4.7 / 4.6 stay at $30/$150. Opus 4.6 fast mode deprecated.

## Other "small wins" worth knowing for the orchestration story

- **`!` prefix in `claude agents`** — prefix a shell command to run as a background job you can attach to and detach from. Also as `claude --bg --exec 'pytest -x'`.
- **`.claude/skills` plugins auto-load** — no marketplace required. `claude plugin init <name>` scaffolds a new plugin.
- **`/reload-skills`** — re-scan skill directories without restarting. `SessionStart` hooks can return `reloadSkills: true` to make skills they install available in the same session.
- **`disallowed-tools` in skill/command frontmatter** — remove tools from the model while a skill is active.
- **`MessageDisplay` hook event** — lets hooks transform or hide assistant message text as displayed.
- **`--fallback-model` switching** — when the primary isn't found, the session switches for the rest of the session instead of failing every request.
- **`defaultEnabled: false` in plugin.json** — plugins install without turning on until enabled.
- **Streaming tool execution always on** — including with telemetry disabled and on Bedrock/Vertex/Foundry.
- **`←←` opens agents view** — now works on Bedrock/Vertex/Foundry and with telemetry disabled.
- **`claude mcp list` / `get` show pending approval** — instead of auto-approving and connecting unapproved `.mcp.json` servers when output is piped.

## What this teaches

Workflows shipped **alongside** Opus 4.8 (the model upgrade that makes xhigh meaningfully better) and **alongside** plugin-and-hook ergonomics improvements. The bundle is intentional: a more capable model, a richer orchestration primitive, and tighter plugin integration arriving together.
