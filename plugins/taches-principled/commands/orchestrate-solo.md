---
name: orchestrate-solo
skill: subagent-orchestration
description: Solo (lightweight) orchestration — no subagent fan-out, no critic-revise loop. Use for small tasks, exploratory work, or when protocol overhead exceeds task complexity.
argument-hint: [task to orchestrate]
---

$ARGUMENTS

Execute the task directly in the main context, without subagent fan-out:

1. **No subagents.** Do NOT spawn `tp-explorer`, `tp-critic`, `tp-global-implementer`, or any other subagent.
2. **No centralized scratchpad.** Read files and modify files directly via Read/Write/Edit/Bash tools.
3. **No critic-revise loop.** Self-verify against the task's success criteria; no `MAX_ITERATIONS` cycle.
4. **No parallel workers.** Execute tasks sequentially in the main context.
5. **Apply the same verification gates** as the full orchestration path (verify commands from the plan, success criteria, file state checks), but in main context rather than via subagent.
6. **Document decisions inline** in the commit message or handoff file rather than via a scratchpad.

**When to use solo mode:**
- Task touches ≤ 3 files AND has no checkpoint types
- Task is exploratory (research, spike, prototype)
- User explicitly passes `--solo` or `--lightweight`
- Context budget is tight (&lt; 30% remaining) and the cost of subagent setup exceeds the task complexity

**When NOT to use solo mode:**
- Task touches &gt; 5 files or has cross-cutting concerns
- Task has `checkpoint:human-verify` or `checkpoint:decision` markers
- High-stakes code (auth, payments, data integrity) — always use full orchestration
- User says "thorough" / "careful" / "with critique"
