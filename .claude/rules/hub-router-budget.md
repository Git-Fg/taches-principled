---
name: hub-router-budget
description: Hub skills must stay under 500 tokens and route to references/. Mode bodies are one-paragraph descriptions, not procedural workflows.
---

# Rule: MUST keep hub SKILL.md under the 500-token router ceiling

**Why:** Hubs load on every session that touches the plugin. A hub over 500 tokens pushes total loaded content toward the 10,000-token silent-truncation threshold. The model remembers the opening (modes list) and closing (CONTRAST) but invents routing for the middle. Worse: when a mode body inlines procedural logic ("if full evaluation, do X; if ad-hoc, do Y"), that mechanism belongs in `references/`, not the router. The hub becomes a 2,500-token wall of procedure that the user pays for on every load.

## Rule

- Total hub SKILL.md (frontmatter + body) MUST be under 500 tokens.
- Each mode body in the hub is ONE short paragraph: what the mode covers + which references to read.
- Procedural logic (workflows, conditional branches, multi-step instructions) lives in `references/`, not in the hub.
- Imperative reference citations ("You MUST read `references/X.md` BEFORE ...") are the only mechanism-style content allowed in the hub.
- The "Output" section that lists what each mode produces MUST stay (one line per mode).
- The "§CONTRAST" / "DO NOT use this skill for" section MUST stay.

## Token budget

Approximate: 1 line of markdown ≈ 15-20 tokens. 500 tokens ≈ 25-30 lines of body (excluding frontmatter). If the hub exceeds 30 lines of body, audit the mode bodies for inlined procedure.

## Verification

```
wc -l plugins/<plugin>/skills/<hub>/SKILL.md
```
Then count body lines (excluding frontmatter). If body > 30 lines, scan each mode body for:
- Multi-step workflows (numbered steps with "1. ... 2. ...")
- Conditional branches ("If full X, do Y; if ad-hoc, do Z")
- Pre-conditions described in prose
- Implementation details ("the orchestrator spawns N parallel ...")

Move all such content to a reference file. The hub body for that mode becomes: "WHAT it covers. You MUST read `references/X.md` BEFORE ..."

## Bad / Good

**Bad:** A QUALITY mode body in a 135-line hub reads:
```
**Full 8-dimension evaluation:** Load the `mcp-quality-evaluate` skill — it is the orchestrator that spawns 8 `mcp-quality-judge` subagents in parallel (one per dimension), reads the JSONL traces, applies the tiebreak rule, and synthesizes the markdown report. This replaces the manual routing described in prior versions.

**Pre-condition:** Ensure the server is fully implemented (IMPLEMENT mode) before running the orchestrator. The judges score produced artifacts — code, schemas, runtime behavior — not abstract intent.

**Ad-hoc single-dimension checks:** If you need to spot-check one specific dimension without running all 8 judges, read `references/quality-rubric.md` directly for that dimension's evidence requirements and scoring criteria, then evaluate manually. Do not use the full orchestrator for a single-dimension check.
```
The hub is 5× over the 500-token ceiling; the mode body is procedural, not routing.

**Good:** The QUALITY mode body is two short paragraphs:
```
Quality evaluation via the 8-dimension Claude-Optimal rubric. Server must already be implemented (IMPLEMENT mode) before evaluation.

You MUST read `references/quality-rubric.md` BEFORE running any evaluation. It teaches the 8-dimension rubric, the FAIL/PARTIAL/PASS/EXEMPLARY scoring scale, the pass threshold, and the per-dimension evidence requirements. Do not proceed without reading it.

You MUST read `references/quality-judge-pattern.md` BEFORE running the full orchestrator. It teaches the parallel-judge pattern, the judge contract, the tiebreak rule, and the report format. Do not proceed without reading it.

For the full 8-dimension evaluation, load the `mcp-quality-evaluate` skill — it is the orchestrator that spawns 8 `mcp-quality-judge` subagents in parallel.
```
