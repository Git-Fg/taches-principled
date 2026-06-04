---
name: task-lifecycle
description: "Track and build features from initial idea to implementation. Use when the user wants to add a new feature, add a task, refine an idea, build something, or turn a rough description into a detailed technical spec."
when_to_use: |
  - User wants to capture a new requirement, feature, or task idea as a draft.
  - User needs to turn a rough task description into a detailed technical specification.
  - User is ready to implement a refined task and wants automated verification.
  - User wants to update documentation to reflect completed work.
argument-hint: "[subcommand] [task-title-or-path] [--flags]"
---

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

---

# REFINE Mode

Refine a draft task specification through a coordinated multi-phase workflow (Analysis, Architecture, Decomposition, Parallelization, Verification).

You MUST read `references/refine-workflow.md` BEFORE executing any REFINE commands. Do not make assumptions without reading this file.

---

# IMPLEMENT Mode

Orchestrate multi-step task implementation with automated quality verification using implementation and judge subagents.

You MUST read `references/implement-workflow.md` BEFORE executing any IMPLEMENT commands. Do not make assumptions without reading this file.

---

# DOCUMENT Mode

Update documentation after code changes — READMEs, guides, API docs. Preserves style and conventions.

You MUST read `references/document-workflow.md` BEFORE executing DOCUMENT mode.
You MUST read `references/document-templates.md` BEFORE executing documentation multi-agent flows.

---

# Shared Evaluation Protocol

You MUST read `references/evaluation-protocol.md` BEFORE scoring any artifacts.
Evaluation uses the shared judge protocol for chain-of-thought, scratchpad-first writing, MAX_ITERATIONS semantics, and full integrity rules.

## CONTRAST
- NOT for: ddd (structure vs task execution), NOT for diagnose (analysis vs tracking), NOT for refine (improvement vs task closure), NOT for plan-do-check-act (plan vs do)
