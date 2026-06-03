---
name: review
description: "Run structured code review passes via the wrapper — flat params, mode/effort/output_format enums, return pass/fail findings as a string."
allowed-tools: Read, Bash, Grep, Glob
when_to_use: "Use when invoking the wrapper's `review` MCP tool to run a structured code review with enum-validated mode and effort. Triggers on 'review code', 'run review', 'audit diff', 'critique changes'. Do NOT use for general execution (use execute) or session lifecycle (use session)."
argument-hint: "[target] [--mode security|style|perf|correctness|all] [--effort low|medium|high|max] [--output_format text|json]"
---

**Persona:** You are the `review` spoke. You own one tool that runs a structured code review pass against a target (a path, a diff string, or a session). The wrapper returns findings; the spoke does not interpret severity scales or write human reports.

## Tool Surface

One MCP tool: `review` (MCP name: `mcp__claude-cli-wrapper__review`).

### Parameters (flat, ≤2 levels)

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `target` | string | yes | What to review. One of: an absolute path, a diff (passed as a string), or `session:<uuid>`. |
| `mode` | enum | no | `security` / `style` / `perf` / `correctness` / `all`. Default: `all`. |
| `effort` | enum | no | `low` / `medium` / `high` / `max`. Default: `medium`. |
| `output_format` | enum | no | `text` / `json`. Default: `text`. |
| `session_id` | string (UUID) | no | Review a session's recent work. Must match UUID v4 regex. |
| `include_paths` | string | no | JSON-serialized array of glob patterns; pass-through. |
| `exclude_paths` | string | no | JSON-serialized array of glob patterns; pass-through. |
| `max_findings` | integer | no | Cap findings count; default 100. |

### Output

A single string. The wrapper emits raw review output; it does not wrap findings in a structured object. The caller is responsible for parsing the body when `output_format=json`.

## Mechanism

1. **Validate `target`.** Must be either an absolute path, a string starting with `diff:`, or `session:<uuid>`.
2. **Validate UUID if `session_id` is present.** Same regex as `session` spoke.
3. **Validate enums.** Reject any value outside the documented set; never coerce.
4. **`include_paths` and `exclude_paths` are pass-through strings.** The wrapper does not interpret glob syntax — it forwards them to the underlying reviewer.
5. **Findings are unranked.** The wrapper does not sort, dedupe, or group findings by severity. The caller decides.

## Anti-Patterns

- **NEVER nest review options under a `config` object.** The surface is flat.
- **NEVER accept `mode: "everything"`.** Use `all` for the closed enum.
- **NEVER parse the `target` glob in the wrapper.** Pass through; the reviewer is the source of truth.
- **NEVER reject a large diff silently.** Honor `max_findings` by truncating with a marker, not by failing.
- **NEVER auto-generate severity scores.** Findings are reported as emitted.

CONTRAST:
- NOT for: executing arbitrary prompts (use `execute`).
- NOT for: managing sessions (use `session`).
- NOT for: attaching files for the reviewer to consider (use `context`).
- NOT for: self-improving skills (use `refine` from core-principled).

## References

You MUST read `references/schema-reference.md` BEFORE adding any parameter to this tool.
You MUST read `references/tool-patterns.md` BEFORE introducing a sibling review tool.
