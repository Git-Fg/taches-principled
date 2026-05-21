# Subagents Reference

Subagent file structure, configuration, model selection, and best practices.

---

## File Format

```markdown
---
name: your-subagent-name
description: Description of when this subagent should be invoked
tools: tool1, tool2, tool3 # Optional - inherits all tools if omitted
model: sonnet # Optional - specify model alias or 'inherit'
---

<role>
Your subagent's system prompt using pure XML structure. This defines the subagent's role, capabilities, and approach.
</role>

<constraints>
Hard rules using NEVER/MUST/ALWAYS for critical boundaries.
</constraints>

<workflow>
Step-by-step process for consistency.
</workflow>
```

**Critical:** Use pure XML structure in the body. Remove ALL markdown headings (##, ###). Keep markdown formatting within content (bold, lists, code blocks).

### Configuration Fields

| Field | Required | Description |
|-------|----------|-------------|
| `name` | Yes | Unique identifier using lowercase letters and hyphens |
| `description` | Yes | Natural language description of purpose. Include when Claude should invoke this. |
| `tools` | No | Comma-separated list. If omitted, inherits all tools from main thread |
| `model` | No | `sonnet`, `opus`, `haiku`, or `inherit`. If omitted, uses default subagent model |

---

## Storage Locations

| Type | Location | Scope | Priority |
|------|----------|-------|----------|
| **Project** | `.claude/agents/` | Current project only | Highest |
| **User** | `~/.claude/agents/` | All projects | Lower |
| **CLI** | `--agents` flag | Current session | Medium |
| **Plugin** | Plugin's `agents/` dir | All projects | Lowest |

When subagent names conflict, higher priority takes precedence.

---

## Execution Model

### Black Box Model

Subagents execute in isolated contexts without user interaction.

**Key characteristics:**
- Subagent receives input parameters from main chat
- Subagent runs autonomously using available tools
- Subagent returns final output/report to main chat
- User only sees final result, not intermediate steps

**This means:**
- ✅ Subagents can use Read, Write, Edit, Bash, Grep, Glob, WebSearch, WebFetch
- ✅ Subagents can access MCP servers (non-interactive tools)
- ✅ Subagents can make decisions based on their prompt and available data
- ❌ **Subagents CANNOT use AskUserQuestion**
- ❌ **Subagents CANNOT present options and wait for user selection**
- ❌ **Subagents CANNOT request confirmations or clarifications from user**
- ❌ **User does not see subagent's tool calls or intermediate reasoning**

### Workflow Implications

Keep user interaction in main chat:

```markdown
# ❌ WRONG - Subagent cannot do this
---
name: requirement-gatherer
description: Gathers requirements from user
tools: AskUserQuestion  # This won't work!
---

You ask the user questions to gather requirements...
```

```markdown
# ✅ CORRECT - Main chat handles interaction
Main chat: Uses AskUserQuestion to gather requirements
  ↓
Launch subagent: Uses requirements to research/build (no interaction)
  ↓
Main chat: Present subagent results to user
```

---

## Tool Configuration

### Inherit All Tools

Omit the `tools` field to inherit all tools from main thread:

```yaml
---
name: code-reviewer
description: Reviews code for quality and security
---
```

Subagent has access to all tools, including MCP tools.

### Specific Tools

Specify tools as comma-separated list for granular control:

```yaml
---
name: read-only-analyzer
description: Analyzes code without making changes
tools: Read, Grep, Glob
---
```

---

## Model Selection

### Model Capabilities

**Sonnet 4.5** (`sonnet`):
- "Best model in the world for agents" (Anthropic)
- Exceptional at agentic tasks: 64% problem-solving on coding benchmarks
- SWE-bench Verified: 49.0%
- **Use for**: Planning, complex reasoning, validation, critical decisions

**Haiku 4.5** (`haiku`):
- "Near-frontier performance" - 90% of Sonnet 4.5's capabilities
- SWE-bench Verified: 73.3% (one of world's best coding models)
- Fastest and most cost-efficient
- **Use for**: Task execution, simple transformations, high-volume processing

**Opus** (`opus`):
- Highest performance on evaluation benchmarks
- Most capable but slowest and most expensive
- **Use for**: Highest-stakes decisions, most complex reasoning

**Inherit** (`inherit`):
- Uses same model as main conversation
- **Use for**: Ensuring consistent capabilities throughout session

### Sonnet + Haiku Orchestration

**Optimal cost/performance pattern:**

```markdown
1. Sonnet 4.5 (Coordinator):
   - Creates plan
   - Breaks task into subtasks
   - Identifies parallelizable work

2. Multiple Haiku 4.5 instances (Workers):
   - Execute subtasks in parallel
   - Fast and cost-efficient
   - 90% of Sonnet's capability for execution

3. Sonnet 4.5 (Validator):
   - Integrates results
   - Validates output quality
   - Ensures coherence
```

**Benefit**: Use expensive Sonnet only for planning and validation, cheap Haiku for execution.

### When to Use Each Model

| Task Type | Recommended Model | Rationale |
|-----------|------------------|-----------|
| Simple validation | Haiku | Fast, cheap, sufficient |
| Code execution | Haiku | 73.3% SWE-bench, very fast |
| Complex analysis | Sonnet | Superior reasoning |
| Multi-step planning | Sonnet | Best for breaking down complexity |
| Quality validation | Sonnet | Critical checkpoint, needs intelligence |
| Batch processing | Haiku | Cost efficiency |
| Critical security | Sonnet | High stakes require best model |
| Output synthesis | Sonnet | Ensuring coherence |

---

## Invocation

### Automatic

Claude automatically selects subagents based on:
- Task description in user's request
- `description` field in subagent configuration
- Current context

### Explicit

Users can explicitly request a subagent:

```
> Use the code-reviewer subagent to check my recent changes
> Have the test-runner subagent fix the failing tests
```

---

## Tool Security

### Core Principle

**"Permission sprawl is the fastest path to unsafe autonomy."** - Anthropic

Treat tool access like production IAM: start from deny-all, allowlist only what's needed.

### Why It Matters

**Security risks of over-permissioning:**
- Agent could modify wrong code (production instead of tests)
- Agent could run dangerous commands (rm -rf, data deletion)
- Agent could expose protected information
- Agent could skip critical steps (linting, testing, validation)

### Tool Access Audit Checklist

- [ ] Does this subagent need Write/Edit, or is Read sufficient?
- [ ] Should it execute code (Bash), or just analyze?
- [ ] Are all granted tools necessary for the task?
- [ ] What's the worst-case misuse scenario?
- [ ] Can we restrict further without blocking legitimate use?

**Default**: Grant minimum necessary. Add tools only when lack of access blocks task.

---

## Prompt Caching

### Benefits

- **90% cost reduction** on cached tokens
- **85% latency reduction** for cache hits
- Cached content: ~10% cost of uncached tokens
- Cache TTL: 5 minutes (default) or 1 hour (extended)

### Structure for Caching

```markdown
---
name: security-reviewer
description: ...
tools: ...
model: sonnet
---

[CACHEABLE SECTION - Stable content]
<role>
You are a senior security engineer...
</role>

<focus_areas>
- SQL injection
- XSS attacks
...
</focus_areas>

--- [CACHE BREAKPOINT] ---

[VARIABLE SECTION - Task-specific content]
Current task: {dynamic context}
Recent changes: {varies per invocation}
```

**Principle**: Stable instructions at beginning (cached), variable context at end (fresh).

### Best Candidates for Caching

- Frequently-invoked subagents (multiple times per session)
- Large, stable prompts (extensive guidelines, examples)
- Consistent tool definitions across invocations
- Long-running sessions with repeated subagent use

---

## Best Practices

### Be Specific

Create task-specific subagents, not generic helpers.

❌ Bad: "You are a helpful assistant"
✅ Good: "You are a React performance optimizer specializing in hooks and memoization"

### Clear Triggers

Make the `description` clear about when to invoke:

❌ Bad: "Helps with code"
✅ Good: "Reviews code for security vulnerabilities. Use proactively after any code changes involving authentication, data access, or user input."

### Focused Tools

Grant only the tools needed for the task (least privilege):

- Read-only analysis: `Read, Grep, Glob`
- Code modification: `Read, Edit, Bash, Grep`
- Test running: `Read, Write, Bash`