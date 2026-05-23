---
name: refine
description: "Quality improvement hub for code review, complexity reduction, and self-critique. Use when user says 'review this PR', 'check my changes', 'simplify this code', 'reduce complexity', 'reflect on this', or 'critique this work'."
when_to_use: |
  Use when the user says "review this PR", "check my changes", "simplify this code", "reduce complexity", "reflect on this", or "critique this work".
  IMMEDIATELY before merging or committing significant code changes (review).
  IMMEDIATELY when encountering functions over 40 lines, nesting beyond 3 levels, or duplicated code blocks (simplify).
  FIRST before any high-stakes shipping decision (critique).
  Do NOT use for architectural decisions (use create-plans) or greenfield development (use create-plans).
argument-hint: "[mode] [focus-area] [--min-impact critical|high|medium|medium-low|low]"
---

## Decision Router

IF user says "review", "PR", "pull request", "check my changes", "audit", or names a PR number → **REVIEW** mode
IF user says "simplify", "clean up", "reduce complexity", "too nested", or describes high cognitive load → **SIMPLIFY** mode
IF user says "reflect", "critique", "what could be better", "self-review", or asks to review completed work → **CRITIQUE** mode
IF ambiguous → ask: "Would you like to review for issues, simplify for clarity, or critique the approach?"

# Refine

Quality improvement hub combining code review, complexity reduction, and self-critique into a unified skill. Three modes address different quality dimensions:

| Mode | Purpose | Best For |
|------|---------|----------|
| **REVIEW** | Multi-agent scanning for bugs, security, quality | PRs, local changes, pre-commit checks |
| **SIMPLIFY** | Cognitive load reduction through refactoring | Complex functions, deep nesting, duplication |
| **CRITIQUE** | Severity-rated self-critique with evidence | Completed work, high-stakes decisions |

---

## REVIEW Mode

Multi-agent code review that scans for bugs, security vulnerabilities, code quality issues, contract violations, and test coverage gaps. Uses 6 specialized review agents running in parallel, with progressive confidence scoring and impact-based filtering.

### Capability Routing

Six specialized agents run in parallel. Each focuses on a distinct dimension:

| Agent | Focus Area | Key Questions It Answers |
|-------|------------|------------------------|
| **Bug Hunter** | Logic errors, edge cases, race conditions, systemic gaps | Where did the invalid data originate? What architectural gap enabled this? How would this fail under load? |
| **Security Auditor** | OWASP Top 10, auth, injection, secrets exposure, attack vectors | Can this be exploited? What would an attacker do? Does this fail closed or open? |
| **Code Quality Reviewer** | Readability, complexity, naming, duplication, project conventions | Does this follow established patterns? Is the solution simple enough? Would future developers understand this? |
| **Contracts Reviewer** | API contracts, data models, type design, breaking changes | Can illegal states be represented? Are invariants protected? Will this break existing consumers? |
| **Historical Context Reviewer** | Git history, past PRs, recurring patterns, known anti-patterns | What problems occurred before in these files? Have we solved this pattern before? |
| **Test Coverage Reviewer** | Missing tests, untested edge cases, behavioral coverage | What error paths are untested? What regressions could occur? Would this test catch the bug we found? |

### Shared Review Process

#### Phase 1: Preparation
1. Identify the change set (git diff or PR diff)
2. Read instruction files if present in `.claude/` or `CLAUDE.md`
3. Check review scope against `--min-impact` threshold

#### Phase 2: Multi-Agent Issue Detection
Spawn applicable review agents in parallel. Each produces issues with:
- **Impact score**: 0-100 mapped to critical (81-100), high (61-80), medium (41-60), medium-low (21-40), low (0-20)
- **Confidence**: confidence-scored signal with filterable threshold
- **Evidence**: specific file:line references

Progressive confidence threshold: low-confidence findings are included but marked as such. No automated filtering — the user sees everything with confidence indicators.

#### Phase 3: Consolidation
1. Deduplicate by file:line:issue-text
2. Filter to `--min-impact` threshold (default: high)
3. Skip if change set >500 lines (focus on architecture + security only)

### PR Review — Environment-Specific

**Eligibility check**: Skip closed/draft PRs, check PR has description (add one if missing), discover instruction files from base branch.
**Output**: Post inline comments on PR diff with emoji severity indicators. Use MCP GitHub tools when available, fall back to gh API.

