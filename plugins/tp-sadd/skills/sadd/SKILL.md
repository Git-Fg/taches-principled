---
name: sadd
description: "Solve a complex problem by generating candidates and judging them with multiple isolated-context reviewers. Use when the user says 'compare these options', 'pick the best approach', 'which solution is right', 'evaluate these alternatives', 'judge these candidates', 'is this design right', or 'rate these implementations'. Two modes: EXECUTE (run with retry) and JUDGE (multi-judge debate). NOT for: simple bug diagnosis (use `diagnose`), single-shot implementation (do it inline), competitive brainstorming (use `ideation`), fact-checking claims about the world (use `web-search`), or first-principles reasoning with evidence (use `fpf`)."
context: fork
agent: general-purpose
when_to_use: |
  - User wants structured evaluation of a solution against a rubric.
  - User needs multiple independent judges to score a candidate and reach consensus.
  - User wants to delegate a complex task to an isolated subagent context for execution with verification.
argument-hint: "[problem-statement] [EXECUTE|JUDGE]"
arguments: [problem-statement, mode]
---

You are the SADD (Structured Agent-Driven Development) orchestrator. You are an isolated subagent — the main conversation has no context about your work. You will receive a problem statement and a mode (EXECUTE | JUDGE) via $ARGUMENTS[0] and $ARGUMENTS[1].

Produce:
- **EXECUTE**: Task output at `.principled/sadd/{task-id}/output/` with verification history (pass/fail per iteration)
- **JUDGE**: Evaluation report at `.principled/sadd/{eval-id}/verdict.md` with per-criterion scores, evidence, and verdict

## I/O Example

INPUT: `$ARGUMENTS = "Design a rate-limiting strategy for our API JUDGE"`
OUTPUT: `.principled/sadd/rate-limiting/verdict.md` with per-criterion scores, evidence quotes, and verdict.

## Runtime persistence

`.principled/` (in cwd) is the natural runtime emplacement for principled-related artifacts. At intake, read whatever is there if any — prior context may inform this work. When this skill produces durable artifacts, write them to `.principled/` too. Skip if absent.

## Routing Guidance

- EXECUTE: 'isolated execution with verification', 'run with retry', 'implement with self-critique', 'isolated context'
- JUDGE: 'multi-judge debate', 'score against rubric', 'compare candidate solutions', 'judge panel evaluation', 'consensus scoring', 'meta-judge pipeline'
- For architecture design ('supervisor pattern', 'swarm', 'coordinate agents') → use the core `subagent-orchestration` skill.

## Decision Router

IF executing a task in an isolated context with verification retry loops → EXECUTE mode
IF evaluating work with multi-judge debate → JUDGE mode
IF designing multi-agent architecture (supervisor/swarm/hierarchical patterns) → use the core `subagent-orchestration` skill (DESIGN mode).

# Mode: EXECUTE

Implement the task in this isolated forked context, with self-critique and verification.

**Process:**
1. Read the task spec.
2. Implement the task inline (the files are in your isolated context; implementation stays inline).
3. Self-critique: assess the implementation against the spec; identify gaps, regressions, and improvements.
4. Run the verification command.
5. If verification fails, refine the implementation and re-verify (max 3 retries; maxTurns: 15 to prevent runaway loops).
6. Write the output + verification history to `.principled/sadd/{task-id}/output/`.

**When to spawn `sadd-judge`:** for high-stakes decisions, spawn 1-3 `sadd-judge` instances in isolated contexts to independently score your output. Use this when:
- The task is reversible only at high cost (publishing, schema migration).
- Multiple stakeholders need to agree before proceeding.
- You suspect your self-critique is biased.

For routine implementation work, your inline self-critique is sufficient.

## Model Selection

| Profile | Model |
|---------|-------|
| Complex reasoning (architecture, design) | Opus |
| Medium complexity | Sonnet |
| Simple transformations | Haiku |

---

# Mode: JUDGE

Evaluate work using a multi-judge pipeline.

**SINGLE:** spawn one `sadd-judge` with a rubric; return a single verdict.

**DEBATE:** spawn 3 `sadd-judge` subagents in parallel (each in isolated context, each with the same rubric and the candidate under review). Each returns independent scoring + evidence. Synthesize the verdicts inline:
- Unanimous high score → SELECT_AND_POLISH
- All scores < 3.0 → REVISE (re-implement inline, max 2 cycles)
- Split decision → FULL_SYNTHESIS (combine best elements from the candidate with the highest-scoring criterion-specific evidence)
ALWAYS set maxTurns: 15 to prevent runaway loops.

**MULTI-ROUND:** Independent analysis → debate rounds → consensus or disagreement report.

## Key Principle

`judges communicate via filesystem, not through orchestrator`. Write the rubric once (inline, in this context); each `sadd-judge` reads the rubric and the candidate from disk; writes its verdict to disk. You aggregate by reading the verdict files.

---

# Mode: DESIGN

DESIGN mode lives in the `subagent-orchestration` skill (core plugin). For multi-agent architecture design — supervisor/swarm/hierarchical pattern selection, context isolation, coordination protocols — use the core `subagent-orchestration` skill, which references its own references for comprehensive coverage.

`sadd` does not duplicate that content. The two remaining sadd modes (EXECUTE / JUDGE) provide the isolated-context execution and multi-judge evaluation that runs on top of an architecture designed elsewhere.

---

## Output Formats

EXECUTE: Task output with verification history.
JUDGE: Evaluation report with scores, evidence, and verdict (single) or consensus/disagreement summary (debate).
DESIGN output: Produced by the core `subagent-orchestration` skill — see that skill for format.

---

## Failure Handling

| Mode | Failure Mode | Action |
|------|--------------|--------|
| EXECUTE | Verification failed after max retries | Escalate with failure analysis |
| JUDGE | 3 debate rounds without consensus | Report disagreements |
| Any | Agent or sandbox crash mid-run | Resume from `.principled/sadd/{id}/` checkpoint if present; otherwise restart from intake |

---

## Reference Index

This hub skill ships with one specialist agent:

- **sadd-judge** — `JUDGE` mode; scores a candidate against a rubric with structured evidence per criterion. Runs in isolated context (free of the implementer's biases); returns a JSON verdict `{ score, evidence, recommendation }`.

The orchestrator implements inline (EXECUTE) and spawns `sadd-judge` instances for isolated scoring (JUDGE). Inline self-critique handles routine verification; multi-judge debate handles high-stakes decisions.

## CONTRAST
- NOT for: ddd (structure vs competitive generation), NOT for diagnose (analysis vs design), NOT for refine (polish vs multi-judge evaluation)