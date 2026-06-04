#!/usr/bin/env python3
"""
Regenerate .claude-plugin/marketplace.json from its two SSoT sources.

Two-source catalog model (per CLAUDE.md and docs/official/plugins/marketplaces.md):
  - Per-plugin plugin.json: name, version, description (spec-authoritative)
  - .claude-plugin/_meta.json: source, homepage, repository, license,
    category, keywords (catalog-only metadata)

When to run:
  - After editing any per-plugin .claude-plugin/plugin.json
  - After editing .claude-plugin/_meta.json
  - Before committing changes to either source

How to verify:
  jq -e '.plugins | all(. as $p | ([keys[] | select(. == "version")] | length) == 1)' \
    .claude-plugin/marketplace.json

The CI workflow validate-marketplace.yml runs the same check on every PR.
"""

import json
import pathlib

SCRIPT_DIR = pathlib.Path(__file__).parent.resolve()
REPO_ROOT = SCRIPT_DIR.parent
CLAUDE_PLUGIN_DIR = REPO_ROOT / ".claude-plugin"
META_PATH = CLAUDE_PLUGIN_DIR / "_meta.json"
MARKETPLACE_PATH = CLAUDE_PLUGIN_DIR / "marketplace.json"
PLUGINS_DIR = REPO_ROOT / "plugins"


def regenerate() -> None:
    """Regenerate marketplace.json from the two SSoT sources."""
    with open(META_PATH) as f:
        meta = json.load(f)

    plugins = []
    for plugin_dir in sorted(PLUGINS_DIR.iterdir()):
        plugin_json_path = plugin_dir / ".claude-plugin" / "plugin.json"
        if not plugin_json_path.exists():
            continue
        with open(plugin_json_path) as f:
            data = json.load(f)
        plugin_meta = meta.get(data["name"], {})
        entry = {
            "name": data["name"],
            "version": data["version"],
            "description": data["description"],
        }
        entry.update(
            {k: plugin_meta[k] for k in ("source", "homepage", "repository", "license", "category", "keywords") if k in plugin_meta}
        )
        plugins.append(entry)

    with open(MARKETPLACE_PATH, "w") as f:
        json.dump({**meta, "plugins": plugins}, f, indent=2)


if __name__ == "__main__":
    regenerate()