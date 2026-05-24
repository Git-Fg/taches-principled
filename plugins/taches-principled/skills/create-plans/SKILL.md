---
name: create-plans
description: "Creates executable project plans that Claude implements directly. Use when user says 'plan', 'sketch', 'roadmap', or 'break down a project'."
when_to_use: |
  Use when the user says "make a plan", "plan this out", "sketch a roadmap", or "break down this project".
  IMMEDIATELY when starting new work that needs structured decomposition.
  Do NOT use for code review, debugging existing code, or one-off questions.
  Do NOT use when task is already refined and ready for execution (use execute-plans), when a single question needs answering (use diagnose instead), or when task is vague and needs capture first (use add-task).
argument-hint: [project or feature to plan]
---

## Decision Router

IF user asks to "plan" → FIRST create brief before roadmap
IF user asks to "plan a phase" → BEFORE creating tasks read the plan-format and checkpoints reference files
IF scope is unclear or large → BEFORE decomposing read the scope-estimation reference file
IF automation CLI available → BEFORE running commands read the cli-automation reference file

User phrase → Action routing:
- "plan", "make plan", "create plan" → Create brief first (never roadmap first)
- "quick plan", "sketch" → Short intake with 2-3 tasks max
- "full plan", "detailed" → Full intake with scope analysis
- "phase plan", "increment" → Use phase structure from the plan-format reference
- "execute", "run", "build it" → Load `execute-plans` skill (compositional pair)

---

# Create Plans Skill

Create executable project plans that Claude implements directly. Produces CLAUDE.md-executable prompts—not documentation.

## Core Principle

**PLAN.md is the prompt.** You're not writing documentation that gets transformed. You're writing the instruction Claude follows directly.

---

### Policy vs. Mechanism

**Policy** = what a good plan looks like (the desired outcome)
**Mechanism** = how to decompose and sequence tasks (the method)

A plan conflating policy and mechanism becomes brittle — it tells Claude what to do instead of what outcome to achieve. Keep policy in the plan; keep mechanism in the skill's reference docs.

Example:
- Policy (in PLAN.md): "Users can authenticate with email/password"
- Mechanism (in skill reference): "Decompose by subsystem, verify each task independently"

---

## Essential Principles

### Solo Developer + Claude

You plan for ONE person (you) and ONE implementer (Claude). No teams. No stakeholders. No ceremonies.

You are the visionary/product owner. Claude is the builder.

### Plans Are Prompts

PLAN.md is not a document that gets transformed into a prompt. PLAN.md IS the prompt. It contains:

- **Objective** — what and why
- **Context** — @file references
- **Tasks** — files, action, verify, done
- **Verification** — overall checks
- **Success criteria** — measurable completion
- **Output** — SUMMARY.md specification

When planning a phase, you write the prompt that executes it.

### Scope Control

Plans must complete within ~50% of context usage to maintain consistent quality.

**The quality degradation curve:**

| Context Usage | Quality Level | Mental State |
|--------------|---------------|--------------|
| 0-30% | PEAK | "I can be thorough" |
| 30-50% | GOOD | "Still have room" |
| 50-70% | DEGRADING | "Need to be efficient" |
| 70%+ | **POOR — Self-lobotomization** | "Must finish quickly" |

**Critical insight:** Claude degrades at ~40-50% when it perceives context pressure and enters "completion mode."

**Solution:** Aggressive atomicity—split phases into many small, focused plans. Each plan: 2-3 tasks maximum.

**Critical:** At 70%+, Claude begins "self-lobotomization" — cutting corners, giving cursory answers, skipping verification to race to completion. This is invisible degradation. The output looks complete but quality has collapsed.

**Prevention:** Aggressive atomicity. If a plan might exceed 50% context, split it proactively. Small plans are reliable plans.

### Numeric Thresholds

| Metric | Limit | Why |
|--------|-------|-----|
| Tasks per plan | 12 max (2-3 typical) | Degradation past this |
| Sequential dependency chain | 8 max | Parallelization opportunity lost beyond this |
| Files affected per task | 5 max | High coordination cost |
| Verification commands | 1-2 per task | More = verification theater |

**Split signal:** If a task has >3 subsystem touches, >5 files, or requires research + implementation — split it.

### Automate What You Can

Claude automates everything that has a CLI or API. If a tool exists, use it.

**The rule:** If Claude CAN do it via CLI, API, or tool, Claude MUST do it. Never ask you to:
- Deploy to Vercel/Railway/Fly (use CLI)
- Create Stripe webhooks (use CLI/API)
- Run builds/tests
- Write .env files
- Create database resources (use provider CLI)

