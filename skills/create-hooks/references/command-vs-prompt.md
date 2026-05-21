# Command vs Prompt Hooks

Decision guide for choosing between command-based and prompt-based hooks.

---

## Decision Tree

```
Need to execute a hook?
│
├─ Simple yes/no validation?
│  └─ Use COMMAND (faster, cheaper)
│
├─ Need natural language understanding?
│  └─ Use PROMPT (LLM evaluation)
│
├─ External tool interaction?
│  └─ Use COMMAND (formatters, linters, git)
│
└─ Logging/notification only?
   └─ Use COMMAND (no decision needed)
```

---

## Command Hooks

### Characteristics

- **Execution:** Shell command
- **Input:** JSON via stdin
- **Output:** JSON via stdout (optional)
- **Speed:** Fast (<100ms)
- **Cost:** Free (no API usage)
- **Complexity:** Limited to shell scripting logic

### When to Use

**Use command hooks for:**
- File operations (read, write, check existence)
- Running tools (prettier, eslint, git)
- Simple pattern matching (grep, regex)
- Logging to files
- Desktop notifications
- Fast validation (file size, permissions)

**Don't use command hooks for:**
- Natural language analysis
- Complex decision logic
- Context-aware validation

### Examples

**Log bash commands**
```json
{
  "type": "command",
  "command": "jq -r '\"\\(.tool_input.command) - \\(.tool_input.description // \\\"No description\\\")\"' >> ~/.claude/bash-log.txt"
}
```

**Block if file doesn't exist**
```bash
#!/bin/bash
input=$(cat)
file=$(echo "$input" | jq -r '.tool_input.file_path')

if [ ! -f "$file" ]; then
  echo '{"decision": "block", "reason": "File does not exist"}'
  exit 0
fi

echo '{"decision": "approve", "reason": "File exists"}'
```

**Run prettier after edits**
```json
{
  "type": "command",
  "command": "prettier --write \"$(jq -r '.tool_input.file_path')\"",
  "timeout": 10000
}
```

**Desktop notification**
```json
{
  "type": "command",
  "command": "osascript -e 'display notification \"Claude needs input\" with title \"Claude Code\"'"
}
```

---

## Prompt Hooks

### Characteristics

- **Execution:** LLM evaluates prompt
- **Input:** Prompt string with `$ARGUMENTS` placeholder
- **Output:** LLM generates JSON response
- **Speed:** Slower (~1-3s per evaluation)
- **Cost:** Uses API credits
- **Complexity:** Can reason, understand context, analyze semantics

### When to Use

**Use prompt hooks for:**
- Natural language validation
- Semantic analysis (intent, safety, appropriateness)
- Complex decision trees
- Context-aware checks
- Reasoning about code quality

**Don't use prompt hooks for:**
- Simple pattern matching (use regex/grep)
- File operations (use command hooks)
- High-frequency events (too slow/expensive)

### Examples

**Validate commit messages**
```json
{
  "type": "prompt",
  "prompt": "Evaluate this git commit message: $ARGUMENTS\n\nCheck if it:\n1. Starts with conventional commit type (feat|fix|docs|refactor|test|chore)\n2. Is descriptive and clear\n3. Under 72 characters\n\nReturn: {\"decision\": \"approve\" or \"block\", \"reason\": \"specific feedback\"}"
}
```

**Check if Stop is appropriate**
```json
{
  "type": "prompt",
  "prompt": "Review the conversation transcript: $ARGUMENTS\n\nDetermine if Claude should stop:\n1. All user tasks completed?\n2. Any errors that need fixing?\n3. Tests passing?\n\nIf incomplete: {\"decision\": \"block\", \"reason\": \"what's missing\"}\nIf complete: {\"decision\": \"approve\", \"reason\": \"all done\"}"
}
```

**Validate code changes for security**
```json
{
  "type": "prompt",
  "prompt": "Analyze this code change for security issues: $ARGUMENTS\n\nCheck for:\n- SQL injection vulnerabilities\n- XSS attack vectors\n- Authentication bypasses\n\nIf issues found: {\"decision\": \"block\", \"reason\": \"specific vulnerabilities\"}\nIf safe: {\"decision\": \"approve\", \"reason\": \"no issues found\"}"
}
```

---

## Performance Comparison

| Aspect | Command Hook | Prompt Hook |
|--------|-------------|-------------|
| **Speed** | <100ms | 1-3s |
| **Cost** | Free | ~$0.001-0.01 per call |
| **Complexity** | Shell scripting | Natural language |
| **Context awareness** | Limited | High |
| **Reasoning** | No | Yes |
| **Best for** | Operations, logging | Validation, analysis |

---

## Variables Available to Hooks

Command hooks have access to two variables that expand at hook execution time:

### `$ARGUMENTS`

The tool input/properties from the triggering event, serialized as a JSON string.

**Available in:**
- `PreToolUse` — contains `tool_input` (the tool's input parameters)
- `UserPromptSubmit` — contains the raw user prompt text
- `PostToolUse` — contains `tool_input` and `tool_output`

**Example in PreToolUse:**
```json
{
  "type": "command",
  "command": "echo '$ARGUMENTS' | jq -r '.tool_input.command'"
}
```

For a `Bash` tool call with `{ "command": "npm install" }`, `$ARGUMENTS` expands to the JSON object `{"command": "npm install", ...}`.

### `$CLAUDE_PROJECT_DIR`

Expands to the absolute path of the current Claude Code project directory.

**Always available** in all hook types regardless of `cwd`.

**Example:**
```json
{
  "type": "command",
  "command": "prettier --write $CLAUDE_PROJECT_DIR/src/**/*.ts"
}
```

**Use cases:**
- Run formatters/linters on project files
- Read project-specific config files
- Construct paths relative to project root

### Using Variables Together

```json
{
  "type": "command",
  "command": "file_exists=$CLAUDE_PROJECT_DIR/.gitignore && echo $file_exists"
}
```

Note: Variables are expanded by the shell, so always quote them when used in JSON strings to prevent word splitting.

---

## Combining Both

You can use multiple hooks for the same event:

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "echo \"$input\" >> ~/bash-log.txt"
          },
          {
            "type": "prompt",
            "prompt": "Analyze this bash command for safety: $ARGUMENTS"
          }
        ]
      }
    ]
  }
}
```

Hooks execute in order. If any hook blocks, execution stops.

---

## Recommendations

**High-frequency events** (PreToolUse, PostToolUse):
- Prefer command hooks
- Use prompt hooks sparingly

**Low-frequency events** (Stop, UserPromptSubmit):
- Prompt hooks are fine
- Cost/latency less critical

**Balance:**
- Command hooks for simple checks
- Prompt hooks for complex validation
- Combine when appropriate