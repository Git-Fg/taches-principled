#!/usr/bin/env python3
"""
Regenerate .claude-plugin/marketplace.json from its SSoT sources.

Schema compliance (per knowledge/raw/official/plugins/marketplaces.md):
  The official Claude Code marketplace schema requires a flat top-level
  structure: `name`, `owner`, `plugins`. Anything else at the top level
  is rejected by the CLI at `claude plugin marketplace add` time.

Three-source model (post #47 fix):
  - Per-plugin plugin.json: name, version, description (spec-authoritative)
  - .claude-plugin/_meta.json: source, homepage, repository, license,
    category, keywords (catalog-only metadata) AND marketplace-level
    metadata under a top-level "marketplace" key (name, owner, etc.)
  - The output marketplace.json has the schema-compliant shape:
        { "name", "owner", "description", "version", "$schema", "plugins": [...] }

When to run:
  - After editing any per-plugin .claude-plugin/plugin.json
  - After editing .claude-plugin/_meta.json
  - Before committing changes to either source

How to verify:
  jq -e '.plugins | all(. as $p | ([keys[] | select(. == "version")] | length) == 1)' \\
    .claude-plugin/marketplace.json

  jq -e 'has("name") and has("owner") and has("plugins") and (.plugins | type == "array")' \\
    .claude-plugin/marketplace.json

The CI workflow validate-marketplace.yml runs both checks on every PR.
"""

import json
import pathlib

SCRIPT_DIR = pathlib.Path(__file__).parent.resolve()
REPO_ROOT = SCRIPT_DIR.parent
CLAUDE_PLUGIN_DIR = REPO_ROOT / ".claude-plugin"
META_PATH = CLAUDE_PLUGIN_DIR / "_meta.json"
MARKETPLACE_PATH = CLAUDE_PLUGIN_DIR / "marketplace.json"
PLUGINS_DIR = REPO_ROOT / "plugins"

MARKETPLACE_SCHEMA_URL = "https://anthropic.com/claude-code/marketplace.schema.json"


def regenerate() -> None:
    """Regenerate marketplace.json from the three SSoT sources."""
    with open(META_PATH) as f:
        meta = json.load(f)

    marketplace_meta = meta.get("marketplace", {})

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

    output = {
        "$schema": MARKETPLACE_SCHEMA_URL,
        "name": marketplace_meta["name"],
        "owner": marketplace_meta["owner"],
        "description": marketplace_meta.get("description", ""),
        "version": marketplace_meta.get("version", ""),
        "plugins": plugins,
    }

    with open(MARKETPLACE_PATH, "w") as f:
        json.dump(output, f, indent=2)
        f.write("\n")


if __name__ == "__main__":
    regenerate()