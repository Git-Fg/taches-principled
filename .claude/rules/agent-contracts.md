---
name: agent-contracts
description: Agent frontmatter must match declared capabilities. Mismatches are runtime failures.
---

# Rule: MUST NOT set tools or model unless the restriction IS the point

**Why:** A `tools:` field is a HARD allowlist — anything not listed is invisible to the agent. Setting it for "least privilege" without a specific reason silently strips user MCP servers, project quirks, and settings.json custom tools. Setting `model:` locks the agent to a static tier, causing 5-10x cost waste or quality drops.

## Rule

- Never set `tools:` unless the restriction IS the point (currently only `wiki-searcher` is allowed: read-only enforcement).
- Never set `model:` — inherit from orchestrator.
- Set `background: true` when typical runtime exceeds ~30s, or the agent is parallel-by-design, or long-running.
- Never include spawn/delegation/fan-out instructions in agent bodies — the Agent tool is removed from subagents; only skills with `context: fork` can orchestrate.

## Bad / Good

**Bad:** `tools: [Read, Write]` — agent loses access to all user MCP servers and custom tools.
**Good:** No `tools:` field — inherits full tool pool including user MCP servers.

**Bad:** `model: sonnet` — locks agent, breaks when user upgrades to opus.
**Good:** No `model:` field — inherits orchestrator's model naturally.

**Bad:** Agent body: "Spawn an explorer subagent..." — runtime error, Agent tool unavailable to subagents.
**Good:** Agent body describes execution only; orchestration lives in skill bodies with `context: fork`.
