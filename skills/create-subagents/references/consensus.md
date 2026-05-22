# Consensus Mechanisms: Weighted Voting, Debate, and Adversarial Critique

## Sections
- [Why Simple Voting Fails](#why-simple-voting-fails)
- [Weighted Voting](#weighted-voting)
- [Debate Protocol](#debate-protocol)
- [Adversarial Critique](#adversarial-critique)
- [Convergence Detection](#convergence-detection)
- [Implementation Reference](#implementation-reference)

---

Multi-agent systems make decisions. When multiple agents provide inputs, the system must reconcile them. Simple majority voting treats hallucinations from weak models as equal to reasoning from strong models. This reference covers robust consensus mechanisms.

---

## Why Simple Voting Fails

**The voting problem:** Simple majority voting ignores confidence and expertise. A weak model with low confidence votes equally to a strong model with high confidence.

**The sycophancy problem:** LLMs have an inherent bias toward agreement. Without explicit countermeasures, multi-agent discussions converge on agreeable answers, not correct ones.

**Example of voting failure:**

```
Agent A (weak, hallucinates): "Option 1 is best" — confidence 0.3
Agent B (weak): "Option 1 is best" — confidence 0.4
Agent C (strong): "Option 2 is best" — confidence 0.9

Simple vote: Option 1 wins 2-1
Reality: Both A and B were wrong. Option 2 is correct.
```

**Signal of failure:** Discussion terminates too quickly. "Everyone agrees" is a sycophancy signal, not a correctness signal.

---

## Weighted Voting

**Principle:** Weight each vote by `confidence × domain_expertise`. Agents with higher confidence or domain expertise carry more weight in final decisions.

**Formula:** `weighted_score = Σ(vote × verbalized_confidence × domain_expertise)`

**Example:**

```python
# Agent votes and their weights
agents = {
    "A": {"vote": "Option 1", "confidence": 0.3, "expertise": "low"},
    "B": {"vote": "Option 1", "confidence": 0.4, "expertise": "medium"},
    "C": {"vote": "Option 2", "confidence": 0.9, "expertise": "high"}
}

# Weight mapping
expertise_weights = {"low": 0.5, "medium": 1.0, "high": 2.0}

# Calculate weighted scores
for agent, data in agents.items():
    weight = data["confidence"] * expertise_weights[data["expertise"]]
    print(f"{agent}: vote={data['vote']}, weight={weight}")

# Option 1: 0.3*0.5 + 0.4*1.0 = 0.15 + 0.4 = 0.55
# Option 2: 0.9*2.0 = 1.8
# Option 2 wins
```

**WeightedConsensus implementation:**

```python
def calculate_weighted_consensus(
    votes: Dict[str, Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Calculate weighted consensus from agent votes.

    Args:
        votes: {
            "agent_id": {
                "selection": str,
                "confidence": float (0.0-1.0),
                "expertise": float (0.0-1.0)  # 1.0 = full domain expertise
            }
        }

    Returns: {
        "status": "complete" | "no_votes",
        "result": winner_option,
        "details": {
            option: {
                "weighted_score": float,
                "avg_confidence": float,
                "vote_count": int
            }
        },
        "consensus_strength": float (0.0-1.0)
    }
    """
    if not votes:
        return {"status": "no_votes", "result": None, "details": {}}

    option_scores: Dict[str, Dict] = {}

    for agent_id, vote_data in votes.items():
        option = vote_data["selection"]
        confidence = vote_data["confidence"]
        expertise = vote_data.get("expertise", 1.0)
        weight = confidence * expertise

        if option not in option_scores:
            option_scores[option] = {"weighted_score": 0, "confidence_sum": 0, "count": 0}

        option_scores[option]["weighted_score"] += weight
        option_scores[option]["confidence_sum"] += confidence
        option_scores[option]["count"] += 1

    # Find winner
    winner = max(option_scores.items(), key=lambda x: x[1]["weighted_score"])
    winner_name = winner[0]
    winner_stats = winner[1]

    total_votes = sum(s["count"] for s in option_scores.values())
    consensus_strength = winner_stats["weighted_score"] / sum(
        s["weighted_score"] for s in option_scores.values()
    )

    return {
        "status": "complete",
        "result": winner_name,
        "details": {
            opt: {
                "weighted_score": stats["weighted_score"],
                "avg_confidence": stats["confidence_sum"] / stats["count"],
                "vote_count": stats["count"]
            }
            for opt, stats in option_scores.items()
        },
        "consensus_strength": consensus_strength
    }
```

---

## Debate Protocol

**Principle:** Structured adversarial critique over multiple rounds yields higher accuracy than collaborative consensus on complex reasoning tasks.

**Why debate works:** Agents must justify positions rather than simply agreeing. Weak arguments are exposed. Confidence adjusts based on critique.

**Structure:**

```
Round 1 (Opening):
- Each agent presents position + reasoning + confidence

Round 2 (Challenge):
- Each agent challenges others' positions
- Must articulate specific weaknesses

Round 3 (Defense):
- Agents defend against challenges
- Adjust confidence based on critique strength

[Optional: Round N continues until convergence or max rounds]

Final (Decision):
- Weighted voting based on post-debate confidence
- Or convergence detection
```

**DebateProtocol implementation:**

```python
class DebateProtocol:
    def __init__(self, max_rounds=3):
        self.max_rounds = max_rounds
        self.rounds: List[Dict[str, Any]] = []

    def run_debate(
        self,
        topic: str,
        agents: List[str],
        initial_positions: Dict[str, str]
    ) -> Dict[str, Any]:
        """
        Run structured multi-agent debate.

        Returns: {
            "converged": bool,
            "final_positions": {agent: final_position},
            "adjusted_confidence": {agent: new_confidence},
            "rounds": [round_data...]
        }
        """
        positions = initial_positions.copy()
        confidences = {agent: 0.8 for agent in agents}  # Initial confidence

        for round_num in range(self.max_rounds):
            round_data = {"round": round_num + 1, "exchanges": []}

            # Challenge phase
            for agent in agents:
                challenge = f"Challenge to {agent}: Explain weaknesses in your position."
                round_data["exchanges"].append({
                    "type": "challenge",
                    "from": "system",
                    "to": agent,
                    "content": challenge
                })

                # Agent responds with critique of others
                critique = self._generate_critique(agent, positions, confidences)
                round_data["exchanges"].append({
                    "type": "critique",
                    "from": agent,
                    "content": critique
                })

            # Check convergence
            if self.check_convergence(positions):
                round_data["converged"] = True
                self.rounds.append(round_data)
                break

            # Adjust confidence based on critique strength
            confidences = self._adjust_confidence(positions, confidences)

            self.rounds.append(round_data)

        return {
            "converged": len(self.rounds) < self.max_rounds,
            "final_positions": positions,
            "adjusted_confidence": confidences,
            "rounds": self.rounds
        }

    def check_convergence(self, positions: Dict[str, str]) -> bool:
        """Check if debate has converged (all positions stable or strong consensus)."""
        unique_positions = set(positions.values())
        if len(unique_positions) == 1:
            return True  # Full consensus

        # Check if critiques are just restating same points
        # (converged on disagreement, not on solution)
        if len(unique_positions) > 2:
            return False

        # Convergence if majority has same high-confidence position
        # and minorities have lower confidence
        return False  # Default: don't auto-converge

    def _generate_critique(
        self,
        agent: str,
        positions: Dict[str, str],
        confidences: Dict[str, float]
    ) -> str:
        """Generate critique of other agents' positions."""
        # In production: LLM generates actual critique
        return f"Critique from {agent}"

    def _adjust_confidence(
        self,
        positions: Dict[str, str],
        confidences: Dict[str, float]
    ) -> Dict[str, float]:
        """Adjust confidence based on critique received."""
        # In production: analyze critique content and adjust
        return confidences
```

---

## Adversarial Critique

**Principle:** Assign explicit adversarial roles. Require agents to state disagreements before convergence is allowed.

**The anti-sycophancy mechanism:**

1. **Designate adversarial agents:** One agent's job is to find flaws
2. **Require dissent before agreement:** An agent must articulate specific objections before "agreeing"
3. **Protect minority positions:** Don't weight by vote count alone — minority with strong reasoning beats majority with weak reasoning

**Adversarial critique prompt:**

```markdown
<role>
You are an adversarial critic. Your job is to find flaws in proposed solutions.
</role>

<workflow>
1. Review other agents' positions
2. For each position:
   - Identify specific weaknesses
   - Propose alternative explanations
   - Rate confidence (0-1) based on strength of reasoning
3. State any agreements — but only AFTER stating disagreements
4. Do NOT simply agree with majority. Your adversarial role requires critique.

<constraint>
NEVER start with agreement. You must state specific objections first.
Agreement without critique is not permitted in your role.
</constraint>
```

---

## Convergence Detection

**Principle:** Don't allow "everyone agrees" to be the stopping condition. Require active convergence — positions that have survived genuine challenge.

**Convergence signals:**

| Signal | Meaning |
|--------|---------|
| All agents give same position after challenge | Strong convergence (possibly sycophancy — verify) |
| Strong agent maintains position while others adjust | Real convergence on strong reasoning |
| Weak agents converge to strong agent | Delegitimization of weak positions |
| Agents maintain distinct positions after challenge | No convergence — use weighted voting |

**Anti-sycophancy convergence check:**

```markdown
## Convergence Check Protocol

1. Debate completes (max rounds or convergence detected)
2. For each agent, record:
   - Initial position
   - Number of times challenged
   - Whether position changed after challenge
3. Evaluate:
   - If ALL positions are same: SUSPECT sycophancy
     - Run additional adversarial round
     - Verify with independent source
   - If strong agent maintained position: LEGITIMATE convergence
   - If positions differ: WEIGHTED VOTE
```

---

## Implementation Reference

**ConsensusManager from coordination.py:**

```python
class ConsensusManager:
    def __init__(self):
        self.votes: Dict[str, List[Dict[str, Any]]] = {}
        self.debates: Dict[str, List[Dict[str, Any]]] = {}

    def initiate_vote(self, topic_id: str, agents: List[str], options: List[str]) -> None:
        """Initiate a voting round on a topic."""
        self.votes[topic_id] = [
            {"agent_id": agent, "status": "pending", "option": None}
            for agent in agents
        ]

    def submit_vote(
        self,
        topic_id: str,
        agent_id: str,
        selection: str,
        confidence: float
    ) -> None:
        """Submit a vote with confidence weight."""
        for vote in self.votes[topic_id]:
            if vote["agent_id"] == agent_id:
                vote["option"] = selection
                vote["confidence"] = confidence
                vote["status"] = "cast"
                break

    def calculate_weighted_consensus(self, topic_id: str) -> Dict[str, Any]:
        """Calculate weighted consensus from cast votes."""
        # Implementation: see WeightedConsensus above
        pass
```

---

## Key Principles

1. **Never use simple majority voting** — it treats weak hallucinations as equal to strong reasoning
2. **Weight by confidence × expertise** — domain experts with high confidence carry more weight
3. **Require adversarial critique** — agents must state disagreements before convergence
4. **Detect sycophancy** — quick agreement is a warning signal
5. **Allow minority positions** — strong reasoning from one agent beats weak consensus
6. **Set round limits** — prevent infinite debate loops