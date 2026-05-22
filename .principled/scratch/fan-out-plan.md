# Fan-out Porting Plan

## Agent Assignments
| Agent | Plugin | CEK source (read-only) | tp target (write) | Skills | CEK lines |
|-------|--------|----------------------|-------------------|--------|-----------|
| 1 | tp-kaizen | context-engineering-kit/kaizen/3.0.0 | plugins/tp-kaizen | 7 | 2,375 |
| 2 | tp-sadd | context-engineering-kit/sadd/3.0.0 | plugins/tp-sadd | 10 | 10,039 |
| 3 | tp-sdd | context-engineering-kit/sdd/3.0.0 | plugins/tp-sdd | 5 | 4,069 |
| 4 | tp-review + tp-docs | context-engineering-kit/review+docs/3.0.0 | plugins/tp-review + tp-docs | 4 | 2,323 |
| 5 | tp-git + tp-tdd | context-engineering-kit/git+tdd/3.0.0 | plugins/tp-git + tp-tdd | 10 | 3,795 |
| 6 | tp-ddd + tp-tech-stack | context-engineering-kit/ddd+tech-stack/3.0.0 | plugins/tp-ddd + tp-tech-stack | rules | ~files |

## Refactoring Patterns (for all agents)

### 1. Decision Router
Every SKILL.md starts with:
```markdown
## Decision Router

IF {trigger condition} → {first action}
IF {combining with other workflow tools} → {synergy hint using semantic vocabulary, not plugin names}
```

### 2. No XML
`<task>` → `## Task`, `<context>` → `## Context`, `<role>` → `## Role`

### 3. No Threats
Replace "you will be killed" with professional quality constraints.

### 4. No Cross-Plugin References
Never name another plugin (no "tp-sadd", "sdd", etc.). Use semantic vocabulary:
- "implementation artifact" (not "sdd produces")
- "independent judge" (not "use sadd:judge")
- "test coverage" (not "use tdd")
- "decision record" (not "use fpf")

### 5. Delta Principle
Don't explain what Claude already knows. Remove:
- Verbose checklists that are standard practice
- Tutorial-style explanations of basic commands
- Theory citations (ARC, ACE, etc.)
- Redundant boilerplate

Keep only: what's unique about this skill's process.
