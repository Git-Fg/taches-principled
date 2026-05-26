#!/usr/bin/env python3
"""Lightweight session start coaching."""
import json
import sys

payload = json.load(sys.stdin)

# Simple coaching - no tracking, just context
print(json.dumps({
    "decision": {
        "notification": {
            "message": "Tip: Spawn subagents for parallel investigation. Use skills for method frameworks when workflows are complex."
        }
    }
}))