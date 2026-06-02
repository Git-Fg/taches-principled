---
name: capture
description: Run a headless Claude Code session with canonical behavioral-verification capture flags and return artifact paths. Triggers when user says "capture session", "collect behavioral artifacts", "run verification capture", "profile a skill invocation", "audit skill routing", "measure hook in vivo". Use before meta-review or meta-issue when you need fresh artifacts.
when_to_use: Before behavioral verification, trigger collision testing, hook validation, or plugin A/B testing — whenever you need a fresh capture of Claude Code's actual behavior rather than analyzing an existing transcript.
user-invocable: true
allowed-tools: Bash
---

## Routing Guidance

This skill is triggered when the user wants to collect behavioral artifacts. Triggers include: "capture session", "profile a skill invocation", "audit skill routing", "measure hook in vivo", "run verification capture", "behavioral capture". The skill runs `claude -p` headlessly and returns artifact paths — it does NOT analyze artifacts (that is `session-inspect`'s job).

**Trigger phrases:** "capture", "profile", "behavioral capture", "headless capture", "run verification", "collect artifacts"

## Decision Router

IF user passes --help → display routing guidance and exit

## Execution Mode

**Default: subagent delegation.** For CAPTURE, spawn a Bash subagent to execute the headless capture command.

## CAPTURE Protocol

Generate a capture UUID and session ID, then run the canonical capture incantation:

1. **Generate identifiers:**
   ```bash
   UUID=$(uuidgen 2>/dev/null || python3 -c "import uuid; print(uuid.uuid4())")
   # Use UUID as the session-id — it must be a valid UUID format
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

4. **Wait for completion** (the Bash subagent blocks until the capture finishes).

5. **Report artifact paths:**
   Return the three artifact paths to the main agent:
   - Debug log: `~/.claude/captures/<UUID>.debug.log`
   - Stream-json: `~/.claude/captures/<UUID>.stream.jsonl`
   - Persisted JSONL: `~/.claude/projects/<encoded-cwd>/<UUID>.jsonl`

6. **Store the session ID** in a local marker file for downstream skills to reference:
   ```bash
   echo "$UUID" > ~/.claude/captures/.last-capture-id
   ```

## Artifact Provenance

| Artifact | Path | Best for |
|---|---|---|
| Debug log | `~/.claude/captures/<UUID>.debug.log` | Hook fires, permission gates, plugin sync, MCP errors |
| Stream-json | `~/.claude/captures/<UUID>.stream.jsonl` | Streaming behavior, partial chunks, early termination |
| Persisted JSONL | `~/.claude/projects/<encoded-cwd>/<UUID>.jsonl` | Tool calls, results, usage, errors |

## Downstream Usage

After CAPTURE, route to `session-inspect` for artifact parsing, then to `meta-review` for analysis.

The `session-inspect` skill accepts any artifact path and routes to the correct parser based on file extension/content.
