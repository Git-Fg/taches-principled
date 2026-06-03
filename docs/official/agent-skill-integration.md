---
description: Agent-skill integration patterns, skill preloading rules, and context distinction
when_to_read: Before adding skills to agents or understanding context: fork field
path: ./official/agent-skill-integration.md
---

> ## Documentation Index
> Fetch the complete documentation index at: https://code.claude.com/docs/llms.txt
> Use this file to discover all available pages before exploring further.

# Agent-Skill Integration Patterns

Source: [Claude Code Subagents Documentation](https://code.claude.com/docs/en/sub-agents) and [Claude Code Skills Documentation](https://code.claude.com/docs/en/skills)

---

## The Core Distinction

| Field | Location | Purpose |
|-------|----------|---------|
| `context: fork` | SKILL frontmatter | Runs skill in an isolated forked subagent context |
| `skills:` | AGENT frontmatter | Preloads skill content into subagent at startup |

These are separate mechanisms serving different purposes:
- **`context: fork`** is a SKILL feature — makes the skill run in a subagent
- **`skills:`** is an AGENT feature — gives the agent the skill's methodology

---

## Skills Preloading Philosophy

**"Better too much than not enough."**

All potentially relevant skills MUST be preloaded across all agent types. This is not optional guidance — it is a mandatory constraint for deterministic capability access. The outdated rule that restricted skill preloading exclusively to evaluation or critique agents is hereby retired.

### Why This Philosophy

1. **Progressive disclosure makes preloading efficient.** Properly authored skills are structured for progressive disclosure: frontmatter metadata is lightweight, and deeper reference files load only on demand. The baseline context consumption from preloading a skill is extremely low.

2. **Capability access must be deterministic.** An agent that might need a capability must have it preloaded — not discover mid-task that a skill is unavailable. Orchestrated workflows and ad-hoc direct invocations both require deterministic access.

3. **The AI retains lazy-loading autonomy.** While base skills are preloaded deterministically, the AI retains full autonomy to decide whether it needs to lazily load deeper reference files from those skills based on the specific task at hand. Preloading is not the same as processing.

### Decision Rule

**"Could this agent's task possibly benefit from this skill?"**

If yes — preload. Do not second-guess, conditionally filter, or optimize for narrow scope. The cost of preloading a skill that goes unused is measured in tokens; the cost of missing a skill mid-task is measured in capability failure.

| Agent Type | Preload? | Rationale |
|-----------|----------|-----------|
| Evaluation | YES | Framework needed to assess against |
| Audit | YES | Framework needed to check compliance |
| Critique | YES | Framework needed to assess quality |
| Execution | YES | May encounter any pattern during implementation |
| Research | YES | Discovery path unpredictable, any skill may apply |
| Explorer | YES | Investigation scope unknown at spawn |

**Anti-pattern to remove:** The old rule that execution and research agents should NOT preload skills. This created capability gaps — agents that needed methodology mid-task but didn't have it loaded.

### Cross-Plugin Skill Preloading

**It is perfectly safe and highly recommended to preload skills from plugins that may not currently be installed on the user's machine.** Claude Code evaluates the `skills:` frontmatter array dynamically at startup; if a requested skill is unavailable or uninstalled, the system gracefully ignores it without throwing an error. Because properly authored skills rely on progressive disclosure, their baseline context consumption is extremely low. Aggressively preloading all potentially relevant methodology skills ensures maximum deterministic capability access with zero risk of breaking the agent. An agent can list `sadd`, `fpf`, `tdd`, and `ddd` in its `skills:` array even when the user has only the core plugin installed — unsupported skills are silently skipped.

---

## Correct Pattern Examples

### Universal Preloading Pattern

```yaml
---
name: implementer
description: Implements based on explicit specifications
skills: [implement-task, tool-design, rules-orchestration]
---
# Executes specs — preloads implementation skills for deterministic access
```

```yaml
---
name: researcher
description: Researches topics via web search and documentation
skills: [diagnose, improve]
---
# Research path unpredictable — preloads for any methodology needed
```

### Evaluation Agent — Explicit Framework Preloading

```yaml
---
name: grader
description: Evaluates skill quality against grading rubric
skills: [skill-authoring]
---
# Evaluates against skill-authoring methodology
```

```yaml
---
name: sadd-judge
description: Evaluates solutions against SADD criteria
skills: [sadd]
---
# Evaluates against SAD (Structured Agent-Driven Development) methodology
```

---

## Progressive Disclosure in Context Economy

Skills authored for progressive disclosure deliver value at multiple tiers:

| Layer | Triggers | Context Cost |
|-------|----------|--------------|
| Frontmatter (name + description) | Always injected | ~200 tokens |
| SKILL.md body | Skill loaded, body accessed | Variable by skill size |
| `references/` files | Explicitly referenced in body | Only when loaded |

**Baseline cost is low.** A skill's frontmatter + lightweight body is typically under 500 tokens. This is the cost of deterministic capability access.

**Lazy loading handles deep content.** When a skill body references a `references/` file, that file loads only if the agent's task actually requires it. Preloading the skill does not preload all its references — it only makes the skill available.

**The AI decides depth.** The spawned agent, having preloaded the skill's baseline content, retains full autonomy to lazily load deeper reference files or not based on whether the task at hand requires them.

---

## Anti-Patterns

| Anti-pattern | Problem | Correction |
|-------------|---------|------------|
| Selective preloading by agent type | Capability gaps when agent encounters unexpected task requirements | Preload ALL potentially relevant skills on ALL agents |
| Blanket removal of preloads | Loses framework context for evaluation agents | Keep preloads — they are load-bearing for evaluation |
| Adding `context: fork` to agent definitions | Not a valid agent field | Remove — use SKILL frontmatter instead |
| Conditional preload based on task framing | Unpredictable task paths require uniform capability access | Preload unconditionally — lazy loading handles depth |
| Optimizing for narrow scope | Agents that receive expanded scope mid-task fail | Cast wide — deterministic access over narrow optimization |

---

## Marketplace Convention

**"Preload broadly; load deeply on demand."**

This separation is load-bearing:
- **Preloading** delivers base skill content deterministically (low cost, always available)
- **Lazy loading** delivers deep reference content only when required (zero cost until needed)
- **Skills** teach WHAT to do (routing, delegation, methodology) — preloaded
- **Agents** own HOW to execute (evaluation criteria, verification protocols) — preloaded with all relevant skills

---

## Quick Reference

```yaml
# All agents — preload potentially relevant skills
skills: [skill-authoring, subagent-orchestration, diagnose, improve]

# Execution agent — with execution-relevant skills
skills: [implement-task, tool-design]

# Research agent — with research and discovery skills
skills: [diagnose, ideation]

# Evaluation agent — with framework it evaluates against
skills: [some-framework]
```

```yaml
# Skill for subagent execution — context: fork
context: fork
agent: general-purpose
```
