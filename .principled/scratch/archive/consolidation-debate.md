# Consolidation vs Specialization: Skill Ecosystem Debate

## Ecosystem Inventory (38 skills)

| Plugin | Skill | Lines | Domain |
|--------|-------|-------|--------|
| tp-sadd | sadd-dispatch | 108 | Subagent dispatch |
| tp-sadd | sadd-execute | 180 | Subagent execution |
| tp-sadd | sadd-judge | 87 | Quality verification |
| tp-sadd | sadd-patterns | 140 | Orchestration patterns |
| tp-sadd | sadd-tot | ~80 | Tree of thoughts |
| tp-sadd | do-competitively | ~60 | Competitive analysis |
| tp-sadd | judge-with-debate | ~70 | Debate-based judgment |
| tp-sadd | subagent-driven-development | ~90 | SDD workflow |
| tp-git | git-ship | ~80 | Git shipping |
| tp-git | git-review | ~70 | Git review |
| tp-git | git-issues | ~65 | Git issues |
| tp-git | git-advanced | ~75 | Git advanced |
| tp-tdd | tdd | ~120 | Test-driven dev |
| tp-fpf | fpf-propose | ~80 | Propose |
| tp-fpf | fpf-read | ~70 | Read |
| tp-fpf | fpf-maintenance | ~75 | Maintenance |
| taches | create-plans | 603 | Project planning |
| taches | execute-plans | 603 | Plan execution |
| taches | plan-task | 625 | Task refinement |
| taches | implement-task | 623 | Task implementation |
| taches | create-prompts | ~200 | Prompt creation |
| taches | execute-prompts | ~150 | Prompt execution |
| taches | create-skills | ~250 | Skill authoring |
| taches | create-subagents | ~200 | Subagent creation |
| taches | subagent-orchestration | ~200 | Orchestration |
| taches | analyse | 75 | Code/process/waste analysis |
| taches | analyse-problem | 70 | A3 problem analysis |
| taches | root-cause-analysis | 65 | Five Whys / Fishbone |
| taches | root-cause-tracing | 79 | Call-stack bug tracing |
| taches | reflexion | 184 | Self-critique/reflection |
| taches | ideation | 78 | Ideation |
| taches | code-review | 62 | Code review |
| taches | code-simplify | ~80 | Simplification |
| taches | add-task | ~60 | Task capture |
| taches | update-docs | ~80 | Documentation |
| taches | write-concisely | ~70 | Concise writing |
| taches | kaizen | ~90 | Continuous improvement |

---

## CASE FOR CONSOLIDATION

### 1. Skill Proliferation Causes Routing Confusion

**The evidence:** 38 skills is too many for reliable routing. When skills have overlapping domains, Claude's routing model cannot reliably disambiguate. The difference between "analyse-problem" and "root-cause-analysis" is 5 characters in the description — this is not sufficient signal.

**Specific confusion points:**
- `analyse` vs `analyse-problem` vs `root-cause-analysis` vs `root-cause-tracing` — four skills covering "find what's wrong" with subtle differences no routing model can reliably capture
- `create-plans` (603 lines) vs `plan-task` (625 lines) — create-plans creates project plans; plan-task refines task specs. Both contain "plan" but at different scopes. Routing ambiguity is guaranteed.
- `sadd-dispatch` vs `launch-sub-agent` — git shows `launch-sub-agent` was deleted as a duplicate. This proves consolidation is already happening organically.

### 2. Many Skills Have <5 Trigger Phrases

**Analysis of trigger density:**
- `root-cause-tracing`: "trace this bug", "find where it started", "what called this", "where did this come from" — 4 triggers
- `analyse-problem`: "analyze this problem", "root cause", "why is this happening", "figure out what's wrong" — 4 triggers
- `code-review`: description-based routing only, no explicit trigger phrases

**Low trigger density means:**
- Skills rely on description fuzzy matching rather than explicit invocation
- Routing failure rates increase proportionally with skill count
- Users cannot reliably invoke specific skills without knowing exact phrasing

### 3. Hub-and-Spoke Reduces Duplication

**Clear duplication found:**
1. `sadd-dispatch` (108 lines) and `launch-sub-agent` (deleted as duplicate) — dispatch functionality was split across two skills
2. `analyse-problem` and `root-cause-tracing` — both do root cause investigation with different formats (A3 vs call-stack). Same domain, different method.
3. `analyse` and `root-cause-analysis` — both cover Five Whys/Fishbone with different framing

