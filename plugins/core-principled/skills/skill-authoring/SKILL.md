---
name: skill-authoring
description: "Create, optimize, and test Claude Code skills, including metadata refinement and trigger benchmarking."
allowed-tools: Read, Edit, Write, Grep, Glob
when_to_use: "Use when building new capabilities, fixing skill routing, or optimizing trigger signals. Do NOT use for general code authoring or project planning."
---

## Routing Guidance

- WORKFLOW mode activates when user says "build a skill", "make a skill for X", "write a skill", "create a new skill", "add a skill", or "I need to author a skill".
- METHODOLOGY mode activates when user asks to "optimize skill descriptions", "benchmark triggers", "improve routing", "fix trigger issues", "test if my skill fires", or "fix why my skill doesn't load".
- Do NOT use for general code writing or project planning.
- Use `context: fork` when this skill orchestrates multiple steps, produces heavy parallel output, or builtin agent behavior matches the goal.
- Do NOT use when the skill is simple (single tool call), you need intermediate results in main conversation, or builtin behavior contradicts this skill's purpose.

## Decision Router

IF creating a new skill within this plugin's structure → use **WORKFLOW** mode

IF writing descriptions that trigger reliably → use **METHODOLOGY** mode

IF optimizing existing trigger performance → use **METHODOLOGY** mode

---

## WORKFLOW MODE

*Creating new skills in this plugin's structure*

### Pre-Flight Validation Checklist

Before committing a skill, verify:

- [ ] Description triggers on intended inputs (test with `claude -p`)
- [ ] Description does NOT trigger on off-topic inputs (expect 0)
- [ ] Description ≤ 150 chars
- [ ] when_to_use ≤ 200 chars
- [ ] Body ≤ 500 lines
- [ ] No invalid frontmatter fields (metadata, related_skills, tags)
- [ ] Skill name is kebab-case, max 64 chars, no XML tags, no "anthropic" or "claude"
- [ ] Numeric thresholds present if applicable
- [ ] Anti-Patterns section with concrete wrong/right pairs
- [ ] Security audit: bundled scripts reviewed for unexpected network calls or unauthorized system access

### Skill Categories

Skills fall into five categories. Each has a different purpose and design pattern.

| Category | Purpose | Test |
|----------|---------|------|
| **Constraint/Guardrail** | Override the agent's DEFAULT behavior | "Does this change what the agent produces by default?" |
| **Orchestration** | Route work to the right specialist at the right time | "Does this define WHEN to delegate?" |
| **Domain Expertise** | Provide deep knowledge the base model lacks | "Would plausible-but-wrong outputs result without this?" |
| **Quality Assurance** | Enforce verification gates BEFORE completion | "Does this define what evidence must exist?" |
| **Creative Direction** | Break output convergence toward generic responses | "Does this prevent AI slop?" |

**Real examples:**
- Constraint: "NEVER use console.log. Always use src/lib/logger.ts" (one constraint changed 200+ sessions)
- Orchestration: "When scope is unclear → delegate to tp-explorer. When scope is clear → delegate to implementer"
- Domain Expertise: Company-specific pricing logic that the base model gets wrong
- Quality Assurance: "Before marking complete: (1) tests pass, (2) no type errors, (3) screenshot attached"
- Creative Direction: "We reject generic AI aesthetics. Pick: Brutalist OR Maximalist OR Retro-futuristic"

**How categories map to Policy vs. Mechanism:**
- Constraint = pure mechanism (redirecting default output)
- Orchestration = pure policy (routing decisions without execution)
- Domain/QA/Creative = mechanism (what the agent does when it acts)

### Policy vs. Mechanism

**Policy** = when a skill should trigger (the routing decision)
**Mechanism** = what the skill teaches and how it guides behavior

