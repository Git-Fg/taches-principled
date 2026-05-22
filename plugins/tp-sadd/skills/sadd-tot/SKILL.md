---
name: sadd-tot
description: "Explore solution space through systematic ideation, pruning, and expansion — generate diverse proposals, prune to top 3, develop full solutions, evaluate with judges"
when_to_use: |
  When user says 'tree of thoughts', 'explore solution space', 'systematic exploration', 'generate and prune', 'multiple proposals', 'ideate then narrow'. IMMEDIATELY when user wants to explore many approaches before committing to one. FIRST when task requires exploring diverse solution paths with pruning before implementation.
argument-hint: "Task description [--output <path>]"
---

## Decision Router

IF a task requires exploring multiple solution paths before committing to implementation → use Tree of Thoughts for systematic exploration, pruning, and expansion
IF a single good solution approach suffices → use competitive generation instead (cheaper — skips exploration phase)
IF all expanded solutions score below 3.0 → trigger REDESIGN (return to expansion with lessons learned, max 2 redesign cycles)
IF the solution space is well-understood with clear best practices → standard implementation is more efficient

# Tree of Thoughts

Execute complex reasoning through systematic exploration: 3 agents generate diverse proposals (high-probability and creative), a meta-judge and pruning judges select the top 3, then 3 agents expand those into full solutions. A second meta-judge and evaluation judges assess solutions, with adaptive strategy selection for the final output.

## Core Principle

Systematic exploration before commitment produces better outcomes than diving into the first viable approach. The Tree of Thoughts pattern explicitly explores the solution space, prunes unpromising paths, and develops only the most promising branches — avoiding premature convergence on suboptimal approaches.

## Process

### Phase 1: Exploration (6 proposals per agent, 3 agents in parallel)

Launch 3 exploration agents. Each produces 6 high-level approaches (not implementations) covering both conventional (high probability >0.80) and creative (low probability <0.10) regions of the solution space. Each proposal includes: description, key design decisions, trade-offs, probability estimate, complexity, and risks.

Proposals saved to `.specs/research/{name}-{date}.proposals.[a|b|c].md`.

### Phase 1.5: Pruning Meta-Judge (in parallel with Phase 1)

Launch a pruning meta-judge in parallel with exploration agents. The meta-judge generates an evaluation specification YAML for evaluating high-level proposals. Criteria focus on feasibility, alignment with requirements, potential for quality, and risk manageability.

Follow the meta-judge evaluation pattern (see `meta-judge-pattern.md` in this plugin's references directory).

### Phase 2: Pruning (3 judges, select top 3 proposals)

After BOTH Phase 1 and Phase 1.5 complete, launch 3 pruning judges in parallel. Each receives ALL proposals and the EXACT pruning meta-judge specification. Each scores proposals and votes for their top 3.

Aggregate votes using ranked choice (1st=3 points, 2nd=2 points, 3rd=1 point). Select top 3 by total points. Handle ties by comparing average criterion scores. Document selection in `.specs/research/{name}-{date}.selection.md`.

### Phase 3: Expansion (3 agents, one per selected proposal)

Launch 3 expansion agents, each developing one selected proposal into a full solution. Each receives: the original task, their assigned proposal (verbatim), judge feedback from pruning phase to address, and expected output format.

Expansion agents use CoT reasoning + self-critique. Solutions saved with unique identifiers (`solution.a.md`, `solution.b.md`, `solution.c.md`).

### Phase 3.5: Evaluation Meta-Judge (in parallel with Phase 3)

Launch a second meta-judge in parallel with expansion agents. Generates an evaluation specification YAML for evaluating full solution implementations. Criteria focused on comparative evaluation across multiple solutions.

See `meta-judge-pattern.md` in this plugin's references directory.

### Phase 4: Evaluation (3 judges)

After BOTH Phase 3 and Phase 3.5 complete, launch 3 evaluation judges in parallel. Each receives ALL solutions and the EXACT evaluation meta-judge specification. Each produces: comparative analysis, evidence-based ratings, and final VOTE.

Parse only structured headers from judges.

### Phase 4.5: Adaptive Strategy Selection

| Condition | Strategy |
|-----------|----------|
| Unanimous vote | SELECT_AND_POLISH — polish winner with targeted improvements from judge feedback |
| All avg scores < 3.0 | REDESIGN — analyze failure modes, return to Phase 3 with lessons learned (max 2 redesign cycles, then escalate) |
| Otherwise | FULL_SYNTHESIS — proceed to Phase 5 |

### Phase 5: Synthesis (FULL_SYNTHESIS only)

Launch one synthesis agent with ALL solutions and ALL evaluation reports. Synthesizes by: copying superior sections when one solution wins, combining approaches when hybrid is better, fixing identified issues. Documents every decision with rationale and source attribution.

## Outputs

| Phase | Output | Location |
|-------|--------|----------|
| Exploration | Proposals | `.specs/research/{name}-{date}.proposals.[a\|b\|c].md` |
| Pruning | Judge votes | `.specs/research/{name}-{date}.pruning.[1\|2\|3].md` |
| Selection | Vote tally | `.specs/research/{name}-{date}.selection.md` |
| Expansion | Full solutions | `solution.[a\|b\|c].md` |
| Evaluation | Judge reports | `.specs/reports/{name}-{date}.[1\|2\|3].md` |
| Synthesis | Final solution | `{output_path}` |

## Design Decisions

### Why exploration + pruning before expansion (not direct generation)
Direct generation of full solutions biases toward the first viable approach the agent thinks of. By separating exploration (many cheap proposals) from expansion (fewer expensive implementations), the pattern explores more of the solution space per unit of cost. ~70% of proposals are pruned before any implementation cost is incurred.

### Why two meta-judges (pruning + evaluation)
Proposals and full implementations require different evaluation criteria. Proposals are judged on feasibility and promise. Implementations are judged on completeness, correctness, and quality. A single specification cannot capture both. Two meta-judges produce appropriate criteria for each phase.

### Why max 2 redesign cycles (not infinite)
Redesign demonstrates that the problem itself may be poorly defined or missing constraints. Two cycles is sufficient to determine whether the issue is solvable with better guidance. After two failures, the problem likely needs human intervention to clarify requirements or constraints.
