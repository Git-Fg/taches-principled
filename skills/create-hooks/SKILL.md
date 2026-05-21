---
name: create-hooks
description: "Build Claude Code hooks for event-driven automation. Use when setting up validation, logging, notifications, or custom completion logic."
when_to_use: |
  Do NOT use for reviewing existing hooks, configuring MCP servers, or writing general Claude Code instructions.
---

## What Hooks Are

Hooks are scripts that run when things happen. A tool gets called → your hook runs. Claude stops → your hook runs. A session starts → your hook runs.

They're middleware for Claude's behavior.

## The Key Insight

Hooks observe or intercept. They can't change what Claude thinks—only what actions are allowed, or what happens as side effects.

**Blocking hooks** can prevent actions (safety rails)
**Observation hooks** can log/notify (audit trails)

### Policy vs. Mechanism

**Policy** = when a hook should fire (the interception decision)
**Mechanism** = what the hook actually does when it fires (the script logic)

A hook definition conflating policy and mechanism becomes opaque — the hook fires but its purpose is unclear, making debugging and maintenance difficult.

Example:
- Policy: "Block any Bash command containing 'rm -rf' on production paths"
- Mechanism: "Parse stdin JSON, check tool_input.command against regex, return block decision"

## Hook Events

| Event | When | Can Block? |
|-------|------|------------|
| PreToolUse | Before tool runs | Yes |
| PostToolUse | After tool runs | No |
| UserPromptSubmit | User submits a prompt | Yes |
| Stop | Claude tries to stop | Yes |
| SessionStart | Session begins | No |
| Notification | Claude needs input | No |

## What Good Looks Like

**Safety rail** (block dangerous commands):
```json
{
  "hooks": {
    "PreToolUse": [{
      "matcher": "Bash",
      "hooks": [{
        "type": "prompt",
        "prompt": "Block if command contains 'rm -rf' or 'git push --force'. Return {\"decision\": \"block\", \"reason\": \"...\"}"
      }]
    }]
  }
}
```

**Audit trail** (log all bash commands):
```json
{
  "hooks": {
    "PostToolUse": [{
      "matcher": "Bash",
      "hooks": [{
        "type": "command",
        "command": "echo \"$ARGUMENTS\" >> ~/.claude/bash-log.txt"
      }]
    }]
  }
}
```

**Desktop notification** (when Claude needs you):
```json
{
  "hooks": {
    "Notification": [{
      "hooks": [{
        "type": "command",
        "command": "osascript -e 'display notification \"Claude needs input\"'"
      }]
    }]
  }
}
```

**Session context injection** (add context at session start):
```json
{
  "hooks": {
    "SessionStart": [{
      "hooks": [{
        "type": "command",
        "command": "echo '{\"hookSpecificOutput\": {\"hookEventName\": \"SessionStart\", \"additionalContext\": \"Current sprint: Sprint 23. Focus: User authentication\"}}'"
      }]
    }]
  }
}
```

**Note on `hookSpecificOutput`**: When using SessionStart hooks to inject context, the output must use the `hookSpecificOutput` schema with `hookEventName` set to `"SessionStart"` and `additionalContext` containing the context string. This allows Claude to receive project-specific context at session start.

## Hook Types

**Command hooks** — Run a shell script
- Good for: logging, notifications, file operations
- Input: JSON via stdin
- Output: JSON via stdout (for blocking hooks)

**Prompt hooks** — Let Claude evaluate
- Good for: complex decisions, natural language checks
- Input: `$ARGUMENTS` placeholder
- Output: `{"decision": "approve|block", "reason": "..."}`

## Where Hooks Live

`.claude/hooks.json` — Project-level
`~/.claude/hooks.json` — User-level

## Common Mistakes

### Numeric Thresholds

| Metric | Limit | Why |
|--------|-------|-----|
| Hooks per event type | 5 max | More = execution order confusion, debugging nightmare |
| Default timeout | 60s | External commands without timeout can hang indefinitely |
| Matcher specificity | Be precise | ".*" matches everything — intentional only |

