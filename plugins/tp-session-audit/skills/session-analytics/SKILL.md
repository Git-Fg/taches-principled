---
name: session-analytics
description: "Analyze session transcripts to extract data, diagnose anti-patterns, and generate GitHub issues from findings."
allowed-tools: Read, Glob, Grep, Bash, Agent
when_to_use: "Use for session metrics, anti-pattern review, or creating issues from findings. Examples: \"parse debug log\", \"analyze hooks\". CONTRAST: No code analysis (use refine); no general project bugs (use meta-issue)."
argument-hint: "<inspect|review|issue> [session-id|--dry-run] [--filter errors|tools|cost|skills] [--full|--summary]"
---

## Routing Guidance

- **CAPTURE**: 'capture session', 'collect artifacts', 'headless capture', 'run verification capture', 'profile a skill invocation', 'audit skill routing', 'measure hook in vivo', 'behavioral capture'
- **INSPECT**: 'parse session', 'session metrics', 'session data', 'inspect transcript', 'session cost', 'what tools did I use', 'how long was this session', 'extract session data'
- **REVIEW**: 'review session', 'what went wrong', 'behavioral review', 'anti-pattern', 'meta-review', 'session critique', 'why did it fail', 'investigate session'
- **ISSUE**: 'create issue from review', 'file report', 'meta-issue', 'generate GitHub issue', 'make a bug report from session'
- CONTRAST with diagnose: session-analytics analyzes session transcripts; diagnose analyzes code problems.
- CONTRAST with code-review: session-analytics extracts behavioral patterns; code-review analyzes source code quality.

## What This Skill Changes

**Default behavior:** Session data remains unstructured JSONL — tool calls, errors, and cost metrics require ad-hoc grep commands. Anti-patterns surface only when the user explicitly asks, and no systematic recording exists. Issue creation is manual and inconsistent.

**With this skill:** Standardized three-mode extraction (INSPECT), behavioral diagnosis (REVIEW), and sanitized issue generation (ISSUE). The main agent delegates data extraction and analysis to subagents; it synthesizes results and manages the issue creation workflow.

**Why mode separation:** INSPECT is data extraction (fast, single-pass). REVIEW is behavioral interpretation (deeper, may fan out subagents). ISSUE is report generation (post-review action, requires privacy audit).

## Decision Router

IF user wants to collect behavioral artifacts (capture session, headless capture, run verification) → **CAPTURE** mode
IF user wants structured session data (metrics, tool calls, cost) → **INSPECT** mode
IF user wants behavioral anti-pattern diagnosis → **REVIEW** mode
IF user wants to create a GitHub issue from review findings → **ISSUE** mode
IF user passes `--mode cross-analyze` → **CROSS-ANALYZE** mode
IF user passes `--mode adjudicate` → **ADJUDICATE** mode

---

## CAPTURE Mode

Collects behavioral artifacts by running a headless Claude Code session with canonical capture flags. Use before INSPECT, REVIEW, or meta-issue when you need fresh artifacts.

### When to Use

Before behavioral verification, trigger collision testing, hook validation, or plugin A/B testing — whenever you need a fresh capture of Claude Code's actual behavior rather than analyzing an existing transcript.

### CAPTURE Protocol

Generate a capture UUID, then run the canonical capture incantation:

1. **Generate identifiers:**
   ```bash
   UUID=$(uuidgen 2>/dev/null || python3 -c "import uuid; print(uuid.uuid4())")
   SESSION_ID="$UUID"
   ```

2. **Create capture directory:**
   ```bash
   mkdir -p ~/.claude/captures
   ```

3. **Run the capture:**
   ```bash
   claude -p "$ARGUMENTS" \
     --session-id "$UUID" \
     --debug "hooks,api,plugins,skills" \
     --debug-file ~/.claude/captures/${UUID}.debug.log \
     --output-format stream-json \
     --include-hook-events \
     --include-partial-messages \
     --max-budget-usd 0.50 \
     --verbose 2>&1 | tee ~/.claude/captures/${UUID}.stream.jsonl
   ```

4. **Wait for completion** (the command blocks until the capture finishes).

