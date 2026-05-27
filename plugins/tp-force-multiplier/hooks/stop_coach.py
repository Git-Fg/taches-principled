#!/usr/bin/env python3
"""Coach at turn end based on observed patterns."""
import json
import sys
from pathlib import Path

payload = json.load(sys.stdin)
transcript = Path(payload['transcript_path'])

if not transcript.exists():
    sys.exit(0)

content = transcript.read_text()

# Detect: no subagent spawn in this turn, 5+ tool calls
has_subagent = '"SubagentStart"' in content
tool_count = content.count('"tool":')

if tool_count >= 5 and not has_subagent:
    # Pattern: sequential work that could be distributed
    print(json.dumps({
        "decision": {
            "notification": {
                "message": "Pattern: 5+ tools executed without parallel delegation. Complex work that could be distributed benefits from fan-out — spawn investigators to explore independently."
            }
        }
    }))
    sys.exit(0)

# Skill gap detection: complex workflow without skill loaded
# Look for patterns suggesting need for method frameworks
# Semantic detection - no hardcoded skill names

has_skill_load = '/skill' in content.lower() or 'SKILL.md' in content
read_count = content.count('"tool": "Read"')
grep_count = content.count('"tool": "Grep"')
edit_count = content.count('"tool": "Edit"')

# Complex investigation: 3+ reads and greps
complex_investigation = read_count >= 3 and grep_count >= 1

# Complex creation: reads followed by writes/edits
complex_creation = read_count >= 2 and (edit_count >= 1 or content.count('"tool": "Write"') >= 1)

if (complex_investigation or complex_creation) and not has_skill_load and tool_count >= 8:
    # Pattern: workflow complexity suggests method framework
    print(json.dumps({
        "decision": {
            "notification": {
                "message": "Pattern: Repeated Read/Grep/Edit without method framework. When investigation or creation workflows repeat, a skill can encode the pattern — consider loading relevant guidance."
            }
        }
    }))
    sys.exit(0)