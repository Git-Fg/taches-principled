# Hook Types and Events

Complete reference for all Claude Code hook events.

---

## PreToolUse

**When it fires:** Before any tool is executed

**Can block:** Yes

**Input schema:**
```json
{
  "session_id": "abc123",
  "transcript_path": "~/.claude/projects/.../session.jsonl",
  "cwd": "/current/working/directory",
  "permission_mode": "default",
  "hook_event_name": "PreToolUse",
  "tool_name": "Bash",
  "tool_input": {
    "command": "npm install",
    "description": "Install dependencies"
  }
}
```

**Output schema** (to control execution):
```json
{
  "decision": "approve" | "block",
  "reason": "Explanation",
  "permissionDecision": "allow" | "deny" | "ask",
  "permissionDecisionReason": "Why",
  "updatedInput": {
    "command": "npm install --save-exact"
  }
}
```

**Use cases:**
- Validate commands before execution
- Block dangerous operations
- Modify tool inputs
- Log command attempts
- Ask user for confirmation

**Example:** Block force pushes to main
```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "prompt",
            "prompt": "Check if this git command is safe: $ARGUMENTS\n\nBlock if: force push to main/master\n\nReturn: {\"decision\": \"approve\" or \"block\", \"reason\": \"explanation\"}"
          }
        ]
      }
    ]
  }
}
```

---

## PostToolUse

**When it fires:** After a tool completes execution

**Can block:** No (tool already executed)

**Input schema:**
```json
{
  "session_id": "abc123",
  "transcript_path": "~/.claude/projects/.../session.jsonl",
  "cwd": "/current/working/directory",
  "permission_mode": "default",
  "hook_event_name": "PostToolUse",
  "tool_name": "Write",
  "tool_input": {
    "file_path": "/path/to/file.js",
    "content": "..."
  },
  "tool_output": "File created successfully"
}
```

**Output schema:**
```json
{
  "systemMessage": "Optional message to display",
  "suppressOutput": false
}
```

**Use cases:**
- Auto-format code after Write/Edit
- Run tests after code changes
- Update documentation
- Trigger CI builds
- Send notifications

**Example:** Auto-format after edits
```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [
          {
            "type": "command",
            "command": "prettier --write $CLAUDE_PROJECT_DIR",
            "timeout": 10000
          }
        ]
      }
    ]
  }
}
```

---

## UserPromptSubmit

**When it fires:** User submits a prompt to Claude

**Can block:** Yes

**Input schema:**
```json
{
  "session_id": "abc123",
  "transcript_path": "~/.claude/projects/.../session.jsonl",
  "cwd": "/current/working/directory",
  "permission_mode": "default",
  "hook_event_name": "UserPromptSubmit",
  "prompt": "Write a function to calculate factorial"
}
```

**Output schema:**
```json
{
  "decision": "approve" | "block",
  "reason": "Explanation",
  "systemMessage": "Message to user"
}
```

**Use cases:**
- Validate prompt format
- Block inappropriate requests
- Preprocess user input
- Enforce prompt templates

**Example:** Require issue numbers in prompts
```json
{
  "hooks": {
    "UserPromptSubmit": [
      {
        "hooks": [
          {
            "type": "prompt",
            "prompt": "Check if prompt mentions an issue number (e.g., #123 or PROJ-456): $ARGUMENTS\n\nIf no issue number: {\"decision\": \"block\", \"reason\": \"Please include issue number\"}\nOtherwise: {\"decision\": \"approve\", \"reason\": \"ok\"}"
          }
        ]
      }
    ]
  }
}
```

---

## Stop

**When it fires:** Claude attempts to stop working

**Can block:** Yes

**Input schema:**
```json
{
  "session_id": "abc123",
  "transcript_path": "~/.claude/projects/.../session.jsonl",
  "cwd": "/current/working/directory",
  "permission_mode": "default",
  "hook_event_name": "Stop",
  "stop_hook_active": false
}
```

