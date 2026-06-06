---
name: marketplace-integrity
description: marketplace.json is derived, never hand-edited. Single sources of truth per CHANGELOG 1.14.0.
---

# Rule: MUST regenerate marketplace.json from plugin.json + _meta.json

**Why:** Hand-editing marketplace.json creates drift between plugin metadata and catalog metadata. The two-source model (plugin.json for name/version/description, _meta.json for everything else) prevents mismatches. Any hand-edit is guaranteed to be overwritten on next regeneration.

## Rule

- NEVER edit `.claude-plugin/marketplace.json` directly.
- Edit `plugins/<name>/.claude-plugin/plugin.json` for name, version, description.
- Edit `.claude-plugin/_meta.json` for source, homepage, repository, license, category, keywords.
- Regenerate with: `python3 scripts/regenerate-marketplace.py`.
- Bump plugin version (minor for features, patch for fixes/docs) before regenerating.

## Bad / Good

**Bad:** Editing marketplace.json to set a new description — change silently overwritten on next regeneration.
**Good:** Edit plugin.json, bump version, run regenerate script, commit both files atomically.

**Bad:** Forgetting to bump version before regenerating — marketplace shows stale version.
**Good:** Edit plugin.json version → regenerate → both files updated in same commit.
