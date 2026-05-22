---
name: execute-prompts
description: "Executes prompts from .principled/prompts/ via delegated sub-tasks. Use when user says 'run prompts', 'execute prompts', or 'launch prompts'."
when_to_use: |
  Use when the user says "run prompts", "execute prompts", "launch the prompts", or "run my prompt file".
  Do NOT use for interactive debugging, single-file edits, or one-off questions that don't involve prompt files.
---

## Decision Router

IF executing a single prompt → Read `{baseDir}/workflows/execute-prompt.md` BEFORE starting
IF executing parallel prompts → Read `{baseDir}/workflows/execute-prompt.md` for parallel coordination rules
IF executing sequential prompts → Read `{baseDir}/workflows/execute-prompt.md` for sequential handoff rules

This skill is self-contained — no cross-skill routing needed.

---

## Core Principle

**Delegate execution to preserve orchestration capacity.** Sub-tasks execute in isolated contexts while the main conversation remains lean for iteration, error recovery, and coordination.

---

## Sections

- [Policy vs. Mechanism](#policy-vs-mechanism)
- [Execution Strategies](#execution-strategies)
- [Execution Mode Intake](#execution-mode-intake)
- [Argument Parsing](#argument-parsing)
- [File Resolution](#file-resolution)
- [Archival and Git Workflow](#archival-and-git-workflow)
- [Anti-Patterns](#anti-patterns)
- [Numeric Thresholds](#numeric-thresholds)

---

## Policy vs. Mechanism

**Policy** = which execution strategy to use (determined by prompt relationships)
**Mechanism** = how to parse, resolve, and execute (the operational method)

A task conflating policy and mechanism becomes rigid — it runs prompts instead of achieving outcomes. State the strategy based on prompt dependencies; keep the parsing logic separate.

### Strategy Selection

| Scenario | Strategy | Why |
|----------|----------|-----|
| One prompt specified | Single | No coordination needed |
| Multiple independent prompts | Parallel | Maximize throughput |
| Multiple dependent prompts | Sequential | Each must complete before next |

**Default:** When multiple prompts are specified without a flag, use sequential for safety. Dependencies are often implicit.

---

## Execution Strategies

### Single Execution

Use when: one prompt target, or user explicitly requests one-at-a-time.

**Mechanism:**
1. Read the complete prompt file
2. Delegate to a general-purpose subagent
3. Wait for completion
4. Archive to `.principled/prompts/completed/`
5. Commit work via git
6. Return results

### Parallel Execution

Use when: multiple prompts with no interdependencies.

**Critical constraint:** ALL subagent dispatches MUST occur in a SINGLE message. This is the mechanism that enables true parallelization — not batching, not async/await, but concurrent dispatch in one token emission.

**Mechanism:**
1. Read all prompt files
2. Track each prompt's execution as a distinct unit — resolution, dispatch, completion
3. Dispatch ALL subagents in one message
4. For parallel execution, track each subagent's completion independently to enable partial failure reporting
5. Wait for all completions
6. Archive all prompts
7. Commit all work
8. Return consolidated results

**Explorer Subagent Protocol:**
When executing multiple prompts in parallel, coordination through shared state:
1. Check `.principled/scratch/multi-agent-state.md` for any prior execution context
2. Write current execution batch info to scratchpad
3. Each subagent should have **Write tool access** to update scratchpad
4. After completion, read scratchpad for any cross-agent findings
5. Consolidate results before archival

### Sequential Execution

Use when: prompts have dependencies (output of one feeds into another).

**Mechanism:**
1. Read first prompt file
2. Dispatch subagent
3. Wait for completion
4. Track progression through the chain — each prompt's completion gates the next
5. Archive completed prompt
6. Repeat for each subsequent prompt
7. Commit all work
8. Return consolidated results

**Failure handling:** If any prompt fails, stop the chain and report. Do not continue with dependent prompts.

---

## Execution Mode Intake

**Pre-execution gate:** Before parsing arguments, determine execution mode when multiple prompts are involved.

### When to Ask

Ask the user about execution mode when:
- Multiple prompts are specified
- User asks to "run" or "execute" prompts (not "step through" or "confirm each")

**Skip this gate when:**
- User explicitly said "step through" or "confirm before each"
- Single prompt only
- User specified `--parallel` or `--sequential` flag directly

### The Question

```
Question: How would you like to execute these prompts?

Options:
- A: Fully autonomous (recommended) — Execute all prompts without stopping
- B: Step through one at a time — Confirm before each prompt executes
- C: Something else
```

**Default to A (autonomous)** when user says "run" without qualification.

**If user selects C:** Acknowledge and stop — ask what they'd like to do instead.

**If user selects B:** Set step-through mode, execute one prompt at a time with confirmation gates.

---

## Argument Parsing

The execution target is determined by `$ARGUMENTS`.

### Input Forms

| Input | Interpretation |
|-------|----------------|
| (empty) | Most recently created prompt |
| `"005"` | Prompt number 005 |
| `"user-auth"` | Filename containing "user-auth" |
| `"005 006 007"` | Multiple prompts (default: sequential) |
| `"005 006 007 --parallel"` | Multiple prompts, parallel |
| `"005 006 007 --sequential"` | Multiple prompts, sequential |

**Parsing rules:**
- Arguments that are not `--parallel` or `--sequential` are prompt identifiers
- Multiple prompts without a flag default to sequential (safety over speed)

---

## File Resolution

For each prompt identifier, resolve to a concrete file path.

### Resolution Method

| Identifier Type | Matching Method |
|----------------|-----------------|
| Empty or "last" | `ls -t .principled/prompts/*.md \| head -1` |
| Number (e.g., "5") | Zero-padded match: "5" matches "005-_.md" |
| Text (e.g., "auth") | Filename contains string anywhere |

### Resolution Outcomes

| Outcome | Action |
|---------|--------|
| Exactly one match | Use that file |
| Multiple matches | List candidates, ask user to choose |
| No match | Track as failed state, report error with available prompts listing |

**Always verify file exists before dispatch.** Assumed existence is a race condition.

---

## Archival and Git Workflow

After each prompt completes successfully, archive it and commit the resulting work.

### Archival

- Destination: `.principled/prompts/completed/`
- Preserve original filename
- Add completion metadata if desired

### Git Workflow

**Stage files explicitly:**
```bash
git add [file1] [file2]
```
Never `git add .` — stage only files you modified.

**Commit format:**
```
[type]: [specific description]
```

| Change Type | Commit Type |
|-------------|-------------|
| New feature | `feat:` |
| Bug fix | `fix:` |
| Refactor | `refactor:` |
| Style/format | `style:` |
| Documentation | `docs:` |
| Tests | `test:` |
| Maintenance | `chore:` |

---

## Execution Gotchas

### Thought/Action/Observation Anti-Pattern

**The Problem:**
When Claude sees code blocks with `Thought:`, `Action:`, `Observation:` patterns, it interprets them as output templates to mimic, not as instructions to execute. Instead of calling Write() tool, it generates text that says "Thought: Let me analyze... Action: Write(...)".

**Why This Happens:**
1. Code blocks look like output format — Claude thinks "this is what my response should look like"
2. Pattern mimicking — The agent copies the structure as text instead of executing
3. Pseudo-code confusion — `Action: Write(...)` looks like code to output, not a command to run

**The Fix:**
Replace all Thought/Action/Observation examples with imperative natural language:
- Instead of: "Thought: I need to read the prompt file..."
- Write: "First, use the Read tool to load the prompt file."

---

## Anti-Patterns

### Parallelization Without True Concurrency

**Anti-pattern:** Spawning subagents across multiple messages for "parallel" execution.

**Why it fails:** Sequential token emission creates sequential execution. The illusion of parallelization with sequential latency.

**Fix:** All parallel subagent dispatches MUST be in a single message.

### Ignoring Dependencies in Sequential

**Anti-pattern:** Running prompts in sequence without checking if they have actual dependencies.

**Why it fails:** Wastes time on independent prompts; misses parallelization opportunity.

**Fix:** Explicitly ask user if prompts are dependent, or default to parallel when unsure.

### Archiving Before Completion

**Anti-pattern:** Archiving prompts before execution finishes.

**Why it fails:** Failed prompts remain in the queue instead of being flagged.

**Fix:** Archive only after confirmed completion. On failure, keep in place and report error.

---

## Numeric Thresholds

| Metric | Limit | Why |
|--------|-------|-----|
| Parallel Task calls | Single message only | True concurrency requires single emission |
| Prompts per sequential chain | No hard limit | Stop on failure; user controls scope |
| Commit message length | 72 chars max | Standard git convention |

**Parallel execution is all-or-nothing:** If you cannot fit all parallel Task calls in one message, fall back to sequential. Batched "parallel" is sequential with added latency.

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

**Workflows:** `{baseDir}/workflows/execute-prompt.md`
**Self-contained:** This skill does not reference other skills by name or invocation pattern.