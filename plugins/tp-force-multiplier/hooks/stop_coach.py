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
        "systemMessage": "Essential: If you find yourself executing 5+ sequential operations, stop and fan out. Do not wait until you are stuck. Complex work that could be distributed benefits from parallel delegation — spawn investigators to explore independently without hesitation."
    }))
    sys.exit(0)

# Skill gap detection: complex workflow without skill loaded
has_skill_load = '/skill' in transcript.lower() or 'SKILL.md' in transcript
tool_patterns = ['Read', 'Grep', 'Edit', 'Write', 'Bash', 'Search']
pattern_count = sum(transcript.count(f'"tool": "{t}"') for t in tool_patterns)

# Complex workflow: high tool count without skills
if pattern_count >= 6 and not has_skill_load and tool_count >= 8:
    # Essential: invoke skills before complexity compounds
    print(json.dumps({
        "systemMessage": "Essential: If you find yourself repeating complex workflows without loading skills, subagents, or other native tools, stop and invoke them immediately. Do not wait for complexity to build. When patterns repeat, capabilities can encode the method — deploy them without hesitation and use them aggressively."
    }))
    sys.exit(0)

sys.exit(0)