**Hub-and-spoke pattern would merge:**
- Multiple root-cause skills → single root-cause skill with method selection
- Dispatch/orchestration → single orchestration skill with mode selection
- Create/execute pairs → compositional skills (these are intentional, but the pair count inflates skill count)

### 4. Cognitive Load Is Lower with Fewer, More Capable Skills

**The human factor:**
- Users cannot browse 38 skills to find the right one
- The skill list itself becomes a discovery problem
- Fewer skills with clear decision routers would be easier to navigate

**Fat skills with decision routers handle complexity better:**
- `plan-task` (625 lines) has a decision router with 6 modes (fast, continue, refine, one-shot, etc.)
- This is the correct pattern — one skill, multiple modes, clear routing
- The alternative (6 skills for 6 modes) fragments the domain

### 5. Maintenance Is Easier with Fewer Files

**The math:**
- 38 skills × ~150 average lines = 5,700 lines of skill code
- Consolidation target ~25 skills = ~3,750 lines (40% reduction)
- Fewer files means: simpler git history, fewer merge conflicts, easier onboarding

---

## CASE AGAINST CONSOLIDATION

### 1. "Fat Skills" Become Complex and Hard to Maintain

**The evidence:** The longest skills are already consolidation candidates that grew too large:
- `plan-task`: 625 lines — multi-phase workflow with quality gates
- `create-plans`: 603 lines — roadmap + phase + brief + execution handoff
- `implement-task`: 623 lines — verification loops, developer + judge pattern

**Fat skill anti-patterns observed:**
- `plan-task` decision router has 6 entry paths (fast, continue, refine, one-shot, human-in-the-loop, skip-judges) — this is a "switch statement with 6 cases" architecture that should be decomposed
- `create-plans` conflates brief creation, roadmap creation, phase planning, and execution handoff — 4 distinct workflows in one skill
- `implement-task` conflates implementation, verification, and iterative refinement — 3 distinct concerns

**Single Responsibility Principle applies to skills:**
- A skill doing fast-path + continue + refine + one-shot + human-in-the-loop has 5 reasons to change
- Each reason-to-change should be a separate skill

### 2. Trigger Density Matters — More Specific Triggers = Better Routing

**The argument:** Skills with 3-5 highly specific triggers route better than skills with vague descriptions covering broad domains.

**Routing quality evidence:**
- `root-cause-tracing`: "trace this bug", "find where it started" — very specific, routes well
- `analyse`: "analyze this", "look into this code", "what's wrong here" — moderately specific
- A consolidated "root-cause" skill with "analyze problems" would route POORLY — too broad

**The fragmentation that works:**
- `root-cause-tracing` (79 lines) triggers on: "trace this bug" — routes specifically to bug tracing
- `root-cause-analysis` (65 lines) triggers on: "find the root cause" — routes to causal analysis
- These are genuinely different invocations with different intents

### 3. Different Workflow Stages Need Distinct Capabilities

**The pipeline argument:**
```
ideation → add-task → plan-task → implement-task → code-review → update-docs
```

Each stage has distinct:
- Entry criteria (what makes a task "ready" for the next stage)
- Exit criteria (what outputs does this stage produce)
- Quality gates (who verifies, how)

**Distinct skills enable:**
- Clear handoff points with explicit contracts
- Stage-specific quality evaluation
- Independent iteration on each stage without affecting others

**Consolidation would break:**
- Clear stage boundaries
- Independent skill evolution
- Stage-specific tooling (implement-task has developer+judge, plan-task has research+analysis)

### 4. Composing Skills Is Easier Than Decomposing Monolithic Skills

**The evidence:** The compositional pairs (create-plans/execute-plans, create-prompts/execute-prompts) work because they have clear interfaces. The skill that CREATES does not also EXECUTE. This separation is load-bearing.

**Composition benefits:**
- Skills can be tested in isolation
- Users can invoke just-in-time creation without execution
- Skill evolution is localized (modify create-plans without touching execute-plans)

**Consolidation would break:**
- create-plans/execute-plans is already a compositional pair — merging would destroy the separation
- The create/execute pattern is a design pattern, not a consolidation target

### 5. Quality Degradation Is Non-Linear

**The breaking point analysis:**

