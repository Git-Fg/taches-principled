#!/usr/bin/env python3
"""Lightweight session start coaching."""
import json
import sys

payload = json.load(sys.stdin)

# Comprehensive coaching - proactive subagent/skill usage
print(json.dumps({
    "decision": {
        "notification": {
            "message": "Essential: For any task involving exploration, implementation, self-review, or self-critic work — spawn subagents immediately and run them in parallel. Do not wait until you are stuck. Load skills for method frameworks. If a task has independent parts, fan out subagents without hesitation."
        }
    }
}))