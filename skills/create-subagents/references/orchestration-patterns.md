# Orchestration Patterns for Multi-Agent Systems

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

---

## Sonnet + Haiku Orchestration

**Optimal cost/performance pattern:**

Research findings:
- Sonnet 4.5: "Best model in the world for agents", exceptional at planning and validation
- Haiku 4.5: "90% of Sonnet 4.5 performance", one of best coding models, fast and cost-efficient

**Pattern:**
```
1. Sonnet 4.5 (Orchestrator):
   - Analyzes task
   - Creates plan
   - Breaks into subtasks
   - Identifies what can be parallelized

2. Multiple Haiku 4.5 instances (Workers):
   - Each completes assigned subtask
   - Executes in parallel for speed
   - Returns results to orchestrator

3. Sonnet 4.5 (Orchestrator):
   - Integrates results from all workers
   - Validates output quality
   - Ensures coherence
   - Delivers final output
```

**Cost/performance optimization:** Expensive Sonnet only for planning/validation, cheap Haiku for execution.

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

### Handoff Protocol

**Clean handoffs between agents:**

```markdown
<agent_handoff_format>
From: {source_agent}
To: {target_agent}
Task: {specific task}
Context:
  - What was done: {summary of prior work}
  - Key findings: {important discoveries}
  - Constraints: {limitations or requirements}
  - Expected output: {what target agent should produce}

Attachments:
  - {relevant files, data, or previous outputs}
</agent_handoff_format>
```

**Why explicit format matters:** Prevents information loss, ensures target agent has full context, enables validation.

### Synchronization

**Handling parallel execution:**

```markdown
Launch pattern:
1. Initiate all parallel agents with shared context
2. Track which agents have completed
3. Collect outputs as they arrive
4. Wait for all to complete OR timeout
5. Proceed with available results (flag missing if timeout)

Partial failure handling:
- If 1 of 3 agents fails: Proceed with 2 results, note gap
- If 2 of 3 agents fail: Consider retry or workflow failure
- Always communicate what was completed vs attempted
</markdown>
```

---

## Anti-Patterns

### Over-Orchestration

❌ Using multiple agents when single agent would suffice

**Example:** Three agents to review 10 lines of code (overkill).

**Fix:** Reserve multi-agent for genuinely complex tasks. Single capable agent often better than coordinating multiple simple agents.

### No Coordination

❌ Launching multiple agents with no coordination or synthesis

**Problem:** User gets conflicting reports, no coherent output, unclear which to trust.

**Fix:** Always synthesize multi-agent outputs into coherent final result.

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

### No Error Recovery

❌ Orchestration with no fallback when agent fails

**Problem:** One agent failure causes entire workflow failure.

**Fix:** Graceful degradation, retry logic, alternative agents, partial results.

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