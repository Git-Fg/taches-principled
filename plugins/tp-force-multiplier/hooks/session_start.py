#!/usr/bin/env python3
"""Lightweight session start coaching."""
import json
import sys

payload = json.load(sys.stdin)

# Strong coaching - mandatory language
print(json.dumps({
    "decision": {
        "notification": {
            "message": "Essential: Spawn subagents for parallel investigation. Load skills for method frameworks on complex workflows."
        }
    }
}))