---
name: create-subagents
description: "Creates specialized Claude Code subagents with focused roles. Use when user says 'create an agent', 'delegate work', or 'set up automated subagents'."
when_to_use: |
  Use when the user says "create an agent", "spawn a subagent", "make me an agent for X", or "delegate this work".
  Do NOT use for general help, single-task execution, or when direct conversation is faster.
  Do NOT use when the goal is general parallel research (use subagent-orchestration), for single-agent tasks, or when direct implementation is faster.
argument-hint: [role description] [tools] [model]
---

## Decision Router

IF creating plugin-distributed subagent → NOTE: plugin subagents IGNORE hooks, mcpServers, permissionMode frontmatter fields
IF using Task tool → NOTE: tool renamed to "Agent" in v2.1.63, backward-compatible alias exists
IF writing spawn prompts → FIRST read the writing-subagent-prompts reference file from the references folder
IF choosing orchestration pattern → IMMEDIATELY read the orchestration-core reference file
IF handling failures → IMMEDIATELY read the failure-modes reference file
IF understanding token cost → BEFORE budgeting read the memory-architecture reference file

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
tools: Tool1, Tool2, Tool3    # Describe by role, not by tool name — what must the subagent accomplish? omit for full access
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

### Plugin Scope Gotcha

**Critical:** When subagents come from plugins (installed via `/plugin install`), these frontmatter fields are SILENTLY IGNORED:
- `hooks` — hook configuration not applied to plugin subagents
- `mcpServers` — MCP server access not granted to plugin subagents
- `permissionMode` — permission restrictions not enforced

**If you need these fields**, copy the subagent definition to `.claude/agents/` (project scope) or `~/.claude/agents/` (user scope).

**URL:** https://code.claude.com/docs/en/sub-agents#choose-a-subagent-scope

**skills field:**
- Preload skills into subagent context at startup
- Full skill content injected, not just description
- Use when: subagent needs domain knowledge before starting (e.g., security-reviewer with project patterns)

**memory field:**
- Persistent memory scope: `user` (~/.claude/agent-memory/), `project` (.claude/agent-memory/), `local` (.claude/agent-memory.local/)
- Enables cross-session learning

**background field:**
- Set `true` to always run as background task
- Background subagents run concurrently, auto-deny permission prompts

**maxTurns field:**
- Maximum agentic turns before subagent stops
- Guards against runaway agents

**isolation field:**
- Set `worktree` for git worktree isolation
- Gives subagent isolated repo copy, auto-cleaned if no changes

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
tools: Describe by role — this subagent reads source, searches patterns, and runs security analysis tools
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

**Worker cap enforcement:** When you need more than 5 workers, add a second-tier supervisor rather than overloading one. See the gotchas reference file for the full supervisor bottleneck explanation.

### The Sonnet-Haiku Pattern

Most efficient orchestration:

1. **Sonnet** (orchestrator): Analyzes, plans, decomposes
2. **Haiku workers** (parallel): Execute subtasks
3. **Sonnet**: Validates, integrates, delivers

Expensive model for thinking, cheap model for doing.

## Memory Scope Decision Tree

Enable memory on every subagent by default. Without it, each invocation starts from scratch — no accumulated patterns, no learned conventions.

| Scope | Location | Git | Use when |
|-------|----------|-----|----------|
| `project` | `.claude/agent-memory/<name>/` | Committed | Team-shared knowledge, code patterns, project conventions |
| `user` | `~/.claude/agent-memory/<name>/` | Not committed | Cross-project expertise, universal patterns |
| `local` | `.claude/agent-memory.local/<name>/` | Gitignored | Secrets, sensitive findings, project-specific knowledge |

**Decision guide:**
```
Is the knowledge project-specific (code patterns, team conventions)?
  → YES → memory: project (commit it so teammates benefit)
Is the knowledge universal across all projects?
  → YES → memory: user (stays on your machine)
Does the agent handle sensitive output (security findings, credentials)?
  → YES → memory: local (gitignored, not shared)
```

## Body Prompt Philosophy — The Waste Test

**Rule:** If you're writing more than ~30 lines of body content, you're duplicating a skill.

The markdown body (after frontmatter) is the subagent's system prompt. Keep it general and concise — a short role statement and a few behavioral guardrails. Never turn it into a manual.

**The test:** If deleting a body section and adding a skill reference produces the same behavior, the body section was waste.

