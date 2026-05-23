# Hub-Spoke Skill Architecture Recommendation

## Key Principle

Hub-and-spoke is the right consolidation model because there are genuine workflow stages and action types that warrant distinct skills, but within each stage, multiple specialized skills fragment the routing surface without adding coherent capability. The hub skill auto-selects between specialized methods based on context signals — this collapses redundant spokes while preserving distinct behaviors. Do NOT conflate hub-and-spoke with "fat skill anti-pattern" — the hub's job is routing, not doing-everything.

The break-even point for routing quality is 22-28 skills. Current is 38. Target is 28.

---

## Exempt Skills (Do Not Merge)

These skills are compositional pairs or serve distinct workflow stages where separation is load-bearing:

| Skill | Reason Exempt |
|-------|--------------|
| `create-plans` + `execute-plans` | Compositional pair — create produces PLAN.md consumed by execute; separation enables just-in-time creation |
| `create-prompts` + `execute-prompts` | Compositional pair — prompt creation vs prompt execution are distinct phases |
| `plan-task` + `implement-task` | Different scope (project plan vs task implementation) with distinct entry/exit criteria |
| `ideation` + `add-task` | Different workflow stages (divergent generation vs task capture) |
| `subagent-orchestration` | Low-level spawn primitive — orchestration policy vs dispatch mechanism |
| `kaizen` | Constraint/guardrail at design-time — opportunity-focused, not problem-focused |
| `plan-do-check-act` | PDCA iterative cycle — orthogonal to other execution skills |
| `create-skills` + `create-subagents` | Different targets (skill artifacts vs agent definitions) |

---

## Consolidation Targets

### 1. Problem Analysis Cluster: 4 -> 1

**Skills merged:**
- `analyse` + `analyse-problem` + `root-cause-analysis` + `root-cause-tracing`

**New skill name:** `diagnose`

**Decision router logic:**
```
IF investigating specific incident → A3 format documentation
IF tracing bug backward through call stack → instrumentation before failure
IF applying Five Whys or Fishbone → structured causal analysis
IF general code/process/waste analysis → Gemba Walk / VSM / Muda selection
```

**Rationale:** All four serve "understand what went wrong" with incompatible entry formats. `analyse` is the routing hub — it already contains Gemba/VSM/Muda routing. The other three add A3, Five Whys/Fishbone, and backward-tracing methods. A single `diagnose` skill with a decision router preserves all capabilities while eliminating 3 route-confusion points.

---

### 2. Execution Dispatch Cluster: 3 -> 1-2

**Skills merged:** `sadd-dispatch` + `sadd-execute` + `subagent-driven-development`

**New skill:** Absorb into `implement-task` — expand modes to cover:
- Single task (simplest case)
- Sequential with per-step verification (current `implement-task` strength)
- Parallel with isolated retries
- Best-of-N competitive with meta-judge

**Note:** `launch-sub-agent` was already deleted as a duplicate — this consolidation is organic.

**Rationale:** `implement-task` (623 lines) has the most sophisticated verification loop (refine/continue/human-in-the-loop). It should absorb the simpler tp-sadd patterns rather than the reverse. `sadd-dispatch` adds single-task dispatch with model selection. `sadd-execute` adds competitive mode. `subagent-driven-development` adds plan-driven dispatch with code review gates.

**Keep separate:** `subagent-orchestration` (low-level spawn primitives), `sadd-tot` (exploration phase, not execution)

---

### 3. Verification Cluster: 3 -> 1

**Skills merged:** `code-review` + `code-simplify` + `write-concisely`

**New skill name:** `refine`

**Decision router logic:**
```
IF reviewing code (PR/local) → multi-agent review (6 specialized agents)
IF simplifying code → 5-stage numeric threshold pipeline
IF improving prose clarity → Strunk & White application
```

