# RACE Framework for Spawn Prompts

RACE is a structured format for writing subagent spawn prompts. Each field serves a distinct purpose:

## The Four Fields

### Role
What the subagent IS — its function, expertise, and identity.

> "You are a [specialization] specializing in [specific domain]."

### Action
What the subagent DOES — the methodology or approach sequence.

> "1. [step] 2. [step] 3. [step]"

### Context
What the subagent operates WITHIN — constraints, focus areas, boundaries.

> "Focus on [areas]. Constraints: [rules]. Context provided: [template variables]."

### Expectation
What success looks like — output format, success criteria, quality bar.

> "Return structured findings in this format: [template]. Verification: [how to confirm success]."

## RACE in Existing Agents

Each agent file already demonstrates RACE in practice — this reference is for audit purposes when creating new agents. The mapping below shows how the existing agent structure maps to RACE fields:

| Agent | Role | Action | Context | Expectation |
|-------|------|--------|---------|-------------|
| architect | Analyze requirements, propose solutions | Approach (4-step) | Focus Areas + Constraints | Output Format (trade-off analysis) |
| critic | Review milestones for quality | Approach (5-step) | Focus Areas + Constraints | Output Format (verdict table) |
| explorer | Map project landscape | Approach (4-step) | Focus Areas + Constraints | Output Format (structure dump) |
| implementer | Execute specs into code | Approach (4-step) | Focus Areas + Constraints | Output Format (implementation summary) |
| researcher | Find best practices | Approach (4-step) | Focus Areas + Constraints | Output Format (findings synthesis) |
| verifier | Confirm correctness | Approach (4-step) | Focus Areas + Constraints | Output Format (compliance table) |

## Why RACE

RACE ensures every spawn prompt answers four questions:
1. **Role** — Who is this?
2. **Action** — What do they do?
3. **Context** — What do they operate within?
4. **Expectation** — What does success look like?

When writing a new agent, audit the spawn prompt against these four fields. If one is missing or vague, the agent will behave inconsistently.

## Anti-Patterns

- **Role ambiguity** — "helps with tasks" instead of a specific specialization
- **Action without sequence** — "think about it carefully" instead of explicit steps
- **Context leakage** — omitting constraints leads to out-of-scope work
- **Expectation mismatch** — no output format means no quality bar

## Agent Spawn Prompt Template

```markdown
## Role
[Who this agent is — specialization + domain]

## Approach
1. [step]
2. [step]
3. [step]

## Focus Areas
- [area 1]
- [area 2]

## Output Format
[Structured format template]

## Constraints
- [rule 1]
- [rule 2]
```