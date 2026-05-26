---
name: force-multiplier
description: Override skill for force-multiplier plugin hooks — customize coaching behavior and patterns. Use when you want to customize how the plugin observes and coaches subagent/skill usage.
when_to_use: When you want to customize the coaching thresholds, message phrasing, or detection patterns.
---

# Force Multiplier Skill

This skill provides customization hooks for the force-multiplier plugin behavior. It lets you adjust detection thresholds, message phrasing, and coaching patterns.

## Configuration Options

### Detection Thresholds

| Setting | Default | Description |
|---------|---------|-------------|
| `tool_threshold` | 5 | Min tools before coaching triggers |
| `subagent_cooldown` | 3 | Turns between subagent coaching |
| `skill_hint_turns` | 10 | Turns before suggesting skills |

### Message Templates

Override the coaching messages by setting environment variables:

```bash
export FORCE_MULTIPLIER_SESSION_MSG="Your custom session start message"
export FORCE_MULTIPLIER_STOP_MSG="Your custom stop message"
export FORCE_MULTIPLIER_COMPACT_MSG="Your custom compaction message"
```

### Detection Patterns

The plugin detects these patterns:

- **Sequential work**: 5+ tool calls without subagent spawn
- **Skill gap**: Complex workflow with no skill loaded
- **Context pressure**: Pre-compaction state

## Integration

This skill is optional — the hooks work standalone. Load this skill only if you want to customize behavior.