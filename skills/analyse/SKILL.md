---
name: analyse
description: Auto-selects best improvement method (code exploration, workflow mapping, or waste identification) for a given target
when_to_use: |
  Use when the user says "analyze this", "look into this code", "what's wrong here", or "find the problem".
  IMMEDIATELY when investigating code quality, process bottlenecks, or implementation gaps.
argument-hint: "[target description]"
---

## Decision Router

IF analyzing code implementation, exploring unfamiliar code, or checking documentation accuracy → use Gemba Walk (go see the actual code)
IF analyzing workflows, processes, multi-stage pipelines, or bottlenecks → use Value Stream Mapping
IF analyzing code quality, technical debt, over-engineering, or resource waste → use Muda (Waste Analysis)
IF the method is already clear from context → apply it directly without auto-selection
IF combining with structured problem documentation → produce findings for a downstream A3 analysis

# Analyse

Automatically selects and applies the most appropriate analysis technique for a given target. Three methods cover code exploration, process mapping, and waste identification.

## Core Principle

Match the analysis method to the nature of the target. Code problems need code observation. Process problems need flow measurement. Quality problems need waste identification.

## Method Selection

| If the target is... | Use... |
|---|---|
| Code implementation, legacy systems, gap between docs and reality | Gemba Walk |
| Workflows, CI/CD pipelines, team handoffs, cycle time | Value Stream Mapping |
| Code quality, technical debt, duplication, resource use | Muda Analysis |

## Process

### Phase 1: Scope and Select
1. Define what is being analyzed and why
2. Select the method (auto or explicit override)
3. State assumptions before observing

### Phase 2: Execute Method
Each method follows a distinct process:

**Gemba Walk** — Observe actual code:
- Identify entry points and data flow
- Compare assumptions against reality
- Document surprises, hidden dependencies, undocumented behavior

**Value Stream Mapping** — Measure the flow:
- Map every step from start to end, including wait states
- Measure processing time vs waiting time for each step
- Calculate lead time, value-add ratio, and efficiency

**Muda Analysis** — Classify waste:
- Examine against the seven waste types (Overproduction, Waiting, Transportation, Over-processing, Inventory, Motion, Defects)
- Quantify impact for each finding (time, complexity, cost)
- Prioritize by impact

### Phase 3: Report
1. Present findings per category
2. Recommend specific actions with priority (HIGH/MEDIUM/LOW)
3. Include estimated impact of implementing recommendations

## Output

A structured analysis report with method rationale, observations, prioritized recommendations, and estimated improvement impact. Written to conversation — actionable for downstream improvement cycles.

## Design Decisions

### Three methods, not a generic framework
Each method targets a distinct problem class. A single generic "analyze everything" approach would produce shallower results. The auto-selector removes decision overhead when the target type is clear.

### No fixed template — method shapes the output
Gemba Walk output is artifact-centric (surprises, gaps). VSM output is metric-centric (lead time, efficiency). Muda output is category-centric (waste type, impact). Forcing all three into one template would lose method-specific signal.