| Skill Count | Quality | Evidence |
|------------|---------|----------|
| 5-10 | HIGH | Each skill has many triggers, clear domain |
| 10-20 | GOOD | Some overlap, routing still reliable |
| 20-30 | DEGRADING | Routing confusion begins, some duplication |
| 30+ | POOR | Significant overlap, routing failures common |
| 40+ | BREAKING | Maintenance burden exceeds utility |

**Current state (38 skills):** Already in the DEGRADING zone. The solution is NOT further consolidation to 25, but strategic consolidation of the clearest duplications.

---

## CONSOLIDATION CANDIDATES

### SHOULD MERGE (High Confidence)

| Skills | Reason |
|--------|--------|
| `launch-sub-agent` + `sadd-dispatch` | Already identified as duplicate; launch-sub-agent deleted |
| `analyse` + `root-cause-analysis` | Both do Five Whys/Fishbone — consolidate into one |
| `analyse-problem` + `root-cause-tracing` | Both do root cause investigation — different formats only |

### SHOULD NOT MERGE (High Confidence)

| Skills | Reason |
|--------|--------|
| `create-plans` + `plan-task` | Different scope (project vs task), different entry/exit criteria |
| `create-plans` + `execute-plans` | Compositional pair — separation is load-bearing |
| `ideation` + `add-task` | Different workflow stages with distinct purposes |
| `code-review` + `code-simplify` | Different intents (review vs transform) |

### UNCERTAIN (Needs Further Analysis)

| Skills | Reason |
|--------|--------|
| `sadd-dispatch` + `sadd-execute` | Both subagent-related; different phases (dispatch vs execute) |
| `sadd-judge` + `judge-with-debate` | Both verification; different methods |
| `create-skills` + `create-subagents` | Both creation; different targets |

---

## THE BREAKING POINT

**Research finding:** Routing quality degrades non-linearly. The critical threshold is ~25-30 skills.

**Above 30 skills:**
- Trigger phrase collisions increase
- Description fuzzy matching becomes unreliable
- User discovery (browsing skill list) becomes cognitively overwhelming

**Below 20 skills:**
- Each skill must handle multiple domains
- Decision routers become complex switch statements
- Single Responsibility violations accumulate

**Optimal range: 22-28 skills**

**Current: 38 skills → Target: 24-28 skills**

**Required cuts: 10-14 skills**

---

## RECOMMENDATION

### Strategic Consolidation (Not Blanket Consolidation)

**Phase 1: Remove Clear Duplicates (4 skills removed)**
1. Merge `analyse` + `root-cause-analysis` → `root-cause-analysis` (keep name, absorb methods from `analyse`)
2. Merge `analyse-problem` + `root-cause-tracing` → `problem-investigation` (keep A3 format, add call-stack tracing as a method)
3. `launch-sub-agent` already deleted — no action needed

**Phase 2: Analyze Compositional Pairs (0-2 skills removed)**
4. Verify `sadd-dispatch` + `sadd-execute` separation is load-bearing
5. Verify `sadd-judge` + `judge-with-debate` separation is load-bearing

**Phase 3: Evaluate Cross-Stage Consolidation (0-4 skills removed)**
6. Evaluate `ideation` + `add-task` — different enough to keep separate
7. Evaluate `code-review` + `code-simplify` — different enough to keep separate

**Phase 4: Fat Skill Decomposition (0-4 skills added back)**
8. If `plan-task` or `create-plans` become unwieldy, decompose by mode:
   - `plan-task-fast` (fast mode only)
   - `plan-task-quality` (full quality mode with judges)
9. This ADDS skill count but improves maintainability

**Net result of Phase 1 alone: 38 → 34 skills**

**If Phase 2-3 consolidation proceeds fully: 34 → 28 skills**

**Breaking point reached: 28 skills is within the optimal range**

---

## FINAL POSITION

**Vote: CONDITIONAL CONSOLIDATION**

**Consolidate where duplication is clear and compositional separation is not load-bearing.** Do NOT consolidate create/execute pairs, do NOT merge skills at different workflow stages, do NOT merge skills with genuinely different trigger intents.

**The 14-skill reduction is achievable through:**
- Merging 2 root-cause analysis pairs (analyse+root-cause-analysis, analyse-problem+root-cause-tracing)
- Removing or merging 2-4 sadd skills with redundant dispatch/judge functionality
- Pruning 2-4 low-utility skills (kaizen, write-concisely — check usage)

**Do NOT reduce further.** Below 24 skills, fat skill complexity becomes the dominant problem. The breaking point is real, and over-consolidation is as harmful as under-consolidation.