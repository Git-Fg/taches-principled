# Frontmatter Complete Reference

Full frontmatter field reference with descriptions, types, defaults, and examples for Claude Code skills.

## Standard Fields

All fields are optional. Only `description` is recommended so Claude knows when to use the skill.

### Required Fields

| Field | Type | Description |
|-------|------|-------------|
| `description` | string | What the skill does and when to use it. Used for routing. Recommended ≤150 chars (max 1,024). |

### Optional Fields

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `name` | string | directory name | Display name in skill listings. Does not affect command name. |
| `when_to_use` | string | — | Additional trigger contexts. ≤200 chars. |
| `argument-hint` | string | — | Hint shown during autocomplete after `/skill-name`. |
| `arguments` | list[string] | — | Named positional arguments mapping to `$name` substitution. |
| `disable-model-invocation` | boolean | `false` | Set `true` to prevent Claude from auto-triggering. Only user invocation. |
| `user-invocable` | boolean | `true` | Set `false` to hide from `/` menu. Still auto-loads by relevance. |
| `allowed-tools` | list[string] | — | Tools pre-approved during skill. Does NOT restrict. |
| `disallowed-tools` | list[string] | — | Tools removed from available pool during skill. |
| `model` | string | `inherit` | Model override: `sonnet`, `opus`, `haiku`, full ID, or `inherit`. |
| `effort` | string | `inherit` | Effort level: `low`, `medium`, `high`, `xhigh`, `max`. |
| `context` | string | — | Set `fork` to run body in isolated subagent context. |
| `agent` | string | `general-purpose` | Subagent type when `context: fork`: `Explore`, `Plan`, `general-purpose`. |
| `hooks` | map | — | Hooks scoped to skill lifecycle. |
| `paths` | list[string] | — | Glob patterns limiting when skill auto-activates by file path. |
| `shell` | string | `bash` | Shell for `!` command execution: `bash` or `powershell`. |

---

## Field Details

### `description`

**Purpose:** Primary routing signal. Tells Claude when to load this skill.

**Best practices:**
- Put trigger phrases in first 200 characters (survives truncation)
- Use user vocabulary, not internal jargon
- Include explicit trigger phrases: "Use when user says X, Y, or Z"
- Add exclusions via `when_to_use` to prevent false triggers

**Example:**
```yaml
description: "Reviews code for bugs, security, and logic errors. Use when user asks 'review code', 'check PR', 'find bugs', or 'audit this'."
```

### `name`

**Purpose:** Display name shown in skill listings.

**Note:** Does not change the command name. The directory name or file name (for commands) sets the command name.

**Example:**
```yaml
name: security-audit  # Shows in listings; command is /security-audit
```

### `when_to_use`

**Purpose:** Additional trigger contexts and exclusions.

**Example:**
```yaml
when_to_use: |
  Do NOT use for formatting, linting, or running tests.
```

### `argument-hint`

**Purpose:** Autocomplete hint after `/skill-name`.

**Example:**
```yaml
argument-hint: "[issue-number]"
# User types /fix-issue [cursor shows "issue-number" hint]
```

### `arguments`

**Purpose:** Named positional arguments for `$name` substitution.

**Mapping:** Names map to positions in `$ARGUMENTS`.

```yaml
---
arguments: [issue, branch]
---
# /migrate-component SearchBar React Vue
# $issue = SearchBar (first position)
# $branch = React (second position)
```

### `disable-model-invocation`

**Purpose:** Prevent Claude from auto-triggering. User must invoke manually.

**Use for:** Side-effect skills (deploy, commit, send messages) where auto-triggering is dangerous.

```yaml
disable-model-invocation: true
```

### `user-invocable`

**Purpose:** Hide from `/` menu but still allow auto-loading.

**Use for:** Background knowledge skills that Claude should know but users shouldn't invoke directly.

```yaml
user-invocable: false
```

### `allowed-tools`

**Purpose:** Pre-approve tools during skill. Skips permission prompts.

