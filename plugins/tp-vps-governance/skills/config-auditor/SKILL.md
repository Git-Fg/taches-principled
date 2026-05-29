---
name: config-auditor
description: "Audit CLAUDE.md hierarchy for conflicts, duplications, and optimization opportunities on VPS instances."
allowed-tools: Read, Glob, Grep, Edit
when_to_use: |
  Use when the user says:
  - "audit config"
  - "check CLAUDE.md"
  - "review rules for conflicts"
  - "configuration audit"
  - "optimize rules"
  - "my CLAUDE.md is bloated"
  FIRST when preparing for VPS deployments or after major rule changes.
  Do NOT use for syncing rules to agents (use rule-propagator) or memory cleanup (use memory-curator).
argument-hint: "[audit|conflicts|optimize] [--dry-run] [--yes]"
---

## CONTRAST with Other Skills

- **rule-propagator**: syncs shared rules to subagent fleet
- **memory-curator**: audits and deduplicates memory files
- **THIS**: audits config hierarchy for conflicts and optimization

---

## Decision Router

IF user wants comprehensive config analysis → **AUDIT** mode (default)
IF user wants to find rule conflicts only → **CONFLICTS** mode
IF user wants optimization recommendations → **OPTIMIZE** mode

All modes default to `--dry-run` (read-only analysis).

---

## AUDIT Mode

Comprehensive analysis of CLAUDE.md hierarchy and .claude/rules/ structure.

### Process

1. **Discover configs** — Recursive glob from CWD upward:
   - `CLAUDE.md` at each directory level
   - `.claude/rules/**/*.md` at each project level
   - `~/.claude/CLAUDE.md` (global)
   - `~/.claude/rules/**/*.md` (global rules)

2. **Map hierarchy** — Build tree showing:
   ```
   ~/CLAUDE.md (global) — 120 lines, ~300 tokens
   ~/projects/foo/CLAUDE.md — 85 lines, ~200 tokens
   ~/projects/foo/.claude/rules/code-style.md — 45 lines, ~110 tokens
   ```

3. **Analyze issues** — Detect:
   - **Duplications**: same rule text in multiple files (hash comparison)
   - **Conflicts**: contradictory rules (e.g., "use tabs" vs "use spaces")
   - **Path-scope misplacements**: global rules that should be path-scoped
   - **Orphans**: rules referencing deleted files/projects

4. **Score** — Calculate:
   - Overlap percentage between levels
   - Token waste from duplication
   - Health score: green / yellow / red

5. **Output** — Present structured report:
   ```
   ## Config Audit Report

   Files scanned: 7
   Total lines: 340
   Total tokens: ~850

   ### Critical (2)
   - [CONFLICT] Indentation: tabs (global) vs spaces (project)

   ### Warnings (3)
   - [DUPLICATE] "Use TypeScript strict mode" in 2 files

   ### Info (1)
   - [OPTIMIZE] 3 rules could be path-scoped, saving ~120 tokens
   ```

6. **Save** — Write report to `.principled/scratch/config-audit-{timestamp}.md`

---

## CONFLICTS Mode

Focuses exclusively on contradictory rules.

### Process

1. Run full discovery (same as AUDIT)
2. Compare all rules pairwise across hierarchy levels
3. Flag contradictions with severity:
   - **Critical**: opposite directives (tabs vs spaces, required vs forbidden)
   - **Warning**: inconsistent preferences (different naming conventions)
4. Output: conflict pairs with file paths and suggested resolution

### Output Format
```
### Conflict: Indentation Style
- Global (line 12): "Use tabs for indentation"
- Project (line 8): "Use 2 spaces for indentation"
- Resolution: Project-level wins (more specific scope)
- Action: Remove global rule or add project override
```

---

## OPTIMIZE Mode

Identifies consolidation opportunities.

### Process

1. Run full discovery (same as AUDIT)
2. Identify:
   - Rules duplicated across multiple files (consolidate to one)
   - Global rules that should be path-scoped (add frontmatter)
   - Unused rules (no matching file patterns in project)
   - Large files that should be split (frontmatter + multiple path-scopes)
3. Calculate potential token savings per action
4. Present prioritized recommendations

### Output Format
```
### Optimization Opportunities

1. [HIGH] Consolidate "TypeScript strict" rule
   Found in: 3 files → Move to .claude/rules/typescript.md
   Token savings: ~80 tokens

2. [MEDIUM] Add path: frontmatter to rules/code-style.md
   Current: loads everywhere → Target: only src/
   Token savings: ~40 tokens

Total potential savings: ~120 tokens (14% reduction)
```

---

## Safety

- Default: `--dry-run` (read-only, no writes)
- With `--yes`: can generate optimized file structures
- Never modifies files without explicit confirmation