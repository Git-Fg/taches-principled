# Context Efficiency

Token budgets and optimization guidance for execution phases.

---

## Token Budget Targets

**Strategy A: Fully Autonomous**
- Subagent workspace: 25,000 tokens
- Orchestrator overhead: 2,500-3,000 tokens (~10-15%)
- Milestone reviews: ~500 tokens (~2% per review)
- Total target: <30% overhead (including workers + reviews)

**Strategy B: Segmented**
- Per-segment subagent: 20,000 tokens
- Orchestrator (checkpoint management + state): 10,000 tokens
- Checkpoint verification context: 5,000 tokens
- Total per segment: 35,000 tokens max

**Strategy C: Sequential**
- Domain context (plan files, codebase): 15,000 tokens
- Execution context (deviation rules, execute-phase): 7,000 tokens
- Orchestrator workspace: 10,000 tokens
- User interaction: 3,000 tokens
- Total: 35,000 tokens max

---

## File Loading Strategy

**During execution, load files strategically:**

| Phase | Files to Load | Read Mode |
|-------|--------------|-----------|
| Initial context | Plan + execution_context only | Full |
| Task execution | Only files in `<context>` section | Full |
| Verification | Files modified by tasks | Head (first 50 lines) |
| Deviation handling | Specific file with issue | Full |

**Context section principle:** Load only what the plan's `<context>` section explicitly names. Do not pre-load related files.

**Head read usage:**
- Quick verification (file exists, basic structure)
- Checking import statements
- Verifying compilation
- Not for understanding logic (use full read for that)

---

## When to Use Head vs Full Read

**Use head read (50 lines) when:**
- Verifying a file was created/modified
- Checking import completeness
- Confirming build artifacts exist
- Quick state checks

**Use full read when:**
- Understanding logic to modify
- Debugging deviation issues
- Analyzing error traces
- Making architectural decisions

If you need to understand, use full read directly. If you need to verify existence, head read.

---

## Context Monitoring Thresholds

**During execution, monitor context usage:**

| Threshold | Remaining | Action |
|-----------|-----------|--------|
| Green | >25% | Normal operation |
| Yellow | 15-25% | Warning: flush completed segments, avoid loading new files |
| Red | 10-15% | Pause: aggregate partial progress, create intermediate summary |
| Critical | <10% | STOP: create partial SUMMARY.md, surface to user |

**Monitoring approach:**
- Check context estimate at each task boundary
- Before loading new files, verify budget allows
- When approaching yellow, stop loading non-essential files

---

## Subagent Context Isolation

**Principle:** Each subagent operates in isolation with complete context for its segment only.

**Isolation requirements:**
- No shared conversation history between segments
- Subagent receives: plan summary, segment tasks, deviation rules, output format
- Subagent produces: tasks completed, files modified, deviations, checkpoint status
- Orchestrator aggregates results for Summary creation

**What subagent context MUST include:**
1. Plan summary (what this plan accomplishes)
2. Segment tasks (what this subagent executes)
3. Deviation rules (full reference, not summary)
4. Success criteria (verbatim from plan)
5. Rollback procedure (one-command revert)
6. Output format (SUMMARY.md structure)

**What subagent context must NOT include:**
- Other segments' outputs
- Orchestrator reasoning
- Other subagent artifacts
- Parent conversation history

**Why isolation matters:**
- Subagent failures don't cascade
- Each segment is independently retryable
- Context stays bounded regardless of plan length
- Parallel segments don't interfere