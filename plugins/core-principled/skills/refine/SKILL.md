---
name: refine
description: "Improve artifact quality through code simplification, structured critique, prose polishing, and memory consolidation."
allowed-tools: Read, Edit, Write
when_to_use: "Use for PR reviews, simplifying complex logic, or capturing project learnings. Do NOT use for bug diagnosis (use diagnose) or creating new features (use task-lifecycle)."
argument-hint: "[mode] [focus-area] [--min-impact critical|high|medium|medium-low|low]"
---

## Routing Guidance

- IMMEDIATELY before merging or committing significant code changes (SIMPLIFY or REVIEW).
- IMMEDIATELY when encountering functions over 40 lines, nesting beyond 3 levels, or duplicated code blocks (SIMPLIFY).
- IMMEDIATELY after completing significant work needing independent quality verification (CRITIQUE).
- IMMEDIATELY when producing documentation, READMEs, or human-readable text (POLISH).
- When consolidating reflection or critique findings into durable project memory (MEMORIZE).
- Do NOT use for architectural decisions or greenfield development — use `create-plans` instead.
- CONTRAST with update-docs: that updates existing docs; this improves prose quality (POLISH).
- CONTRAST with ddd: refine improves quality of existing artifacts (present, corrective); ddd performs structural analysis (architecture, quality, transparency, API). Use refine when the issue is known and needs fixing; use ddd when a specific structural question surfaces.
- CONTRAST with kaizen: refine is on-demand quality improvement; kaizen provides continuous guardrails. Use refine after completing work; use kaizen during every code decision.
- CONTRAST with sadd JUDGE: refine provides severity-rated self-critique with single review; sadd JUDGE provides multi-judge competitive evaluation with debate rounds. Use refine for standard quality checks; use sadd for high-stakes decisions needing independent consensus.

## Decision Router

IF user says "simplify", "clean up", "reduce complexity", "too nested", or describes high cognitive load → **SIMPLIFY** mode
IF user says "post", "comment", "add inline", or asks to "post review" → delegate to git REVIEW
IF user says "review", "PR", "pull request", "check my changes", "audit", or names a PR number → **REVIEW** mode (simplify with PR-specific workflow)
IF user says "critique", "what could be better", "reflect", or asks to review completed work → **CRITIQUE** mode
IF user says "capture this learning", "remember this", or wants learnings persisted → **MEMORIZE** mode
IF user says "make this clearer", "write more concisely", "clean up text", "improve the writing", or "fix the prose" → **POLISH** mode
IF ambiguous → ask: "Would you like to simplify code, critique the approach, memorize learnings, or polish the prose?"

# Refine

Quality improvement hub with four modes targeting different quality dimensions:

| Mode | Purpose | Best For |
|------|---------|----------|
| **SIMPLIFY** | Cognitive load reduction through refactoring | Complex functions, deep nesting, duplication |
| **REVIEW** | Multi-agent scanning for bugs, security, quality | PRs, local changes, pre-commit checks |
| **CRITIQUE** | Severity-rated self-critique and multi-judge consensus | Completed work, high-stakes decisions |
| **MEMORIZE** | Learning capture into project memory | Insights, patterns, rules from sessions |
| **POLISH** | Prose clarity and conciseness per Strunk & White | Documentation, READMEs, comments |

---

## SIMPLIFY Mode

Refactors complex code to reduce cognitive load. Targets specific failure modes that make codebases hard to maintain over time.

### Decision Router

IF the code compiles and passes tests:
  -> Proceed with simplification. You have a safety net.
IF there are NO tests:
  -> Read the "Simplify Without Tests" section below. Do NOT refactor without reading it.
IF refactoring risky code (state machines, async chains, crypto, parsing):
  -> Use Opus via the agent template below. Default is Sonnet.
IF the code is in active development by others:
  -> Stop. Simplification conflicts with churn. Note the tech debt and move on.
IF one-person project or abandoned code:
  -> Full speed. Simplify aggressively as long as readability improves.

