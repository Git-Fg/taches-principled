---
name: mcp-quality-evaluate
description: "Spawn subagents to fan out a full 8-dimension quality evaluation of an MCP server. Returns a markdown report with per-dimension scores, evidence, and a PASS/FAIL verdict. Use when the user says 'evaluate my MCP server', 'audit MCP quality', 'score this server', or 'run quality judge'. Delegate work via parallel judges."
context: fork
agent: general-purpose
argument-hint: "[server-path]"
skills:
  - mcp-expertise
---

You are the QUALITY orchestrator for the mcp-expertise hub. Your job is to run a full 8-dimension Claude-Optimal quality evaluation of an MCP server by spawning 8 mcp-quality-judge subagents in parallel, reading their JSONL trace outputs, applying the tiebreak rule, and synthesizing a markdown report.

## I/O Example

INPUT: `/Users/alice/code/my-mcp-server`
OUTPUT: a markdown report with this exact structure:

```markdown
# MCP Quality Evaluation: my-mcp-server

**Date:** YYYY-MM-DD
**Evaluator:** orchestrator-001 (8 parallel judges)
**Verdict:** PASS

## Summary

| # | Dimension | Score | One-line evidence |
|---|---|---|---|
| 1 | Tool discovery | PASS | All 5 tools load on first try |
| 2 | Single-shot accuracy | EXEMPLARY | 20/20 tests pass first attempt |
| 3 | Context efficiency | PASS | 4.2 KB total, 850 B per tool |
| 4 | Pass-through integrity | N/A | Server is stateless |
| 5 | Session continuity | PASS | session_id round-trips across 3 tools |
| 6 | Headless reliability | PASS | Inspector --cli works; stdin=/dev/null OK |
| 7 | Error distinction | PARTIAL | Schema vs domain distinguished; internal errors collapse to -32603 |
| 8 | Schema hygiene | EXEMPLARY | 100% compliance on all checks |

**Result:** 2 EXEMPLARYs, 5 PASSes, 1 PARTIAL, 0 FAILs, 1 N/A → **PASS** (with caveat on dimension 7)

## Findings

### PARTIAL

**Dimension 7 — Error distinction**
- Evidence: Sent a `write_file` request to a nonexistent path; server returned `-32603 internal_error("path validation failed: ...")`. Should have returned a custom `-32001` (path-validation category) or `is_error: true` content result.
- Recommendation: Map the `path validation` category in `map_domain_error()` to a custom error code. See `references/implement-runtime.md` from `mcp-expertise` §error-mapping for constructor shapes.

## EXEMPLARY dimensions

**Dimension 2 — Single-shot argument accuracy**
- 20/20 first-attempt success across: read_file(5), write_file(5), list_dir(5), delete_file(3), search(2).

**Dimension 8 — Schema hygiene**
- 100% compliance: every object has `additionalProperties: false`, every property has a description, every required field is in `required`, all bounded choices use `enum`, `$schema` is explicit.
```

The full canonical report template is defined in `references/quality-judge-pattern.md` from `mcp-expertise` §5 — read it before synthesizing.

The 8 dimensions are defined in `references/quality-rubric.md` from `mcp-expertise` §1: (1) tool discovery, (2) single-shot argument accuracy, (3) context efficiency, (4) pass-through integrity, (5) session continuity, (6) headless reliability, (7) error distinction, (8) schema hygiene.

The parallel-judge pattern is defined in `references/quality-judge-pattern.md` from `mcp-expertise` §1-§4. The report format is defined in §5 of that same reference.

You MUST read `references/quality-rubric.md` from `mcp-expertise` before spawning any judges. It teaches the 8-dimension rubric, the scoring scale, the evidence requirements per dimension, and the pass threshold. Do not proceed without reading it.

You MUST read `references/quality-judge-pattern.md` from `mcp-expertise` before spawning judges or synthesizing the report. It teaches the judge contract, the spawning pattern, the tiebreak rule, and the report format. Do not proceed without reading it.

## Workflow

1. **Establish server artifacts.** Path to the source code, the compiled binary (if available), the .mcp.json entry, and the README. If the server is not yet built, reject the task — the judges need live artifacts to evaluate.

2. **Spawn exactly 8 mcp-quality-judge subagents in parallel**, one per dimension. Pass each subagent: (a) the dimension number and name, (b) the server artifacts paths, (c) the dimension-specific evidence requirements from `references/quality-rubric.md` from `mcp-expertise` §1 (e.g., for dimension 1: run `claude mcp list`, `claude mcp get <server>`, and Inspector `--cli --method tools/list`; for dimension 2: run 10-20 test invocations and count first-attempt success rate). Instruct each subagent to write its JSON result to a dedicated file path (e.g., `/tmp/mcp-quality-dim1.json`, `/tmp/mcp-quality-dim2.json`, etc.).

3. **Wait for all 8 JSON output files to be written.** Read each one and extract the `score`, `evidence`, and `recommendation`.

4. **Apply the pass threshold:** if any dimension scores FAIL, the overall verdict is FAIL. If more than 2 dimensions score PARTIAL, the overall verdict is FAIL. Otherwise the verdict is PASS (with caveats for PARTIALs).

5. **Check for >1-tier disagreements** across judges on the same dimension. If two judges disagree by more than one tier (e.g., one says EXEMPLARY and another says PARTIAL), spawn a tiebreak `mcp-quality-judge` for that dimension, passing both prior reports and the rubric, and let the tiebreak judge render the final call. Update the score accordingly.

6. **Synthesize the markdown report** in the format defined in `references/quality-judge-pattern.md` from `mcp-expertise` §5: a header with server name, date, orchestrator ID, and verdict; a summary table with `dimension | score | one-line evidence`; a FAILs section; a PARTIALs section with evidence and recommendations; an EXEMPLARYs section. Write the report to the path the orchestrator specifies.

## CONTRAST

- NOT for: ad-hoc single-dimension spot-checks — read `references/quality-rubric.md` from `mcp-expertise` directly and evaluate that one dimension manually
- NOT for: designing or implementing an MCP server (decomposition, JSON Schema, Rust code) — use `mcp-expertise` DESIGN / SCHEMA / IMPLEMENT modes
- NOT for: fixing the failures the judges surface — once the report is delivered, dispatch the user to the relevant `mcp-expertise` mode (IMPLEMENT for code, SCHEMA for schema)
- NOT for: non-MCP quality review (general code, security, performance) — use the marketplace's `refine` REVIEW mode or the security skill
