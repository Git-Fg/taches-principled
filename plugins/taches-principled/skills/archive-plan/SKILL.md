---
name: archive-plan
description: "Archive completed plans and extract learnings into project memory. Use when wrapping up or shipping a plan."
when_to_use: "Use when user wants to archive a completed plan, extract learnings, or wrap up a shipped feature."
argument-hint: "[plan-path or empty for latest completed]"
---

## Routing Guidance

- AFTER execute-plans completes and SUMMARY.md is created.
- When the user wants to preserve plan artifacts before starting fresh.
- When cross-session learning accumulation is desired.
- Do NOT use for ongoing plans — only completed or abandoned plans.
- CONTRAST with refine MEMORIZE: MEMORIZE captures general insights from any session work; archive-plan bundles specific plan artifacts and extracts plan-specific learnings. Use archive-plan when the unit of work is a completed plan phase; use MEMORIZE for ad-hoc insights.
- CONTRAST with rules-orchestration SYNC: archive-plan is one of two writers to `.principled/memory/learnings.md` (the other is refine MEMORIZE). rules-orchestration SYNC reads that file to bridge durable insights into committed rules. Run archive-plan (or MEMORIZE) before SYNC.

## Decision Router

```
IF user mentions a specific plan path or phase number → archive that plan
IF user says "archive", "wrap up", "done" with no specific plan → archive latest completed plan (find most recent SUMMARY.md)
IF user says "extract learnings" or "what did we learn" → skip archival, just condense learnings
IF ambiguous → ask: "Which plan would you like to archive? I found: [list recent plans]"
```

## Core Principle

Archive is the closure step in the plan lifecycle. It preserves artifacts for future reference and distills learnings into reusable knowledge. Copy (never move) original files — plans remain accessible in their original location.

## The 4-Phase Workflow

### Phase 1: Discovery

1. Locate the target plan artifacts: PLAN.md, SUMMARY.md, related scratchpad files
2. Identify the milestone/phase from the plan's context (ROADMAP.md or directory structure)
3. **HARD PRECONDITION CHECK — ABORT if not satisfied:**
   - **A. Plan completed:** `SUMMARY.md` MUST exist at the same path as `PLAN.md`. If missing → emit `{"status": "failed", "reason": "no-summary", "retry_possible": false, "completed_portion": "discovery", "remediation": "Run execute-plans to produce SUMMARY.md, or run /archive with --abandoned flag if the plan was intentionally abandoned."}` and STOP. Do NOT proceed to Phase 2.
   - **B. Plan abandoned (explicit override):** If user passes `--abandoned` or `--force`, accept the plan as abandoned. In this case the archive bundle includes a `STATUS.md` placeholder noting the abandonment and the reason (sourced from the user); learnings extraction is limited to whatever PLAN.md captured.
4. **If both A and B fail** (no SUMMARY and no `--abandoned` flag): halt with the `no-summary` failure signal above.
5. List all artifacts to include in the archive bundle (PLAN.md, SUMMARY.md, scratchpad files, ROADMAP.md excerpt).

**Enforcement rule:** Phases 2 (Archive) and 3 (Condense) MUST NOT execute until Phase 1's precondition check passes. This is a hard gate, not a warning.

### Phase 2: Archive

1. Create archive directory at `.principled/attic/{milestone}/{plan-id}/`
2. Copy all discovered artifacts to archive directory
3. Generate metadata using the template at `templates/archive-bundle.md`
4. Verify all files copied successfully (compare file counts)

### Phase 3: Condense

1. Read all archived artifacts (PLAN.md, SUMMARY.md, scratchpad files)
2. Extract learnings per the taxonomy at `references/learning-taxonomy.md`
3. Classify each learning by type and confidence
4. Append learnings to `.principled/memory/learnings.md` with date and plan reference
5. Deduplicate against existing learnings — merge, don't append duplicates

### Phase 4: Report

Present summary:
- Archive path: `.principled/attic/{milestone}/{plan-id}/`
- Files archived: {n}
- Learnings extracted: {n} new, {n} reinforced
- Knowledge base updated: yes/no

After archival completes, consider starting a new planning cycle with `create-plans` to scope the next phase or feature. Archive preserves context; planning resumes momentum.

## File References

- Archive bundle template: `templates/archive-bundle.md`
- Learning taxonomy: `references/learning-taxonomy.md`
- Archive location: `.principled/attic/` (follows existing attic convention)
- Learnings location: `.principled/memory/learnings.md` (follows existing memory convention)

## Boundary Policy

Do NOT archive:
- Plans currently being executed (no SUMMARY.md)
- Plans from external projects
- Generated code or build artifacts — only plan documents

## Failure Signal

```json
{"status": "failed" | "success", "reason": "...", "completed_portion": "...", "retry_possible": true/false}
```

| status | reason | retry_possible |
|--------|--------|----------------|
| `failed` | `no-completed-plans` | `false` |
| `failed` | `no-summary` | `false` |
| `failed` | `archive-write-failed` | `true` |
| `failed` | `learnings-conflict` | `true` |
| `failed` | `plan-not-found` | `true` |
