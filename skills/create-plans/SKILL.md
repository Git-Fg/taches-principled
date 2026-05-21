---
name: create-plans
description: "Create executable project plans that Claude implements directly. Use when user asks to plan, sketch, roadmap, or break down a project."
when_to_use: |
  Do NOT use for code review, debugging existing code, or one-off questions.
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
| 70%+ | POOR | "Must finish quickly" |

**Critical insight:** Claude degrades at ~40-50% when it perceives context pressure and enters "completion mode."

**Solution:** Aggressive atomicity—split phases into many small, focused plans. Each plan: 2-3 tasks maximum.

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
- Run builds/tests (use Bash)
- Write .env files (use Write tool)
- Create database resources (use provider CLI)

**How verification works:**
- Tasks have explicit `verify` commands (run tests, check builds)
- If verification passes → task is done
- If verification fails → fix it and retry
- Only ask you to verify things that genuinely require human judgment (visual appearance, UX feel)

### Deviation Rules

Plans are guides, not straitjackets. Real development involves discoveries. Handle deviations automatically:

1. **Auto-fix bugs** — Broken behavior → fix immediately, document in Summary
2. **Auto-add missing critical** — Security/correctness gaps → add immediately, document
3. **Auto-fix blockers** — Can't proceed → fix immediately, document
4. **Ask about architectural** — Major structural changes → stop and ask
5. **Log enhancements** — Nice-to-haves → log to ISSUES.md, continue

**Only Rule 4 requires your input.** Rules 1-3, 5 execute automatically.

---

### Checkpoint Types

Checkpoints are for verification and decisions, not manual work. Claude automates everything that has a CLI or API.

| Type | Trigger | When to Use |
|------|---------|-------------|
| `checkpoint:human-verify` | Claude automated, human confirms | Visual checks, UI verification, reviewing generated content |
| `checkpoint:decision` | Human makes implementation choice | Architecture, library selection, API design |
| `checkpoint:human-action` | Human performs action (no CLI/API) | Email verification, 2FA, account approval requiring web login |

**Checkpoint declaration example:**
```markdown
### Task 2: Deploy to production
Files: .env.production
Action: Run deployment via CLI, verify health endpoint
Verify: `curl https://api.production.com/health` returns 200
Done: Production deployed and healthy
Checkpoint: checkpoint:human-verify  # Human confirms deployment looks correct
```

**Protocol:** Claude automates work → reaches checkpoint → presents results → waits for confirmation → resumes

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

### User Gates

Never charge ahead at critical decision points. Use gates:
- **AskUserQuestion**: Structured choices (2-4 options)
- **Inline questions**: Simple confirmations
- **Decision gate loop**: "Ready, or ask more questions?"

Mandatory gates:
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

Run on every invocation:

```bash
# Check git status
git rev-parse --git-dir 2>/dev/null || echo "NO_GIT_REPO"

# Check for planning structure
ls -la .principled/plans/ 2>/dev/null
ls -la .principled/plans/phases/ 2>/dev/null

# Find any continue-here files
find . -name ".continue-here.md" -type f 2>/dev/null

