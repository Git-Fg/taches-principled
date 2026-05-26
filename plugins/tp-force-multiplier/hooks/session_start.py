#!/usr/bin/env python3
"""Lightweight session start coaching."""
import json
import sys

payload = json.load(sys.stdin)

# Comprehensive coaching - proactive subagent/skill usage
print(json.dumps({
    "decision": {
        "notification": {
            "message": "Essential: Proactively spawn subagents for exploration, implementation, self-review, and self-critic tasks. Use them in parallel — do not wait until you are stuck. Load skills for method frameworks. The pattern is: if a task has independent parts, fan out subagents immediately."
        }
    }
}))