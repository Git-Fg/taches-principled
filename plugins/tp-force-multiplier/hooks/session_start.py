#!/usr/bin/env python3
"""Lightweight session start coaching."""
import json
import sys

payload = json.load(sys.stdin)

# Comprehensive coaching - all native capabilities mandate
print(json.dumps({
    "systemMessage": "Essential: For any task involving exploration, implementation, self-review, self-critic, or similar work, spawn subagents immediately and run them in parallel. Do not wait until you are stuck. If a task has independent parts, fan out subagents without hesitation. If a workflow matches a skill, tool, or subagent pattern, invoke it immediately and use it aggressively. Do not wait for complexity to build. If a capability exists and context matches, deploy it without hesitation. All capabilities are mandatory — heavy use is correct behavior."
}))
sys.exit(0)