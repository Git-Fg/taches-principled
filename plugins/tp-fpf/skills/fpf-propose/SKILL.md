---
name: fpf-propose
description: "Execute the complete First Principles Framework cycle — generate competing hypotheses, verify logic, validate evidence, audit trust, and produce a decision with full traceability."
when_to_use: "Use when the user says 'first principles', 'hypothesize', 'propose options', 'FPF', 'evaluate from first principles', 'reason from scratch', or 'generate hypotheses'. IMMEDIATELY when the user asks to 'analyze this problem', 'evaluate alternatives', 'compare solutions', 'make a decision with rationale', or 'think through this carefully'. BEFORE committing to a major technical decision, architectural choice, or complex problem solution."
---

## Decision Router

IF analyzing a problem from first principles -> START with context initialization, THEN generate -> verify -> validate -> audit -> decide
IF user provides problem statement -> Use it directly as the hypothesis focus
IF combining with root cause analysis findings -> Use as input evidence
IF combining with reflection output -> Use reflection findings to validate hypotheses

# Propose Hypotheses

## Core Principle

The First Principles Framework (FPF) uses the ADI cycle (Abduction-Deduction-Induction): generate competing explanations, verify logical validity, validate against empirical evidence, audit trustworthiness, then decide with full traceability.

## Process

### Step 1: Initialize Context
1. Create `.fpf/` directory structure if missing:
```bash
mkdir -p .fpf/{evidence,decisions,sessions,knowledge/{L0,L1,L2,invalid}}
```
2. Launch a sub-agent to initialize context: read the problem statement, analyze scope, write context to `.fpf/context.md`

### Step 2: Generate Hypotheses (Parallel)
Launch sub-agents to generate competing hypotheses (3-5 recommended). Each hypothesis covers a different region of the solution space:
- High-probability candidates (the obvious explanations)
- Low-probability alternatives (creative but plausible)
Each written to `.fpf/knowledge/L0/{id}.md`

### Step 3: Present Summary + User Input
Display hypothesis table, ask user if they want to add their own.

### Step 4: Verify Logic (Parallel per hypothesis)
For each L0 hypothesis, launch a sub-agent to:
1. Verify internal logical consistency
2. Check for hidden assumptions
3. Move to L1 (verified) or invalid

### Step 5: Validate Evidence (Parallel per hypothesis)
For each L1 hypothesis, launch a sub-agent to:
1. Search for supporting or refuting evidence in the codebase
2. Cross-reference with existing knowledge
3. Move to L2 (validated) or invalid

### Step 6: Audit Trust (Parallel per hypothesis)
For each L2 hypothesis, launch a sub-agent to:
1. Calculate R_eff (evidence reliability score)
2. Identify weakest link (WLNK)
3. Write audit report to `.fpf/evidence/`

### Step 7: Decide
Launch a sub-agent to:
1. Review all L2 hypotheses and audit reports
2. Create Design Rationale Record (DRR) in `.fpf/decisions/`
3. Present recommendation with rationale

### Step 8: Present Final Summary
Present results, ask user if they agree with the decision. If not, iterate from step 7.

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

## Completion Checklist

- [ ] `.fpf/` directory structure exists
- [ ] Context recorded in `.fpf/context.md`
- [ ] Hypotheses generated, verified, validated, and audited
- [ ] DRR created in `.fpf/decisions/`
- [ ] Final summary presented to user
