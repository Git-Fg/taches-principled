---
name: rules-orchestration
description: "Manages CLAUDE.md and .claude/rules/ lifecycle — analyzes conversations for rule-worthy insights, synthesizes proposals, integrates into rules, and maintains quality. Use when refining project conventions, updating CLAUDE.md after significant work, or codifying discovered patterns."
when_to_use: |
  Use when the user says:
  - "update my rules"
  - "refine CLAUDE.md"
  - "codify this convention"
  - "add this to my rules"
  - "rules need updating"
  - "my CLAUDE.md is bloated"
  - "extract rules from this conversation"
  - "standardize my project rules"
  - "optimize my .claude/rules/"
  IMMEDIATELY after significant skill execution (create-plans, execute-plans, refine) when conventions were established.
  FIRST when CLAUDE.md exceeds 200 lines or .claude/rules/ has more than 10 files.
  Do NOT use for one-off questions or temporary instructions.
  Do NOT modify managed/enterprise rules at system paths.
  CONTRAST with refine MEMORIZE: MEMORIZE captures to .principled/memory/learnings.md; rules-orchestration integrates into committed rules files.
argument-hint: "[ANALYZE|ADD|RESTRUCTURE|REVIEW|SYNC] [target]"
---

## Decision Router

IF user wants to extract insights from current/last conversation → **ANALYZE** mode
IF user wants to restructure or audit existing rules → **RESTRUCTURE** mode
IF user wants to add a specific convention to rules → **ADD** mode
IF user wants to review and approve pending proposals → **REVIEW** mode
IF user wants to sync with recent skill execution or learn output → **SYNC** mode
IF target is ambiguous → ask: "Analyze current conversation, restructure existing rules, add a specific convention, review pending proposals, or sync with recent work?"

---

## ANALYZE Mode

Extracts insights from conversation history or skill output and synthesizes them into structured rule proposals.

### When
After conversation or skill execution with discoverable conventions, anti-patterns, or decisions worth codifying.

### Process

1. **Capture context** — Read from `.principled/scratch/` or conversation summary
2. **Extract insights** — Spawn a rules-analyzer subagent to identify conventions, anti-patterns, tool preferences, architectural decisions, and domain knowledge
3. **Synthesize proposals** — Convert raw insights into structured proposals: category (TECHNICAL, PROCESS, PATTERN, DECISION), priority (critical, important, nice-to-have), proposed location (CLAUDE.md vs `.claude/rules/`), and rationale
4. **Present proposals** — Show user proposed changes with file targets
5. **On approval** — Integrate into target files, run git add and commit

### Output
- Proposal scratchpad: `.principled/scratch/rules-proposals-{timestamp}.md`
- Updated rules files

---

## RESTRUCTURE Mode

Audits and reorganizes existing rules to reduce bloat, eliminate duplication, and improve loading efficiency.

### When
CLAUDE.md exceeds 200 lines, `.claude/rules/` has more than 10 files, or rules feel disorganized.

### Process

1. **Audit current state** — Read all existing rules files, map structure
2. **Identify issues** — Spawn a rules-auditor subagent to find duplication, missing path scoping, oversized files, contradictions, and vagueness
3. **Design new structure** — Propose reorganization: split large files, add `paths:` frontmatter, merge duplicates, archive deprecated
4. **Present plan** — Show before/after structure
5. **On approval** — Execute restructure, verify no syntax errors, commit

---

## ADD Mode

Adds a single convention to the rules system with conflict checking and proper frontmatter.

### When
User explicitly wants to codify a specific convention.

### Process

1. **Capture intent** — Understand the convention to add
2. **Determine placement** — CLAUDE.md (global) vs `.claude/rules/` (path-scoped) vs new file
3. **Draft rule** — Follow `{baseDir}/references/rule-writing-guide.md` conventions; include Bad/Good examples
4. **Conflict check** — Grep existing rules for overlap or contradiction
5. **Integrate and commit** — Apply with Edit tool, git add, conventional commit

---

## REVIEW Mode

Multi-judge evaluation of pending rule proposals before integration.

### When
Pending proposals exist from ANALYZE or SYNC that need approval before being committed.

### Process

1. **Load proposals** — Read from `.principled/scratch/rules-proposals-*.md`
2. **Spawn review panel** — 2-3 critic subagents evaluate clarity, conflict, efficiency, and shareability
3. **Aggregate verdict** — Present consensus with approve/revise/reject per proposal
4. **Apply approved** — Integrate approved rules, archive rejected ones

---

## SYNC Mode

Bridges the gap between ephemeral memory captures and durable rules integration.

### When
After `learn` command captures insights, or after skill execution that established conventions.

### Process

1. **Read sources** — `.principled/memory/learnings.md` and recent scratchpad files
2. **Extract candidates** — Conventions, decisions, anti-patterns that warrant rules
3. **Check existing** — Avoid duplication with current rules
4. **Propose additions** — Targeted snippets with placement recommendation
5. **Auto-integrate low-risk** — Critical/correctness rules added directly
6. **Queue high-risk** — Architectural or structural rules flagged for REVIEW

---

## Design Decisions

**Files as source of truth.** Rules are files on disk, not conversation state. All coordination via filesystem, not message passing.

**Propose-then-approve.** Never auto-apply without presenting proposals. Matches the refine self-critic pattern.

**No managed rules.** Explicit check: do not modify files under `/etc/claude-code/` or other system-managed paths.

**Minimal agents.** Three agents cover the full lifecycle: analyze (extract), audit (evaluate), integrate (apply). Reuse existing plugin-level agents where possible.
