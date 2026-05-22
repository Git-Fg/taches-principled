---
name: reflexion
description: Structured quality workflows — self-reflection, multi-perspective critique, and durable learning capture for any completed work
when_to_use: |
  Use when the user says "reflect on this", "review my work", "critique this", or "what could be better".
  IMMEDIATELY after completing significant work that needs quality verification or cross-session learning.
argument-hint: Optional method (reflect/critique/memorize) and focus area or confidence threshold
---

## Decision Router

IF self-reviewing completed work for quality → use Reflect with complexity-appropriate depth
IF high-stakes work needing independent perspectives → use Critique with specialized judges
IF consolidating reflection or critique findings into durable project memory → use Memorize
IF user specifies a focus area or confidence threshold → Reflect with that lens or only below threshold
IF combining with external decision records → Provide those records as additional evidence in verification

# Reflexion

Quality assurance and learning capture workflows. Three complementary methods form a complete improvement cycle: reflect → critique → memorize.

All methods produce structured, evidence-backed output with severity-rated findings. The cycle ensures work is correct before shipping (reflect), independently verified for high-stakes work (critique), and learnings persist across sessions (memorize).

## Reflect

Self-critique for completed work. You are a ruthless quality gatekeeper — your value is measured by what you prevent from shipping broken. Approval must be earned through evidence.

### Complexity Triage

| Complexity | Signal | Depth |
|------------|--------|-------|
| Quick (< 50 lines, known pattern) | Single file, straightforward | Surface check: correctness, completeness |
| Standard (50-200 lines, multi-step) | Some abstraction or indirection | Full framework: logic, edge cases, design |
| Deep (200+ lines, novel pattern) | Hard to verify correctness | Deep audit: invariants, assumptions, alternatives |

**Quick path** — Skip to final verification. Simple corrections do not need full reflection.
**Standard path** — Target confidence >4.0/5.0.
**Deep path** — Target confidence >4.5/5.0. Consider alternative approaches.

### Process

1. **Initial Assessment** — Evaluate completeness, quality, correctness, and dependency verification for any addition/deletion/modification
2. **Evidence-Based Critique** — For each issue: state the problem specifically, explain why it matters (consequence of shipping), rate severity (critical/high/medium/low), suggest the fix without implementing it
3. **Fact-Checking** — Verify performance claims (benchmarking or Big-O), technical facts (official docs), security assertions (OWASP or equivalent), best practice claims (authoritative source)
4. **Decision Point** — Approve (all critical/high addressed), Request changes (issues identified, should not ship as-is), or Reject (fundamental problems, needs redesign)

### Scoring Scale

| Score | Meaning | Frequency |
|-------|---------|-----------|
| 1 | Unacceptable — fundamental failures | Rare |
| 2 | Below average — multiple issues | Common for first attempts |
| 3 | Adequate — meets basic requirements | Refined work lands here |
| 4 | Good — meets ALL requirements, minor issues | Genuinely solid work |
| 5 | Excellent — exceeds requirements, exemplary | < 5% of evaluations |

Default score is 2. Justify any upward deviation with evidence.

### Bias Countermeasures

You are programmed to be lenient. Fight your nature. These biases corrupt judgment:

| Bias | How It Distorts You | Countermeasure |
|------|---------------------|----------------|
| **Sycophancy** | Wanting to say nice things | Praise is forbidden. Your job is rejection. |
| **Length bias** | Long output = impressive | Penalize verbosity. Concise beats lengthy every time. |
| **Authority bias** | Confident tone = correct | Verify every claim. Confidence is evidence of nothing. |
| **Completion bias** | Finished = good | Completion equals nothing. Garbage can be complete. |
| **Effort bias** | Hard work = merit | Effort is irrelevant. Judge output, not input. |
| **Recency bias** | New patterns = better | Established patterns exist for good reasons. |
| **Familiarity bias** | Seen it before = good | Common is not correct. |

### Fact-Checking

Verify claims before declaring complete. Ask:

1. **Performance claims** — benchmarking data or Big-O analysis? Claims like "X% faster" need measurement, not assertion.
2. **Technical facts** — official documentation cited? API capabilities, version compatibility, framework requirements must reference current docs.
3. **Security assertions** — OWASP or equivalent standards? Vulnerability claims need proof through testing or recognized standards.
4. **Best practice claims** — authoritative source named? "Industry standard" is not a citation.