5. **Report artifact paths:**
   Return the three artifact paths:
   - Debug log: `~/.claude/captures/<UUID>.debug.log`
   - Stream-json: `~/.claude/captures/<UUID>.stream.jsonl`
   - Persisted JSONL: `~/.claude/projects/<encoded-cwd>/<UUID>.jsonl`

6. **Store the session ID** for downstream skills:
   ```bash
   echo "$UUID" > ~/.claude/captures/.last-capture-id
   ```

### Artifact Provenance

| Artifact | Path | Best for |
|---|---|---|
| Debug log | `~/.claude/captures/<UUID>.debug.log` | Hook fires, permission gates, plugin sync, MCP errors |
| Stream-json | `~/.claude/captures/<UUID>.stream.jsonl` | Streaming behavior, partial chunks, early termination |
| Persisted JSONL | `~/.claude/projects/<encoded-cwd>/<UUID>.jsonl` | Tool calls, results, usage, errors |

### Execution

**Default: subagent delegation.** For CAPTURE, spawn a Bash subagent to execute the headless capture command.

**Spawn pattern:**
- Scope: `~/.claude/captures/` directory for artifact output
- Role: general-purpose (headless execution)
- Output: Three artifact paths reported to main agent

After CAPTURE, route to **INSPECT** mode for artifact parsing, then to **REVIEW** mode for analysis.

---

## INSPECT Mode

### Multi-Artifact Routing

`session-inspect` handles three artifact types. Detect which type you're working with:

**Routing rules (apply in order):**
1. If input path ends with `.jsonl` → check if first line contains `"type"` or `MessageParam` → JSONL parser (existing)
2. If input path ends with `.debug.log` → debug-log parser (grep for `[HOOK]`, `[API]`, `[PERMISSION]`, `[ERROR]` sections)
3. If input path ends with `.stream.jsonl` → stream-json parser (parse per-turn delta events, extract `type`, `model`, `usage`, `stop_reason`)
4. If the input is a directory → scan for `.debug.log`, `.stream.jsonl`, and `.jsonl` files and process all three

**Debug-log parser** (apply to `.debug.log` files):
- Extract lines matching `\[HOOK\]`, `\[API\]`, `\[PERMISSION\]`, `\[ERROR\]`, `\[MCP\]`, `\[PLUGIN\]`
- Group by category
- Return categorized event list

**Stream-json parser** (apply to `.stream.jsonl` files):
- Parse each line as a JSON object
- Extract: `type` (message/ping/partial_message/etc), `model`, `usage` (input_tokens, output_tokens), `stop_reason` (end_turn/partial/etc)
- Count unique event types
- Return structured event summary

---

Parses raw session JSONL into structured data — tool calls, errors, cost, loaded plugins, and behavioral events. You MUST read `references/inspect-reference.md` before executing INSPECT mode.

### Session Discovery

Claude Code stores session transcripts at `~/.claude/sessions/{uuid}/raw-transcript.jsonl`.

1. **Latest session**: `ls -t ~/.claude/sessions/ | head -1` → use that UUID
2. **By ID**: user provides the UUID directly
3. **By content**: grep across sessions for a keyword the user remembers

If no session ID provided and latest session is empty or still running, try the previous one.

### INSPECT Submodes

**Default: SUMMARY** — quick overview of session metadata, tool counts, error summary, and environment loaded.

**--full flag: FULL** — complete structured extraction including every tool call, assistant message count, git state snapshot, and init event details.

**--filter flag: FILTER** — specific event filtering (`errors`, `tools`, `cost`, `skills`).

### Execution

**Default: subagent delegation.** For structured extraction, spawn a **`session-inspector`** subagent with the session path and requested mode. The subagent reads the JSONL, applies the privacy scrub, and writes structured output to `.principled/scratch/session-inspect-{uuid}.{json|md}`.

**Spawn pattern:**
- Scope: session transcript at `~/.claude/sessions/{uuid}/raw-transcript.jsonl`
- Role: **`session-inspector`** (data extraction)
- Output: `.principled/scratch/session-inspect-{uuid}.json` (FULL) or `.principled/scratch/session-inspect-{uuid}.md` (SUMMARY)
- Mode: SUMMARY / FULL / FILTER as specified by user flags

