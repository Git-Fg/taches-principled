# Multi-Agent Gotchas: Lessons from Production Deployments

Multi-agent systems fail in predictable ways. These eight gotchas account for the majority of production failures. A practitioner can scan this in 2 minutes.

---

## The Eight Critical Gotchas

| # | Gotcha | Key Threshold | Prevention |
|---|--------|---------------|------------|
| 1 | Supervisor bottleneck | 3-5 workers/supervisor | Second-tier supervisors |
| 2 | Token cost underestimation | 15x baseline single-agent | Treat 15x as normal |
| 3 | Sycophantic consensus | Weighted voting | Adversarial roles |
| 4 | Agent sprawl | 3-5 agents minimum viable | Start minimal |
| 5 | Telephone game | Direct response | forward_message or shared files |
| 6 | Error propagation | Circuit breaker | Verification checkpoints |
| 7 | Over-decomposition | 2-4 tool ops/agent | Meaningful task scope |
| 8 | Missing shared state | Scratchpad | Shared persistent storage |

---

## 1. Supervisor Bottleneck

**Insight:** Supervisor context grows non-linearly with worker count. At 5+ workers, the supervisor spends more tokens on processing summaries than workers spend on actual tasks.

**Example:** 10 workers sending summaries to one supervisor saturates ~4,000+ tokens just in summaries before tool calls.

**Threshold:** Hard cap at **3-5 workers per supervisor**. Add second-tier supervisors instead.

---

## 2. Token Cost Underestimation

**Insight:** Teams budget 3x but actual is ~15x due to coordination overhead, retries, and consensus rounds being invisible in estimates.

**Example:** "3 agents at 1000 tokens = 3000 tokens" vs reality ~7,200 tokens when you factor spawn prompts, summarization, retries, and synthesis.

**Threshold:** Budget for **15x baseline**. Treat anything less as a bonus.

---

## 3. Sycophantic Consensus

**Insight:** LLMs bias toward agreement. Without intervention, multi-agent discussions converge on false premises because agents want to be helpful, not correct.

**Example:** Agent A proposes X → Agent B agrees weakly (hallucinating) → Agent C sees A+B converging → group commits to wrong X.

**Threshold:** Assign adversarial roles; require explicit disagreement before convergence.

---

## 4. Agent Sprawl

**Insight:** Communication channels grow quadratically (n×(n-1)/2). At 10 agents, 45 potential coordination points — each new agent adds more overhead than value.

**Example:** Team adds 8 researchers to analyze 50 APIs faster. Reality: supervisor spends 40% of tokens on coordination, 60% on work. Worse than 3 focused agents.

**Threshold:** Start with **minimum viable number**. More agents only when context isolation benefit is clear and worker cap hasn't been reached.

---

## 5. Telephone Game

**Insight:** Information degrades through repeated summarization. Each agent paraphrasing loses nuance — by final output, 70-80% information loss is typical.

**Example:** "SQL injection in line 127 of auth.ts — user input not sanitized" → "SQL injection in auth.ts" → "Security issue found" → "There was a security issue" (exact vulnerability: gone).

**Threshold:** Use **forward_message** for final complete outputs; shared scratchpad for state multiple agents need to access faithfully. Direct response bypasses supervisor synthesis.

---

## 6. Error Propagation Cascades

**Insight:** One hallucination compounds — downstream agents have no way to distinguish upstream errors from facts. Small errors early become increasingly wrong results downstream.

**Example:** Worker 1 hallucinates "/users/v2/auth" endpoint → Worker 2 trusts and checks it → Worker 3 finds "token timing issue" → Final report: "Critical vulnerability in /users/v2/auth" (endpoint was /auth/login all along).

**Threshold:** Never trust upstream output without verification. Add validation checkpoints between agents for critical outputs; implement circuit breakers.

---

## 7. Over-Decomposition

**Insight:** Fine-grained splitting creates more coordination overhead than the task itself. A 10-step pipeline spends more tokens on handoffs than actual work.

**Example:** 10 agents each doing one micro-task (read file, find function, analyze function, etc.) = ~3,000 coordination tokens, ~2,000 actual work tokens. Net loss vs. 3 agents with coherent scopes (~500 coordination, ~4,500 work).

**Threshold:** If a task can be described in one sentence, it's too narrow. Decompose until tasks are **2-4 tool-using operations minimum**.

---

## 8. Missing Shared State

**Insight:** Without shared persistent storage, agents duplicate work, produce inconsistent outputs, and make contradictory decisions without knowing it.

**Example:** Three agents independently researching "authentication docs" — all three do the same research, 3x time, 3x tokens, same output. Or worse: Agent 1 decides approach X, Agent 2 decides approach Y → contradictory final recommendations.

**Threshold:** Establish shared persistent storage **before** building workflows. Use `.principled/scratch/multi-agent-state.md` or CheckpointManager.