---
description: Agent-skill integration patterns, skill preloading rules, and context distinction
when_to_read: Before adding skills: to agents or understanding context: fork field
---

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

## When to Preload Skills in Agents

**Decision rule:** "Does this agent's job require knowing the skill's methodology?"

| Agent Type | Preload? | Rationale |
|-----------|----------|-----------|
| Evaluation | YES | Evaluates against framework criteria |
| Audit | YES | Checks compliance with framework |
| Critique | YES | Assesses against framework |
| Execution | NO | Receives specs from orchestrator |
| Research | NO | Task-driven, not framework-dependent |

**Why:** Evaluation/critique agents need the framework to assess against. Execution agents receive pre-digested specifications — they execute, not evaluate.

---

## Correct Pattern Examples

### Agents That SHOULD Preload

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
name: judge
description: Evaluates solutions against SADD criteria
skills: [sadd]
---
# Evaluates against SAD (Structured Agent-Driven Development) methodology
```

```yaml
---
name: hypothesis-generator
description: Generates hypotheses for FPF PROPOSE cycle
skills: [fpf]
---
# Uses FPF (First Principles Thinking) methodology
```

### Agents That SHOULD NOT Preload

```yaml
---
name: implementer
description: Implements based on explicit specifications
---
# Receives specs from orchestrator, no framework needed
```

---

## Anti-Patterns

| Anti-pattern | Problem | Correction |
|-------------|---------|------------|
| Blanket removal of all skill preloads | Evaluation agents NEED framework context | Keep preloads for evaluation/critique types |
| Adding `context: fork` to agent definitions | Not a valid agent field | Remove — use SKILL frontmatter instead |
| Circular dependencies | Skill spawns agent, agent preloads skill without need | Only preload when agent evaluates against framework |
| Preloading skills in execution agents | Wastes context on unused methodology | Executors receive specs, not frameworks |
| Preloading skills in research agents | Methodology not needed for task-driven work | Research is task-oriented, not framework-dependent |

---

## Marketplace Convention

**"Agents evaluate against frameworks; skills orchestrate execution."**

This separation is load-bearing:
- **Skills** teach WHAT to do (routing, delegation, methodology)
- **Agents** own HOW to execute (evaluation criteria, verification protocols)
- **Agents that evaluate** preload the framework they assess against
- **Agents that execute** receive specs from the orchestrator without preloading

---

## Quick Reference

```yaml
# Evaluation agent — preload required
skills: [framework-skill]

# Execution agent — no preload
(no skills field)

# Research agent — no preload
(no skills field)
```

```yaml
# Skill for subagent execution — context: fork
context: fork
agent: general-purpose
```
