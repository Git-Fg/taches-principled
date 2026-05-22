---
name: add-task
description: "Create a draft task file in .specs/tasks/draft/ from user intent — sets up folder structure, type classification, naming convention, and preserves original prompt"
argument-hint: "[task title or description] [dependencies:task-file.md]"
---

## Decision Router

IF user has a task to capture → create draft task file in `.specs/tasks/draft/`
IF user has multiple related tasks → create separate files for each
IF combining with refinement workflow → draft will be consumed by the refinement pipeline later
IF user provides no description → ask clarifying questions before creating

# Add Task

Creates a draft task specification file from user intent. Sets up the standardized folder structure, classifies the task type, generates a file name from an action-oriented title, and preserves the original user prompt exactly for downstream refinement. The draft is intentionally minimal — a container for future analysis, not the final specification.

## Core Principle

Capture intent exactly as stated. The draft preserves the original user prompt verbatim. Future stages enrich it with analysis, architecture, and verification.

## Process

### Phase 1: Ensure Directory Structure
1. Create task directories if missing: `.specs/tasks/{draft,todo,in-progress,done}/` and `.specs/scratchpad/`
2. Add `.specs/scratchpad/` to `.gitignore` if not already present
3. Verification: all required directories exist

### Phase 2: Analyze Input
1. Extract the core task objective from user input
2. Identify implied type using the classification table
3. Note any dependencies (task files this depends on — assume none if not provided)

| Type | Extension | Use When |
|------|-----------|----------|
| feature | `.feature.md` | New functionality or capability |
| bug | `.bug.md` | Something is broken or not working |
| refactor | `.refactor.md` | Code restructuring, no behavior change |
| test | `.test.md` | Adding or updating tests |
| docs | `.docs.md` | Documentation changes only |
| chore | `.chore.md` | Maintenance, dependency updates |
| ci | `.ci.md` | CI/CD configuration changes |

### Phase 3: Generate File Name
1. Create short name from title: lowercase, hyphenated, 3-5 words, no special characters
2. Form file name: `<short-name>.<type>.md`
3. Verify uniqueness across all status folders to avoid overwrites

### Phase 4: Create Task File

Write task file to `.specs/tasks/draft/<short-name>.<type>.md`:

```markdown
---
title: <action-oriented title>
depends_on: <list of dependency task files>
---

## Initial User Prompt

{EXACT user input as provided}

## Description

// Will be filled in future stages
```

Title must start with an action verb (Add, Fix, Update, Implement, Remove, Refactor). Only add `depends_on` if dependencies were explicitly provided.

## Output

```
Created task file: .specs/tasks/draft/<name>.<type>.md
Title: <action-oriented title>
Type: <feature|bug|refactor|test|docs|chore|ci>
Depends on: <list or "none">
```

## Design Decisions

### Separate draft and todo folders
Draft is for unrefined tasks; todo is for tasks ready to implement. The separation enforces refinement as a required step, preventing premature implementation of underspecified work. This follows the principle that specification quality precedes implementation.

### Type as file extension
The file extension encodes the task type directly, making it visible in file listings and grep searches without opening the file. This enables tooling to filter or group tasks by type.

### Relationship to development pipeline
Creates the input artifact for the refinement workflow. Draft tasks are enriched by the refinement workflow which adds analysis, architecture, decomposition, and verification sections before moving them to todo/.
