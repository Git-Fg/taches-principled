# Agent Definition Quality Audit

Audit Date: 2026-05-23
Scope: plugins/taches-principled/agents/ and skills/*/agents/

---

## Summary

17 agent definitions audited. Most are well-structured with proper spawn footers, failure signals, and clear role definitions. However, several quality issues were identified.

---

## Agents with Invalid Frontmatter

**`skill-auditor.md:1-6`** — Invalid field `hooks` in agent frontmatter
- `hooks` is a skill field, not an agent field. Agent frontmatter should only contain: name, description, model, effort, context, tools, disallowedTools, skills, mcpServers, paths, shell, systemPrompt, background, isolation, memory.
- Impact: Agent configuration may not load correctly in some contexts.

**`grader.md:1-6`** — Same issue: invalid field `hooks` in agent frontmatter

**`comparator.md:1-6`** — Same issue: invalid field `hooks` in agent frontmatter

**`analyzer.md:1-6`** — Same issue: invalid field `hooks` in agent frontmatter

---

## Agents with Generic Descriptions

**`implementer.md` (create-plans)** — Line 3
```
description: Implements specific tasks based on clear specifications.
```
- "Implements specific tasks" — too generic. No trigger phrases. What would cause Claude to invoke this agent vs. any other?
- Compare to `execute-implementer.md`: "Executes plan tasks by implementing code changes. Use when a plan task requires building or modifying files according to a specification." — much clearer trigger.

**`researcher.md` (create-plans)** — Line 3
```
description: Researches technologies, libraries, APIs, and best practices for unfamiliar components.
```
- "Researches technologies, libraries, APIs" — no specific trigger phrases. When would Claude spawn this vs. just searching directly?

**`verifier.md` (create-plans)** — Line 3
```
description: Verifies implementations against specifications, runs tests, and checks for regressions.
```
- "Verifies implementations" — no trigger phrases. Compare to `execute-verifier.md` which includes "Use after implementer completes to validate correctness."

---

## Agents Missing Required Sections

**`explorer.md` (create-plans)** — Missing Failure Signal
- Has spawn footer but no explicit failure signal schema like other agents.
- All other evaluation pipeline agents (grader, comparator, skill-auditor, subagent-auditor, analyzer) have it. This explorer doesn't.
- **Note:** explorer.md has `tools: Read, Write, Grep, Glob, Bash` which is appropriate for its investigation role.

**`architect.md` (create-plans)** — Missing Failure Signal
- Same issue — no failure signal schema.

---

## Agents with Tool Gaps

**`code-reviewer.md`** — Missing Write tool
- Line 4: `tools: Read, Grep, Glob`
- A code reviewer finding issues might want to write a report. But since the report goes to orchestrator via structured output (not a file), this may be intentional. However, most other analysis agents have Write.
- **Verdict:** Acceptable but inconsistent. If the agent needs to write findings to a file for persistence, it cannot.

**`create-plans/critic.md`** — Missing Write tool
- Line 5: `tools: Read, Grep`
- Review output goes to orchestrator. Acceptable for read-only analysis role.

---

## Agents with Bloated Body

**`skill-auditor.md`** — 229 lines
- This agent body is substantial (229 lines), but it is an evaluation agent that duplicates skill-auditing logic from the skill-auditor SKILL.md in the taches-principled plugin.
- The agent describes itself as part of a pipeline but the body essentially replicates what a skill with the same name does.
- Per CLAUDE.md guidance: "If body is >30 lines, it's duplicating a skill which is waste."

**`prompt-engineer.md`** — 126 lines
- The prompt-engineer skill in create-prompts skill is the canonical source. This agent is 126 lines but essentially restates the skill content.

**`grader.md`** — 184 lines
- Evaluation agent with substantial content. The grading rubrics and output formats are appropriate for the agent's specialized role, but the body length approaches waste territory.

**`comparator.md`** — 137 lines
- Comparison logic duplicated from evaluation pipeline design documented elsewhere.

**`analyzer.md`** — 117 lines
- Synthesis logic is evaluation-specific, not duplicating a skill per se.

---

## Anti-Pattern Examples

### 1. XML-style structure in skill-auditor.md
**Lines 71-75:**
```markdown
**Forbidden**:
- Checkpoint types: `### Step 1`, `### Step 2` (procedures, not principles)
- XML-style tags (use markdown sections instead)
```
The agent forbids XML-style tags but uses extensive markdown tables (which is fine). This is self-referential inconsistency.

### 2. Vague constraint in explorer.md
**Line 63:**
```markdown
- Report only what's discovered, not assumed
```
Vs. execute-plans agents which have concrete constraints like "Only modify files within your assigned scope". This constraint is vague — what counts as "assumed"?

### 3. Missing severity classification in explorer.md
The explorer outputs findings without severity ranking. Other critique agents (critic, execute-critic) classify issues as CRITICAL/WARNING/SUGGESTION. Explorer doesn't.

### 4. Inconsistent spawn footer format
Most agents use:
```markdown
**Spawn footer:** You are a subagent executing a delegated task...
```

But `create-plans/agents/critic.md` line 114 says:
```markdown
**Spawn footer:** You are a subagent executing a delegated task...
```
This is correct but buried at line 114 after the YAML frontmatter. The standard pattern among other agents is to put spawn footer as the LAST section before closing `---`, not mid-file.

### 5. Variable template inconsistency
Some agents use `{{variable}}` syntax:
- `implementer.md` (create-plans): `{{context}}`, `{{task}}`, `{{spec}}`
- `explorer.md` (create-plans): `{{context}}`, `{{scope}}`, `{{task}}`

Others don't use variables at all:
- `execute-implementer.md` uses `{{context}}`, `{{files}}`, `{{task}}`, `{{verify}}`
- The variable templates are not validated anywhere — no schema enforcing what variables an agent expects.

---

## Strengths

1. **spawn-footer** is present in all 17 agents — consistent pattern established
2. **failure signal** schema is present in 14/17 agents — `explorer.md` and `architect.md` are exceptions
3. **output format** defined in all agents — structured reporting is standard
4. **model selection** is appropriate — haiku for fast/ exploration, sonnet for analysis/implementation
5. **role names** are descriptive and kebab-case — code-reviewer, skill-auditor, prompt-engineer, etc.
6. **create-plans agents** have proper separation: explorer (haiku), researcher (sonnet), architect (sonnet), critic (sonnet), implementer (sonnet), verifier (haiku)

---

## Quick Fixes

1. **skill-auditor.md, grader.md, comparator.md, analyzer.md** — Remove invalid `hooks` field from frontmatter
2. **explorer.md (create-plans)** — Add failure signal schema at end
3. **architect.md (create-plans)** — Add failure signal schema at end
4. **implementer.md (create-plans)** — Add trigger phrase to description (e.g., "Use when a plan specifies concrete tasks with files and verification criteria")
5. **researcher.md (create-plans)** — Add trigger phrase (e.g., "Use when implementation encounters unfamiliar libraries or patterns")
6. **verifier.md (create-plans)** — Add trigger phrase (e.g., "Use after implementer completes to validate correctness")

---

## Context for Future Review

- The `skill-auditor.md` agent at `plugins/taches-principled/agents/skill-auditor.md` audits skills, not agents. The subagent-auditor.md audits agent definitions. These are separate concerns.
- Agent definitions in `skills/*/agents/` are prompt templates for spawning general-purpose subagents — they are not auto-discovered system agents like those in `plugins/taches-principled/agents/`.
- The evaluation pipeline (grader → comparator → skill-auditor → analyzer) is aspirational per CLAUDE.md, not yet fully operational in any skill.