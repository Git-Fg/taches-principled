# Matchers and Pattern Matching

Matchers are regex patterns that filter which tools trigger a hook.

---

## Syntax

Matchers use JavaScript regex syntax:

```json
{
  "matcher": "pattern"
}
```

The pattern is tested against the tool name using `new RegExp(pattern).test(toolName)`.

---

## Common Patterns

### Exact Match
```json
{
  "matcher": "Bash"
}
```
Matches: `Bash`
Doesn't match: `bash`, `BashOutput`

### Multiple Tools (OR)
```json
{
  "matcher": "Write|Edit"
}
```
Matches: `Write`, `Edit`

### Starts With
```json
{
  "matcher": "^Bash"
}
```
Matches: `Bash`, `BashOutput`

### Ends With
```json
{
  "matcher": "Output$"
}
```
Matches: `BashOutput`

### Contains
```json
{
  "matcher": ".*write.*"
}
```
Matches: `Write`, `NotebookWrite`, `TodoWrite`

Case-sensitive! `write` won't match `Write`.

### Any Tool (No Matcher)
```json
{
  "hooks": {
    "PreToolUse": [
      {
        "hooks": [...]  // No matcher = matches all tools
      }
    ]
  }
}
```

---

## Tool Categories

### All File Operations
```json
{
  "matcher": "Read|Write|Edit|Glob|Grep"
}
```

### All Bash Tools
```json
{
  "matcher": "Bash.*"
}
```
Matches: `Bash`, `BashOutput`, `BashKill`

### All MCP Tools
```json
{
  "matcher": "mcp__.*"
}
```
Matches: `mcp__memory__store`, `mcp__filesystem__read`, etc.

### Specific MCP Server
```json
{
  "matcher": "mcp__github__.*"
}
```

---

## MCP Tool Naming

MCP tools follow the pattern: `mcp__{server}__{tool}`

Examples:
- `mcp__memory__store`
- `mcp__filesystem__read`
- `mcp__github__create_issue`

---

## Real-World Examples

### Log All Bash Commands
```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "jq -r '.tool_input.command' >> ~/bash-log.txt"
          }
        ]
      }
    ]
  }
}
```

### Format Code After Any File Write
```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write|Edit|NotebookEdit",
        "hooks": [
          {
            "type": "command",
            "command": "prettier --write $CLAUDE_PROJECT_DIR"
          }
        ]
      }
    ]
  }
}
```

### Block Destructive Git Commands
```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "/path/to/check-git-safety.sh"
          }
        ]
      }
    ]
  }
}
```

`check-git-safety.sh`:
```bash
#!/bin/bash
input=$(cat)
command=$(echo "$input" | jq -r '.tool_input.command')

if [[ "$command" == *"git push --force"* ]] || \
   [[ "$command" == *"rm -rf /"* ]] || \
   [[ "$command" == *"git reset --hard"* ]]; then
  echo '{"decision": "block", "reason": "Destructive command detected"}'
else
  echo '{"decision": "approve", "reason": "Safe"}'
fi
```

---

## Common Mistakes

### ❌ Case Sensitivity
```json
{
  "matcher": "bash"  // Won't match "Bash"
}
```

### ❌ Missing Escape
```json
{
  "matcher": "mcp__memory__*"  // * is literal, not wildcard
}
```

### ❌ Unintended Partial Match
```json
{
  "matcher": "Write"  // Matches "Write", "TodoWrite", "NotebookWrite"
}
```

---

## Multiple Matchers

You can have multiple matcher blocks for the same event:

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "/path/to/bash-validator.sh"
          }
        ]
      },
      {
        "matcher": "Write|Edit",
        "hooks": [
          {
            "type": "command",
            "command": "/path/to/file-validator.sh"
          }
        ]
      },
      {
        "matcher": "mcp__.*",
        "hooks": [
          {
            "type": "command",
            "command": "/path/to/mcp-logger.sh"
          }
        ]
      }
    ]
  }
}
```

Each matcher is evaluated independently. A tool can match multiple matchers.

---

## Debugging Matchers

### Enable debug mode
```bash
claude --debug
```

Debug output shows:
```
[DEBUG] Getting matching hook commands for PreToolUse with query: Bash
[DEBUG] Found 3 hook matchers in settings
[DEBUG] Matched 1 hooks for query "Bash"
```

### Test your matcher

Use JavaScript regex to test patterns:

```javascript
const toolName = "mcp__memory__store";
const pattern = "mcp__memory__.*";
const regex = new RegExp(pattern);
console.log(regex.test(toolName)); // true
```

Or in Node.js:
```bash
node -e "console.log(/mcp__memory__.*/.test('mcp__memory__store'))"
```

### Common mistakes

❌ **Case sensitivity**
```json
{
  "matcher": "bash"  // Won't match "Bash"
}
```

✅ **Correct**
```json
{
  "matcher": "Bash"
}
```

---

❌ **Missing escape**
```json
{
  "matcher": "mcp__memory__*"  // * is literal, not wildcard
}
```

✅ **Correct**
```json
{
  "matcher": "mcp__memory__.*"  // .* is regex for "any characters"
}
```

---

❌ **Unintended partial match**
```json
{
  "matcher": "Write"  // Matches "Write", "TodoWrite", "NotebookWrite"
}
```

✅ **Exact match only**
```json
{
  "matcher": "^Write$"
}
```

---

## Advanced Patterns

### Negative lookahead (exclude tools)
```json
{
  "matcher": "^(?!Read).*"
}
```
Matches: Everything except `Read`

### Match any file operation except Grep
```json
{
  "matcher": "^(Read|Write|Edit|Glob)$"
}
```

### Case-insensitive match
```json
{
  "matcher": "(?i)bash"
}
```
Matches: `Bash`, `bash`, `BASH`

(Note: Claude Code tools are PascalCase by convention, so this is rarely needed)

---

## Performance Considerations

**Broad matchers** (e.g., `.*`) run on every tool use:
- Simple command hooks: negligible impact
- Prompt hooks: can slow down significantly

**Recommendation**: Be as specific as possible with matchers to minimize unnecessary hook executions.

**Example**: Instead of matching all tools and checking inside the hook:
```json
{
  "matcher": ".*",  // Runs on EVERY tool
  "hooks": [
    {
      "type": "command",
      "command": "if [[ $(jq -r '.tool_name') == 'Bash' ]]; then ...; fi"
    }
  ]
}
```

Do this:
```json
{
  "matcher": "Bash",  // Only runs on Bash
  "hooks": [
    {
      "type": "command",
      "command": "..."
    }
  ]
}
```

---

## Tool Name Reference

Common Claude Code tool names:

### File Operations
- `Read`
- `Write`
- `Edit`
- `NotebookEdit`
- `Glob`
- `Grep`

### Bash
- `Bash`
- `BashOutput`
- `KillShell`

### Tasks
- `Task`
- `TaskOutput`
- `TaskStop`
- `TaskGet`

### Other
- `AskUserQuestion`
- `WebSearch`
- `WebFetch`
- `Skill`
- `SlashCommand`
- `ExitPlanMode`

MCP tools: `mcp__{server}__{tool}` (varies by installed servers)

Run `claude --debug` and watch tool calls to discover available tool names.