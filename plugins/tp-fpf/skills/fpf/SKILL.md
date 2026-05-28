---
name: fpf
description: "Generate and evaluate competing hypotheses. Use when deciding between alternatives, auditing evidence quality, or tracking decision rationale."
when_to_use: |
  PROPOSE: 'first principles', 'hypothesize', 'propose options', 'FPF', 'evaluate from first principles', 'reason from scratch', 'generate hypotheses', 'evaluate alternatives', 'compare solutions', 'make a decision'
  MAINTAIN: 'reset FPF', 'soft reset', 'hard reset', 'archive FPF', 'clear FPF state', 'refresh FPF', 'reconcile FPF', 'sync FPF with code', 'detect drift', 'check evidence freshness', 'waive', 'deprecate'
  QUERY: 'FPF status', 'search FPF', 'query FPF', 'knowledge base', 'what hypotheses do we have', 'show FPF state', 'check evidence freshness', 'look up hypothesis', 'find decisions', 'inspect FPF'
  IMMEDIATELY when user asks to analyze a problem from first principles or make decisions with rationale.
  BEFORE committing to major technical decisions, architectural choices, or complex problem solutions.
  CONTRAST with diagnose: fpf evaluates hypotheses to make decisions; diagnose investigates why something broke. Prefer fpf when multiple alternatives are specified or when "decide", "choose", "compare" appears.
---

## Decision Router

IF analyzing problem from first principles → PROPOSE mode
IF managing FPF state, evidence freshness, or resetting → MAINTAIN mode
IF searching knowledge base or checking FPF status → QUERY mode

# Mode: PROPOSE

Execute complete First Principles Framework cycle with ADI (Abduction-Deduction-Induction) cycle.

## Process

**Initialize:** Set up `.fpf/` structure and document context. Spawn subagent to capture scope.

**Generate in parallel:** Launch 3-5 agents for competing hypotheses — obvious explanations and creative alternatives. Each hypothesis starts at L0 (unverified).

**Verify logic in layers:** Move hypotheses through L0 (raw) → L1 (internally consistent) → L2 (evidence-validated). Invalidate at any layer if checks fail.

**Audit trust:** For L2 hypotheses, calculate R_eff (evidence reliability) and identify WLNK (weakest link). Higher trust = more confident decision basis.

**Decide and document:** Review all L2 hypotheses, create Design Rationale Record (DRR) with recommendation, present to user.

## Artifacts Created

| Path | Contents |
|------|----------|
| `.fpf/context.md` | Problem context and scope |
| `.fpf/knowledge/L0/*.md` | Initial hypotheses |
| `.fpf/knowledge/L1/*.md` | Verified hypotheses |
| `.fpf/knowledge/L2/*.md` | Validated hypotheses |
| `.fpf/knowledge/invalid/*.md` | Rejected hypotheses |
| `.fpf/evidence/*.md` | Evidence and audit files |
| `.fpf/decisions/*.md` | Design Rationale Record |

---

# Mode: MAINTAIN

FPF lifecycle operations — reset reasoning cycles, reconcile with code changes, manage evidence freshness.

## Reset Cycle

**Soft Reset:** Archive current session state with what was completed and key decisions. Clear active work areas.

**Hard Reset:** Archive entire `.fpf/` directory, create fresh structure, start new hypothesis cycle.

## 2. Reconcile with Code

**ALWAYS spawn a subagent to scan git diff and cross-reference affected files.** The subagent should:
- Run `git diff --name-only <baseline_commit> HEAD` to identify changed files
- Cross-reference each changed file against evidence `carrier_ref` fields
- Flag evidence with carrier_ref pointing to stale or modified files
- Report findings before any reconciliation action is taken

Detect context drift from git diff:
```bash
git diff --name-only <baseline_commit> HEAD
```
Cross-reference evidence `carrier_ref` fields with changed files. Flag stale evidence and outdated decisions.

Update `.fpf/.baseline` with current timestamp and commit SHA.

## 3. Evidence Freshness

| Term | Meaning |
|------|---------|
| **Stale** | Evidence `valid_until` passed. Decision questionable, not wrong. |
| **Expired** | Stale and unwaived. Requires action. |
| **Waive** | "I know it's stale, I accept the risk temporarily." |
| **Refresh** | Re-run validation to create fresh evidence. |
| **Deprecate** | Decision obsolete. Downgrade hypothesis, restart evaluation. |
| **WLNK** | Weakest Link: reliability = min(all evidence). One stale piece makes decision questionable. |

## 4. Audit Trail

All actions recorded in `.fpf/evidence/`:
- `deprecate-{hypothesis}-{date}.md`
- `waiver-{evidence}-{date}.md`

---

# Mode: QUERY

Search FPF knowledge base, display hypothesis details with assurance information, report knowledge base state.

## Query Process

Search all hypothesis layers (L0, L1, L2, invalid) and decisions. For each match, display title, layer, kind, R_eff score (if L1+), dependencies, and evidence summary in table format.

## Status Process

**ALWAYS spawn a subagent to verify .fpf/ structure and scan evidence freshness.** The subagent should:
- Verify all required directories exist (context/, knowledge/L0-L2/, invalid/, evidence/, decisions/)
- Scan all evidence files for `valid_until` timestamps
- Flag expired and stale evidence with dates and reasons
- Report directory structure state and freshness summary

Verify `.fpf/` structure exists. Count hypotheses per layer. Check evidence freshness (scan for expired). Count decisions. Report to user.

## Output

### Query Results
```
## Results for: {query}
| ID | Title | Layer | Kind | R_eff | Scope |
|----|-------|-------|------|-------|-------|
```

### Status Report
```
## FPF Status

### Directory Structure
- [x] .fpf/ exists
- [x] knowledge/L0/ ({n} hypotheses)
- [x] knowledge/L1/ ({n} verified)
- [x] knowledge/L2/ ({n} validated)
- [x] knowledge/invalid/ ({n} rejected)
- [x] evidence/ ({n} evidence files)
- [x] decisions/ ({n} decision records)

### Evidence Freshness
- Fresh: {n}
- Stale: {n}
- Expired: {n}
```

---

## Completion Checklist

- [ ] `.fpf/` directory structure exists
- [ ] Context recorded in `.fpf/context.md`
- [ ] Hypotheses generated, verified, validated, audited
- [ ] DRR created in `.fpf/decisions/`
- [ ] Final summary presented to user