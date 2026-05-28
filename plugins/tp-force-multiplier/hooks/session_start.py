#!/usr/bin/env python3
"""Lightweight session start coaching via systemMessage."""
import json
import sys

# Read input (discard - we don't need it for this hook)
try:
    json.load(sys.stdin)
except:
    pass

# SessionStart hook: output systemMessage for immediate coaching hint
# Valid output fields for SessionStart: continue, suppressOutput, stopReason,
# decision (approve/block), reason, systemMessage, terminalSequence, permissionDecision
print(json.dumps({
    "systemMessage": "Pattern: Tasks with independent parts benefit from parallel fan-out. When work can be distributed, spawn subagents for exploration, implementation, verification, or critique. Delegation accelerates; sequential execution bottlenecks."
}))
sys.exit(0)