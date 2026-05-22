---
name: sadd-dispatch
description: "Dispatch sub-agents with CoT reasoning and self-critique: single-task dispatch with auto model selection, or plan-driven multi-task execution with code review gates"
argument-hint: "Task description [--model opus|sonnet|haiku] [--agent <name>] [--plan <path>]"
---

## Decision Router

IF user asks to delegate a focused single task to a sub-agent → single mode: analyze task, select model, dispatch with CoT prefix and self-critique suffix
IF executing a plan with independent tasks sharing no state or files → parallel plan mode: dispatch one sub-agent per task simultaneously, then review holistically
IF executing a plan with sequential or dependent tasks → sequential plan mode: dispatch one sub-agent per task in order, review after each
IF investigating 3+ unrelated issues without shared state → parallel investigation mode: group by subsystem, dispatch per domain, review for conflicts
IF the task is trivial (single file, mechanical change) → use Haiku without specialized agent
IF tasks share state or files → do NOT parallelize; use sequential with code review between each

# Dispatch Sub-Agent

Dispatch sub-agents with isolated context for focused execution. Supports single-task dispatch with automatic model selection, or plan-driven multi-task execution with code review as a quality gate. Each sub-agent works in a clean context window without accumulated context pollution.

## Core Principle

Context isolation is the primary benefit of sub-agents. Each sub-agent works in a clean context window without accumulated context pollution. The orchestrator owns all cognition; the sub-agent owns only execution.

## Mode 1: Single Sub-Agent

Dispatch one sub-agent with isolated context for a focused task. Best for single requests where a dedicated agent handles implementation, research, or analysis.

### Process

**Phase 1: Task Analysis** — Determine type (implementation, research, documentation, review, architecture, testing, transformation), complexity (high/medium/low), output size (large/medium/small), and domain match.

**Phase 2: Model Selection**

| Profile | Model |
|---------|-------|
| Complex reasoning (architecture, design, critical decisions) | Opus |
| Specialized domain with complexity | Opus + specialized agent |
| Non-complex but long output | Sonnet |
| Simple and short | Haiku |
| Default (uncertain) | Opus |

**Phase 3: Specialized Agent Matching** — Use a specialized agent when the task clearly benefits from domain expertise (developer for code, researcher for investigation, architect for design). Skip specialization for trivial tasks. If no matching specialist exists, use general-purpose.

**Phase 4: Construct Sub-Agent Prompt** — Build with three mandatory components:

1. **CoT Prefix (first):** "Let me understand what is being asked... let me break this down... let me consider what could go wrong... let me verify my approach before proceeding"
2. **Task Body:** Task description, constraints, context, expected output format
3. **Self-Critique Suffix (last):** Generate 5 verification questions specific to this task, answer each with evidence, revise if gaps found. Must not submit until all questions have satisfactory answers.

**Phase 5: Dispatch** — Use the Task tool with selected model. Pass only context relevant to this specific task — never the entire conversation history.

### Output

The sub-agent returns its work directly. The orchestrator reviews output quality before accepting.

## Mode 2: Plan-Driven Multi-Task

Execute plans by dispatching a fresh sub-agent per task with code review as a quality gate between them. Each sub-agent gets a clean context focused on its specific task, avoiding context pollution from accumulated session state.

### Sequential Execution (dependent tasks)

1. Load plan and create task tracking
2. For each task in order:
   - Dispatch a fresh sub-agent with exact task specification from the plan, relevant context, and expected output format
   - Sub-agent implements with CoT reasoning and self-critique, then reports back with summary
   - Dispatch a code review sub-agent to check the work against plan requirements
   - Fix any Critical or Important issues before proceeding
3. Final review after all tasks complete — validate overall architecture and plan completeness

### Parallel Execution (independent tasks)

1. Load plan and group tasks by dependency
2. Dispatch one sub-agent per independent task simultaneously — each receives focused scope, clear goals, and output constraints
3. Review all outputs after all agents return — check for conflicts, run full test suite
4. Fix integration issues if found

### Parallel Investigation (unrelated failures)

1. Group failures by file or subsystem — each domain must be independent
2. Each agent gets specific scope (one file/subsystem), clear goal (fix these tests), constraints (don't change other code)
3. All agents run concurrently
4. Review summaries, verify no conflicts, run full suite

### Quality Gates

- Review output after each task (sequential) or after batch (parallel)
- Fix Critical issues immediately, Important issues before next task
- Run full test suite after integration

### When to Stop

Stop and ask for help when: a blocker is hit mid-task, plan has critical gaps, verification fails repeatedly, or instructions are unclear. Do not force through blockers.

## Design Decisions

### Why CoT prefix + self-critique suffix (not just a task description)
The CoT prefix forces structured reasoning before action, preventing the "rush to implement" failure mode. The self-critique suffix provides a quality gate before submission, catching the most common errors (incomplete requirements, missed edge cases, pattern violations).

### Why auto model selection (not always Opus)
Model tiering saves cost without sacrificing quality. Haiku handles ~30% of real-world tasks (mechanical updates, documentation tweaks). Opus reserved for the ~40% that genuinely need reasoning depth.

### Why per-task sub-agents (not one agent for all tasks in plan mode)
Each sub-agent starts with a clean context focused on its specific task. Accumulated context from previous tasks (file exploration, decisions made, dead ends) would pollute a single agent's reasoning. Fresh context per task means each decision is made with full attention.

### Why code review between tasks (not at the end)
Catching issues immediately prevents cascading failures where later tasks build on broken foundations. The cost of fixing an issue grows with each downstream task that depends on it.
