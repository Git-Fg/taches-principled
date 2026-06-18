---
name: agent-contracts
description: Agent frontmatter must match declared capabilities. Mismatches are runtime failures. The marketplace ships 6 named agents; specialization lives in lens prompts.
---

# Rule: MUST NOT set tools or model unless the restriction IS the point

**Why:** A `tools:` field is a HARD allowlist — anything not listed is invisible to the agent. Setting it for "least privilege" without a specific reason silently strips user MCP servers, project quirks, and settings.json custom tools. Setting `model:` locks the agent to a static tier, causing 5-10x cost waste or quality drops.

## The marketplace's 6 named subagents

The marketplace ships **6 named subagents** — all the "specialized reviewer" roles collapse into `tp-critic` parameterized by a lens prompt. Before adding a new agent definition, ask: "Could this be a one-sentence lens passed to `tp-critic` instead?" If yes, do not add an agent file.

| Agent | Role | Notes |
|---|---|---|
| `tp-critic` | Universal isolated-context reviewer. Accepts a lens prompt. | Used for ALL review/judgment/verification work. |
| `tp-explorer` | Universal isolated-context codebase mapper. Accepts a scope prompt. | Used for ALL read-only codebase exploration. |
| `tp-researcher` | Universal isolated-context external researcher. Accepts a question. | Used for ALL web/doc research. |
| `mcp-quality-judge` | Domain-specialized isolated judge for MCP servers. | Preloads `mcp-expertise`. The single domain exemplar. |
| `sadd-judge` | Candidate scoring against a rubric. | Preloads scoring discipline. |
| `wiki-searcher` | Read-only wiki query. | `tools: [Read, Glob, Grep]` — the single allowed `tools:` restriction. |

## Rule

- **Never set `tools:` unless the restriction IS the point** (currently only `wiki-searcher` is allowed: read-only enforcement).
- **Never set `model:`** — inherit from orchestrator.
- **Set `background: true`** when typical runtime exceeds ~30s, or the agent is parallel-by-design, or long-running.
- **Never include spawn/delegation/fan-out instructions** in agent bodies — the Agent tool is removed from subagents; only skills with `context: fork` can orchestrate.

## Specialized reviewers = lens prompts

When a skill needs an adversarial review through a specific angle ("find logic errors", "scan for OWASP Top 10", "audit Cargo.toml"), spawn `tp-critic` with that lens in the spawn prompt. Do NOT create a separate agent file like `tp-bug-hunter`, `security-reviewer`, or `rust-cargo-reviewer`. The lens is one sentence; the agent definition is load-bearing only when there is a NEVER policy the tool boundary must enforce.

## Bad / Good

**Bad:** `tools: [Read, Write]` — agent loses access to all user MCP servers and custom tools.
**Good:** No `tools:` field — inherits full tool pool including user MCP servers.

**Bad:** `model: sonnet` — locks agent, breaks when user upgrades to opus.
**Good:** No `model:` field — inherits orchestrator's model naturally.

**Bad:** Agent body: "Spawn an explorer subagent..." — runtime error, Agent tool unavailable to subagents.
**Good:** Agent body describes execution only; orchestration lives in skill bodies with `context: fork`.

**Bad:** Creating `tp-bug-hunter`, `tp-code-quality-reviewer`, `security-reviewer`, `rust-cargo-reviewer`, etc. as separate agent files.
**Good:** Spawn `tp-critic` with the lens in the prompt — same isolation benefit, one definition, no file proliferation.