# CROSS-ANALYZE Mode Protocol

*Analyzes three capture artifacts in parallel for convergent findings.*

## When to Use

After a CAPTURE session has been collected. Analyzes the three artifacts (debug log, stream-json, persisted JSONL) in parallel using three specialized agents, then reports convergence across analysts.

## Input

- **Capture UUID**: User provides UUID → paths constructed from `~/.claude/captures/<UUID>*` and `~/.claude/projects/<encoded-cwd>/<UUID>.jsonl`
- **Direct paths**: User provides artifact paths directly
- **Error**: If no capture found → `{"status": "failed", "reason": "no-capture", "remediation": "Run /tp-session-audit:capture first"}`

## Artifact Types

| Artifact | Path Pattern | Analyst | Extracts |
|---|---|---|---|
| Debug log | `~/.claude/captures/<UUID>.debug.log` | `tp-debug-tracer` | Hook fires, permission gates, plugin sync, MCP errors |
| Stream-json | `~/.claude/captures/<UUID>.stream.jsonl` | `session-inspector` | Streaming events, partial chunks, early termination |
| Persisted JSONL | `~/.claude/projects/<encoded-cwd>/<UUID>.jsonl` | `session-meta-reviewer` | Tool calls, results, usage, errors |

## Execution

**Phase 1 — Detect artifact paths:**
- If UUID provided → construct from `~/.claude/captures/<UUID>*` and `~/.claude/projects/<encoded-cwd>/<UUID>.jsonl`
- If paths provided directly → use those
- If no capture → error with remediation

**Phase 2 — Fan out three parallel specialists:**

All three spawn with `background: true` concurrently:
1. **`session-inspector`** (`--full` mode) ← stream-json → structured event list
2. **`session-meta-reviewer`** (custom subagent) ← persisted JSONL → anti-pattern list
3. **`tp-debug-tracer`** (custom subagent, if available) ← debug log → root-cause traces
   - **Fallback:** If `tp-debug-tracer` not available, use `session-inspector` on debug log instead

**Phase 3 — Await all results:**
- Use `TaskOutput` with `block: true` for all three

**Phase 4 — Aggregate findings:**
- Compile all findings from all three analysts
- **Convergence signal:** Mark findings appearing in ≥2 analyst outputs with `convergence: high`
- Findings from only one analyst → `convergence: low` (could be analyst artifact or noise)

## Output Format

```json
{
  "status": "complete",
  "mode": "cross-analyze",
  "capture_id": "<UUID>",
  "findings": [
    {
      "finding": "<description>",
      "analysts": ["session-meta-reviewer", "debug-tracer"],
      "convergence": "high",
      "severity": "HIGH",
      "evidence": { "file": "<path>", "line": <n>, "text": "..." }
    }
  ],
  "summary": { "total": N, "high_convergence": M, "low_convergence": K }
}
```

## Summary Table Format

Report as: `finding | analysts_that_found_it | convergence | severity`

- High-convergence findings listed first
- Each finding references the specific artifact/line that supports it

## Debug-Log Parser

Apply to `.debug.log` files:
- Extract lines matching `\[HOOK\]`, `\[API\]`, `\[PERMISSION\]`, `\[ERROR\]`, `\[MCP\]`, `\[PLUGIN\]`
- Group by category
- Return categorized event list

## Stream-JSON Parser

Apply to `.stream.jsonl` files:
- Parse each line as a JSON object
- Extract: `type` (message/ping/partial_message/etc), `model`, `usage` (input_tokens, output_tokens), `stop_reason` (end_turn/partial/etc)
- Count unique event types
- Return structured event summary