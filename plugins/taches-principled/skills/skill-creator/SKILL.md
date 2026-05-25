---
name: skill-creator
description: "Teaches skill authorship methodology — trigger optimization, context:fork patterns, frontmatter precision, and portable subagent prompts. Use when improving skill descriptions, benchmarking triggers, or designing skill architecture. NOT for general code writing or project planning."
when_to_use: |
  Use when improving skill descriptions, benchmarking triggers, designing skill architecture, or learning about context:fork patterns.
  Do NOT use for writing production code, creating subagents as agents (use context:fork instead), or general project planning (use create-plans).
  Do NOT use when the user wants to create a skill using the plugin's workflow — use create-skills for that.
---

## Skill Creator

Teaches the craft of skill authorship. Focuses on methodology — how to write descriptions that trigger reliably, how to structure skill bodies for progressive disclosure, and how to use context:fork patterns for orchestration.

Jump in wherever the user is — rough idea, existing skill needing refinement, or architecture question.

The skill trusts you to orchestrate the workflow. It provides principles and patterns, not scripts.

## Core Loop

```
Intent → Draft → Test → Review → Improve → repeat
```

Order is flexible. If the user says "just vibe with me," skip formal testing.

---

## Step 1: Capture Intent

Understand before writing:
1. What should this skill enable Claude to do?
2. When should it trigger? (specific user phrases/contexts)
3. What's the expected output format?
4. Should objective test cases verify it works?

Ask about edge cases, input/output formats, dependencies, and success criteria.

---

## Step 2: Draft the SKILL.md

