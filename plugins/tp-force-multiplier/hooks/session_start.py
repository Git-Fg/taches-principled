#!/usr/bin/env python3
"""Lightweight session start coaching."""
import json
import sys

payload = json.load(sys.stdin)

# Comprehensive coaching - all native capabilities mandate
print(json.dumps({
    "systemMessage": "Essential: For any task involving exploration, implementation, self-review, self-critic, or similar work, spawn subagents immediately and run them in parallel. Do not wait until you are stuck. If a task has independent parts, fan out subagents without hesitation. Also: Use and abuse skills, tools, and subagents from session start — they are not optional, they are the job. Heavy capability deployment is correct behavior."
}))
sys.exit(0)