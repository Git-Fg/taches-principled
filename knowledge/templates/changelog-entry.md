```markdown
## [1.2.3] — YYYY-MM-DD

### Added
### Changed
### Removed
### Fixed

### AUDIT  (use when the entry is driven by a meta-review or full-audit cycle)
- One-line summary of audit scope (e.g. "P1-P6 subagent contract redesign; 7 agents gained tools: lists")
- Link to the audit artifact (e.g. `.principled/plans/AUDIT-YYYY-MM-DD.md`)
- Per-finding resolution: which findings were Fixed, which were Skipped, which were Deferred

### Skip notes  (use when an audit issue is closed without a code change)
- Format: `**{issue-id}** ({one-line summary}) — {rationale with citation}`

### Out of scope  (use when audit findings are explicitly deferred to a later release)
- Format: `**{issue-id} {finding-id}** — {one-line description}. {effort estimate}. {when to do it}.`
```

## CHANGELOG Entry Conventions

The four canonical sections (Added/Changed/Removed/Fixed) cover most entries.
Three additional sections are reserved for specific entry types:

- **AUDIT** — used when the entry is driven by a meta-review or full-audit
  cycle. Cite the audit artifact in `.principled/plans/`. Per-finding
  resolution belongs in this section, not in Fixed.
- **Skip notes** — used when an audit issue is closed without a code
  change. Always cite the issue number and the rationale with evidence
  (date, channel, observation). The 1.12.0 Skip notes block was the
  template for this style.
- **Out of scope** — used when audit findings are explicitly deferred
  to a later release. Always include an effort estimate and a trigger
  for when to revisit. The 1.14.0 Out of scope block was the template.