A skill conflating policy and mechanism produces:
- Skills too broad (trigger too generic)
- Skills too narrow (trigger too specific)
- Skills that know WHEN but not HOW (vague guidance)
- Skills that know HOW but not WHEN (can't decide when to act)

Good skill design separates:
- Frontmatter: policy (name, description, when_to_use, triggers)
- Body: mechanism (principles, patterns, anti-patterns, examples)

### The Core Insight

**Skills share the context window with everything else.** Every token competes with the user's request, conversation history, and other loaded content. Skills use progressive disclosure across three levels:

- **Level 1 (Metadata):** Always loaded at startup. Put routing signals here.
- **Level 2 (Instructions):** Loaded when triggered via bash. Put essential principles in SKILL.md.
- **Level 3 (Resources & Code):** Loaded as needed via bash. Put details, schemas, and executable scripts here to consume zero tokens until accessed.

- Assume Claude is smart. Don't explain obvious things.
- If a line doesn't earn its keep, delete it.

### What Good Looks Like

Design principles for skills:

- **Clear routing signal** — description tells Claude exactly when to act and when not to
- **Principle first** — opening lines set the mental model before details compete
- **Structure follows purpose** — organize around how the reader thinks
- **Concision is respect** — every line competes for context space
- **One vivid example** — teaches judgment better than ten edge cases

### Numeric Thresholds

| Metric | Limit | Why |
|--------|-------|-----|
| Description length | 1024 chars max | Official limit; use the full space |
| when_to_use length | 200 chars max | Longer = context bloat, not better routing |
| Skill body | 500 lines max | Beyond = principle dilution; split or reference |
| Tools allowed | 7 max | Beyond = coordination overhead |
| Spawn prompt length | 1500 tokens max | Reliability drop beyond this |

**Split signal:** If a skill needs >7 tools, >500 lines, or covers multiple concerns — split into focused skills.

### When to Use Folders

Simple skills (one focused task) → single SKILL.md file

Complex skills (multiple workflows, extensive domain knowledge) → use folders:

```
skill-name/
├── SKILL.md          # Principles, routing
├── agents/           # Bundled subagent prompts
├── references/       # Step-by-step procedures + domain knowledge
├── templates/        # Output structures
└── scripts/          # Executable code
```

**WARNING - Discovery Depth Limit:** Automatic skill discovery only scans 1 level deep. Do not nest skills inside category folders (e.g., `skills/category/skill-name/SKILL.md`), or they will not be found by the Skill tool and will require manual Glob scanning to locate.

**When to use agents/ vs inline:**
- Use `agents/` when: reused by multiple skills, needs independent versioning, or must be portable
- Use inline when: single-skill-specific, simple, or tied directly to skill's body text

### Common Mistakes

- **Over-explaining.** Only explain what's specific to your domain.
- **Generic descriptions.** "Helps with code" → Claude won't know when to use it.
- **No success criteria.** How does Claude know when it's done?
- **Inconsistent structure.** Random organization forces Claude to hunt for information.
- **Too many examples.** One good example teaches more than five mediocre ones.

### Testing Your Skill

**Headless trigger validation:**

```bash
claude -p "<test-query>" \
  --output-format stream-json \
  --include-partial-messages \
  2>&1 | grep -o '"skill-name"'
```

**Train/test split:** Keep 4-5 held-out cases. If 100% on training but fails on held-out → overfit. Rebuild with genuinely different queries.

**Collect test queries:**
- Real user prompts that should trigger your skill
- Synthesize edge cases (variations, paraphrases)
- Include negative cases (queries that should NOT trigger)

### Anti-Patterns

| Wrong | Right | Why |
|-------|-------|-----|
| "Helps with coding tasks" | "Reviews Python code for security vulnerabilities" | Vague triggers nothing; specific routes correctly |
| "Use when writing Go code" (too broad) | "Use when user adopts library/foo" | Restrict to single concern |
| Generic name "helper" | Domain noun "security-audit" | "helper" has no semantic anchor |
| Version metadata per file | Git history as source of truth | Version numbers never control anything |

---

## METHODOLOGY MODE

*Trigger optimization, context:fork patterns, frontmatter precision*

### Writing Frontmatter

The description is a routing prompt, not a keyword tag. Write for the model's linguistic reasoning — a good description triggers for "generate a presentation" even without the word "pptx".

**Key rules:**
- **<150 characters** in description (keeps ~20+ skills under 1% budget)
- **Trigger keywords front-loaded** in first 50 chars (survives truncation)
- **Plain quoted scalar** (`"..."`) not block scalar (`>` or `|-`)
- **"Use when" explicit** — tells Claude when to activate
- **Exclusions in `when_to_use`** — prevents false triggering

### The Optimal Template

```yaml
description: "[Verb] [artifact] for [domain]. Use when user [trigger1], [trigger2], or [trigger3]."
when_to_use: |
  Do NOT use for [exclusion1], [exclusion2].
```

### 5 Optimized Examples

```yaml
# Commit Writer
description: "Writes commit messages from staged changes. Use when user asks to commit, types 'commit this', or 'write a commit message'."
when_to_use: |
  Do NOT use for pushing, merging, or checking status.

# Deploy (side-effect skill)
description: "Deploys to staging or production. Use when user types /deploy, says 'deploy', 'ship', or 'push to prod'."
when_to_use: |
  Do NOT use for building, testing, or code review.
disable-model-invocation: true

# Test Generator
description: "Creates unit tests with edge cases. Use when user asks to 'write tests', 'add test coverage', or 'generate tests'."
when_to_use: |
  Do NOT use for running existing tests.

# Code Review
description: "Reviews code for bugs, security, logic errors. Use when user asks 'review code', 'check PR', 'find bugs', or 'audit this'."
when_to_use: |
  Do NOT use for formatting, linting, or running tests.

# Security Audit
description: "Audits code for OWASP Top 10 security flaws. Use when user mentions 'security', 'vulnerabilities', 'SQL injection', or 'XSS'."
when_to_use: |
  Do NOT use for general code review without security focus.
effort: high
```

### context:fork — When to Use

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

### Portable Subagent Prompts

**Why this matters:** Custom agent definitions require complex configuration and aren't portable. A simpler pattern:

1. **Store** prompt templates as markdown files in `agents/*.md`
2. **Read** them with your native tools when needed
3. **Spawn** a `general-purpose` subagent with that content

```markdown
# Research Analyst Persona

## Your Role
You are a research specialist focused on finding recent, credible sources.

## Your Approach
1. Start with web search for sources from the last 12 months
2. Cross-reference claims across at least 3 independent sources
3. Identify consensus vs disagreement in the field

## Output Format
Return findings as markdown with inline citations like [source](url)
```

Template for new agent files:

```markdown
# [Role Name]

## Your Role
[Brief description of what this agent does]

## Your Approach
[Step-by-step methodology or key principles]

## Output Format
[Expected structure for results]
```

### Trigger Optimization Workshop

**The Trigger Testing Loop:** Write candidate → Test with 10 queries → Analyze misses → Refine → Repeat

**Build three test categories:**
- **Should trigger:** 5-10 real phrases users might say
- **Should NOT trigger:** 3-5 edge cases (related but wrong skill)
- **Boundary cases:** Ambiguous queries where reasonable people disagree

**Description tuning knobs:**

| Symptom | Fix |
|---------|-----|
| Never triggers | Add "Use when user says 'X'" with explicit phrases |
| Triggers too often | Add NOT clause |
| Triggers on wrong intent | Narrow the action verb ("Generate" vs "Review" vs "Fix") |

**Measuring success:** Trigger rate >90%, false positive rate <10%

### When to Split vs Combine Skills

**Split when:**
- Trigger contexts are disjoint (React vs Python skills)
- Different model/effort needs (haiku vs opus architect)
- Distinct user audiences (devops vs frontend)
- Body exceeds 500 lines and sections are independently useful

**Combine when:**
- Same trigger context, slight variations in behavior
- Shared reference material (duplication > 500 lines)
- Workflow sequence (deploy → verify → notify)

### Skill Anatomy

```
skill-name/
├── SKILL.md              # YAML frontmatter + body (<500 lines)
├── agents/               # Prompt templates for portable delegation
├── scripts/              # Only for deterministic/fragile operations. Code never enters context, only output does. Install dependencies locally.
├── references/           # One level deep — schemas, cheatsheets
└── assets/               # Templates, JSON schemas
```

**Writing style:**
- Third-person imperative: "Extract...", "Run...", "Validate..."
- Explain the why behind requirements — agents reason better from principles
- Lean: remove anything not pulling its weight

### File Reference Conventions

**Three canonical rules:**

1. **Path resolution**: Any path within a skill that points to its own supporting content resolves within that skill's folder. Use clean relative paths like `references/file.md`, `agents/template.md`. Never use complex variables like `{baseDir}` or `${CLAUDE_SKILL_DIR}`.

2. **No parent traversal**: File paths MUST NOT use relative parent paths (`../`) to traverse outside the skill directory. Skills are self-contained. Cross-skill references must be semantic (citing a skill or role by name) rather than path-based.

3. **Centralized routing**: ONLY SKILL.md cites supporting files. Reference files must never cross-cite other reference files. The SKILL.md is the sole router — all citations flow through it, never peer-to-peer between references.

**Citation language — deterministic over passive:**
- WRONG: "You can read references/format.md for formatting rules"
- WRONG: "See reference at references/patterns.md"
- RIGHT: "You MUST read `references/format.md` BEFORE writing any code. Do not proceed or make assumptions without reading this file."

Passive citations are ignored by LLMs 99% of the time. Every reference must be a strict imperative with explicit dependency.

### Native Tool Referencing

**The brittle-tool-name problem:** Skills that say "Use the Agent tool" or "Use the Task tool" break when the underlying API migrates. The Task tool was renamed to Agent tool — a skill that hardcoded "Task tool" would fail silently or produce wrong behavior.

**The solution:** Use semantic natural language that delegates to whatever is currently available.

| Brittle (breaks on API rename) | Native (forward-compatible) |
|-------------------------------|------------------------------|
| `Use the Agent tool to spawn` | `Use your native tools to spawn a subagent` |
| `Use the Task tool` | `delegate work via your native tools` |
| `Use the Write tool` | `Use your native tools to write the file` |
| `Use the Edit tool` | `Use your native tools to make the change` |
| `Use the Read tool` | `Use your native tools to read the file` |
| `Use the Bash tool` | `Use your native tools to run shell commands` |
| `Spawn a subagent with Write tool access` | `Spawn a subagent with write access` |

**Why "native tools" works:** The phrase "use your native tools" forces the model to actively consult its dynamically injected tool registry rather than blindly executing a hardcoded string. It acts as a cognitive anchor — the model must enumerate what tools it actually has available and select from that live list, not from a static string in the prompt.

**Principles:**
- Describe capability intent, not tool identity. "write access" beats "Write tool access."
- Use "your native tools" as a generic redirect — it always resolves to the correct current tools.
- Never hardcode tool names in orchestration directives. The names change; the capability intent does not.
- Exceptions: MCP fully-qualified names (`BigQuery:bigquery_schema`) must stay exact — those are server-level identities, not model tools.

### Frontmatter Reference

**Standard fields only** — no custom `metadata` blocks:

| Field | Purpose |
|-------|---------|
| `name` | Display name. Max 64 chars, lowercase/hyphens only, no XML, no "claude"/"anthropic" |
| `description` | Primary routing signal. Semantic intent, not keywords. ≤150 chars (max 1024), no XML |
| `when_to_use` | Additional trigger contexts. ≤200 chars |
| `argument-hint` | Autocomplete hint after `/skill-name` |
| `arguments` | Named positional args → `$name` substitution in order |
| `disable-model-invocation` | `true` = only you invoke. Breaks `skills:` preloading |
| `user-invocable` | `false` = hidden from `/`, auto-loads by relevance |
| `allowed-tools` | Tools pre-approved during skill. Does NOT restrict |
| `model` | Override session model: `sonnet`/`opus`/`haiku`/full-ID/`inherit` |
| `effort` | Thinking budget: `low`/`medium`/`high`/`xhigh`/`max` |
| `context` | Set `fork` to run body in isolated subagent context |
| `agent` | Subagent type when `context:fork`: `Explore`/`Plan`/`general-purpose` |
| `hooks` | Hooks scoped to skill lifecycle |
| `paths` | Glob patterns for auto-activation by file path |
| `shell` | Shell for command execution: `bash` (default) or `powershell` |

### Common Pitfalls

| Pitfall | Fix |
|---------|-----|
| Guidelines-only `context:fork` | A forked skill without actionable tasks wastes the subagent dispatch. Use forks for executing workflows, not injecting reference knowledge. |
| Vague description | "Deploy to production via bin/deploy.sh. Use when user says 'deploy' or 'ship'." |
| Missing guard rail | Set `disable-model-invocation: true` for destructive skills |
| Brittle path reference | Use clean relative paths (e.g., `references/file.md`) — paths resolve within the skill's folder by default |
| Relying on `allowed-tools` for security | `allowed-tools` only partially blocks; tools like `Edit` and `Agent` completely bypass it. Use `disallowed-tools` instead. |
| Undeclared dependency | Document required MCP servers in .mcp.json (see knowledge/raw/official/plugins/plugins-reference.md §MCP servers); plugin agents silently ignore mcpServers frontmatter — declare all MCP servers in the plugin's .mcp.json or plugin.json, not in agent definition files |
| Global package installation | Install packages locally to avoid interfering with the user's computer environment |
| Unsafe network calls | Audit external sources; external dependencies can change and become malicious |
| Recursive trigger | Let descriptions route. No cross-references in bodies. |
| Passive file citations | Never use "You can read" or "See reference" — write "You MUST read `references/X.md` BEFORE proceeding. Do not make assumptions without this file." |

### When Your Skill Isn't Working

**Symptom: "Claude never uses my skill"**
- Add "Use when: [phrase1], [phrase2], [phrase3]" to description
- Check for `disable-model-invocation: true` (prevents auto-trigger)
- Verify skill is in watched directory

**Symptom: "Claude uses my skill at the wrong time"**
- Add "NOT for: [wrong contexts]" to description
- Narrow the action verb ("Generate" vs "Review" vs "Fix")
- Use `paths:` to restrict to specific file types

**Symptom: "Skill loads but doesn't do what I want"**
- Rewrite instructions as step-by-step imperatives
- Check `allowed-tools:` if skill needs specific tools without prompting
- Test substitutions: invoke with `/skill-name test arg` and check `$0` expansion

---

## Reference Index

You MUST read the relevant reference file BEFORE working on that aspect. Do not proceed or make assumptions without reading the applicable reference.

| Reference | Purpose | When to Read (BEFORE this action) |
|-----------|---------|-----------------------------------|
| `references/context-management.md` | Context window principles, SKILL.md vs references/ load strategy | You MUST read this BEFORE deciding what belongs in body vs references/. Do NOT split, merge, or restructure a skill approaching 500 lines or 7 tools without first understanding the three-tier progressive disclosure pattern. |
| `references/skill-self-testing.md` | YAML validation, threshold checks, trigger testing | You MUST read this BEFORE committing any new skill. Do NOT mark a skill complete without running all threshold checks, YAML validation, and trigger tests documented here. |
| `references/cross-skill-discovery.md` | Skill routing, description patterns, name conventions | You MUST read this BEFORE writing or debugging a description that triggers incorrectly. Do NOT modify `description` or `when_to_use` without first understanding the routing patterns documented here. |
| `references/frontmatter-complete.md` | Full frontmatter field reference with examples | You MUST read this BEFORE writing complex frontmatter. Do NOT guess at field types, defaults, or valid values — ALWAYS verify against this canonical reference first. |

---

## Workflow Principle

Skill creation follows phases: requirements → draft → verify → integrate. Each phase is a decision point — proceed when criteria are met, not on a schedule.

**Principle over procedure:** A skill about coordinated work should demonstrate coordination. Frame each phase as a tracked task with clear completion criteria.

For pre-commit verification of threshold checks, ALWAYS spawn a reviewer subagent and loop until no HIGH findings.
Spawn **`tp-skill-auditor`** to audit frontmatter validity, description triggers, and structure.
Spawn **`tp-grader`** to evaluate teaching effectiveness across the four weighted dimensions.
This verifies routing signal density, delta clarity, and anti-pattern quality before the skill enters the loading pool.