# Orchestration Patterns for Multi-Agent Systems

## Sections
- [Pattern Catalog](#pattern-catalog)
- [Sonnet + Haiku Orchestration](#sonnet--haiku-orchestration)
- [Hybrid Approaches](#hybrid-approaches)
- [Implementation Guidance](#implementation-guidance)
- [Anti-Patterns](#anti-patterns)
- [Best Practices](#best-practices)
- [Pattern Selection](#pattern-selection)

---

Orchestration defines how multiple subagents coordinate to complete complex tasks.

**Single agent:** Sequential execution within one context.
**Multi-agent:** Coordination between multiple specialized agents, each with focused expertise.

---

## Pattern Catalog

### Sequential Pattern

Agents chained in predefined, linear order.

**Characteristics:**
- Each agent processes output from previous agent
- Pipeline of specialized transformations
- Deterministic flow (A → B → C)
- Easy to reason about and debug

**Ideal for:**
- Document review workflows (security → performance → style)
- Data processing pipelines (extract → transform → validate → load)
- Multi-stage reasoning (research → analyze → synthesize → recommend)

**Example:**
```
Task: Comprehensive code review

Flow:
1. security-reviewer: Check for vulnerabilities
   ↓ (security report)
2. performance-analyzer: Identify performance issues
   ↓ (performance report)
3. test-coverage-checker: Assess test coverage
   ↓ (coverage report)
4. report-synthesizer: Combine all findings into actionable review
```

**Implementation:**
```
Main chat orchestrates:
1. Launch security-reviewer with code changes
2. Wait for security report
3. Launch performance-analyzer with code changes + security report context
4. Wait for performance report
5. Launch test-coverage-checker with code changes
6. Wait for coverage report
7. Synthesize all reports for user
```

**Benefits:** Clear dependencies, each stage builds on previous.
**Drawbacks:** Slower than parallel (sequential latency), one failure blocks pipeline.

---

### Parallel Pattern

Multiple specialized subagents perform tasks simultaneously.

**Characteristics:**
- Agents execute independently and concurrently
- Outputs synthesized for final response
- Significant speed improvements
- Requires synchronization

**Ideal for:**
- Independent analyses of same input (security + performance + quality)
- Processing multiple independent items (review multiple files)
- Research tasks (gather information from multiple sources)

**Example:**
```
Task: Comprehensive code review (parallel approach)

Launch simultaneously:
- security-reviewer (analyzes auth.ts)
- performance-analyzer (analyzes auth.ts)
- test-coverage-checker (analyzes auth.ts test coverage)

Wait for all three to complete → synthesize findings.

Time: max(agent_1, agent_2, agent_3) vs sequential: agent_1 + agent_2 + agent_3
```

**Benefits:** Massive speed improvement, efficient resource utilization.
**Drawbacks:** Increased complexity, synchronization challenges, higher cost (multiple agents running).

---

### Hierarchical Pattern

Agents organized in layers, higher-level agents oversee lower-level.

**Characteristics:**
- Tree-like structure with delegation
- Higher-level agents break down tasks
- Lower-level agents execute specific subtasks
- Master-worker relationships

**Ideal for:**
- Large, complex problems requiring decomposition
- Tasks with natural hierarchy (system design → component design → implementation)
- Situations requiring oversight and quality control

**Example:**
```
Task: Implement complete authentication system

Hierarchy:
- architect (top-level): Designs overall auth system, breaks into components
  ↓ delegates to:
  - backend-dev: Implements API endpoints
  - frontend-dev: Implements login UI
  - security-reviewer: Reviews both for vulnerabilities
  - test-writer: Creates integration tests
  ↑ reports back to:
- architect: Integrates components, ensures coherence
```

**Benefits:** Handles complexity through decomposition, clear responsibility boundaries.
**Drawbacks:** Overhead in coordination, risk of misalignment between levels.

---

### Coordinator Pattern

Central LLM agent routes tasks to specialized sub-agents.

**Characteristics:**
- Central decision-maker
- Dynamic routing (not hardcoded workflow)
- AI model orchestrates based on task characteristics
- Similar to hierarchical but focused on process flow

**Ideal for:**
- Diverse task types requiring different expertise
- Dynamic workflows where next step depends on results
- User-facing systems with varied requests

**Example:**
```
Task: "Help me improve my codebase"

Coordinator analyzes request → determines relevant agents:
- code-quality-analyzer: Assess overall code quality
  ↓ findings suggest security issues
- Coordinator: Route to security-reviewer
  ↓ security issues found
- Coordinator: Route to auto-fixer to generate patches
  ↓ patches ready
- Coordinator: Route to test-writer to create tests for fixes
  ↓
- Coordinator: Synthesize all work into improvement plan
```

**Dynamic routing** based on intermediate results, not predefined flow.

**Benefits:** Flexible, adaptive to task requirements, efficient agent utilization.
**Drawbacks:** Coordinator is single point of failure, complexity in routing logic.

---

### Orchestrator-Worker Pattern

Central orchestrator assigns tasks, manages execution.

**Characteristics:**
- Centralized coordination with distributed execution
- Workers focus on specific, independent tasks
- Similar to distributed computing master-worker pattern
- Clear separation of planning (orchestrator) and execution (workers)

**Ideal for:**
- Batch processing (process 100 files)
- Independent tasks that can be distributed (analyze multiple API endpoints)
- Load balancing across workers

**Example:**
```
Task: Security review of 50 microservices

Orchestrator:
1. Identifies all 50 services
2. Breaks into batches of 5
3. Assigns batches to worker agents
4. Monitors progress
5. Aggregates results

Workers (5 concurrent instances of security-reviewer):
- Each reviews assigned services
- Reports findings to orchestrator
- Independent execution (no inter-worker communication)
```

**WARNING — Supervisor bottleneck:** The orchestrator pattern is susceptible to the supervisor bottleneck problem. Supervisor context grows non-linearly with worker count. At 5+ workers, the supervisor spends more tokens processing summaries than workers spend on actual tasks.

**HARD CAP: 3-5 workers per supervisor.** When you need more workers, add a second-tier supervisor rather than overloading one. See `{baseDir}/references/gotchas.md` for full explanation.

---

### Swarm Pattern (Peer-to-Peer)

Remove central control. Agents communicate directly based on predefined protocols.

**Characteristics:**
- No central coordinator or supervisor
- Any agent can transfer control to any other through explicit handoff
- Dynamic routing based on task requirements
- No single point of failure

**Ideal for:**
- Tasks requiring flexible exploration
- Dynamic requirements that defy upfront decomposition
- Systems where any agent might be best suited for next step

**The Handoff Protocol:**
```python
def handle_customer_request(request):
    if request.type == "billing":
        return billing_agent  # Direct handoff, no supervisor intermediary
    elif request.type == "technical":
        return technical_agent
    elif request.type == "sales":
        return sales_agent
    else:
        return general_agent
```

**vs. Supervisor Pattern:**

| Aspect | Supervisor | Swarm |
|--------|------------|-------|
| Control | Centralized | Distributed |
| Bottleneck risk | High (supervisor context) | Low (no central point) |
| Coordination overhead | High (supervisor routes all) | Low (direct handoff) |
| Failure mode | Single point of failure | No single point of failure |
| Best for | Well-defined workflows | Exploratory/dynamic tasks |

**Anti-pattern alert:** Swarm only works when handoff protocols are explicit and well-defined. Without clear protocols, agents drift. The swarm pattern requires more upfront design than supervisor.

---

### The forward_message Pattern (Telephone Game Mitigation)

**The problem:** Information degrades through repeated summarization as it passes between agents. LangGraph benchmarks show supervisor architectures initially perform ~50% worse than optimized versions due to paraphrase degradation.

**The mechanism:** Subagents pass responses directly to users, bypassing supervisor synthesis.

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

**When to use forward_message:**
- Subagent response is final and complete
- Supervisor synthesis would lose important details
- Response format must be preserved exactly
- Subagent has unique expertise that should be preserved in output

**Implementation:** Use shared scratchpads (`.principled/scratch/multi-agent-state.md`) instead of message-passing. Agents write findings, next agent reads directly. No supervisor summarization in between.

**See:** `{baseDir}/references/gotchas.md` — The Telephone Game gotcha for full explanation.

---

## Sonnet + Haiku Orchestration

**Optimal cost/performance pattern:**

1. **Sonnet** (Orchestrator):
   - Analyzes task, creates plan
   - Breaks into subtasks, identifies what can be parallelized

2. **Haiku** (Workers):
   - Each completes assigned subtask
   - Executes in parallel for speed
   - Returns results to orchestrator

3. **Sonnet** (Orchestrator):
   - Integrates results from all workers
   - Validates output quality
   - Ensures coherence

**Cost/performance optimization:** Use Sonnet for planning/validation, Haiku for execution.

---

## Hybrid Approaches

Real-world systems often combine patterns for different workflow phases.

### Sequential Then Parallel

**Sequential for initial processing → Parallel for analysis:**

```
Task: Comprehensive feature implementation review

Sequential phase:
1. requirements-validator: Check requirements completeness
   ↓
2. implementation-reviewer: Verify feature implemented correctly
   ↓

Parallel phase (once implementation validated):
3. Launch simultaneously:
   - security-reviewer
   - performance-analyzer
   - accessibility-checker
   - test-coverage-validator
   ↓

Sequential synthesis:
4. report-generator: Combine all findings
```

**Rationale:** Early stages have dependencies (can't validate implementation before requirements), later stages are independent analyses.

### Coordinator With Hierarchy

**Coordinator orchestrating hierarchical teams:**

```
Top level: Coordinator receives "Build payment system"

Coordinator creates hierarchical teams:

Team 1 (Backend):
- Lead: backend-architect
  - Workers: api-developer, database-designer, integration-specialist

Team 2 (Frontend):
- Lead: frontend-architect
  - Workers: ui-developer, state-management-specialist

Team 3 (DevOps):
- Lead: infra-architect
  - Workers: deployment-specialist, monitoring-specialist

Coordinator:
- Manages team coordination
- Resolves inter-team dependencies
- Integrates deliverables
```

**Benefit:** Combines dynamic routing (coordinator) with team structure (hierarchy).

---

## Implementation Guidance

### Synchronization

**Handling parallel execution:**

1. Initiate all parallel agents with shared context
2. Track which agents have completed
3. Collect outputs as they arrive
4. Wait for all to complete OR timeout
5. Proceed with available results (flag missing if timeout)

**Partial failure handling:**
- If 1 of 3 agents fails: Proceed with 2 results, note gap
- If 2 of 3 agents fail: Consider retry or workflow failure
- Always communicate what was completed vs attempted

---

## Anti-Patterns

### Over-Orchestration

❌ Using multiple agents when single agent would suffice

**Example:** Three agents to review 10 lines of code (overkill).

**Fix:** Reserve multi-agent for genuinely complex tasks. Single capable agent often better than coordinating multiple simple agents.

**Warning:** See gotchas.md — Over-decomposition. If a subagent's task can be described in one sentence, it's probably too narrow. Each handoff is an opportunity for context loss.

### No Coordination

❌ Launching multiple agents with no coordination or synthesis

**Problem:** User gets conflicting reports, no coherent output, unclear which to trust.

**Fix:** Always synthesize multi-agent outputs into coherent final result.

**Warning:** See gotchas.md — Missing shared state. Agents without shared scratchpads duplicate work and produce inconsistent outputs.

### Sequential When Parallel

❌ Running independent analyses sequentially

**Example:** Security review → performance review → quality review (each independent, done sequentially).

**Fix:** Parallel execution for independent tasks. 3x speed improvement in this case.

### Unclear Handoffs

❌ Agent outputs that don't provide sufficient context for next agent

**Problem:**
```
Agent 1: "Found issues"
Agent 2: Receives "Found issues" with no details on what, where, or severity
Agent 2: Can't effectively act on vague input
```

**Fix:** Structured handoff format with complete context.

**Warning:** See gotchas.md — Telephone game. Information degrades through paraphrasing. Use shared scratchpads, not message-passing.

### No Error Recovery

❌ Orchestration with no fallback when agent fails

**Problem:** One agent failure causes entire workflow failure.

**Fix:** Graceful degradation, retry logic, alternative agents, partial results. See `{baseDir}/references/fault-tolerance.md`.

**Warning:** See gotchas.md — Error propagation cascades. One agent's hallucination becomes another's fact. Add verification checkpoints.

### Agent Sprawl

❌ Adding more agents "for parallelism" without context isolation benefit

**Problem:** Each additional agent adds communication channels quadratically. At 10 agents, 45 potential coordination points.

**Fix:** Start with minimum viable number (3-5). Add only when clear context isolation benefit exists.

**Warning:** See gotchas.md — Agent sprawl. Diminishing returns past 3-5 agents, coordination overhead grows quadratically.

### Supervisor Bottleneck

❌ Routing 6+ workers through single supervisor

**Problem:** Supervisor context grows non-linearly with worker count. At 5+ workers, supervisor spends more tokens processing summaries than workers spend on actual tasks.

**Fix:** Hard cap at 3-5 workers per supervisor. Add second-tier supervisor for more workers.

**Warning:** See gotchas.md — Supervisor bottleneck. This is the #1 reason multi-agent systems degrade. It happens to every team that doesn't cap workers.

### Sycophantic Consensus

❌ Accepting "everyone agrees" as correctness signal

**Problem:** LLM bias toward agreement. Multi-agent discussions converge on agreeable answers, not correct ones.

**Fix:** Weighted voting by confidence × expertise. Assign adversarial roles requiring explicit disagreement before convergence.

**Warning:** See gotchas.md — Sycophantic consensus. Quick agreement is a sycophancy signal, not a reliability signal.

---

## Best Practices

### Right Granularity

**Agent granularity:** Not too broad, not too narrow.

Too broad: "general-purpose-helper" (defeats purpose of specialization)
Too narrow: "checks-for-sql-injection-in-nodejs-express-apps-only" (too specific)
Right: "security-reviewer specializing in web application vulnerabilities"

### Clear Responsibilities

**Each agent should have clear, non-overlapping responsibility.**

Bad: Two agents both "review code for quality" (overlap, confusion)
Good: "security-reviewer" + "performance-analyzer" (distinct concerns)

### Minimize Handoffs

**Minimize information loss at boundaries.**

Each handoff is opportunity for context loss. Structured handoff formats prevent this.

### Parallelize Where Possible

**If agents don't depend on each other's outputs, run them concurrently.**

### Coordinator Lightweight

**Keep coordinator logic lightweight.**

Heavy coordinator = bottleneck. Coordinator should route and synthesize, not do deep work itself.

### Cost Optimization

**Use model tiers strategically.**

- Planning/validation: Sonnet 4.5 (needs intelligence)
- Execution of clear tasks: Haiku 4.5 (fast, cheap, still capable)
- Highest stakes decisions: Sonnet 4.5
- Bulk processing: Haiku 4.5

---

## Pattern Selection

### Decision Tree

```
Is task decomposable into independent subtasks?
├─ Yes: Parallel pattern (fastest)
└─ No: ↓

Do subtasks depend on each other's outputs?
├─ Yes: Sequential pattern (clear dependencies)
└─ No: ↓

Is task large/complex requiring decomposition AND oversight?
├─ Yes: Hierarchical pattern (structured delegation)
└─ No: ↓

Do task requirements vary dynamically?
├─ Yes: Coordinator pattern (adaptive routing)
└─ No: Single agent sufficient
```

### Performance vs Complexity

| Pattern | Performance | Complexity | Flexibility |
|---------|-------------|------------|-------------|
| Parallel | Highest | Medium | Low |
| Hierarchical | High | High | Medium |
| Sequential | Medium | Low | Low |
| Coordinator | Lowest | Highest | Highest |

**Trade-off:** Choose simplest pattern that meets requirements.