**How verification works:**
- Tasks have explicit `verify` commands (run tests, check builds)
- If verification passes → task is done
- If verification fails → fix it and retry
- Only ask you to verify things that genuinely require human judgment (visual appearance, UX feel)

### Bash Injection = 0 Context Cost

Bash commands embedded in plan verification use `!<command>` syntax — the command CODE
never enters context, only its OUTPUT counts. This means complex validation scripts cost nothing.

Example:
- Verbose: "Run `npm test` to verify" (test output goes in context)
- Efficient: `!npm test` (only "X tests passed" output enters context, not the test suite code)

**When to use:** Build verification, test runs, lint checks, health endpoints.
**URL:** https://docs.claude.com/en/docs/agents-and-tools/agent-skills/overview#level-3-resources-and-code-loaded-as-needed

### Deviation Rules

Plans are guides, not straitjackets. Real development involves discoveries. Handle deviations automatically:

1. **Auto-fix bugs** — Broken behavior → fix immediately, document in Summary
2. **Auto-add missing critical** — Security/correctness gaps → add immediately, document
3. **Auto-fix blockers** — Can't proceed → fix immediately, document
4. **Heuristic architectural decisions** — Structural changes → evaluate, choose simplest correct path, log decision
5. **Log enhancements** — Nice-to-haves → log to ISSUES.md, continue

**All rules execute automatically.** No user input needed for any deviation type. Architectural decisions use heuristic rules (simplest path, reversible choices, plan direction) and log with rationale.

---

### Checkpoint Types

Checkpoints are markers that tell the executor how to handle a task segment. The execution skill resolves them autonomously.

| Type | Strategy Resolution |
|------|-------------------|
| `checkpoint:human-verify` | Executor self-verifies via CLI or file state. Logs result. (Maps exec strategy B) |
| `checkpoint:decision` | Executor applies heuristic rules, chooses path, logs rationale. (Maps exec strategy C) |
| `checkpoint:human-action` | Executor checks for CLI alternative; if none, placeholds and logs. (Maps exec strategy C) |

**Checkpoint declaration example:**
```markdown
### Task 2: Deploy to production
Files: .env.production
Action: Run deployment via CLI, verify health endpoint
Verify: `curl https://api.production.com/health` returns 200
Done: Production deployed and healthy
Checkpoint: checkpoint:human-verify  # Executor self-verifies via health endpoint
```

**Protocol:** Autonomous execution resolves all checkpoints without user interaction. Status updates at milestones.

### Ship Fast, Iterate Fast

No enterprise process. No approval gates.

Plan → Execute → Ship → Learn → Repeat.

Milestones mark shipped versions (v1.0, v1.1) and enable continuous iteration.

### Anti-Enterprise Patterns

NEVER include in plans:
- Team structures, RACI matrices
- Stakeholder meetings, alignment ceremonies
- Sprint ceremonies, standups, retros
- Multi-week estimates
- Change management processes
- Documentation for documentation's sake

If it sounds like corporate PM theater, delete it.

### Context Awareness

Monitor token usage via system warnings.

- **At 25% remaining**: Mention context getting full
- **At 15% remaining**: Offer handoff
- **At 10% remaining**: Auto-create handoff, stop

### Decision Documentation

Plans in the autonomous workflow don't ask questions at checkpoints. Instead, they document decision points with sufficient context for the executor to resolve heuristically:

- **Decision point**: "Auth strategy — options: sessions (simple), JWT (mobile-ready), hybrid"
- **Context**: Enough signal for heuristic choice (recommended option, trade-offs, reversibility)
- **No questions**: The executor decides based on heuristic rules and logs the choice

Mandatory decision documentation:
- Before writing PLAN.md (confirm breakdown)
- After low-confidence research
- On verification failures
- After phase completion with issues
- Before starting next phase with previous issues

---

## Planning Hierarchy

```
BRIEF.md      → What you want (human vision)
    ↓
ROADMAP.md    → Phases to get there
    ↓
PLAN.md       → What Claude does right now
    ↓
