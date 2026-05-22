---
name: sadd-judge
description: "Evaluate work using meta-judge then judge sub-agents: single judge for routine checks, 3-judge debate for high-stakes consensus"
when_to_use: |
  When user says 'judge this', 'evaluate', 'assess quality', 'verify this', 'check my work', 'review this solution', 'grade this', 'is this any good'. IMMEDIATELY when user asks for LLM-as-Judge verification or quality assessment. FIRST when evaluation requires independent criteria (not hardcoded). DO NOT use when you want explicit multi-round adversarial debate with a panel of judges — use the debate-oriented evaluation skill instead.
argument-hint: "[evaluation-focus] [--debate]"
---

## Decision Router

IF routine quality check without specific focus → single meta-judge + judge pipeline
IF high-stakes evaluation requiring consensus across multiple perspectives → meta-judge then 3 debating judges
IF user provides an evaluation focus → scope the meta-judge to that dimension
IF judges cannot reach consensus after 3 rounds → report persistent disagreements for human review
IF there is no work to evaluate → ask what should be evaluated

# Judge

Launch a two-phase or multi-phase evaluation pipeline. A meta-judge generates tailored evaluation criteria, then one or more judges apply those criteria with fresh context for unbiased assessment. This is report-only — findings are presented without modifying the work.

## Core Principle

Structured evaluation must separate criteria generation from criteria application to prevent confirmation bias. The meta-judge defines what "good" looks like for this specific artifact; the judge(s) measure against that definition with independent reasoning.

## Meta-Judge Evaluation Pattern

See the meta-judge evaluation pattern documentation for the shared pattern (YAML spec structure, threshold scoring, critical constraints).

## Mode 1: Single Judge (Routine Evaluation)

### Process

**Phase 1: Context Extraction**
Identify work to evaluate from conversation history or user input. Extract: original task, output produced, files involved, constraints mentioned, artifact type. Present scope summary.

**Phase 2: Dispatch Meta-Judge**
Follow the shared meta-judge pattern. Include original user prompt, context about the work, artifact type, and evaluation focus.

**Phase 3: Dispatch Judge**
Provide original task, work output summary, files involved, and the EXACT meta-judge specification YAML.

**Phase 4: Process and Present Results**
Validate evaluation (scores in range, evidence-supported, no contradictions), then present with verdict, key findings, and follow-up options.

## Mode 2: Judge with Debate (High-Stakes Evaluation)

### Process

**Phase 0: Setup** — Create `.specs/reports/` for judge output files.

**Phase 1: Meta-Judge** — Dispatch one meta-judge with task description, solution context, and artifact type. Generate evaluation specification YAML covering all relevant quality dimensions.

**Phase 2: Independent Analysis (Round 0)** — Launch 3 judges in parallel. Each receives solution path, task description, and EXACT meta-judge spec YAML. Each produces independent assessment saved to `.specs/reports/{solution-name}-{date}.[1|2|3].md` with per-criterion scores, evidence, overall score, and key strengths/weaknesses.

**Phase 3: Consensus Check** — After each evaluation round, verify: all overall scores within 0.5 points of each other, no criterion has >1 point gap across any two judges, all judges explicitly accept consensus.

**Phase 4: Debate Rounds (max 3)** — For each round, launch 3 judges in parallel. Each reads own previous report and other judges' reports from filesystem (orchestrator does not mediate). Each identifies disagreements (>1 point gap on any criterion), defends position with evidence, challenges counter-positions, and revises if convinced. Append debate round section to their report file. After each round, return to consensus check.

**Phase 5: Final Report**
- **If consensus achieved:** Synthesize consensus report with consolidated scores per criterion, consensus strengths and weaknesses, debate summary (rounds to consensus, initial disagreements, how resolved), and final recommendation.
- **If no consensus after 3 rounds:** Report persistent disagreements with specific criteria where consensus was not reached, all judge reports for human review, and flag for manual evaluation.

## Output

Single judge mode presents results directly to the user. Low scores indicate improvement opportunities, not failures.

Debate mode saves judge report files in `.specs/reports/` and presents a final synthesis with consensus or disagreement summary and per-judge scores.

## Design Decisions

### Why meta-judge before judge (not hardcoded criteria)
Hardcoded criteria are generic and miss artifact-specific nuances. A meta-judge dynamically generates tailored rubrics matching the specific artifact type, focus, and context. This produces more precise evaluations without maintaining rubric templates.

### Why context isolation (not evaluating in-session)
Evaluating work within the same context window that produced it creates confirmation bias. A fresh judge sub-agent with only the work and criteria avoids the "I built this so it must be good" trap.

### Why single judge for routine checks (not multi-judge)
For routine quality checks, one focused judge with fresh context provides sufficient signal at lower cost. Multi-judge debate is reserved for high-stakes evaluations where consensus is critical.

### Why meta-judge runs once for debate (not per round)
The evaluation criteria are a property of the task, not the debate. Changing criteria between rounds would make score comparisons meaningless. A single shared specification grounds all debate in the same measurement framework.

### Why judges communicate through filesystem for debate (not orchestrator mediation)
The orchestrator reading and paraphrasing judge reports would introduce the telephone game problem — lossy compression of detailed reasoning. Direct filesystem reads preserve full fidelity and avoid context pollution in the orchestrator.

### Why debate (not simple averaging)
Averaging scores hides meaningful disagreements. A 4/5 from one judge and a 2/5 from another might average to 3/5, but that obscures a fundamental disagreement about quality. Debate surfaces why the disagreement exists and whether one judge's evidence is more compelling.
