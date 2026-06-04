---
name: sadd
description: "Solve a complex problem by generating multiple candidate solutions and picking the best one with structured evaluation. Use when the user wants to compare options, pick the best approach, or do a deep dive into a hard problem where a single attempt might fail."
when_to_use: |
  - User wants to see several alternative solutions and have them evaluated against each other.
  - User needs a thorough exploration of a problem space where a single path might fail.
  - User wants to delegate a task to a background worker with automated verification.
---

## Routing Guidance

- COMPETE: 'best-of-N', 'competitive generation', 'generate multiple solutions', 'quality over speed'
- EXECUTE: 'spawn subagent', 'launch agent', 'delegate this', 'implement with verification', 'run in background'
- JUDGE: 'multi-judge debate', 'score against rubric', 'compare candidate solutions', 'judge panel evaluation', 'consensus scoring', 'meta-judge pipeline'
- EXPLORE: 'tree of thoughts', 'explore solution space', 'generate and prune', 'ideate then narrow'
- For architecture design ('supervisor pattern', 'swarm', 'coordinate agents') -> use the core `subagent-orchestration` skill.

## Decision Router

IF generating multiple competing solutions with meta-judge evaluation → COMPETE mode
IF spawning tasks via context-isolated subagents with optional verification → EXECUTE mode
IF evaluating work with meta-judge + judge pipeline or multi-judge debate → JUDGE mode
IF exploring solution space with systematic pruning (ToT) → EXPLORE mode
IF designing multi-agent architecture (supervisor/swarm/hierarchical patterns) -> use the core `subagent-orchestration` skill (DESIGN mode).

# Mode: COMPETE

Generate 3+ solutions in parallel with meta-judge evaluation and adaptive synthesis.

## Process

**Phase 1: Parallel Generation + Meta-Judge**
ALWAYS spawn sadd-meta-judge first to generate evaluation rubric before sadd-generator subagents launch.
ALWAYS spawn 3 sadd-generator subagents in parallel after meta-judge delivers rubric.
ALWAYS set maxTurns: 15 for this mode to prevent runaway generation loops.

**Phase 2: Multi-Judge Evaluation**
ALWAYS spawn 3 sadd-judge subagents in parallel for independent scoring.

**Phase 3: Adaptive Strategy**
| Condition | Strategy |
|-----------|----------|
| Unanimous vote | SELECT_AND_POLISH |
| All scores < 3.0 | REDESIGN (max 2 cycles) |
| Split decision | FULL_SYNTHESIS |

**Phase 4: Synthesis (conditional)**
One sadd-synthesizer combines best elements from solutions with documented rationale.

Output: Final solution with `.a.md`, `.b.md`, `.c.md` candidates preserved.

---

# Mode: EXECUTE

ALWAYS spawn fresh subagents with isolated context for each implementation attempt.

**SPAWN:** Simple spawn with auto model selection, CoT prefix, self-critique suffix.
ALWAYS set maxTurns: 15 for this mode to prevent runaway execution loops.

**VERIFY:** sadd-meta-judge + implementor + sadd-judge with retry loop (score >= 4.0 = pass, max 3 retries).
ALWAYS set maxTurns: 15 for this mode.

**PLAN-DRIVEN:** Execute plan tasks sequentially with code review between each, or in parallel with integration check.

## Model Selection

| Profile | Model |
|--------|-------|
| Complex reasoning (architecture, design) | Opus |
| Medium complexity | Sonnet |
| Simple transformations | Haiku |

---

# Mode: JUDGE

Evaluate work using sadd-meta-judge then sadd-judge subagents. Three modes:

**SINGLE:** sadd-meta-judge generates spec, one sadd-judge evaluates.

**DEBATE:** ALWAYS spawn 3 sadd-judge subagents in parallel, consensus check after each round, max 3 rounds.
ALWAYS set maxTurns: 15 for this mode.