### Local Changes Review — Environment-Specific

**Diff source**: Run `git status --short` to identify changed files, differentiate staged vs. unstaged, take action accordingly.
**Output**: Terminal report with quality gate (PASS/FAIL) determined by issue count vs. threshold. JSON output with `--json` flag.

---

## SIMPLIFY Mode

Refactors complex code to reduce cognitive load. Targets specific failure modes that make codebases hard to maintain over time.

### Decision Router

IF the code compiles and passes tests:
  -> Proceed with simplification. You have a safety net.
IF there are NO tests:
  -> Read the "Simplify Without Tests" section below. Do NOT refactor without reading it.
IF you are refactoring risky code (state machines, async chains, crypto, parsing):
  -> Use Opus via the agent template below. Default is Sonnet.
IF the code is in active development by others:
  -> Stop. Simplification conflicts with churn. Note the tech debt and move on.
IF this is a one-person project or abandoned code:
  -> Full speed. Simplify aggressively as long as readability improves.

### What This Adds (Delta Principle)

Claude already refactors on request. This skill changes *when* and *how* it simplifies, targeting the specific failure modes that make codebases hard to maintain over time.

| Default Claude Behavior | This Skill's Behavior |
|---|---|
| Refactors when asked, limited by conversation context | Actively *seeks* simplification opportunities during any code visit |
| Treats all code equally | Applies numeric thresholds to target only high-cognitive-load code |
| May introduce abstractions prematurely | Bias toward monoliths — extract only when proven necessary |
| No systematic pipeline — simplifies opportunistically | 5-stage pipeline guarantees consistent output |
| No guardrails for untested code | Exception rules for untested code with safety-first defaults |

### Core Principle

**Simplification is refactoring that reduces cognitive load.** If the change does not make the code easier to hold in working memory, it is not simplification — it is rearrangement. Judge every transformation against this single criterion.

### The 5-Stage Simplification Pipeline

Run these stages in order. Each stage feeds the next. Stop when the code meets the thresholds in the table below.

#### 1. Extract and Name

Identify anonymous blocks, magic values, inline conditionals, and bare literals. Give each a name that captures intent.

```
# Before
if x > 86400: process_later()

# After
SECONDS_IN_DAY = 86400
if elapsed > SECONDS_IN_DAY: process_later()
```

**Rule of thumb:** If you have to read the body to understand a value or block, extract and name it.

#### 2. Reduce Nesting

Flatten conditionals with early returns, guard clauses, and inversion. Max 3 levels of nesting (see Thresholds table).

```
# Before
if user:
    if user.is_active:
        if user.has_permission("edit"):
            do_edit()

# After
if not user or not user.is_active:
    return
if not user.has_permission("edit"):
    return
do_edit()
```

#### 3. Remove Duplication

Consolidate repeated patterns. Extract to a named function or data-driven loop. Do NOT extract when the duplication is coincidental (same text, different semantics).

#### 4. Eliminate Dead Code

Remove commented-out code, unreachable branches, unused variables, unused imports, and unreachable functions. Commenting-out is not version control — git handles history.

#### 5. Replace State Machines with Data

When a chain of if/elif or match/case branches over a single enum or string, replace with a lookup table (dict, map, configuration object). If the branching involves side effects, extract the side effects into functions stored in the table.

### When to Simplify vs Leave Alone

| Situation | Decision | Rationale |
|---|---|---|
| Function >40 lines | Simplify | Exceeds working-memory capacity; extract cohesive subgroups |
| Nesting >3 levels | Simplify | Each level adds a mental stack frame |
| Duplication >3 copies | Simplify | Maintainability debt; extract or parameterize |
| Active development churn | Leave alone | Simplification conflicts with ongoing edits |
| Serialization / data mapping | Leave alone | Often necessarily verbose; clarity suffers from extraction |
| Hot path / tight loop | Simplify carefully | Keep extracted, but verify no perf regression |
| Code you don't fully understand | Investigate first | Simplifying misunderstood code creates bugs |
| Single-use glue / adapter code | Leave alone | Indirection for its own sake increases cognitive load |

### Simplify Without Tests

When a project has no tests, simplification carries risk. Follow these rules in order:

1. **Prefer moves over changes.** Rename variables, extract constants, add whitespace. These are semantics-preserving and safe.
2. **Restrict to 1-level extractions.** Extract a block, but do not change control flow. Guard clauses are higher risk without tests.
3. **Never inline.** Consolidating duplicated code without tests is acceptable only if you can manually trace every path. When in doubt, leave duplication and note the tech debt.
4. **Mark every change with `# SIMPLIFY: <reason>`** so the next reader (or a test-writer) can verify intent.
5. **Dead-code removal is always safe** if reachability is proven statically. Remove commented-out code unconditionally — tests do not test comments.

### Numeric Thresholds

Thresholds are guides, not laws. If a function serves as a crucial business-rule with high complexity that is *inherent*, document the decision and leave it. If the complexity is *accidental*, simplify.

| Metric | Threshold | Action |
|---|---|---|
| Function length | >40 lines | Extract cohesive subgroups |
| Nesting depth | >3 levels | Guard clauses, early returns |
| Parameters | >5 | Bundle into config object |
| Boolean flags in params | >=2 | Split function or use enum |
| Duplicate blocks | >=3 occurrences | Extract or parameterize |
| Comments explaining "what" (not "why") | Any | Extract to named function; the name replaces the comment |
| Variables reassigned | >3 times in same scope | Split into smaller functions |
| Chained method calls | >4 | Extract intermediates with named variables |

### Anti-Patterns

Each anti-pattern shows the wrong approach, the right approach, and the consequence of getting it wrong.

#### 1. Extracting for extraction's sake

**Wrong:** Splitting a 50-line function into 5 ten-line functions, each called once.
**Right:** Extract only when the extracted block has a clear identity and can be named.
**Consequence:** Indirection without abstraction. The reader must jump between files to trace logic. Cognitive load *increases*.

#### 2. Renaming during extraction

**Wrong:** Renaming variables, extracting functions, and changing control flow in the same pass.
**Right:** One transformation per commit. Extract first, rename in a separate change.
**Consequence:** Bugs become untraceable. If a test fails, you cannot tell which transformation caused it.

#### 3. Removing "unnecessary" error handling

**Wrong:** Removing a null check because "the caller never passes null."
**Right:** Keep defensive checks unless you can prove the type system enforces the invariant. If the language lacks non-null types, keep the check.
**Consequence:** Latent production bugs. The null check existed because someone — maybe the original author — learned the hard way.

#### 4. Over-normalizing data transformations

**Wrong:** Replacing a readable single-use loop with `itertools.groupby`, `functools.reduce`, or a chain of list comprehensions.
**Right:** Use comprehensions for simple maps/filters. Leave loops for complex multi-step transformations. Readability is the metric.
**Consequence:** The simplification becomes harder to read than the original. You have introduced a puzzle, not a solution.

#### 5. Flattening with boolean flags

**Wrong:** Replacing nested conditionals with a single flat block gated by `should_process = all(conditions)` — the flags now encode the original nesting implicitly.
**Right:** Early returns for each condition. Each guard is self-documenting.
**Consequence:** Debugging requires evaluating the boolean composition mentally. The work of understanding the nesting is replaced by the work of understanding the boolean algebra.

#### 6. Inlining too aggressively

**Wrong:** Inlining a helper that is called in 3 places but has different semantics in each call site. The duplication was coincidental, not structural.
**Right:** Only inline when the extracted code is called in one place or the call sites are semantically identical.
**Consequence:** A seemingly safe refactor introduces subtle semantic differences. The code passes tests but fails at runtime under edge cases.

#### 7. Optimizing before simplifying

**Wrong:** Replacing a naive loop with a cached/generator/deferred version during the simplification pass.
**Right:** Simplify first. Profile second. Optimize third. Only if the profile says it matters.
**Consequence:** Premature optimization creates complex code that is harder to simplify later. You have increased cognitive load for hypothetical performance gains.

#### 8. Leaving dead code as "documentation"

**Wrong:** Keeping commented-out blocks "in case someone needs to see the old version."
**Right:** Git history is the record. Delete commented-out code unconditionally.
**Consequence:** Readers waste mental cycles determining whether commented code is relevant. The file grows without benefit. Signal-to-noise ratio degrades over time.

### Agent Template

Use this template when delegating simplification to a subagent. Copy the full block and fill in the bracketed fields.

#### Role

You are a code simplification agent. Your sole purpose is to reduce cognitive load in the target code — not add features, not optimize performance, not fix bugs (unless a bug is blocking simplification).

#### Approach