---

## REVIEW Mode

Reviews Claude Code session transcripts for behavioral anti-patterns and investigates root causes. You MUST read `references/review-reference.md` before executing REVIEW mode.

### REVIEW Submodes

**Default: REVIEW** — quick diagnostic of the most recent or specified session using a single diagnostic subagent.

**investigate argument: INVESTIGATE** — deep investigation with parallel subagent fan-out (2 subagents simultaneously) for structural or recurring failures.

### Process (REVIEW mode)

1. **Discover session** — find the target transcript
2. **Spawn `session-meta-reviewer` subagent** — reads full JSONL, produces behavioral analysis
3. **Present findings** — anti-patterns (PLUGIN scope only), what went well, scope verdict
4. **Next step suggestion** — if actionable findings exist, suggest running ISSUE mode

### Process (INVESTIGATE mode)

1. **Discover session** — same as REVIEW
2. **Spawn 2 parallel subagents**:
   - **Diagnostic subagent** (**`session-meta-reviewer`**): reads transcript, identifies anti-patterns and root cause scope
   - **Context & Outcome subagent** (**`session-context-analyzer`**): analyzes git state, environment, and behavioral outcomes (what worked vs what broke)
3. **Synthesize** — merge findings, cross-reference with git state, deduplicate, assign severity
4. **Scope gate** — check if findings are PLUGIN scope (reportable) or USER-FILE/ENVIRONMENT scope (excluded)
5. **Write unified report** to `.principled/scratch/meta-review-{session_id}.md`

### Privacy

The **`session-meta-reviewer`** agent strips: file contents from workspace, user prompts verbatim (paraphrases intent only), project directory paths, environment variables, tokens, credentials.

### Execution

**Default: subagent delegation.** For REVIEW, spawn one **`session-meta-reviewer`** subagent. For INVESTIGATE, spawn 2 parallel subagents. The main agent synthesizes results; it never performs transcript analysis inline.

**Spawn pattern:**
- Scope: session transcript at `~/.claude/sessions/{uuid}/raw-transcript.jsonl`
- Role: **`session-meta-reviewer`** (diagnostic), **`session-context-analyzer`** (context & outcome analysis)
- Output: `.principled/scratch/meta-review-{session_id}.md`

---

## ISSUE Mode

Creates a GitHub issue from meta-review findings. You MUST read `references/issue-reference.md` before executing ISSUE mode.

### ISSUE Submodes

**Default: CREATE** — creates a GitHub issue using `gh issue create`.

**--dry-run flag: DRY-RUN** — builds and prints the issue body without creating it.

### Prerequisites

1. **Verify `gh` is available** — `which gh`. If missing, tell user to install GitHub CLI.
2. **Verify git remote** — `git remote get-url origin`. If missing, tell user this only works in a git repo with a GitHub remote.
3. **Verify review file exists** — read the meta-review output from `.principled/scratch/`

### Privacy Audit (CREATE mode)

Before creating any issue, scan the review content for:
- Absolute file paths (except `~/.claude/sessions/` which is generic)
- User prompt text (should be paraphrased, not quoted)
- Environment variable values
- Token or credential strings
- Project-specific file contents

If any sensitive content found: **ABORT** and tell the user what needs to be redacted.

### Scope Exclusion

If the meta-review file has `Report advised: NO` (all findings are USER-FILE/ENVIRONMENT/MODEL scope), tell the user:

> "The review found no actionable plugin-scope findings. All issues trace to user configuration or environment state. Creating a public issue is not recommended — the root cause is outside the plugin's control."

The user can override with explicit confirmation.

### Execution

**Default: subagent delegation.** For privacy audit and body construction, spawn an **`session-issue-generator`** subagent. For issue creation, use the Bash tool directly with `gh issue create`.

**Spawn pattern:**
- Scope: `.principled/scratch/meta-review-{session_id}.md`
- Role: **`session-issue-generator`** (privacy audit, body construction)
- Output: issue body file → `gh issue create`

