---
name: ideation
description: "Explore a vague idea or generate creative alternatives before committing to an approach. Use when the user says 'think through this', 'explore possibilities', 'generate ideas for X', 'brainstorm', 'what are the options', 'I'm not sure what to do yet'. Two modes: DIVERGE (single-question collaborative exploration) and CREATE-IDEAS (6 distinct approaches with trade-offs). NOT for: scoring competitive solutions (use `sadd` JUDGE); NOT for: first-principles reasoning on a hard decision (use `fpf`)."
when_to_use: |
  - User wants to refine a vague idea through collaborative dialogue.
  - User needs a list of creative alternatives or diverse approaches to a problem.
  - Use for early-stage conceptualization before architecture or implementation begins.
argument-hint: "[feature concept, problem, or topic]"
---

## Runtime persistence

`.principled/` (in cwd) is the natural runtime emplacement for principled-related artifacts. At intake, read whatever is there if any — prior context may inform this work. When this skill produces durable artifacts, write them to `.principled/` too. Skip if absent.

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

**Default: inline divergent generation.** Ideation benefits from diverse angles, but spawning 6 subagents to generate 6 ideas duplicates reasoning you can do in-context at lower cost. Generate the 6 approaches inline in this order: 3 high-probability central solutions, then 3 low-probability distinct regions. After generating, optionally spawn 2 `tp-critic` instances in parallel — one with lens "challenge these 3 anchor candidates for feasibility", one with lens "challenge these 3 tail candidates for feasibility" — for isolated-context stress tests.

**Process for create-ideas mode:**
- Generate 3 high-probability central solutions inline (anchor candidates)
- Generate 3 low-probability distinct solutions inline (tail candidates)
- Optionally spawn 2 `tp-critic` instances in parallel with the challenge lenses above
- Present all 6 ranked options to the user (do not merge or average)
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

Explore the idea with single questions focusing on purpose, constraints, and success criteria. Generate 6 approaches with trade-offs inline (3 high-probability anchors + 3 low-probability tails). Present the design section by section, confirming each before proceeding.

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

- **Anchor candidates:** 3 high-probability central solutions, generated inline (you are the anchor).
- **Tail candidates:** 3 low-probability distinct solutions, generated inline (you are the tail).
- **Stress test (optional):** spawn 2 `tp-critic` instances in parallel — "challenge these anchor candidates" + "challenge these tail candidates".
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

IF performing convergent ideation (high-probability) → generate inline (you are the anchor)
IF performing divergent ideation (low-probability) → generate inline (you are the tail)
IF performing codebase research for constraints → spawn **`tp-explorer`**