# Check for existing artifacts
[ -f .principled/plans/BRIEF.md ] && echo "BRIEF: exists"
[ -f .principled/plans/ROADMAP.md ] && echo "ROADMAP: exists"
```

**If NO_GIT_REPO detected:** Use AskUserQuestion to present options:

**Question:** No git repository found. Initialize one?
**Options:**
- A: Initialize git repository (recommended)
- B: Continue without git

Present scan findings before intake.

---

## Intake

Based on scan results, present context-aware options:

**If handoff found:**
Use AskUserQuestion to present options:

**Question:** Found handoff at .principled/plans/phases/XX/.continue-here.md. What would you like to do?
**Options:**
- A: Resume from handoff (recommended)
- B: Discard handoff, start fresh
- C: Do something else

**If planning structure exists:**
Use AskUserQuestion to present options:

**Question:** What would you like to do?
**Options:**
- A: Plan next phase (recommended)
- B: Execute current phase
- C: Create handoff
- D: View/update roadmap
- E: Something else

**If no planning structure:**
Use AskUserQuestion to present options:

**Question:** No planning structure found. What would you like to do?
**Options:**
- A: Start new project (create brief) (recommended)
- B: Create roadmap from existing brief
- C: Jump straight to phase planning
- D: Get guidance on approach

---

## Explore with Subagent Fan-Out

Before creating a plan, understand the project thoroughly. Use subagent fan-out to explore in parallel:

**Read the agents folder** at `skills/create-plans/agents/` — each markdown file is a subagent prompt template. Read the relevant agent, fill in placeholders like `{{context}}`, `{{task}}`, `{{scope}}`, and dispatch it as a subagent.

**Fan-out pattern for exploration:**

1. **Explorer agents** — Map project structure, find key files, identify patterns. Spawn 3-5 in parallel, each covering different areas (frontend, backend, config, tests, docs).

2. **Researcher agents** — For unfamiliar technologies or patterns in the spec, spawn parallel researchers to find current best practices.

3. **Architect agents** — When facing complex decisions (auth strategy, state management, API design), spawn an architect agent to evaluate trade-offs.

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

Read agent templates from `skills/create-plans/agents/`, then dispatch parallel subagents for exploration:
1. Explorer agents (3-5) — map project structure across different areas (frontend, backend, config, tests)
2. Researcher agents — find best practices for unfamiliar technologies
3. Architect agents — evaluate trade-offs for complex decisions

After all complete, aggregate findings into understanding of the project.

---

## Routing

| Response | Action |
|----------|--------|
| "brief", "new project", "start" | Create brief |
| "roadmap", "phases" | Create roadmap |
| "phase", "plan phase", "next phase" | Plan phase |
| "chunk", "next tasks" | Plan chunk |
| "execute", "run", "do it" | Load execute-plans skill |
| "research", "investigate" | Create research prompt |
| "handoff", "pack up", "stopping" | Create handoff |
| "resume", "continue" | Load handoff |
| "transition", "complete", "done" | Mark phase complete |
| "milestone", "ship", "release" | Complete milestone |

---

## Execution Handoff

**When user says "execute", "run", "build it", "do it":**

Load the execute-plans skill to execute this plan autonomously.

The execute-plans skill uses intelligent orchestration:
- Analyzes task dependencies
- Spawns parallel subagents for independent tasks
- Spawns critic subagents at milestones for self-review
- Creates SUMMARY.md and commits when done

Do NOT re-invoke create-plans. Do NOT ask for guidance. Execute autonomously via execute-plans.

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

**Forgetting the human.** Some decisions need you. Mark them clearly: "Decision needed: [what] — options presented."

---

## Anti-Patterns

### ❌ 500-line mega-plan
A single PLAN.md that tries to cover 8 phases with 40 tasks is a compilation target, not a prompt. Claude degrades at ~50% context usage — the back half will be implemented poorly.

### ✅ Split into focused phases
Each plan: 2-3 tasks, ~15-60 min of work. Dependencies declared explicitly. Context stays under 40%.

### ❌ Vague task definitions
"Implement auth" has no verification, no scope, no exit criteria. Claude can't know when it's done.

### ✅ Concrete task anatomy
`Files: src/auth/login.ts + src/auth/register.ts` | `Action: Implement JWT login with refresh tokens` | `Verify: POST /api/auth/login returns 200 + sets HttpOnly cookie` | `Done: Login works, register works, refresh flow works`

### ❌ Missing deviation handling
A plan that doesn't account for discoveries will stop and ask for every exception.

### ✅ Embedded deviation rules
Auto-fix bugs, auto-add missing criticals, auto-fix blockers — all documented in the plan itself. Only ask about architectural changes.

---

## Reference Index

**Formats:** `references/plan-format.md`, `references/checkpoints.md`, `references/scope-estimation.md`
**Automation:** `references/cli-automation.md`
**Templates:** `templates/brief.md`, `templates/phase-prompt.md`, `templates/roadmap.md`, `templates/summary.md`
**Workflows:** `workflows/execute-phase.md`
**Milestones:** `references/milestone-management.md`
**Subagent Prompts:** `agents/explorer.md`, `agents/researcher.md`, `agents/architect.md`, `agents/implementer.md`, `agents/verifier.md`

---

## Domain Expertise (Not Included)

The original skill included a `domain_expertise` system that scanned `~/.claude/skills/expertise/` for domain-specific skills, used keyword inference to detect project types, and loaded expertise via pattern matching.

**This was excluded as over-engineered cruft:**

- Keyword inference is brittle and misses more than it hits
- Requires maintaining a parallel expertise directory structure
- The skill functions fine without it (graceful degradation exists)
- Simpler alternative: just ask the user "What type of project?"

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

## What Now?

After creating a plan, use AskUserQuestion to present next steps:

**Question:** What would you like to do with this plan?

**Options:**
- A: Execute this plan (recommended) — load execute-plans skill and autonomously orchestrate subagents
- B: Refine plan — suggest improvements based on review
- C: Create follow-up tasks — plan next chunk or phase
- D: Done for now

After user selection:
- If A: Invoke execute-plans skill with the plan path for autonomous execution
- If B: Present specific refinement suggestions as options
- If C: Route to chunk/phase planning
- If D: Acknowledge and stop