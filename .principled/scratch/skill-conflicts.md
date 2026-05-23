# Skill Ecosystem Conflicts

## Contradictions Found

### 1. `create-plans` vs `plan-task` — Different mechanisms, same trigger intent

**File:** `plugins/taches-principled/skills/create-plans/SKILL.md`
**File:** `plugins/tp-sdd/skills/plan-task/SKILL.md`

Both skills handle "planning" but with incompatible structures:

| Aspect | create-plans | plan-task (tp-sdd) |
|--------|--------------|-------------------|
| Directory | `.principled/plans/` | `.specs/tasks/` |
| Output | BRIEF.md, ROADMAP.md, PLAN.md | Task files in draft/todo/in-progress |
| Trigger | "make a plan", "plan this out", "sketch a roadmap" | "plan this", "break this down", "refine this task" |
| Default threshold | N/A | 3.5/5.0 |

**Contradiction:** A user who says "plan this out" could route to either skill depending on plugin load order, producing completely different artifacts and workflows.

---

### 2. `analyse-problem` vs `root-cause-analysis` — Ambiguous boundaries

**File:** `plugins/taches-principled/skills/analyse-problem/SKILL.md:4-7`
**File:** `plugins/taches-principled/skills/root-cause-analysis/SKILL.md:4-6`

Both skills claim to do root cause analysis but with different methods:

- `analyse-problem`: A3 format, Five Whys or Fishbone, structured documentation
- `root-cause-analysis`: Five Whys and Fishbone directly

**Contradiction:**
```
analyse-problem when_to_use: "Do NOT use for ongoing issues without a specific incident (use root-cause-analysis)"
root-cause-analysis when_to_use: No such exclusion
```

The boundary between "specific incident" (analyse-problem) and "ongoing issue" (root-cause-analysis) is unclear and may cause routing confusion.

---

### 3. `code-review` vs `reflexion` — Overlapping quality verification

**File:** `plugins/taches-principled/skills/code-review/SKILL.md:4-8`
**File:** `plugins/taches-principled/skills/reflexion/SKILL.md:4-8`

Both skills do quality verification after work is done:

- `code-review`: "review this PR", "check my changes", "review the code"
- `reflexion`: "reflect on this", "review my work", "critique this"

**Contradiction:**
```
code-review Do NOT: "when work was already completed and needs reflection (use reflexion)"
reflexion Do NOT: No such exclusion
```

This suggests reflexion is for completed work, but code-review also says "before merging" which implies completion. The boundary is unclear.

---

### 4. `create-prompts` + `execute-prompts` — Broken compositional pair

**File:** `plugins/taches-principled/skills/create-prompts/SKILL.md:484-486`
```
**Self-contained:** This skill produces prompts as standalone artifacts. Prompts created by this skill flow to a companion execution skill as a compositional pair.
```

**File:** `plugins/taches-principled/skills/execute-prompts/SKILL.md:281-283`
```
**Self-contained:** This skill does not reference other skills by name or invocation pattern.
```

**Issue:** create-prompts claims a compositional pair exists, but execute-prompts explicitly refuses to acknowledge the relationship. The execution flow is one-directional and undocumented on the receiving end.

---

## Duplicate Overlaps

### 1. `implement-task` (taches-principled) vs `implement-task` (tp-sdd) — Identical name, identical triggers, different implementations

**File:** `plugins/taches-principled/skills/implement-task/SKILL.md`
**File:** `plugins/tp-sdd/skills/implement-task/SKILL.md`

Both have:
- Same skill name: `implement-task`
- Same trigger phrases: "implement this task", "build this", "start working on the task"
- Same directory structure: `.specs/tasks/{todo,in-progress,done}/`
- Same default thresholds: 4.0/4.5

**Duplicate overlap:** Two skills with identical names and triggers that do the same thing. Claude routing may pick either based on load order, producing unpredictable behavior.

---

### 2. `plan-task` (taches-principled) vs `plan-task` (tp-sdd) — Identical structure, different plugins

