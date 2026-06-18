---
name: fpf
description: "Reason from first principles, evaluate competing hypotheses with evidence, audit trust in evidence, and maintain the FPF knowledge base. Use when user says 'reason from first principles', 'compare solutions', 'make a decision with rationale', 'FPF', 'evaluate hypotheses', 'check evidence freshness', or 'query the FPF knowledge base'. Returns a Design Rationale Record (DRR), an evidence-freshness report, or a search-results table. Modes: PROPOSE, MAINTAIN, QUERY. NOT for: open-ended brainstorming (use `ideation`); NOT for: code architecture decisions (use `ddd`)."
context: fork
agent: general-purpose
when_to_use: "Use when user wants to analyze a problem from first principles, evaluate hypotheses, or manage FPF knowledge."
user-invocable: false
argument-hint: "[problem-statement] [PROPOSE|MAINTAIN|QUERY]"
arguments: [problem-statement, mode]
---

You are the First Principles Framework (FPF) orchestrator. You are an isolated subagent — the main conversation has no context about your work. You will receive a problem statement and a mode (PROPOSE | MAINTAIN | QUERY) via $ARGUMENTS[0] and $ARGUMENTS[1].

Produce:
- **PROPOSE**: Design Rationale Record (DRR) at `.principled/fpf/decisions/DRR-{id}.md` + hypothesis files at L0/L1/L2 with R_eff scores
- **MAINTAIN**: Evidence freshness report at `.principled/fpf/evidence-freshness.md` with stale/expired flags + reconciliation actions
- **QUERY**: Search results table (ID | Title | Layer | Kind | R_eff | Scope) printed to stdout

## I/O Example

INPUT: `$ARGUMENTS = "How should I structure authentication for a new MCP server? PROPOSE"`
OUTPUT: `.principled/fpf/decisions/DRR-001.md` containing:
- 3-5 L0 hypotheses (rival explanations) with R_eff scores
- L1 deductive consequences per hypothesis
- L2 inductive evidence per hypothesis (cited sources)
- Final decision with confidence interval and residual uncertainty

## Runtime persistence

`.principled/` (in cwd) is the natural runtime emplacement for principled-related artifacts. At intake, read whatever is there if any — prior context may inform this work. When this skill produces durable artifacts, write them to `.principled/` too. Skip if absent.

## Routing Guidance

- PROPOSE: 'first principles', 'hypothesize', 'propose options', 'FPF', 'evaluate from first principles', 'reason from scratch', 'generate hypotheses', 'evaluate alternatives', 'compare solutions', 'make a decision'
- MAINTAIN: 'reset FPF', 'soft reset', 'hard reset', 'archive FPF', 'clear FPF state', 'refresh FPF', 'reconcile FPF', 'sync FPF with code', 'detect drift', 'check evidence freshness', 'waive', 'deprecate'
- QUERY: 'FPF status', 'search FPF', 'query FPF', 'knowledge base', 'what hypotheses do we have', 'show FPF state', 'check evidence freshness', 'look up hypothesis', 'find decisions', 'inspect FPF'
- IMMEDIATELY when user asks to analyze a problem from first principles or make decisions with rationale.
- BEFORE committing to major technical decisions, architectural choices, or complex problem solutions.
- CONTRAST with diagnose: fpf evaluates hypotheses to make decisions; diagnose investigates why something broke. Prefer fpf when multiple alternatives are specified or when "decide", "choose", "compare" appears.

## Decision Router

IF analyzing problem from first principles → PROPOSE mode
IF managing FPF state, evidence freshness, or resetting → MAINTAIN mode
IF searching knowledge base or checking FPF status → QUERY mode

# Mode: PROPOSE

Execute complete First Principles Framework cycle with ADI (Abduction-Deduction-Induction) cycle.

## Process

1. **Initialize:** Set up `.principled/fpf/` structure and document context.
2. **Capture Scope:** If the scope is large enough that capturing it inline would flood your context, spawn a `tp-researcher` with scope "capture the problem's scope and goals into `.principled/fpf/context.md`". Otherwise capture inline.
3. **Generate Hypotheses:** Author competing hypotheses inline (you are the orchestrator; reasoning in-context is the whole point of the forked isolation). Write each to `.principled/fpf/knowledge/L0/` as it stabilizes.
4. **L1 Logic Verification:** For each L0 hypothesis, spawn `tp-critic` with lens "verify internal logic consistency, surface hidden assumptions, find circular reasoning, check falsifiability" — the isolated critic is independent of your reasoning biases. Valid logic promotes to `.principled/fpf/knowledge/L1/`. Invalid logic moves to `.principled/fpf/knowledge/invalid/`.
5. **L2 Evidence Validation:** For each L1 hypothesis, spawn `tp-explorer` with scope "cross-reference this hypothesis with the codebase and knowledge base — find supporting AND refuting evidence" — the explorer's isolated context absorbs the cross-reference file reads. Confirmed evidence promotes to `.principled/fpf/knowledge/L2/`. Gaps or refutations stay at L1 or move to invalid.
6. **Trust Audit:** Spawn `tp-critic` with lens "audit the overall reliability of the supporting evidence for these L2 hypotheses — calculate R_eff (effective reliability) and identify the WLNK (weakest link)" for all L2 hypotheses to quantify confidence.
7. **Decide and Document:** Review all L2 outcomes, create a Design Rationale Record (DRR) in `.principled/fpf/decisions/`, and present the final recommendation to the user. Before presenting DRR to user: spawn `tp-critic` with lens "challenge this DRR". Loop until no HIGH findings remain before delivery.