### Debugging Checklist

When a hook misbehaves:
1. Test with `claude --debug` — shows which hooks matched
2. Validate JSON: `jq . .claude/hooks.json`
3. Check script has executable permissions: `ls -la /path/to/hook.sh`
4. Verify timeout is set (especially for network calls)
5. For Stop hooks: confirm `stop_hook_active` is checked

**Infinite loops.** If your Stop hook triggers another stop, you loop forever. Check `stop_hook_active` flag.

**Over-blocking.** Every blocked action is friction. Block the dangerous, not the annoying.

**No timeout.** External commands can hang. Set reasonable timeouts.

## Clarifying Questions

1. **What event should trigger this hook?** (PreToolUse for validation, PostToolUse for logging)

2. **Should it block or just observe?** (Blocking needs decision output)

3. **What tools should trigger it?** (Use matcher: "Bash" or "Bash|Write|Edit")

## Security Checklist

**Critical safety requirements**:

- **Infinite loop prevention**: Check `stop_hook_active` flag in Stop hooks to prevent recursive triggering
- **Timeout configuration**: Set reasonable timeouts (default: 60s) to prevent hanging
- **Permission validation**: Ensure hook scripts have executable permissions (`chmod +x`)
- **Path safety**: Use absolute paths with `$CLAUDE_PROJECT_DIR` to avoid path injection
- **JSON validation**: Validate hook config with `jq` before use to catch syntax errors
- **Selective blocking**: Be conservative with blocking hooks to avoid workflow disruption

**Testing protocol**:
```bash
# Always test with debug flag first
claude --debug

# Validate JSON config
jq . .claude/hooks.json
```

## Debugging

Hooks not working? Debug workflow:

1. **Always test with debug flag first**:
```bash
claude --debug
```

2. **Check hook output** - Debug mode shows which hooks matched, command execution, and output

3. **Validate JSON**:
```bash
jq . .claude/hooks.json
```

4. **Common issues**:
   - Hooks not triggering: Check matcher pattern matches the tool name
   - Command execution failures: Verify script has executable permissions
   - Prompt hook issues: Ensure output JSON is valid with `decision` and `reason`
   - Permission problems: Verify hook script permissions with `ls -la`
   - Timeout handling: Set explicit timeout if external commands are slow

## Success Criteria

A well-configured hook has:

- Valid JSON in `.claude/hooks.json` (validated with `jq`)
- Appropriate hook event selected for the use case
- Correct matcher pattern that matches target tools
- Command or prompt that executes without errors
- Proper output schema (decision/reason for blocking hooks)
- Tested with `--debug` flag showing expected behavior
- No infinite loops in Stop hooks (checks `stop_hook_active` flag)
- Reasonable timeout set (especially for external commands)
- Executable permissions on script files if using file paths

## Anti-Patterns

### ❌ Hooks that do multiple things invisibly
A PreToolUse hook that logs the command, modifies the input, AND checks permissions is three responsibilities under one matcher. When it breaks, you don't know which behavior failed.

### ✅ One purpose per hook, named explicitly
Separate hooks for separate concerns: one for logging, one for input modification, one for permissions. Each is independently testable.

### ❌ No timeout on external commands
`curl` or `git` commands without timeout can hang indefinitely, blocking Claude.

### ✅ Explicit timeouts
`"timeout": 10000` for external commands. Default to 60s for unknown commands.

### ❌ Stop hook without stop_hook_active check
A Stop hook that always blocks will loop infinitely if Stop fires again after blocking.

### ✅ Guard with stop_hook_active
```
if [ "$stop_hook_active" = "true" ]; then
  echo '{"decision": "approve"}'
  exit 0
fi
# ... validation logic
```

## See Also

- `references/hook-types.md` — All hook events with input/output JSON schemas
- `references/matchers.md` — Regex patterns for filtering which tools trigger hooks
- `references/command-vs-prompt.md` — Decision guide for command vs prompt hook types
