---
name: fpf
description: "First Principles Framework — generate competing hypotheses with ADI cycle (Abduction-Deduction-Induction), audit trust with R_eff and weakest-link analysis, maintain knowledge base with evidence freshness management, and query FPF state. Modes: PROPOSE, MAINTAIN, QUERY."
when_to_use: |
  PROPOSE: 'first principles', 'hypothesize', 'propose options', 'FPF', 'evaluate from first principles', 'reason from scratch', 'generate hypotheses', 'analyze this problem', 'evaluate alternatives', 'compare solutions', 'make a decision'
  MAINTAIN: 'reset FPF', 'soft reset', 'hard reset', 'archive FPF', 'clear FPF state', 'refresh FPF', 'reconcile FPF', 'sync FPF with code', 'detect drift', 'check evidence freshness', 'waive', 'deprecate'
  QUERY: 'FPF status', 'search FPF', 'query FPF', 'knowledge base', 'what hypotheses do we have', 'show FPF state', 'check evidence freshness', 'look up hypothesis', 'find decisions', 'inspect FPF'
  IMMEDIATELY when user asks to analyze a problem from first principles or make decisions with rationale.
  BEFORE committing to major technical decisions, architectural choices, or complex problem solutions.
---

## Decision Router

IF analyzing problem from first principles → PROPOSE mode
IF managing FPF state, evidence freshness, or resetting → MAINTAIN mode
IF searching knowledge base or checking FPF status → QUERY mode

# Mode: PROPOSE

Execute complete First Principles Framework cycle with ADI (Abduction-Deduction-Induction) cycle.

## Process

**Step 1: Initialize Context**
```bash
mkdir -p .fpf/{evidence,decisions,sessions,knowledge/{L0,L1,L2,invalid}}
```
Spawn subagent to analyze scope and write context to `.fpf/context.md`.

**Step 2: Generate Hypotheses (Parallel)**
Launch 3-5 agents generating competing hypotheses:
- High-probability candidates (obvious explanations)
- Low-probability alternatives (creative but plausible)
Each written to `.fpf/knowledge/L0/{id}.md`

**Step 3: Verify Logic (Parallel per hypothesis)**
For each L0 hypothesis:
- Verify internal logical consistency
- Check for hidden assumptions
- Move to L1 (verified) or invalid

**Step 4: Validate Evidence (Parallel per hypothesis)**
For each L1 hypothesis:
- Search for supporting/refuting evidence in codebase
- Cross-reference with existing knowledge
- Move to L2 (validated) or invalid

**Step 5: Audit Trust (Parallel per hypothesis)**
For each L2 hypothesis:
- Calculate R_eff (evidence reliability score)
- Identify WLNK (weakest link)
- Write audit report to `.fpf/evidence/`

**Step 6: Decide**
Spawn subagent to:
- Review all L2 hypotheses and audit reports
- Create Design Rationale Record (DRR) in `.fpf/decisions/`
- Present recommendation with rationale

**Step 7: Present Final Summary**
Present results, ask if user agrees. If not, iterate from step 6.

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

## 1. Reset Cycle

**Soft Reset (Archive):**
1. Create session archive in `.fpf/sessions/` with what was completed, why reset, key decisions
2. Clear active work areas

**Hard Reset:**
1. Archive `.fpf/` to `.fpf/archive/`
2. Create fresh `.fpf/` structure
3. Start new hypothesis cycle

## 2. Reconcile with Code

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

1. Search `.fpf/knowledge/L0/`, `.fpf/knowledge/L1/`, `.fpf/knowledge/L2/`, `.fpf/knowledge/invalid/`, `.fpf/decisions/`
2. For each found hypothesis, display:
   - Title, layer (L0/L1/L2), kind, scope
   - If layer >= L1: audit section with R_eff score
   - Dependencies if exist
   - Evidence summary
3. Present in table format

## Status Process

1. Check `.fpf/` directory structure exists
2. Count hypotheses per layer
3. Check evidence freshness (scan `.fpf/evidence/` for expired)
4. Count decisions in `.fpf/decisions/`
5. Report to user

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