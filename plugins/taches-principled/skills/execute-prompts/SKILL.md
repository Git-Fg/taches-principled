---
name: execute-prompts
description: "Execute prompts from .principled/prompts/ via delegated sub-tasks. Use when running prompt files."
when_to_use: "Use when user asks to run, execute, or launch generated prompt files."
argument-hint: [prompt-id or description]
---

## Routing Guidance

- Do NOT use for interactive debugging, single-file edits, or one-off questions that don't involve prompt files.
- Do NOT use for executing plan files — use execute-plans instead.

## Decision Router

IF executing a single prompt → Read the execute-prompt workflow file from the workflows folder BEFORE starting
IF executing parallel prompts → Read the execute-prompt workflow file from the workflows folder for parallel coordination rules
IF executing sequential prompts → Read the execute-prompt workflow file from the workflows folder for sequential handoff rules

This skill is self-contained — no cross-skill routing needed.

---

## Core Principle

**Delegate execution to preserve orchestration capacity.** Sub-tasks execute in isolated contexts while the main conversation remains lean for iteration, error recovery, and coordination.

---

## Policy vs. Mechanism

**Policy** = which execution strategy to use (determined by prompt relationships)
**Mechanism** = how to parse, resolve, and execute (the operational method)

State the strategy based on prompt dependencies; keep the parsing logic separate.

### Strategy Selection

| Scenario | Strategy | Why |
|----------|----------|-----|
| One prompt specified | Single | No coordination needed |
| Multiple independent prompts | Parallel | Maximize throughput |
| Multiple dependent prompts | Sequential | Each must complete before next |

**Default:** When multiple prompts are specified without a flag, use sequential for safety.

---

## Execution Strategies

### Single Execution

Read the complete prompt file, delegate to a general-purpose subagent, wait for completion, archive to `.principled/prompts/completed/`, commit work, return results.

### Parallel Execution

Read all prompt files, track each prompt's execution as a distinct unit, dispatch ALL subagents in one message for true parallelization. After completion, archive all prompts, commit all work, return consolidated results.

**Critical constraint:** ALL subagent dispatches MUST occur in a SINGLE message. Sequential token emission creates sequential execution.

### Sequential Execution

Read first prompt file, dispatch subagent, wait for completion, track progression through the chain. Repeat for each subsequent prompt. If any prompt fails, stop the chain and report.

---

## Argument Parsing

### Input Forms

| Input | Interpretation |
|-------|----------------|
| (empty) | Most recently created prompt |
| `"005"` | Prompt number 005 |
| `"user-auth"` | Filename containing "user-auth" |
| `"005 006 007"` | Multiple prompts (default: sequential) |
| `"005 006 007 --parallel"` | Multiple prompts, parallel |
| `"005 006 007 --sequential"` | Multiple prompts, sequential |

**Parsing rules:** Arguments that are not `--parallel` or `--sequential` are prompt identifiers. Multiple prompts without a flag default to sequential.

---

## File Resolution

### Resolution Principle

For each prompt identifier, resolve to a concrete file path. Match by number (zero-padded) or by text (filename contains string). Always verify file exists before dispatch.

| Outcome | Action |
|---------|--------|
| Exactly one match | Use that file |
| Multiple matches | List candidates, ask user to choose |
| No match | Track as failed state, report error |

---

## Archival and Git Workflow

### Archival Principle

Archive to `.principled/prompts/completed/` only after confirmed completion. On failure, keep in place and report error.

### Git Workflow

Stage files explicitly: `git add [file1] [file2]`. Never `git add .` — stage only files you modified. Commit format: `[type]: [specific description]`.

After execution completes, consider capturing insights from the results into project memory via `refine memorize`.

---

## Execution Gotchas

**The Thought/Action/Observation Anti-Pattern is documented in the execute-plans skill.**

### Anti-Patterns

**Parallelization Without True Concurrency:** Spawning subagents across multiple messages for "parallel" execution. Fix: All parallel subagent dispatches MUST be in a single message.

**Ignoring Dependencies in Sequential:** Running prompts in sequence without checking if they have actual dependencies. Fix: Explicitly ask user if prompts are dependent, or default to parallel when unsure.

**Archiving Before Completion:** Archiving prompts before execution finishes. Fix: Archive only after confirmed completion.

---

## Numeric Thresholds

| Metric | Limit | Why |
|--------|-------|-----|
| Parallel Task calls | Single message only | True concurrency requires single emission |
| Prompts per sequential chain | No hard limit | Stop on failure; user controls scope |
| Commit message length | 72 chars max | Standard git convention |

**Parallel execution is all-or-nothing:** If you cannot fit all parallel Task calls in one message, fall back to sequential.

---

## Success Criteria

A prompt execution succeeds when:
- **Correct resolution**: Prompt identified by number/name/empty as intended
- **Strategy matched**: Single/parallel/sequential matches prompt count and dependencies
- **Artifact archived**: Output moved to `.principled/prompts/completed/` after execution
- **Git committed**: Commit created with proper scope format (`feat:`, `fix:`, etc.)
- **Clean handoff**: Orchestrator receives structured results, not raw output

---

## Reference Index

IF executing a prompt → BEFORE running read `references/execute-prompt.md`. Do not bypass the workflow steps in this file.
**Self-contained:** This skill does not reference other skills by name or invocation pattern.
