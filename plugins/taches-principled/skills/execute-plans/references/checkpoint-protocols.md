# Checkpoint Protocols

Protocols for handling checkpoint types autonomously. Checkpoints are segmentation markers, not interaction points.

## Template: checkpoint:human-verify

**Purpose:** Verification gate that the orchestrator resolves autonomously.

**Protocol flow:**

```
1. Orchestrator loads verification criteria from plan
2. Orchestrator executes the work up to this checkpoint
3. Spawn verifier subagent with checkpoint criteria
4. Verifier runs automated checks (tests, lint, file state)
5. Returns structured pass/fail with evidence

IF pass → record { checkpoint: "verify", status: "passed" }, continue to next segment
IF fail → orchestrator fixes, spawns verifier again, retries
After 2 fix cycles → log remaining issues, continue
```

**Key rule:** Never present verification to the user. Verification is a subagent-spawn cycle, not a presentation gate.

---

## Template: checkpoint:decision

**Purpose:** Orchestrator resolves autonomously through heuristic analysis.

**Protocol flow:**

```
1. Orchestrator identifies decision point
2. Gather context for each option
3. Apply heuristics in order:
   a. Default to simplest path (fewest files, least complexity)
   b. Follow plan recommendations if specified
   c. Prefer reversible choices over irreversible ones
   d. Follow existing project patterns over novel approaches
4. Select option, document rationale
5. Record: { checkpoint: "decision", choice, rationale }
6. Execute selected path, continue
```

**Heuristic rules:**
- Simplest path wins unless evidence favors otherwise
- Reversible > irreversible (can undo if wrong)
- Project patterns > novel approaches (consistency matters more than optimization)
- When genuinely ambiguous: pick the option with fastest verification feedback (testability tiebreaker)

**Key rule:** Never ask the user. Every decision has a heuristic resolution path.

---

## Template: checkpoint:human-action

**Purpose:** External action needed — orchestrator attempts automation, logs if impossible.

**Protocol flow:**

```
1. Check for CLI/API alternative first
2. If CLI alternative exists: execute it, verify, continue
3. If no CLI/API alternative:
   a. Log the manual step to SUMMARY.md as "unavoidable manual gate"
   b. Use placeholder/simulated value if needed
   c. Continue with remaining work
   d. Report gate in final status
```

**Key rule:** Never pause execution. Log the gate, continue with what's available.

---

## Resume Signal Handling

**When resuming after checkpoint completion:**

Checkpoint state is sufficient for resume — no reload needed.

| Checkpoint Type | Resume Action |
|----------------|--------------|
| `checkpoint:human-verify` | Proceed to next segment, verification already recorded |
| `checkpoint:decision` | Continue on selected path |
| `checkpoint:human-action` | If gate was logged, continue with placeholder; if completed, proceed normally |

**Partial context recovery:**
- Checkpoint state is sufficient for resume
- Reconstruct execution state from checkpoint record + next segment

---

## Checkpoint Metadata

Each checkpoint in PLAN.md uses the inline `Checkpoint:` field syntax:

```markdown
### Task 3: Deploy to production
Files: .env.production
Action: Run deployment via CLI, verify health endpoint
Verify: `curl https://api.production.com/health` returns 200
Done: Production deployed and healthy
Checkpoint: checkpoint:human-verify  # Self-verified by exec strategy B
```

**Fields:**
- `type`: checkpoint:human-verify | checkpoint:decision | checkpoint:human-action
- `id`: Unique identifier for tracking (optional)
- `criteria` / `options` / `action`: Type-specific payload

IF designing checkpoint syntax → BEFORE writing checkpoints read the plan-format reference documentation for full checkpoint syntax details.
