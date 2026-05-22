---
name: orchestration-patterns
description: Five patterns for orchestrating parallel subagent work
---

# Parallel Orchestration Patterns

Five patterns for structuring parallel subagent execution.

## 1. Horizontal Split (Investigation Lens)

Each agent owns a different analytical lens on the same scope.

```
Orchestrator
├── @security "Audit auth/ for OWASP Top 10"
├── @perf "Analyze db queries for N+1"
└── @style "Check code style violations"
```

**When:** Multi-dimensional analysis of the same files.
**Why:** Single reviewer gravitates to one lens; parallel catches all simultaneously.

## 2. Vertical Slice (Layer Ownership)

Each agent owns a different layer of the stack.

```
Orchestrator
├── @frontend "Implement UI in src/ui/"
├── @backend "Implement API in src/api/"
└── @tests "Write integration tests in tests/"
```

**When:** Tasks are decomposed by layer (frontend/backend/tests).
**Why:** File-disjoint, no conflicts, each agent owns its domain.

## 3. Pipeline (Chained Dependencies)

Each step depends on the prior step's output.

```
Orchestrator
├── @researcher "Research library X → /tmp/research.json"
└── @implementer "Implement using /tmp/research.json"
```

**When:** Sequential dependencies (research → implementation).
**Why:** Orchestrator coordinates, workers execute independently.

## 4. Contest (Competing Hypotheses)

Multiple theories tested in parallel, orchestrator converges on winner.

```
Orchestrator
├── @theory-A "Test: race condition in async handler"
└── @theory-B "Test: memory leak in connection pool"
```

**When:** Root cause unknown, multiple plausible explanations.
**Why:** Single agent finds one explanation and stops; contest finds faster.

## 5. Fan-Out/Fan-In (Aggregator)

N parallel workers each handle a slice, one aggregator merges results.

```
Orchestrator
├── @worker-A "Process slice 1 → /tmp/result-a.json"
├── @worker-B "Process slice 2 → /tmp/result-b.json"
└── @aggregator "Merge /tmp/result-*.json → combined.json"
```

**When:** Large task dividable into independent slices.
**Why:** Keeps main context clean; aggregator handles synthesis overhead.

---

## Spawn Prompt Structure

Use RACE for every spawn:

```
## Role
[What this agent is]

## Action
[Concrete, scoped task — imperative form, file ownership boundaries]

## Context
[What orchestrator did; what this agent does; interface contracts]

## Expectation
[Output format; success criteria; coverage rule]
```

## Anti-Patterns

- **Never** spawn agents editing overlapping files
- **Never** delegate without success criteria
- **Never** skip rollback plan
- **Never** assume subagent completed without validation
