# Grader Output Template

When evaluating a skill, produce this structured output:

```
## Grade: [skill-name]

**Overall**: X/10

| Dimension | Score | Evidence |
|-----------|-------|----------|
| Routing Signal | X/4 | [quote from description] |
| Delta Clarity | X/3 | [quote showing what skill adds vs default] |
| Teaching Posture | X/3 | [how principles are taught vs procedures] |
| Anti-Pattern Quality | X/2 | [quote with consequence] |

### Verdict
[One sentence: overall teaching effectiveness assessment]

### If Improving
[The single highest-impact change]
```

## Structured Format (for Analyzer Pipeline)

When outputting for machine-readable consumption, append this block:

```json
{
  "skill": "[skill-name]",
  "grading": {
    "overall": X,
    "dimensions": {
      "routing_signal": {
        "score": X,
        "max": 4,
        "quote": "[exact quote from description]",
        "observation": "[why this score was given]"
      },
      "delta_clarity": {
        "score": X,
        "max": 3,
        "quote": "[exact quote]",
        "observation": "[why this score was given]"
      },
      "teaching_posture": {
        "score": X,
        "max": 3,
        "examples": ["[example of principle]", "[example of procedure]"],
        "observation": "[why this score was given]"
      },
      "anti_pattern_quality": {
        "score": X,
        "max": 2,
        "examples": ["[wrong/right pair with consequence]"],
        "observation": "[why this score was given]"
      }
    }
  },
  "verdict": "[one-sentence teaching effectiveness]",
  "if_improving": {
    "change": "[specific change to make]",
    "dimension_impact": "[which dimension this improves most]",
    "teaching_outcome": "[what Claude learns after this change]"
  }
}
```

## Grading Examples

### Example: Low Teaching Effectiveness (2/10)

```
## Grade: vague-helper

**Overall**: 2/10

| Dimension | Score | Evidence |
|-----------|-------|----------|
| Routing Signal | 0/4 | "Helps with coding tasks" — no triggers |
| Delta Clarity | 0/3 | No delta stated |
| Teaching Posture | 1/3 | Step-by-step with no principles |
| Anti-Pattern Quality | 1/2 | "Don't be too generic" — vague |

### Verdict
A skill that tells Claude nothing it couldn't infer from system prompts.

### If Improving
Add explicit trigger phrases: "Use when user asks to 'write a function', 'create a variable', or 'refactor X'." Without triggers, this skill never loads.
```

```json
{
  "skill": "vague-helper",
  "grading": {
    "overall": 2,
    "dimensions": {
      "routing_signal": {"score": 0, "max": 4, "quote": "Helps with coding tasks", "observation": "No trigger phrases"},
      "delta_clarity": {"score": 0, "max": 3, "quote": "None", "observation": "No delta stated"},
      "teaching_posture": {"score": 1, "max": 3, "examples": ["Step 1", "Step 2"], "observation": "Procedures only"},
      "anti_pattern_quality": {"score": 1, "max": 2, "examples": ["Don't be generic"], "observation": "Vague warning"}
    }
  },
  "verdict": "A skill that tells Claude nothing it couldn't infer from system prompts.",
  "if_improving": {
    "change": "Add explicit trigger phrases",
    "dimension_impact": "routing_signal",
    "teaching_outcome": "Claude will know when to invoke this skill"
  }
}
```

### Example: High Teaching Effectiveness (8/10)

```
## Grade: plan-author

**Overall**: 8/10

| Dimension | Score | Evidence |
|-----------|-------|----------|
| Routing Signal | 3/4 | "Use when user asks to plan, sketch, roadmap, or break down a project" |
| Delta Clarity | 3/3 | "Unlike implementation skills, planning skills teach judgment about scope and sequencing" |
| Teaching Posture | 2/3 | "The key principle: decompose until each task fits in one context window" with examples |
| Anti-Pattern Quality | 1/2 | Anti-patterns show wrong/right but no consequence |

### Verdict
A skill that teaches scoping judgment and decomposition principles effectively.

### If Improving
Add consequence to anti-patterns: "A plan with 6+ tasks degrades quality — by task 4, Claude rushes to finish rather than think carefully."
```

```json
{
  "skill": "plan-author",
  "grading": {
    "overall": 8,
    "dimensions": {
      "routing_signal": {"score": 3, "max": 4, "quote": "Use when user asks to plan, sketch, roadmap, or break down a project", "observation": "Multiple specific triggers"},
      "delta_clarity": {"score": 3, "max": 3, "quote": "Unlike implementation skills, planning skills teach judgment...", "observation": "Clear contrast with default"},
      "teaching_posture": {"score": 2, "max": 3, "examples": ["The key principle: decompose..."], "observation": "Principles first, examples as reference"},
      "anti_pattern_quality": {"score": 1, "max": 2, "examples": ["Over-decomposition anti-pattern"], "observation": "Wrong/right present but no consequence stated"}
    }
  },
  "verdict": "A skill that teaches scoping judgment and decomposition principles effectively.",
  "if_improving": {
    "change": "Add consequence to anti-patterns",
    "dimension_impact": "anti_pattern_quality",
    "teaching_outcome": "Claude will understand why over-decomposition fails, not just that it does"
  }
}
```