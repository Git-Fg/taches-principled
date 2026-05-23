---
name: kaizen
description: Four design-time constraints for every code decision: incremental improvement, error-proof design (poka-yoke), standardized patterns, and YAGNI. Shapes implementation, refactoring, and architecture.
when_to_use: |
  Use when the user says "apply kaizen", "use the constraints", "design this properly", "check against principles", "apply YAGNI", "check for over-engineering", "what's the simplest approach", or "avoid speculation".
  IMMEDIATELY before writing code — these constraints apply to every decision.
  FIRST when tempted to add abstractions, speculate about future needs, or fix everything in one pass.
  DO NOT use when implementing trivial one-liners — use for architectural decisions, refactoring, and non-trivial implementation choices.
  CONTRAST with brainstorm/ideation: those explore WHAT to build; kaizen shapes HOW to build it.
  CONTRAST with plan-do-check-act: that tests changes; kaizen prevents bad patterns from entering the codebase.
argument-hint: Applied automatically when implementing, refactoring, designing, or handling errors
---

## Decision Router

IF implementing code, refactoring, making architecture decisions, or handling errors → apply all four kaizen pillars as design-time constraints
IF a problem is complex or has unclear causes → use a structured analysis method (tracing backward, asking why iteratively) before taking action
IF faced with "we might need this someday" requirements → apply JIT/YAGNI to cut speculation before it enters the codebase
IF the team introduces a new pattern without discussion → flag against Standardized Work and require team consensus
IF tempted to fix all quality issues in one pass → enforce Incremental Improvement: one change at a time, verify between each

# Kaizen

Continuous improvement applied as four design-time constraints on every code decision. Not a checklist to follow, but constraints that shape how code gets written, reviewed, and maintained.

## Core Principle

Small improvements continuously. Prevent errors at design time. Follow proven patterns. Build only what is needed now. These are not aspirations — they are quality gates applied at every decision point.

## The Four Pillars

### 1. Continuous Improvement — Incremental over revolutionary

The smallest change that improves quality, then verify, then repeat. Never try to fix everything in one pass.

- Make it work, then make it clear, then make it efficient — never all three at once
- Always leave code slightly better than you found it (fix small issues as you encounter them)
- One improvement per iteration, verified before the next
- Accept "better than before" even if not perfect — diminishing returns are real

**Red flag:** "I will refactor it later" without an immediate action. Either do it now or accept it as-is.

### 2. Poka-Yoke — Error proofing at design time

Design systems that make errors impossible or immediately visible, not systems that handle errors gracefully after they occur.

- Use the type system to make invalid states unrepresentable
- Validate at system boundaries once, use safely everywhere
- Fail fast and loudly with clear messages
- Validate before use, not after
- Required configuration over optional with defaults — fail at startup, not in production

**Layers, in order:** Type system (compile time) → Validation (runtime, early) → Guards (preconditions) → Error boundaries (graceful degradation)

**Red flag:** "Users should just be careful" or optional config with no validation.

### 3. Standardized Work — Follow established patterns

Consistency over cleverness. New patterns require team consensus. Documentation lives with code.

- Before introducing a new pattern, search the codebase for similar solved problems
- Match existing file structure, naming conventions, error handling, import locations
- Comments explain "why", not "what" — code explains itself
- Automate standards via linters, type checks, CI/CD gates
- When a new standard emerges, document it

**Red flag:** "I prefer to do it my way" without checking existing patterns.

### 4. Just-In-Time (JIT) — Build only what is needed now

YAGNI applied rigorously. No "just in case" features, no premature optimization, no speculative abstractions.

- Implement only current requirements — delete speculative code
- Wait for the Rule of Three (three similar cases) before abstracting
- Profile before optimizing, measure before and after
- Prefer duplication over the wrong abstraction
- Add complexity only when a current requirement demands it, not when you anticipate future needs

**Red flag:** "We might need this someday" without a concrete, imminent requirement.

## Output

This skill produces no standalone artifact. It applies as behavioral constraints during development — every implementation, refactoring, architecture decision, and error handling path is shaped by these four pillars.

## Design Decisions

### Four pillars, not a checklist
These are design-time constraints, not a post-hoc audit. The pillars guide decisions as they are made. A post-hoc audit is too late — the code is already written.

### No code examples here
The patterns these pillars enforce (making invalid states unrepresentable, validating at boundaries, following conventions) are widely documented. The skill states the constraint; the developer (Claude) knows how to apply it.

### Guardrail stance, not procedure
This skill does not define a workflow. It defines invariants that apply across all workflows. The structured analysis methods (tracing, Five Whys, Fishbone, PDCA, A3) are complementary tools invoked when these guardrails surface a problem worth analyzing in depth.
