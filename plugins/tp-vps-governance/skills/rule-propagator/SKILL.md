---
name: rule-propagator
description: "Sync shared rules to subagent fleet by injecting frontmatter references. Solves the rule isolation gap where subagents don't inherit user rules."
when_to_use: |
  Use when the user says:
  - "sync rules"
  - "propagate rules to agents"
  - "update agent configurations"
  - "fix rule isolation"
  - "init rules manifest"
  IMMEDIATELY after adding new project rules that subagents need.
  Do NOT use for auditing rules (use config-auditor) or memory cleanup (use memory-curator).
argument-hint: "[init|apply|status|dry-run] [--yes] [--manifest path]"
---

## CONTRAST with Other Skills

- **config-auditor**: analyzes config hierarchy for conflicts
- **memory-curator**: audits and deduplicates memory files
- **THIS**: syncs shared rules to subagent fleet via frontmatter injection

---

## Decision Router

IF manifest doesn't exist → prompt for **INIT** first
IF user wants to create/reset manifest → **INIT** mode
IF user wants to apply rules to agents → **APPLY** mode (default)
IF user wants to check sync status → **STATUS** mode
IF user wants to preview changes → **DRY-RUN** mode

All write modes default to `--dry-run`. Use `--yes` to execute.

---

## INIT Mode

Initialize the rules manifest and shared-rules skill.

### Process

1. **Check existing** — Look for `rules-manifest.yaml` at `~/.claude/vps-governance/`
2. **Create directory** — `mkdir -p ~/.claude/vps-governance/`
3. **Write manifest** — Copy from `{baseDir}/templates/rules-manifest.yaml`
4. **Scan for agents** — Glob `plugins/*/agents/*.md` to discover agent definitions
5. **Populate manifest** — Add discovered agents to `agent_patterns`
6. **Create shared-rules** — Create `skills/shared-rules/SKILL.md` with placeholder content
7. **Output** — Show initialized manifest and next steps:
   ```
   Created: ~/.claude/vps-governance/rules-manifest.yaml
   Discovered: 12 agent definitions
   Next: Run /rule-propagator apply --yes to inject shared-rules
   ```

---

## APPLY Mode

Inject shared-rules skill into agent frontmatter.

### Process

1. **Read manifest** — Load rules-manifest.yaml
2. **For each agent pattern** in manifest:
   a. Glob for matching agent files
   b. For each agent file:
      - Parse YAML frontmatter
      - Check if shared-rules skill already in `skills:` list
      - If missing: show diff of what would be added
3. **Resolve conflicts** (if `conflict_detection: true`):
   - Check `last_sync` timestamp vs file modification time
   - If agent was modified since last sync: warn, skip by default
   - With `--force`: override manual modifications
4. **Dry-run** (default): Show all diffs, write nothing
5. **With --yes**: Write changes to agent files
6. **Update manifest**: Set `last_sync` to current timestamp
7. **Commit**: `git add` changed agent files + manifest, commit with message:
   ```
   feat(rule-propagator): sync shared-rules to {count} agents
   ```

### Conflict Detection

```
WARNING: Agent modified since last sync
  File: plugins/tp-fpf/agents/hypothesis-generator.md
  Last sync: 2025-05-20T10:00:00Z
  Modified:  2025-05-28T14:30:00Z
  A manual edit was made after the last sync.
  Use --force to override, or review manually.
```

---

## STATUS Mode

Check synchronization state across the fleet.

### Process

1. **Read manifest** — Load rules-manifest.yaml
2. **For each agent pattern**:
   - Glob for matching files
   - Compare frontmatter `skills:` list with manifest `inject:` list
   - Classify: synced / drifted / missing
3. **Output status**:
   ```
   Rule Propagation Status
   ========================
   Synced:   8 agents
   Drifted:  2 agents (modified since last sync)
   Missing:  1 agent (since removed)

   Last sync: 2025-05-20T10:00:00Z
   Agents tracked: 11
   ```

---

## DRY-RUN Mode

Preview all changes without writing.

### Process

1. Execute APPLY logic with all writes suppressed
2. Show complete diff for each file that would change
3. Summary: files changed, agents affected, estimated token overhead