**File:** `plugins/taches-principled/skills/plan-task/SKILL.md`
**File:** `plugins/tp-sdd/skills/plan-task/SKILL.md`

Both have:
- Same skill name: `plan-task`
- Similar triggers: "refine this task" vs "plan this", "break this down"
- Same directory structure: `.specs/tasks/draft/` → `todo/`
- Same phases: research, codebase analysis, business analysis, architecture synthesis, decomposition, parallelize, verifications
- Same default threshold: 3.5/5.0

**Duplicate overlap:** Nearly identical skills in different plugins with no meaningful differentiation.

---

### 3. `ideation` vs `create-ideas` — Circular referral

**File:** `plugins/taches-principled/skills/ideation/SKILL.md:5-6`
```
Do NOT use when the user wants pure enumeration of ideas without refinement or collaborative shaping — use create-ideas instead.
```

**File:** `plugins/tp-sdd/skills/create-ideas/SKILL.md:5-6`
```
Do NOT use for collaborative refinement of a single idea — use ideation instead.
```

Both skills explicitly refer users to each other but are actually in the SAME plugin ecosystem. A user who says "help me brainstorm" could get either skill depending on which is loaded first.

---

### 4. `add-task` (taches-principled) vs `add-task` (tp-sdd) — Near identical

**File:** `plugins/taches-principled/skills/add-task/SKILL.md`
**File:** `plugins/tp-sdd/skills/add-task/SKILL.md`

Both:
- Use `.specs/tasks/draft/` directory
- Same type classification table (feature, bug, refactor, test, docs, chore, ci)
- Same filename format: `<short-name>.<type>.md`

**Duplicate overlap:** Functionally identical skills.

---

### 5. `launch-subagent` vs `sadd-dispatch` vs `create-subagents` — Subagent spawning confusion

**File:** `plugins/tp-sadd/skills/launch-subagent/SKILL.md`
**File:** `plugins/tp-sadd/skills/sadd-dispatch/SKILL.md`
**File:** `plugins/taches-principled/skills/create-subagents/SKILL.md`

Three skills for subagent spawning with overlapping triggers:

| Skill | Trigger keywords |
|-------|-----------------|
| launch-subagent | "launch subagent", "dispatch agent", "delegate to agent" |
| sadd-dispatch | "dispatch subagent", "launch agent for task", "delegate this" |
| create-subagents | "create an agent", "spawn a subagent", "make me an agent" |

All three could route from "delegate this work" depending on plugin load order.

---

## Conflicting Guidance

### 1. `sadd-patterns` vs `sadd-dispatch` — When to use multi-agent

**File:** `plugins/tp-sadd/skills/sadd-patterns/SKILL.md:11-15`
```
IF single-agent context limits are not being hit → do NOT add multi-agent complexity
```

**File:** `plugins/tp-sadd/skills/sadd-dispatch/SKILL.md:15`
```
IF the task is trivial (single file, mechanical change) → use Haiku without specialized agent
```

**Conflict:** sadd-patterns says "don't add multi-agent if single-agent suffices", but sadd-dispatch doesn't clearly integrate this constraint—it may dispatch subagents for tasks that could be done inline.

---

### 2. `subagent-orchestration` vs `sadd-dispatch` — Overlapping scope

**File:** `plugins/taches-principled/skills/subagent-orchestration/SKILL.md:4-7`
```
Use when user says "delegate this", "run in parallel", "spawn agents", "use subagents"...
Do NOT use for simple single-step tasks or when Claude is already acting as orchestrator without explicit request.
```

**File:** `plugins/tp-sadd/skills/sadd-dispatch/SKILL.md:5`
```
When user says 'dispatch subagent', 'launch agent for task', 'delegate this'...
```

**Conflict:** Both claim "delegate this" as a trigger. subagent-orchestration explicitly says it handles "delegate this", but sadd-dispatch also claims it.

---

