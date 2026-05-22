---
name: subagent-driven-development
description: Execute implementation plans by dispatching fresh subagent per task with code review between tasks - use when implementing plans with multiple independent tasks or investigating 3+ unrelated issues
when_to_use: |
  Use when the user says "implement this plan", "execute plan", "dispatch per task",
  "subagent implementation", "run the tasks", or "execute these items".
  IMMEDIATELY when user provides a plan with multiple tasks to implement.
  FIRST when tasks are independent or sequential with code review between them.
argument-hint: Plan file path and execution mode (sequential/parallel)
---

## Decision Router

IF tasks are tightly coupled and must execute in order → sequential execution
IF tasks are independent (different files/subsystems/bugs) → parallel execution
IF sequential execution → dispatch one agent per task, review after each
IF parallel execution → dispatch agents in batches, review between batches
IF subagent fails → dispatch fix agent with specific instructions (do not fix manually)

# subagent-driven-development

Execute plans by dispatching fresh subagent per task, with code and output review after each or batch of tasks.

## Policy: Core Principle

Fresh subagent per task + review between tasks = high quality, fast iteration.

**Why fresh subagent per task:**
- No context pollution from previous work
- Each task gets full attention
- Code review catches issues early

**Why review between tasks:**
- Catch structural problems before they compound
- Apply feedback before next task amplifies issues
- Verify task requirements met

## Mechanism: Sequential Execution

### Step 1: Load Plan

Read plan file, create task list with TodoWrite.

### Step 2: Execute Task

For each task, dispatch implementation subagent:
```
Task tool (general-purpose):
  description: "Implement Task N: {task name}"
  prompt: |
    Read Task N from {plan-file} carefully.

    Your job:
    1. Implement exactly what the task specifies
    2. Write tests (follow TDD if task says to)
    3. Verify implementation works
    4. Commit your work
    5. Report back

    Work from: {directory}

    Report: What you implemented, tested, test results, files changed, any issues
```

### Step 3: Code Review

After each task, dispatch code-reviewer subagent:
```
Task tool (code-reviewer):
  WHAT_WAS_IMPLEMENTED: {from subagent's report}
  PLAN_OR_REQUIREMENTS: Task N from {plan-file}
  BASE_SHA: {commit before task}
  HEAD_SHA: {current commit}
  DESCRIPTION: {task summary}
```

**Code reviewer returns:** Strengths, Issues (Critical/Important/Minor), Assessment

### Step 4: Apply Feedback

- **Critical issues:** Fix immediately before proceeding
- **Important issues:** Fix before next task
- **Minor issues:** Note for later

If issues found, dispatch fix subagent with specific instructions. Do not fix manually (context pollution risk).

### Step 5: Continue

Mark task complete, move to next task, repeat Steps 2-4.

### Step 6: Final Review

After all tasks complete, dispatch final code-reviewer to:
- Review entire implementation
- Check all plan requirements met
- Validate overall architecture

### Step 7: Complete

Finalize the development branch: verify tests pass, present completion options to the user, and execute their choice.

## Mechanism: Parallel Execution

For independent tasks across different files/subsystems/bugs.

### Step 1: Load Plan

Read plan file, identify independent task groups.

### Step 2: Batch Execution

Default batch size: 3 tasks.

For each task:
- Mark in_progress
- Execute exactly as specified
- Run verifications as specified
- Mark completed

### Step 3: Report

When batch complete, show what was implemented, verification output, ask for feedback.

### Step 4: Continue

Based on feedback:
- Apply changes if needed
- Execute next batch
- Repeat until complete

### Step 5: Complete

After all batches are verified, finalize the development branch.

## Parallel Investigation Special Case

When multiple unrelated failures can be investigated without shared state.

### Step 1: Identify Independent Domains

Group failures by what's broken. Each domain is independent if fixing one doesn't affect tests for another.

### Step 2: Create Focused Agent Tasks

Each agent gets:
- **Specific scope:** One test file or subsystem
- **Clear goal:** Make these tests pass
- **Constraints:** Do not change other code
- **Expected output:** Summary of findings and fixes

### Step 3: Dispatch in Parallel

Launch agents concurrently for independent domains.

### Step 4: Review and Integrate

When agents return:
- Read each summary
- Verify fixes don't conflict
- Run full test suite
- Integrate all changes

## Red Flags

**Never:**
- Skip code review between tasks
- Proceed with unfixed Critical issues
- Dispatch multiple implementation agents in parallel (conflicts)
- Implement without reading plan task
- Fix manually after subagent failure

**Stop and ask when:**
- Blocker mid-batch (missing dependency, test fails, instruction unclear)
- Plan has critical gaps
- Verification fails repeatedly
- Instruction is unclear

## Verification

After agents return:
1. Review each summary - understand what changed
2. Check for conflicts - did agents edit same code?
3. Run full suite - verify all fixes work together
4. Spot check - agents can make systematic errors

## Key Principles

- Fresh subagent per task (no context pollution)
- Review between or after tasks (catch issues early)
- Fix through subagents (don't fix manually)
- Stop when blocked (don't guess)