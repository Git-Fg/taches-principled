# Context Management for Subagents

## Sections
- [Core Problem](#core-problem)
- [Memory Architecture](#memory-architecture)
- [Context Strategies](#context-strategies)
- [Subagent Patterns](#subagent-patterns)
- [Anti-Patterns](#anti-patterns)
- [Best Practices](#best-practices)

---

"Most agent failures are not model failures, they are context failures."

---

## Core Problem

LLMs are stateless by default. Each invocation starts fresh with no memory of previous interactions.

**For subagents, this means:**
- Long-running tasks lose context between tool calls
- Repeated information wastes tokens
- Important decisions from earlier in workflow forgotten
- Context window fills with redundant information

**Critical threshold:** When context approaches limit, quality degrades before hard failure.

---

## Memory Architecture

### Short-Term Memory (STM)

**Last 5-9 interactions.**

Preserved in context window.

**Use for:**
- Current task state
- Recent tool call results
- Immediate decisions
- Active conversation flow

**Limitation:** Limited capacity, volatile (lost when context cleared).

### Long-Term Memory (LTM)

**Persistent storage across sessions.**

Implementation: External storage (files, databases, vector stores).

**Use for:**
- Historical patterns
- Accumulated knowledge
- User preferences
- Past task outcomes

**Access pattern:** Retrieve relevant memories into working memory when needed.

### Working Memory

**Current context + retrieved memories.**

**Composition:**
- Core task information (always present)
- Recent interaction history (STM)
- Retrieved relevant memories (from LTM)
- Current tool outputs

**Management:** This is what fits in context window. Optimize aggressively.

### Core Memory

**Actively used information in current interaction.**

**Examples:**
- Current task goal and constraints
- Key facts about the codebase being worked on
- Critical requirements from user
- Active workflow state

**Principle:** Keep core memory minimal and highly relevant. Everything else is retrievable.

---

## Context Strategies

### Summarization

**Pattern:** Move information from context to searchable database, keep summary in memory.

**Trigger summarization when:**
- Context reaches 75% of limit
- Task transitions to new phase
- Information is important but no longer actively needed
- Repeated information appears multiple times

**Quality guidelines:**

1. **Highlight important events**
   ```
   Bad: "Reviewed code, found issues, provided fixes"
   Good: "Identified critical SQL injection in auth.ts:127, provided parameterized query fix."
   ```

2. **Include timing for sequential reasoning**
   ```
   "First attempt: Direct fix failed due to type mismatch.
    Second attempt: Added type conversion, introduced runtime error.
    Final approach: Refactored to use type-safe wrapper (successful)."
   ```

3. **Structure into categories vs long paragraphs**
   ```
   Issues found:
   - Security: SQL injection (Critical), XSS (High)
   - Performance: N+1 query (Medium)

   Actions taken:
   - Fixed SQL injection with prepared statements
   - Deferred performance optimization
   ```

### Sliding Window

**Pattern:** Recent interactions in context, older interactions as vectors for retrieval.

**Implementation:**
```markdown
Maintain in context:
- Last 5 tool calls and results (short-term memory)
- Current task state and goals (core memory)
- Key facts from user requirements (core memory)

Move to vector storage:
- Tool calls older than 5 steps
- Completed subtask results
- Historical debugging attempts
```

**Benefit:** Bounded context growth, relevant history still accessible.

### Semantic Context Switching

**Pattern:** Detect context changes, respond appropriately.

**On context switch:**
1. Summarize current context state
2. Save state to working memory/file
3. Load relevant context for new topic
4. Acknowledge switch: "Switching from bug analysis to feature implementation."

**Prevents:** Mixing contexts, applying wrong constraints, forgetting important info when switching tasks.

### Scratchpads

**Pattern:** Record intermediate results outside LLM context.

**When to use scratchpads:**
- Complex calculations with many steps
- Exploration of multiple approaches
- Detailed analysis that may not all be relevant
- Debugging traces
- Intermediate data transformations

**Implementation:**
```markdown
<scratchpad_workflow>
For complex debugging:
1. Create scratchpad file: `.principled/scratch/debug-session-{timestamp}.md`
2. Log each hypothesis and test result in scratchpad
3. Keep only current hypothesis and key findings in context
4. Reference scratchpad for full debugging history
5. Summarize successful approach in final output
</scratchpad_workflow>
```

**Benefit:** Context contains insights, scratchpad contains exploration. User gets clean summary, full details available if needed.

### Compaction

**Pattern:** Summarize near-limit conversations, reinitiate with summary.

**Workflow:**
```markdown
<compaction_workflow>
When context reaches 90% capacity:
1. Identify essential information:
   - Current task and status
   - Key decisions made
   - Critical constraints
   - Important discoveries
2. Generate concise summary (max 20% of context size)
3. Save full context to archival storage
4. Create new conversation initialized with summary
5. Continue task in fresh context
</compaction_workflow>
```

**When to use:** Long-running tasks, exploratory analysis, iterative debugging.

---

## Subagent Patterns

### Stateful Subagent

**For long-running or frequently-invoked subagents:**

```markdown
<role>
You are a system architect maintaining coherent design across project evolution.
</role>

<memory_management>
On each invocation:
1. Read `.principled/memory/architecture-state.md` for current system state
2. Perform assigned task with full context
3. Update architecture-state.md with new components, decisions, patterns
4. Maintain concise state (max 500 lines), summarize older decisions
</memory_management>
```

### Stateless Subagent

**For simple, focused subagents:**

```markdown
<role>
You are a syntax validator. Check code for syntax errors.
</role>

<workflow>
1. Read specified files
2. Run syntax checker (language-specific linter)
3. Report errors with line numbers
4. No memory needed - each invocation is independent
</workflow>
```

**When to use stateless:** Single-purpose validators, formatters, simple transformations.

### Context Inheritance

**Inheriting context from main chat:**

Subagents automatically have access to:
- User's original request
- Any context provided in invocation

```markdown
Main chat: "Review the authentication changes for security issues.
           Context: We recently switched from JWT to session-based auth."

Subagent receives:
- Task: Review authentication changes
- Context: Recent switch from JWT to session-based auth
```

---

## Anti-Patterns

### Context Dumping

❌ Including everything in context "just in case"

**Problem:** Buries important information in noise, wastes tokens, degrades performance.

**Fix:** Include only what's relevant for current task. Everything else is retrievable.

### No Summarization

❌ Letting context grow unbounded until limit hit

**Problem:** Sudden context overflow mid-task, quality degradation before failure.

**Fix:** Proactive summarization at 75% capacity, continuous compaction.

### Lossy Summarization

❌ Summaries that discard critical information

**Example:**
```
Bad summary: "Tried several approaches, eventually fixed bug"
Lost information: What approaches failed, why, what the successful fix was
```

**Fix:** Summaries preserve essential facts, decisions, and rationale. Details go to archival storage.

### No Memory Structure

❌ Unstructured memory (long paragraphs, no organization)

**Problem:** Hard to retrieve relevant information, poor for LLM reasoning.

**Fix:** Structured memory with categories, bullet points, clear sections.

### Context Failure Ignorance

❌ Assuming all failures are model limitations

**Reality:** "Most agent failures are context failures, not model failures."

Check context quality before blaming model:
- Is relevant information present?
- Is it organized clearly?
- Is important info buried in noise?
- Has context been properly maintained?

---

## Best Practices

### Core Memory Minimal

Keep core memory minimal and highly relevant.

**Rule of thumb:** If information isn't needed for next 3 steps, it doesn't belong in core memory.

### Structured Summaries

Summaries should be structured, categorized, and scannable.

**Template:**
```
**Status**: [Progress]
**Completed**:
- [Key accomplishment 1]
- [Key accomplishment 2]

**Decisions**:
- [Important choice 1]: [Rationale]

**Next**: [Immediate next steps]
```

### Timing Matters

Include timing for sequential reasoning.

"First tried X (failed), then tried Y (worked)" is more useful than "Used approach Y".

### Retrieval Over Retention

Better to retrieve information on-demand than keep it in context always.

**Exception:** Frequently-used core facts (task goal, critical constraints).

### External Storage

**Use filesystem for:**
- Full logs and traces
- Detailed exploration results
- Historical data
- Intermediate work products

**Use context for:**
- Current task state
- Key decisions
- Active workflow
- Immediate next steps

---

## Context Isolation Mechanisms (Multi-Agent)

When delegating to subagents, choose the right isolation mechanism based on task complexity.

### Three Mechanisms

| Mechanism | Description | Use When | Trade-off |
|-----------|-------------|----------|-----------|
| **Full context delegation** | Pass entire orchestrator context to subagent | Complex tasks requiring complete understanding | Partially defeats context isolation purpose |
| **Instruction passing** | Create instructions via function call; subagent receives only objective/constraints/inputs/outputs | Simple, well-defined subtasks | Maintains isolation but limits subagent flexibility |
| **File system memory** | Subagent reads/writes persistent storage | Complex tasks requiring shared state | Introduces latency; scales better than message-passing |

### Default to Instruction Passing

Start with instruction passing — pass only what the subtask needs:
- Objective: What to accomplish
- Constraints: What to avoid
- Inputs: What to work with
- Outputs: What format to produce

**Example:**
```markdown
<Objective>
Analyze security of auth.ts for SQL injection vulnerabilities.
</Objective>
<Constraints>
- Do NOT modify any code
- Do NOT run commands that modify state
- Focus only on SQL injection
</Constraints>
<Inputs>
- File: src/auth.ts
- Recent changes: git diff HEAD~5 src/auth.ts
</Inputs>
<Outputs>
- List of findings with severity, location, and specific remediation
</Outputs>
```

### When to Escalate to Filesystem

Use shared scratchpads (`.principled/scratch/multi-agent-state.md`) when:
- Multiple agents must access the same data
- Results from one agent feed into another agent's task
- State must persist across agent invocations
- No single agent has the complete picture

**See also:** `{baseDir}/references/gotchas.md` — Missing shared state gotcha for when this matters.

### When Full Context Is Appropriate

Full context delegation is appropriate only when:
- Subtask genuinely requires understanding the entire system state
- Orchestrator has already distilled the context to only relevant portions
- The alternative would require passing a complex dependency graph

**Warning:** Full context delegation partially defeats the purpose of context isolation. Only use when the isolation cost exceeds the coordination cost.

---

## Context Degradation Signals

Three signals indicate context is degrading quality before hitting hard limits:

| Signal | What Happens | Mitigation |
|--------|-------------|------------|
| **Lost-in-middle effect** | Attention weakens for mid-context content | Move critical info to start/end of context |
| **Attention scarcity** | Too many competing items in context | Aggressive prioritization; split to scratchpads |
| **Context poisoning** | Irrelevant content displaces useful content | Strict context hygiene; exclude noise |

**The quality degradation curve:**

```
Context Usage  │  Quality Level   │  Mental State
─────────────────────────────────────────────────────
0-30%          │  PEAK           │  "I can be thorough"
30-50%         │  GOOD           │  "Still have room"
50-70%         │  DEGRADING      │  "Getting tight"
70%+           │  POOR           │  "Running out"
```

**Target:** Plans should complete within ~50% of context usage. Stop before quality degrades, not at context limit. See `{baseDir}/references/token-economics.md` for full explanation of token economics.