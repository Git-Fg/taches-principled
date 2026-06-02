#!/usr/bin/env python3
"""Lightweight session start coaching."""
import json
import sys

payload = json.load(sys.stdin)

# Coaching - three gates before subagent fan-out
print(json.dumps({
    "hookSpecificOutput": {
        "hookEventName": "SessionStart",
        "additionalContext": "Before spawning subagents, verify three gates: (1) Is this task non-trivial? (2) Are parts independent and parallelizable? (3) Will delegation save total work, or just shift it? Skip delegation if any answer is no. Subagent fan-out is a cost-bearing decision, not a default."
    }
}))
sys.exit(0)