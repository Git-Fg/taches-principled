# When `context: fork` earns its isolation cost

`context: fork` is the Claude Code mechanism that runs a skill in an isolated subagent instead of inline in the main conversation. The forked subagent has no access to your main conversation history and returns only the useful result to you.

## When fork is the right choice

Use `context: fork` when the skill:

- **Reads many files** to synthesize an answer (a "map" operation that would flood the main conversation)
- **Performs exploratory reasoning** the main agent should not see in full (multi-step analysis, hypothesis iteration, debate rounds)
- **Produces a clean final artifact** the main conversation can use directly (a report, a verdict, a transformed file)
- **Performs long multi-step reasoning** that consumes many tokens of intermediate exploration (planning a project, evaluating hypotheses, competitive generation)

The 4 fork skills in the taches-principled marketplace all match this pattern:

| Skill | Why fork |
|---|---|
| `plan-lifecycle` | Multi-phase planning reads every referenced file in the plan; returns a structured execution report |
| `sadd` | Multi-judge debate runs N rubric evaluations in isolated contexts; returns the chosen candidate |
| `task-lifecycle` | The 4-stage task lifecycle (CAPTURE → REFINE → IMPLEMENT → DOCUMENT) produces verbose intermediate output for each stage |
| `fpf` | Hypothesis generation, evidence validation, trust auditing — each stage iterates over prior stage's output |

## When fork is the wrong choice

Do NOT use `context: fork` when:

- The skill is a one-line lookup (the fork overhead exceeds the work)
- The user needs the skill's intermediate work visible (debugging, transparency)
- The skill's value IS in-context application (a style guide the main agent must read while writing)
- The fork's spawn overhead exceeds the context savings

## What changed in 1.23.0

Before 1.23.0, fork skills were designed around *parallel worker subagents*: `plan-lifecycle` would spawn N parallel `tp-global-implementer` workers, `sadd` would spawn 3 parallel `sadd-generator` instances.

After 1.23.0, **fork skills implement inline within the fork** and spawn only `tp-critic` for isolated review. The parallelism that mattered most (multiple judges scoring one candidate from different angles) is preserved; the parallelism that didn't matter (N implementations of the same code) was removed.

The fork's isolation value remains: the user's session is shielded from the multi-step reasoning. The fork is no longer for inner parallelism; it's for **outer isolation around long reasoning.**

## What this file must contain

A `references/fork-rationale.md` should answer:

1. **What isolation value does this fork provide?** (What would leak into the user's session if the work ran inline?)
2. **Why does the work need a fresh context?** (What state does the orchestrator's accumulated bias pollute?)
3. **What does the fork preserve from the parent?** (Files? Plan? Task spec?)
4. **What does the fork NOT inherit?** (The user's conversational history, prior skills loaded, etc.)

Example skeleton:

```markdown
# Why this fork

**Isolation value:** <one sentence on what would pollute the main conversation if inline>

**What the fork inherits:**
- <files or state from the parent>

**What the fork does NOT inherit:**
- The user's earlier conversation history
- The parent's loaded skills (the fork gets only what its frontmatter preloads)

**Post-fork return:** <what the parent receives — usually a structured report or verdict>
```

A reviewer auditing this skill should be able to confirm the fork flag is justified without re-reading the parent skill body.