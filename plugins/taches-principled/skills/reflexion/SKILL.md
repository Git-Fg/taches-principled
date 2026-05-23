---
name: reflexion
description: "Multi-perspective judge review for high-stakes decisions, and learning capture into project memory. Use when user says 'critique this', 'what could be better', or 'capture this learning'."
when_to_use: |
  Use when the user says "critique this", "what could be better", or "capture this learning".
  IMMEDIATELY after completing significant work that needs independent quality verification (critique).
  When consolidating reflection or critique findings into durable project memory (memorize).
  Do NOT use for simple self-review (use refine in critique mode instead) or for architectural decisions (use create-plans).
argument-hint: Optional method (critique/memorize) and focus area or confidence threshold
---

## Decision Router

IF high-stakes work needing independent perspectives → use Critique with specialized judges
IF consolidating reflection or critique findings into durable project memory → use Memorize
IF user specifies a focus area or confidence threshold → Critique with that lens or only below threshold
IF combining with external decision records → Provide those records as additional evidence in verification

# Reflexion

Quality assurance and learning capture workflows. Two complementary methods form a complete improvement cycle: critique → memorize.

Both methods produce structured, evidence-backed output with severity-rated findings. The cycle ensures work is independently verified for high-stakes decisions (critique), and learnings persist across sessions (memorize).

## Critique

Multi-perspective review using independent judges with cross-examination and consensus. For high-stakes work where a single reviewer is insufficient.

### Process

1. **Context Gathering** — Identify scope, capture original requirements, modified files, decisions made, constraints. Summarize for confirmation.
2. **Independent Judge Reviews** — Spawn 2-3 judge subagents simultaneously, each with isolated context focused on their evaluation angle:

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

Critique extends self-review with multi-perspective depth. Memorize closes the loop by capturing learnings. Together they form the complete improvement cycle: critique → memorize.

For simple self-critique without independent judges, use `refine` in critique mode instead.