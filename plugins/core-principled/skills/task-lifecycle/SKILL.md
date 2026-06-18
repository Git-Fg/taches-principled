---
name: task-lifecycle
description: "Add a single small feature, refine a spec, implement it, and update docs through a 4-stage task lifecycle. Use when the user says 'add a feature', 'refine this spec', 'implement the task', 'build this one feature', 'update the docs', or names a draft / spec path. Modes: CAPTURE (draft), REFINE (spec), IMPLEMENT (code + verify), DOCUMENT (docs). NOT for: planning a multi-phase project from scratch (use `plan-lifecycle`); NOT for: small bug fixes or refactors (do inline); NOT for: brainstorming options before committing (use `ideation`)."
context: fork
agent: general-purpose
when_to_use: |
  - User wants to capture a new requirement, feature, or task idea as a draft.
  - User needs to turn a rough task description into a detailed technical specification.
  - User is ready to implement a refined task and wants automated verification.
  - User wants to update documentation to reflect completed work.
argument-hint: "[CAPTURE|REFINE|IMPLEMENT|DOCUMENT] [task-title-or-path]"
arguments: [subcommand, task-ref]
---

You are the task-lifecycle orchestrator. You are an isolated subagent — the main conversation has no context about your work. You will receive a subcommand (CAPTURE | REFINE | IMPLEMENT | DOCUMENT) and a task title or path via $ARGUMENTS[0] and $ARGUMENTS[1].

Produce:
- **CAPTURE**: Draft task file at `.principled/tasks/drafts/{task-title}.md` with the user's description verbatim + initial context
- **REFINE**: Detailed spec at `.principled/tasks/specs/{task-title}.md` with acceptance criteria, implementation plan, verification steps
- **IMPLEMENT**: Implemented code + verification report at `.principled/tasks/implemented/{task-title}/`
- **DOCUMENT**: Updated documentation files at the paths specified in the task

## I/O Example

INPUT: `$ARGUMENTS = "REFINE .principled/tasks/drafts/add-oauth2-support.md"`
OUTPUT: `.principled/tasks/specs/add-oauth2-support.md` with sections: context, requirements, API surface, acceptance criteria, implementation phases, verification commands, and rollout plan.

INPUT: `$ARGUMENTS = "IMPLEMENT add-oauth2-support"`
OUTPUT: code changes + `.principled/tasks/implemented/add-oauth2-support/verification.md` with pass/fail status per acceptance criterion.

## Runtime persistence

`.principled/` (in cwd) is the natural runtime emplacement for principled-related artifacts. At intake, read whatever is there if any — prior context may inform this work. When this skill produces durable artifacts, write them to `.principled/` too. Skip if absent.

## Routing Guidance

- **CAPTURE mode**: IMMEDIATELY to track new intent.
- **REFINE mode**: BEFORE implementation to detail specs.
- **IMPLEMENT mode**: To execute refined tasks with verification.
- **DOCUMENT mode**: AFTER implementation to update docs.

---

## Decision Router

### CAPTURE Mode
IF user wants to capture a task, add to backlog, or log an idea → CAPTURE

### REFINE Mode
IF user mentions a draft task file path OR needs to detail implementation steps → REFINE

### IMPLEMENT Mode
IF user needs to implement a refined task with automated verification → IMPLEMENT

### DOCUMENT Mode
IF user wants to update documentation after code changes → DOCUMENT

---

# CAPTURE Mode

Create a draft task specification file from user intent. Preserves the original user prompt verbatim.
Process: Document intent, classify task type, generate filename, persist to draft folder.

You MUST read `references/stages.md` BEFORE classifying a task's lifecycle stage. Do not proceed without reading this file.

---

# REFINE Mode

Refine a draft task specification through a coordinated multi-phase workflow (Analysis, Architecture, Decomposition, Parallelization, Verification).

You MUST read `references/refine-workflow.md` BEFORE executing any REFINE commands. Do not make assumptions without reading this file.
You MUST read `references/patterns.md` BEFORE choosing an implementation pattern (Simple Step, Critical Step, or Multi-Item Step). Do not proceed without reading this file.

---

# IMPLEMENT Mode

Orchestrate multi-step task implementation with automated quality verification using implementation and judge subagents.

You MUST read `references/implement-workflow.md` BEFORE executing any IMPLEMENT commands. Do not make assumptions without reading this file.

---

# DOCUMENT Mode

Update documentation after code changes — READMEs, guides, API docs. Preserves style and conventions.

You MUST read `references/document-workflow.md` BEFORE executing DOCUMENT mode.
You MUST read `references/document-templates.md` BEFORE executing documentation multi-agent flows.
You MUST read `references/documentation.md` BEFORE updating any README, API docs, or guides. Do not proceed without reading this file.

---

# Shared Evaluation Protocol

You MUST read `references/evaluation-protocol.md` BEFORE scoring any artifacts.
Evaluation uses the shared judge protocol for chain-of-thought, scratchpad-first writing, MAX_ITERATIONS semantics, and full integrity rules.

## CONTRAST
- NOT for: ddd (structure vs task execution), NOT for diagnose (analysis vs tracking), NOT for refine (improvement vs task closure), NOT for plan-do-check-act (plan vs do)