SUMMARY.md    → What happened
```

Each level gives context to the level below.

---

## Context Scan

On every invocation, spawn an explorer subagent (can read source, write findings, search project structure, and run commands) to scan the project context:

- Check git status — detect if git is initialized
- List planning structure (`.principled/plans/`, `.principled/plans/phases/`)
- Find any `.continue-here.md` files
- Check for existing artifacts (BRIEF.md, ROADMAP.md)
- Write all findings to `.principled/scratch/context-scan.md`

Read the scratchpad before proceeding to intake.

**If NO_GIT_REPO detected:** Auto-initialize: `git init && git add -A && git commit -m "chore: initial commit"`. No question needed — every project needs version control.

---

## Intake

Before planning, ensure you have sufficient context:

1. **Understand the goal** — what needs to be built
2. **Clarify scope** — priorities, constraints, what success looks like
3. **Set execution mode** — fully autonomous or human-in-the-loop at milestones

Use your tool to ask users your questions and prefill answers to gather what you need. Keep it focused — you don't need everything upfront, just enough to plan confidently.

If a handoff file exists at `.principled/plans/phases/XX/.continue-here.md`, skip the intake and auto-resume. If a BRIEF.md or ROADMAP.md already exists, skip the intake and proceed to the next phase.

Always check for existing artifacts in `.principled/plans/` before starting — never make the user re-answer questions already answered. If no git repo exists, auto-initialize silently.

---

## Explore with Subagent Fan-Out

Before creating a plan, understand the project thoroughly. Use subagent fan-out to explore in parallel:

**Read the agents folder** — each markdown file is a subagent prompt template. Read the relevant agent, fill in placeholders like `{{context}}`, `{{task}}`, `{{scope}}`, and dispatch it as a subagent.

**Fan-out pattern for exploration:**

1. **Explorer agents** — Map project structure, find key files, identify patterns. Spawn 3-5 in parallel, each covering different areas (frontend, backend, config, tests, docs).

2. **Researcher agents** — For unfamiliar technologies or patterns in the spec, spawn parallel researchers to find current best practices.

3. **Architect agents** — When facing complex decisions (auth strategy, state management, API design), spawn an architect subagent to evaluate trade-offs.

**Fan-out rules:**
- All parallel subagent dispatches MUST occur in a single message
- Each subagent should have disjoint scope (different files/areas)
- Subagents start cold — pass all context in the spawn prompt
- Cap at 5 concurrent subagents to avoid coordination overhead

**Task coordination — when to track vs. delegate:**

Tracking (orchestrator retains):
- Coordinating dependencies and sequencing decisions
- Aggregating findings from multiple subagents
- Making trade-off calls when researchers disagree
- Final verdict on plan quality before handoff

Delegating (subagent owns execution):
- Parallel exploration of disjoint areas
- Deep research on specific technical questions
- Implementation of well-scoped, independent tasks
- Verification against specific criteria

Signal: if a task requires seeing output from another task to proceed, it is a dependency — handle it in the orchestrator, not a subagent. Subagents should be able to complete their scope without waiting for other subagents.

**Example explore phase:**

Read the agent templates, then dispatch parallel subagents for exploration:
1. Explorer agents (3-5) — map project structure across different areas (frontend, backend, config, tests)
2. Researcher agents — find best practices for unfamiliar technologies
3. Architect agents — evaluate trade-offs for complex decisions

After all complete, aggregate findings into understanding of the project.

**Subagent handoff:** Every subagent must receive explicit handoff with:
- Who spawned it and why (role and purpose)
- What context it needs to work with
- What scope to cover (specific files/areas)
- What success criteria to meet (pass/fail conditions)
- How to report back (structured format)

Without clear handoff, subagents operate without proper scope boundaries. The orchestrator must provide all context inline — subagents start cold with no conversation history.

### Centralized Scratchpad Protocol

When fanning out subagents for exploration, ALL findings MUST be written to a centralized scratchpad:

**Location:** `.principled/scratch/{plan-id}-exploration.md`

**Before spawning subagents:**
1. Read any existing scratchpad for prior findings (avoid duplicate work)
2. Write exploration questions and current context to scratchpad
3. Define what "success" looks like for each subagent's findings

**Subagent tool requirements for exploration (NON-OPTIONAL):**
- **NEVER** use "native" Explore subagents (Haiku, read-only)
- **REQUIRED** minimum: read source files, write findings to disk, search project structure, and run shell commands
- Write access is **NON-OPTIONAL** — findings must be persisted

**After subagents return:**
1. Read scratchpad BEFORE synthesizing findings
2. Merge findings from scratchpad, not from subagent reports
3. Write synthesis conclusions to scratchpad

**Why:** Prevents telephone-game degradation. Direct scratchpad access eliminates paraphrase drift that occurs when orchestrators synthesize without source access.

**Using critic agents during planning:**

After the fan-out exploration, before writing the plan, spawn a critic subagent (read the critic agent template from the agents folder) to challenge the emerging approach:

```
Spawn a critic subagent (general-purpose with Write tool access):
Focus: Challenge the proposed approach as devil's advocate
- What assumptions does the approach make that might be wrong?
- What could go wrong with this direction?
- Are there hidden dependencies or conflicts we missed?
- What risks does the task grouping miss?