**MULTI-ROUND:** Independent analysis → debate rounds → consensus or disagreement report.

## Key Principle

sadd-meta-judge runs once (shared spec grounds all evaluation). sadd-judge agents communicate via filesystem, not through orchestrator.

---

# Mode: DESIGN

DESIGN mode lives in the `subagent-orchestration` skill (core plugin). For multi-agent architecture design — supervisor/swarm/hierarchical pattern selection, context isolation, coordination protocols — use the core `subagent-orchestration` skill, which references `multi-agent-patterns` for comprehensive coverage.

`sadd` does not duplicate that content. The four remaining sadd modes (COMPETE/EXECUTE/JUDGE/EXPLORE) provide the competitive evaluation and tree-of-thoughts execution that runs on top of an architecture designed elsewhere.

---

# Mode: EXPLORE

Tree of Thoughts: explore solution space with systematic pruning and expansion.

## Process

**Phase 1: Exploration**
ALWAYS spawn 3 sadd-explorer subagents for divergent coverage.
ALWAYS set maxTurns: 15 for this mode to prevent runaway exploration loops.

**Phase 2: Pruning** — sadd-meta-judge generates spec, ALWAYS spawn 3 sadd-judge subagents to score and vote for top 3.

**Phase 3: Expansion** — ALWAYS spawn 3 sadd-expander subagents to expand selected proposals into full solutions.

**Phase 4: Evaluation** — ALWAYS spawn 2nd sadd-meta-judge + 3 sadd-judge subagents to assess solutions.

**Phase 5: Adaptive Strategy** — SELECT_AND_POLISH (unanimous), REDESIGN (all < 3.0), FULL_SYNTHESIS (split).

Max 2 redesign cycles. If exhausted without passing, escalate to human.

---

## Output Formats

COMPETE: Final solution + candidate solutions (`.a|.b|.c.md`) + judge reports (`.specs/reports/`)

EXECUTE: Task output with verification history (SPAWN/PLAN-DRIVEN) or pass/fail report (VERIFY)

JUDGE: Evaluation report with scores, evidence, and verdict (single) or consensus/disagreement summary (debate)

EXPLORE: Final solution + proposals + pruning votes + evaluation reports

DESIGN output: Produced by the core `subagent-orchestration` skill — see that skill for format.

---

## Failure Handling

| Mode | Failure Mode | Action |
|------|--------------|--------|
| COMPETE | All solutions < 3.0 after 2 redesigns | Escalate to human |
| EXECUTE | Verification failed after max retries | Escalate with failure analysis |
| JUDGE | 3 debate rounds without consensus | Report disagreements |
| EXPLORE | Max redesign cycles exhausted | Escalate to human |

All modes include structured failure signals with retry_possible flag.

## Reference Index

This hub skill ships with six specialist agents. Pick by mode:

- **sadd-expander** — `EXPLORE` mode; enumerates solution branches and
  prunes low-quality ones. Used by tree-of-thoughts runs.
- **sadd-explorer** — `COMPETE` mode; quick scan of the solution space
  before committing to a generation strategy.
- **sadd-generator** — `COMPETE`/`EXECUTE` mode; produces a single
  candidate per invocation (the worker in a competitive run).
- **sadd-judge** — `JUDGE` mode; scores a candidate against a rubric
  with structured evidence per criterion.
- **sadd-meta-judge** — meta-judge pipeline; aggregates multiple
  `sadd-judge` outputs and resolves disagreements across judges.
- **sadd-synthesizer** — final-stage; merges multiple candidates or
  judge verdicts into the user-facing output.

The agents compose: a competitive run typically spawns N
`sadd-generator` workers → fan to N `sadd-judge` reviewers → fan to
one `sadd-meta-judge` → finish with `sadd-synthesizer`. The hub
handles dispatch.

## CONTRAST
- NOT for: ddd (structure vs competitive generation), NOT for diagnose (analysis vs design), NOT for refine (polish vs compete)