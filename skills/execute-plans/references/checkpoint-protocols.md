# Checkpoint Protocols

Templates and flows for each checkpoint type.

---

## Template: checkpoint:human-verify

**Purpose:** Verification gate requiring explicit user confirmation before proceeding.

**Protocol flow:**

```
1. Orchestrator loads verification criteria from plan
2. Orchestrator executes the work up to this checkpoint
3. Present verification prompt to user:

════════════════════════════════════
Verification Required: [Task Name]
════════════════════════════════════

Criteria:
[Criteria 1]
[Criteria 2]

Files modified:
- [file list]

What's next?
1. Confirm - verification passed, proceed
2. Reject  - verification failed, address feedback
3. Stop    - pause execution, investigate
════════════════════════════════════
```

**On-user-action responses:**

Present these structured options to the user and wait for their selection:

For checkpoint:human-verify:
- option A: "Approved - continue" (user confirms verification passed)
- option B: "Issues found - see description" (user rejects verification)
- option C: "Stop execution" (user halts for investigation)

**On user "Approved - continue":**
- Record: `{ checkpoint: "verify", status: "passed", timestamp: ISO8601 }`
- Proceed to next segment/task

**On user "Issues found - see description":**
- Follow Verification Failure Gate protocol
- Present specific failure details
- Await decision: Retry / Skip / Stop

**On user "Stop execution":**
- Halt execution
- Create partial SUMMARY.md with status
- Surface to user for investigation

---

## Template: checkpoint:decision

**Purpose:** User must choose between alternative paths or directions.

**Protocol flow:**

```
1. Orchestrator identifies decision point
2. Orchestrator gathers context for each option
3. Present decision prompt to user:

════════════════════════════════════
Decision Required: [Decision Name]
════════════════════════════════════

Current task: [task name]
Decision needed: [what to choose]

Option A: [description]
  - Impact: [impact description]
  - Risk: [risk level]

Option B: [description]
  - Impact: [impact description]
  - Risk: [risk level]

Context:
[relevant context gathered]

What's next?
1. Option A
2. Option B
3. Different approach
4. Defer
════════════════════════════════════
```

**On-user-action responses:**

Present these structured options to the user and wait for their selection:

For checkpoint:decision:
- option A: "Option A" (execute path A)
- option B: "Option B" (execute path B)
- option C: "Different approach" (user proposes alternative)
- option D: "Defer" (halt for later decision)

**On user selection:**
- Record: `{ checkpoint: "decision", choice: "[A|B|different|defer]", timestamp: ISO8601 }`
- Execute the selected path
- Continue to next task

**On "Defer":**
- Record: `{ checkpoint: "decision", choice: "deferred", timestamp: ISO8601 }`
- Halt execution at this point
- Surface to user for later decision

---

## Template: checkpoint:human-action

**Purpose:** External system state change required before execution can continue.

**Protocol flow:**

```
1. Orchestrator identifies required external action
2. Present action prompt to user:

════════════════════════════════════
Action Required: [Action Name]
════════════════════════════════════

Current task: [task name]
Blocked by: [what needs to happen]

Required action:
[Specific action to perform]

Example command:
[example if applicable]

Verification:
[how to verify the action completed]

Type "done" when completed.
════════════════════════════════════
```

**On-user-action responses:**

Present these structured options to the user and wait for their selection:

For checkpoint:human-action:
- option A: "Action completed" (verification passed)
- option B: "Action failed - see details" (verification failed)
- option C: "Skip this step" (proceed without this action)

**After user confirms "Action completed":**
- Run verification command
- If verified: Record `{ checkpoint: "human-action", status: "completed", timestamp: ISO8601 }`, proceed
- If not verified: Present retry guidance, wait again

**Authentication gates use the same protocol** but document as "Authentication Gate" not "checkpoint:human-action".

---

## Resume Signal Handling

**When resuming after checkpoint completion:**

When the user types "approved" or selects "continue", execution resumes automatically. The structured options handle the input routing — no special parsing needed.

| Checkpoint Type | Resume Action |
|----------------|--------------|
| `checkpoint:human-verify` | Proceed to next segment, verification already recorded |
| `checkpoint:decision` | Execute selected path |
| `checkpoint:human-action` | Verify state change, then proceed |

**Resume format in orchestrator state:**

```json
{
  "last_checkpoint": {
    "type": "human-verify|decision|human-action",
    "id": "checkpoint-id",
    "status": "passed|completed|selected",
    "timestamp": "ISO8601",
    "response": "user response details"
  },
  "resume_from": "next-segment-id"
}
```

**Partial context recovery:**
- Checkpoint state is sufficient for resume
- No need to reload full plan context
- Reconstruct execution state from checkpoint record + next segment

---

## Checkpoint Metadata

Each checkpoint in PLAN.md should have:

```markdown
type="checkpoint:human-verify"
id="verify-01"
label="Verify build output"
criteria:
  - Build completes without errors
  - Generated files exist
  - Tests pass
```

**Fields:**
- `type`: checkpoint:human-verify | checkpoint:decision | checkpoint:human-action
- `id`: Unique identifier for tracking
- `label`: Human-readable name
- `criteria` / `options` / `action`: Type-specific payload