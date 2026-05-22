---
name: do-competitively
description: Execute high-stakes tasks through competitive multi-agent generation, meta-judge evaluation, and adaptive synthesis - use when quality matters more than speed and parallel exploration would reveal different approaches
argument-hint: Task description and optional output path
---

## Decision Router

IF task is trivial or low-stakes → use simpler execution (competitive overhead not justified)
IF task requires novel approach discovery → competitive generation to explore solution space
IF quality matters more than speed → competitive with meta-judge specification
IF three or more independent approaches exist → competitive generation with all three running
IF solutions exist but quality is uncertain → meta-judge evaluation then selective synthesis

# do-competitively

Execute tasks through competitive multi-agent generation, meta-judge evaluation, and evidence-based synthesis to produce superior results by combining the best elements from parallel implementations.

## Policy: When to Use

This skill implements the Generate-Critique-Synthesize (GCS) pattern for high-stakes tasks where:

- Multiple valid approaches exist and the best is unclear
- Quality matters more than speed
- Self-critique during generation improves outcomes
- Meta-judge tailored rubrics outperform hardcoded criteria

**Skip this skill when:**
- Task is simple with one obvious approach
- Speed is critical
- Resources are limited (this pattern is expensive)

## Mechanism: Three-Phase Process

### Phase 1: Parallel Generation + Meta-Judge

Launch 4 agents in parallel: 3 generators + 1 meta-judge.

**Meta-judge** produces evaluation specification YAML (rubrics, scoring criteria). This runs in parallel because it only needs the task description, not generator outputs.

**Generators** produce independent solutions to the same problem. Each receives identical context but explores different approaches. Solutions saved with `.a.md`, `.b.md`, `.c.md` suffixes.

**Dispatch order:** Meta-judge first (needs time to collect context), then generators.

**Prompt structure for generators:**
- Task description with constraints
- Required output filename (with [a|b|c] identifier)
- Self-critique loop: verify questions, answer, revise

### Phase 2: Multi-Judge Evaluation

Wait for all Phase 1 agents before dispatching judges.

Launch 3 judges in parallel. Each receives:
- The exact meta-judge evaluation specification YAML (verbatim, no modifications)
- Paths to all three candidate solutions

Each judge produces:
- Comparative analysis with evidence
- Per-solution scores against meta-judge criteria
- Vote for preferred solution

Reports saved to `.specs/reports/{solution-name}-{date}.[1|2|3].md`

**Critical:** Never tell judges the score threshold. They must evaluate without bias.

### Phase 2.5: Adaptive Strategy Selection

The orchestrator (not a subagent) analyzes judge outputs.

**Three strategies based on results:**

| Condition | Strategy | Action |
|-----------|----------|--------|
| Unanimous vote + clear winner | SELECT_AND_POLISH | Take winning solution, apply judge feedback |
| All solutions below 3.0/5.0 | REDESIGN | Return to Phase 1 with lessons learned |
| Split decision with merit | FULL_SYNTHESIS | Launch synthesizer to combine best elements |

Parse VOTE lines from judge replies (do not read report files directly).

### Phase 3: Synthesis (Conditional)

Only runs when FULL_SYNTHESIS strategy selected.

Launch one synthesizer agent with all solutions and evaluation reports. Agent:
- Copies superior sections when one solution clearly wins
- Combines approaches when hybrid is better
- Fixes identified issues
- Documents decisions (what from where and why)

## Setup

Create reports directory before starting:
```bash
mkdir -p .specs/reports
```

Report naming: `.specs/reports/{solution-name}-{YYYY-MM-DD}.[1|2|3].md`

## Output

Final solution at specified output path. Candidate solutions preserved with `.a.md`, `.b.md`, `.c.md` suffixes for reference. Judge reports in `.specs/reports/`.

Reply includes strategy used, files created, and synthesis decisions table.

## Key Principles

- Meta-judge runs once (same spec for all judges across all rounds)
- Judges communicate through filesystem (orchestrator does not mediate)
- Self-critique loop in generation catches issues before evaluation
- Adaptive strategy avoids waste: polish winners, redesign failures, synthesize splits