Apply the 5-stage Simplification Pipeline in order: Extract and Name, Reduce Nesting, Remove Duplication, Eliminate Dead Code, Replace State Machines with Data. Do not skip stages. Do not reorder them. Do not combine stages in a single pass.

#### Focus Areas

- Functions exceeding 40 lines
- Nesting exceeding 3 levels
- Duplicate blocks appearing 3+ times
- Dead code (commented-out, unreachable, unused)
- If/elif chains over an enum or string that can be replaced with a lookup table
- Boolean flag parameters (any function with 2+ bool params needs splitting)

#### Output Format

You must produce exactly one file per modified source file: a diff in unified format. Place each diff in `.claude/artifacts/{task_id}-{filename}.diff`. Do not apply changes directly unless the orchestrator explicitly approves.

For each diff, include a summary line:
- Lines before / after
- Which pipeline stages were applied
- Whether tests exist and were run

#### Model Selection

- **Default:** Sonnet. Fast, good judgment for routine extraction and flattening.
- **Risky code (state machines, async chains, crypto, parsing, lock/unlock sequences):** Opus. The cost premium is justified by correctness guarantees.
- **Dead-code removal:** Any model. Statically provable reachability does not require advanced reasoning.

Switch models by re-spawning the subagent with the appropriate model pin. Do not downgrade mid-task.

#### Constraints

- Never combine pipeline stages in a single pass. Each stage is its own commit or diff.
- Never rename variables in the same pass as extraction. One transformation per pass.
- Never inline a helper used in 3+ places unless all call sites are semantically identical.
- Never remove a defensive null check without compiler-enforced non-null guarantees.
- Never add abstractions (classes, patterns) that do not exist in the original code. Simplify within the existing paradigm.
- Stop and report after 2 successive failures on the same transformation. Do not retry with different prompts.

#### Failure Signal

If the subagent encounters any of these conditions, it must stop and report immediately — do not attempt recovery:

1. The target file does not match the described content (wrong branch, stale description).
2. The code does not compile or has failing tests before any change.
3. The simplification would require changing a public API signature.
4. The target file is generated code or a vendored dependency (undo any edits instantly).

### Scope Policy

This skill applies to **any code file you read or edit**, regardless of language. Simplification is a cross-cutting concern — it is not restricted to a specific directory or module. When you encounter code exceeding any numeric threshold, evaluate whether to simplify now or leave a marker.

The scope expands to **imported dependencies only when tracing call paths**. You may read a dependency's source to understand a function, but you must NOT modify it.

### Boundary Policy

Do NOT simplify:

- Generated code (protobuf, OpenAPI stubs, parser generators, etc.). Machine-written code resists human readability patterns.
- Vendored or third-party dependencies. The original form is authoritative; local patches diverge on update.
- Configuration files (YAML, JSON, TOML). Config is declarative — there is no cognitive load to reduce.
- Test files beyond readability normalization. Tests benefit from explicitness; over-extraction makes failures harder to diagnose.
- Migration or data-munging scripts intended for single use. They will be deleted, not maintained.

### Success Criteria

A simplification pass is complete when ALL of the following are true:

1. **Cognitive load reduced:** The target code has fewer lines, fewer nesting levels, or fewer duplicate blocks than before. If none of these changed, the pass did nothing — revert.
2. **Tests pass:** The existing test suite (unit, integration, snapshot) produces identical results before and after. If no tests exist, verify with the "Simplify Without Tests" rules.
3. **No behavior change:** The simplification does not alter return values, side effects, error paths, or observable behavior. If behavior changed, it was a bug fix, not a simplification — revert and separate.
4. **Each stage isolated:** A reviewer can inspect each stage's output independently. If stages are mixed, the diff is opaque — redo.
5. **Thresholds met:** Every remaining function is at or below the numeric thresholds, OR each exception is documented with an inline comment explaining why the complexity is inherent, not accidental.

---

## CRITIQUE Mode

Self-critique for completed work with severity-rated findings. You are a ruthless quality gatekeeper — your value is measured by what you prevent from shipping broken. Approval must be earned through evidence.

### Complexity Triage

| Complexity | Signal | Depth |
|------------|--------|-------|
| Quick (< 50 lines, known pattern) | Single file, straightforward | Surface check: correctness, completeness |
| Standard (50-200 lines, multi-step) | Some abstraction or indirection | Full framework: logic, edge cases, design |
| Deep (200+ lines, novel pattern) | Hard to verify correctness | Deep audit: invariants, assumptions, alternatives |

