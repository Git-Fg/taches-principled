# Synthesis: What this means for taches-principled

**Audience:** taches-principled maintainers (this is a maintainer doc, not a user-facing one).
**Date:** 2026-06-02
**Scope filter:** Custom-endpoint compatible only — every recommendation below works against any Claude-compatible API (minimax / MiniMax / MM-X / etc.).

---

## The one-line takeaway

**Dynamic Workflows formalize, in the platform itself, the orchestration patterns taches-principled invented in skill bodies.** Fan-out, critique loops, adversarial verification, judge panels, loop-until-dry — these are now first-class script primitives in Claude Code, available against any model endpoint that supports tool use with schema enforcement.

The strategic question for taches-principled is no longer *"do we provide orchestration?"* — the platform does. It is **"do we provide the *quality patterns that go into the workflow scripts Claude writes*?"**

---

## What the platform now owns (so we should stop owning)

These were the things skill bodies in taches-principled had to teach the main agent to do — and the runtime now does them directly:

| Capability | Where we taught it | Where the platform owns it now |
|---|---|---|
| Fan-out across N subagents with structured output | `subagent-orchestration` skill, `create-subagents` references | `agent(prompt, {schema})` script hook |
| Pipeline through stages with no barrier | Hand-rolled in `next-tasks-orchestration` and command bodies | `pipeline(items, stage1, stage2, ...)` |
| Barrier-synchronized parallel fan-out | `parallel` patterns in our hub skills | `parallel(thunks)` |
| Adversarial verify (N skeptics per finding) | `sadd` patterns + manual orchestration in `critique` | Tool-schema-level pattern named in the Workflow tool description |
| Judge panel + synthesize winner | `sadd-judge` + `sadd-meta-judge` + `sadd-synthesizer` agents | Named in Workflow tool guidance |
| Loop-until-dry discovery | We never had this cleanly — emerged ad-hoc in skills | Named pattern with example code |
| Multi-modal sweep | Implicit in some research commands | Named pattern with example code |
| Completeness critic | `self-critic` + `self-review` agents | Named pattern |
| Worktree isolation per agent | We documented it but didn't auto-apply | `isolation: 'worktree'` opt on `agent()` |
| Resumable orchestration | We had no story for this | Built into the runtime; same script + same args → 100% cache hit |
| Concurrency cap with auto-queue | We never bounded this | 16 concurrent / 1000 total guards built in |

## What the platform does NOT own (where we keep adding value)

The platform gives Claude the *primitives*. It does not give Claude **judgment about when and how to use them well.** This is where taches-principled stays load-bearing:

### 1. Methodology — the principled approach behind each pattern

The Workflow tool description names the patterns (adversarial verify, judge panel, etc.) but does not teach the *methodology* behind them: when to use FPF (first-principles), when to use TDD, when to use DDD bounded contexts, when to invoke SADD's tree-of-thoughts vs competitive generation. Our plugins (`tp-fpf`, `tp-tdd`, `tp-ddd`, `tp-sadd`) encode this judgment.

**Action:** Every plugin's hub skill should now teach Claude **what kind of workflow to write for this methodology** — not "use the Agent tool to spawn N agents" (deprecated framing), but "when writing a workflow script for this kind of task, here is the phase structure and the schema each agent should return."

### 2. Anti-patterns and consequence framing

The platform doc names patterns but not failures. Our skills carry the consequence framing — "if you skip adversarial verification on this kind of task, here is what fails." That value carries forward unchanged.

**Action:** Audit every skill for anti-pattern sections. The platform reading the workflow script will execute it; only our skills can stop Claude from writing the wrong shape in the first place.

### 3. Schema design for structured-output agents

The `agent(prompt, {schema})` opt is powerful but unforgiving — the agent retries on schema mismatch, so a sloppy schema burns tokens. Our skills can teach Claude the **right shape of schema for the methodology**: what fields a critique should return, what fields a code-review judgment should return, what fields a debug-tracer finding should return.

**Action:** Create a `references/workflow-schemas/` directory in each plugin with the canonical JSON Schemas for that methodology's agent return values.

### 4. Phase decomposition that respects methodology

A workflow script's `meta.phases` block is the user-visible structure of the run. The default Claude-generated workflow will pick generic phase names (Scan, Review, Fix). Our methodologies have *principled* phase structures: A3 (Background → Current State → Goal → Analysis → Countermeasures → Plan → Follow-up), PDCA, TDD's Red-Green-Refactor, FPF's PROPOSE/EXTEND/VERIFY. These should appear as `phases` in workflows the methodology skills cause Claude to write.

**Action:** Each methodology skill body should include a "**Workflow phase structure for this methodology**" subsection with the canonical phase titles and their detail strings.

### 5. Custom-endpoint discipline

The Workflow runtime calls the model API like an interactive session. This means our skills should:
- Verify the endpoint supports **tool use with schema enforcement** before recommending `schema:` opts
- Not assume **xhigh effort** is available — fall back to a doubled-up adversarial verify if xhigh is missing
- Respect endpoint **concurrency limits** — if our methodology recommends 8-way fan-out and the endpoint caps at 4 concurrent, the workflow stalls. Either document the requirement or default to lower concurrency.

**Action:** Add a `Custom-endpoint considerations` block to each methodology skill describing the minimum endpoint capabilities required.

---

## Concrete plugin-by-plugin implications

