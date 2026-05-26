---
name: rules-orchestration
description: "Manages CLAUDE.md and .claude/rules/ lifecycle — analyzes conversations for rule-worthy insights, synthesizes proposals, integrates into rules, and maintains quality. Use when refining project conventions, updating CLAUDE.md after significant work, or codifying discovered patterns."
when_to_use: |
  Use when the user says:
  - "update my rules"
  - "refine CLAUDE.md"
  - "codify this convention"
  - "add this to my rules"
  - "rules need updating"
  - "my CLAUDE.md is bloated"
  - "extract rules from this conversation"
  - "standardize my project rules"
  - "optimize my .claude/rules/"
  IMMEDIATELY after significant skill execution (create-plans, execute-plans, refine) when conventions were established.
  FIRST when CLAUDE.md exceeds 200 lines or .claude/rules/ has more than 10 files.
  Do NOT use for one-off questions or temporary instructions.
  Do NOT modify managed/enterprise rules at system paths.
  CONTRAST with refine MEMORIZE: MEMORIZE captures to .principled/memory/learnings.md; rules-orchestration integrates into committed rules files.
argument-hint: "[ANALYZE|ADD|RESTRUCTURE|REVIEW|SYNC] [target]"
---

## Decision Router

IF user wants to extract insights from current/last conversation → **ANALYZE** mode
IF user wants to restructure or audit existing rules → **RESTRUCTURE** mode
IF user wants to add a specific convention to rules → **ADD** mode
IF user wants to review and approve pending proposals → **REVIEW** mode
IF user wants to sync with recent skill execution or learn output → **SYNC** mode
IF target is ambiguous → ask: "Analyze current conversation, restructure existing rules, add a specific convention, review pending proposals, or sync with recent work?"

---

## ANALYZE Mode

Extracts insights from conversation history or skill output and synthesizes them into structured rule proposals.

### When
After conversation or skill execution with discoverable conventions, anti-patterns, or decisions worth codifying.

### Process

1. **Capture context** — Read from `.principled/scratch/` or conversation summary. Determine the source: recent skill execution output, session transcript, or explicit user request.

2. **Extract insights** — Spawn a rules-analyzer subagent (read `{baseDir}/agents/rules-analyzer.md` first) to identify conventions, anti-patterns, tool preferences, architectural decisions, and domain knowledge. Pass the context path and instruct it to write findings to `.principled/scratch/rules-analysis-{timestamp}.md`.

3. **Synthesize proposals** — Read the analysis output. Convert raw insights into structured proposals with:
   - **Category**: TECHNICAL | PROCESS | PATTERN | ANTI-PATTERN | DECISION
   - **Priority**: critical | important | nice-to-have
   - **Target**: CLAUDE.md (global) or `.claude/rules/<name>.md` (path-scoped)
   - **Rationale**: Why this rule belongs in the project
   - **Rule text**: Draft rule content following `{baseDir}/references/rule-writing-guide.md`

4. **Write proposal file** — Save to `.principled/scratch/rules-proposals-{timestamp}.md` with all proposals in the structured format from the template.

5. **Present proposals** — Show user a numbered list of proposals with file targets and a one-line rationale. Ask: "Integrate these rules?"

6. **On approval** — Spawn a rules-integrator subagent (read `{baseDir}/agents/rules-integrator.md`) with the proposal file path and target files. The integrator applies changes and commits.

### Output
- Analysis: `.principled/scratch/rules-analysis-{timestamp}.md`
- Proposals: `.principled/scratch/rules-proposals-{timestamp}.md`
- Updated rules files (committed)

---

## RESTRUCTURE Mode

Audits and reorganizes existing rules to reduce bloat, eliminate duplication, and improve loading efficiency.

### When
CLAUDE.md exceeds 200 lines, `.claude/rules/` has more than 10 files, or rules feel disorganized.

### Process

1. **Audit current state** — Read all files in `.claude/rules/` and `CLAUDE.md`. Map: total line count, file count, any obvious duplication visible without analysis.

2. **Identify issues** — Spawn a rules-auditor subagent (read `{baseDir}/agents/rules-auditor.md` first) with full paths to all rules files. Instruct it to write findings to `.principled/scratch/rules-audit.md`.

3. **Design new structure** — Review the audit report. Design a reorganization:
   - Which files to split (target: under 200 lines each)
   - Which rules need `paths:` frontmatter added
   - Which duplicates to merge
   - Which deprecated rules to archive (move to `.principled/attic/rules/`)
   - Target directory structure

4. **Present plan** — Show before/after structure. For each blocker and warning from the audit, include the proposed fix. Ask: "Apply this restructure?"

