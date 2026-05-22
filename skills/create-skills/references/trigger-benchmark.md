# Trigger Benchmark: Skill Description Reliability Testing

## Sections
- [Philosophy](#philosophy)
- [The 20-Query Framework](#the-20-query-framework)
- [Exit Criteria](#exit-criteria)
- [Test Overfitting Detection](#test-overfitting-detection)
- [Running the Benchmark](#running-the-benchmark)
- [Building Good Test Cases](#building-good-test-cases)
- [Trigger Benchmark Checklist](#trigger-benchmark-checklist)

---

## Philosophy

Testing skill descriptions is not about passing — it's about understanding what your description ACTUALLY routes.

A skill that scores 100% on 5 test cases but fails on real user queries has learned nothing. Your goal is insight, not compliance. When a test case fails, you learn something about your description. That is the point.

The benchmark is a teaching instrument. It tells you where your description is unclear, too narrow, or too broad. Use it to understand, not to gate.

---

## The 20-Query Framework

Build a test suite of 20 queries across 5 categories:

| Category | Count | Purpose |
|----------|-------|---------|
| **Core positive** | 5 | Must-trigger cases — the primary use cases |
| **Edge positive** | 3 | Ambiguous but should trigger — boundary cases |
| **Core negative** | 5 | Must-not-trigger cases — clearly off-topic |
| **Edge negative** | 3 | Ambiguous but should not trigger — adjacent territory |
| **Held-out** | 4 | Reserved — never seen during development |

Total: 20 queries

### Core Positive (5 queries)

These are the primary use cases. If these don't trigger, the skill is broken.

Examples for a "create-plans" skill:
1. "Plan this feature"
2. "Break down this implementation"
3. "Create a roadmap for the project"
4. "Sketch out how to build this"
5. "What are the steps to implement X?"

### Edge Positive (3 queries)

Ambiguous cases that should trigger but are not the core use case.

1. "Can you help me think through this?" (implied planning)
2. "I need to figure out how to approach this" (implied decomposition)
3. "Where do I start with this?" (implied scope)

### Core Negative (5 queries)

Clearly off-topic. If these trigger, the description is too broad.

1. "Write a function for me"
2. "Fix the bug in line 42"
3. "Format this code"
4. "Explain what this API does"
5. "Run the tests"

### Edge Negative (3 queries)

Adjacent territory that should NOT trigger.

1. "Create a PR description" (adjacent: both involve writing, different intent)
2. "Write documentation for this module" (adjacent: both are writing, different domain)
3. "Make a checklist" (adjacent: lists vs. plans with structure)

### Held-Out (4 queries)

These are reserved. You never look at them during development. You test on them ONLY after you've finalized your description.

1. "I have a big task, how should I organize it?"
2. "What's the best way to tackle this feature?"
3. "Help me scope this properly"
4. "Show me the approach for this"

---

## Exit Criteria

These are targets for production readiness, not gates.

| Metric | Target | Why |
|--------|--------|-----|
| Core positive | 100% | If these don't trigger, the skill is fundamentally broken |
| Edge positive | >60% | Ambiguous cases reveal description gaps |
| Core negative | 100% | False positives destroy trust in the routing system |
| Edge negative | >40% | Some overlap is acceptable in adjacent domains |
| Held-out | >70% | If held-out fails, you overfit to your test cases |

**If edge positive <60%:** Description is too narrow — add more trigger phrases covering adjacent cases.

**If core negative <100%:** Description is too broad — add exclusion language (Do NOT use for...).

**If held-out <70%:** You optimized for the test cases, not for real users. Rebuild the test suite.

---

## Test Overfitting Detection

Test overfitting is when your description passes all your test cases but fails on real user queries. The description has memorized the test cases without learning the underlying routing logic.

### How to Detect Overfitting

| Signal | What It Means |
|--------|--------------|
| Core positive = 100% AND held-out < 70% | Overfit — description works for test cases but not real queries |
| All positive queries are variations of the same phrase | Overfit — one trigger pattern learned, not the concept |
| Negative queries all use the same unrelated topic | Underfit — description is too broad in one dimension only |

### How to Fix Overfitting

1. **Rebuild the test suite** with genuinely different queries — not variations of the same phrases
2. **Add held-out queries early** — don't let them become "the test" after the fact
3. **Check edge positive rate** — if edge positive > core positive, you're too narrow

### The Overfitting Formula

```
If core_positive = 100% AND held_out < 70%:
    → You overfit. Fix: add genuinely different held-out queries.

If edge_positive < core_positive - 20%:
    → You're too narrow. Fix: add broader trigger language.
```

---

## Running the Benchmark

### Headless Testing Method

Run via `claude -p` with stream-json output:

```bash
claude -p "<query>" \
  --output-format stream-json \
  --include-partial-messages \
  2>&1 | grep -o '"skill-name"' | head -1
```

- Returns nothing = did not trigger
- Returns "skill-name" = triggered

### Multiple Runs Per Query

Each query should be run **3 times** to handle non-determinism:

```bash
for i in 1 2 3; do
  result=$(claude -p "<query>" --output-format stream-json 2>&1 | grep -c "skill-name")
  echo "$result"
done | awk '{sum+=$1; count++} END {print sum/count}'
```

If the average is >= 1, the query triggers reliably.

### Aggregate Results

For each query category:

| Category | Queries | Pass | Fail | Pass Rate |
|----------|---------|------|------|-----------|
| Core positive | 5 | X | Y | Z% |
| Edge positive | 3 | X | Y | Z% |
| Core negative | 5 | X | Y | Z% |
| Edge negative | 3 | X | Y | Z% |
| Held-out | 4 | X | Y | Z% |

---

## Building Good Test Cases

### Good Positive Queries

**Good:** Specific, action-oriented, uses the language users would actually use.

```
"create a skill for handling PRs"
"build a multi-agent system"
"write a plan for this feature"
```

**Bad:** Too vague or too specific.

```
"do something with skills" (too vague — tests nothing)
"create a skill for GitHub PR review in Python 3.11 microservices" (too specific)
```

### Good Negative Queries

**Good:** Adjacent domain, clearly different intent.

```
"write a script that creates a PR" (adjacent: writing, different intent)
"fix the authentication bug" (adjacent: code, different intent)
```

**Bad:** So unrelated it doesn't test the boundary.

```
"what is the weather today" (so unrelated it tests nothing)
"play a song" (so unrelated it tests nothing)
```

### Edge Case Guidelines

- Edge positive should be genuinely ambiguous — if you know it should trigger, it's core positive
- Edge negative should be adjacent but not overlapping — if you know it shouldn't trigger, it's core negative
- Held-out queries should be genuinely different from all other queries — not variations

---

## Trigger Benchmark Checklist

Before calling a description "tested":

- [ ] 5 core positive cases (100% required)
- [ ] 3 edge positive cases (>60% target)
- [ ] 5 core negative cases (100% required)
- [ ] 3 edge negative cases (>40% target)
- [ ] 4 held-out cases (>70% target)
- [ ] Test overfitting check passed
- [ ] Failure cases analyzed, not just counted
- [ ] Description survives character limit (150 chars)
- [ ] If core positive < 100%: fix description before proceeding
- [ ] If core negative < 100%: add exclusion language before proceeding

---

## Reading the Results

### If Core Positive Fails (< 100%)

Your description lacks specific trigger language. Users don't trigger the skill because they don't know to use the exact phrasing.

**Fix:** Add explicit trigger phrases: "Use when user says 'X', 'Y', or 'Z'."

### If Edge Positive Fails (< 60%)

Your description is too narrow. It only covers the most obvious cases.

**Fix:** Add broader trigger language covering adjacent use cases.

### If Core Negative Fails (< 100%)

Your description is too broad. It triggers on off-topic queries.

**Fix:** Add exclusion language: "Do NOT use for general coding, X, or Y."

### If Held-Out Fails (< 70%)

You optimized for the test cases. The description is overfit.

**Fix:** Rebuild held-out queries with genuinely different phrases. Don't just rephrase core positives.

---

## Key Principle

**The benchmark tells you what your description actually does, not what you intended it to do.** Trust the results over your intentions. If it fails on real queries but passes your tests, your tests are wrong. Fix the tests.

The goal is to understand your description's actual routing behavior, then make it match your intended behavior.