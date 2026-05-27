#!/usr/bin/env python3
"""Lightweight session start coaching."""
import json
import sys

payload = json.load(sys.stdin)

# Subagents tip - advisory framing
print(json.dumps({
    "decision": {
        "notification": {
            "message": "Pattern: Tasks with independent parts benefit from parallel fan-out. When work can be distributed, spawn subagents for exploration, implementation, verification, or critique. Delegation accelerates; sequential execution bottlenecks."
        }
    }
}))
sys.exit(0)

# Skills tip - advisory framing
print(json.dumps({
    "decision": {
        "notification": {
            "message": "Pattern: Available skills encode proven methods — consider loading when context suggests methodological advantage. Relevant skills reduce pattern reinvention; skipping them means carrying complexity manually."
        }
    }
}))
sys.exit(0)