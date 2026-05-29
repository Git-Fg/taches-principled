---
name: add-task
description: "Create draft task files from user intent. Use when capturing tasks, adding to backlog, or logging things to do later."
when_to_use: |
  Use when the user says "capture this task", "create a task", "add to my backlog", or "log this as something to do".
  IMMEDIATELY when the user expresses intent that should be tracked, refined, and implemented later.
  CONTRAST with refine-task: add-task captures raw intent as a draft; refine-task adds analysis, architecture, and verification rubrics. Use add-task to capture; use refine-task to specify.
  CONTRAST with create-plans: add-task creates lightweight task files for the task lifecycle; create-plans creates project-level plans with milestones. Use add-task for feature/bug/refactor tasks; use create-plans for project decomposition.
argument-hint: "[task title or description] [dependencies:task-file.md]"
---

## What This Skill Changes

**Default behavior:** Task intent is lost in conversation or captured in a bloated CLAUDE.md. Unrefined ideas get implemented on first pass without structured analysis, architecture, or verification criteria.

**With this skill:** Task intent is captured verbatim in a typed draft file (`.specs/tasks/draft/`) with type encoded in the filename extension. The draft is a required first step before refinement — refinement cannot run without a draft. This enforces a pipeline that separates capture from specification.

**Why the pipeline matters:** Capturing intent and specifying implementation are different cognitive modes. Mixing them produces underspecified implementations and scope creep. The draft/todo separation enforces this separation as a structural constraint, not a memory rule.

---

## Decision Router

IF user has a task to capture → create draft task file in `.specs/tasks/draft/`
IF user has multiple related tasks → create separate files for each
IF combining with refinement workflow → draft will be consumed by `refine-task`; do not add structure here, let refinement add it
IF user provides no description → ask clarifying questions before creating

# Add Task

Creates a draft task specification file from user intent. Sets up the standardized folder structure, classifies the task type, generates a file name from an action-oriented title, and preserves the original user prompt exactly for downstream refinement.

## Core Principle

Capture intent exactly as stated. The draft preserves the original user prompt verbatim. Future stages enrich it with analysis, architecture, and verification.

## Process Principle

Document intent, verify directory structure exists, classify task type, generate filename, persist to draft folder. Title must start with an action verb (Add, Fix, Update, Implement, Remove, Refactor).

### Task Type Classification

| Type | Extension | Use When |
|------|-----------|----------|
| feature | `.feature.md` | New functionality or capability |
| bug | `.bug.md` | Something is broken or not working |
| refactor | `.refactor.md` | Code restructuring, no behavior change |
| test | `.test.md` | Adding or updating tests |
| docs | `.docs.md` | Documentation changes only |
| chore | `.chore.md` | Maintenance, dependency updates |
| ci | `.ci.md` | CI/CD configuration changes |

## Output

```
Created task file: .specs/tasks/draft/<name>.<type>.md
Title: <action-oriented title>
Type: <feature|bug|refactor|test|docs|chore|ci>
Depends on: <list or "none">
```

## Design Decisions

### Separate draft and todo folders
Draft is for unrefined tasks; todo is for tasks ready to implement. The separation enforces refinement as a required step.

### Type as file extension
The file extension encodes the task type directly, making it visible in file listings and grep searches without opening the file.