**Important:** Does NOT restrict tools. For true restriction, use `disallowed-tools` or agent `tools:` allowlist.

```yaml
allowed-tools: [Read, Grep, Glob, Bash]
```

### `disallowed-tools`

**Purpose:** Remove specific tools from the available pool during skill.

```yaml
disallowed-tools: [Edit, Write]
# Claude cannot edit or write files while this skill is active
```

### `model`

**Purpose:** Override the session model when this skill is active.

**Values:** `sonnet`, `opus`, `haiku`, full model ID (e.g., `claude-opus-4-8`), or `inherit`.

```yaml
model: sonnet
```

### `effort`

**Purpose:** Set thinking budget when skill is active.

**Values:** `low`, `medium`, `high`, `xhigh`, `max`.

```yaml
effort: high
```

### `context`

**Purpose:** Run skill body in isolated subagent context.

**Value:** `fork` creates an isolated context.

```yaml
context: fork
```

### `agent`

**Purpose:** Specify which subagent type to use with `context: fork`.

**Values:** `Explore`, `Plan`, `general-purpose` (default).

```yaml
context: fork
agent: Explore
```

### `hooks`

**Purpose:** Hooks scoped to this skill's lifecycle.

```yaml
hooks:
  PreToolUse:
    - matcher: "Bash"
      hooks:
        - type: command
          command: "./validate.sh"
```

### `paths`

**Purpose:** Glob patterns limiting when skill auto-activates.

```yaml
paths: ["src/**/*.ts", "tests/**/*.ts"]
# Skill activates only when working with TypeScript files
```

### `shell`

**Purpose:** Shell for `!` command and ` ```! ` blocks.

**Values:** `bash` (default), `powershell` (requires `CLAUDE_CODE_USE_POWERSHELL_TOOL=1`).

```yaml
shell: powershell
```

---

## String Substitutions

When a skill is invoked, these substitutions are available:

| Variable | Description |
|----------|-------------|
| `$ARGUMENTS` | All arguments passed when invoking the skill |
| `$ARGUMENTS[N]` | Access argument by 0-based index |
| `$N` | Shorthand for `$ARGUMENTS[N]` |
| `$name` | Named argument from `arguments` field |
| `${CLAUDE_SESSION_ID}` | Current session ID |
| `${CLAUDE_EFFORT}` | Current effort level |
| `${CLAUDE_SKILL_DIR}` | Directory containing the SKILL.md file |

**Example:**
```yaml
---
arguments: [issue, branch]
---
Fix GitHub issue $issue by branch $branch
# /fix-issue 123 feature-login
# $issue = 123
# $branch = feature-login
```

---

## Invalid Fields

The following are NOT valid frontmatter fields. Do not use them:

| Invalid Field | Why | Use Instead |
|---------------|-----|-------------|
| `metadata` | Not a valid field | Top-level fields directly |
| `related_skills` | Not a valid field | Skill references in body text |
| `tags` | Not a valid field | `when_to_use` for additional context |
| `version` | Not a valid field | Git history is source of truth |

---

## Field Comparison

| Field | Where Used | Effect |
|-------|-----------|--------|
| `name` | Skills, agents, commands | Display label |
| `description` | Skills, agents, commands | Routing signal |
| `tools` | Agents only | Hard allowlist |
| `allowed-tools` | Skills, commands | Pre-approval (skips prompts) |
| `disallowed-tools` | Skills | Hard block |

---

## Example: Complete Frontmatter

```yaml
---
name: deploy-staging
description: "Deploys to staging environment. Use when user types /deploy, says 'deploy', 'ship', or 'push to staging'."
when_to_use: "Do NOT use for production deployments or building."
argument-hint: "[environment]"
arguments: [env]
disable-model-invocation: true
allowed-tools: [Bash]
model: inherit
effort: high
context: fork
agent: general-purpose
hooks:
  PostToolUse:
    - matcher: "Bash"
      hooks:
        - type: command
          command: "./notify.sh"
paths: ["src/**", "tests/**"]
---
```