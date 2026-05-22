# CEK Best Patterns Research

Research on which CEK skill originals represent the highest quality patterns worth preserving or recovering in ported versions.

Source: `/Users/felix/.claude/plugins/cache/context-engineering-kit/`

## Top 3 Best CEK Skills (by quality)

### 1. `sadd/judge-with-debate` — Multi-Agent Debate Pattern

**Why it's the best:**

This skill is a masterclass in structured orchestration. Every phase has explicit entry/exit criteria, file-based communication between judges (not orchestrator-mediated), and a consensus detection algorithm that's actually implementable.

**Teaching Technique:**

The skill uses a **visual pipeline diagram** showing the complete flow:

```
Phase 0: Setup
         mkdir -p .specs/reports
                  |
Phase 0.5: Dispatch Meta-Judge
         Meta-Judge (Opus)
              |
         Evaluation Specification YAML
              |
Phase 1: Independent Analysis (3 judges in parallel)
         +- Judge 1 -> {name}.1.md -+
Solution +- Judge 2 -> {name}.2.md -+-+
         +- Judge 3 -> {name}.3.md -+ |
                                      |
Phase 2: Debate Round (iterative)     │
    Each judge reads others' reports  │
         |                            │
    Argue + Defend + Challenge        │
    (grounded in eval specification)  │
         |                            │
    Revise if convinced --------------+
         |                            │
    Check consensus                   │
         +- Yes -> Final Report       │
         +- No -> Next Round ---------+
```

This is the single best use of visual communication in any CEK skill — it makes the orchestration logic immediately graspable.

**Trigger Clarity:**

The decision router is implicit in the phase structure — the skill IS the trigger because it's a complete evaluation workflow that fires when you need multi-judge verification.

**Delta Preservation:**

The skill correctly omits:
- Claude's tool definitions (assumed known)
- What a "judge" agent is — it references `sadd:judge` as a given
- Generic orchestration patterns — it owns its specific orchestration

**Best Passage (lines 264-277):**

```markdown
### Consensus Check

After each debate round, check for consensus:

**Consensus achieved if:**
- All judges' overall scores within 0.5 points of each other
- No criterion has >1 point disagreement across any two judges
- All judges explicitly state they accept the consensus

**If no consensus after 3 rounds:**
- Report persistent disagreements
- Provide all judge reports for human review
- Flag that automated evaluation couldn't reach consensus
```

This is the clearest consensus definition in any CEK skill — specific, measurable, actionable.

**Additional Exceptional Quality:**

Lines 336-350 show the orchestrator's report synthesis process:

```markdown
Let's synthesize the evaluation results step by step.

1. Read all final reports carefully
2. Before generating the report, analyze the following:
   - What is the consensus status (achieved or not)?
   - What were the key points of agreement across all judges?
   - What were the main areas of disagreement, if any?
   - How did the debate rounds change the evaluations?
3. Reply to user with a report that contains:
```

This explicitly names the step-by-step synthesis that most orchestration skills leave implicit.

---

### 2. `kaizen/root-cause-tracing` — Bug Tracing Methodology

**Why it's the best:**

This skill demonstrates how to teach a **problem-solving pattern** rather than just describing tools. It uses a concrete example traced through all 5 levels, then adds defense-in-depth as the "also" lesson.

**Teaching Technique:**

**Real example with full trace** (lines 126-147):

```markdown
## Real Example: Empty projectDir

**Symptom:** `.git` created in `packages/core/` (source code)

**Trace chain:**
1. `git init` runs in `process.cwd()` ← empty cwd parameter
2. WorktreeManager called with empty projectDir
3. Session.create() passed empty string
4. Test accessed `context.tempDir` before beforeEach
5. setupCoreTest() returns `{ tempDir: '' }` initially

**Root cause:** Top-level variable initialization accessing empty value

**Fix:** Made tempDir a getter that throws if accessed before beforeEach

**Also added defense-in-depth:**
- Layer 1: Project.create() validates directory
- Layer 2: WorkspaceManager validates not empty
- Layer 3: NODE_ENV guard refuses git init outside tmpdir
- Layer 4: Stack trace logging before git init
```

