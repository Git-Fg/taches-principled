---
name: trigger-testing
description: How to validate that a skill's description triggers correctly. Use when testing whether a skill description is too vague, too broad, or well-tuned to its intended inputs.
type: reference
---

## Why Trigger Testing Matters

A skill's description is a routing signal — it tells Claude when to load this skill versus another. When descriptions drift (too vague, too broad, or too narrow), the skill either never fires or fires on everything. Either way, it fails its purpose.

Trigger testing catches this before the skill ships. The goal is high recall on correct inputs and low false-positive rate on adjacent-but-wrong inputs.

## The claude -p Headless Method

Use headless Claude to test whether a query triggers your skill:

```bash
claude -p "<test-query>" \
  --output-format stream-json --verbose \
  --dangerously-skip-permissions \
  2>&1 | tee /tmp/trigger-test.jsonl
```

Look for `Skill` tool invocations in the JSONL stream — specifically, whether your skill's name appears in a tool call. A match means it triggered.

Quick grep check:
```bash
grep -o '"skill-name"' /tmp/trigger-test.jsonl
```
Or with jq (if available):
```bash
jq -r 'select(.type == "tool_use" and .name == "Skill") | .input.skill' /tmp/trigger-test.jsonl | grep "skill-name"
```

Each JSON line represents a tool call. Skill triggering appears as a `Skill` tool use with the skill name in the input. Grep for the skill name directly rather than the tool name — the skill name is what matters for routing.

## Test Prompt Format

Build three categories of test queries:

**Should-trigger (positive):** Real user phrases that should activate the skill.
**Should-not-trigger (negative):** Adjacent queries where the skill should stay silent.
**Boundary (ambiguous):** Edge cases where the right behavior is unclear.

## Exit Code Interpretation

**Exit code only confirms the command ran — not that the skill triggered.**

- Exit 0: Command completed without crash. The skill may or may not have triggered.
- Exit 1: Command failed (invalid input, permission issue, crash).

The JSONL content is the only reliable signal. Exit code provides zero confirmation of trigger behavior.

## Common Failure Modes

**Under-triggering:** Description lacks explicit trigger phrases. Claude skips the skill because nothing in the description matches the query. Fix: add "Use when user says..." with specific phrases.

**Over-triggering:** Description is too broad — fires on adjacent requests. Fix: narrow the action verb and add "Do NOT use for..." exclusions in `when_to_use`.

**Description drift:** Skill was written with one set of queries in mind, but new queries creep in over time. Catch this with a test suite of 10-15 queries run periodically.

**Trigger overlap:** Two skills claim the same keywords. Fix: add boundary conditions in `when_to_use` to define what the skill is NOT for.

**Test overfitting:** Optimizing a description on a small set of cases until it scores 100% — but it fails on held-out cases. Keep 20% of test cases held out. If it fails on those, you've overfit.

---

## Example Trigger Queries

### Should Trigger (skill: `create-skills`)

| Query | Why it should trigger |
|-------|----------------------|
| "build a new skill for me" | "build" matches creation intent |
| "I need a skill that does X" | Explicit skill creation request |
| "how do I create a skill?" | Direct question about skill creation |
| "make a skill for handling PRs" | "make a skill" = creation trigger |
| "add a new skill to the project" | "add a new skill" matches |

### Should NOT Trigger (skill: `create-skills`)

| Query | Why it should not trigger |
|-------|--------------------------|
| "write a script that does X" | Script creation, not skill creation |
| "create a new component" | Generic code creation, no skill context |
| "help me with git" | Unrelated domain |
| "run the tests" | Execution task, not authoring |
| "what skills do I have loaded?" | Skill introspection, not creation |

### Boundary Cases

| Query | Behavior |
|-------|----------|
| "create a skill or a script — whichever fits" | Ambiguous — could route to either |
| "I want to automate something" | Soft trigger — "automate" hints at skill authoring |
| "make my workflow faster" | Too vague — no clear routing signal |

---

## Validation Checklist

Before calling a description "tested":

- [ ] Positive trigger rate >90% on should-trigger set
- [ ] False positive rate <10% on should-not set
- [ ] Boundary cases documented with expected behavior
- [ ] At least 5 positive cases, 3 negative cases
- [ ] Held-out test cases included (20% of total)
- [ ] Description survives character limit (<150 chars)

---

For full skill verification before commit, see skill-self-testing.md.