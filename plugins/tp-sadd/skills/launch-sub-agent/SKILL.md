---
name: launch-sub-agent
description: "Launch focused sub-agent with automatic model selection based on task complexity, Zero-shot CoT reasoning, and mandatory self-critique verification"
when_to_use: |
  When user says 'launch sub-agent', 'dispatch agent', 'delegate to agent', 'spawn agent', 'send to background', 'run this in a subagent'. IMMEDIATELY when user wants to delegate work with optimal model selection. FIRST when task requires context isolation and self-critique verification.
argument-hint: Task description and optional model/agent/output flags
---

## Decision Router

IF task is trivial lookup or simple transformation → Haiku (cost-effective)
IF task requires architecture, novel problem-solving, or critical decisions → Opus (maximum reasoning)
IF task is non-complex but output is extensive → Sonnet (balanced capability and cost)
IF task matches specialized domain (code, research, architecture) → Select matching agent type
IF default/uncertain → Opus (quality over cost)

# launch-sub-agent

Launch a focused sub-agent with intelligent model selection and mandatory verification.

## Policy: Why This Pattern

Context isolation is the primary benefit. Each sub-agent operates in a clean context window focused on its specific task. Evaluating work within the same context that produced it creates confirmation bias.

**The pattern has three mandatory components:**
1. Zero-shot Chain-of-Thought reasoning prefix (think before acting)
2. Task body with scope and constraints
3. Self-critique verification suffix (verify before completing)

## Mechanism: Five-Phase Dispatch

### Phase 1: Task Analysis

Analyze systematically before dispatching:

```
1. Task Type: Code implementation / Research / Documentation / Review / Architecture / Testing / Simple transformation
2. Complexity: High (architecture, novel problems) / Medium (standard patterns) / Low (simple, well-defined)
3. Output Size: Large (multiple files) / Medium (single feature) / Small (quick answer)
4. Domain Match: Does task align with specialized agent profile?
```

### Phase 2: Model Selection

| Task Profile | Model | Rationale |
|--------------|-------|----------|
| Complex reasoning (architecture, design, critical) | Opus | Maximum capability |
| Specialized domain + complex | Opus + agent | Expertise + reasoning |
| Simple and short | Haiku | Fast, cost-effective |
| Long output but not complex | Sonnet | Balanced |
| Default/uncertain | Opus | Quality over cost |

**Decision tree:**
```
Is task COMPLEX?
├── YES → Opus
│         └── Match specialized domain? → Include agent prompt
└── NO → Is task SIMPLE + SHORT?
          ├── YES → Haiku
          └── NO → Sonnet (long output, not complex)
                  └── Otherwise → Opus (default)
```

### Phase 3: Specialized Agent Matching

When task matches a specialized domain, incorporate relevant agent instructions after the CoT prefix.

**Use specialized agents when:**
- Domain expertise clearly improves quality
- Task clearly fits a known pattern (developer, researcher, architect)

**Skip when:**
- Task is trivial (specialization overhead not justified)
- No matching agent available

### Phase 4: Construct Prompt

Build with three mandatory sections:

**CoT Prefix (first):**
```
## Reasoning Approach

Before taking any action, think systematically:

1. What is the core objective? What are the explicit requirements?
2. What are the major components? What order should I tackle them?
3. What assumptions am I making? What edge cases might exist?
4. Does my approach address all requirements? Is there a simpler way?
```

**Task Body:**
```
<task>{task description}</task>
<constraints>{any constraints from context}</constraints>
<context>{relevant files, patterns, requirements}</context>
<output>{expected deliverable format and location}</output>
```

**Self-Critique Suffix (last):**
```
## Self-Critique (MANDATORY)

Before completing, verify your work:

1. Generate 5 verification questions specific to this task
2. Answer each with specific evidence from your solution
3. If ANY gap found: STOP, FIX, RE-VERIFY, DOCUMENT

Do not submit until all verification questions have satisfactory answers.
```

### Phase 5: Dispatch

Use Task tool with selected model. Pass only context relevant to this task (not entire conversation history).

## Examples

| Input | Analysis | Selection |
|-------|----------|-----------|
| "Design caching strategy for 10k req/s" | Architecture, High complexity | Opus + architect agent |
| "Update README with --verbose flag" | Documentation, simple | Haiku |
| "Implement pagination for /users" | Code, medium complexity | Sonnet + developer agent |
| "Research auth options (OAuth2, SAML, passwordless)" | Research, high complexity | Opus + researcher agent |

## Key Principles

- Self-critique loop is non-negotiable
- Sub-agents must answer verification questions before completing
- Context isolation: pass only relevant context, not conversation history
- When in doubt, use Opus (quality over cost)