**Quick path** — Skip to final verification. Simple corrections do not need full reflection.
**Standard path** — Target confidence >4.0/5.0.
**Deep path** — Target confidence >4.5/5.0. Consider alternative approaches.

### Process

1. **Initial Assessment** — Evaluate completeness, quality, correctness, and dependency verification for any addition/deletion/modification
2. **Evidence-Based Critique** — For each issue: state the problem specifically, explain why it matters (consequence of shipping), rate severity (critical/high/medium/low), suggest the fix without implementing it
3. **Fact-Checking** — Verify performance claims (benchmarking or Big-O), technical facts (official docs), security assertions (OWASP or equivalent), best practice claims (authoritative source)
4. **Decision Point** — Approve (all critical/high addressed), Request changes (issues identified, should not ship as-is), or Reject (fundamental problems, needs redesign)

### Scoring Scale

| Score | Meaning | Frequency |
|-------|---------|-----------|
| 1 | Unacceptable — fundamental failures | Rare |
| 2 | Below average — multiple issues | Common for first attempts |
| 3 | Adequate — meets basic requirements | Refined work lands here |
| 4 | Good — meets ALL requirements, minor issues | Genuinely solid work |
| 5 | Excellent — exceeds requirements, exemplary | < 5% of evaluations |

Default score is 2. Justify any upward deviation with evidence.

### Bias Countermeasures

You are programmed to be lenient. Fight your nature. These biases corrupt judgment:

| Bias | How It Distorts You | Countermeasure |
|------|---------------------|----------------|
| **Sycophancy** | Wanting to say nice things | Praise is forbidden. Your job is rejection. |
| **Length bias** | Long output = impressive | Penalize verbosity. Concise beats lengthy every time. |
| **Authority bias** | Confident tone = correct | Verify every claim. Confidence is evidence of nothing. |
| **Completion bias** | Finished = good | Completion equals nothing. Garbage can be complete. |
| **Effort bias** | Hard work = merit | Effort is irrelevant. Judge output, not input. |
| **Recency bias** | New patterns = better | Established patterns exist for good reasons. |
| **Familiarity bias** | Seen it before = good | Common is not correct. |

### Fact-Checking

Verify claims before declaring complete. Ask:

1. **Performance claims** — benchmarking data or Big-O analysis? Claims like "X% faster" need measurement, not assertion.
2. **Technical facts** — official documentation cited? API capabilities, version compatibility, framework requirements must reference current docs.
3. **Security assertions** — OWASP or equivalent standards? Vulnerability claims need proof through testing or recognized standards.
4. **Best practice claims** — authoritative source named? "Industry standard" is not a citation.

Red flags: absolute statements ("always", "never"), superlatives ("fastest", "most secure"), specific numbers without context.

### Output Format

```markdown
## Critique: {scope}
**Verdict**: {Approve/Changes Needed/Reject}
**Confidence**: {score}/5.0 — {High/Medium/Low}

### Issues Found
- {severity}: {issue} → {suggestion}

### Verified Claims
- {claim} ← {evidence source}

### Summary
{One-paragraph assessment}
```

## Failure Signal

```json
{"status": "failed" | "success", "reason": "...", "completed_portion": "...", "retry_possible": true/false}
```

| status | reason | completed_portion | retry_possible |
|--------|--------|-------------------|----------------|
| `failed` | `review-inconclusive` | Multiple conflicting issues found | `false` (present findings to user) |
| `failed` | `simplification-loop` | 3+ retries without quality improvement | `true` (accept current state) |
| `failed` | `verification-failed` | Tests/lint fail after simplification | `true` (rollback and escalate) |
| `failed` | `critique-conflict` | Judges disagree on verdict after debate | `false` (present disagreements) |
| `failed` | `scope-overflow` | Task too large for single pass | `true` (decompose into smaller units) |
| `failed` | `self-critique-loop` | Infinite refinement without convergence | `true` (set max iterations) |

**Fields:**
- `status`: `"failed"` when quality improvement cannot complete; `"success"` when improvement achieved or accepted
- `reason`: Specific failure mode from the options above
- `completed_portion`: What was reviewed/improved before failure
- `retry_possible`: `true` if recoverable with different approach; `false` if needs user decision