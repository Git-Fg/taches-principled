---
name: execute-prompts
description: "Execute prompts from .principled/prompts/ via delegated sub-tasks. Use when user asks to run, execute, or launch prompts."
when_to_use: |
  Do NOT use for interactive debugging, single-file edits, or one-off questions that don't involve prompt files.
---

# Execute Prompts Skill

Execute prompts from `.principled/prompts/` as delegated sub-tasks with fresh context. Supports single, parallel, and sequential execution strategies.

## Core Principle

**Delegate execution to preserve orchestration capacity.** Sub-tasks execute in isolated contexts while the main conversation remains lean for iteration, error recovery, and coordination.

---

## Sections

- [Policy vs. Mechanism](#policy-vs-mechanism)
- [Execution Strategies](#execution-strategies)
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
2. Delegate via Task tool with `subagent_type="general-purpose"`
3. Wait for completion
4. Archive to `.principled/prompts/completed/`
5. Commit work via git
6. Return results

### Parallel Execution

Use when: multiple prompts with no interdependencies.

**Critical constraint:** ALL Task tool calls MUST occur in a SINGLE message. This is the mechanism that enables true parallelization — not batching, not async/await, but concurrent dispatch in one token emission.

**Mechanism:**
1. Read all prompt files
2. Dispatch ALL Task tools in one message
3. Wait for all completions
4. Archive all prompts
5. Commit all work
6. Return consolidated results

### Sequential Execution

Use when: prompts have dependencies (output of one feeds into another).

**Mechanism:**
1. Read first prompt file
2. Dispatch Task tool
3. Wait for completion
4. Archive completed prompt
5. Repeat for each subsequent prompt
6. Commit all work
7. Return consolidated results

**Failure handling:** If any prompt fails, stop the chain and report. Do not continue with dependent prompts.

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
| No match | Report error, list available prompts |

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

## Anti-Patterns

### Parallelization Without True Concurrency

**Anti-pattern:** Spawning Task tools across multiple messages for "parallel" execution.

**Why it fails:** Sequential token emission creates sequential execution. The illusion of parallelization with sequential latency.

**Fix:** All parallel Task calls MUST be in a single message.

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

## Reference Index

**Workflows:** `workflows/execute-prompt.md`
**Self-contained:** This skill does not reference other skills by name or invocation pattern.