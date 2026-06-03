# Segmented Execution Template

This template is used for Strategy B: Autonomous Segmented Execution. It separates the plan into blocks between `checkpoint:human-verify` markers.

## Execution Mechanism

1. **Parse plan into segments** — identify blocks separated by checkpoints.
2. **For each segment**:
   - **Spawn worker subagent** (tp-global-implementer) to execute the block.
   - **Worker requirements**:
     - General-purpose subagent with read, write, search, and shell command access.
     - Worker writes implementation results to `.principled/scratch/{plan-id}-execution.md`.
     - Worker includes: files modified, verification results, any deviations detected.
   - **Orchestrator self-verifies** checkpoint conditions:
     - Run all verify commands from the plan's task definitions.
     - If verify commands don't exist, use automated checks: file existence, test pass rate, lint status, build success.
     - **PASS** → log verification in SUMMARY.md, proceed to next segment.
     - **FAIL** → spawn tp-critic subagent to diagnose, then fix and re-verify (max 2 fix attempts).
   - **Status update**: "Segment [N] complete — [verification result]"
3. **Aggregate all segment results** into the final SUMMARY.md.
4. **Update ROADMAP.md** and **Commit** the changes.

## Verification Rules
- Run `!npm test` or equivalent for every task with a verify command.
- Use `!curl` for health checks.
- If self-verification fails after 2 fix attempts: log remaining issues in SUMMARY.md as "Known Limitations" and proceed to the next segment.
