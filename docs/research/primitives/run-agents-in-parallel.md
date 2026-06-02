# Run Agents in Parallel — the canonical comparison

**Canonical source:** https://code.claude.com/docs/en/agents
**Scope:** Local surfaces only — what works against any Claude-compatible API endpoint.

This page is the single most important orientation doc — it picks the right primitive for the work.

## The local ways Claude Code parallelizes work

| Approach | What it gives you | Use when |
|---|---|---|
| **Subagents** | Delegated workers inside one session that do a side task in their own context and return a summary | A side task would flood your main conversation with search results, logs, or file contents you won't reference again |
| **Dynamic workflows** | A script that runs many subagents and cross-checks their results, for work too big to coordinate one turn at a time or that needs more than a single pass | Codebase-wide audit, 500-file migration, cross-checked research, plan drafted from several angles |

## Decision questions the doc asks

1. **Who coordinates the work?**
   - Claude delegates inside one conversation → **subagents**
   - A script holds the plan instead of Claude's turn-by-turn judgment → **dynamic workflows**

2. **Do the workers need to talk to each other?**
   - Subagents report only to the spawning conversation
   - Workflows pass results through script variables, not direct messaging

3. **Do tasks touch the same files?**
   - Isolate with **worktrees** — subagents and your own sessions can each use one
   - In a workflow, pass `isolation: 'worktree'` to `agent()` when agents will mutate files in parallel

## Supporting tools mentioned

- **Worktrees** — separate git checkout per session so parallel sessions never edit the same files. Subagents you spawn can each get a worktree.
- **`/batch` skill** — bundled skill that splits one large change into 5–30 worktree-isolated subagents that each open a pull request. It's a packaged use of subagents + worktrees, not a separate coordination style.

## "Look similar but different problem"

- **Background bash command** runs one shell command without blocking the conversation. It does NOT spawn an agent.
- **Forked subagent** is a subagent that inherits your full conversation context instead of starting fresh. Still a subagent, not a separate surface.

## How to check on running work

| Surface | Command |
|---|---|
| Subagents in the current session | `/agents` (Running tab) |
| Anything running in the background of the current session | `/tasks` |
| Dynamic workflows | `/workflows` |