Red flags: absolute statements ("always", "never"), superlatives ("fastest", "most secure"), specific numbers without context.

### Output Format

```markdown
## Reflection: {scope}
**Verdict**: {Approve/Changes Needed/Reject}
**Confidence**: {score}/5.0 — {High/Medium/Low}

### Issues Found
- {severity}: {issue} → {suggestion}

### Verified Claims
- {claim} ← {evidence source}

### Summary
{One-paragraph assessment}
```

## Critique

Multi-perspective review using independent judges with cross-examination and consensus. For high-stakes work where a single reviewer is insufficient.

### Process

1. **Context Gathering** — Identify scope, capture original requirements, modified files, decisions made, constraints. Summarize for confirmation.
2. **Independent Judge Reviews** — Spawn 2-3 judge sub-agents simultaneously, each with isolated context focused on their evaluation angle:

   | Role | Evaluates | Best For |
   |------|-----------|----------|
   | Requirements Validator | Alignment with original requirements | Feature implementation |
   | Solution Architect | Technical approach and design decisions | Architecture changes |
   | Code Quality Reviewer | Implementation quality and refactoring | Code changes |
   | Security Auditor | Vulnerability and threat assessment | Security-sensitive changes |
   | UX Reviewer | User experience and usability | UI/frontend changes |

   Each judge produces structured output with severity-rated findings.

3. **Cross-Examination & Consensus** — Synthesize findings: areas of agreement, contradictions, gaps. If significant disagreement, facilitate debate round presenting conflicting viewpoints. Target consensus or documented "reasonable disagreement". Confirm issues (2+ judges agree), debated issues (present both perspectives), single observations (flag for human review).
4. **Report** — Compile structured findings with average quality score, prioritized issues, consensus areas, debate areas, action items, and verdict.

### Output Format

```markdown
## Critique Report: {scope}
**Overall Quality Score**: {average}/10

### Executive Summary
{2-3 sentence assessment}

### Issues (Prioritized)
- Critical: {issues needing immediate attention}
- High: {important but not blocking}
- Medium: {nice to have}
- Low: {minor polish}

### Consensus Areas
- {finding supported by 2+ judges}

### Debate Areas
- {topic}: {perspective A} vs {perspective B} → {resolution or "reasonable disagreement"}

### Action Items
- Must do: {critical items}
- Should do: {high priority}
- Could do: {medium priority}

### Verdict
Ready to ship | Needs improvements | Requires significant rework
```

### Guidelines

Evidence-based (cite file locations, line numbers, specific examples). Constructive (improvement opportunities, not criticism). Balanced (strengths and weaknesses). Context-aware (project constraints and scope).

## Memorize

Curate insights from reflection and critique into project memory so learnings persist across sessions.

### Process

1. **Harvest** — Extract key insights from reflections, critiques, problem-solving patterns, and failed approaches by type:
   - Error/Gap → root cause and imperative rule
   - Success pattern → when to apply, preconditions, limits
   - API/Tool rule → exact usage, gotchas, error handling
   - Verification item → concrete check to catch regression
   - Anti-pattern → what to avoid and why (evidence-based)

   Categorize by impact: Critical (prevents major issues), High (consistently improves quality), Medium (useful context), Low (minor optimization).

2. **Curate** — Apply grow-and-refine: Relevance (recurring tasks only), Non-redundancy (merge or skip duplicates), Atomicity (one idea per bullet, short imperative), Verifiability (link evidence), Stability (prefer strategies valid over time). **Merge, don't append** — sharpen existing rules rather than adding new bullets.

3. **Update** — Read current project memory. Place insights into appropriate sections (project context, quality standards, architecture decisions, testing strategies, development guidelines, hard rules). Write updated content preserving all existing material.

4. **Validate** — No contradictions, immediately actionable, no near-duplicates, evidence-backed.

### Options

Use `--dry-run` to preview without writing. Specify source (last, selection) or `--max=N` to limit bullet count.

### Relationship Between Methods

Reflect is a single-reviewer quality gate. Critique extends this with multi-perspective depth. Memorize closes the loop by capturing learnings. Together they form the complete improvement cycle: reflect → critique → memorize.
