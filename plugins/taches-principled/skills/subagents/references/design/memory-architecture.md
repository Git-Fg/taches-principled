---
name: memory-architecture
description: Claude Code's four-layer memory system and effective context limits
---

# Memory Architecture

Claude Code implements a four-layer memory system:

| Layer | Mechanism | Persistence |
|-------|-----------|-------------|
| CLAUDE.md | Human-authored, loaded every session | Global/Project |
| MEMORY.md | Learned during sessions, auto-written | Project |
| Subagent Memory | `memory:` frontmatter per agent | Agent-scoped |

---

## Subagent Memory Scopes

| Scope | Location | Purpose |
|-------|----------|---------|
| user | `~/.claude/agent-memory/<name>/` | Cross-project |
| project | `.claude/agent-memory/<name>/` | Project-specific, version-controlled |
| local | `.claude/agent-memory.local/<name>/` | Project-specific, gitignored |

---

## Context Window Discipline

**Effective quality ceiling:** ~147K-152K tokens (not 200K)

| Threshold | Action |
|-----------|--------|
| Auto-compaction triggers at ~64-75% capacity | System compresses history |
| Critical information must survive compaction | CLAUDE.md or disk artifact |

**Rule:** Never put critical state only in conversation history. Persist to disk.

---

## State Persistence Rules

| State Type | Persistence Mechanism |
|------------|----------------------|
| Must survive compaction | CLAUDE.md or disk artifact |
| Must survive session end | Disk artifact (orchestrator) or agent-memory (subagent) |
| Must be shared between subagents | Orchestrator-owned disk artifact |
| Ephemeral task state | Conversation only |

---

## Anti-Patterns

- **Context stuffing** — curated high-signal context beats comprehensive dumps
- **Assuming subagent remembers** — subagents start fresh, no prior conversation
- **Putting critical state in conversation** — compact it away and you lose it