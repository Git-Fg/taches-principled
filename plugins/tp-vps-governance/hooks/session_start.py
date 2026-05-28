#!/usr/bin/env python3
"""Session start hook for tp-vps-governance plugin."""
import json
import os
import sys

HOOKS_JSON_PATH = os.path.join(os.path.dirname(__file__), "hooks.json")
RULES_MANIFEST_PATH = os.path.expanduser("~/.claude/vps-governance/rules-manifest.yaml")


def load_hooks_config():
    """Load and validate hooks.json configuration."""
    try:
        with open(HOOKS_JSON_PATH, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError, IOError):
        return None


def check_rules_manifest_exists():
    """Check if rules-manifest.yaml exists at expected location."""
    return os.path.isfile(RULES_MANIFEST_PATH)


def main():
    """Main entry point for SessionStart hook."""
    config = load_hooks_config()
    if config is None:
        sys.exit(0)

    if not check_rules_manifest_exists():
        notification_msg = (
            "VPS Governance: rules-manifest.yaml not found at ~/.claude/vps-governance/rules-manifest.yaml. "
            "Run /rule-propagator init to initialize the rules manifest."
        )
        output = {
            "decision": {
                "notification": {
                    "message": notification_msg
                }
            }
        }
        print(json.dumps(output))

    sys.exit(0)


if __name__ == "__main__":
    main()