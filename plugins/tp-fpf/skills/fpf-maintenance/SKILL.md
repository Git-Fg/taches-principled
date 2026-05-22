---
name: fpf-maintenance
description: Manage FPF lifecycle operations — reset reasoning cycles (soft archive or hard clear), reconcile knowledge base with code changes (detect drift, flag stale evidence), and manage evidence freshness (classify, refresh, deprecate, waive).
when_to_use: |
  Use when the user says "reset FPF", "soft reset", "hard reset", "archive FPF", "clear FPF state", "fresh start with FPF".
  IMMEDIATELY when the user asks to "actualize", "reconcile FPF", "sync FPF with code", "detect drift", or "check for stale evidence".
  BEFORE starting a new hypothesis cycle after significant codebase changes.
  BEFORE major releases to review outstanding evidence.
---

## Decision Router

IF resetting FPF state -> Offer soft reset (archive session) or hard reset (clear knowledge base)
IF reconciling project state with recent code changes -> Detect context drift from git diff, flag stale evidence, flag outdated decisions
IF checking or managing evidence freshness -> Classify evidence as fresh/stale/expired, offer refresh/deprecate/waive
IF archived session exists from prior reset -> Ask user if they want to restore it
IF combining with new investigation cycle -> Run reset before starting fresh propose flow

# Maintenance Operations

## Core Principle

Evidence is perishable and tied to code. When the codebase changes, evidence may lose validity. When time passes, evidence expires. Regular maintenance prevents decisions based on outdated information -- fresh thinking requires clean state, not old assumptions.

---

## 1. Reset Cycle

Clear the FPF state for a fresh start. Archive what you have learned -- do not carry old assumptions.

### Process

**Option 1: Soft Reset (Archive)**
1. Create session archive in `.fpf/sessions/` recording:
   - What was completed or abandoned
   - Why it was reset
   - Key decisions and evidence from the session
2. Clear active work areas

**Option 2: Hard Reset**
1. Archive the entire `.fpf/` directory to `.fpf/archive/`
2. Create fresh `.fpf/` structure
3. Start new hypothesis cycle

### Output

```
## Reset Complete
- Action: {soft/hard}
- Archived to: {path}
- Next: Start a fresh hypothesis cycle
```

---

## 2. Actualize Knowledge Base

Reconcile the project's FPF state with recent repository changes -- detect context drift, stale evidence, and outdated decisions.

### Process

**Step 1: Check Git Changes**
Run git commands to identify changes since last actualization:
```bash
git diff --name-only <baseline_commit> HEAD
git diff --stat <baseline_commit> HEAD
```

**Step 2: Check Context Drift**
If config files changed (package.json, Dockerfile, etc.), compare detected state with `.fpf/context.md`.

**Step 3: Check Evidence Staleness**
Cross-reference evidence `carrier_ref` fields with changed files from git diff. Flag affected evidence.

**Step 4: Check Decision Relevance**
Trace DRR files back to source evidence. If foundational files changed, flag as potentially outdated.

**Step 5: Update Baseline**
```yaml
# .fpf/.baseline
last_actualized: {timestamp}
commit: {current_sha}
```

**Step 6: Present Report**
```
## Actualization Report
**Files Changed**: {n}
**Context Drift**: {yes/no}
**Stale Evidence**: {n}
**Decisions to Review**: {n}
```

### Output

Structured actualization report with action items for each drift category.

---

## 3. Evidence Freshness Management

Identify stale decisions, refresh evidence, deprecate obsolete hypotheses, or waive acceptable risk.

### Quick Concepts

| Term | Meaning |
|------|---------|
| **Stale** | Evidence `valid_until` has passed. Decision is questionable, not wrong. |
| **Expired** | Stale and unwaived. Requires action. |
| **Waive** | "I know it's stale, I accept the risk temporarily." Documents explicit acceptance. |
| **Refresh** | Re-run the validation to create fresh evidence. |
| **Deprecate** | Decision is obsolete. Downgrade hypothesis, restart evaluation. |
| **WLNK** | Weakest Link principle: reliability = min(all evidence). One stale piece makes the whole decision questionable. |

### Process

**Step 1: Generate Freshness Report**
1. List all evidence files in `.fpf/evidence/`
2. Read `valid_until` from frontmatter
3. Classify as FRESH, STALE, or EXPIRED

**Step 2: Present Report**
```
### EXPIRED (Requires Action)
| Evidence | Hypothesis | Expired | Days Overdue |
|----------|------------|---------|--------------|

### STALE (Warning)
| Evidence | Hypothesis | Expires | Days Left |
|----------|------------|---------|-----------|

### FRESH
| Evidence | Hypothesis | Expires |
|----------|------------|---------|
```

**Step 3: Handle User Actions**
- **Refresh**: Re-run validation for the hypothesis
- **Deprecate**: Move hypothesis down a layer (L2 to L1 to L0), create deprecation record
- **Waive**: Create waiver record in `.fpf/evidence/` with expiration date and rationale

### Common Workflows

```
Weekly maintenance: /fpf:fpf-maintenance -> refresh, deprecate, or waive each item
Pre-release: /fpf:fpf-maintenance -> waive with documented rationale for release docs
After major change: /fpf:fpf-maintenance -> deprecate obsolete decisions, start new cycle
```

### Audit Trail

All actions recorded in `.fpf/evidence/`:
- `deprecate-{hypothesis}-{date}.md`
- `waiver-{evidence}-{date}.md`
