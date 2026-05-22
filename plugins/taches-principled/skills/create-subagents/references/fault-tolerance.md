# Fault Tolerance: Circuit Breakers and Checkpoints

## Sections
- [Why Fault Tolerance Matters](#why-fault-tolerance-matters)
- [Circuit Breaker Pattern](#circuit-breaker-pattern)
- [Checkpoint and Resume](#checkpoint-and-resume)
- [Exponential Backoff](#exponential-backoff)
- [Idempotent Operations](#idempotent-operations)
- [Implementation Reference](#implementation-reference)

---

Multi-agent systems fail differently than single-agent systems. A single agent fails completely or succeeds. A multi-agent system can fail partially — one agent goes wrong while others continue, errors cascade through the pipeline, and the system produces confident-looking wrong output.

Designing for failure is not optional — it is mandatory.

---

## Why Fault Tolerance Matters

**Three failure modes unique to multi-agent systems:**

| Failure Mode | What Happens | Why It's Dangerous |
|--------------|--------------|---------------------|
| **Cascade failure** | One agent's error becomes another's input | Hallucinations compound |
| **Silent degradation** | Supervisor loses fidelity through summarization | Wrong answers that look confident |
| **Orphan work** | A subagent produces output that never gets used | Wasted tokens, missing context |

**Single-agent safety:** If an agent fails, you see the failure immediately. The error is visible in the output.

**Multi-agent danger:** If Agent A hallucinates and passes the hallucination to Agent B, Agent B may treat it as fact — and compound the error. The final output looks coherent but is wrong from the start. The error is invisible until someone catches it manually.

---

## Circuit Breaker Pattern

**Purpose:** Prevent cascading failures by detecting repeated agent failures and routing around them.

**The mechanism:**
1. Track failure count per agent
2. When failure count exceeds threshold, "open the circuit" — disable that agent
3. Future tasks route to alternative agents or fail fast
4. After cooldown period, allow retry

**Why not just retry?** Retrying a failing agent with the same context and same inputs produces the same failure. The circuit breaker recognizes patterns: if Agent X has failed 3 times, Agent X is likely broken, not just unlucky. Don't keep throwing work at it.

**Implementation:**

```python
class AgentCircuitBreaker:
    def __init__(self, max_retries=3, cooldown_seconds=60):
        self.max_retries = max_retries
        self.cooldown_seconds = cooldown_seconds
        self.failure_counts: Dict[str, int] = {}
        self.circuit_open_at: Dict[str, float] = {}  # timestamp

    def is_open(self, agent_id: str) -> bool:
        """Check if circuit is open (agent temporarily disabled)."""
        if agent_id not in self.circuit_open_at:
            return False
        if time.time() - self.circuit_open_at[agent_id] > self.cooldown_seconds:
            # Cooldown expired, allow retry
            del self.circuit_open_at[agent_id]
            self.failure_counts[agent_id] = 0
            return False
        return True

    def record_failure(self, agent_id: str) -> None:
        """Record a failure and open circuit if threshold exceeded."""
        self.failure_counts[agent_id] = self.failure_counts.get(agent_id, 0) + 1
        if self.failure_counts[agent_id] > self.max_retries:
            self.circuit_open_at[agent_id] = time.time()

    def record_success(self, agent_id: str) -> None:
        """Reset failure count on successful task."""
        self.failure_counts[agent_id] = 0
        if agent_id in self.circuit_open_at:
            del self.circuit_open_at[agent_id]

    def handle_failure(self, agent_id: str, task_id: str) -> Dict[str, Any]:
        """Handle failure with retry or fallback routing."""
        self.record_failure(agent_id)
        if self.is_open(agent_id):
            return {
                "action": "fallback",
                "target": "alternative_agent",
                "reason": f"Circuit open for {agent_id}"
            }
        delay = min(2 ** self.failure_counts[agent_id], 60)
        return {
            "action": "retry",
            "delay": delay,
            "reason": f"Retry {self.failure_counts[agent_id]} with {delay}s backoff"
        }
```

---

## Checkpoint and Resume

**Purpose:** Persist workflow state to disk so that failures can be recovered without redoing completed work.

**The problem:** Long-running multi-agent workflows lose all progress on failure. If the supervisor crashes at step 8 of 10, steps 1-8 are wasted.

**The solution:** Periodic checkpointing. At defined milestones, persist complete state to disk. On failure, reload from checkpoint rather than restarting.

**Checkpoint state must include:**
1. Current workflow position (which step)
2. All completed task outputs
3. Agent states and readiness
4. Shared scratchpad contents
5. Context window summaries for each agent

**The CheckpointManager:**

```python
class CheckpointManager:
    def __init__(self, checkpoint_dir=".principled/scratch/checkpoints"):
        self.checkpoint_dir = Path(checkpoint_dir)
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)

    def save_checkpoint(self, workflow_id: str, step: int, state: Dict[str, Any]) -> None:
        """Save workflow state at milestone."""
        checkpoint = {
            "workflow_id": workflow_id,
            "step": step,
            "state": state,
            "timestamp": time.time()
        }
        path = self.checkpoint_dir / f"{workflow_id}_step{step}.json"
        with open(path, 'w') as f:
            json.dump(checkpoint, f)

    def load_checkpoint(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """Load most recent checkpoint for workflow."""
        checkpoints = sorted(
            self.checkpoint_dir.glob(f"{workflow_id}_step*.json"),
            key=lambda p: p.stat().st_mtime
        )
        if not checkpoints:
            return None
        with open(checkpoints[-1]) as f:
            return json.load(f)

    def get_latest_step(self, workflow_id: str) -> int:
        """Get the step number of the most recent checkpoint."""
        checkpoint = self.load_checkpoint(workflow_id)
        return checkpoint["step"] if checkpoint else 0
```

**Checkpoint protocol:**
```markdown
## Checkpoint Protocol

1. **Define milestones** in workflow design:
   - After each phase completion
   - Before risky operations
   - At natural boundary points

2. **Checkpoint before handoff:**
   - Save state before sending to next agent
   - Next agent verifies checkpoint exists before proceeding

3. **Resume on failure:**
   - Load checkpoint, restore state
   - Resume from last completed step, not from beginning
   - Notify user: "Resuming from step X, previous progress restored"
```

---

## Exponential Backoff

**Purpose:** Retry failed operations with increasing delays to avoid hammering a failing service or exacerbating cascade failures.

**The mechanism:** Each retry waits longer. First retry: 1 second. Second retry: 2 seconds. Third retry: 4 seconds. Maximum: 60 seconds.

**Why it works:** Many failures are transient. A service that's overwhelmed recovers faster if you give it space. Retrying immediately after a timeout just adds load to a system that's already struggling.

**Formula:** `delay = min(2 ** failure_count, 60)` seconds

| Failure Count | Delay |
|---------------|-------|
| 1 | 1 second |
| 2 | 2 seconds |
| 3 | 4 seconds |
| 4 | 8 seconds |
| 5 | 16 seconds |
| 6+ | 32-60 seconds (capped) |

**Anti-pattern — constant backoff:** Retrying every 1 second for 10 attempts is not friendlier. It adds 10x the load of exponential backoff and still doesn't give the failing system time to recover.

**Anti-pattern — long initial delay:** Starting at 60 seconds means you wait a full minute even on a transient 1-second hiccup. Start small, grow as failures persist.

---

## Idempotent Operations

**Purpose:** Design agents so that retrying a failed operation produces the same result as running it once.

**The problem:** If Agent A fails mid-write, retrying might duplicate the write. If Agent B runs the same analysis twice, it might produce slightly different results. Without idempotency, retries are dangerous.

**Patterns for idempotency:**

| Operation Type | Idempotency Pattern |
|----------------|---------------------|
| File writes | Write to temp file, then atomic rename |
| API calls | Include idempotency key in request |
| Analysis tasks | Use seeded randomness (same input → same output) |
| State updates | Check state before writing, only write if changed |

**Atomic rename pattern for file writes:**
```python
def safe_write(path: Path, content: str):
    temp_path = path.with_suffix('.tmp')
    with open(temp_path, 'w') as f:
        f.write(content)
    temp_path.rename(path)  # Atomic on POSIX
    # If this fails, retry checks if file exists before writing
```

**State check-before-write pattern:**
```python
def update_state(new_finding: Dict):
    state = load_shared_state()
    if new_finding["id"] in [f["id"] for f in state["findings"]]:
        return  # Already present, skip (idempotent retry)
    state["findings"].append(new_finding)
    save_shared_state(state)
```

---

## Implementation Reference

**Coordination utilities** from multi-agent-patterns reference (`scripts/coordination.py`):

```python
# Full AgentFailureHandler with circuit breaker
class AgentFailureHandler:
    def __init__(self, communication, max_retries=3):
        self.communication = communication
        self.max_retries = max_retries
        self.failure_counts: Dict[str, int] = {}
        self.circuit_breakers: Dict[str, float] = {}

    def handle_failure(self, agent_id: str, task_id: str, error: str) -> Dict[str, Any]:
        self.failure_counts[agent_id] = self.failure_counts.get(agent_id, 0) + 1
        if self.failure_counts[agent_id] > self.max_retries:
            self._activate_circuit_breaker(agent_id)
            return {"action": "fallback", "alternative": self._find_alternative_agent(agent_id)}
        delay = min(2 ** self.failure_counts[agent_id], 60)
        return {"action": "retry", "delay": delay}

    def _activate_circuit_breaker(self, agent_id: str) -> None:
        self.circuit_breakers[agent_id] = time.time() + 60

    def _find_alternative_agent(self, failed_agent: str) -> str:
        return "default_backup_agent"  # Capability-aware lookup would go here

    def is_available(self, agent_id: str) -> bool:
        if agent_id in self.circuit_breakers:
            if time.time() > self.circuit_breakers[agent_id]:
                del self.circuit_breakers[agent_id]
                self.failure_counts[agent_id] = 0
                return True
            return False
        return True

    def record_success(self, agent_id: str) -> None:
        self.failure_counts[agent_id] = 0
```

---

## Usage in Orchestration

**Integrate fault tolerance into workflow design:**

```markdown
## Fault-Tolerant Workflow

1. **Initialize**:
   - Create checkpoint directory
   - Set up failure handler with max_retries=3

2. **At each milestone**:
   - Save checkpoint (workflow state + agent outputs)
   - Record success to circuit breaker

3. **On failure**:
   - Check circuit breaker status
   - If open: route to alternative or fail fast
   - If retry: apply exponential backoff
   - Load checkpoint, resume from last good state

4. **Never continue past untrusted output**:
   - Verify agent outputs before passing downstream
   - If verification fails: circuit breaker + checkpoint + retry
```

---

## Key Principle

**Design for failure isolation, not failure prevention.** You cannot prevent all failures. You can design your system so that failures are contained, visible, and recoverable.

The three questions every multi-agent workflow must answer before execution:
1. If this agent fails, what routes around it?
2. If this agent produces wrong output, how do we catch it before it propagates?
3. If the entire workflow crashes, what is the minimum we must redo?