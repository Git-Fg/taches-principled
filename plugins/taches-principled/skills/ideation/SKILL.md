---
name: ideation
description: "Refine rough ideas or generate creative options with probability sampling. Two modes: refinement and divergent generation."
when_to_use: |
  Use when the user says "I have an idea", "help me figure out", "design this", "what are my options", "let's brainstorm", "help me think through this", or "let's think about".
  IMMEDIATELY when a concept is vague or unformed — BEFORE sketching architecture or writing code.
argument-hint: "[feature concept, problem, or topic]"
---

## Decision Router

IF user wants to explore or refine an unformed idea → use brainstorm mode: collaborative questioning to refine
IF user wants creative idea generation (not refinement) → use **create-ideas** mode
IF user has simple task capture needs → use add-task instead
IF user needs formal planning with milestones → use create-plans instead
IF user already knows exactly what they want → skip to design capture directly
IF combining with development workflow → produce `.specs/plans/<topic>.design.md` then create task file
IF user needs structured evaluation rather than generation → use evaluation workflow instead
IF idea is fully formed and documented → no need for this skill

---

## DO NOT Boundaries

- **DO NOT use for simple task capture** — use `add-task` instead for straightforward task creation
- **DO NOT use for formal planning** — use `create-plans` instead for structured planning with milestones and phases

## CONTRAST

- CONTRAST with add-task: ideation explores and refines ideas through dialogue; add-task captures task intent for later refinement. Use ideation when the idea is vague; use add-task when intent is clear.
- CONTRAST with create-plans: ideation explores what to build and why; create-plans decomposes what to build into executable tasks. Use ideation at concept stage; use create-plans at decision stage.

---

## What This Skill Changes

**Default behavior:** Claude treats "design this" as design-capture — it asks for requirements and jumps to a solution. "Brainstorm" requests get flattened to a list rather than explored through dialogue.

**With this skill:** Idea exploration is preceded by constraint elicitation. "Design this" requests trigger collaborative dialogue before any solution generation. create-ideas mode generates 6 probability-weighted options (3 anchors, 3 tail) rather than 1-2 variations.

**Why probability sampling:** High-probability anchors cover the obvious solutions. Low-probability tail explorations prevent premature convergence on the first plausible option. Without both, brainstorming produces safe consensus, not creative options.

---

## Execution Mode

**Default: subagent delegation.** For creative idea generation, spawn parallel subagents. The main agent synthesizes results — it never generates ideas inline.

**Spawn pattern for create-ideas mode:**
- ALWAYS spawn 3 **high-probability anchor** subagents for convergent exploration (>0.80 probability)
- ALWAYS spawn 3 **diverse tail** subagents for divergent exploration (<0.10 probability)
- ALWAYS aggregate findings inline after all 6 complete
- Scope: the topic, the generative brief, constraints from brainstorm mode (if any)
- Output: `.specs/plans/<topic>.design.md`

**Spawn pattern for brainstorm mode:**
- Main agent runs collaborative dialogue directly
- Spawn explorer subagent only when codebase research is needed to validate constraints

# Brainstorm Mode

Collaborative dialogue that turns rough ideas into documented designs. Operates before implementation planning.

## Core Principle

Designs emerge through exploration, not dictation. Single questions answered one at a time build clarity without overwhelming the participant.

### Brainstorm Process Principle

Explore the idea with single questions focusing on purpose, constraints, and success criteria. Generate 6 approaches with trade-offs (3 high-probability anchors, 3 diverse tail explorations). Present the design section by section, confirming each before proceeding.

Output: Validated design written to `.specs/plans/<topic>.design.md`, committed to git.

## Design Decisions

### One question at a time
Multiple questions overwhelm and cause topic abandonment.

### Probability-based exploration
High-probability options establish the expected path; low-probability options prevent premature convergence.

### Section-by-section validation
Incremental validation catches misunderstandings early.

# Create Ideas Mode

Generate 6 distinct responses for a given topic: 3 high-probability anchors (>0.80) representing central solutions, and 3 diverse tail explorations (<0.10) exploring different solution regions. Responses must be genuinely distinct.

## Failure Signal

```json
{"status": "failed", "reason": "no-viable-options|user-abandoned|scope-too-broad", "completed_portion": "...", "retry_possible": true|false}
```
