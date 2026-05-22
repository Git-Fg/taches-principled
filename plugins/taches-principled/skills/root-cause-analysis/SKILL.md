---
name: root-cause-analysis
description: Two root cause analysis methods: Five Whys traces single-path causal chains iteratively; Fishbone explores causes across six categories (People, Process, Technology, Environment, Methods, Materials).
when_to_use: |
  Use when the user says "find the root cause", "why did this happen", "trace this back", or "what's causing this".
  IMMEDIATELY when debugging — BEFORE applying fixes, not after.
argument-hint: "[problem description] [--depth N]"
---

## Decision Router

IF problem has a clear single causal chain from symptom to root → **Five Whys** (drill down iteratively, stop at systemic cause)
IF problem has multiple potential contributing factors across domains → **Fishbone / Cause-and-Effect** (explore 6 categories systematically)
IF "human error" appears as a cause → keep digging regardless of method — the system should have made the error impossible
IF combining with structured documentation → produce findings as input for section 4 of an A3 analysis

# Root Cause Analysis

Root cause analysis methods for debugging incidents, process failures, and quality problems. Choose the method that matches the problem structure.

## Core Principle

Every surface symptom is the end of a causal chain. Treating the symptom leaves the chain intact. The goal is to find the systemic cause — a missing validation, unclear process, absent automation, or design choice.

## Five Whys

Iteratively ask "why" to trace from surface symptoms to fundamental systemic causes. The name "five" is a guideline — stop when you reach a process, system, or policy cause.

### Process
1. State the problem clearly — the specific symptom
2. Ask "Why did this happen?" — answer with the direct cause
3. For each answer, ask "Why?" again — trace one level deeper
4. Repeat until reaching a systemic cause (missing process, validation, automation, or design gap)
5. Validate by tracing forward — root cause → symptom should be a logical chain
6. If branches emerge, explore each independently
7. Propose solutions addressing the root cause — not intermediate answers

### Output
A causal chain from symptom to root cause with solutions tied to the root cause level.

## Fishbone / Cause-and-Effect

Systematic exploration of all potential causes across six categories using the Ishikawa method.

### The Six Categories

| Category | What to Examine |
|----------|----------------|
| **People** | Skills, training gaps, communication, team dynamics |
| **Process** | Workflows, procedures, standards, reviews |
| **Technology** | Tools, infrastructure, dependencies, config |
| **Environment** | Workspace, deployment targets, external factors |
| **Methods** | Approaches, patterns, architectures, practices |
| **Materials** | Data quality, third-party services, inputs |

### Process
1. State the problem clearly — the "head" of the fish
2. For each category, brainstorm potential causes (don't stop at the first one)
3. Identify which causes are symptoms vs. root causes
4. Cross-reference — mark causes that span multiple categories (systemic)
5. Prioritize — score by impact and likelihood
6. Propose solutions tied to specific root causes

### Output
A categorized cause map identifying root causes across six dimensions with prioritized solutions.