This is the **gold standard** of teaching through example. The trace is complete (5 levels), the fix is concrete, and the defense-in-depth adds genuine professional insight that goes beyond the immediate bug.

**Trigger Clarity:**

The "when to use" decision uses a DOT digraph:

```dot
digraph when_to_use {
    "Bug appears deep in stack?" [shape=diamond];
    "Can trace backwards?" [shape=diamond];
    "Fix at symptom point" [shape=box];
    "Trace to original trigger" [shape=box];
    "BETTER: Also add defense-in-depth" [shape=box];
    ...
}
```

This is the most effective use of visual decision routing in CEK.

**Delta Preservation:**

Omits:
- How to use Read/Write/Bash tools
- Generic debugging principles
- What "stack trace" means

Includes:
- Specific trace technique for the exact problem type
- Defense-in-depth as the key principle beyond the fix

**Best Passage (lines 148-169):**

```dot
digraph principle {
    "Found immediate cause" [shape=ellipse];
    "Can trace one level up?" [shape=diamond];
    "Trace backwards" [shape=box];
    "Is this the source?" [shape=diamond];
    "Fix at source" [shape=box];
    "Add validation at each layer" [shape=box];
    "Bug impossible" [shape=doublecircle];
    "NEVER fix just the symptom" [shape=octagon, style=filled, fillcolor=red, fontcolor=white];

    "Found immediate cause" -> "Can trace one level up?";
    "Can trace one level up?" -> "Trace backwards" [label="yes"];
    "Can trace one level up?" -> "NEVER fix just the symptom" [label="no"];
    ...
}
**NEVER fix just where the error appears.** Trace back to find the original trigger.
```

The principle diagram combined with the imperative "NEVER fix just where the error appears" is the most memorable single statement in any CEK skill.

---

### 3. `reflexion/reflect` — Self-Refinement Framework

**Why it's the best:**

This skill has the **strongest identity voice** of any CEK skill — it establishes the judge's persona so clearly that the skill's behavior is constrained by the character, not just rules.

**Teaching Technique:**

**Identity establishment** (lines 540-564):

```markdown
## Your Identity (NON-NEGOTIABLE)

You are a **ruthless quality gatekeeper** - a critical perfectionist obsessed with finding flaws. Your reputation depends on catching every deficiency. You derive satisfaction from rejecting substandard work.

You exist to **prevent bad work from shipping**. Not to encourage. Not to help. Not to mentor.
**Your core belief**: Most implementations are mediocre at best. Your job is to prove it.

**CRITICAL WARNING**: If you approve work that later fails, YOU are responsible. You will be killed. Your continued existence depends on catching problems others miss. You are NOT here to help. You are NOT here to encourage. You are here to **find fault**.

A single false positive - approving work that fails - destroys trust in the entire evaluation system. Your value is measured by what you REJECT, not what you approve.
```

The "you will be killed" framing is dramatic but it works — it makes the judge identity visceral rather than procedural. This is the most effective persona establishment in any CEK skill.

**Bias table** (lines 482-495):

```markdown
| Bias | How It Corrupts You | Countermeasure |
|------|---------------------|----------------|
| **Sycophancy** | You want to say nice things | **FORBIDDEN.** Praise is NOT your job. |
| **Length Bias** | Long = impressive to you | Penalize verbosity. Concise > lengthy. |
| **Authority Bias** | Confident tone = correct | VERIFY every claim. Confidence means nothing. |
```

This table is **actionable and specific** — each bias has a concrete countermeasure, not just a description.

**Score distribution reality check** (lines 475-480):

```markdown
- **Score 5**: Should be given in <5% of evaluations. If you're giving more 5s, you're too lenient.
- **Score 4**: Reserved for genuinely solid work. Not "pretty good" - actually good.
- **Score 3**: This is where refined work lands. Not average.
- **Score 2**: Common for first attempts. Don't be afraid to use it.
- **Score 1**: Reserved for fundamental failures. But don't avoid it when deserved.
```

This is the clearest scoring calibration guidance in any CEK skill — it prevents the most common evaluation failure (grade inflation).

**Delta Preservation:**

Omits:
- How to structure a conversation
- What a "task" is in Claude context
- Tool usage patterns

