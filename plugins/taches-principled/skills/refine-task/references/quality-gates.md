# Quality Gates Reference

Reusable patterns for independent judge evaluation. Applies to any skill using quality verification with subagent judges.

## Scoring Scale (per criterion)

| Score | Label | Meaning |
|-------|-------|---------|
| 1 | Poor | Missing essential elements, fundamental misunderstanding |
| 2 | Below Average | Some correct elements, significant gaps |
| 3 | Adequate | Meets basic requirements, functional but minimal |
| 4 | Good | Meets all requirements, few minor issues |
| 5 | Excellent | Exceptional quality, exceeds expectations |

## Weighted Score Computation

```
Overall = sum(criterion_score * criterion_weight) for all criteria
```

**Requirements:**
- Weights MUST sum to 1.0
- Each criterion has a clear, measurable description
- Typically 3-6 criteria per rubric

## Decision Logic

| Condition | Action |
|-----------|--------|
| score >= THRESHOLD | PASS — proceed to next phase/step |
| score < THRESHOLD | FAIL — re-launch with feedback |
| MAX_ITERATIONS reached | Proceed with warning |

## Judge Prompt Template

```
Evaluate artifact at: <artifact_path>

Role: <evaluator role>
Rubric:
|criterion|weight|description|
|---|---|---|

Context: <task context>

Score each criterion 1-5. Provide chain-of-thought justification BEFORE each score.
Compute weighted overall. Return PASS/FAIL with specific improvements if FAIL.
```

## Integrity Rules

| Rule | Response |
|------|----------|
| Score 5.0/5.0 | **Hallucination** — reject and re-run judge. Perfect scores are impossible in rigorous evaluation. |
| Missing numerical score | **Rejection signal** — reject and re-run judge |
| Excessively long report without structured evaluation | **Rejection signal** — reject and re-run judge |
| Score below threshold | **FAIL** — re-launch with specific feedback |

## Panel Voting (N judges)

Configurable panel size (1 for solo, 2 for standard panel, N for larger consensus).

1. Collect scores per criterion from all judges
2. Compute median per criterion
3. Flag high-variance criteria: `|score_max - score_min| > 2.0`
4. Compute weighted overall from medians
5. PASS if overall >= threshold

If high variance detected: present perspectives to user for resolution. If user declines, use median (conservative approach).

**Threshold guidance:** 3.5 for experimental work, 4.0 for standard quality, 4.5+ for critical paths.