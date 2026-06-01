---
name: sadd
description: "Multi-agent development: generate alternatives, verify quality, coordinate workers."
when_to_use: "Use when user wants competitive generation, multi-judge evaluation, or tree-of-thoughts solution exploration."
---

## Routing Guidance

- COMPETE: 'best-of-N', 'competitive generation', 'generate multiple solutions', 'quality over speed'
- EXECUTE: 'spawn subagent', 'launch agent', 'delegate this', 'implement with verification', 'run in background'
- JUDGE: 'evaluate', 'judge this', 'assess quality', 'verify', 'check my work', 'multi-judge debate'
- DESIGN: 'design architecture', 'multi-agent', 'supervisor pattern', 'swarm', 'coordinate agents'
- EXPLORE: 'tree of thoughts', 'explore solution space', 'generate and prune', 'ideate then narrow'

## Decision Router

IF generating multiple competing solutions with meta-judge evaluation → COMPETE mode
IF spawning tasks via context-isolated subagents with optional verification → EXECUTE mode
IF evaluating work with meta-judge + judge pipeline or multi-judge debate → JUDGE mode
IF designing multi-agent architecture (supervisor/swarm/hierarchical patterns) → DESIGN mode
IF exploring solution space with systematic pruning (ToT) → EXPLORE mode

# Mode: COMPETE

Generate 3+ solutions in parallel with meta-judge evaluation and adaptive synthesis.

## Process

**Phase 1: Parallel Generation + Meta-Judge**
ALWAYS spawn meta-judge first to generate evaluation rubric before generator subagents launch.
ALWAYS spawn 3 generator subagents in parallel after meta-judge delivers rubric.
ALWAYS set maxTurns: 15 for this mode to prevent runaway generation loops.

**Phase 2: Multi-Judge Evaluation**
ALWAYS spawn 3 judge subagents in parallel for independent scoring.

**Phase 3: Adaptive Strategy**
| Condition | Strategy |
|-----------|----------|
| Unanimous vote | SELECT_AND_POLISH |
| All scores < 3.0 | REDESIGN (max 2 cycles) |
| Split decision | FULL_SYNTHESIS |

**Phase 4: Synthesis (conditional)**
One synthesizer combines best elements from solutions with documented rationale.

Output: Final solution with `.a.md`, `.b.md`, `.c.md` candidates preserved.

---

# Mode: EXECUTE

ALWAYS spawn fresh subagents with isolated context for each implementation attempt.

**SPAWN:** Simple spawn with auto model selection, CoT prefix, self-critique suffix.
ALWAYS set maxTurns: 15 for this mode to prevent runaway execution loops.

**VERIFY:** Meta-judge + implementor + judge with retry loop (score >= 4.0 = pass, max 3 retries).
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

Evaluate work using meta-judge then judge subagents. Three modes:

**SINGLE:** Meta-judge generates spec, one judge evaluates.

**DEBATE:** ALWAYS spawn 3 judge subagents in parallel, consensus check after each round, max 3 rounds.
ALWAYS set maxTurns: 15 for this mode.

**MULTI-ROUND:** Independent analysis → debate rounds → consensus or disagreement report.

## Key Principle

Meta-judge runs once (shared spec grounds all evaluation). Judges communicate via filesystem, not through orchestrator.

---

# Mode: DESIGN

Design multi-agent architectures for context isolation and coordination.

**Supervisor/Orchestrator:** Central agent decomposes, spawns, synthesizes. Use for clear decomposition with human oversight.

**Peer-to-Peer/Swarm:** No central control, agents communicate via filesystem. Use for flexible exploration.

**Hierarchical:** Strategic → Planning → Execution layers. Use for large-scale projects.

## Core Principle

Context isolation is the primary benefit — subagents exist to give each execution a clean context window, not to anthropomorphize role division.

## Execution

**Default: subagent delegation.** For DESIGN mode, spawn a sadd-architect subagent to recommend pattern based on complexity analysis. The main agent synthesizes findings; it never designs inline.

**Spawn pattern:**
- Scope: Analyze task complexity (scope, dependencies, coordination needs)
- Role: sadd-architect subagent
- Output: Pattern recommendation (supervisor/swarm/hierarchical) with rationale

## Design Guidelines

- Default to filesystem-based inter-agent communication
- Use debate protocols for consensus, not simple voting
- Set iteration limits on all agent execution
- Start simple — add multi-agent complexity only when single-agent fails

---

# Mode: EXPLORE

Tree of Thoughts: explore solution space with systematic pruning and expansion.

## Process

**Phase 1: Exploration**
ALWAYS spawn 3 sadd-explorer subagents for divergent coverage.
ALWAYS set maxTurns: 15 for this mode to prevent runaway exploration loops.

**Phase 2: Pruning** — Meta-judge generates spec, ALWAYS spawn 3 judge subagents to score and vote for top 3.

**Phase 3: Expansion** — ALWAYS spawn 3 agent subagents to expand selected proposals into full solutions.

**Phase 4: Evaluation** — ALWAYS spawn 2nd meta-judge + 3 judge subagents to assess solutions.

**Phase 5: Adaptive Strategy** — SELECT_AND_POLISH (unanimous), REDESIGN (all < 3.0), FULL_SYNTHESIS (split).

Max 2 redesign cycles. If exhausted without passing, escalate to human.

---

## Output Formats

COMPETE: Final solution + candidate solutions (`.a|.b|.c.md`) + judge reports (`.specs/reports/`)

EXECUTE: Task output with verification history (SPAWN/PLAN-DRIVEN) or pass/fail report (VERIFY)

JUDGE: Evaluation report with scores, evidence, and verdict (single) or consensus/disagreement summary (debate)

DESIGN: Architecture recommendation with pattern rationale, coordination mechanism, and failure mitigations

EXPLORE: Final solution + proposals + pruning votes + evaluation reports

---

## Failure Handling

| Mode | Failure Mode | Action |
|------|--------------|--------|
| COMPETE | All solutions < 3.0 after 2 redesigns | Escalate to human |
| EXECUTE | Verification failed after max retries | Escalate with failure analysis |
| JUDGE | 3 debate rounds without consensus | Report disagreements |
| EXPLORE | Max redesign cycles exhausted | Escalate to human |

All modes include structured failure signals with retry_possible flag.