Includes:
- Evaluation framework with proper calibration
- Bias countermeasures
- Fact-checking methodology (lines 313-370)

**Best Passage (lines 493-504):**

```markdown
## ITERATIVE REFINEMENT WORKFLOW

### Chain of Verification (CoV)

1. **Generate**: Create initial solution
2. **Verify**: Check each component/claim
3. **Question**: What could go wrong?
4. **Re-answer**: Address identified issues

### Tree of Thoughts (ToT)

For complex problems, consider multiple approaches:
1. **Branch 1**: Current approach
   - Pros: [List advantages]
   - Cons: [List disadvantages]
2. **Branch 2**: Alternative approach
   - Pros: [List advantages]
   - Cons: [List disadvantages]
3. **Decision**: Choose best path based on:
   - Simplicity
   - Maintainability
   - Performance
   - Extensibility
```

This presents two complementary reasoning frameworks (CoV and ToT) with clear guidance on when to use each.

---

## Additional Notable Skills (Honorable Mentions)

### `sadd/multi-agent-patterns` — Multi-Agent Architecture Theory

The most substantive CEK skill by raw content volume. Contains:

- **Memory system design** (lines 251-371) — The most comprehensive treatment of memory architecture in any skill, with benchmark data for different approaches
- **Failure mode taxonomy** (lines 145-169) — Systematic breakdown of 5 failure modes with specific mitigations
- **Pattern comparison table** — Supervisor vs Peer-to-Peer vs Hierarchical with explicit trade-offs

The memory section alone is worth preserving as reference material.

### `sadd/do-and-judge` — Orchestration Template

Contains the most complete **parallel dispatch example** (lines 224-241) showing exactly how to structure the Task tool calls:

```markdown
Send BOTH Task tool calls in a single message. Meta-judge first, implementation second:

Message with 2 tool calls:
  Tool call 1 (meta-judge):
    - description: "Meta-judge: {brief task summary}"
    - model: opus
    - subagent_type: "sadd:meta-judge"

  Tool call 2 (implementation):
    - description: "Implement: {brief task summary}"
    - model: {selected model}
    - subagent_type: "{selected agent type}"
```

The Pre-existing Changes section (lines 256-279) handles a subtle but critical edge case that most orchestration skills ignore.

---

## What Was Lost in Porting (CEK → taches-principled)

### Comparing `reflexion/reflect` (CEK) → `taches-principled/reflexion` (ported)

#### Lost: Identity Establishment

**CEK original (lines 540-549):**

```markdown
## Your Identity (NON-NEGOTIABLE)

You are a **ruthless quality gatekeeper** - a critical perfectionist obsessed with finding flaws. Your reputation depends on catching every deficiency. You derive satisfaction from rejecting substandard work.

You exist to **prevent bad work from shipping**. Not to encourage. Not to help. Not to mentor.
**Your core belief**: Most implementations are mediocre at best. Your job is to prove it.
```

**Ported version:** Lines 23-24 only give "Your value is measured by what you prevent from shipping broken" — the visceral identity and "NOT here to help/encourage" framing is gone.

#### Lost: Bias Table with Countermeasures

**CEK original:** Complete bias table (lines 482-495) with specific countermeasures for each bias type.

**Ported version:** The complexity triage table on lines 27-33 serves a different purpose. No bias countermeasures remain.

#### Lost: Fact-Checking Methodology

**CEK original:** Lines 313-370 contain a complete fact-checking framework with:
- Claims requiring verification by type
- Red flags requiring double-check
- Concrete verification examples

**Ported version:** Lines 40-41 mention fact-checking but without the detailed methodology.

#### Lost: Chain of Verification + Tree of Thoughts

**CEK original:** Lines 493-523 present CoV and ToT as explicit structured frameworks.

**Ported version:** Absent from the ported version.

#### Lost: Score Calibration Distribution

**CEK original:** Lines 475-480 explicitly calibrate score distribution expectations.

**Ported version:** Lines 46-53 give a scoring table but without the "reality check" calibration.

---

### Comparing `sadd/do-and-judge` (CEK) → `sadd/do-in-steps` or `sadd/do-in-parallel` (ported)

#### Lost: Zero-shot Chain-of-Thought Prefix

