---
name: task-model-fit
description: "Reference for evaluating whether a task suits LLM-based planning or traditional code. Read when unsure whether to use create-plans or implement directly."
type: reference
---

# Task-Model Fit for Planning

Use this reference to decide whether `create-plans` is the right tool or if direct implementation serves better.

## Decision Table

| Proceed with LLM Planning | Stop and use traditional code |
|---------------------------|-------------------------------|
| Multi-subsystem project with scope not fixed upfront | Simple single-file script |
| Ambiguous requirements needing decomposition | Precise algorithmic task (sorting, math, parsing) |
| Research + implementation mixed | Real-time or sub-second latency required |
| Many unknown dependencies to discover | 100% accuracy requirement (hallucination risk) |
| Output format not predetermined desired | Deterministic identical output required |
| Parallel exploration across domains beneficial | Sequential dependency chain >8 steps |

## When LLM Planning Works Well

**Strengths:**

- **Synthesis across sources** — Combines information from multiple inputs (files, docs, APIs) better than rule-based approaches
- **Judgment with rubrics** — Grading, evaluation, classification where criteria map to language reasoning
- **Ambiguity handling** — Works with vague requirements by asking clarifying questions and exploring paths
- **Context navigation** — Explores large codebases, identifies patterns, discovers dependencies
- **Multi-path exploration** — Parallel investigation of alternatives before committing to approach
- **Domain knowledge leverage** — Benefits from training data to suggest best practices without explicit research

**Signal:** If the task requires understanding intent, weighing trade-offs, or navigating unclear requirements — LLM planning adds value.

## When Traditional Code Is Better

**Limitations:**

- **Precise computation** — Math, counting, exact algorithms where rounding or approximation fails
- **Perfect accuracy** — Hallucination risk makes 100% precision impossible; acceptable error rates must be defined upfront
- **Latency constraints** — LLM inference is measured in seconds; sub-second response needs traditional code
- **Deterministic output** — Same input must produce bit-identical output; LLMs cannot guarantee this
- **Sequential dependencies** — Each step depends heavily on prior result; errors compound in chains >8 tasks
- **Proprietary data** — Model lacks necessary context that cannot be injected via prompts

**Signal:** If the task has a known correct answer, must run fast, or requires surgical precision — write the code directly.

## Red Flags — Problems That Look Like Planning But Are Not

These tasks seem like planning candidates but are better handled by direct implementation:

| Red Flag | Why LLM Planning Fails | Better Approach |
|----------|------------------------|-----------------|
| "Automate this script" | Execution is trivial; planning adds overhead | Write/run the script directly |
| "Refactor this module" | Well-scoped, file-limited task | Edit tools with explicit scope |
| "Add error handling" | Pattern is known, not exploratory | Template or linter rule |
| "Migrate from X to Y" | Mechanical transformation | Script or codemod |
| "Set up CI/CD" | CLI-driven, known steps | Provider docs + CLI |
| "Write unit tests" | Pattern-following, not exploratory | Test generation tool or template |
| "Fix this bug" | Requires root-cause tracing, not planning | Debug skill or direct inspection |
| "Optimize this query" | Precise measurement and adjustment | Profiling tools + targeted changes |

**Signal:** If you already know the steps and could write a script to do it — it is not a planning task.

## Quick Heuristic

Before invoking `create-plans`, ask:

1. Do I know the exact steps? → No planning needed, implement directly
2. Is it a single-file or well-scoped change? → No planning needed, implement directly
3. Does it require discovering unknown dependencies? → Planning warranted
4. Are there multiple valid approaches to evaluate? → Planning warranted
5. Is the output natural language (docs, analysis, reports)? → Planning warranted

**Rule:** If exploration or judgment is required, plan. If execution is required, code.