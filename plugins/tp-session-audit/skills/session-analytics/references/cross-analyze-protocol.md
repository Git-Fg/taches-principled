# CROSS-ANALYZE Mode Protocol

*Analyzes three capture artifacts in parallel for convergent findings.*

## When to Use

After a CAPTURE session has been collected. Analyzes the three artifacts (debug log, stream-json, persisted JSONL) in parallel using three isolated-context specialists, then reports convergence across analysts.

## Input

- **Capture UUID**: User provides UUID → paths constructed from `~/.claude/captures/<UUID>*` and `~/.claude/projects/<encoded-cwd>/<UUID>.jsonl`
- **Direct paths**: User provides artifact paths directly
- **Error**: If no capture found → `{"status": "failed", "reason": "no-capture", "remediation": "Run /tp-session-audit:capture first"}`

## Artifact Types

| Artifact | Path Pattern | Specialist (lens / scope) | Extracts |
|---|---|---|---|
| Debug log | `~/.claude/captures/<UUID>.debug.log` | `tp-explorer` (scope: "parse debug log; extract root-cause traces from hook fires, permission gates, plugin sync, MCP errors") | Hook fires, permission gates, plugin sync, MCP errors |
| Stream-json | `~/.claude/captures/<UUID>.stream.jsonl` | `tp-explorer` (scope: "parse stream-json; produce structured event list with streaming events, partial chunks, early termination") | Streaming events, partial chunks, early termination |
| Persisted JSONL | `~/.claude/projects/<encoded-cwd>/<UUID>.jsonl` | `tp-critic` (lens: "examine persisted JSONL for behavioral anti-patterns; identify tool calls, results, usage, errors") | Tool calls, results, usage, errors |

## Execution

**Phase 1 — Detect artifact paths:**
- If UUID provided → construct from `~/.claude/captures/<UUID>*` and `~/.claude/projects/<encoded-cwd>/<UUID>.jsonl`
- If paths provided directly → use those
- If no capture → error with remediation

**Phase 2 — Fan out three parallel specialists:**

All three spawn with `background: true` concurrently. Each spawn prompt includes the privacy scrub directive (strip workspace file contents, verbatim user prompts, project paths, environment variables, tokens, credentials):
1. **`tp-explorer`** with scope "parse stream-json → structured event list" (FULL mode)
2. **`tp-critic`** with lens "examine persisted JSONL for behavioral anti-patterns"
3. **`tp-explorer`** with scope "extract root-cause traces from debug log"

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
      "analysts": ["critic", "debug-explorer"],
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