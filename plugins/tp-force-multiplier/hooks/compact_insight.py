#!/usr/bin/env python3
"""Coaching before context pressure."""
import json
import sys

print(json.dumps({
    "decision": {
        "notification": {
            "message": "MANDATORY: Spawn subagents now to offload work before context pressure increases."
        }
    }
}))