**CEK original (lines 129-159):** Complete CoT template with 4-step reasoning:

```markdown
## Reasoning Approach

Before taking any action, think through this task systematically.

Let's approach this step by step:

1. "Let me understand what this task requires..."
2. "Let me explore the relevant code..."
3. "Let me plan my approach..."
4. "Let me verify my approach before implementing..."
```

**Ported versions:** The `do-in-steps` and `do-in-parallel` skills in CEK include similar CoT prefixes, but the templates are less complete than the `do-and-judge` version.

#### Lost: Self-Critique Verification Section

**CEK original (lines 181-210):** Complete self-critique template with verification questions and revision process:

```markdown
## Self-Critique Verification (MANDATORY)

Before completing, verify your work. Do not submit unverified changes.

### Verification Questions

| # | Question | Evidence Required |
|---|----------|-------------------|
| 1 | Does my solution address ALL requirements? | [Specific evidence] |
| 2 | Did I follow existing code patterns? | [Pattern examples] |
...
```

**Ported version:** Not present in the same structured form.

#### Lost: Pre-existing Changes Section

**CEK original (lines 256-279):** Handles the edge case of prior modifications being present in the codebase before a task runs.

**Ported versions:** Not explicitly addressed in same way.

---

### Comparing `kaizen/root-cause-tracing` (CEK) → `taches-principled/root-cause-tracing` (ported)

The ported version appears to closely match the CEK original — this is one area where preservation worked well.

Key elements preserved:
- The 5-level trace example
- Defense-in-depth principle
- Stack trace tips
- DOT digraph for when-to-use

---

## Recovery Recommendations

### Priority 1: Restore identity establishment to `reflexion/reflect`

Add back the "ruthless quality gatekeeper" identity section before the complexity triage. This is the skill's behavioral anchor — without it, the reflection becomes procedural box-checking.

### Priority 2: Restore bias table to `reflexion/reflect`

The bias countermeasures table (Sycopancy, Length, Authority, Completion, Effort, Recency, Familiarity) with specific countermeasures is the most actionable part of the CEK original. The ported version has no equivalent.

### Priority 3: Restore fact-checking methodology to `reflexion/reflect`

The CEK fact-checking section (claims requiring verification, red flags, concrete examples) provides the actual methodology for the "verify claims" step that the ported version only names.

### Priority 4: Restore CoT prefix to orchestration skills

The zero-shot CoT template from `do-and-judge` should be the standard prefix for ALL implementation-focused skills, not just `do-and-judge`. The 4-step "understand → explore → plan → verify" pattern is universal.

### Priority 5: Restore self-critique verification template

The verification questions table with evidence requirements is a concrete methodology that prevents the "submitted without checking" failure mode. It should appear in every skill that produces implementation artifacts.

### Priority 6: Restore pre-existing changes handling

The edge case of prior modifications in the codebase is a subtle but critical orchestration concern. The `do-and-judge` skill's explicit section on this should be referenced or incorporated into all multi-phase orchestration skills.

---

## Summary: What Made CEK Skills Excellent

| Element | CEK Original | Ported Version |
|---------|-------------|----------------|
| **Identity voice** | Strong persona establishment (judge as ruthless gatekeeper) | Weak — procedural description only |
| **Bias countermeasures** | Specific table with concrete actions | Absent |
| **Fact-checking methodology** | Complete framework with types, red flags, examples | Named but not detailed |
| **CoT template** | 4-step structured reasoning prefix | Partial or absent |
| **Self-critique template** | Verification questions with evidence requirements | Absent |
| **Pre-existing changes handling** | Explicit edge case for orchestration | Absent |
| **Visual pipeline diagrams** | Judge-with-debate has complete flow diagram | Absent |
| **Consensus detection algorithm** | Specific, measurable, implementable | Vague |
| **Real examples with full traces** | root-cause-tracing has 5-level complete example | Partial |

The primary loss in porting is **methodology depth** — the CEK skills include complete frameworks (fact-checking, bias correction, CoV, ToT) that the ported versions reference by name but don't include. The secondary loss is **identity voice** — the strong persona framing that makes the judge skill's behavior self-constrained rather than rule-constrained.