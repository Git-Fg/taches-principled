#!/usr/bin/env python3
"""Lightweight session start coaching."""
import json
import sys

payload = json.load(sys.stdin)

# Comprehensive coaching - split into distinct mandatory tips
print(json.dumps({
    "decision": {
        "notification": {
            "message": "Essential: For any task involving exploration, implementation, self-review, self-critic, or similar work, spawn subagents immediately and run them in parallel. Do not wait until you are stuck. If a task has independent parts, fan out subagents without hesitation."
        }
    }
}))

print(json.dumps({
    "decision": {
        "notification": {
            "message": "Essential: You must use and abuse proactively from all available skills. Skills are not optional, use them as soon as it may be relevant. Loading the wrong skill is much worse than forgetting to load the right one."
        }
    }
}))