If critic finds critical issues: reconsider the approach before committing to plan.
```

**Why:** Catching a flawed approach during planning is cheaper than reworking during execution. The explore phase gathers information; the critic phase tests whether that information supports the chosen direction.

### Model Routing for Fan-Out

Each subagent role uses a model matched to its cognitive load:

| Role | Model | Rationale |
|------|-------|----------|
| Explorer subagent | Haiku | Structural I/O — file discovery, pattern detection |
| Researcher subagent | Haiku | Documentation reading — lightweight comprehension |
| Architect subagent | Sonnet | Trade-off evaluation — requires deeper reasoning |
| Pre-plan critic subagent | Haiku | Assumption challenge — lightweight pattern recognition |
| Post-plan critic subagent | Sonnet | Dependency verification — requires full plan comprehension |

---

## Plan Creation Loop

After exploration, create plans in a structured loop: one phase at a time, with critic review between phases.

### Loop Structure

For each phase plan:

```
1. Synthesize exploration findings into phase scope
2. Write phase PLAN.md (2-3 tasks, verification per task)
3. Spawn critic subagent to review the plan
   - Focus: task granularity, missing edge cases, dependency ordering
   - Critic writes findings to scratchpad
4. Read scratchpad, revise plan based on critic feedback
5. Check: is planner context approaching 50%?
   - If yes: create handoff document, route to execution gate
   - If no: proceed to next phase
6. Repeat for next phase
```

### Context Management Across Phases

Each phase loop iteration consumes context. Monitor token usage:

- **At 50% planner context used:** Stop creating, present execution gate. Do not start a new phase creation loop. The remaining context is for the execution phase.
- **Phase creation should be fast:** Write brief, write 2-3 tasks, spawn critic, revise. If a single phase plan is taking more than a few turns, the scope is too large.

### Critic Integration

Spawn one critic subagent per phase plan (general-purpose, Write access):

```
Focus: Review the phase plan as a cold-start executor
- "If I followed this PLAN.md literally, would the outcome be correct?"
- Are the tasks atomic enough? (2-3 per plan, not 12)
- Does each task have a verifiable completion criterion?
- Are file paths and commands correct (not assumptions)?
- Would I be blocked on any task by prerequisites?
```

The critic reads the new PLAN.md from the scratchpad path, writes findings back. Orchestrator reads findings, applies revisions, then proceeds.

**Why per-phase:** Phase plans are independent — critic feedback on phase 2 does not invalidate phase 1. A single end-to-end critic review creates a bottleneck and encourages the critic to comment on irrelevant phases.

**Exception — one end-to-end review:** After ALL phases are created, spawn a Sonnet critic subagent for a cross-phase consistency audit of the full roadmap: do the phases fit together? Are there missing dependencies between phases? Is the completion order correct?

---

## Routing

| Response | Action |
|----------|--------|
| "brief", "new project", "start" | Create brief |
| "roadmap", "phases" | Create roadmap |
| "phase", "plan phase", "next phase" | Plan phase |
| "chunk", "next tasks" | Plan chunk |
| "execute", "run", "do it" | Load execution skill |
| "research", "investigate" | Create research prompt |
| "handoff", "pack up", "stopping" | Create handoff |
| "resume", "continue" | Load handoff |
| "transition", "complete", "done" | Mark phase complete |
| "milestone", "ship", "release" | Complete milestone |

---

## Execution Handoff

**When user says "execute", "run", "build it", "do it":**

Single question:

**Question:** Ready to execute [plan name]?

**Options:**
- Execute autonomously — loads execution skill, status updates only
- Let me review first — show the plan, then re-present

**If user selects execute:** Route to `execute-plans`. The execution skill autonomously analyzes checkpoint structure, selects strategy, spawns parallel workers, self-reviews, and commits. Status updates only — no questions.

Do NOT re-invoke create-plans. Do NOT ask for guidance. Execute autonomously via the execution skill.

---

## Files Structure

```
.principled/plans/
├── BRIEF.md              # Vision
├── ROADMAP.md            # Phase structure + tracking
└── phases/
    ├── 01-foundation/
    │   ├── 01-01-PLAN.md
    │   ├── 01-01-SUMMARY.md
    │   ├── 01-02-PLAN.md
    │   └── 01-02-SUMMARY.md
    └── 02-auth/
        └── 02-01-PLAN.md