## Orphaned Skills

### 1. `kaizen` — Design-time constraint, no natural trigger

**File:** `plugins/taches-principled/skills/kaizen/SKILL.md`

```
when_to_use: "Use when the user says 'apply kaizen', 'use the constraints', 'design this properly', or 'check against principles'."
```

**Issue:** No user naturally says "apply kaizen". This skill must be manually invoked. No other skill references it.

---

### 2. `plan-do-check-act` — No natural trigger

**File:** `plugins/taches-principled/skills/plan-do-check-act/SKILL.md`

```
when_to_use: "Use when the user says 'let's try an experiment', 'test this hypothesis', 'run a PDCA cycle', or 'try this and measure it'."
```

**Issue:** No user says "run a PDCA cycle". This skill requires explicit invocation of methodology names.

---

### 3. `write-concisely` — No natural trigger

**File:** `plugins/taches-principled/skills/write-concisely/SKILL.md`

```
when_to_use: "Use when the user says 'make this clearer', 'write this more concisely', 'clean up this text', or 'improve the writing'."
```

**Issue:** No user naturally says "make this clearer" as a skill trigger—they would just ask for the change. No other skill references it.

---

### 4. `fpf-read`, `fpf-propose`, `fpf-maintenance` — Niche FPF methodology

**File:** `plugins/tp-fpf/skills/fpf-read/SKILL.md`
**File:** `plugins/tp-fpf/skills/fpf-propose/SKILL.md`
**File:** `plugins/tp-fpf/skills/fpf-maintenance/SKILL.md`

```
fpf-read when_to_use: "Use when the user says 'FPF status', 'search FPF', 'query FPF', 'knowledge base'..."
fpf-propose when_to_use: "Use when the user says 'first principles', 'hypothesize', 'propose options', 'FPF'..."
fpf-maintenance when_to_use: "Use when the user says 'reset FPF', 'soft reset', 'hard reset'..."
```

**Issue:** FPF (First Principles Framework) is a niche methodology. Skills only trigger on explicit "FPF" mentions. No integration with other skills that produce decisions requiring first-principles analysis.

---

### 5. `root-cause-tracing` — Very specific bug scenario

**File:** `plugins/taches-principled/skills/root-cause-tracing/SKILL.md`

```
when_to_use: "Use when the user says 'trace this bug', 'find where it started', 'what called this', or 'where did this come from'."
```

**Issue:** Only triggers on specific bug-tracing language. No skill routes to it when debugging. Low discoverability.

---

## Broken Compositional Pairs

### 1. `create-prompts` + `execute-prompts` — Asymmetric contract

**Issue:** create-prompts explicitly references a "companion execution skill as a compositional pair" but execute-prompts states it "does not reference other skills by name or invocation pattern." The connection is one-directional and undocumented on the execution side.

---

## Summary Table

| Issue Type | Skills Involved | Severity |
|------------|----------------|----------|
| Duplicate (implement-task) | taches-principled vs tp-sdd | HIGH — identical names, identical triggers |
| Duplicate (plan-task) | taches-principled vs tp-sdd | HIGH — identical names, nearly identical functionality |
| Duplicate (add-task) | taches-principled vs tp-sdd | MEDIUM — nearly identical |
| Duplicate (ideation/create-ideas) | taches-principled vs tp-sdd | MEDIUM — circular referral |
| Broken compositional pair | create-prompts + execute-prompts | MEDIUM — one-directional contract |
| Contradiction (analyse-problem vs root-cause-analysis) | taches-principled internal | MEDIUM — unclear boundary |
| Conflicting triggers | subagent-orchestration vs sadd-dispatch | MEDIUM — "delegate this" collision |
| Orphaned skill | kaizen | LOW — design-time constraint |
| Orphaned skill | plan-do-check-act | LOW — niche methodology |
| Orphaned skill | write-concisely | LOW — no natural trigger |
| Orphaned skill | fpf-* skills | LOW — niche methodology |