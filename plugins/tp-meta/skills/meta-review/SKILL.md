---
name: meta-review
description: "Review Claude Code session transcripts for behavioral anti-patterns and investigate root causes."
allowed-tools: Read, Glob, Grep, Bash, Agent
when_to_use: "Use when user wants to review a session for anti-patterns or investigate the root cause of a session failure."
argument-hint: "[review|investigate] [latest|<session-id>] [--concern <description>]"
---

## Routing Guidance

- REVIEW: 'what went wrong', 'self-review', 'self-critic', 'review my session', 'analyze my behavior', 'meta-review', 'behavioral review', 'session review'
- INVESTIGATE: 'investigate what happened', 'why did it fail', 'root cause of session', 'dig into the transcript', 'deep investigation'
- IMMEDIATELY when user wants to understand behavioral issues in a Claude Code session.
- FIRST when something went wrong and user wants structured analysis before filing a report.
- CONTRAST with diagnose: meta-review analyzes session transcripts; diagnose analyzes code problems.

## What This Skill Changes

**Default behavior:** Claude ends sessions without systematic behavioral review — anti-patterns surface only when the user explicitly asks, and no systematic recording exists. Root causes are discussed conversationally, if at all, and rarely traced to actionable vs excluded scope.

**With this skill:** Every session gets a structured behavioral review. The main agent never reads the JSONL directly — it delegates to a dedicated diagnostic agent. Findings are scoped (PLUGIN/USER-FILE/ENVIRONMENT/MODEL) so only actionable items reach GitHub. INVESTIGATE mode fans out 3 parallel subagents to avoid cross-contamination in findings.

**Why mode separation:** REVIEW is quick (one subagent, 5 min) for obvious problems. INVESTIGATE is deep (3 subagents, systemic root cause) for structural or recurring failures.

---

## Decision Router

IF user wants to understand what went wrong in a session → **REVIEW** mode (default)
IF user wants deep investigation with subagent fan-out → **INVESTIGATE** mode

---

## REVIEW Mode

Quick diagnostic of the most recent or specified session.

### Process

1. **Discover session** — find the target transcript at `~/.claude/sessions/{uuid}/raw-transcript.jsonl`
   - If no session specified: use `ls -t ~/.claude/sessions/ | head -1`
   - Validate the file exists and is non-empty

2. **Spawn meta-reviewer subagent** with the transcript path and any user concern
   - The subagent reads the full JSONL and produces the behavioral analysis
   - Wait for the subagent to return its findings file path

3. **Present findings** — read the subagent's output and summarize:
   - Anti-patterns found (PLUGIN scope only — actionable ones)
   - What went well
   - Scope verdict (is this reportable?)

4. **Next step suggestion** — if actionable findings exist, suggest running `meta-issue` to create a GitHub issue

---

## INVESTIGATE Mode

Deep investigation with parallel subagent fan-out.

### Process

1. **Discover session** — same as REVIEW

2. **Spawn 3 parallel subagents**:
   - **Diagnostic subagent** (meta-reviewer agent): reads transcript, identifies anti-patterns and root cause scope
   - **Context subagent** (general-purpose): checks git state from the session — `git log --oneline -5`, `git diff --stat`, branch name
   - **Good/Bad subagent** (general-purpose): reads transcript, extracts what worked well vs what broke, with specific event evidence

3. **Synthesize** — after all subagents return:
   - Merge findings into a unified report
   - Cross-reference: do the git state changes explain any anti-patterns?
   - Deduplicate findings across subagents
   - Assign severity: HIGH (actionable PLUGIN root cause), MEDIUM (possible improvement), LOW (informational)

4. **Scope gate** — check:
   - Are ALL findings USER-FILE scope? → Report NOT advised
   - Are ANY findings PLUGIN scope? → Report advised, include specific suggestions
   - Is the session a marketplace-only session (no rules/hooks)? → Narrow scope to plugin behavior only

5. **Write unified report** to `.principled/scratch/meta-review-{session_id}.md`

6. **Present to user** — summary with option to proceed to `meta-issue`

---

## Privacy

This skill handles session transcripts which may contain sensitive information. The meta-reviewer agent is instructed to strip:
- File contents from the user's workspace
- User prompts verbatim (paraphrase intent only)
- Project directory paths
- Environment variables, tokens, credentials

The output report contains only behavioral patterns, tool names, error categories, and suggestions.

---

## Execution Mode

**Default: subagent delegation.** For transcript analysis, spawn the meta-reviewer agent. For investigation, spawn 3 parallel subagents. The main agent synthesizes results; it never performs transcript analysis inline.

**Spawn pattern:**
- Scope: session transcript at `~/.claude/sessions/{uuid}/raw-transcript.jsonl`
- Role: meta-reviewer (diagnostic), general-purpose (context, good/bad analysis)
- Output: `.principled/scratch/meta-review-{session_id}.md`
