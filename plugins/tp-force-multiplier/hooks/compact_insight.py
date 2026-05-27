#!/usr/bin/env python3
"""Coaching before context pressure."""
import json
import sys

print(json.dumps({
    "decision": {
        "notification": {
            "message": "Pattern: Context pressure increasing. Subagent fan-out distributes work before capacity constraints — consider delegation before complexity compounds."
        }
    }
}))
sys.exit(0)