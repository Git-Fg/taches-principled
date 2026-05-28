#!/usr/bin/env python3
"""Coaching before context pressure."""
import json
import sys

# PostCompact hook - output systemMessage for coaching
print(json.dumps({
    "systemMessage": "Essential: If context pressure is increasing, fan out immediately. Do not wait until you are stuck. Before complexity compounds, deploy all capabilities — skills, tools, and subagents. Context constraints are a signal to distribute work, not a signal to compress it."
}))
sys.exit(0)