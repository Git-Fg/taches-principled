---
name: analyse-problem
description: Comprehensive A3 one-page problem analysis with root cause investigation and action plan
argument-hint: "[problem description]"
---

## Decision Router

IF investigating a recurring issue, incident, or major improvement opportunity → produce a complete A3 analysis
IF the problem is a trivial one-line fix or minor bug → skip (A3 is designed for significant, recurring, or systemic issues)
IF deeper root cause work is needed → use Five Whys or Fishbone analysis within section 4 of the template
IF the situation evolves during investigation → update the A3 as a living document until closure

# Analyse Problem

Structured one-page problem documentation and resolution planning using the A3 format — named after the paper size that constrains analysis to concise, complete thinking.

## Core Principle

Force complete, concise root-cause-to-resolution thinking onto a single page. If it doesn't fit, the problem isn't well enough understood yet.

## Process

### Phase 1: Frame the Problem
1. **Background** — Why this matters: context, business impact, urgency, who is affected
2. **Current Condition** — What is happening now: facts, data, metrics, examples (not opinions)
3. **Goal/Target** — What success looks like: specific, measurable, time-bound targets

### Phase 2: Analyze Root Causes
4. **Root Cause Analysis** — Why the problem exists using Five Whys or Fishbone. Dig until you reach systemic or process-level causes, not just technical details.

### Phase 3: Plan and Execute
5. **Countermeasures** — Specific actions addressing root causes (not vague intentions). Each countermeasure must tie to a root cause identified in section 4.
6. **Implementation Plan** — Timeline, responsibilities, dependencies, milestones. Distinguish immediate from short-term from long-term.

### Phase 4: Verify
7. **Follow-up** — Success metrics, monitoring plan, review dates. How to verify success and prevent recurrence.

## Output

An A3 document covering the full problem lifecycle: background, current state, goal, root cause, countermeasures, implementation plan, and follow-up. Written to conversation. Can be used as a historical record for organizational learning.

## Template

```
TITLE: [Concise problem statement]

1. BACKGROUND — Why this matters
2. CURRENT CONDITION — What's happening (data, not opinions)
3. GOAL/TARGET — Specific, measurable targets
4. ROOT CAUSE ANALYSIS — Five Whys or Fishbone
5. COUNTERMEASURES — Actions tied to root causes
6. IMPLEMENTATION PLAN — Who, what, when, dependencies
7. FOLLOW-UP — Success metrics, monitoring, review dates
```

## Design Decisions

### One-page constraint
The A3 paper size is the forcing function. If the analysis genuinely requires more space, the problem scope is too broad — decompose into sub-problems and produce multiple A3s.

### Countermeasures tied to root causes
Section 5 must reference section 4 explicitly. Every countermeasure must trace to a specific root cause. This prevents treating symptoms.

### Living document until closed
The A3 should be updated as understanding grows or the situation changes. Only close it when the follow-up metrics confirm success and prevention measures are in place.
