# Roadmap: Multi-Phase Project Planning

For project-level goals, multi-phase initiatives, and broad-scope work requiring decomposition into executable plans.

## When to Use

This spoke loads when scope-work infers Roadmap scale: broad scope, multiple components, explicit "phases", "milestones", or multi-step decomposition ask.

## Core Principle

PLAN.md is the prompt. It is the instruction Claude follows directly — not a document to be transformed.

## Planning Hierarchy

```
BRIEF.md      → What you want (human vision)
    ↓
ROADMAP.md   → Phases to get there
    ↓
PLAN.md      → What Claude does right now
    ↓
SUMMARY.md   → What happened
```

## Process

### 1. Context Scan
Before planning:
- Check git status and project structure
- List existing artifacts in `.principled/plans/`
- Find any `.continue-here.md` files
- Write findings to `.principled/scratch/context-scan.md`

### 2. Intake
Gather just enough to plan confidently:
- What needs to be built
- Priorities and constraints
- What success looks like

### 3. Fan-Out Exploration
Use parallel subagents to explore project structure:
- 3-5 areas explored simultaneously
- All findings written to `.principled/scratch/{plan-id}-exploration.md`

### 4. Brief Creation
Document the vision in BRIEF.md:
- What and why
- Constraints and success criteria
- Scope boundaries

### 5. Roadmap Creation
Break into 2-3 task phases. Each phase = 2-3 tasks, ~15-60 min each.

### 6. Phase Plan Execution
Execute one phase at a time:
- Write phase PLAN.md (2-3 tasks)
- Execute via subagents with verification
- Create SUMMARY.md on completion
- Loop until roadmap done

## Success Invariants

1. **Plans are atomic** — 2-3 tasks per plan, no mega-plans
2. **Tasks are verifiable** — each has `verify:` command
3. **Context limits respected** — stop at 50% context, create handoff
4. **Autonomous deviation handling** — auto-fix bugs, log enhancements

## Design Decisions

- **Aggressive atomicity** — small plans are reliable plans
- **Token-conscious execution** — context degradation is invisible; split proactively
- **CLI-first** — if a tool exists for it, use it
- **No enterprise ceremonies** — no standups, no RACI, no multi-week estimates
