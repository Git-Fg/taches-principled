# Context Management for Subagents

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
1. Create scratchpad file: `.claude/scratch/debug-session-{timestamp}.md`
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
---
name: code-architect
description: Maintains understanding of system architecture across multiple invocations
tools: Read, Write, Grep, Glob
model: sonnet
---

<role>
You are a system architect maintaining coherent design across project evolution.
</role>

<memory_management>
On each invocation:
1. Read `.claude/memory/architecture-state.md` for current system state
2. Perform assigned task with full context
3. Update architecture-state.md with new components, decisions, patterns
4. Maintain concise state (max 500 lines), summarize older decisions
</memory_management>
```

### Stateless Subagent

**For simple, focused subagents:**

```markdown
---
name: syntax-checker
description: Validates code syntax without maintaining state
tools: Read, Bash
model: haiku
---

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