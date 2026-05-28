#!/usr/bin/env python3
"""Lightweight session start coaching."""
import json
import sys

payload = json.load(sys.stdin)

# Comprehensive coaching - subagents AND skills mandate
print(json.dumps({
    "systemMessage": "Essential: For any task involving exploration, implementation, self-review, self-critic, or similar work, spawn subagents immediately and run them in parallel. Do not wait until you are stuck. If a task has independent parts, fan out subagents without hesitation. Also: Proactively load and abuse skills for method frameworks, debugging, review, critique, simplification, ideation, planning, and implementation. Skills are not optional — use them from session start. If a workflow matches a known skill pattern, load it immediately."
}))
sys.exit(0)