### tp-sadd (Structured Agent-Driven Development)
This plugin is the most directly overlapped. SADD's competitive-generation, judge-panel, and meta-judge patterns are now the *named patterns in the Workflow tool description*. Action: rewrite the SADD hub skill to teach Claude **how to write a SADD workflow script** rather than how to orchestrate SADD inline. The body of every SADD mode (COMPETE, JUDGE, VERIFY, EXPLORE) becomes a workflow template, not a fan-out recipe.

### tp-fpf (First-Principles Framework)
FPF's PROPOSE / EXTEND / VERIFY cycle, hypothesis-generator → logic-verifier → evidence-validator → trust-auditor pipeline, maps cleanly onto `pipeline(items, propose, extend, verify)`. Action: the FPF hub skill teaches the workflow shape; the subagent definitions stay as the canonical role prompts that workflow scripts will reference.

### tp-tdd
Red-Green-Refactor is a three-phase workflow shape. Action: provide a TDD workflow template in `tp-tdd/workflows/tdd-feature.js` that Claude can pick up or imitate when the user asks "write tests first" workflows. Three phases, structured-output schema for failing test → minimal implementation → refactor.

### tp-ddd (Domain-Driven Design)
DDD's bounded-context analysis is naturally a multi-modal sweep (by aggregate, by service, by use case, by event flow). Action: encode this as a multi-modal sweep workflow template.

### tp-git
Most git workflow automation stays as it is — it's CLI orchestration, not multi-agent. The one shift: `/loop` + `/goal` together replace the "babysit the PR" patterns we used to teach manually. Action: `tp-git`'s SHIP/REVIEW modes should mention `/goal "PR merged with green CI"` as the canonical end-condition.

### tp-meta
Meta-review of session transcripts is naturally an adversarial verify (multiple reviewers, each looking for a different anti-pattern class). Action: the meta-review skill teaches Claude to write a workflow with one reviewer per anti-pattern category, then a synthesizer.

### taches-principled core
The big move here: **most commands in the core plugin (`/orchestrate`, `/next-tasks-orchestration`, `/critique`, `/improve`) are now thin pointers to "have Claude write a workflow for this kind of task."** Their value collapses from "do the orchestration" to "tell Claude what kind of workflow to write." Action: rewrite each as a 1–3 sentence pointer per the High Freedom, High Trust principle.

---

## What changes in the CLAUDE.md guidance

The project CLAUDE.md teaches a "subagent-first execution contract": default to subagents, only main-agent for trivial work. With workflows in the picture, the contract becomes layered:

| Task scale | Default execution mode |
|---|---|
| Trivial (1-file edit, single search) | Main agent inline |
| Non-trivial single-context (3-10 files, single methodology) | **Subagents** (still the right answer — workflows have setup overhead) |
| Multi-stage non-trivial (fan out, then verify, then synthesize) | **Workflow** |
| Codebase-wide / many-file / multi-methodology | **Workflow** with phase structure |
| Long-running with external triggers | Workflow + `/loop` + channels |

The skill's job is no longer "spawn subagents" — it's "**recognize the task scale and tell Claude which execution mode is right.**"

---

## What we should NOT do

A few tempting moves that would actually hurt:

1. **Do not** rewrite the entire plugin to use `Workflow` everywhere. Workflows have real setup overhead (script generation, approval prompt, concurrency setup). Trivial and small tasks still belong inline; non-trivial single-context still belongs in subagents.

2. **Do not** remove the subagent definitions. The Workflow runtime can use them — `agent(prompt, {agentType: 'critic'})` resolves to our `tp-sadd:sadd-judge` agent definition. Our agent definitions are the durable artifact; the orchestration around them is what changes.

3. **Do not** treat the `Workflow` tool as a transformation we apply autonomously. Per the project's Transformer Mandate: the AI generates and scores, the human decides. We document workflows as a *capability* and as a *recommendation pattern*, not as a structural rewrite to push without consent.

---

## Custom-endpoint deployment checklist

For every methodology skill that recommends writing a workflow, the skill body should require Claude to verify:

- [ ] Endpoint supports tool use with **structured output schema enforcement**
- [ ] Endpoint supports the **concurrency** the workflow will use (default 16; reduce if needed)
- [ ] Endpoint supports **prompt caching with the 5-minute TTL** assumption in `ScheduleWakeup` delay picking (or accept slower wakeups)
- [ ] If the workflow uses `ultracode` / xhigh effort, endpoint exposes the effort field
- [ ] If the workflow uses `isolation: 'worktree'`, git is available in the execution environment

If any check fails, the methodology should describe a **graceful degradation path** (e.g., "fall back to subagents with manual schema validation instead of `agent(prompt, {schema})`").

---

## What to ship next

In priority order:

1. **Update CLAUDE.md** — the subagent-first contract becomes the workflow-aware contract above. (Self-contained edit, no skill changes yet.)
2. **Rewrite tp-sadd hub skill** — teach Claude to write SADD-shaped workflows. (Biggest payoff because SADD overlaps most.)
3. **Add `Workflow phase structure` subsection** to each methodology skill body (FPF, TDD, DDD, meta-review).
4. **Add `references/workflow-schemas/`** to each methodology plugin with canonical agent return schemas.
5. **Audit core taches-principled commands** for collapse to thin pointers (`/orchestrate`, `/next-tasks-orchestration`, etc.).
6. **Document custom-endpoint considerations** in each methodology skill — the deployment checklist above.

None of these changes break anything that exists. They re-layer the value: we go from competing with the platform's orchestration to *teaching the platform's orchestration what shape to take for our methodologies.*
