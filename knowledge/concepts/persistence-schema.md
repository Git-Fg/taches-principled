---
title: ".principled/ canonical structure"
type: schema
created: 2026-06-04
updated: 2026-06-04
plugin: core-principled
status: active
---

# `.principled/` Canonical Structure

This document is the **single source of truth** for the `.principled/` folder layout used by the `taches-principled` marketplace. The marketplace's `SessionStart` hook (`plugins/core-principled/scripts/session_start.py`) auto-generates `.principled/INDEX.md` based on this schema.

## Top-level layout

```
.principled/
├── INDEX.md            # Auto-generated master catalog. Do not hand-edit.
├── SCHEMA.md           # This file.
│
├── memory/             # Cross-plugin durable learnings (curated, not auto-generated)
│   ├── learnings.md    # Project-maintenance + refine MEMORIZE writers
│   ├── decisions/      # Architectural Decision Records (ADRs)
│   └── patterns/       # Discovered patterns and anti-patterns
│
├── plans/              # Plan-lifecycle artifacts
│   ├── BRIEF.md        # Project vision
│   ├── ROADMAP.md      # Phase structure
│   └── phases/
│       └── XX-name/
│           ├── {phase}-{plan}-PLAN.md
│           ├── {phase}-{plan}-SUMMARY.md
│           └── FINDINGS.md
│
├── specs/              # Specifications and tasks
│   ├── plans/          # Ideation outputs (`.design.md`)
│   └── tasks/          # Task-lifecycle: draft / todo / in-progress / done
│
├── pdca/               # Plan-Do-Check-Act cycles
│   └── [cycle]/
│       ├── plan.md
│       ├── do.md
│       ├── check.md
│       └── act.md
│
├── fpf/                # First Principles Framework
│   ├── context.md
│   └── knowledge/{L0,L1,L2,invalid}/
│
├── sadd/               # Structured Agent-Driven Development
│   ├── meta-judge-specs/
│   ├── candidates/
│   ├── judge-reports/
│   └── syntheses/
│
├── sessions/           # Session audit (canonical home; replaces scratch/session-*)
│   ├── inspect/{session_id}.{json,md}
│   ├── meta-reviews/{session_id}.md
│   └── issues/{session_id}-body.md
│
├── scratch/            # Ephemeral cross-plugin working state
│   └── {timestamp-or-uuid}.md
│
└── attic/              # Archived completed work
    └── {milestone}/{plan-id}/
```

## Plugins NOT in `.principled/`

The following plugins use **alternative persistence** and do NOT participate in `.principled/`:

| Plugin | Alternative storage | Rationale |
|---|---|---|
| `tp-wiki` | `~/.claude/wiki-root.md` registry | Wikis are user-managed multi-instance state; the registry pattern is load-bearing for the multi-wiki feature. **Do not migrate tp-wiki into `.principled/wiki/`.** |
| `tp-git` | git itself | Git is the persistence. No additional layer needed. |
| `tp-mcp` | (none) | Designs are documentation-only. |
| `tp-rust` | (none) | Cargo project state. |
| `claude-cli-wrapper` | (none) | Stateless CLI invocations. |

## Canonical frontmatter

Every artifact under `.principled/` (except `INDEX.md` and `SCHEMA.md` themselves) should have a YAML frontmatter block:

```yaml
---
title: <Human-readable name>
type: <plan | spec | task | hypothesis | evidence | cycle | review | issue | commit | design | synthesis | artifact>
created: YYYY-MM-DD
updated: YYYY-MM-DD
plugin: <tp-wiki | tp-sadd | tp-fpf | tp-pdca | tp-session-audit | core-principled | tp-git | tp-mcp | tp-rust | claude-cli-wrapper>
skill: <skill name, if applicable>
subagent: <subagent name, if applicable>
tags: [from common taxonomy]
sources: [<other .principled/ paths this references>]
related: [<other .principled/ paths related>]
status: <draft | active | completed | archived>
---
```

This is the same convention as `tp-wiki` already uses, extended with `plugin`, `skill`, `subagent`, `related`, and `status` for cross-plugin discovery.

## Pre-flight / post-flight contract

Each skill/subagent that produces `.principled/` artifacts should declare:

1. **Pre-flight read** — which `.principled/` files to Read before starting (typically: `INDEX.md`, then directory-specific files)
2. **Post-flight write** — which `.principled/` files to Write after completion
3. **Failure-mode handling** — what if the dir doesn't exist, what if `INDEX.md` is missing

The hook (`session_start.py`) reads `INDEX.md` to surface prior work at session start. Any new artifact should be reflected in `INDEX.md` on the next session start (the hook regenerates it if it detects drift).

## Versioning

`SCHEMA.md` is the source of truth. Changes to the canonical structure require:

1. A `principled:` commit to this file
2. A CHANGELOG entry in the marketplace
3. A note in `.principled/INDEX.md` "## Schema version" section (if added)

The schema version is implicit in the `updated:` field of this file. Future changes should also bump an explicit `version:` field when one is added.

## See also

- `knowledge/concepts/contributing.md` "Marketplace Regeneration" section
- `CLAUDE.md` "Artifact Hygiene — `.principled/` Directory" section
- `plugins/core-principled/scripts/session_start.py` (the hook that reads this file)
- `plugins/tp-session-audit/skills/session-analytics/SKILL.md` (uses `sessions/` subdir)