**Rationale:** All three transform existing work product. Mode-based routing handles the distinct behaviors. `code-review` (6 parallel review agents) and `code-simplify` (transformation pipeline) are distinct enough to warrant mode separation, but both arrive via "improve this" type triggers.

---

### 4. Judge Evaluation Cluster: 2 -> 1

**Skills merged:** `sadd-judge` + `judge-with-debate`

**New skill name:** `judge`

**Decision router logic:**
```
IF single-judge evaluation → routine path
IF multi-judge debate until consensus → debate mode (default for high-stakes)
```

**Rationale:** `sadd-judge` already has `--debate` flag. `judge-with-debate` adds multi-round debate loop — this is subsumed by the debate mode. The result is a unified judge skill with single/debate paths.

---

## Skills to Keep As-Is (Distinct Triggers)

| Skill | Rationale |
|-------|-----------|
| `git-ship`, `git-review`, `git-issues` | Git-specific workflows — no meaningful overlap |
| `fpf-read`, `fpf-propose`, `fpf-maintenance` | FPF-specific trilogy — self-contained reasoning framework |
| `tdd` | Distinct TDD methodology |
| `reflexion` | Self-critique with distinct trigger ("reflect on this") |
| `sadd-patterns` | Architecture design — not execution |
| `do-competitively` | Distinct competitive generation mode |
| `sadd-tot` | Tree of Thoughts — distinct exploration phase |
| `update-docs` | Post-code-change documentation — distinct workflow |
| `subagent-orchestration` | Low-level primitive — necessary for spawn infrastructure |
| `add-task` | Task capture entry point |

---

## Final Skill Count

| Metric | Value |
|--------|-------|
| Current skills | 38 |
| Skills removed by consolidation | -10 |
| Post-consolidation target | ~28 |

**Breakdown of removals:**
- Problem analysis cluster: -3 (4 -> 1)
- Execution dispatch cluster: -2 (3 -> 1, or -3 -> 2)
- Verification cluster: -2 (3 -> 1)
- Judge cluster: -1 (2 -> 1)
- `git-advanced` merged into `git-ship`: -1
- `launch-sub-agent` already deleted: no action needed

**Note:** The 25-skill target in some inputs is aggressive and not achievable without losing plugin-specific skills or creating fat-skill anti-patterns. 28 skills is the realistic optimal — within the 22-28 breaking point range.

---

## CLAUDE.md Update Required

Add to the Skill Authoring section or create a new Hub-Spoke Pattern section:

```markdown
## Hub-Spoke Skill Architecture

Use hub-and-spoke to consolidate skills that share purpose but differ in method, entry format, or verification strategy.

**Hub skills** auto-select between methods based on context signals — they route, they don't execute-all-things.
**Spoke skills** provide specialized behavior too distinct to absorb into modes.

**When to use:**
- Multiple skills cover the same workflow stage but with incompatible entry formats
- Low trigger density per skill (< 5 triggers)
- Routing confusion between similar skill names

**When NOT to use:**
- Skills serve different workflow stages (planning vs execution)
- Skills have distinct entry/exit contracts with downstream dependencies
- Create/execute compositional pairs (separation is intentional and load-bearing)

**Canonical hub skills:**
- `diagnose` — routes between investigation methods (A3, Five Whys, call-stack tracing, Gemba/VSM/Muda)
- `refine` — routes between improvement modes (review, simplify, write-clearly)
- `judge` — routes between evaluation modes (single, debate)
```

---

## Implementation Order

1. **Phase 1 (High value, low risk):** Merge problem analysis cluster into `diagnose`
2. **Phase 2 (Medium value, medium risk):** Expand `implement-task` to absorb tp-sadd dispatch patterns
3. **Phase 3 (Medium value, low risk):** Merge `code-review`+`code-simplify`+`write-concisely` into `refine`, and `sadd-judge`+`judge-with-debate` into `judge`
4. **Phase 4 (Evaluate):** Assess whether `sadd-tot` warrants mode absorption or stays separate
