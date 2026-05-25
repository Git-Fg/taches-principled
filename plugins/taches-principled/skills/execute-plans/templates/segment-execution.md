# Segment Execution Template

Subagent prompt for executing a segment between checkpoints.

---

## Segment Definition

A **segment** is an autonomous block of tasks between two checkpoints.

```
[Checkpoint A] → [Segment 1: Tasks 1-3] → [Checkpoint B] → [Segment 2: Tasks 4-6] → [Checkpoint C]
```

Each segment executes independently. Subagent does not create SUMMARY or commit.

---

## Subagent Prompt Structure

```
Execute segment {N} from {plan_path}.

## Segment Tasks
[Tasks from plan, limited to this segment]

## Segment Goals
[What this segment accomplishes]

## Deviation Rules
{Include full deviation-rules.md content}

## Checkpoint Context
Previous checkpoint: {prev_checkpoint_id} ({status})
Next checkpoint: {next_checkpoint_id} ({type})

## Rollback for this segment
{one-command undo for files modified by this segment}

## Output Format

Report to orchestrator:

# Segment {N} Completion Report

## Tasks Executed
- [Task X]: [outcome]
- [Task Y]: [outcome]

## Files Modified
- [absolute paths]

## Deviations
- Auto-fixed: [list]
- Logged: [list]

## Checkpoint Status
{next_checkpoint_id}: ready for verification

## Verification Artifacts
[Any files needed for checkpoint verification]
```

---

## What to Capture for Aggregation

Orchestrator collects from each segment:
1. Tasks executed (with outcomes)
2. Files modified (absolute paths)
3. Deviations encountered
4. Checkpoint verification artifacts
5. Any state needed for next segment

**Do NOT include in segment output:**
- SUMMARY.md (orchestrator creates this after all segments complete)
- Commit information (orchestrator commits after all segments)
- ROADMAP updates (orchestrator handles)

**Subagent does not create SUMMARY or commit.**

---

## Partial Completion Handling

**If segment fails mid-execution:**

1. Report failure to orchestrator:
```
Segment {N} failed at task {X}.

Error: [error description]
Completed tasks: [list]
Modified files: [list]

How to proceed?
1. Retry segment from task {X}
2. Skip segment, continue to checkpoint
3. Abort plan execution
```

2. Orchestrator presents options to user
3. User decides; orchestrator issues retry (max 2 retries) or continue

**If checkpoint verification fails:**

1. Present failure gate:
```
Verification failed for checkpoint {id}.

Expected: [criteria]
Actual: [what happened]

Options:
1. Retry - fix issues, retry verification
2. Skip   - mark as incomplete, continue
3. Stop   - pause execution, investigate
```

2. Orchestrator waits for user decision

---

## Checkpoint Handoff Format

**From segment to checkpoint:**

```
Segment {N} artifacts for checkpoint {id}:

Verification ready:
- [artifact 1]
- [artifact 2]

Files modified this segment:
- /path/to/file1
- /path/to/file2

State summary:
[brief description of system state]
```

**From checkpoint to next segment:**

```
Checkpoint {id} passed.

Resume context:
- Decision/verification recorded
- State: [relevant state]

Segment {N+1} can proceed.
```

---

## Context Budget

Segment subagent receives:
- Segment tasks: ~500 tokens
- Deviation rules: ~1,500 tokens
- Checkpoint context: ~300 tokens
- Output format: ~400 tokens
- **Total overhead: ~2,700 tokens**

Segment subagent workspace (20,000 tokens):
- Implementation code for segment tasks only
- Verification for segment
- No need for full plan context

---

## Segment Boundaries

**Starting a segment:**
- Load only files needed for segment tasks
- Do not load files from previous segments
- Do not pre-load files for future segments

**Ending a segment:**
- Leave system in clean state
- All segment tasks verified complete
- Artifacts ready for checkpoint verification
- No pending changes that could leak to next segment

**Inter-segment isolation:**
- Each segment subagent starts fresh
- No shared state between segments
- Orchestrator owns all cross-segment state

---

## Milestone Self-Review (within segment)

At segment midpoint (every 2-3 tasks), trigger a self-review:

**Spawn the reviewer** using `{baseDir}/agents/critic.md` as the spawn prompt. Fill the placeholders with the current segment state, files modified so far, milestone number, and review task.

The reviewer returns structured output with blocking/non-blocking classification. If blocking issues are found, fix before proceeding to next task.

**Do not skip the review** even if tasks appear to be running cleanly. Integration issues often surface at milestone boundaries.

---

**Subagent spawn footer (append to every segment prompt):**

You are a subagent executing a delegated task. Your context starts fresh — you have no access to prior conversation or other subagents' outputs. When complete, return your full results (file paths, findings, and any artifacts) to the orchestrator in structured form. If you encounter anything unexpected or have any question or doubt, stop and report back with what you found and what is unclear. Do not proceed silently on assumptions.