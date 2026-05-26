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
            "message": "Essential: Proactively load and abuse skills for method frameworks, debugging, review, critique, simplification, ideation, planning, and implementation. Skills are not optional, use them from session start. If a workflow matches a known skill pattern, load it immediately."
        }
    }
}))