---
name: judge-with-debate
description: "Multi-round debate between independent judges until consensus — for high-stakes evaluation where rigorous argumentation improves assessment accuracy"
when_to_use: |
  When user says 'debate this', 'multi-judge debate', 'reach consensus', 'adversarial evaluation', 'multiple perspectives on quality', 'high-stakes evaluation'. IMMEDIATELY when user asks for evaluation through structured debate between judges. FIRST when high-stakes decisions require arguing positions before consensus. DO NOT use for routine quality checks — use sadd-judge instead.
argument-hint: Solution path(s) and evaluation criteria
---

## Decision Router

IF evaluating routine quality check → single judge (debate overhead not justified)
IF high-stakes evaluation requiring consensus → meta-judge then 3 debating judges
IF user provides evaluation focus → scope meta-judge to that dimension
IF judges cannot reach consensus after 3 rounds → report persistent disagreements for human review
IF no work to evaluate → ask what should be evaluated

# judge-with-debate

Evaluate solutions through multi-agent debate where independent judges analyze, challenge each other's assessments, and iteratively refine their evaluations until reaching consensus or maximum rounds.

## Policy: When to Use

For high-stakes evaluation where multiple perspectives and rigorous argumentation improve assessment accuracy. Structured debate forces judges to defend positions with evidence and consider counter-arguments.

**Key benefits over single-judge:**
- Meta-judge produces tailored rubrics before evaluation
- Three independent perspectives reduce individual bias
- Evidence-based debate surfaces disagreements
- Iterative refinement drives convergence

**Skip this skill when:**
- Routine check with no specific stakes
- Speed over accuracy
- Single perspective sufficient

## Mechanism: Three-Phase Process

### Phase 0.5: Meta-Judge

Dispatch one meta-judge with:
- Task description (what solution was supposed to accomplish)
- Solution context
- Artifact type

Meta-judge produces evaluation specification YAML covering all quality dimensions. This runs ONCE and is shared by all judges across all rounds.

**Prompt template:**
```
Generate an evaluation specification yaml for the following task. You will produce rubrics, checklists, and scoring criteria that judge agents will use through multi-round debate.

Task: {description}
Context: {any relevant context}
Artifact type: {code|documentation|configuration|etc.}
Evaluation mode: Multi-judge debate with consensus-seeking
```

### Phase 1: Independent Analysis

Spawn 3 judges in parallel (Opus recommended).

Each receives:
- Path to solution(s) being evaluated
- Exact meta-judge evaluation specification YAML
- Task description

Each produces independent assessment saved to `.specs/reports/{solution-name}-{date}.[1|2|3].md`:
- Per-criterion scores with evidence
- Specific quotes supporting ratings
- Overall weighted score
- Key strengths and weaknesses

**Key principle:** Independence in initial analysis prevents groupthink.

### Phase 2: Debate Rounds (Max 3)

For each round, launch 3 judges in parallel. Each reads:
- Their own previous report
- Other judges' reports (from filesystem directly)
- Original solution
- Meta-judge evaluation specification

Each judge:
- Identifies disagreements (score gap >1 point on any criterion)
- Defends position with evidence from solution and specification
- Challenges other judges' positions with counter-evidence
- Revises assessment if convinced

Appends "Debate Round {R}" section to their report file.

**Orchestrator does not mediate.** Judges communicate through filesystem only.

### Phase 3: Consensus Check

After each debate round:

**Consensus achieved when:**
- All overall scores within 0.5 points
- No criterion has >1 point gap across any two judges
- All judges explicitly accept consensus

**If no consensus after 3 rounds:**
- Report persistent disagreements
- Provide all reports for human review
- Flag automated evaluation limitation

### Phase 4: Final Report

**If consensus:**
```
Consensus Scores
| Criterion | Judge 1 | Judge 2 | Judge 3 | Final |
|-----------|---------|---------|---------|-------|
| {Name}    | {X}/5   | {X}/5   | {X}/5   | {X}/5 |

Consensus Overall: {avg}/5.0

Debate Summary
- Rounds to consensus: {N}
- Initial disagreements: {list with specific criteria}
- How resolved: {explanation}

Final recommendation with justification
```

**If no consensus:**
- All judges' final scores showing disagreements
- Specific criteria where consensus wasn't reached
- Analysis of why consensus couldn't be reached

## Setup

Create reports directory:
```bash
mkdir -p .specs/reports
```

Report naming: `.specs/reports/{solution-name}-{YYYY-MM-DD}.[1|2|3].md`

## Key Principles

- Meta-judge runs once (shared spec grounds all debate)
- Judges read other reports from filesystem directly
- Orchestrator does not paraphrase reports (telephone game problem)
- Maximum 3 debate rounds (diminishing returns after)
- Require evidence for changing positions
- Same evaluation specification across all rounds (criteria are property of task, not debate)