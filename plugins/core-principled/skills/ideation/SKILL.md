---
name: ideation
description: "Explore a vague idea or generate creative alternatives before committing to an approach. Use when the user wants to 'think through', 'explore possibilities', or 'generate ideas' for an unformed problem."
when_to_use: |
  - User wants to refine a vague idea through collaborative dialogue.
  - User needs a list of creative alternatives or diverse approaches to a problem.
  - Use for early-stage conceptualization before architecture or implementation begins.
argument-hint: "[feature concept, problem, or topic]"
---

## Routing Guidance

- IMMEDIATELY when a concept is vague or unformed — BEFORE sketching architecture or writing code.

## Decision Router

IF user wants to explore or refine an unformed idea → use brainstorm mode: collaborative questioning to refine
IF user wants creative idea generation (not refinement) → use **create-ideas** mode
IF user has simple task capture needs → use task-lifecycle CAPTURE mode instead
IF user needs formal planning with milestones → use plan-lifecycle PLAN mode instead
IF user already knows exactly what they want → skip to design capture directly
IF combining with development workflow → produce `.principled/specs/plans/<topic>.design.md` then create task file
IF user needs structured evaluation rather than generation → use evaluation workflow instead
IF idea is fully formed and documented → no need for this skill

---

## DO NOT Boundaries

- **DO NOT use for simple task capture** — use `task-lifecycle` CAPTURE mode instead for task capture
- **DO NOT use for formal planning** — use `plan-lifecycle PLAN mode` instead for project planning

## CONTRAST

- CONTRAST with task-lifecycle CAPTURE: ideation explores and refines ideas through dialogue; task-lifecycle CAPTURE mode captures clear intent as a draft. Use ideation when the idea is vague; use task-lifecycle CAPTURE when intent is clear.
- CONTRAST with plan-lifecycle PLAN mode: ideation explores ideas; plan-lifecycle PLAN mode decomposes a project into phases and tasks. Use ideation when the concept needs exploration; use plan-lifecycle PLAN mode when scope is clear and decomposition is needed.

---

## What This Skill Changes

**Default behavior:** Claude treats "design this" as design-capture — it asks for requirements and jumps to a solution. "Brainstorm" requests get flattened to a list rather than explored through dialogue.

**With this skill:** Idea exploration is preceded by constraint elicitation. "Design this" requests trigger collaborative dialogue before any solution generation. create-ideas mode generates 6 probability-weighted options (3 anchors, 3 tail) rather than 1-2 variations.

**Why probability sampling:** High-probability anchors cover the obvious solutions. Low-probability tail explorations prevent premature convergence on the first plausible option. Without both, brainstorming produces safe consensus, not creative options.

---

## Execution Mode

**Default: subagent delegation.** For creative idea generation, spawn parallel subagents. The main agent synthesizes results — it never generates ideas inline.

**Spawn pattern for create-ideas mode:**
- ALWAYS spawn 3 **`tp-ideation-anchor`** subagents for convergent exploration (high-probability)
- ALWAYS spawn 3 **`tp-ideation-tail`** subagents for divergent exploration (low-probability)
- ALWAYS aggregate findings inline after all 6 complete
- Scope: the topic, the generative brief, constraints from brainstorm mode (if any)
- Output: `.principled/specs/plans/<topic>.design.md`

**Spawn pattern for brainstorm mode:**
- Main agent runs collaborative dialogue directly
- Spawn **`tp-explorer`** subagent only when codebase research is needed to validate constraints

# Brainstorm Mode

Collaborative dialogue that turns rough ideas into documented designs. Operates before implementation planning.

## Core Principle

Designs emerge through exploration, not dictation. Single questions answered one at a time build clarity without overwhelming the participant.

### Brainstorm Process Principle

Explore the idea with single questions focusing on purpose, constraints, and success criteria. Generate 6 approaches with trade-offs (using 3 **`tp-ideation-anchor`** and 3 **`tp-ideation-tail`** agents). Present the design section by section, confirming each before proceeding.

Output: Validated design written to `.principled/specs/plans/<topic>.design.md`, committed to git.

## Design Decisions

### One question at a time
Multiple questions overwhelm and cause topic abandonment.

### Probability-based exploration
High-probability options establish the expected path; low-probability options prevent premature convergence.

### Section-by-section validation
Incremental validation catches misunderstandings early.

# Create Ideas Mode

Generate 6 distinct responses for a given topic.

- **Anchor subagents:** Spawn 3 `tp-ideation-anchor` subagents for high-probability central solutions.
- **Tail subagents:** Spawn 3 `tp-ideation-tail` subagents for low-probability distinct regions.
- **Synthesis:** Do not merge or average — present 6 distinct ranked options to the user.
- **Ranked presentation:** Order options by combined anchor/tail interest; do not flatten diversity.
- **Output:** Write ranked design to `.principled/specs/plans/<topic>.design.md` and commit to git.

## Failure Signal

```json
{"status": "failed", "reason": "no-viable-options|user-abandoned|scope-too-broad", "completed_portion": "...", "retry_possible": true|false}
```

---

## CONTRAST

- NOT for: structured agent-driven development — use sadd
- NOT for: first-principles reasoning — use fpf
- NOT for: code quality improvement — use refine
- NOT for: root cause diagnosis — use diagnose
- NOT for: design constraint decisions — use kaizen

## Reference Index

IF performing convergent ideation (high-probability) → spawn **`tp-ideation-anchor`**
IF performing divergent ideation (low-probability) → spawn **`tp-ideation-tail`**
IF performing codebase research for constraints → spawn **`tp-explorer`**
