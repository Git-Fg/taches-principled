# Meta-Judge Pattern

## The Pattern

CEK `do-and-judge` uses a **meta-judge** that generates evaluation specification BEFORE implementation begins.

```
Phase 1: Task Analysis + Model Selection
Phase 2: PARALLEL dispatch
    - Meta-judge: generates evaluation spec (rubrics, checklist, scoring criteria)
    - Implementation agent: produces the artifact
Phase 3: Judge verifies using meta-judge's spec
Phase 4: If score <4.0 → retry with feedback (max 2 retries)
```

## Why It Works

- Meta-judge produces **tailored rubrics** before the implementation exists
- Judge applies the spec mechanically — catches blind spots self-critique misses
- Parallel dispatch (meta-judge + implementation) adds no latency
- Retry loop with score threshold prevents quality shortcuts

## Key Constraints

| Element | Value | Purpose |
|---------|-------|---------|
| Score threshold | ≥4.0/5.0 | Quality gate |
| Max retries | 2 | Prevent infinite loops |
| Same spec on retry | Do NOT re-run meta-judge | Criteria don't change, only implementation |
| Judge threshold blind | NEVER tell judge the threshold | Avoid bias |

## Adaptation for taches-principled

The `execute-plans` skill already orchestrates parallel workers and milestone reviews. Adding meta-judge requires:

1. For each task segment in a plan, run meta-judge parallel to implementation subagent
2. Pass meta-judge's evaluation YAML to the segment's verification agent
3. Retry failed segments (score <4.0) with feedback until passing or escalate

This is most applicable when plan segments produce discrete artifacts (code, config, docs) rather than exploratory research.