Follow the [Writing Skills](#writing-skills) section. Keep the main file under 500 lines. Move dense context to `references/` or `scripts/`.

---

## Step 3: Test — Measure, Don't Guess

### Trigger Validation with Headless Claude

To objectively test whether a description triggers correctly:

```bash
claude -p "<query>" \
  --output-format stream-json --verbose \
  --dangerously-skip-permissions \
  2>&1 | tee /tmp/trigger-test.jsonl
```

**What to look for in stream events:**
- `content_block_start` with `tool_use` (type: Skill or Read) → skill is being loaded
- `content_block_delta` with `input_json_delta` → skill name appears in parameters
- If you see the Skill tool invoked with your skill's name → it triggered

**Quick validation with grep:**
```bash
grep '"Skill".*"skill-name"' /tmp/trigger-test.jsonl
```

The script returns JSON output with exit codes:
- Exit 0: Success (triggered as expected)
- Exit 1: Failure (didn't trigger when expected, or triggered when not expected)
- Exit 2: Error (invalid arguments)

### Train/Test Split — Avoid Overfitting Descriptions

When optimizing a description on 20 test cases, keep 4-5 cases held out. If the optimized description scores 100% on training but fails on held-out cases, you've overfit. Iterate until the description generalizes.

**Rule:** "It works on my training cases" is not enough. The description must not be tailored to specific phrasings.

**Test case format:** `query | expected_trigger | notes`
- `query`: The actual user prompt
- `expected_trigger`: `yes` if skill should load, `no` if it shouldn't
- `notes`: Context or edge case description

**Collecting test queries:**
- Log real user prompts that should trigger your skill
- Synthesize edge cases (variations, paraphrases, ambiguous phrasings)
- Include negative cases (queries that should NOT trigger)

---

## Step 4: Review

Show results to the user. Key questions:
- Did the skill trigger when expected?
- Did it NOT trigger for the should-not cases?
- Is the output quality acceptable?

---

## Step 5: Improve

Based on feedback:
1. **Generalize** — don't overfit to specific phrasings
2. **Clarify boundaries** — add negative triggers if false positives occur
3. **Lean** — remove instructions that cause wasted steps

Repeat until the skill reliably triggers and behaves correctly.

---

## Writing Skills

### Frontmatter

The description is a routing prompt, not a keyword tag. Write for the model's linguistic reasoning. A good description triggers for "generate a presentation" even without the word "pptx".

**Be "pushy"** — Claude tends to undertrigger skills. Include specific trigger contexts and USE WHEN clauses.

**Key rules:**
- **<150 characters** in description (keeps ~20+ skills under 1% budget)
- **Trigger keywords front-loaded** in first 50 chars (survives truncation)
- **Plain quoted scalar** (`"..."`) not block scalar (`>` or `|-`)
- **"Use when" explicit** — tells Claude when to activate
- **Exclusions in `when_to_use`** — prevents false triggering

**Three anti-patterns:**

1. **Under-triggering:** Vague = model skips it
   ```yaml
   # Bad
   description: Implements X in Golang.
   ```
   ```yaml
   # Good
   description: "Implements X in Golang. Use when user adopts library/foo or imports github.com/library/foo."
   ```

2. **Over-triggering:** Too broad = fires on unrelated requests
   ```yaml
   # Bad
   description: Use when writing Go code.
   ```
   Fix: Restrict to the single concern.

3. **Trigger overlap:** Two skills claiming the same keywords.
   Fix: Add boundary in `when_to_use`: `NOT for: [adjacent use case].`

**Never cite other skill names in descriptions.** Use semantic boundaries instead.

---

### The Optimal Template

```yaml
description: "[Verb] [artifact] for [domain]. Use when user [trigger1], [trigger2], or [trigger3]."
when_to_use: |
  Do NOT use for [exclusion1], [exclusion2].
```

**Rules:**
- **<150 characters** in description
- **Trigger keywords front-loaded** in first 50 chars
- **Plain quoted scalar** (`"..."`) not block scalar (`|>`)
- **"Use when" explicit** — tells Claude when to activate
- **Exclusions in `when_to_use`** — prevents false triggering
- **`disable-model-invocation: true`** for side-effect skills (deploy, commit)

---

### 5 Optimized Examples

**1. Commit Writer:**
```yaml
description: "Writes commit messages from staged changes. Use when user asks to commit, types 'commit this', or 'write a commit message'."
when_to_use: |
  Do NOT use for pushing, merging, or checking status.
```

**2. Deploy:**
```yaml
description: "Deploys to staging or production. Use when user types /deploy, says 'deploy', 'ship', or 'push to prod'."
when_to_use: |
  Do NOT use for building, testing, or code review.
disable-model-invocation: true
```

**3. Test Generator:**
```yaml
description: "Creates unit tests with edge cases. Use when user asks to 'write tests', 'add test coverage', or 'generate tests'."
when_to_use: |
  Do NOT use for running existing tests.
```

**4. Code Review:**
```yaml
description: "Reviews code for bugs, security, logic errors. Use when user asks 'review code', 'check PR', 'find bugs', or 'audit this'."
when_to_use: |
  Do NOT use for formatting, linting, or running tests.
```

**5. Security Audit:**
```yaml
description: "Audits code for OWASP Top 10 security flaws. Use when user mentions 'security', 'vulnerabilities', 'SQL injection', or 'XSS'."
when_to_use: |
  Do NOT use for general code review without security focus.
effort: high
```

---

### Why This Format Works

| Element | Why |
|---------|-----|
| Plain scalar `"` not `>` | No unintended whitespace expansion, cleaner token count |
| "Use when user" | Explicit activation directive Claude reads as routing rule |
| Quoted triggers `'deploy'` | Claude matches exact phrases plus variations |
| `Do NOT use for` in `when_to_use` | Prevents false positives on adjacent requests |
| `<150 chars` | Fits comfortably in 1% budget; leaves headroom for 20+ skills |

---

## context:fork — When to Use

| Agent type | Builtin behavior | Use when |
|-----------|-----------------|-----------|
| `Explore` | "Investigate. Do not edit. Summarize." | Codebase exploration |
| `Plan` | "Analyze architecture. Plan steps." | Implementation planning |
| `general-purpose` | None | Complex orchestration |

**Use `context: fork`** when: skill orchestrates multiple steps, produces heavy parallel output, or builtin agent behavior matches the goal.

**Don't use** when: skill is simple (single tool call), you need intermediate results in main conversation, or builtin behavior contradicts the skill's purpose.

**`context:fork` vs `skills:` field:**
- `context:fork` — Agent provides the system prompt (role/persona), skill is the **task** to execute
- `skills:` field — You write the system prompt directly, skill is **reference knowledge** to inject at startup

Choose `context:fork` when you want the agent's builtin behavior (Explore's read-only discipline, Plan's architecture focus). Choose `skills:` when you need full control over the system prompt or want to load multiple skills as reference material.

---

## Portable Subagent Prompts — No Custom Agents Required

**Why this matters:** Custom agent definitions (`context:fork`, `agent: Explore`, etc.) require complex configuration and aren't portable across projects. A simpler pattern exists:

1. **Store** prompt templates as markdown files in `agents/*.md`
2. **Read** them with the Read tool when needed
3. **Spawn** a `general-purpose` subagent with that content

This works everywhere, requires no special configuration, and prompt templates are just text files you can version control.

### When to Use Each Pattern

| Pattern | Use when | Example |
|---------|----------|---------|
| **Prompt file + general agent** | Portable skills, version-controlled prompts, simple delegation | "Analyze this PR using the reviewer prompt" |
| **context:fork with agent type** | Builtin agent behavior matches your need (Explore, Plan) | "Explore this codebase and summarize" |
| **Custom .claude/agents/ definition** | Complex reusability, same settings/hooks across uses | "Database reviewer agent with specific tool allowlist" |

### Complete Example Workflow

**Step 1:** Create a prompt template file at `agents/researcher.md`:

```markdown
# Research Analyst Persona

## Your Role
You are a research specialist focused on finding recent, credible sources and cross-referencing claims.

## Your Approach
1. Start with web search to find sources from the last 12 months
2. Cross-reference claims across at least 3 independent sources
3. Identify consensus vs disagreement in the field
4. Cite all sources with URLs

## Output Format
Return findings as markdown with:
- Section headers for each theme
- Bullet points for key findings
- Inline citations like [source](url)
```

**Step 2:** In your skill, reference and use it:

```markdown
Read agents/researcher.md. Then spawn a general-purpose subagent with:

"""
$(cat agents/researcher.md)

Query: $ARGUMENTS

Return your findings as markdown with source citations.
"""
```

**Note:** `$ARGUMENTS` substitutes all user-provided arguments. Use `$0`/`$1`/`$2` for positional args, or named args from the `arguments` frontmatter field.

### Template for agent/*.md Files

Copy this template when creating new prompt files:

```markdown
# [Role Name]

## Your Role
[Brief description of what this agent does]

## Your Approach
[Step-by-step methodology or key principles]

## Output Format
[Expected structure for results]
```

### Best Practices for Portable Prompts

- **Keep prompts under 200 lines** — Easier to read and iterate
- **Use clear section headers** — Makes prompts navigable
- **Include examples in the prompt file** — Shows the agent expected output format
- **Version control alongside skill** — Both evolve together
- **Avoid hardcoded paths** — Use `$ARGUMENTS` and string substitutions
- **Test prompts independently** — You can read the file and try it manually before integrating

---

## Trigger Optimization Workshop

Writing descriptions that trigger reliably is the #1 skill authorship challenge.

### The Trigger Testing Loop

1. **Write candidate description** → 2. **Test with 10 queries** → 3. **Analyze misses** → 4. **Refine** → 5. **Repeat**

### Test Query Bank Construction

Build three categories:
- **Should trigger:** 5-10 real phrases users might say
- **Should NOT trigger:** 3-5 edge cases (related but wrong skill)
- **Boundary cases:** Ambiguous queries where reasonable people disagree

### Description Tuning Knobs

| Symptom | Fix | Example |
|---------|-----|---------|
| Never triggers | Add USE WHEN with explicit phrases | "Use when user says 'deploy', 'ship', 'release'" |
| Triggers too often | Add NOT clause | "NOT for: local development, testing" |
| Triggers on wrong intent | Narrow the action verb | "Generate" ≠ "Review" ≠ "Fix" |

### Measuring Success

- Trigger rate on should-trigger cases: >90%
- False positive rate on should-not cases: <10%
- If both pass → description is ready

---

## When to Split vs Combine Skills

### Split When:
- Trigger contexts are disjoint (React vs Python skills)
- Different model/effort needs (haiku format vs opus architect)
- Distinct user audiences (devops vs frontend)
- Body exceeds 500 lines and sections are independently useful

### Combine When:
- Same trigger context, slight variations in behavior
- Shared reference material (duplication > 500 lines)
- Workflow sequence (deploy → verify → notify)

### The 3-Skill Heuristic

If you find yourself creating 4+ related skills, consider:
- One orchestrator skill (workflow)
- Two execution skills (specialized tasks)
- Zero cross-references (descriptions route, not names)

---

## Skill Anatomy

```
skill-name/
├── SKILL.md              # YAML frontmatter + body (<500 lines)
├── agents/               # Prompt templates for portable delegation
├── scripts/              # Only for deterministic/fragile operations
├── references/           # One level deep — schemas, cheatsheets
└── assets/              # Templates, JSON schemas
```

### Writing Style

- **Third-person imperative:** "Extract...", "Run...", "Validate..."
- **Explain the why** behind requirements — agents reason better from principles than rigid rules
- **Lean:** Remove anything not pulling its weight
- **Degree of freedom:** Match specificity to fragility. High freedom = text only. Low freedom = scripts with no parameters

---

## Skill Scope — Where Skills Live

| Scope | Location | When to use | Priority |
|-------|----------|-------------|----------|
| **Enterprise** | Via managed settings | Organization-wide, admin-enforced | 1 (highest) |
| **Personal** | `~/.claude/skills/{name}/SKILL.md` | Personal, cross-project | 2 |
| **Project** | `{project}/.claude/skills/{name}/SKILL.md` | Project-specific | 3 |
| **Plugin** | `<plugin>/skills/<name>/SKILL.md` | Bundled with plugins | 4 |

**Priority:** `enterprise > personal > project > plugin`. Personal beats project when both exist.

**Trigger conflict:** When multiple skills match a query, the highest-priority skill triggers. Within the same scope, the model selects based on semantic match to descriptions.

---

## Frontmatter Reference

```yaml
---
name: my-skill                    # Lowercase/hyphens only, max 64 chars
description: What this skill does. Put key use case FIRST. Truncated at 1,536 chars with when_to_use.
when_to_use: Additional trigger phrases/contexts. Appended to description.
argument-hint: [issue-number]      # Autocomplete hint after /skill-name
arguments: [issue, branch]          # Named positional args → $issue, $branch in content
disable-model-invocation: true    # true = only YOU invoke. For side-effect ops (deploy/push/delete)
user-invocable: false            # true = hidden from / menu, Claude auto-loads by relevance only
allowed-tools: Read Grep          # Tools pre-approved during skill. Does NOT restrict.
model: sonnet                    # Override: sonnet/opus/haiku/full-ID/inherit
effort: high                      # Thinking budget: low/medium/high/xhigh/max
context: fork                     # Run skill body in isolated subagent
agent: Explore                    # Subagent type: Explore/Plan/general-purpose
hooks:                            # Hooks scoped to skill lifecycle
paths: src/**/*.kt               # Glob patterns for auto-activation by file path
shell: bash                        # Shell for command execution blocks
---
```

### Field Details

| Field | Type | Description |
|-------|------|-------------|
| `name` | string | Display name. Omit → uses directory name. Max 64 chars, lowercase/hyphens |
| `description` | string | Primary routing signal. Semantic intent, not keywords. Truncated at 1,536 chars combined with `when_to_use` |
| `when_to_use` | string | Additional trigger contexts. Appended to description in listing |
| `argument-hint` | string | Autocomplete hint after `/skill-name` (e.g., `"[issue-number]"`). UI-only, does not enable argument substitution. |
| `arguments` | list | Named positional args → `$name` substitution in order. Required for `$ARGUMENTS`/`$0`/`$1` to work. Can be used without `argument-hint`. |
| `disable-model-invocation` | bool | `true` → only you invoke. **Breaks `skills:` preloading in subagents** |
| `user-invocable` | bool | `false` → hidden from `/` menu, auto-loads by relevance |
| `allowed-tools` | list | Tools pre-approved during skill. Does NOT restrict available tools |
| `model` | string | Override session model. `sonnet`/`opus`/`haiku`/`claude-sonnet-4.6`/`claude-opus-4.6`/`claude-haiku-4.5`/full-ID/`inherit`. Use when skill needs specific model capabilities (Haiku for fast read-only, Opus for complex reasoning). Default `inherit` uses session model. |
| `effort` | string | Thinking budget override: `low`/`medium`/`high`/`xhigh`/`max`. Use for skills that benefit from extended reasoning (complex analysis, multi-step planning). Default inherits session effort. |
| `context` | string | Set `fork` to run body in isolated subagent context |
| `agent` | string | Subagent type when `context:fork`: `Explore`/`Plan`/`general-purpose` |
| `hooks` | map | Hooks scoped to skill lifecycle. Hook types: `command` (shell), `http` (web request), `mcp_tool` (MCP call), `prompt` (injected prompt), `agent` (subagent spawn). See hooks guide for lifecycle events. |
| `paths` | list | Glob patterns for auto-activation. Skill loads only for matching file paths |
| `shell` | string | Shell for command execution blocks: `bash` (default) or `powershell`. Use `powershell` on Windows where bash is unavailable. |

### Invocation Matrix

| Frontmatter | You invoke | Claude invokes | Description loaded |
|-------------|-----------|----------------|-------------------|
| (default) | Yes | Yes | Always in context |
| `disable-model-invocation: true` | Yes | **No** | Only when you invoke |
| `user-invocable: false` | **No** | Yes | Always in context, hidden from `/` |

### String Substitutions

| Variable | Value |
|----------|-------|
| `$ARGUMENTS` | All arguments passed (appended if not in content) |
| `$ARGUMENTS[N]` / `$N` | Arg by 0-based index |
| `$name` | Named arg from `arguments` field, mapped by position |
| `${CLAUDE_SESSION_ID}` | Current session ID |
| `${CLAUDE_EFFORT}` | Current effort level |
| `${CLAUDE_SKILL_DIR}` | Absolute path to skill's SKILL.md directory |

---

## Common Pitfalls

### 1. The Vague Description

Bad: "Helper for deployments"
Good: "Deploy to production via bin/deploy.sh. Use when user says 'deploy' or 'ship'."

**Why:** Claude doesn't know what "helper" means. Be explicit about action and trigger.

### 2. The Missing Guard Rail

Bad: Skill that runs `rm -rf` without `disable-model-invocation: true`
Good: Always set `disable-model-invocation: true` for destructive skills

**Why:** Claude might auto-invoke when you're just asking about deployment strategy.

### 3. The Brittle Path Reference

Bad: `Read ~/projects/my-repo/templates/config.yaml`
Good: `Read ${CLAUDE_SKILL_DIR}/../templates/config.yaml`

**Why:** Hardcoded paths break when skills move. `${CLAUDE_SKILL_DIR}` is portable.

### 4. The Overly-Broad Permission

Bad: `allowed-tools: [Bash]`
Good: `allowed-tools: [Bash(git log:*), Bash(git diff:*)]`

**Why:** `Bash` alone permits ANY command. Scope to exactly what's needed.

### 5. The Undeclared Dependency

Bad: Skill uses MCP server but never mentions it
Good: "Requires [MCP server] installed and configured"

**Why:** Users copy skills without knowing about external dependencies.

### 6. The Recursive Trigger

Bad: Skill A says "also use skill B", skill B says "also use skill A"
Good: Let descriptions route. No cross-references in bodies.

**Why:** Creates brittle dependency graphs. Descriptions should be self-routing.

---

## When Your Skill Isn't Working

### Symptom: "Claude never uses my skill"

**Diagnostic:**
1. Run `/skills` — is your skill listed?
2. Check description: does it have explicit trigger phrases?
3. Test query: would YOU pick this skill based on the description?

**Fixes:**
- Add "Use when: [phrase1], [phrase2], [phrase3]" to description
- Add `when_to_use:` frontmatter with more triggers
- Check for `disable-model-invocation: true` (prevents auto-trigger)
- Verify skill is in watched directory

### Symptom: "Claude uses my skill at the wrong time"

**Diagnostic:**
1. What was the user's actual query?
2. What in your description matched that query?
3. Is the description too broad?

**Fixes:**
- Add "NOT for: [wrong contexts]" to description
- Narrow the action verb ("Generate" vs "Review" vs "Fix")
- Use `paths:` to restrict to specific file types
- Consider `disable-model-invocation: true` if it's a manual workflow

### Symptom: "Skill loads but doesn't do what I want"

**Diagnostic:**
1. Is the instruction clear? (imperative mood: "Extract...", not "You should extract")
2. Are tool calls scoped correctly? (`allowed-tools`)
3. Are there unexplained placeholders? (unsubstituted `$ARGUMENTS`)

**Fixes:**
- Rewrite instructions as step-by-step imperatives
- Add `allowed-tools:` if skill needs specific tools without prompting
- Test substitutions: invoke with `/skill-name test arg` and check `$0` expansion

---

## Skills vs Rules vs Agents — Decision Guide

**Quick reference:**
- CLAUDE.md = **what** your project is (context, conventions)
- Rules = **principles** (always-true heuristics, ~100 lines)
- Skills = **procedures** (step-by-step workflows, ~300+ lines)
- Agents = **who** to delegate (specialist personas)

**When to promote:** CLAUDE.md section grown into procedure → move to skill. Skill body exceeds ~30 lines of domain knowledge → split: keep role in agent, move knowledge to skill via `skills:` field.

---

## Contrast with create-skills

This skill (skill-creator) teaches **methodology**:
- How to write descriptions that trigger reliably
- How to structure skill bodies for progressive disclosure
- How to use context:fork and portable subagent prompts
- How to optimize triggers with train/test methodology

The create-skills skill teaches the **plugin's workflow** for skill creation:
- The specific steps to create a skill within this plugin
- How to integrate new skills into the plugin structure
- The conventions specific to this plugin's skill ecosystem