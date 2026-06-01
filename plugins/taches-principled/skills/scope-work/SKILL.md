---
name: scope-work
description: "Infer work scale from input and route to appropriate workflow. Capture tasks, refine specs, or plan projects based on what the user needs."
when_to_use: "Use when user asks to capture a task, log an item, refine a spec, or outline a broad project roadmap."
---

## Routing Guidance

- IMMEDIATELY when the user expresses intent that should be tracked, refined, or planned.
- CONTRAST with diagnose: scope-work handles task lifecycle (capture → refine → plan); diagnose handles problem investigation (root cause tracing, error analysis).

## Execution Protocol

**1. State Assessment:** Before taking any action, infer the project's current state and work scale from the input.

- Scan input: Is it a one-liner (bug, hotfix), a feature description (refactor, capability), or a project goal (multi-phase)?
- Check for existing artifacts in `.specs/tasks/` and `.principled/plans/`
- Map implicit history via git status and existing summaries

**2. Goal Alignment:** Based on your assessment, align the user's request with the appropriate workflow scale.

---

## Domain Router

Infer work scale from input characteristics:

**Nano-Spec** → One-liner, bug fix, hotfix. User wants to capture and go.
- Input: single sentence, file path, error message
- Trigger phrases: "capture this task", "add to my backlog", "create a task", "log this"
- Route to: nano-spec spoke

**Task-Spec** → Feature, refactor, capability. User wants structured analysis before implementation.
- Input: multi-sentence description, explicit refinement ask
- Trigger phrases: "refine this task", "turn this into a spec", "detail the steps"
- Route to: task-spec spoke

**Roadmap** → Project-level goal, multi-phase initiative.
- Input: broad scope, multiple components, "phases", "milestones"
- Trigger phrases: "make a plan", "plan this out", "sketch a roadmap", "break down this project"
- Route to: roadmap spoke

**Ambiguous** → Input spans multiple scales or is unclear:
- Ask one clarifying question: "Is this a quick task capture, a task to refine, or a full project plan?"
- Do not proceed until scale is clear.

**Negative cases** (what should NOT trigger scope-work):
- "run tests", "fix the bug", "debug this" → diagnose instead
- "review this code" → refine REVIEW instead
- "scan for vulnerabilities" → security instead
- "execute the plan" → execute-plans instead

---

## Success Invariants

Regardless of inferred work scale, these always hold:

1. **Input intent is captured verbatim** — what the user asked for is preserved
2. **Output format matches inferred scale** — nano/task/roadmap each have distinct outputs
3. **Templates load lazily** — spokes load only when their scale is inferred
4. **Contextual Handoff** — subagent spawns use Mission + Boundary + Mandate pattern

---

## Spoke Delegation

Load spokes lazily based on inferred scale:

```
IF Nano-Spec inferred → load {baseDir}/references/nano-spec.md
IF Task-Spec inferred → load {baseDir}/references/task-spec.md
IF Roadmap inferred → load {baseDir}/references/roadmap.md
```

---

## DO NOT Boundaries

- **DO NOT use for problem investigation** — "find the bug", "trace root cause" → diagnose
- **DO NOT use for code review** — "review this" → refine REVIEW
- **DO NOT use for execution** — "run the plan", "build it" → execute-plans
- **DO NOT use for security scanning** — "scan for vulnerabilities" → security
