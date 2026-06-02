# Channels — Push events into a running session

**Canonical source:** https://code.claude.com/docs/en/channels
**Status:** Research preview
**Custom-endpoint compatibility:** Channels are local MCP servers — they run on your machine and push events into your running Claude Code session. The session itself calls whatever model API you've configured, so a custom Claude-compatible endpoint works.

## What it is

A **channel is an MCP server** that pushes events into your running Claude Code session. Two-way: Claude reads the event and replies back through the same channel.

Events arrive only while the session is open — for always-on use, run Claude in a persistent background process.

## Built-in channels

- **Telegram**, **Discord**, **iMessage** — included in the research preview
- **fakechat** — officially supported demo channel that runs a chat UI on localhost, no auth, no external service. Use this to test the plugin flow before connecting a real platform.

You install a channel as a plugin and configure it with your own credentials. All channels require Bun.

## The two patterns channels enable

1. **Chat bridge** — ask Claude something from your phone via Telegram/Discord/iMessage; the answer comes back in the same chat while the work runs on your machine against your real files.
2. **Webhook receiver** — a webhook from CI, error tracker, deploy pipeline, etc. arrives where Claude already has your files open and remembers what you were debugging.

## Security model

Every approved channel plugin maintains a **sender allowlist**: only IDs you've added can push messages; everyone else is silently dropped.

- Telegram/Discord bootstrap by pairing: send a message → bot replies with a pairing code → you approve the code in your session → ID is allowlisted.
- iMessage bypasses the gate when you text yourself; add others by handle with `/imessage:access allow`.
- Per-session opt-in: `--channels <plugin>` (just being in `.mcp.json` isn't enough).

## Permission relay

Channels that declare the permission relay capability can forward in-session permission prompts to you remotely — so you can approve/deny tool use while away from the terminal. **Anyone allowlisted can approve tool use** — only allowlist senders you trust with that authority.

For unattended use, `--dangerously-skip-permissions` bypasses prompts entirely; only use in trusted environments.

## How channels compare to other "external pipe" features (local-only subset)

| Feature | What it does | Good for |
|---|---|---|
| Standard MCP server | Claude queries it; nothing is pushed | On-demand access to read/query a system |
| **Channels** | **Pushes events from non-Claude sources into the already-running local session** | Webhooks, alerts, mobile chat → Claude with your files open |

## What this enables for the orchestration story

Channels are the **reactive cousin** of scheduled-tasks. Instead of polling on an interval, the session waits idle and reacts when CI / Sentry / your phone fires an event. This makes "always-on Claude that handles whatever lands" a first-class pattern — and because it's MCP-based, it composes with any Claude-compatible endpoint.

## Building your own channel

The [channels reference](https://code.claude.com/docs/en/channels-reference) documents the contract: capability declaration, notification events, reply tools, sender gating, permission relay. If you need to wire a system that doesn't have a plugin yet (your error tracker, your deploy pipeline, a private Slack), you build it once as an MCP server and it pushes into any local Claude Code session, regardless of which model endpoint that session uses.
