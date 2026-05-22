# Integration Architecture — Deep Design

## Current Architecture

```
taches-principled repo (Git-Fg/taches-principled)
├── .claude-plugin/
│   ├── plugin.json          # "taches-principled" plugin v0.2.0
│   └── marketplace.json     # Lists only "taches-principled" plugin
├── skills/                  # 8 skills (create-*, execute-*, subagent, simplify)
├── commands/                # 3 commands (debug, whats-next, simplify)
├── agents/                  # 7 shared agents
└── CLAUDE.md                # Development guide
```

## Target Architecture

```
taches-principled repo (Git-Fg/taches-principled)
├── .claude-plugin/
│   ├── plugin.json          # "taches-principled" plugin v0.3.0 (updated)
│   └── marketplace.json     # Lists ALL plugins (taches-principled + 11 new)
├── skills/                  # Existing 8 skills (untouched)
├── commands/                # Existing + new integration commands
├── agents/                  # Existing shared agents
├── plugins/                 # NEW: one directory per imported plugin
│   ├── sadd/
│   │   ├── .claude-plugin/plugin.json
│   │   └── skills/{judge,do-in-steps,...}/SKILL.md
│   ├── sdd/
│   │   ├── .claude-plugin/plugin.json
│   │   └── skills/{brainstorm,plan-task,implement-task,...}/SKILL.md
│   ├── reflexion/
│   │   ├── .claude-plugin/plugin.json
│   │   └── skills/{reflect,critique,memorize}/SKILL.md
│   ├── kaizen/
│   ├── fpf/
│   ├── review/
│   ├── docs/
│   ├── git/
│   ├── tdd/
│   ├── ddd/
│   └── tech-stack/
├── CLAUDE.md                # Updated for multi-plugin management
└── README.md                # Plugin ecosystem overview
```

## Plugin Naming Convention

| Directory    | Plugin Name                    | Description (routing signal)                    |
|-------------|--------------------------------|------------------------------------------------|
| (root)      | `taches-principled`            | Core: skills, subagents, plans, prompts         |
| `sadd/`     | `taches-principled-sadd`       | Structured agent-driven development + judging    |
| `sdd/`      | `taches-principled-sdd`        | Spec-driven development workflow                 |
| `reflexion/`| `taches-principled-reflexion`  | Self-reflection and quality critique             |
| `kaizen/`   | `taches-principled-kaizen`     | Continuous improvement analysis                  |
| `fpf/`      | `taches-principled-fpf`        | First-principles reasoning framework             |
| `review/`   | `taches-principled-review`     | Code and PR review with specialized agents       |
| `docs/`     | `taches-principled-docs`       | Documentation generation and writing quality     |
| `git/`      | `taches-principled-git`        | Git workflow automation                          |
| `tdd/`      | `taches-principled-tdd`        | Test-driven development                          |
| `ddd/`      | `taches-principled-ddd`        | Domain-driven design rules                       |
| `tech-stack/`| `taches-principled-tech-stack`| Technology-specific best-practice rules          |

## Semantic Synergy Vocabulary

Skills communicate through shared concepts about workflow stages — not by naming each other. When multiple plugins are installed, Claude composes them because they share vocabulary about these concepts:

### Shared Concepts (the "what")

| Concept | Meaning | Used By |
|---------|---------|---------|
| **implementation artifact** | Code, config, or docs produced during execution | sadd (judges it), sdd (produces it), review (reviews it), docs (documents it), tdd (tests it) |
| **judgment criteria** | Quality standards for evaluating artifacts | sadd (defines and applies), sdd (fulfills), review (checks) |
| **reflection output** | Self-critique or quality analysis | reflexion (produces), kaizen (improves from), fpf (validates) |
| **decision record** | Structured rationale for a choice | fpf (produces), all (consumes) |
| **test coverage** | Extent of behavioral verification | tdd (ensures), review (audits), sadd (verifies) |
| **specification** | Formal requirement definition | sdd (creates), implementer (follows), judge (evaluates against) |
| **action plan** | Ordered steps with verification | create-plans (produces), execute-plans (runs), kaizen (improves) |
| **improvement cycle** | Identify → Fix → Verify → Learn | kaizen (drives), reflexion (reflects), fpf (validates) |

### How Synergy Emerges

**Example: User runs `/sadd:judge` with both sadd and sdd installed**