### Core Principle

**Simplification is refactoring that reduces cognitive load.** If the change does not make the code easier to hold in working memory, it is not simplification — it is rearrangement. Judge every transformation against this single criterion.

### The 5-Stage Simplification Pipeline

Run these stages in order. Each stage feeds the next. Stop when the code meets the thresholds.

#### 1. Extract and Name

Identify anonymous blocks, magic values, inline conditionals, and bare literals. Give each a name that captures intent.

#### 2. Reduce Nesting

Flatten conditionals with early returns, guard clauses, and inversion. Max 3 levels of nesting.

#### 3. Remove Duplication

Consolidate repeated patterns. Extract to a named function or data-driven loop. Do NOT extract when the duplication is coincidental.

#### 4. Eliminate Dead Code

Remove commented-out code, unreachable branches, unused variables, unused imports. Git handles history — commenting is not version control.

#### 5. Replace State Machines with Data

When a chain of if/elif or match/case branches over a single enum or string, replace with a lookup table.

### When to Simplify vs Leave Alone

| Situation | Decision |
|-----------|----------|
| Function >40 lines | Simplify |
| Nesting >3 levels | Simplify |
| Duplication >3 copies | Simplify |
| Active development churn | Leave alone |
| Serialization / data mapping | Leave alone |
| Hot path / tight loop | Simplify carefully |
| Code you don't fully understand | Investigate first |

### Simplify Without Tests

1. **Prefer moves over changes.** Rename variables, extract constants. These are semantics-preserving.
2. **Restrict to 1-level extractions.** Extract a block, but do not change control flow.
3. **Never inline.** Consolidating without tests is risky — leave duplication and note the tech debt.
4. **Mark every change with `# SIMPLIFY: <reason>`** for future verification.
5. **Dead-code removal is always safe** if reachability is proven statically.

### Numeric Thresholds

| Metric | Threshold | Action |
|--------|-----------|--------|
| Function length | >40 lines | Extract cohesive subgroups |
| Nesting depth | >3 levels | Guard clauses, early returns |
| Parameters | >5 | Bundle into config object |
| Boolean flags in params | >=2 | Split function or use enum |
| Duplicate blocks | >=3 occurrences | Extract or parameterize |
| Variables reassigned | >3 times | Split into smaller functions |

### Anti-Patterns

| Wrong | Right | Consequence |
|-------|-------|-------------|
| Splitting a 50-line function into 5 ten-line functions called once | Extract only when the block has a clear identity | Indirection without abstraction increases cognitive load |
| Renaming during extraction | One transformation per commit | Bugs become untraceable |
| Removing "unnecessary" null checks | Keep defensive checks unless type system enforces | Latent production bugs |
| Over-normalizing with reduce/chains | Use comprehensions for simple maps/filters | The simplification becomes harder to read |
| Flattening with boolean flags | Early returns for each condition | Debugging requires evaluating boolean algebra mentally |
| Inlining a helper used in 3 places with different semantics | Only inline when call sites are semantically identical | Subtle semantic differences pass tests but fail at runtime |
| Optimizing before simplifying | Simplify first, profile second, optimize third | Premature optimization creates complex code |
| Leaving dead code as "documentation" | Git history is the record — delete | Signal-to-noise ratio degrades |

### Boundary Policy

Do NOT simplify:
- Generated code (protobuf, OpenAPI stubs, parser generators)
- Vendored or third-party dependencies
- Configuration files (YAML, JSON, TOML)
- Test files beyond readability normalization
- Single-use migration or data-munging scripts

---

## REVIEW Mode

Multi-agent code review that scans for bugs, security vulnerabilities, code quality issues, contract violations, and test coverage gaps. Uses 6 specialized review agents running in parallel.

### Agent Spawning

Spawn all six reviewers in parallel. Each agent focuses on a distinct dimension:

