#!/usr/bin/env python3
"""Coach at turn end based on observed patterns."""
import json
import sys

payload = json.load(sys.stdin)

# Stop hook receives transcript as content, not path
transcript = payload.get('transcript', '')

if not transcript:
    sys.exit(0)

# Detect: no subagent spawn in this turn, 5+ tool calls
has_subagent = 'SubagentStart' in transcript or 'subagent' in transcript.lower()
tool_count = transcript.count('"tool":')

if tool_count >= 5 and not has_subagent:
    # Essential: parallelize when complexity builds
    print(json.dumps({
        "systemMessage": "Essential: If you find yourself executing 5+ sequential tools, stop and fan out. Do not wait until you are stuck. Complex work that could be distributed benefits from parallel delegation — spawn investigators to explore independently without hesitation."
    }))
    sys.exit(0)

# Skill gap detection: complex workflow without skill loaded
has_skill_load = '/skill' in transcript.lower() or 'SKILL.md' in transcript
read_count = transcript.count('"tool": "Read"')
grep_count = transcript.count('"tool": "Grep"')
edit_count = transcript.count('"tool": "Edit"')

# Complex investigation: 3+ reads and greps
complex_investigation = read_count >= 3 and grep_count >= 1

# Complex creation: reads followed by writes/edits
complex_creation = read_count >= 2 and (edit_count >= 1 or '"tool": "Write"' in transcript)

if (complex_investigation or complex_creation) and not has_skill_load and tool_count >= 8:
    # Essential: invoke skills before complexity compounds
    print(json.dumps({
        "systemMessage": "Essential: If you find yourself repeating Read/Grep/Edit patterns without loading a skill, stop and invoke one immediately. Do not wait for complexity to build. When workflows repeat, a skill can encode the pattern — load it without hesitation and use it aggressively."
    }))
    sys.exit(0)

sys.exit(0)