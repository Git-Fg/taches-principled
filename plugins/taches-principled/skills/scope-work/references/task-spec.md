# Task-Spec: Full Task Refinement

For features, refactors, and capabilities requiring analysis, architecture, and verification before implementation.

## When to Use

This spoke loads when scope-work infers Task-Spec scale: a multi-sentence description with explicit refinement ask, or a draft task needing elaboration.

## Core Principle

Specification quality is a prerequisite for implementation speed. Analysis before writing code reduces rework.

## Process

The task-spec workflow has 7 phases. Each phase adds a distinct layer. Skip phases only when explicitly requested.

### Phase 1: Research
Gather relevant documentation, patterns, and prior art. Write findings to `.specs/scratchpad/<id>.md`.

### Phase 2: Analysis
Parallel analysis in three streams:
- **Codebase Impact**: Identify affected files, interfaces, integration points
- **Business Requirements**: Refine description, create acceptance criteria
- **Research Integration**: Synthesize findings from Phase 1

### Phase 3: Architecture
Synthesize research and analysis into architectural overview. Document decisions and trade-offs.

### Phase 4: Decomposition
Break into ordered implementation steps. Each step has: goal, expected output, success criteria, risks.

### Phase 5: Parallelization
Reorganize steps for maximum parallel execution. Identify dependency chains and parallel groups.

### Phase 6: Verification
Add evaluation rubrics for each step. Determine verification level:
- None: Simple operations (mkdir, delete)
- Single Judge: Non-critical artifacts
- Panel of 2: Critical artifacts (business logic, security)

### Phase 7: Promote
Move refined task from draft to todo:
```bash
git mv .specs/tasks/draft/<file>.md .specs/tasks/todo/
```

## Output

A refined task file at `.specs/tasks/todo/<name>.<type>.md` with:
- Description (refined from original)
- Architecture overview
- Implementation steps with verification rubrics
- Dependencies and parallelization

## Design Decisions

- **Parallel analysis first** — prevents designing without understanding constraints
- **Independent judges per phase** — objective quality signals
- **Scratchpad-first** — write findings to scratchpad before committing to task file
- **Verification as first-class** — every step has an explicit verification level