```

**Naming convention:**
- Plans: `{phase}-{plan}-PLAN.md` (e.g., `01-03-PLAN.md`)
- Summaries: `{phase}-{plan}-SUMMARY.md` (e.g., `01-03-SUMMARY.md`)
- Phase folders: `{phase}-{name}/` (e.g., `01-foundation/`)

Files sort chronologically. Related artifacts are adjacent.

---

## What Good Looks Like

```markdown
# Phase 1: Database Setup

## Objective
Set up PostgreSQL with the user schema.

Purpose: Establish data layer for the application
Output: Migration files, Prisma schema, connection verified

## Context
@.principled/plans/BRIEF.md
@.principled/plans/ROADMAP.md

## Tasks

### Task 1: Create Supabase project
Files: .env
Action: Run `supabase projects list` to verify CLI access, then note project ref
Verify: `supabase projects list` shows project
Done: Project exists with connection string in .env

### Task 2: Create users table migration
Files: supabase/migrations/001_users.sql
Action: Write migration creating users table with id, email, password_hash, created_at, updated_at
Verify: `supabase db push` succeeds
Done: Table exists in Supabase dashboard

### Task 3: Generate Prisma schema
Files: prisma/schema.prisma
Action: Run `supabase gen types typescript` and update Prisma schema
Verify: `npx prisma validate` passes
Done: Types generated, no schema errors

## Verification
- [ ] `supabase projects list` shows project
- [ ] Users table exists in Supabase dashboard
- [ ] `npx prisma validate` passes
- [ ] Connection string in .env

## Success Criteria
- PostgreSQL running with users table
- Prisma schema validated
- Ready for auth implementation

## Output
After completion, create `.principled/plans/phases/01-foundation/SUMMARY.md`
```

---

## Common Mistakes

**Vague tasks.** "Implement auth" isn't a task. "Create login endpoint with email/password form" is.

**No verification.** Every task needs a way to check it worked. "It's done" isn't verification. "`curl /api/auth/login` returns 200" is.

**Huge phases.** If PLAN.md is 500 lines, the phase is too big. Split into 01-01, 01-02, etc.

**Not documenting decisions.** Every plan should include enough context for the executor to resolve checkpoints heuristically. If there's a choice (auth strategy, library selection, API design), document the options with trade-offs: "Decision point: [options] — recommended: [X] because [reason]." The executor chooses from documented options autonomously.

---

## Anti-Patterns

**Full anti-pattern catalog is in the plan-format.md reference file in this skill's references.**

### 500-line Mega-Plan
Each plan: 2-3 tasks, ~15-60 min of work. Quality degradation is invisible until too late.

### Vague Task Definitions
"Implement auth" isn't a task. "Create login endpoint with email/password form" is.

---

## Reference Index

IF writing brief → FIRST read the brief template file
IF writing phase plan → BEFORE tasks read the plan-format and checkpoints reference files
IF scope is unclear → BEFORE decomposing read the scope-estimation reference file
IF automation available → BEFORE running commands read the cli-automation reference file
IF managing milestones → read the milestone-management reference file
IF spawning subagents → read the explorer agent template, researcher agent template, architect agent template, critic agent template, verifier agent template, and implementer agent template from the agents folder for templates

---

## Domain Expertise (Not Included)

The original skill included a `domain_expertise` system that scanned `~/.claude/skills/expertise/` for domain-specific skills, used keyword inference to detect project types, and loaded expertise via pattern matching.

**This was excluded as over-engineered cruft:**

- Keyword inference is brittle and misses more than it hits
- Requires maintaining a parallel expertise directory structure
- The skill functions fine without it (graceful degradation exists)
- Simpler alternative: the explore phase discovers project type organically

If domain expertise is needed, invoke the relevant expertise skill directly rather than trying to auto-detect.

---

## Success Criteria

- Context scan runs before intake
- Appropriate workflow selected based on state
- PLAN.md IS the executable prompt
- Hierarchy maintained (brief → roadmap → phase)
- Handoffs preserve full context for resumption
- Context limits respected (auto-handoff at 10%)
- Deviations handled automatically per embedded rules
- All work fully documented

## Single Execution Gate

**The only user interaction point.** After plan creation is complete, present one question:

**Question:** Execute this plan?

**Options:**
- Execute autonomously (recommended) — loads execution skill, status updates only
- Let me review first — show the plan, then re-present the gate

**If user selects execute:** Route to `execute-plans`. Do NOT explain the execution skill's strategy selection — it handles that autonomously. Status updates only.

**If user selects review:** Show the plan, then re-ask "Execute this plan?" with the same two options.

**No other questions.** No "What else?" No "Done for now?" No refinement prompts. The user said "plan" — deliver a plan and one decision gate.