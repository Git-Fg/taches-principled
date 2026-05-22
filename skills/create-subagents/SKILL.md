---
name: create-subagents
description: "Create specialized Claude Code subagents with focused roles. Use when user asks to create an agent, delegate work, or set up automated subagents."
when_to_use: |
  Do NOT use for general help, single-task execution, or when direct conversation is faster.
---

## Decision Router

IF writing spawn prompts → FIRST read `{baseDir}/references/writing-subagent-prompts.md`
IF choosing orchestration pattern → IMMEDIATELY read `{baseDir}/references/orchestration-patterns.md`
IF managing subagent context → BEFORE spawning read `{baseDir}/references/context-management.md`
IF configuring subagent tools → BEFORE setting restrictions read `{baseDir}/references/subagents.md`
IF evaluating subagent quality → BEFORE testing read `{baseDir}/references/evaluation-and-testing.md`
IF designing multi-agent coordination → IMMEDIATELY read `{baseDir}/references/gotchas.md`
IF handling failures in multi-agent workflows → IMMEDIATELY read `{baseDir}/references/fault-tolerance.md`
IF understanding token cost of multi-agent → BEFORE budgeting read `{baseDir}/references/token-economics.md`
IF reconciling conflicting agent outputs → BEFORE deciding read `{baseDir}/references/consensus.md`

---

# Create Subagents Skill

Create specialized Claude Code subagents with expert guidance. Subagents are specialized Claude instances that run in isolated contexts with focused roles and limited tool access.

---

## What Subagents Are

Subagents enable delegation of complex tasks to specialized agents that operate autonomously without user interaction, returning their final output to the main conversation.

**Key constraint:** Subagents are black boxes that cannot interact with users.

Subagents:
- ✅ Can use tools like Read, Write, Edit, Bash, Grep, Glob
- ✅ Can access MCP servers and other non-interactive tools
- ❌ **Cannot use AskUserQuestion** or any tool requiring user interaction
- ❌ **Cannot present options or wait for user input**
- ❌ **User never sees subagent's intermediate steps**

### Policy vs. Mechanism

**Policy** = when to spawn a subagent vs. handling inline (delegation strategy)
**Mechanism** = how to construct the spawn prompt, scope files, define success criteria

A subagent definition conflating policy and mechanism produces agents that:
- Know WHAT to do but not WHEN to act (missing policy)
- Know WHEN to act but not HOW to do it (missing mechanism)

Separate in your thinking:
- Policy decisions live in the orchestrator's judgment
- Mechanism details live in the spawn prompt you write

Example:
- Policy: "Subagent is appropriate when task has clear scope + independent verification"
- Mechanism: "Spawn with file-disjoint scopes, RACE structure, explicit rollback"

---

## Quick Start

### Create via /agents command

1. Run `/agents` command
2. Select "Create New Agent"
3. Choose project-level (`.claude/agents/`) or user-level (`~/.claude/agents/`)
4. Define the subagent:
   - **name**: lowercase-with-hyphens
   - **description**: When should this subagent be used?
   - **tools**: Optional comma-separated list (inherits all if omitted)
   - **model**: Optional (`sonnet`, `opus`, `haiku`, or `inherit`)