The judge skill says: "evaluate implementation artifacts against quality criteria"
The sdd skill says: "produces implementation artifacts from specification"

Claude understands: "I should run sdd:implement-task to create artifacts, then judge them"
Because both skills describe their relationship to "implementation artifacts" without naming each other.

**Example: User runs `/reflexion:critique` with reflexion and fpf installed**

The reflexion skill says: "multi-perspective review of completed work"
The fpf skill says: "validate decisions against evidence"

Claude understands: "I can use FPF decision records as evidence in the critique"

## Refactoring Patterns Applied Per Plugin

### Pattern 1: Extract Common Meta-Judge (sadd)
CEK sadd has the same meta-judge pattern copy-pasted across 10 skills (~4,000 lines). The taches-principled version:
1. Defines meta-judge ONCE as a reference pattern in the skill body
2. Each skill says "uses meta-judge pattern" and documents ONLY what's unique (parallel vs sequential vs competitive)
3. Keeps the core value (independent evaluation) without the verbatim duplication

### Pattern 2: Remove Threatening Tone (sadd, reflexion)
Replace "you will be killed" with professional constraints:
- ❌ "If you use anything except sub-agents you will be killed immediately!"
- ✅ "You are the orchestrator. Your role is to dispatch agents, not execute tasks. Using tools directly violates this role."

### Pattern 3: XML → Markdown (sadd, reflexion)
Replace `<task>`/`<context>`/`<role>` XML tags with markdown headings:
- ❌ `<task>Execute...</task>`
- ✅ `## Task`
- The `<context>` block → `## Context`
- The `<role>` block → `## Role`

### Pattern 4: Add Decision Routers (all)
Prepend a decision router to every skill:
```markdown
## Decision Router

IF evaluating completed work → FIRST identify artifacts, THEN dispatch meta-judge + judge
IF combining with test results → Include test output as evaluation evidence
IF results fail threshold → iterate with feedback from judge report
```

### Pattern 5: Apply Delta Principle (all, especially git, docs)
Remove content Claude already knows:
- ❌ Explaining what `git diff` does (Claude knows this)
- ✅ Defining the workflow pattern: "Use git:commit when you need structured conventional commits with pre-commit checks"
- ❌ 1,044 lines explaining Strunk & White's Elements of Style
- ✅ ~150 lines: "Apply Strunk & White's writing rules — active voice, positive form, concrete language. Teach these rules by example in documentation."

## Estimated Size Reduction

| Plugin | CEK (lines) | taches-principled (est.) | Reduction |
|--------|-------------|------------------------|-----------|
| sadd   | 10,039      | ~5,000                 | 50%       |
| sdd    | 4,069       | ~2,500                 | 39%       |
| reflexion | 1,430    | ~800                   | 44%       |
| kaizen | 2,375       | ~1,500                 | 37%       |
| fpf    | 974         | ~600                   | 38%       |
| review | 619         | ~450                   | 27%       |
| docs   | 1,704       | ~500                   | 71%       |
| git    | 2,773       | ~1,500                 | 46%       |
| tdd    | 1,022       | ~600                   | 41%       |
| **Total** | **25,005** | **~13,450**           | **46%**   |

## Implementation Strategy

### Per-Plugin Process
1. Read CEK original SKILL.md
2. Apply refactoring patterns (1-5 above)
3. Write taches-principled version
4. Create plugin.json manifest
5. Create reference files if policy/mechanism split needed
6. Update marketplace listing
7. Verify: read SKILL.md alone → you know what to do

### Synergy Verification
For each plugin, verify:
- [ ] SKILL.md contains no references to other plugins' names or file paths
- [ ] SKILL.md uses shared vocabulary concepts for its workflow stage
- [ ] Plugin works when installed alone (no dependencies on other plugins)
- [ ] When installed alongside other plugins, workflow composition is natural

## Beyond Phase 0: Ecosystem-Level Improvements

Once all plugins are integrated, these cross-cutting improvements become possible:

1. **`taches-principled` core CLAUDE.md** — Document the shared vocabulary and synergy patterns so Claude understands the ecosystem
2. **`taches-principled` integration commands** — `/ecosystem-status`, `/synergy-map` to show installed plugins and their connections
3. **Shared evaluation pipeline** — Grading dimensions from create-skills apply to sdd implementations, sadd judgments, and kaizen analyses
4. **Unified decision framework** — fpf decision records feed into kaizen problem analysis, reflexion critique evaluates them
