---
name: brainstorm
description: Use when user says "brainstorm", "design", "think through", or "explore approaches" — before writing implementation plans. Refines rough ideas into fully-formed designs through collaborative questioning, alternative exploration, and incremental validation. Not for mechanical processes with clear paths.
argument-hint: Optional initial feature concept or topic to brainstorm
---

## Decision Router

IF user asks to brainstorm, design, or explore approaches → this skill
IF task is mechanical with a clear implementation path → DO NOT use this skill; proceed directly
IF user says "help me think through X" → this skill
IF user provides a complete spec and just wants implementation → DO NOT use this skill

# Refine Ideas Into Designs

Collaborative dialogue to transform rough ideas into fully-formed designs and specs.

## Process

**1. Understand the idea:**
- Check project state (files, docs, recent commits)
- Ask ONE question at a time — prefer multiple choice when possible
- Explore: purpose, constraints, success criteria

**2. Explore approaches:**
- Generate 6 diverse approaches with trade-offs
- Sample strategically:
  - First 3: high probability (>0.80)
  - Last 3: diverse alternatives (<0.10 each)
- Lead with recommendation, explain reasoning

**3. Present design incrementally:**
- Break into sections of 200-300 words
- Confirm each section before proceeding
- Cover: architecture, components, data flow, error handling, testing

## Key Principles

- **One question at a time** — avoid overwhelming with multiple questions
- **Multiple choice preferred** — easier to answer than open-ended
- **YAGNI ruthlessly** — remove unnecessary features
- **Explore alternatives** — propose 2-3 approaches before settling
- **Incremental validation** — present design in sections, validate each

## After Design

Write validated design to `.specs/plans/<topic>.design.md`. If continuing:
- Ask: "Ready to set up for implementation?"
- Use `/worktrees create` for isolated workspace
- Use `/add-task` to create task file for target approach