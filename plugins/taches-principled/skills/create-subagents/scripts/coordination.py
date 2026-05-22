#!/usr/bin/env python3
"""
Multi-Agent Coordination Utilities

Provides reusable components for multi-agent orchestration:
- AgentCommunication: In-memory message bus
- SupervisorAgent: Central coordinator with worker registration and task decomposition
- HandoffProtocol: Peer-to-peer transfer with state
- ConsensusManager: Weighted voting with confidence weighting
- AgentFailureHandler: Circuit breaker with exponential backoff
- CheckpointManager: Workflow state persistence and resume

Usage:
    from coordination import AgentCommunication, SupervisorAgent, ConsensusManager

License: MIT
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional
import time
import json
from pathlib import Path


class MessageType(Enum):
    REQUEST = "request"
    RESPONSE = "response"
    HANDOVER = "handover"
    FEEDBACK = "feedback"
    ALERT = "alert"


@dataclass
class AgentMessage:
    sender: str
    receiver: str
    message_type: MessageType
    content: Dict[str, Any]
    timestamp: float = field(default_factory=time.time)
    message_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    requires_response: bool = False
    priority: int = 0  # 0 = normal, higher = more urgent


def uuid():
    import uuid as uuid_module
    return str(uuid_module.uuid4())


class AgentCommunication:
    """In-memory message bus for agent communication."""

    def __init__(self) -> None:
        self.inbox: Dict[str, List[AgentMessage]] = {}
        self.outbox: List[AgentMessage] = []
        self.message_history: List[AgentMessage] = []

    def send(self, message: AgentMessage) -> None:
        """Send a message to an agent."""
        if message.receiver not in self.inbox:
            self.inbox[message.receiver] = []
        self.inbox[message.receiver].append(message)
        self.outbox.append(message)
        self.message_history.append(message)

    def receive(self, agent_id: str) -> List[AgentMessage]:
        """Receive all messages for an agent, clearing its inbox."""
        messages = self.inbox.get(agent_id, [])
        self.inbox[agent_id] = []
        return messages

    def broadcast(
        self,
        sender: str,
        message_type: MessageType,
        content: Dict[str, Any],
        receivers: List[str],
    ) -> None:
        """Broadcast a message to multiple agents."""
        for receiver in receivers:
            self.send(AgentMessage(
                sender=sender,
                receiver=receiver,
                message_type=message_type,
                content=content,
            ))


class SupervisorAgent:
    """Central coordinator with worker registration, task decomposition, and aggregation."""

    def __init__(self, name: str, communication: AgentCommunication) -> None:
        self.name = name
        self.communication = communication
        self.workers: Dict[str, Dict[str, Any]] = {}
        self.task_queue: List[Dict[str, Any]] = []
        self.completed_tasks: List[Dict[str, Any]] = []
        self.current_state: Dict[str, Any] = {}

    def register_worker(self, worker_id: str, capabilities: List[str]) -> None:
        """Register a worker agent with the supervisor."""
        self.workers[worker_id] = {
            "capabilities": capabilities,
            "status": "available",
            "current_task": None,
            "metrics": {"completed": 0, "failed": 0},
        }

    def decompose_task(self, task: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Decompose a task into subtasks by type."""
        task_type = task.get("type", "other")
        subtasks = []

        if task_type == "research":
            subtasks = [
                {"id": f"{task['id']}_search", "type": "search", "parent_task": task["id"], "priority": 1},
                {"id": f"{task['id']}_analyze", "type": "analyze", "parent_task": task["id"], "priority": 2},
                {"id": f"{task['id']}_synthesize", "type": "synthesize", "parent_task": task["id"], "priority": 3},
            ]
        elif task_type == "create":
            subtasks = [
                {"id": f"{task['id']}_plan", "type": "plan", "parent_task": task["id"], "priority": 1},
                {"id": f"{task['id']}_draft", "type": "draft", "parent_task": task["id"], "priority": 2},
                {"id": f"{task['id']}_review", "type": "review", "parent_task": task["id"], "priority": 3},
            ]
        else:
            subtasks = [{"id": f"{task['id']}_execute", "type": "execute", "parent_task": task["id"], "priority": 1}]

        return subtasks

    def assign_task(self, subtask: Dict[str, Any], worker_id: str) -> None:
        """Assign a subtask to a worker agent."""
        if worker_id not in self.workers:
            raise ValueError(f"Unknown worker: {worker_id}")
        self.workers[worker_id]["current_task"] = subtask
        self.workers[worker_id]["status"] = "busy"

    def select_worker(self, subtask: Dict[str, Any]) -> str:
        """Select best available worker for subtask (capability-aware + load-balanced)."""
        required_capability = subtask.get("type")
        available_workers = [
            (wid, w) for wid, w in self.workers.items()
            if w["status"] == "available" and required_capability in w["capabilities"]
        ]
        if not available_workers:
            raise ValueError(f"No available worker for capability: {required_capability}")

        # Select worker with fewest completed tasks
        selected = min(available_workers, key=lambda x: x[1]["metrics"]["completed"])
        return selected[0]

    def aggregate_results(self, subtask_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Aggregate results from completed subtasks."""
        summary_parts = []
        all_findings = []

        for result in subtask_results:
            if "summary" in result:
                summary_parts.append(result["summary"])
            if "findings" in result:
                all_findings.extend(result["findings"])

        quality_score = sum(r.get("quality", 0.5) for r in subtask_results) / len(subtask_results) if subtask_results else 0

        return {
            "results": subtask_results,
            "summary": " | ".join(summary_parts) if summary_parts else "",
            "findings": all_findings,
            "quality_score": quality_score,
        }

    def run_workflow(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute complete supervised workflow end-to-end."""
        subtasks = self.decompose_task(task)
        subtask_results = []

        for subtask in subtasks:
            try:
                worker_id = self.select_worker(subtask)
                self.assign_task(subtask, worker_id)
                result = self._simulate_worker_response(worker_id, subtask)
                subtask_results.append(result)
                self.workers[worker_id]["metrics"]["completed"] += 1
                self.workers[worker_id]["status"] = "available"
                self.workers[worker_id]["current_task"] = None
            except ValueError as e:
                subtask_results.append({"id": subtask["id"], "status": "failed", "error": str(e)})

        final_result = self.aggregate_results(subtask_results)

        return {
            "task": task,
            "subtask_results": subtask_results,
            "final_result": final_result,
            "success": all(r.get("status") != "failed" for r in subtask_results),
        }

    def _simulate_worker_response(self, worker_id: str, subtask: Dict[str, Any]) -> Dict[str, Any]:
        """Simulates worker completing a subtask (inline, not async)."""
        return {
            "id": subtask["id"],
            "worker": worker_id,
            "status": "completed",
            "summary": f"Completed {subtask['type']} for {subtask['parent_task']}",
            "quality": 0.8,
        }

    def _send(self, message: AgentMessage) -> None:
        """Send message through communication channel."""
        self.communication.send(message)


class HandoffProtocol:
    """Peer-to-peer transfer with state preservation."""

    def __init__(self, communication: AgentCommunication) -> None:
        self.communication = communication

    def create_handoff(
        self,
        from_agent: str,
        to_agent: str,
        context: Dict[str, Any],
        reason: str,
    ) -> AgentMessage:
        """Create a handoff message with transferred context."""
        return AgentMessage(
            sender=from_agent,
            receiver=to_agent,
            message_type=MessageType.HANDOVER,
            content={
                "handoff_reason": reason,
                "transferred_context": context,
                "handoff_timestamp": time.time(),
            },
            priority=1,
        )

    def accept_handoff(self, agent_id: str) -> Optional[AgentMessage]:
        """Accept first pending HANDOVER message for agent, or None."""
        messages = self.communication.receive(agent_id)
        for msg in messages:
            if msg.message_type == MessageType.HANDOVER:
                return msg
        return None

    def transfer_with_state(
        self,
        from_agent: str,
        to_agent: str,
        state: Dict[str, Any],
        task: Dict[str, Any],
    ) -> bool:
        """Transfer full task state for resumable handoff."""
        handoff = self.create_handoff(
            from_agent=from_agent,
            to_agent=to_agent,
            context={
                "task_state": state,
                "task_details": task,
                "progress": "in_progress",
            },
            reason="Task continuation",
        )
        self.communication.send(handoff)

        # Wait for acknowledgment
        time.sleep(0.1)  # Placeholder for async waiting
        responses = self.communication.receive(from_agent)
        for resp in responses:
            if resp.message_type == MessageType.RESPONSE and resp.content.get("status") == "handoff_received":
                return True
        return False


class ConsensusManager:
    """Weighted voting with confidence weighting for multi-agent decisions."""

    def __init__(self) -> None:
        self.votes: Dict[str, List[Dict[str, Any]]] = {}
        self.debates: Dict[str, List[Dict[str, Any]]] = {}

    def initiate_vote(self, topic_id: str, agents: List[str], options: List[str]) -> None:
        """Initiate a voting round on a topic."""
        self.votes[topic_id] = [
            {"agent_id": agent, "status": "pending", "option": None, "confidence": 0.5, "expertise": 1.0}
            for agent in agents
        ]

    def submit_vote(
        self,
        topic_id: str,
        agent_id: str,
        selection: str,
        confidence: float,
        expertise: float = 1.0,
    ) -> None:
        """Submit a vote for a topic with confidence and expertise weights."""
        for vote in self.votes[topic_id]:
            if vote["agent_id"] == agent_id:
                vote["option"] = selection
                vote["confidence"] = confidence
                vote["expertise"] = expertise
                vote["status"] = "cast"
                break

    def calculate_weighted_consensus(self, topic_id: str) -> Dict[str, Any]:
        """Calculate weighted consensus from cast votes.

        Returns: {
            "status": "complete" | "no_votes",
            "result": winner_option,
            "details": {selection: {weighted_score, avg_confidence, vote_count}},
            "consensus_strength": float (0.0-1.0)
        }
        """
        if topic_id not in self.votes:
            return {"status": "no_votes", "result": None, "details": {}}

        cast_votes = [v for v in self.votes[topic_id] if v["status"] == "cast"]
        if not cast_votes:
            return {"status": "no_votes", "result": None, "details": {}}

        option_scores: Dict[str, Dict[str, Any]] = {}

        for vote in cast_votes:
            option = vote["option"]
            weight = vote["confidence"] * vote["expertise"]

            if option not in option_scores:
                option_scores[option] = {"weighted_score": 0.0, "confidence_sum": 0.0, "count": 0}

            option_scores[option]["weighted_score"] += weight
            option_scores[option]["confidence_sum"] += vote["confidence"]
            option_scores[option]["count"] += 1

        # Find winner
        if not option_scores:
            return {"status": "no_votes", "result": None, "details": {}}

        winner = max(option_scores.items(), key=lambda x: x[1]["weighted_score"])
        winner_name = winner[0]
        winner_stats = winner[1]

        total_weight = sum(s["weighted_score"] for s in option_scores.values())
        consensus_strength = winner_stats["weighted_score"] / total_weight if total_weight > 0 else 0

        return {
            "status": "complete",
            "result": winner_name,
            "details": {
                opt: {
                    "weighted_score": stats["weighted_score"],
                    "avg_confidence": stats["confidence_sum"] / stats["count"],
                    "vote_count": stats["count"],
                }
                for opt, stats in option_scores.items()
            },
            "consensus_strength": consensus_strength,
        }


class AgentFailureHandler:
    """Circuit breaker with exponential backoff for fault-tolerant multi-agent systems."""

    def __init__(
        self,
        communication: Optional[AgentCommunication] = None,
        max_retries: int = 3,
    ) -> None:
        self.communication = communication
        self.max_retries = max_retries
        self.failure_counts: Dict[str, int] = {}
        self.circuit_breakers: Dict[str, float] = {}  # agent -> unlock timestamp

    def handle_failure(
        self, agent_id: str, task_id: str, error: str
    ) -> Dict[str, Any]:
        """Handle failure from an agent.

        Returns: {
            "action": "retry" | "fallback",
            "delay": float (seconds, for retry),
            "alternative": str (agent_id, for fallback)
        }
        """
        self.failure_counts[agent_id] = self.failure_counts.get(agent_id, 0) + 1

        if self.failure_counts[agent_id] > self.max_retries:
            self._activate_circuit_breaker(agent_id)
            return {
                "action": "fallback",
                "alternative": self._find_alternative_agent(agent_id),
                "reason": f"Circuit open for {agent_id} after {self.failure_counts[agent_id]} failures",
            }

        delay = min(2 ** self.failure_counts[agent_id], 60)
        return {
            "action": "retry",
            "delay": delay,
            "reason": f"Retry {self.failure_counts[agent_id]} with {delay}s backoff",
        }

    def _activate_circuit_breaker(self, agent_id: str) -> None:
        """Temporarily disable agent for 60 seconds (1-minute cooldown)."""
        self.circuit_breakers[agent_id] = time.time() + 60

    def _find_alternative_agent(self, failed_agent: str) -> str:
        """Returns 'default_backup_agent' (placeholder for capability-aware lookup)."""
        return "default_backup_agent"

    def is_available(self, agent_id: str) -> bool:
        """Check if agent available (circuit breaker not active)."""
        if agent_id in self.circuit_breakers:
            if time.time() > self.circuit_breakers[agent_id]:
                del self.circuit_breakers[agent_id]
                self.failure_counts[agent_id] = 0
                return True
            return False
        return True

    def record_success(self, agent_id: str) -> None:
        """Reset failure count on successful task completion."""
        self.failure_counts[agent_id] = 0
        if agent_id in self.circuit_breakers:
            del self.circuit_breakers[agent_id]


class CheckpointManager:
    """Workflow state persistence for recovery from failures."""

    def __init__(self, checkpoint_dir: str = ".principled/scratch/checkpoints") -> None:
        self.checkpoint_dir = Path(checkpoint_dir)
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)

    def save_checkpoint(self, workflow_id: str, step: int, state: Dict[str, Any]) -> None:
        """Save workflow state at milestone."""
        checkpoint = {
            "workflow_id": workflow_id,
            "step": step,
            "state": state,
            "timestamp": time.time(),
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

    def list_checkpoints(self, workflow_id: str) -> List[int]:
        """List all checkpoint step numbers for a workflow."""
        return sorted([
            int(p.stem.split("_step")[1])
            for p in self.checkpoint_dir.glob(f"{workflow_id}_step*.json")
        ])


if __name__ == "__main__":
    # Basic smoke test
    comm = AgentCommunication()
    supervisor = SupervisorAgent("test-supervisor", comm)
    supervisor.register_worker("worker-1", ["search", "analyze"])
    supervisor.register_worker("worker-2", ["draft", "review"])

    result = supervisor.run_workflow({"id": "task-1", "type": "research"})
    print(f"Workflow success: {result['success']}")
    print(f"Final result quality: {result['final_result']['quality_score']}")

    # Test consensus
    consensus = ConsensusManager()
    consensus.initiate_vote("topic-1", ["agent-a", "agent-b", "agent-c"], ["A", "B"])
    consensus.submit_vote("topic-1", "agent-a", "A", confidence=0.7, expertise=1.0)
    consensus.submit_vote("topic-1", "agent-b", "A", confidence=0.4, expertise=0.5)
    consensus.submit_vote("topic-1", "agent-c", "B", confidence=0.9, expertise=1.0)

    result = consensus.calculate_weighted_consensus("topic-1")
    print(f"Consensus result: {result['result']} (strength: {result['consensus_strength']:.2f})")

    # Test checkpoint
    checkpoint = CheckpointManager()
    checkpoint.save_checkpoint("workflow-1", 1, {"progress": "initial"})
    checkpoint.save_checkpoint("workflow-1", 2, {"progress": "middle"})
    latest = checkpoint.get_latest_step("workflow-1")
    print(f"Latest checkpoint step: {latest}")