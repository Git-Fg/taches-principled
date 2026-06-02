# Source: Claude Code Docs Index (llms.txt)

**URL:** https://code.claude.com/docs/llms.txt

This file is Anthropic's curated, agent-readable index of every Claude Code doc page. The full set is too long to mirror here — what follows is the orchestration-relevant subset filtered for **custom-endpoint compatibility**.

## Local execution surface (works against any Claude-compatible endpoint)

| Page | URL slug |
|---|---|
| Orchestrate subagents at scale with dynamic workflows | `/workflows` |
| Run agents in parallel | `/agents` |
| Create custom subagents | `/sub-agents` |
| Run parallel sessions with worktrees | `/worktrees` |
| Run prompts on a schedule | `/scheduled-tasks` |
| Push events into a running session with channels | `/channels` |
| Channels reference | `/channels-reference` |
| Keep Claude working toward a goal | `/goal` |
| Speed up responses with fast mode | `/fast-mode` |

## Adjacent local infrastructure

| Page | URL slug |
|---|---|
| Hooks reference | `/hooks` |
| Automate actions with hooks | `/hooks-guide` |
| Checkpointing | `/checkpointing` |
| Manage sessions | `/sessions` |
| Connect Claude Code to tools via MCP | `/mcp` |
| Run Claude Code programmatically | `/headless` |
| Plugins | `/plugins`, `/plugins-reference`, `/plugin-marketplaces`, `/plugin-hints`, `/plugin-dependencies` |

## Weekly release notes — orchestration milestones (local-relevant only)

| Week | What landed |
|---|---|
| 2026-w13 | Auto mode, computer use, transcript search |
| 2026-w14 | Computer use in CLI, flicker-free rendering, per-tool MCP result-size overrides |
| 2026-w15 | **Monitor tool with self-pacing `/loop`**, /team-onboarding |
| 2026-w16 | Opus 4.7 with **xhigh effort level**, /usage breakdown, native binaries |
| 2026-w17 | Session recaps, custom color themes |
| 2026-w18 | Windows without Git Bash, /resume from PR URL, claude project purge |
| 2026-w19 | Plugins from .zip/URLs, Ctrl+R command history, worktrees from local HEAD, auto mode hard deny |
| 2026-w20 | **`/goal`**, fast mode on Opus 4.7 by default |
| 2026-w21 | Auto mode on Pro plan, /usage breakdown of skills/agents/MCP cost, /code-review command |
| 2026-w22 | **Opus 4.8**, **Dynamic Workflows**, fast mode on 4.8 |

## What this index reveals

The local orchestration surface didn't ship as one big announcement — it accumulated **week by week** across Q2 2026. The dynamic-workflow tool that lands in W22 is the culmination of:

1. **Auto mode** (W13) — removed per-tool permission prompts → enables unattended runs
2. **Monitor tool + self-pacing `/loop`** (W15) — proved background-script-with-streamed-output
3. **xhigh effort level** (W16) — the model capability that makes meta-orchestration practical
4. **`/goal`** (W20) — proved condition-driven turn looping
5. **Opus 4.8 + Dynamic Workflows** (W22) — culmination: model strong enough for xhigh-driven orchestration, runtime that materializes the orchestration as a script.

Each prior week's release built primitives the workflow runtime now composes. taches-principled's architecture has to be read against this stack now.