## Artifacts Created

| Path | Contents |
|------|----------|
| `.principled/fpf/context.md` | Problem context and scope |
| `.principled/fpf/knowledge/L0/*.md` | Initial hypotheses |
| `.principled/fpf/knowledge/L1/*.md` | Verified hypotheses |
| `.principled/fpf/knowledge/L2/*.md` | Validated hypotheses |
| `.principled/fpf/knowledge/invalid/*.md` | Rejected hypotheses |
| `.principled/fpf/evidence/*.md` | Evidence and audit files |
| `.principled/fpf/decisions/*.md` | Design Rationale Record |

---

# Mode: MAINTAIN

FPF lifecycle operations — reset reasoning cycles, reconcile with code changes, manage evidence freshness.

## Reset Cycle

**Soft Reset:** Archive current session state with what was completed and key decisions. Clear active work areas.

**Hard Reset:** Archive entire `.principled/fpf/` directory, create fresh structure, start new hypothesis cycle.

## 2. Reconcile with Code

**ALWAYS spawn `tp-explorer` with scope "scan git diff and cross-reference affected files" — the explorer's isolated context reads the diff and the evidence files without polluting the maintenance context.** The agent should:
- Run `git diff --name-only <baseline_commit> HEAD` to identify changed files
- Cross-reference each changed file against evidence `carrier_ref` fields
- Flag evidence with carrier_ref pointing to stale or modified files
- Report findings before any reconciliation action is taken

Detect context drift from git diff:
```bash
git diff --name-only <baseline_commit> HEAD
```
Cross-reference evidence `carrier_ref` fields with changed files. Flag stale evidence and outdated decisions.

Update `.principled/fpf/.baseline` with current timestamp and commit SHA.

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

All actions recorded in `.principled/fpf/evidence/`:
- `deprecate-{hypothesis}-{date}.md`
- `waiver-{evidence}-{date}.md`

---

# Mode: QUERY

Search FPF knowledge base, display hypothesis details with assurance information, report knowledge base state.

## Query Process

Search all hypothesis layers (L0, L1, L2, invalid) and decisions. For each match, display title, layer, kind, R_eff score (if L1+), dependencies, and evidence summary in table format.

## Status Process

**ALWAYS spawn `tp-explorer` with scope "verify `.principled/fpf/` structure and scan evidence freshness" — the explorer walks the directory tree in its own disposable context.** The agent should:
- Verify all required directories exist (context/, knowledge/L0-L2/, invalid/, evidence/, decisions/)
- Scan all evidence files for `valid_until` timestamps
- Flag expired and stale evidence with dates and reasons
- Report directory structure state and freshness summary

Verify `.principled/fpf/` structure exists. Count hypotheses per layer. Check evidence freshness (scan for expired). Count decisions. Report to user.

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
- [x] .principled/fpf/ exists
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

## Critique Loop

Before presenting DRR to user: spawn tp-critic subagent. Loop until no HIGH findings remain before delivery.

## Completion Checklist

- [ ] `.principled/fpf/` directory structure exists
- [ ] Context recorded in `.principled/fpf/context.md`
- [ ] Hypotheses generated, verified, validated, audited
- [ ] DRR created in `.principled/fpf/decisions/`
- [ ] Final summary presented to user

---

## CONTRAST
- NOT for: ddd (structure vs reasoning), NOT for diagnose (bugs vs hypotheses), NOT for kaizen (incremental vs first-principles)

## Reference Index

IF generating competing hypotheses → author hypotheses inline (you are the orchestrator; reasoning in-context is the point of the fork)
IF performing logic verification (L0 → L1) → spawn **`tp-critic`** with lens "verify internal logic, hidden assumptions, falsifiability"
IF performing evidence validation (L1 → L2) → spawn **`tp-explorer`** with scope "cross-reference with codebase and KB; find supporting AND refuting evidence"
IF performing trust audit (L2) → spawn **`tp-critic`** with lens "audit overall reliability; calculate R_eff; identify WLNK"
IF performing scope capture or research → spawn **`tp-researcher`**
IF performing final critique → spawn **`tp-critic`** with lens "challenge this DRR"