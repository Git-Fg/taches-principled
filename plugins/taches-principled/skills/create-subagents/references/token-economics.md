# Token Economics: The Real Cost of Multi-Agent Systems

## Sections
- [The Multiplier Reality](#the-multiplier-reality)
- [Token Cost Breakdown](#token-cost-breakdown)
- [The Budgeting Rule](#the-budgeting-rule)
- [When Multi-Agent Pays Off](#when-multi-agent-pays-off)
- [Model Selection vs Token Budget](#model-selection-vs-token-budget)
- [Measuring Efficiency](#measuring-efficiency)

---

Multi-agent systems cost approximately **15x more** than single-agent chat. Teams consistently underbudget because they estimate per-agent costs without accounting for coordination overhead, retries, and consensus rounds. This reference establishes the real economics.

---

## The Multiplier Reality

| Architecture | Token Multiplier | Why |
|--------------|------------------|-----|
| Single agent chat | 1x baseline | No coordination overhead |
| Single agent with tools | ~4x baseline | Tool calls, context for tool results |
| Two-agent simple | ~6x baseline | One handoff, basic coordination |
| Multi-agent system | ~15x baseline | Full coordination, consensus, retries |

**The gap explanation:**

```
Single agent (1x):
- User query: 100 tokens
- Model reasoning: 500 tokens
- Response: 200 tokens
Total: 800 tokens

Multi-agent (15x):
- Orchestrator prompt: 500 tokens
- Worker 1 spawn + execution: 800 tokens
- Worker 2 spawn + execution: 700 tokens
- Worker 3 spawn + execution: 750 tokens
- Handoff summaries: 300 tokens
- Aggregation: 400 tokens
- Retry round (1 worker failed): 800 tokens
Total: ~4,250 tokens (~15x)
```

**BrowseComp research finding:** 95% of performance variance in multi-agent systems is explained by three factors:
1. Token usage (80% of variance)
2. Number of tool calls
3. Model choice

More tokens almost always wins over fewer tokens. The implication: if you can't afford 15x tokens, you likely can't afford multi-agent architecture — and a single more capable model will outperform a multi-agent system running on a tight budget.

---

## Token Cost Breakdown

**Where the 15x goes:**

| Component | Tokens | Multiplier Contribution |
|-----------|--------|------------------------|
| Spawn prompts (3 workers) | 500 × 3 = 1,500 | 1.9x |
| Worker outputs (3 × 800 tokens each, summarized to 300) | 300 × 3 = 900 | 1.1x |
| Orchestrator processing | 1,200 | 1.5x |
| Aggregation/synthesis | 600 | 0.75x |
| Retry round (1 worker failed) | 1,200 | 1.5x |
| Verification checkpoints | 400 | 0.5x |
| **Total for simple workflow** | **5,800** | **~7x baseline** |

**Adding consensus (debate protocol):**

| Component | Additional Tokens |
|-----------|------------------|
| Round 2 debate | 1,500 |
| Round 3 adversarial | 1,500 |
| Convergence check | 300 |
| **Total with consensus** | **+3,300** |

**Full accounting with all overhead:** 7x baseline (simple) → 11x baseline (with consensus) → 15x baseline (worst case with retries and complex coordination)

**The rule:** The simpler the coordination, the closer to 7x. Complex consensus, deep hierarchies, and retry-heavy workflows approach 15x. Budget accordingly.

---

## The Budgeting Rule

**Rule:** Budget for **15x baseline token cost**. Treat anything less as a bonus.

**How to apply:**

1. **Estimate single-agent baseline:** What would this task cost with one capable agent?
2. **Multiply by 15:** This is your budget
3. **Track actual:** After execution, compare actual to budget
4. **Adjust:** If actual consistently exceeds 10x, the workflow needs optimization

**Budget template:**

```markdown
## Token Budget Estimate

Single-agent baseline estimate: X tokens
Multi-agent budget (15x): X × 15 = Y tokens

Breakdown:
- Spawn prompts: ~20%
- Worker execution: ~40%
- Coordination: ~25%
- Retry/resilience: ~15%

If Y is not acceptable:
- Simplify coordination (fewer agents, simpler patterns)
- Use smaller models for workers (Haiku vs Sonnet)
- Reduce consensus rounds
- Consider single-agent with longer context
```

**When budget exceeds acceptable:**
- Question whether multi-agent is actually required
- A single Sonnet agent with extended context often outperforms multi-agent Haiku
- Model quality × token budget = performance. Often better to spend tokens on one smarter model than spread across many

---

## When Multi-Agent Pays Off

**Multi-agent is justified when:**

| Condition | Single-Agent Alternative | Multi-Agent Advantage |
|-----------|------------------------|------------------------|
| **Context bottleneck** | Quality degrades past 50% context | Each agent operates in clean context |
| **Different tool sets** | One agent with all tools | Specialists with minimal tool sets |
| **Embarrassingly parallel** | Sequential processing | 3-5x speedup on independent tasks |
| **Domain specialization** | General knowledge | Expert-level knowledge per domain |
| **Cost trade-off** | Expensive model × long time | Cheap models × parallel execution |

**Multi-agent is NOT justified when:**
- Task is simple (single agent handles easily)
- Workers are homogeneous (no specialization)
- Tasks are tightly coupled (high handoff overhead negates parallelization)
- Budget is tight (15x multiplier not acceptable)

**The decision:**
```
Is task complex enough that context bottleneck is likely?
├─ Yes → Multi-agent justified
└─ No → Is task embarrassingly parallel with different tool needs?
         ├─ Yes → Multi-agent justified
         └─ No → Single agent sufficient
```

---

## Model Selection Vs Token Budget

**The key insight:** Better models often outperform raw token increases. Before adding agents, try a better model.

| Strategy | Token Cost | Performance Gain |
|----------|------------|-----------------|
| Single Haiku agent | 1x | Baseline |
| Single Sonnet agent | ~3x | Much higher reasoning quality |
| Single Opus agent | ~10x | Highest capability |
| 5 Haiku agents | ~5x | Parallel, but reasoning quality of Haiku |
| 3 Sonnet agents | ~9x | Parallel with Sonnet reasoning |

**The trade-off:**
- Single Opus: Maximum reasoning quality, sequential execution
- 3 Sonnet agents: Parallel, Sonnet reasoning, but coordination overhead

**When to add agents instead of upgrading model:**
1. Task has clear parallelizable subtasks with different tool sets
2. Context bottleneck is the limiting factor (not reasoning quality)
3. Speed matters (parallel execution faster than single sequential)
4. Different domains require different specializations

**The model selection heuristic:**
- **Sonnet for orchestration**: Planning, validation, synthesis
- **Haiku for execution**: Fast, simple tasks
- **Opus for critical decisions**: Highest-stakes reasoning

---

## Measuring Efficiency

**Multi-agent efficiency metric:** `(single_agent_tokens / multi_agent_tokens) × (single_agent_time / multi_agent_time)`

**Example:**

```
Single agent:
- Tokens: 800
- Time: 60 seconds

Multi-agent (3 workers):
- Tokens: 4,000
- Time: 15 seconds

Efficiency: (800/4000) × (60/15) = 0.2 × 4 = 0.8
```

At 0.8, multi-agent is slightly inefficient — 20% more resource-intensive per unit of work compared to single agent, but 4x faster. The trade-off depends on whether speed is valued.

**Efficiency > 1.0:** Multi-agent is more efficient (less resources per unit of work)
**Efficiency = 1.0:** Equivalent to single agent
**Efficiency < 1.0:** Multi-agent is less efficient, only justified for non-token reasons (speed, specialization)

**The practical test:**

```markdown
## Efficiency Check

1. Run task with single capable agent (baseline)
2. Run same task with multi-agent workflow
3. Compare:
   - Token cost ratio
   - Time improvement ratio
   - Output quality (is multi-agent output actually better?)

If multi-agent output is NOT meaningfully better:
   → Single agent wins. Multi-agent overhead not justified.
If multi-agent output IS better:
   → Quality improvement > cost increase? Use multi-agent.
```

---

## Key Principles

1. **Budget 15x** — Not 3x, not 5x. If you can't afford 15x, reconsider multi-agent.
2. **Measure actual cost** — Track tokens post-execution. Compare to estimate.
3. **Model quality often beats more agents** — A smarter single model outperforms many weak models.
4. **Speed vs cost trade-off** — Multi-agent is faster but costs more. Decide which matters.
5. **Efficiency < 1.0 is acceptable only with non-token benefits** — Specialization, context isolation, quality improvements that single-agent can't achieve.