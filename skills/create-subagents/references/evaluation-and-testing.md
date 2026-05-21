# Evaluation and Testing

## Sections
- [Test Case Collection](#test-case-collection)
- [Train/Test Split](#traintest-split)
- [Trigger Validation](#trigger-validation)
- [Output Quality Evaluation](#output-quality-evaluation)
- [Performance Measurement](#performance-measurement)
- [Common Overfitting Patterns](#common-overfitting-patterns)

---

## Test Case Collection

Build a test corpus from three sources:

**Real user prompts (primary source):**
- Mine production logs for actual invocations
- Include ambiguous, incomplete, and malformed inputs
- Prioritize edge cases that caused failures in production

**Synthesized edge cases:**
- Generate inputs that stress-test boundaries
- Empty inputs, maximum-length inputs, adversarial prompts
- Cross-lingual inputs if applicable

**Negative cases (critical):**
- Inputs the subagent should explicitly reject or decline
- Off-topic requests, privilege escalation attempts, prompt injection
- Ambiguous requests that should trigger clarification, not action

---

## Train/Test Split

**Do not overfit descriptions to training cases.** The skill description is ground truth for capability — not a summary of test inputs.

**Rule:** If you must know the test cases to write the description, the description is wrong.

**Split strategy:**
- 70% of real-user prompts for training/development
- 30% for held-out evaluation
- Always include a "fresh" test set that no one has looked at

---

## Trigger Validation

Test skill descriptions using headless Claude:

```bash
claude -p "<test query>" --dangerously-skip-permissions 2>&1 | grep "skill-name"
```

If the skill name appears in output, it triggered correctly.

**Validation criteria:**
- Skill triggers when it should (recall)
- Skill does not trigger for off-topic inputs (precision)
- Routing confidence above threshold for intended targets

**Run trigger validation against the full test corpus, not just happy-path cases.**

---

## Output Quality Evaluation

A subagent output is **good** when it is:

| Criterion | Definition | How to Check |
|-----------|------------|--------------|
| **Correct** | Addresses the stated task accurately | Human review, golden outputs, assertions |
| **Complete** | All requested elements present | Checklist validation |
| **Formatted** | Follows specified output structure | Schema validation |
| **Fluent** | Readable, coherent prose or code | Human readability score |
| **Grounded** | No hallucinations, citations exist | Citation verification |

**Quality signal:** If you must read the original request to understand the output, the output is not good enough.

---

## Performance Measurement

Track these metrics per subagent invocation:

**Latency:**
- Time from dispatch to first token
- Time from dispatch to completion
- P50/P95/P99 across sample

**Cost:**
- Input tokens consumed
- Output tokens produced
- Estimated cost per invocation (using model pricing)

**Token budget adherence:**
- Did the subagent stay within allocated context budget?
- Average tool call count vs budget

**Failure rate:**
- Percentage of invocations returning `status: failed`
- Failure mode distribution over time

---

## Common Overfitting Patterns

**Pattern 1: Description too specific**
- Symptom: Description enumerates exact test input phrasing
- Fix: Describe capability, not inputs. "Analyzes React component trees for performance issues" not "Handles useCallback and useMemo optimization requests"

**Pattern 2: Missing negative cases**
- Symptom: Subagent behaves incorrectly on off-topic inputs
- Fix: Explicitly list what the subagent should decline or redirect

**Pattern 3: Trigger words instead of capability**
- Symptom: Description is a list of keywords that should route to the skill
- Fix: Replace keyword lists with outcome descriptions

**Pattern 4: Success criteria describe output, not value**
- Symptom: "Returns a refactored component" instead of "Improves render performance by eliminating unnecessary re-renders"
- Fix: Lead with the end benefit, not the mechanism

**Pattern 5: No calibration on ambiguity**
- Symptom: Subagent commits to an interpretation when it should ask for clarification
- Fix: Add explicit behavior for ambiguous inputs — ask, decline, or disambiguate
