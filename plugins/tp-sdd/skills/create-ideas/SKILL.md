---
name: create-ideas
description: Use when user asks to "generate ideas", "brainstorm options", or "come up with alternatives" — produces diverse idea set using probability sampling
when_to_use: |
  Use when the user says "generate ideas", "brainstorm options", "come up with alternatives",
  "what if we", or "list possibilities". IMMEDIATELY when the user wants a diverse set of
  options rather than a single recommended approach.
argument-hint: Topic or problem to generate ideas for [optional: number of ideas]
---

## Decision Router

IF user asks to generate ideas, brainstorm options, or come up with alternatives → this skill
IF user wants to explore approaches for a topic → this skill
IF task is already well-defined with a clear path → DO NOT use this skill

# Generate Ideas

Generate a diverse set of ideas using creative sampling with probability weighting.

## Process

Generate 6 responses, each with text and numeric probability:

**Strategic sampling:**
- First 3 responses: high probability ideas (>0.80)
- Last 3 responses: diverse alternatives exploring different regions (<0.10 each)

**Important:** Each response must be genuinely different from the others — avoid overlapping ideas.

## Output Format

```
1. [Idea description] (p=0.XX)
2. [Idea description] (p=0.XX)
...
```

Return ideas conversationally with reasoning, leading with the highest probability option.