5. **On approval** — Execute: create new files, move content, add frontmatter, delete originals, verify no broken references, commit.

---

## ADD Mode

Adds a single convention to the rules system with conflict checking and proper frontmatter.

### When
User explicitly wants to codify a specific convention.

### Process

1. **Capture intent** — Confirm what the user wants to codify. If vague, ask one clarifying question. If clear, proceed.

2. **Determine placement** — Apply the decision tree from `{baseDir}/references/rule-taxonomy.md`:
   - Universal across all files → CLAUDE.md
   - Specific to file types → `.claude/rules/<name>.md` with `paths:` frontmatter
   - Specific to a subsystem → `.claude/rules/<domain>/<name>.md`
   - Otherwise → `.claude/rules/<name>.md` (always-on)

3. **Draft rule** — Write the rule following `{baseDir}/references/rule-writing-guide.md`. Include:
   - Frontmatter: `name`, `description` (one sentence), `paths:` if scoped
   - Body: clear directive, Bad/Good examples
   - Rationale: why this rule

4. **Conflict check** — Grep existing rules for overlap or contradiction. If found, show the conflict and ask: "Merge with existing rule, replace it, or keep both with different scope?"

5. **Integrate and commit** — Apply with Edit tool (append to existing file) or Write tool (new file). Run `git add <file>` and `git commit -m "feat(rules): add [rule name] to [target file]"`. Report the commit URL or hash.

---

## REVIEW Mode

Multi-judge evaluation of pending rule proposals before integration.

### When
Pending proposals exist from ANALYZE or SYNC that need approval before being committed.

### Process

1. **Load proposals** — Find proposal files: `ls .principled/scratch/rules-proposals-*.md`. If multiple exist, use the most recent. If none exist, report and exit.

2. **Spawn review panel** — Dispatch 2-3 critic subagents in parallel (read `{baseDir}/agents/rules-auditor.md` for evaluation criteria). Give each critic the proposal file and this rubric:
   - **Clarity**: Is the rule text actionable? Is the rationale clear?
   - **Conflict**: Does this contradict or duplicate an existing rule?
   - **Efficiency**: Would adding this reduce or increase context cost?
   - **Shareability**: Is this team-relevant or personal preference?
   Instruct each to write their verdict to `.principled/scratch/rules-review-{critic-id}.md`.

3. **Aggregate verdict** — Read all review outputs. For each proposal: count approve/revise/reject votes. Present consensus:
   ```markdown
   | Rule | Verdict | Votes |
   |------|---------|-------|
   | rule-name | APPROVE | 3/3 |
   | rule-name | REVISE | 2/3 |
   | rule-name | REJECT | 1/3 |
   ```
   For REVISE: include specific concerns. For REJECT: include reason.

4. **Apply approved** — For APPROVE: spawn a rules-integrator subagent with approved proposals. For REVISE: present revision options to user. For REJECT: archive proposal with reason.

---

## SYNC Mode

Bridges the gap between ephemeral memory captures and durable rules integration. The learn command stores to memory; SYNC promotes durable insights to rules.

### When
After `learn` command captures insights, or after skill execution that established conventions not yet codified.

### Process

1. **Read sources** — Check for `.principled/memory/learnings.md`. Also scan `.principled/scratch/` for recent SUMMARY.md or execution output. If neither exists, report and exit.

2. **Extract candidates** — Read the memory/scratch files. Identify entries tagged with TECHNICAL, DECISION, or ANTI-PATTERN — these have the highest rule-worthiness.

3. **Check existing** — For each candidate, grep `.claude/rules/` and `CLAUDE.md` for overlap. Skip duplicates. Flag near-matches for human review.

4. **Propose additions** — Write candidate rules to `.principled/scratch/rules-sync-proposals-{timestamp}.md`. Tag each:
   - `auto`: critical/correctness — safe to integrate without approval
   - `review`: important/nice-to-have — needs human review

5. **Auto-integrate low-risk** — For `auto` tagged candidates: spawn rules-integrator directly. Notify user of changes.

6. **Queue for REVIEW** — For `review` tagged candidates: present to user and suggest REVIEW mode.

---

## Design Decisions

**Files as source of truth.** Rules are files on disk, not conversation state. All coordination via filesystem, not message passing.

**Propose-then-approve.** Never auto-apply without presenting proposals. Matches the refine self-critic pattern.

**No managed rules.** Explicit check: do not modify files under `/etc/claude-code/` or other system-managed paths.

**Minimal agents.** Three agents cover the full lifecycle: analyze (extract), audit (evaluate), integrate (apply). Reuse existing plugin-level agents where possible.
