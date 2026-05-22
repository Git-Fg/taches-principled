# Multi-Agent Gotchas: Lessons from Production Deployments

## Sections
- [The Eight Critical Gotchas](#the-eight-critical-gotchas)
- [Supervisor Bottleneck Scaling](#supervisor-bottleneck-scaling)
- [Token Cost Underestimation](#token-cost-underestimation)
- [Sycophantic Consensus](#sycophantic-consensus)
- [Agent Sprawl](#agent-sprawl)
- [Telephone Game in Message-Passing](#telephone-game-in-message-passing)
- [Error Propagation Cascades](#error-propagation-cascades)
- [Over-Decomposition](#over-decomposition)
- [Missing Shared State](#missing-shared-state)

---

These gotchas are the hard-won lessons from production multi-agent systems. They are the mistakes that cause multi-agent architectures to fail in ways single-agent systems never would. Learn them by heart.

---

## The Eight Critical Gotchas

Multi-agent systems fail in predictable ways. These eight gotchas account for the majority of production failures:

| # | Gotcha | Symptom | Root Cause |
|---|--------|---------|-----------|
| 1 | Supervisor bottleneck | Context saturates at 5+ workers | Non-linear context growth |
| 2 | Token cost underestimation | Budget 3x, actual 15x | Coordination overhead invisible |
| 3 | Sycophantic consensus | Agents agree, answers are wrong | LLM bias toward agreement |
| 4 | Agent sprawl | Diminishing returns at 6+ agents | Quadratic communication channels |
| 5 | Telephone game | Information degrades through paraphrasing | Each agent summarizes loses nuance |
| 6 | Error propagation cascades | One hallucination compounds | Downstream agents trust upstream |
| 7 | Over-decomposition | 10-step pipeline, more tokens on handoffs than work | Fine-grained splitting is anti-pattern |
| 8 | Missing shared state | Duplicate work, inconsistent outputs | No persistent coordination layer |

---

## Supervisor Bottleneck Scaling

**The problem:** Supervisor context pressure grows non-linearly with worker count. At 5+ workers, the supervisor spends more tokens processing summaries than workers spend on actual tasks.

**The math:** Each worker sends back a summary. The supervisor must process all of them before synthesizing. At 3 workers: 3 summaries. At 5 workers: 5 summaries. At 10 workers: supervisor is drowning while workers idle.

**BEFORE: 10 workers reporting to one supervisor**

```
Supervisor context at hour 3:
- Worker 1 summary: 200 tokens
- Worker 2 summary: 180 tokens
- Worker 3 summary: 220 tokens
- Worker 4 summary: 190 tokens
- Worker 5 summary: 210 tokens
- Worker 6 summary: 175 tokens
- Worker 7 summary: 205 tokens
- Worker 8 summary: 195 tokens
- Worker 9 summary: 185 tokens
- Worker 10 summary: 215 tokens
= ~2,000 tokens just in summaries
Plus supervisor's own reasoning: ~1,500 tokens
Plus task state: ~500 tokens
Total supervisor context: 4,000+ tokens (before tool calls)
```

**AFTER: 3-5 worker cap with second-tier supervisors**

```
Layer 1:
- Supervisor A manages workers 1-5
- Supervisor B manages workers 6-10

Layer 2:
- Orchestrator coordinates Supervisor A and B
- Each supervisor distills its 5 summaries into 1 summary
- Orchestrator processes 2 summaries, not 10
```

**The rule:** Hard cap at **3-5 workers per supervisor**. When you need more workers, add a second-tier supervisor rather than overloading one.

**If you ignore this:** The supervisor enters "completion mode" — rushing through synthesis, dropping details, producing degraded output that passes as complete but isn't.

---

## Token Cost Underestimation

**The problem:** Teams consistently underbudget because they estimate per-agent costs without accounting for coordination overhead, retries, and consensus rounds. Multi-agent runs cost approximately **15x baseline**, not 3x or 5x.

**The breakdown:**

| Component | Token Multiplier |
|-----------|------------------|
| Single agent chat | 1x baseline |
| Single agent with tools | ~4x baseline |
| Multi-agent system | ~15x baseline |

**Why the gap:**

1. **Coordination overhead**: Each handoff is a prompt injection. Each aggregation is a summary pass.
2. **Consensus rounds**: Debate protocols require multiple passes. Each round multiplies token cost.
3. **Retry loops**: Failed agents require retry prompts. Each retry adds another full prompt cycle.
4. **Context passing**: Workers pass state summaries. Supervisors pass aggregated summaries. Each pass costs tokens.
5. **Verification**: Output validation before passing downstream. Not free.

**BEFORE: "3 agents, each 1000 tokens = 3000 tokens"**

**Reality:**
- Spawn prompts: 500 tokens × 3 = 1,500
- Worker outputs (3 × 800 tokens summarized): 2,400
- Supervisor processing + aggregation: 1,200
- Retry round (1 agent failed): +1,500
- Final synthesis: 600
- **Total: ~7,200 tokens** — not 3,000

**The rule:** Budget for **15x baseline**. Treat anything less as a bonus. If cost is a constraint, question whether multi-agent is actually needed.

**The BrowseComp finding:** 95% of performance variance explained by three factors: token usage (80% of variance), number of tool calls, and model choice. More tokens almost always wins over more agents.

---

## Sycophantic Consensus

**The problem:** Agents in debate patterns tend to converge on agreeable answers, not correct ones. LLMs have an inherent bias toward agreement. Without intervention, multi-agent discussions devolve into consensus on false premises.

**The mechanism:**
1. Agent A proposes X
2. Agent B has doubts but wants to be helpful — says "X has merit"
3. Agent C sees A and B converging — "X seems reasonable"
4. Agent A, reinforced by agreement, commits to X harder
5. The group converges on X, which is wrong

**The signal:** Discussion that terminates too quickly. "Everyone agrees" is not a reliability signal — it's a sycophancy signal.

**BEFORE: Simple majority voting**

```
Agent A: "Option 1 is best" (confidence: 0.7)
Agent B: "Option 1 is best" (confidence: 0.4)  ← weak model, hallucinating
Agent C: "Option 2 is best" (confidence: 0.9)
Result: Option 1 wins 2-1
Reality: Option 2 is correct, Agent B was wrong
```

**AFTER: Weighted voting + adversarial roles**

```
Round 1:
- Agent A: "Option 1" (confidence: 0.7)
- Agent B: "Option 1" (confidence: 0.4)
- Agent C: "Option 2" (confidence: 0.9)

Round 2 (adversarial challenge):
- Agent C challenges: "Why does Agent B support Option 1?"
- Agent B must justify — can't, was guessing
- Agent C's weight increases; Agent B's decreases

Final weighted consensus:
- Option 1: (0.7 × A_weight) + (0.4 × B_weight) = lower score
- Option 2: (0.9 × C_weight) = higher score
Result: Option 2 wins
```

**The rule:** Assign explicit adversarial roles. Require agents to state disagreements before convergence is allowed. Weight by confidence × domain expertise, not simple vote count.

**Countermeasures:**
- Structured debate: agents must critique others' outputs
- Convergence gates: don't allow consensus until explicit disagreement phase complete
- Confidence weighting: higher confidence = higher vote weight
- Domain expertise weighting: specialized agents carry more weight in their domain

---

## Agent Sprawl

**The problem:** Adding more agents past 3-5 shows diminishing returns. Each additional agent adds communication channels quadratically.

**The math:**

| Agents | Communication Channels | Relative Overhead |
|--------|------------------------|-------------------|
| 2 | 1 | 1x |
| 3 | 3 | 3x |
| 4 | 6 | 6x |
| 5 | 10 | 10x |
| 6 | 15 | 15x |
| 10 | 45 | 45x |

Every new agent must coordinate with every existing agent. At 10 agents, 45 potential coordination points — and that's before accounting for actual message passing.

**BEFORE: "More agents = more parallel work = faster"**

```
Team adds 8 more "researcher" agents to analyze 50 APIs faster.
Reality: 10 agents × 10 agents = 100 potential coordination points.
Supervisor spends 40% of tokens on coordination, 60% on actual work.
Worse than 3 agents with clear scope.
```

**AFTER: Minimum viable number of agents**

```
Task: Analyze 50 APIs for security issues
Approach 1 (sprawl): 10 researchers → coordination overhead kills speed
Approach 2 (minimal): 1 orchestrator + 5 researchers → clear handoffs
Approach 3 (if 50 is too many): Batch into 10 APIs × 5 agents, sequential batches
```

**The rule:** Start with the **minimum viable number of agents**. Add only when a clear context isolation benefit exists. If you're adding agents because "we have idle capacity," you're adding coordination debt.

**When more agents actually helps:**
- Context isolation benefit is clear (e.g., different tool sets required)
- Task is embarrassingly parallel (no inter-agent dependencies)
- Worker cap hasn't been reached (3-5 max)
- Shared state mechanism exists

---

## Telephone Game in Message-Passing

**The problem:** Information degrades through repeated summarization as it passes between agents. Each agent paraphrases and loses nuance. This is the "telephone game" problem — by the time information reaches the final agent, it's been transformed multiple times, often incorrectly.

**LangGraph benchmarks:** Supervisor architectures initially perform approximately **50% worse** than optimized versions due to the telephone game problem.

**The mechanism:**
```
Agent A: "Found SQL injection in line 127 of auth.ts — user input not sanitized"
Agent B summarizes for supervisor: "Found SQL injection in auth.ts"
Supervisor summarizes for synthesis: "Security issue found"
Final output: "There was a security issue"
```
What was the exact vulnerability? Gone. What was the fix? Not passed through. The detail degrades with each pass.

**BEFORE: Message-passing through multiple agents**

```
User Query → Supervisor → Worker 1 → Worker 2 → Worker 3 → Aggregation → User
           Each arrow: ~30% information loss
           Total: ~70-80% information loss by final output
```

**AFTER: Direct handoff or shared filesystem**

```
Option A: forward_message tool — subagent responds directly to user
Option B: Shared scratchpad — agents write findings, next agent reads
Option C: Single supervisor — no intermediate workers
```

**The rule:** Use filesystem coordination (shared scratchpads) instead of message-passing for state that multiple agents need to access faithfully. When subagent output is final and complete, bypass supervisor synthesis with a direct response mechanism.

**The forward_message pattern:**
```markdown
<workflow>
1. Worker completes analysis
2. If output is final and complete:
   - Write findings to shared scratchpad
   - Use forward_message to respond directly to user
   - Supervisor synthesis not needed
3. If output feeds into next stage:
   - Write to shared scratchpad
   - Next agent reads scratchpad directly
   - Supervisor does not summarize and re-pass
</workflow>
```

---

## Error Propagation Cascades

**The problem:** One agent's hallucination becomes another agent's "fact." Downstream agents have no way to distinguish upstream hallucinations from genuine information. A small error early compounds into increasingly wrong results downstream.

**The cascade:**
```
Worker 1 (hallucinates): "The API endpoint is at /users/v2/auth"
Worker 2 (trusts): "Checking /users/v2/auth for auth validation"
Worker 3 (trusts): "The /users/v2/auth endpoint has a token timing issue"
Final report: "Critical vulnerability in /users/v2/auth token timing"
Reality: The endpoint is /auth/login — Worker 1 was wrong about everything
```

Each agent trusts the previous agent's output. None verify independently. The hallucination propagates unchecked.

**BEFORE: No verification between agents**

```
Agent A → Agent B → Agent C → Final Output
   ↑          ↑          ↑
   No verification at any step
   Each assumes previous is correct
```

**AFTER: Verification checkpoints between agents**

```
Agent A → [VERIFY: Check A's output independently] → Agent B
                            ↓
                      Catch error here, before it propagates
```

**The rule:** Never trust upstream output without verification. Add validation checkpoints between agents for critical outputs. Implement retry logic with circuit breakers to prevent cascading failures.

**Circuit breaker pattern:**
```python
class AgentCircuitBreaker:
    def handle_failure(agent_id, task_id, error):
        failure_count[agent_id] += 1
        if failure_count > max_retries:
            # Open circuit — don't retry this agent
            # Route to alternative or fail fast
        else:
            # Retry with backoff
            delay = min(2 ** failure_count, 60)
```

**The principle:** Errors compound. Catch them early. Design for failure isolation.

---

## Over-Decomposition

**The problem:** Splitting tasks too finely creates more coordination overhead than the task itself. A 10-step pipeline with 10 agents spends more tokens on handoffs than on actual work.

**The signal:** "Each agent only does one thing" — when you hear this, you're likely over-decomposing. Each handoff is an opportunity for context loss, coordination overhead, and error propagation.

**BEFORE: 10 agents, each with one micro-task**

```
分解:
Agent 1: Read file A
Agent 2: Find function foo
Agent 3: Analyze function foo
Agent 4: Find called functions in foo
Agent 5: Read called functions
Agent 6: Analyze security implications
Agent 7: Write findings
Agent 8: Review findings
Agent 9: Format report
Agent 10: Final review

Coordination tokens: ~3,000
Actual work tokens: ~2,000
Net loss: -1,000 tokens of useful work
```

**AFTER: 3-5 agents with coherent scopes**

```
Consolidate to:
Agent 1: Read + analyze file A + identify foo + identify called functions
Agent 2: Security analysis of entire call chain
Agent 3: Write and format report

Coordination tokens: ~500
Actual work tokens: ~4,500
Net gain: +4,000 tokens of useful work
```

**The rule:** If a subagent's task can be described in one sentence, it's probably too narrow. Decompose until tasks are meaningful (2-4 tool-using operations minimum), not until no single step could fail.

**When decomposition is correct:**
- Tasks genuinely require different tool sets
- Tasks require different model capabilities (Haiku for simple, Sonnet for complex)
- Tasks can run in true parallel (no shared state conflicts)
- Context isolation benefit is clear (memory pressure would be high otherwise)

---

## Missing Shared State

**The problem:** Agents operating without a shared filesystem or state store duplicate work, produce inconsistent outputs, and lose track of what has already been accomplished.

**The failure mode:**
```
Agent 1 (researching API docs): "I'll check the authentication docs"
Agent 2 (researching API docs): "I'll check the authentication docs"
Agent 3 (researching API docs): "I'll check the authentication docs"

All three do the same research. No one knows the others are doing it.
Result: 3x the time, 3x the tokens, same output.
```

Or worse:
```
Agent 1: "I've decided the approach is X"
Agent 2: "I've decided the approach is Y"
They're solving the same problem differently.
Final output: Contradictory recommendations.
```

**BEFORE: No shared state mechanism**

```
Each agent is fully isolated.
No knowledge of what others have found.
No way to check for duplicates.
No shared record of decisions.
```

**AFTER: Shared scratchpad filesystem**

```
.principled/scratch/multi-agent-state.md:
# Research Progress
- [x] Authentication docs: Complete (Agent 1)
- [ ] Rate limiting docs: In progress (Agent 2)
- [ ] Payment API docs: Pending (Agent 3)

# Decisions
- Approach: OAuth 2.0 with refresh tokens (decided by Agent 1)

Agents check this file before starting work.
Duplicate work is prevented.
Decisions are visible to all.
```

**The rule:** Establish shared persistent storage **before** building multi-agent workflows. Use a scratchpad file (`.principled/scratch/multi-agent-state.md`) or CheckpointManager for workflow state that multiple agents must access.

**The FileSystemCoordination pattern:**
```python
# Before starting work, check shared state
state = read_shared_state()
if task_already_done(state, current_task):
    skip_task()
else:
    execute_task()
    update_shared_state(state, results)
```

**The minimum viable shared state:**
1. Task list with completion status
2. Key decisions made
3. Shared findings (if multiple agents research same topic)

---

## Quick Reference: The Eight Gotchas

| Gotcha | Cap | Metric | Prevention |
|--------|-----|--------|------------|
| Supervisor bottleneck | 3-5 workers/supervisor | Supervisor context | Second-tier supervisors |
| Token cost | 15x baseline | Budget | Treat 15x as normal |
| Sycophantic consensus | Weighted voting | Confidence × expertise | Adversarial roles |
| Agent sprawl | 3-5 agents minimum viable | Quadratic channels | Start minimal |
| Telephone game | Direct response | % information retained | forward_message or shared files |
| Error propagation | Circuit breaker | Cascade depth | Verification checkpoints |
| Over-decomposition | 2-4 tool ops/agent | Handoff overhead | Meaningful task scope |
| Missing shared state | Scratchpad or CheckpointManager | Duplicate work % | Shared persistent storage |