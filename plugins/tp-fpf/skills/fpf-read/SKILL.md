---
name: fpf-read
description: Search FPF knowledge base, display hypothesis details with assurance information, and report knowledge base state (hypothesis counts, evidence freshness, decision records).
argument-hint: Search query or "status" for KB overview
---

## Decision Router

IF searching for existing hypotheses (SAFE READ, no side effects) -> Search across all knowledge layers and display results with evidence
IF checking FPF state (SAFE READ, no side effects) -> Count hypotheses per layer, check evidence freshness, list decisions
IF no results found -> Suggest starting a fresh hypothesis cycle
IF knowledge base empty -> Show "not initialized" with option to start a fresh hypothesis cycle

# Query & Status

## Core Principle

Decisions without evidence are guesses. You can't manage what you don't measure. The FPF knowledge base is the audit trail for every significant choice -- regular inspection prevents epistemic debt.

## Query Process

1. **Search** across `.fpf/knowledge/L0/`, `.fpf/knowledge/L1/`, `.fpf/knowledge/L2/`, `.fpf/knowledge/invalid/`, and `.fpf/decisions/` for matching the query
2. **For each found hypothesis**, display:
   - Title, layer (L0/L1/L2), kind, scope
   - If layer >= L1: audit section with R_eff score
   - If dependencies exist: show dependency graph
   - Evidence summary if available
3. **Present results** in table format

## Search Locations

| Location | Contents |
|----------|----------|
| `.fpf/knowledge/L0/` | Proposed hypotheses |
| `.fpf/knowledge/L1/` | Verified hypotheses |
| `.fpf/knowledge/L2/` | Validated hypotheses |
| `.fpf/knowledge/invalid/` | Rejected hypotheses |
| `.fpf/decisions/` | Design Rationale Records |
| `.fpf/evidence/` | Evidence and audit files |

## Status Process

1. **Check directory structure**: Verify `.fpf/` exists with required subdirectories
2. **Count hypotheses**: Files in each knowledge layer
3. **Check evidence freshness**: Scan `.fpf/evidence/` for expired evidence
4. **Count decisions**: Files in `.fpf/decisions/`
5. **Report** to user

## Output

### Query Results

```
## Results for: {query}

| ID | Title | Layer | Kind | R_eff | Scope |
|----|-------|-------|------|-------|-------|
| ... | ... | L2 | functional | 0.89 | api-design |
```

### Status Report

```
## FPF Status

### Directory Structure
- [x] .fpf/ exists
- [x] knowledge/L0/ exists ({n} hypotheses)
- [x] knowledge/L1/ exists ({n} verified)
- [x] knowledge/L2/ exists ({n} validated)
- [x] knowledge/invalid/ exists ({n} rejected)
- [x] evidence/ exists ({n} evidence files)
- [x] decisions/ exists ({n} decision records)

### Evidence Freshness
- Fresh: {n}
- Stale: {n}
- Expired: {n}
- Waived: {n}
```