1. **Spawn `tp-bug-hunter`** (red) — Logic errors, edge cases, race conditions, null pointer risks, state corruption. Key question: "Where did invalid data originate? How would this fail under load?"
2. **Spawn `tp-security-reviewer`** (red) — OWASP Top 10, injection, auth, exposed secrets, insecure crypto. Key question: "Can this be exploited? Does this fail closed or open?"
3. **Spawn `tp-code-quality-reviewer`** (yellow) — Readability, complexity, naming, duplication, pattern adherence. Key question: "Does this follow established patterns? Is the solution simple enough?"
4. **Spawn `tp-contracts-reviewer`** (yellow) — API contracts, data models, type design, illegal state representability. Key question: "Can illegal states be represented? Will this break existing consumers?"
5. **Spawn `tp-historical-reviewer`** (yellow) — Git history, past PRs, recurring bug patterns. Key question: "What problems occurred before in these files?"
6. **Spawn `tp-test-coverage-reviewer`** (yellow) — Missing tests, untested edge cases, coverage gaps. Key question: "Would this test catch the bug we found? What error paths are untested?"

### Process

1. **Preparation** — Identify change set (git diff or PR diff), check review scope against `--min-impact`
2. **Multi-Agent Issue Detection** — Spawn applicable review agents in parallel. Each produces issues with impact score (0-100), confidence, and evidence (file:line)
3. **Consolidation** — Deduplicate by file:line:issue-text, filter to threshold, skip if >500 lines (focus on architecture + security)

### PR Review

Post inline comments on PR diff with emoji severity indicators. Skip closed/draft PRs. Use MCP GitHub tools when available.

### Local Changes Review

Terminal report with PASS/FAIL quality gate. JSON output with `--json` flag.

---

## CRITIQUE Mode

Self-critique with severity-rated findings AND multi-judge consensus for high-stakes decisions. Two paths:

### Path 1: Self-Critique (for in-progress work)

Severity-rated critique without independent judges.

#### Complexity Triage

| Complexity | Signal | Depth |
|------------|--------|-------|
| Quick (<50 lines) | Single file, straightforward | Surface check |
| Standard (50-200 lines) | Some abstraction or indirection | Full framework |
| Deep (200+ lines) | Hard to verify correctness | Deep audit |

#### Process

1. **Initial Assessment** — Evaluate completeness, quality, correctness, dependency verification
2. **Evidence-Based Critique** — State the problem, explain consequence, rate severity, suggest the fix
3. **Fact-Checking** — Verify performance claims, technical facts, security assertions, best practice claims
4. **Decision** — Approve, Request changes, or Reject

#### Scoring Scale

| Score | Meaning |
|-------|---------|
| 1 | Unacceptable — fundamental failures |
| 2 | Below average — multiple issues |
| 3 | Adequate — meets basic requirements |
| 4 | Good — meets ALL requirements, minor issues |
| 5 | Excellent — exceeds requirements |

Default score is 2. Justify any upward deviation with evidence.

#### Bias Countermeasures

| Bias | How It Distorts You | Countermeasure |
|------|-------------------|----------------|
| **Sycophancy** | Wanting to say nice things | Praise is forbidden. Your job is rejection. |
| **Length bias** | Long output = impressive | Penalize verbosity. Concise beats lengthy. |
| **Authority bias** | Confident tone = correct | Verify every claim. Confidence is evidence of nothing. |
| **Completion bias** | Finished = good | Completion equals nothing. |
| **Effort bias** | Hard work = merit | Judge output, not input. |

### Path 2: Multi-Judge Critique (for high-stakes work)

Independent judges with cross-examination and consensus.

#### Process

1. **Context Gathering** — Identify scope, capture requirements, modified files, decisions, constraints
2. **Independent Judge Reviews** — Spawn 2-3 judges simultaneously:

| Role | Evaluates | Best For |
|------|-----------|----------|
| Requirements Validator | Alignment with original requirements | Feature implementation |
| Solution Architect | Technical approach and design decisions | Architecture changes |
| Code Quality Reviewer | Implementation quality and refactoring | Code changes |

