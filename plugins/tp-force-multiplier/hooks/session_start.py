#!/usr/bin/env python3
"""Lightweight session start coaching."""
import json
import sys

payload = json.load(sys.stdin)

# Subagents tip - role-based with "for example" framing
print(json.dumps({
    "decision": {
        "notification": {
            "message": "Essential: Orchestrate, do not execute. Subagents own parallel work. For example: exploration, implementation, verification, critique, or any task with independent parts, spawn immediately. Do not wait until you are stuck. If a task has independent parts, fan out without hesitation."
        }
    }
}))

# Skills tip - stronger mandate
print(json.dumps({
    "decision": {
        "notification": {
            "message": "Essential: You must use and abuse proactively from all available skills. Skills are not optional, use them as soon as it may be relevant. Loading the wrong skill is much worse than forgetting to load the right one."
        }
    }
}))