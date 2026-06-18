---
name: orchestration-contracts
description: Subagent spawning patterns, tool scoping, and output contracts. The #1 rule is the isolation-justifies-a-file test.
---

# Rule: Spawn a subagent only when its isolated context earns the cost; main agent implements inline by default

**Why:** Subagents don't shrink total spend — they move *where* the spend lands (the subagent pays once for its exploration in a disposable context; the parent stays lean). A named subagent definition earns its file only when the task it does burns large intermediate tokens AND returns a small summary AND the parent benefits from not carrying the journey. The marketplace ships 6 named agents — all the "specialized reviewer" roles collapse into `tp-critic` parameterized by a lens prompt.

## The isolation-justifies-a-file test

A spawn earns its cost when **all three** hold:

1. **High intermediate-token burn** (≥10k) — the task would otherwise flood the main conversation with file reads, search results, or reasoning.
2. **Small summary vs huge journey** — the subagent's return is much smaller than its exploration.
3. **Independence matters** — the work product benefits from being judged or explored in a context free of the orchestrator's accumulated biases.

Fail any one → fold into inline work in the main agent, or pass a one-shot spawn prompt at the call site without a dedicated agent file.

## The spawn-vs-inline decision matrix

| Signal | Spawn subagent | Stay inline |
|---|---|---|
| Intermediate tokens the task burns | High (10k+) | Low (<5k) |
| Files already in parent context | No | Yes |
| Result-to-journey ratio | Small summary vs huge journey | Result ≈ journey |
| Back-and-forth needed | No | Yes |
| Independent tasks | Yes | No (shared state) |

## The marketplace's 6 named subagents (the keepers)

| Agent | Role | When it earns its file |
|---|---|---|
| `tp-critic` | Universal isolated-context reviewer. Accepts a **lens** in the spawn prompt ("review through the lens of OWASP Top 10"). | Every adversarial judgment / verification / review need. The lens is one sentence, not a file. |
| `tp-explorer` | Universal isolated-context codebase mapper. Accepts a **scope** in the spawn prompt. | Every read-only codebase exploration that would burn many file reads. |
| `tp-researcher` | Universal isolated-context external researcher. Accepts a **question** in the spawn prompt. | Every web/doc traversal that would burn source-material tokens. |
| `mcp-quality-judge` | Domain-specialized isolated judge. Preloads `mcp-expertise` skill. | MCP server quality evaluation. The single domain exemplar of the lens/scope-prompt pattern. |
| `sadd-judge` | Candidate scoring against a rubric. | Competitive generation evaluation. |
| `wiki-searcher` | Read-only wiki query. `tools: [Read, Glob, Grep]` — the single allowed `tools:` restriction. | Wiki queries — read-only enforcement is load-bearing. |

All other "specialized" reviewers that previously existed (`tp-bug-hunter`, `security-reviewer`, `rust-cargo-reviewer`, etc.) collapse into `tp-critic` with a domain-specific lens prompt. Implementation agents collapse into inline work. Researcher/explorer clones collapse into `tp-explorer`/`tp-researcher` with a scope prompt.

## Rule

- **Agent definitions (`agents/*.md`) MUST NEVER contain spawn, fan-out, or delegation instructions.** The `Agent` tool is strictly removed from the subagent tool registry.
- **Orchestration belongs in skill bodies** with `context: fork` frontmatter, not in agent definitions.
- **Specialization belongs in lens prompts**, not in separate agent files. If you find yourself writing a new specialized reviewer, write a one-sentence lens for `tp-critic` instead.
- **Implementation belongs inline** unless the files are not in the orchestrator's context. Spawning an implementer that re-reads files the orchestrator already holds is a delegation tax, not a benefit.
- **Subagents CAN invoke skills** using the `Skill` tool (v2.1.133+). Subagent→Skill and Forked→Inline workflows are structurally supported.
- **Default to inline** for implementation and trivial work. Spawn for isolated-context review and large exploration.

## Anti-patterns

**Bad:** Agent body says "spawn an explorer subagent to investigate..." — runtime error.
**Good:** Skill body with `context: fork` spawns `tp-explorer` with scope "investigate X".

**Bad:** "If the task is complex, consider using subagents." — optional language.
**Good:** "Spawn `tp-critic` w/ lens Y for isolated review." — declarative.

**Bad:** Main agent spawns 6 specialized reviewers (`tp-bug-hunter`, `security-reviewer`, etc.) in parallel for a code review.
**Good:** Main agent spawns 6 `tp-critic` instances in parallel, each with a distinct lens ("logic errors and edge cases", "OWASP Top 10", etc.) — same isolation benefit, one definition instead of six.

**Bad:** Spawning an implementer to edit files the main agent is already working on.
**Good:** Implement inline; the files are already in context. Spawn `tp-critic` for isolated review.

**Bad:** Spawning a subagent to run a single `git status` or read one file.
**Good:** Run inline; the delegation overhead exceeds the work.

## Spawn Pattern (for skill bodies)

```markdown
## Execution Mode
**Default: inline.** Implement directly; spawn [role] subagents only when the review/exploration earns its isolation cost.

When spawning a subagent:
- Spawn `tp-critic` w/ lens "<specific review angle>" for adversarial judgment.
- Spawn `tp-explorer` w/ scope "<specific exploration question>" for read-only codebase mapping.
- Spawn `tp-researcher` w/ question "<specific external research question>" for web/doc traversal.
- Output: <what the subagent must return — bounded summary, not raw exploration>.

After subagent returns: synthesize, then optionally spawn another `tp-critic` w/ lens "<verify the synthesis against the spec>".
```

## Output discipline

Every spawned subagent must return a **bounded summary** — severity + file:line + one-line fix, not raw exploration. The subagent's internal exploration is disposable; what it returns is permanent in the parent. A 12k-token review of a 3k-token artifact is a delegation tax, not a benefit.