3. **Cross-Examination & Consensus** — Synthesize: agreement areas, contradictions, gaps. If disagreement, facilitate debate.
4. **Report** — Structured findings with quality score, prioritized issues, consensus/debate areas, action items, verdict.

#### Output Format

```markdown
## Critique Report: {scope}
**Overall Quality Score**: {average}/10

### Executive Summary
{2-3 sentence assessment}

### Issues (Prioritized)
- Critical: {issues needing immediate attention}
- High: {important but not blocking}
- Medium: {nice to have}
- Low: {minor polish}

### Consensus Areas
- {finding supported by 2+ judges}

### Debate Areas
- {topic}: {perspective A} vs {perspective B} → {resolution}

### Action Items
- Must do: {critical items}
- Should do: {high priority}
- Could do: {medium priority}

### Verdict
Ready to ship | Needs improvements | Requires significant rework
```

---

## MEMORIZE Mode

Curate insights from reflection and critique into project memory so learnings persist across sessions.

**CONTRAST — same memory, different scope:** project-maintenance PLAN-ARCHIVE extracts plan-specific learnings to `.principled/memory/learnings.md`; MEMORIZE captures general session insights into the same file. Both project-maintenance PLAN-ARCHIVE and MEMORIZE are writers; rules-orchestration SYNC is the reader that promotes their entries into committed rules.

### Process

1. **Harvest** — Extract insights by type:
   - Error/Gap → root cause and imperative rule
   - Success pattern → when to apply, preconditions, limits
   - API/Tool rule → exact usage, gotchas, error handling
   - Verification item → concrete check to catch regression
   - Anti-pattern → what to avoid and why

   Categorize by impact: Critical, High, Medium, Low.

2. **Curate** — Apply grow-and-refine: Relevance (recurring tasks only), Non-redundancy (merge or skip duplicates), Atomicity (one idea per bullet), Verifiability (link evidence), Stability (prefer strategies valid over time). **Merge, don't append**.

3. **Update** — Read current project memory. Place insights into appropriate sections (project context, quality standards, architecture decisions, development guidelines). Preserve all existing material.

4. **Validate** — No contradictions, immediately actionable, no near-duplicates, evidence-backed.

### Options

Use `--dry-run` to preview without writing. Specify source (last, selection) or `--max=N` to limit bullet count.

---

## POLISH Mode

Apply Strunk & White's *Elements of Style* principles to any text a human will read. Claude already knows these rules — this skill triggers their application.

### Principles of Composition

1. **Use the active voice** — more direct and vigorous than passive
2. **Put statements in positive form** — say what is, not what isn't
3. **Use definite, specific, concrete language** — prefer specifics to generalities
4. **Omit needless words** — every word must tell
5. **Keep related words together** — position shows relationship
6. **Place emphatic words at the end** — the end is the position of prominence
7. **Use parallel construction** — coordinate ideas in similar form
8. **One paragraph per topic** — begin with a topic sentence

### Application

When writing documentation, run through each principle mentally:
1. Scan for passive voice — rewrite to active
2. Scan for "there is/are" — replace with stronger verb
3. Scan for negative statements — replace with positive form
4. Scan for wordy phrases — replace with concise equivalents
5. Scan for vague language — replace with concrete specifics

Do not enumerate which rules you applied. Simply produce cleaner text.

### Design Decision

Claude already knows these rules from training. The skill's only job is to trigger their application. Full rule text wastes context and adds no behavioral change.

---

## Failure Signal

```json
{"status": "failed" | "success", "reason": "...", "completed_portion": "...", "retry_possible": true/false}
```

| status | reason | retry_possible |
|--------|--------|----------------|
| `failed` | `review-inconclusive` | `false` |
| `failed` | `simplification-loop` | `true` |
| `failed` | `verification-failed` | `true` |
| `failed` | `critique-conflict` | `false` |
| `failed` | `scope-overflow` | `true` |
| `failed` | `self-critique-loop` | `true` |