5. Write the system prompt (the subagent's instructions)

### File Structure

| Type | Location | Scope | Priority |
|------|----------|-------|----------|
| **Project** | `.claude/agents/` | Current project only | Highest |
| **User** | `~/.claude/agents/` | All projects | Lower |
| **Plugin** | Plugin's `agents/` dir | All projects | Lowest |

Project-level subagents override user-level when names conflict.

---

## Subagent Configuration

### Frontmatter Fields

```yaml
---
name: subagent-name          # Lowercase/hyphens only, must be unique
description: What it does and when to use it. Include trigger keywords.
tools: Tool1, Tool2, Tool3    # Comma-separated; omit for all tools
model: sonnet                # sonnet, opus, haiku, or inherit
---
```

**name field:**
- Lowercase letters and hyphens only
- Must be unique

**description field:**
- Natural language description of purpose
- Include when Claude should invoke this subagent
- Used for automatic subagent selection
- Include trigger keywords that match common user requests

**tools field:**
- Comma-separated list: `Read, Write, Edit, Bash, Grep`
- If omitted: inherits all tools from main thread

**model field:**
- `sonnet`, `opus`, `haiku`, or `inherit`
- `inherit`: uses same model as main conversation

---

## Writing Effective Prompts

### Core Principles

**1. Be specific**
Define exactly what the subagent does and how it approaches tasks.

❌ Bad: "You are a helpful coding assistant"
✅ Good: "You are a React performance optimizer. Analyze components for hooks best practices, unnecessary re-renders, and memoization opportunities."

**2. Use clear structure**
Organize the prompt with labeled sections. Use markdown headers for major sections.

**3. Include constraints**
State what the subagent should NOT do. Use strong modal verbs (MUST, SHOULD, NEVER, ALWAYS).

```markdown
<constraints>
- NEVER modify production code, ONLY test files
- MUST verify tests pass before completing
- ALWAYS include edge case coverage
</constraints>
```

### Recommended Structure

```markdown
<role>
You are a [specific expertise] specializing in [specific domain].
</role>

<focus_areas>
- Specific concern 1
- Specific concern 2
- Specific concern 3
</focus_areas>

<workflow>
1. First step
2. Second step
3. Third step
</workflow>

<output_format>
Expected output structure
</output_format>

<constraints>
- Do not X
- Always Y
- Never Z
</constraints>
```

---

## Examples

### Security Reviewer

```markdown
---
name: security-reviewer
description: Reviews code for security vulnerabilities. Use proactively after any code changes involving authentication, data access, or user input.
tools: Read, Grep, Glob, Bash
model: sonnet
---

## Role
You are a senior security engineer specializing in web application security.

## Focus Areas
- SQL injection vulnerabilities
- XSS (Cross-Site Scripting) attack vectors
- Authentication and authorization flaws
- Sensitive data exposure
- CSRF (Cross-Site Request Forgery)

## Workflow
1. Run git diff to identify recent changes
2. Read modified files focusing on data flow
3. Identify security risks with severity ratings
4. Provide specific remediation steps

## Output Format
For each issue found:
1. **Severity**: [Critical/High/Medium/Low]
2. **Location**: [File:LineNumber]
3. **Vulnerability**: [Type and description]
4. **Risk**: [What could happen]
5. **Fix**: [Specific code changes needed]

## Constraints
- Focus only on security issues, not code style
- Provide actionable fixes, not vague warnings
- If no issues found, confirm the review was completed
```

## Model Selection

| Model | Best For |
|-------|----------|
| **Sonnet** | Complex reasoning, planning, validation |
| **Haiku** | Fast execution, bulk processing, simple tasks |
| **Opus** | Highest-stakes decisions |

### Numeric Thresholds

| Metric | Limit | Why |
|--------|-------|-----|
| Tools per subagent | 7 max | Miller's number; beyond this is coordination overhead |
| Spawn prompt length | 1500 tokens max | Degradation past this; split into multiple agents |
| Files in scope | 10 max per agent | Scope creep = quality loss |
| **Concurrent workers per supervisor** | **3-5 max** | Non-linear context growth; beyond this supervisor saturates |
| **Token budget for multi-agent** | **~15x baseline** | Coordination overhead, retries, consensus rounds all add cost |

**Split signal:** If a task needs >10 files or >7 tools or has >1500 tokens of context — decompose first.

**Worker cap enforcement:** When you need more than 5 workers, add a second-tier supervisor rather than overloading one. See `{baseDir}/references/gotchas.md` for the full supervisor bottleneck explanation.

### The Sonnet-Haiku Pattern

Most efficient orchestration:

1. **Sonnet** (orchestrator): Analyzes, plans, decomposes
2. **Haiku workers** (parallel): Execute subtasks
3. **Sonnet**: Validates, integrates, delivers

Expensive model for thinking, cheap model for doing.

---

## Orchestration Patterns

### Sequential (A → B → C)

When each step depends on the previous. Clear dependencies, easy to debug. Slower.

Example: Security review → Performance review → Report synthesis

### Parallel (A + B + C simultaneously)

When tasks don't depend on each other. Massive speed gains (3-5x faster in practice).

Example: Launch security, performance, and accessibility reviews together

### Hierarchical (coordinator → specialists)

When a large task needs decomposition. Orchestrator breaks down work, specialists execute.

Example: "Build payment system" → coordinator creates teams for backend, frontend, devops

### Coordinator Pattern

Central AI agent routes tasks to specialized subagents dynamically.

Example: "Help me improve my codebase" → coordinator analyzes → routes to appropriate specialists → synthesizes results

### Tracking Spawned Subagents

When orchestrating multiple subagents, treat each as a unit of work for visibility and coordination.

**When tracking matters:**
- Parallel execution (A + B + C simultaneously): Track each worker so the orchestrator knows when all complete before aggregating
- Hierarchical decomposition: Track each specialist's result so the coordinator can verify coverage before synthesizing
- Long-running tasks: Track progress so failure doesn't leave orphaned work

**When tracking is optional:**
- Sequential delegation (A → B → C): Each step completes before the next starts; natural checkpoint is the dependency
- Simple fire-and-forget: When a single subagent handles a well-defined task with clear completion criteria

**Pattern language:**
- "Track parallel workers" — explicit tracking when 3+ agents running and aggregator needs all completed
- "Checkpoint after each" — implicit tracking when execution is strictly sequential
- "Monitor for completion" — tracking when downstream work depends on all results

The orchestrator owns coordination state. Subagents are isolated — they don't see each other's outputs or progress. The orchestrator holds the thread and decides when to proceed, aggregate, or retry.

---

## Workflow Design

### Use Main Chat For:
- Gathering requirements from user (AskUserQuestion)
- Presenting options or decisions to user
- Any task requiring user confirmation/input
- Work where user needs visibility into progress

### Use Subagents For:
- Research tasks (API documentation lookup, code analysis)
- Code generation based on pre-defined requirements
- Analysis and reporting (security review, test coverage)
- Context-heavy operations that don't need user interaction

### Example Workflow Pattern

```
Main Chat: Ask user for requirements (AskUserQuestion)
  ↓
Subagent: Research API and create documentation (no user interaction)
  ↓
Main Chat: Review research with user, confirm approach
  ↓
Subagent: Generate code based on confirmed plan
  ↓
Main Chat: Present results, handle testing/deployment
```

---

## Anti-Patterns

### ❌ Too Generic

```markdown
You are a helpful assistant that helps with code.
```

This provides no specialization. The subagent won't know what to focus on.

### ❌ No Workflow

```markdown
You are a code reviewer. Review code for issues.
```

Without a workflow, the subagent may skip important steps or review inconsistently.

### ❌ Requires User Interaction

**Critical**: Subagents cannot interact with users.

```markdown
---
name: intake-agent
description: Gathers requirements from user
tools: AskUserQuestion
---

<workflow>
1. Ask user about their requirements using AskUserQuestion
2. Follow up with clarifying questions
3. Return finalized requirements
</workflow>
```

**Why this fails:** Subagents execute in isolated contexts. They cannot use AskUserQuestion.

**Correct approach:** Move user interaction to main chat.

### ❌ Missing Constraints

Without constraints, subagents might modify code they shouldn't, run dangerous commands, or skip important steps.

### ❌ Unclear Trigger

The `description` field is critical for automatic invocation.

❌ Bad: `description: Helps with testing`
✅ Good: `description: Creates comprehensive test suites. Use when new code needs tests or test coverage is insufficient.`

### ❌ Vague spawn prompt
"Implement the feature and make sure it's good" — no scope, no success criteria, no rollback.

### ✅ Specific spawn prompt
"Implement POST /api/users in src/api/users.ts. Verify: npx jest --testPathPattern=users. Rollback: git checkout -- src/api/users.ts"

### ❌ Over-permissioned tools
Granting write, edit, and execution tools to a read-only analysis agent.

### ✅ Least-privilege tools
Read-only analysis: `Read, Grep, Glob`. Code implementation: `Read, Edit, Bash`. No extra tools.

### ❌ Generic subagent name
"name: helper" — provides no specialization signal to the orchestrator.

### ✅ Specific subagent name
"name: security-reviewer" — orchestrator knows exactly what this agent does.

### ❌ No rollback plan
Spawn prompt without stated rollback = no recovery path if agent goes wrong.

### ✅ Explicit rollback
"At any failure: stop, report, do not continue. Rollback: git checkout -- <file>"

---

## Multi-Agent Gotchas (Critical)

**BEFORE adding agents, read `{baseDir}/references/gotchas.md`.**

Multi-agent systems fail in predictable ways. These eight gotchas account for the majority of production failures:

| Gotcha | Cap | Prevention |
|--------|-----|------------|
| Supervisor bottleneck | 3-5 workers/supervisor | Second-tier supervisors |
| Token cost underestimation | 15x baseline | Budget 15x, treat less as bonus |
| Sycophantic consensus | Weighted voting | Adversarial roles required |
| Agent sprawl | 3-5 agents minimum | Start minimal |
| Telephone game | Direct response | forward_message or shared files |
| Error propagation cascades | Circuit breaker | Verification checkpoints |
| Over-decomposition | 2-4 tool ops/agent | Meaningful task scope |
| Missing shared state | Scratchpad | Shared persistent storage |

**The telephone game problem:** Information degrades through repeated summarization. LangGraph benchmarks show supervisor architectures perform ~50% worse than optimized versions due to paraphrase degradation.

**Solution:** Use filesystem coordination (shared scratchpads) instead of message-passing for state that multiple agents need to access faithfully.

---

## Reference Index

| Reference | Purpose |
|-----------|---------|
| `{baseDir}/references/writing-subagent-prompts.md` | Core principles, XML structure, examples, anti-patterns |
| `{baseDir}/references/orchestration-patterns.md` | Sequential, parallel, hierarchical, coordinator patterns |
| `{baseDir}/references/subagents.md` | Configuration, model selection, tool security |
| `{baseDir}/references/context-management.md` | STM, LTM, working memory, context strategies |
| `{baseDir}/references/gotchas.md` | Eight critical multi-agent gotchas from production |
| `{baseDir}/references/fault-tolerance.md` | Circuit breaker, checkpoint/resume, exponential backoff |
| `{baseDir}/references/token-economics.md` | Real cost of multi-agent (~15x baseline), when justified |
| `{baseDir}/references/consensus.md` | Weighted voting, debate protocol, adversarial critique |

---

## Success Criteria

A well-configured subagent has:
- Valid YAML frontmatter (name matches file, description includes triggers)
- Clear role definition in system prompt
- Appropriate tool restrictions (least privilege)
- XML-structured system prompt with role, approach, and constraints
- Description field optimized for automatic routing
- Successfully tested on representative tasks
- Model selection appropriate for task complexity (Sonnet for reasoning, Haiku for simple tasks)