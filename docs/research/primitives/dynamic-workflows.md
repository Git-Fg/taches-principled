# Dynamic Workflows

**Canonical source:** https://code.claude.com/docs/en/workflows
**Status:** Research preview (launched May 28, 2026)
**Requires:** Claude Code v2.1.154+. Workflow availability depends on plan, but the **runtime itself is local** — it calls the configured model API. This means it works against a custom Claude-compatible endpoint (e.g., minimax / MiniMax / MM-X) as long as that endpoint supports the API features the workflow's agents use (structured output, schema enforcement, sufficient context window).

## One-sentence definition

A workflow is a **JavaScript script that Claude writes for your task** and the runtime executes in the background, orchestrating up to 1,000 subagents (16 concurrent) with intermediate state in script variables instead of the conversation context.

## Why this changes the game

With subagents and skills, **Claude is the orchestrator** — it decides turn by turn what to spawn or assign next, every result lands in the context window.

With a workflow, **the script is the orchestrator** — the loop, branching, and intermediate results live in the script. Claude's conversation only holds the final answer.

This makes possible what wasn't before:
- **Repeatable orchestration** — the same script runs the same fan-out shape every time
- **Adversarial quality patterns** — N independent agents verify each finding before it's reported
- **Tens to hundreds of agents** in a single run, beyond what one conversation can coordinate

## Comparison the docs make explicit

| | Subagents | Skills | Workflows |
|---|---|---|---|
| What it is | A worker Claude spawns | Instructions Claude follows | A script the runtime executes |
| Who decides what runs next | Claude, turn by turn | Claude, following the prompt | The script |
| Intermediate results live in | Claude's context | Claude's context | Script variables |
| Scale | A few per turn | Same as subagents | Dozens to hundreds per run |
| Interruption | Restarts the turn | Restarts the turn | Resumable in the same session |

## How to start one

Three entry points:

1. **Keyword trigger** — include the word `workflow` anywhere in a prompt
2. **Bundled command** — `/deep-research <question>` is the only built-in workflow today
3. **Ultracode mode** — `/effort ultracode` sets effort to `xhigh` and lets Claude *decide* per task whether to plan a workflow

Workflows you save become `/<name>` commands in `.claude/workflows/` (project) or `~/.claude/workflows/` (personal).

## Script API surface (the part that matters for our skills)

```javascript
export const meta = {
  name: 'find-flaky-tests',
  description: 'Find flaky tests and propose fixes',
  phases: [
    { title: 'Scan', detail: 'grep test logs for retries' },
    { title: 'Fix', detail: 'one agent per flaky test' },
  ],
}
```

The `meta` block is a pure literal — no variables, calls, spreads, or template interpolation. Required: `name`, `description`. Optional: `whenToUse`, `phases`, `model`.

**Script hooks:**

| Hook | Purpose |
|---|---|
| `agent(prompt, opts?)` | Spawn a subagent. With `schema:` JSON Schema, the agent is forced to call a StructuredOutput tool and returns the validated object. Other opts: `label`, `phase`, `model`, `isolation: 'worktree'`, `agentType` |
| `pipeline(items, stage1, stage2, ...)` | Run each item through all stages independently, NO barrier between stages. Item A can be in stage 3 while item B is still in stage 1. **The default for multi-stage work.** |
| `parallel(thunks)` | Run concurrently with a barrier — awaits all before returning. Use only when you genuinely need all prior-stage results together. |
| `log(message)` | Narrator line above the progress tree |
| `phase(title)` | Group subsequent `agent()` calls under a title |
| `args` | The value passed as Workflow `args` input, verbatim |
| `budget` | `{total, spent(), remaining()}` — token target shared across the turn; hard ceiling |
| `workflow(name, args?)` | Run another workflow inline as a sub-step (one level deep only) |

## The runtime constraints

| Constraint | Reason |
|---|---|
| No mid-run user input | Only agent permission prompts can pause; for sign-off between stages, use multiple workflows |
| No direct filesystem/shell access from the workflow itself | Agents read, write, run commands; the script coordinates |
| Up to 16 concurrent agents (fewer on low-CPU machines) | Local resource bound |
| 1,000 agents total per run | Runaway-loop guard |

## Quality patterns the doc names

The `Workflow` tool definition itself enumerates them — each is a composable shape:

- **Adversarial verify** — spawn N independent skeptics per finding, each prompted to refute. Kill if majority refute.
- **Perspective-diverse verify** — give each verifier a distinct lens (correctness, security, perf, reproduces?) — diversity catches what redundancy can't.
- **Judge panel** — generate N independent attempts from different angles, score with parallel judges, synthesize the winner while grafting best ideas from runners-up.
- **Loop-until-dry** — for unknown-size discovery (bugs, issues), keep spawning finders until K consecutive rounds return nothing new. Simple `while count < N` misses the tail.
- **Multi-modal sweep** — parallel agents each searching a different way (by-container, by-content, by-entity, by-time).
- **Completeness critic** — a final agent that asks "what's missing — modality not run, claim unverified, source unread?"

## Cost & control

- Workflows count toward your configured API usage like any other session
- Permission mode controls the launch prompt only; subagents inside always run in `acceptEdits` with the session's tool allowlist
- File edits inside the workflow are auto-approved
- Disable per-session: `/config` → Dynamic workflows off, or `disableWorkflows: true` in settings, or `CLAUDE_CODE_DISABLE_WORKFLOWS=1`

## Resume semantics

- Every run writes its script to `~/.claude/projects/.../wf_<id>.js`
- Same script + same args → 100% cache hit on resume (`resumeFromRunId`)
- `Date.now()` / `Math.random()` / argless `new Date()` throw inside scripts — they'd break resume determinism. Pass timestamps via `args`.

## Custom-endpoint considerations

The workflow runtime calls the model API the same way an interactive session does — meaning a custom Claude-compatible endpoint should work transparently, **but** verify three things before relying on it for production workflows:

1. **Structured-output enforcement** — workflows use `schema:` opts that force the agent to call a StructuredOutput tool. The endpoint must support tool use with schema enforcement, not just text generation.
2. **xhigh effort support** — `ultracode` mode requires the model to support xhigh reasoning effort. Custom endpoints that don't expose the effort field will fall back to the model's default, which may or may not be enough for the planner step.
3. **Concurrent request limit** — the runtime caps concurrent agents at 16 by default. A custom endpoint with a lower rate limit will become the bottleneck; reduce concurrency in the script or in endpoint settings to match.

## Resources beyond the doc

- Companion bundled workflow: `/deep-research` — fans out searches, fetches sources, votes on each claim, returns a cited report
- The script file Claude wrote is readable: open `~/.claude/projects/<session>/<runId>.js` to diff between runs or hand-edit and relaunch
