---
name: sadd-patterns
description: "Design multi-agent architectures — context isolation, supervisor/swarm/hierarchical structures, debate protocols, and coordination patterns"
when_to_use: |
  When user says 'design architecture', 'multi-agent', 'supervisor pattern', 'swarm', 'coordinate agents', 'agent hierarchy', 'how should agents communicate'. IMMEDIATELY when user asks to design a system that spans multiple agent invocations with coordination needs. FIRST when choosing between supervisor, swarm, or hierarchical patterns.
argument-hint: Architecture requirements and coordination pattern
---

## Decision Router

IF designing a system that distributes work across multiple agent invocations → choose architecture pattern based on coordination needs, not organizational metaphor
IF tasks decompose into ordered subtasks with dependencies → use Supervisor/Orchestrator pattern
IF tasks require flexible exploration without rigid planning → use Peer-to-Peer/Swarm pattern
IF tasks span strategic, planning, and execution layers → use Hierarchical pattern
IF single-agent context limits are not being hit → do NOT add multi-agent complexity

# Multi-Agent Architecture Patterns

Multi-agent architectures distribute work across multiple agent invocations, each with its own focused context. When designed well, this distribution enables capabilities beyond single-agent limits. When designed poorly, it introduces coordination overhead that negates benefits.

## Core Principle

Sub-agents exist primarily to isolate context, not to anthropomorphize role division. The critical design insight is that context isolation — giving each subagent a clean window focused on its specific subtask — is the primary benefit of multi-agent systems. Role-based division is a secondary concern.

## Architectural Patterns

### Pattern 1: Supervisor/Orchestrator

A central agent decomposes the user objective into subtasks, dispatches to specialist subagents, and synthesizes results.

```
User Request → Supervisor → [Specialist A, Specialist B, Specialist C] → Aggregation → Final Output
```

**Use when:** Tasks have clear decomposition, require cross-domain coordination, or need human oversight.

**Advantages:** Strict control flow, clear error boundaries, simple human-in-the-loop.

**Disadvantages:** Supervisor context becomes a bottleneck; the "telephone game" where supervisors paraphrase subagent responses with lossy compression.

**Mitigations:**
- Sub-agents write directly to files rather than returning through supervisor
- Supervisor passes structured context, not paraphrased summaries
- File-based checkpoints persist state without full history in supervisor context

### Pattern 2: Peer-to-Peer/Swarm

No central control. Agents communicate directly through shared state (filesystem) and explicit handoff protocols.

**Use when:** Tasks need flexible exploration, rigid planning is counterproductive, or requirements emerge during execution.

**Advantages:** No single point of failure, natural for breadth-first exploration, enables emergent problem-solving.

**Disadvantages:** Coordination complexity grows with agent count, risk of divergence without central state keeper.

**Mitigations:**
- Shared state files as coordination mechanism
- Clear handoff protocols with exit conditions
- Convergence checks that verify progress toward shared goals

### Pattern 3: Hierarchical

Strategic → Planning → Execution layers. Each layer has different context scope and abstraction level.

```
Strategy Layer (Goal Definition) → Planning Layer (Task Decomposition) → Execution Layer (Atomic Tasks)
```

**Use when:** Large-scale projects with clear hierarchical structure, or enterprise workflows requiring both high-level planning and detailed execution.

**Advantages:** Clear separation of concerns, different context structures per layer, mirrors organizational accountability.

**Disadvantages:** Coordination overhead between layers, potential strategy-execution misalignment, complex error propagation.

## Context Isolation Mechanisms

| Mechanism | Best For | Trade-off |
|-----------|----------|-----------|
| Instruction passing | Simple, well-defined subtasks | Limits subagent flexibility |
| Filesystem memory | Complex tasks with shared state | Consistency challenges with concurrent writes |
| Full context delegation | Complex tasks needing complete understanding | Defeats purpose of isolation |

Default to filesystem communication: agents read and write to persistent storage. This avoids context bloat and is transparent and debuggable.

## Consensus and Coordination

### Avoid Simple Majority Voting
Simple voting treats hallucinations from weak reasoning as equal to sound reasoning. Multi-agent discussions can devolve into consensus on false premises.

### Use Debate Protocols Instead
Require agents to critique each other's outputs over multiple rounds. Adversarial critique yields higher accuracy on complex reasoning than collaborative consensus. Structure as separate stages: initial work, critique, revision.

### Monitor for Behavioral Triggers
- **Stall:** No progress between rounds → escalate
- **Sycophancy:** Mimicking answers without unique reasoning → require evidence
- **Divergence:** Moving away from original objective → re-anchor to task

## Failure Modes

| Failure | Symptom | Mitigation |
|---------|---------|------------|
| Supervisor bottleneck | Supervisor context saturation | File-based checkpointing, output constraints (distilled summaries only) |
| Coordination overhead | Token waste on inter-agent messages | Minimize communication, batch results, use structured file formats |
| Divergence | Agents pursue different goals | Clear per-agent objective boundaries, convergence checks, iteration limits |
| Error propagation | Downstream agents consume bad upstream output | Validate outputs before passing, retry logic, graceful degradation |

## Design Guidelines

1. Design for context isolation as the primary benefit — not role simulation
2. Choose architecture by coordination needs, not organizational metaphor
3. Default to filesystem-based inter-agent communication
4. Implement explicit handoff protocols with clear state passing
5. Use critique/debate for consensus, not simple majority voting
6. Set iteration limits on all agent execution
7. Validate outputs before passing between agents
8. Start simple — add multi-agent complexity only when single-agent fails

## Memory and State Management

### Working Memory (context window)
Immediate access, volatile. Keep only active information; summarize completed work.

### Session Memory (files)
Created per session: task lists, intermediate results, decision logs. Persists for session duration.

### Long-Term Memory (CLAUDE.md, memory files)
Cross-session: project context, structured knowledge in markdown or JSON.

### Patterns
- **Handoff files:** Agent A writes state, Agent B reads and continues
- **Result aggregation:** Multiple agents write to separate files, supervisor reads all
- **Progress tracking:** Shared task list updated by all agents

## Design Decisions

### Why filesystem-as-memory (not vector stores or graph databases)
Filesystem-based inter-agent communication is transparent (anyone can read the files), debuggable (state is inspectable), and requires zero infrastructure. Vector stores and knowledge graphs add complexity that is rarely justified for agent coordination. The filesystem is the coordination primitive; structured file formats (JSON, YAML, Markdown) provide the query capability needed for most patterns.

### Why supervisor by default (not swarm)
The supervisor pattern is the simplest to implement, debug, and reason about. It provides clear error boundaries and explicit control flow. Swarm patterns should only be adopted when the task genuinely requires emergent behaviors that cannot be anticipated upfront. Most real-world agent tasks benefit from central coordination.
