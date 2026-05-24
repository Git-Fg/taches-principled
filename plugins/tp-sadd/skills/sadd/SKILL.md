---
name: sadd
description: "Subagent-Driven Development — design multi-agent systems and execute tasks with quality verification: generate competing solutions with meta-judge evaluation, dispatch tasks via context-isolated subagents, run structured judge evaluations, or explore solution space with tree-of-thoughts pruning. Modes: COMPETE, EXECUTE, JUDGE, DESIGN, EXPLORE."
when_to_use: |
  COMPETE: 'best-of-N', 'competitive generation', 'generate multiple solutions', 'quality over speed'
  EXECUTE: 'dispatch subagent', 'launch agent', 'delegate this', 'implement with verification', 'run in background'
  JUDGE: 'evaluate', 'judge this', 'assess quality', 'verify', 'check my work', 'multi-judge debate'
  DESIGN: 'design architecture', 'multi-agent', 'supervisor pattern', 'swarm', 'coordinate agents'
  EXPLORE: 'tree of thoughts', 'explore solution space', 'generate and prune', 'ideate then narrow'
  IMMEDIATELY when user wants to delegate work with quality verification or design multi-agent systems.
  FIRST when task requires model selection, independent verification, or parallel execution.
---

## Decision Router

IF generating multiple competing solutions with meta-judge evaluation → COMPETE mode
IF dispatching tasks via context-isolated subagents with optional verification → EXECUTE mode
IF evaluating work with meta-judge + judge pipeline or multi-judge debate → JUDGE mode
IF designing multi-agent architecture (supervisor/swarm/hierarchical patterns) → DESIGN mode
IF exploring solution space with systematic pruning (ToT) → EXPLORE mode

# Mode: COMPETE

Generate 3+ solutions in parallel with meta-judge evaluation and adaptive synthesis.

## Process

**Phase 1: Parallel Generation + Meta-Judge**
Spawn 4 agents in parallel: meta-judge (generates evaluation YAML) + 3 generators producing independent solutions.

**Phase 2: Multi-Judge Evaluation**
3 judges in parallel evaluate all solutions against meta-judge spec. Each produces comparative analysis and vote.

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

Dispatch fresh subagents with isolated context. Three modes:

**DISPATCH:** Simple dispatch with auto model selection, CoT prefix, self-critique suffix.

**VERIFY:** Meta-judge + implementor + judge with retry loop (score >= 4.0 = pass, max 3 retries).

**PLAN-DRIVEN:** Execute plan tasks sequentially with code review between each, or in parallel with integration check.

## Model Selection

| Profile | Model |
|---------|-------|
| Complex reasoning (architecture, design) | Opus |
| Medium complexity | Sonnet |
| Simple transformations | Haiku |

---

# Mode: JUDGE

Evaluate work using meta-judge then judge subagents. Three modes:

**SINGLE:** Meta-judge generates spec, one judge evaluates.

**DEBATE:** 3 judges in parallel, consensus check after each round, max 3 rounds.

**MULTI-ROUND:** Independent analysis → debate rounds → consensus or disagreement report.

## Key Principle

Meta-judge runs once (shared spec grounds all evaluation). Judges communicate via filesystem, not through orchestrator.

---

# Mode: DESIGN

Design multi-agent architectures for context isolation and coordination.

**Supervisor/Orchestrator:** Central agent decomposes, dispatches, synthesizes. Use for clear decomposition with human oversight.

**Peer-to-Peer/Swarm:** No central control, agents communicate via filesystem. Use for flexible exploration.

**Hierarchical:** Strategic → Planning → Execution layers. Use for large-scale projects.

## Core Principle

Context isolation is the primary benefit — subagents exist to give each execution a clean context window, not to anthropomorphize role division.

## Design Guidelines

- Default to filesystem-based inter-agent communication
- Use debate protocols for consensus, not simple voting
- Set iteration limits on all agent execution
- Start simple — add multi-agent complexity only when single-agent fails

---

# Mode: EXPLORE

Tree of Thoughts: explore solution space with systematic pruning and expansion.

## Process

**Phase 1: Exploration** — 3 agents, 6 proposals each (high-probability + creative).

**Phase 2: Pruning** — Meta-judge generates spec, 3 judges score and vote for top 3.

**Phase 3: Expansion** — 3 agents expand selected proposals into full solutions.

**Phase 4: Evaluation** — 2nd meta-judge + 3 judges assess solutions.

**Phase 5: Adaptive Strategy** — SELECT_AND_POLISH (unanimous), REDESIGN (all < 3.0), FULL_SYNTHESIS (split).

Max 2 redesign cycles. If exhausted without passing, escalate to human.

---

## Output Formats

COMPETE: Final solution + candidate solutions (`.a|.b|.c.md`) + judge reports (`.specs/reports/`)

EXECUTE: Task output with verification history (DISPATCH/PLAN-DRIVEN) or pass/fail report (VERIFY)

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