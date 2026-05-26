---
name: ideation
description: "Refine rough ideas into documented designs through single-question dialogue, or generate 6 distinct creative options using probability sampling. Two modes: concept refinement and divergent generation."
when_to_use: |
  Use when the user says "I have an idea", "help me figure out", "design this", "what are my options", "let's brainstorm", "help me think through this", or "let's think about".
  IMMEDIATELY when a concept is vague or unformed — BEFORE sketching architecture or writing code.
argument-hint: "[feature concept, problem, or topic]"
---

## Decision Router

IF user wants to explore or refine an unformed idea → use brainstorm mode: collaborative questioning to refine
IF user wants creative idea generation (not refinement) → use create-ideas mode
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

# Brainstorm Mode

Collaborative dialogue that turns rough ideas into documented designs. Operates before implementation planning. Uses structured questioning to surface purpose, constraints, and success criteria, then incrementally validates a design section by section. One question per message builds clarity without overwhelming.

## Core Principle

Designs emerge through exploration, not dictation. Single questions answered one at a time build clarity without overwhelming the participant.

## Process

### Phase 1: Understand the Idea
1. Read current project context (files, docs, recent commits) for grounding
2. Ask one question per turn to refine the idea — prefer multiple choice when possible
3. Focus on: purpose, constraints, success criteria
4. Verification: can you state the core problem in one sentence?

### Phase 2: Explore Approaches
1. Generate 6 possible approaches with trade-offs: 3 high-probability (>0.80) as anchors, 3 diverse tail explorations (<0.10)
2. Present options with your recommendation and reasoning
3. Verification: do the approaches cover distinct solution regions (not minor variations of each other)?

### Phase 3: Present the Design
1. Break the design into sections of 200-300 words each
2. Present each section and confirm "does this look right?" before proceeding
3. Cover: architecture, components, data flow, error handling, testing
4. Be ready to revisit and clarify when something does not make sense
5. Verification: every section validated before the next begins

## Output

Validated design written to `.specs/plans/<topic>.design.md`, committed to git.

## Design Decisions

### One question at a time
Multiple questions overwhelm and cause topic abandonment. Single questions force prioritization and make it easy to say "no."

### Probability-based exploration
High-probability options establish the expected path; low-probability options prevent premature convergence. Sampling from both tails avoids confirmation bias.

### Section-by-section validation
Presenting the full design at once invites rubber-stamping. Incremental validation catches misunderstandings early.

### Relationship to development pipeline
Produces validated design specifications that feed into task creation and implementation planning. Operates at the earliest stage of the development lifecycle. When a design is validated, capture it as a draft task to track it through refinement and implementation.

# Create Ideas Mode

Generate 6 distinct responses for a given topic: 3 high-probability anchors (>0.80) representing central solutions, and 3 diverse tail explorations (<0.10) exploring different solution regions. Each response includes explanatory text and a numeric probability. Responses must be genuinely distinct from one another — no overlapping or minor-variation responses.
