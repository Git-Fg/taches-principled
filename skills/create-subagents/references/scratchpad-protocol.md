# Centralized Scratchpad Protocol

## When to Use

When a plan involves subagent fan-out for exploration/investigation, OR when multiple agents need to share findings without telephone-game degradation.

## Why

The telephone game degrades quality by ~50% when orchestrators synthesize subagent reports without source access. Each paraphrasing pass loses nuance and introduces error.

Direct scratchpad access eliminates paraphrase drift entirely.

## Protocol

### Step 1: Before Spawning Subagents

1. **Read** existing scratchpad: `.principled/scratch/{topic}.md`
2. **Write** current questions and context to that scratchpad
3. **Verify** subagent has Write tool access

### Step 2: Subagent Execution

Each subagent MUST:
1. Read scratchpad for any prior findings
2. Write findings to scratchpad in structured format before returning
3. Never pass findings through orchestrator synthesis — write directly to scratchpad

```markdown
## Findings: {subagent-name}

### Scope
{what this agent covered}

### Key Findings
{concrete discoveries}

### Doubts
{things that are unclear or might be wrong}

### Suggestions
{recommended next steps or areas to investigate}
```

### Step 3: After Subagents Return

1. **Read** scratchpad BEFORE synthesizing
2. **Merge** findings from scratchpad directly
3. **Update** scratchpad with synthesis conclusions

## Tool Requirements (NON-OPTIONAL)

For investigation/exploration subagents:
- **NEVER** use "native" Explore subagents (Haiku, read-only) — cannot write findings
- **REQUIRED** minimum: `[Read, Write, Grep, Glob, Bash]`

## Anti-Pattern: Native Explore for Investigation

**❌ Forbidden:**
```
Agent(description = "Explore codebase", subagentType = "Explore")
```

**Why:** Native Explore agents are Haiku-based and read-only. They cannot persist findings to scratchpad. Findings must be written directly, not passed through summarization.

**✅ Correct:**
```
Agent(description = "Explore codebase, write findings to scratchpad",
      subagentType = "general-purpose",
      tools = ["Read", "Write", "Grep", "Glob", "Bash"])
```

## Scratchpad Location

`.principled/scratch/{topic}.md`

Create the scratchpad directory if it doesn't exist:
```bash
mkdir -p .principled/scratch
```

## Integration with Explorer Subagent Protocol

The scratchpad protocol is the mechanism. The Explorer Subagent Protocol (in the skill SKILL.md) is the policy that requires it.

Both must be applied together:
- Explorer Subagent Protocol = "you MUST use scratchpad for exploration"
- Scratchpad Protocol = "here's HOW to use scratchpad correctly"
