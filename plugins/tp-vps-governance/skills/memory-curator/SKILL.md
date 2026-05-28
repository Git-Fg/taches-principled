---
name: memory-curator
description: "Audit, deduplicate, and archive Claude Code memory files. Cleans auto-memory and agent-memory that accumulate on long-running VPS instances."
when_to_use: |
  Use when the user says:
  - "audit memory"
  - "clean up auto-memory"
  - "curate agent memory"
  - "memory hygiene"
  - "deduplicate memory"
  FIRST on VPS instances running for 30+ days.
  Do NOT use for auditing rules (use config-auditor) or propagating rules (use rule-propagator).
argument-hint: "[audit|dedup|archive|clean] [--dry-run] [--yes] [--days 30]"
---

## CONTRAST with Other Skills

- **config-auditor**: analyzes config hierarchy for conflicts
- **rule-propagator**: syncs shared rules to subagent fleet
- **THIS**: maintains memory hygiene (auto-memory + agent-memory)

---

## Decision Router

IF user wants comprehensive overview → **AUDIT** mode (default)
IF user wants to merge duplicates → **DEDUP** mode
IF user wants to archive stale entries → **ARCHIVE** mode
IF user wants full maintenance → **CLEAN** mode (combines dedup + archive)

All modes default to `--dry-run`. Destructive operations require `--yes`.

---

## AUDIT Mode

Discover and analyze all Claude Code memory locations.

### Process

1. **Discover memory locations**:
   - `~/.claude/projects/*/memory/MEMORY.md` — per-project auto-memory
   - `~/.claude/agent-memory/*/` — per-agent persistent memory
   - `.principled/memory/` — project-level plugin memory
   - `.principled/scratch/` — temporary working files

2. **For each location**:
   - Count files, total lines, total size
   - Calculate age range (oldest → newest entry)
   - Detect issues

3. **Detect issues**:
   - **Duplicates**: same content hash or >80% text overlap
   - **Contradictions**: conflicting facts about same entity
   - **Obsolescence**: references to deleted files/projects
   - **Orphans**: entries for projects that no longer exist
   - **Bloat**: individual files >100KB

4. **Score health** per location:
   - Green: 0-1 issues
   - Yellow: 2-3 issues
   - Red: 4+ issues

5. **Output**:
   ```
   Memory Audit Report
   ===================
   Locations scanned: 5
   Total files: 47
   Total size: ~1.2MB

   ~/.claude/projects/foo/memory/: GREEN
   ~/.claude/agent-memory/critic/: YELLOW (2 duplicates)
   .principled/scratch/: RED (1 contradiction, 3 orphans)
   ```

---

## DEDUP Mode

Find and merge duplicate memory entries.

### Process

1. **Run audit** to discover duplicates
2. **For each duplicate group**:
   a. Show content preview (first 10 lines each)
   b. Recommend action: keep_newest / merge / archive_older
   c. Default recommendation: keep newest
3. **Dry-run** (default): show what would change
4. **With --yes**: apply merge/remove actions

### Output Format
```
Duplicate Group: 3 files, similarity 87%
- ~/.claude/projects/foo/memory/MEMORY.md (updated 2025-05-15)
- ~/.claude/agent-memory/critic/MEMORY.md (updated 2025-05-20)
- .principled/scratch/context.md (updated 2025-05-28)

Recommendation: Keep newest (context.md), archive older
Action: Move older to .principled/archive/memory/2025-05/
```

---

## ARCHIVE Mode

Archive stale memory entries.

### Process

1. **Run audit** with age threshold (default: 30 days, configurable via `--days`)
2. **Identify stale entries**:
   - Last modified > threshold days ago
   - Project no longer exists
   - Agent no longer exists
3. **Archive to**: `~/.claude/archive/memory/{category}/{date}/`
4. **Create manifest**: Track original paths for recovery
5. **Dry-run** (default): show what would be archived
6. **With --yes**: move files, update manifest

### Manifest Format
```yaml
archived: 2025-05-28T10:00:00Z
entries:
  - original: ~/.claude/projects/old-project/memory/MEMORY.md
    archived: ~/.claude/archive/memory/projects/2025-05/old-project-memory.md
    reason: project deleted
  - original: ~/.claude/agent-memory/deprecated-agent/
    archived: ~/.claude/archive/memory/agents/2025-05/deprecated-agent/
    reason: agent no longer used
```

---

## CLEAN Mode

Full maintenance: deduplication + archiving in one pass.

### Process

1. **Run dedup** (with auto-resolve using keep_newest)
2. **Run archive** (using --days threshold)
3. **Create backup** before any destructive action
4. **Always requires --yes** (safety: no dry-run default)
5. **Summary**: files removed, space freed, archived count

### Safety
- Pre-flight check: verify backup location is writable
- Atomic operations: copy before delete
- Recovery manifest: all archived files tracked with original paths