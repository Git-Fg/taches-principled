---
name: ddd
description: "Analyze code structure, domain logic placement, and REST API design. Use when code quality or architectural nesting issues occur."
when_to_use: "Use when user asks about business logic placement, naming, transparency, function complexity, or REST endpoint modeling."
---

## Routing Guidance

- ARCHITECTURE: 'where does business logic go', 'too much nesting', 'too many parameters', 'function does too much', 'business logic in controllers'
- QUALITY: 'what should I name this', 'should I use a library', 'silent failure'
- TRANSPARENCY: 'hidden side effect', 'does this return or mutate', 'is this a side effect', 'mutation disguised as query'
- API: 'design REST API', 'API endpoint design', 'HTTP semantics', 'API versioning'

## Relationship to kaizen

ddd and kaizen are complementary, not redundant. They operate at different layers of the same concern (preventing bad code from entering the codebase).

**ddd** is a detailed analysis methodology with 4 modes (ARCHITECTURE, QUALITY, TRANSPARENCY, API) invoked when a specific structural question surfaces. It produces a written analysis, may spawn subagents (codebase scanner, endpoint auditor), and is selected per mode based on the question at hand.

**kaizen** is a lightweight 4-pillar filter applied to every code decision. It runs continuously in the background as guardrails — a developer does not "invoke" kaizen, they apply it as they write. No artifact, no analysis mode, no spawned subagent. The output is shaped code, not a written report.

**Conceptual layering:** kaizen is the immune system (always on, lightweight, prevents infection); ddd is the specialist (called in for specific diagnoses, produces a treatment plan).

## Decision Router

IF code structure or layering issue → ARCHITECTURE mode — ALWAYS spawn a **`tp-explorer`** subagent to map structure
IF naming or error handling issue → QUALITY mode
IF behavior visibility or data flow issue → TRANSPARENCY mode
IF REST API contract design, resource modeling, or versioning issue → API mode — ALWAYS spawn a **`tp-endpoint-auditor`** subagent to review contracts

---

# Mode: ARCHITECTURE

Structure code for maintainability through layered architecture and functional core principles.

**ALWAYS spawn a `tp-explorer` subagent to map structure and identify layering violations.**

### Implementation Guidelines

You MUST read `references/architecture-rules.md` BEFORE beginning architectural analysis to ensure compliance with layering rules, functional core principles, and physical code limits (nesting, size).

---

# Mode: QUALITY

Apply idiom checks: domain-specific naming, library-first approach, visible error handling.

## Domain Naming

Avoid generic names: `utils`, `helpers`, `common`, `shared`. Use domain-specific names reflecting behavior.

## Library First

Search for existing battle-tested libraries before writing custom code.

## Visible Errors

Never silently swallow exceptions. Every catch block needs typed handling and logging.

---

# Mode: TRANSPARENCY

Ensure code reveals its behavior at the call site through CQS and explicit data flow.

### Implementation Guidelines

You MUST read `references/transparency-patterns.md` BEFORE analyzing behavior visibility to ensure compliance with Command-Query Separation and transparency anti-pattern protections.

---

# Mode: API

Design REST API contracts with proper resource modeling, HTTP semantics, and versioning strategies.

**ALWAYS spawn a `tp-endpoint-auditor` subagent to review contracts.**

### Implementation Guidelines

You MUST read `references/api-design.md` BEFORE designing or auditing REST endpoints to ensure compliance with resource modeling rules, HTTP semantics, and versioning strategies.

---

## Reference Index

IF mapping code structure or layering → spawn **`tp-explorer`**
IF auditing REST API contracts or resource modeling → spawn **`tp-endpoint-auditor`**