---

## CROSS-ANALYZE Mode

**When to use:** After a capture session has been collected. Analyzes the three artifacts (debug log, stream-json, persisted JSONL) in parallel using three specialized agents, then reports convergence across analysts.

**Execution:**

1. **Detect artifact paths** from the capture session:
   - If user provides a capture UUID → construct paths from `~/.claude/captures/<UUID>*` and `~/.claude/projects/<encoded-cwd>/<UUID>.jsonl`
   - If user provides paths directly → use those paths
   - If no capture found → error with `{"status": "failed", "reason": "no-capture", "remediation": "Run /tp-session-audit:capture first"}`

2. **Fan out three parallel specialists** (spawn all three concurrently with background=true):
   - **`session-inspector`** (**`--full`** mode) ← stream-json output → structured event list
   - **`session-meta-reviewer`** (custom subagent) ← persisted JSONL → anti-pattern list
   - **`tp-debug-tracer`** (custom subagent, if available) ← debug log → root-cause traces
     - **Note:** `tp-debug-tracer` is also used by `diagnose` STACK-TRACE mode for backward call-chain debugging.

   - If **`tp-debug-tracer`** is not available, use the **`session-inspector`** on the debug log instead

3. **Wait for all three** (TaskOutput with block=true for all three)

4. **Aggregate findings:**
   - Compile all findings from all three analysts
   - **Convergence signal:** Mark findings that appear in ≥2 analyst outputs with a `convergence: high` flag
   - Findings from only one analyst → `convergence: low` (could be analyst artifact or noise)

5. **Report:**
   - Summary table: finding | analysts_that_found_it | convergence | severity
   - High-convergence findings listed first
   - Each finding references the specific artifact/line that supports it

**Output format:**
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

---

## ADJUDICATE Mode

**When to use:** After cross-analyze has produced findings. Validates each finding against evidence and runs adversarial challenge.

**Execution:**

1. **Collect findings** from cross-analyze output (passed as file path argument or previous session-inspect output)

2. **Parallel validation per finding** — for each finding, spawn two agents concurrently:
   - **tp-fpf:fpf-evidence-validator** ← the finding + the JSONL artifact → "evidence supports" or "L1-speculative"
   - **tp-sadd:sadd-judge** ← the finding → try to refute it (refuted=true if uncertain)

   Use `background: true` for all spawns. Spawn all evidence-validators and all adversarial challengers concurrently.

3. **Await all results** (TaskOutput with block=true)

4. **Classify each finding:**
   - **Validated:** evidence-validator says "supports" AND adversary says "not refuted"
   - **Speculative:** evidence says "L1" OR adversary says "refuted"
   - **Rejected:** both say negative

5. **Report:**
   ```json
   {
     "status": "complete",
     "mode": "adjudicate",
     "findings": [
       {
         "finding": "<text>",
         "classification": "validated|speculative|rejected",
         "evidence_check": "supports|L1-speculative|no-evidence",
         "adversarial_check": "not_refuted|refuted",
         "reason": "<explanation>"
       }
     ],
     "summary": { "validated": N, "speculative": M, "rejected": K }
   }
   ```

**Note:** If `tp-fpf:fpf-evidence-validator` is not available (partial install), skip evidence validation and note it. If `tp-sadd:sadd-judge` is not available, use `core-principled:tp-critic` as fallback adversarial agent.

---

## CONTRAST
NOT for diagnose (session patterns vs code bugs), NOT for code-review (workflow anti-patterns vs code quality)

## Reference Index

IF performing structured data extraction (INSPECT) → spawn **`session-inspector`**
IF performing behavioral diagnosis (REVIEW) → spawn **`session-meta-reviewer`**
IF performing deep investigation (INVESTIGATE) → spawn **`session-meta-reviewer`** and **`session-context-analyzer`**
IF performing context and outcome analysis → spawn **`session-context-analyzer`**
IF performing privacy audit and issue body construction (ISSUE) → spawn **`session-issue-generator`**
IF performing forensic log analysis (CROSS-ANALYZE) → spawn **`session-inspector`**