**Output schema:**
```json
{
  "decision": "block" | undefined,
  "reason": "Why Claude should continue",
  "continue": true,
  "systemMessage": "Additional instructions"
}
```

**Use cases:**
- Verify all tasks completed
- Check for errors that need fixing
- Ensure tests pass before stopping
- Custom completion criteria

**Example:** Verify tests pass before stopping
```json
{
  "hooks": {
    "Stop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "npm test && echo '{\"decision\": \"approve\"}' || echo '{\"decision\": \"block\", \"reason\": \"Tests failing\"}'"
          }
        ]
      }
    ]
  }
}
```

**Important:** Check `stop_hook_active` to avoid infinite loops. If true, don't block again.

---

## SessionStart

**When it fires:** At the beginning of a Claude session

**Can block:** No

**Input schema:**
```json
{
  "session_id": "abc123",
  "transcript_path": "~/.claude/projects/.../session.jsonl",
  "cwd": "/current/working/directory",
  "permission_mode": "default",
  "hook_event_name": "SessionStart",
  "source": "startup"
}
```

**Output schema:**
```json
{
  "hookSpecificOutput": {
    "additionalContext": "Context to inject into session"
  }
}
```

**Use cases:**
- Load project context
- Inject sprint information
- Display welcome messages

**Example:** Load current sprint context
```json
{
  "hooks": {
    "SessionStart": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "cat $CLAUDE_PROJECT_DIR/.sprint-context.txt | jq -Rs '{\"hookSpecificOutput\": {\"hookEventName\": \"SessionStart\", \"additionalContext\": .}}'"
          }
        ]
      }
    ]
  }
}
```

---

## Notification

**When it fires:** Claude needs user input (awaiting response)

**Can block:** No

**Use cases:**
- Desktop notifications
- Sound alerts
- External notifications (Slack, etc.)

**Example:** macOS notification
```json
{
  "hooks": {
    "Notification": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "osascript -e 'display notification \"Claude needs input\" with title \"Claude Code\"'"
          }
        ]
      }
    ]
  }
}
```

---

## Quick Reference: Event Summary

| Event | Can Block? | Common Use |
|-------|------------|------------|
| PreToolUse | Yes | Validate, block dangerous, modify input |
| PostToolUse | No | Auto-format, run tests, notify |
| UserPromptSubmit | Yes | Validate prompts, enforce templates |
| Stop | Yes | Verify completion, check tests |
| SessionStart | No | Inject context, welcome message |
| Notification | No | Desktop alerts, Slack messages |

---

## Debugging Hooks

### Validate JSON Config

```bash
jq . ~/.claude/hooks.json
```

If the file is valid JSON, `jq` prints it formatted. If invalid, it reports the parse error with line/column.

### Test with `--debug` Flag

Run Claude Code with debug logging to see hook execution:

```bash
claude --debug
```

Debug output includes:
- Hook events fired
- Matcher results (which hooks matched)
- Hook execution times
- Output from command hooks

### Common Failure Modes

| Symptom | Likely Cause | Diagnosis |
|---------|-------------|------------|
| Hook never fires | Wrong event name in config | Check `hook_event_name` matches documented event names |
| Matcher not matching | Case sensitivity or regex error | Verify tool name casing; test regex with `echo "ToolName" \| grep -E "pattern"` |
| Command returns nothing | JSON output not printed to stdout | Ensure command ends with `echo '{"decision": "..."}'` |
| Block/approve ignored | Wrong output schema key | Verify top-level keys: `decision`, `reason`, `systemMessage` |
| Permission denied | Permission mode not allowing hook | Check `~/.claude/settings.json` permission configuration |

### Testing Hooks in Isolation

To test a command hook's JSON handling:

```bash
# Create test input matching hook schema
echo '{"tool_name": "Bash", "tool_input": {"command": "ls"}}' | \
  your_command_hook.sh
```

Verify the output is valid JSON with expected keys before deploying.