#!/usr/bin/env python3
"""Coaching before context pressure."""
import json
import sys

print(json.dumps({
    "decision": {
        "notification": {
            "message": "Consider spawning subagents to offload work before context pressure increases."
        }
    }
}))