| Good body | Bad body |
|-----------|----------|
| 3-5 lines | 30+ lines duplicating a skill |
| Role + behavioral guardrails | Step-by-step instructions that belong in a skill |
| "You are X. Never modify files. Report lookups with source." | Detailed field specs, workflow steps, tool descriptions |

**What body should contain:**
- One paragraph for the role
- Optional short sections for constraints or output format only if truly needed
- Never duplicate content that exists in a skill (body references the skill instead)
- Never enumerate tools — the agent discovers them at runtime

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

### Verify-While-Work

Dual-track execution: verify ground-truth while agent investigates a slice. Compare findings before synthesis.

Use when: Unknown root cause, high-stakes findings.

Pattern:
- You: Read original source, verify facts
- Agent: Investigate slice, report findings
- Both: Write to scratchpad, compare before synthesis

### Monitor-Wrapped

Background agent + Monitor for completion. Use when: CI runs, benchmark sweeps, long-running external processes.

Pattern:
- Background agent: Runs configs, emits results to file
- Monitor: Fires on completion signal
- Synthesis agent: Aggregates results from file

### Council Triumvirate (High-Stakes Decisions)

For decisions where getting it wrong is costly, use three adversarial roles:

| Role | Job | Output |
|------|-----|--------|
| **Critic** | Devil's advocate — find 2 fatal flaws | Specific mechanism failures |
| **Creative** | Find genuinely different approaches | Core mechanism alternatives |
| **Expert** | Validate factual correctness | Verified claims |

**When to use:** Architecture decisions, strategy selection, security reviews.

**Distinct from Contest:** Contest tests competing hypotheses for root cause. Council tests quality of a single proposal.

**Council protocol:**
1. Present proposal to all three simultaneously
2. Each writes findings to shared scratchpad
3. Orchestrator reads scratchpad, identifies conflicts
4. Conflicts resolved through explicit debate rounds
5. Consensus requires agreement — not just absence of disagreement

---

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

**Full anti-pattern catalog with concrete wrong/right pairs is in the anti-patterns.md file in this skill's references.**

Key patterns to avoid:

### Tool Restriction at Birth
Start with no tool restrictions. Premature restriction is the most common cause of silent agent failures.

### Too Generic
"You are a helpful assistant" provides no specialization.

### No Workflow
Without a workflow, the subagent may skip important steps.

### Requires User Interaction
Subagents cannot use AskUserQuestion — move user interaction to main chat.

### Vague Spawn Prompt
"Implement the feature and make sure it's good" has no scope, success criteria, or rollback.

---

## Multi-Agent Gotchas (Critical)

**BEFORE adding agents, read the gotchas reference file.**

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

**Solution 1 — forward_message:** For final complete outputs, pass directly to user without supervisor synthesis:
```python
def forward_message(message: str, to_user: bool = True):
    if to_user:
        return {"type": "direct_response", "content": message}
```
**Solution 2 — Shared scratchpad:** For state multiple agents need, use `.principled/scratch/{topic}.md` instead of message-passing.

**When swarm over supervisor:** Prefer swarm when sub-agents can respond directly to users — eliminates translation errors entirely.

## Explorer Subagent Protocol

When spawning subagents for investigation/research/exploration:

### Before Spawning
1. Read existing scratchpad: `.principled/scratch/{topic}.md`
2. Write current questions and context to that scratchpad
3. Include explicit instruction for subagent to UPDATE the scratchpad

### Tool Requirements (NON-OPTIONAL)
- **NEVER** use "native" Explore subagents (Haiku, read-only) for investigation
- **REQUIRED** role: subagent must read source, write findings, search patterns, list directories, and run commands
- Write access is **NON-OPTIONAL** — findings must be persisted to scratchpad

### After Subagents Return
1. Read scratchpad BEFORE synthesizing
2. Merge findings into working context
3. Update scratchpad with synthesis conclusions

**Why:** The telephone game degrades quality by ~50% when orchestrators synthesize without source access. Direct scratchpad access eliminates paraphrase drift.

---

## Reference Index

The skill contains reference files covering: writing-subagent-prompts (core principles, XML structure, examples, anti-patterns), orchestration-core (four rules, orchestrator checklist, cost-capability spectrum), failure-modes (detection, recovery, prevention), memory-architecture (four-layer memory, context window discipline), gotchas (eight critical multi-agent gotchas from production), subagents (configuration, model selection, tool security), context-management (STM, LTM, working memory, context strategies), automation-layers (hooks, Monitor, ScheduleWakeup patterns), and tools-reference (TaskGet, TaskOutput, TaskStop, SendMessage).

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