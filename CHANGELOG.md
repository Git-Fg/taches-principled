# Changelog

All notable changes are documented here.

## [Unreleased]

### Added
- **create-skills skill**: Decision Router with IF→FIRST/IMMEDIATELY/BEFORE imperative conditionals at top
- **create-skills skill**: Five skill categories with inspirational examples (Constraint/Guardrail, Orchestration, Domain Expertise, QA, Creative Direction)
- **create-skills skill**: Added Success Criteria section with measurable outcomes
- **create-skills skill**: Added `trigger-benchmark.md` reference (305 lines): 20-query framework, exit criteria, overfitting detection, headless testing method
- **create-skills skill**: Added Automated Checks section to `skill-self-testing.md`: programmatic pre-commit validation script
- **create-skills skill**: Added `scripts/run_trigger_benchmark.py`: automated 20-query test harness with streaming JSONL detection
- **create-skills skill**: Added `scripts/grader-output-template.md`: structured output format for grader → analyzer pipeline
- **execute-plans skill**: Decision Router with strategy selection based on checkpoint types
- **execute-plans skill**: Added Numeric Thresholds section
- **agents/**: New grader, comparator, and analyzer agents for evaluation pipeline
  - `grader.md` (162 lines): Teaching effectiveness rubric with 4 dimensions (Routing Signal, Delta Clarity, Teaching Posture, Anti-Pattern Quality)
  - `comparator.md` (145 lines): Skill version comparison for delta analysis
  - `analyzer.md` (140 lines): Synthesizes evaluations into prioritized improvement path
- **agents/skill-auditor.md**: Added Trigger Benchmark Integration section; added Evaluation Pipeline section documenting multi-agent evaluation workflow
- **CLAUDE.md**: Added Evaluation Pipeline section documenting the grader/comparator/auditor/benchmark/analyzer multi-agent system
- **create-subagents skill**: Multi-agent patterns import from taches-modernized research
  - `references/gotchas.md` (443 lines): Eight critical production gotchas (supervisor bottleneck with 3-5 worker cap, 15x token cost, sycophantic consensus, agent sprawl, telephone game, error propagation cascades, over-decomposition, missing shared state)
  - `references/fault-tolerance.md` (310 lines): Circuit breaker pattern, checkpoint/resume, exponential backoff, idempotent operations
  - `references/token-economics.md` (230 lines): Real multi-agent cost breakdown (~15x baseline), when justified, model selection vs token budget
  - `references/consensus.md` (386 lines): Weighted voting (confidence × expertise), debate protocol, adversarial critique, convergence detection
- **create-subagents skill**: Extended decision router with 5 new routes to new references
- **create-subagents skill**: Added Multi-Agent Gotchas section with hard cap enforcement
- **orchestration-patterns.md**: Added Swarm pattern (peer-to-peer), forward_message pattern (telephone game mitigation), 4 new anti-patterns
- **context-management.md**: Added Context Isolation Mechanisms (3-mechanism taxonomy), Context Degradation Signals
- **execute-plans skill**: Added supervisor bottleneck warning with 3-5 worker cap enforcement
- **create-plans skill**: Added context degradation signals to scope-estimation.md
- **execute-plans skill**: Critical fixes from second round of critic review
- **create-skills skill**: Comprehensive improvements from critic review
- **create-skills skill**: Now teaches bundled agents pattern
- **create-skills skill**: Native task lists + semantic-first skill refactor
- **execute-plans skill**: Added agents/critic.md for milestone self-review
- **create-plans skill**: Added agents folder with subagent prompt templates
- **execute-plans skill**: Added env-variable-pattern reference doc for portable skill paths

### Fixed
- **execute-plans skill**: Use agents/critic.md template for milestone reviews
- **create-plans skill**: Resolve inconsistencies found during reference review
- **create-plans skill**: Resolve critical issues found during reference review
- **execute-plans skill**: Fixed agent template paths to use {baseDir} for plugin portability
- **create-plans skill**: Fixed agent folder references to use {baseDir} for plugin portability
- Corrected GitHub repo references across plugin

### Changed
- **CLAUDE.md**: Reduced from ~475 lines to ~178 lines by moving teaching content to skills ( marketplace operations only)
- **create-plans skill**: Complete remaining deferred improvements from reference review
- Marked all deferred improvements from reference review as resolved
- **create-plans skill**: Remove per-file version tracking (anti-pattern)

## [0.0.2-alpha]

### Added
- **create-plans skill**: Added `agents/` folder with subagent prompt templates (explorer, researcher, architect, implementer, verifier)
- **create-plans skill**: Added fan-out exploration pattern with parallel subagent spawning guidance
- **create-plans skill**: Natural language instructions for reading agent prompts and filling placeholders
- **execute-plans skill**: Added `agents/critic.md` for formalizing milestone self-review pattern
- **CLAUDE.md**: Added Semantic-First Skill Design section with progressive disclosure architecture

### Fixed
- **marketplace.json**: Changed `source.github.repo` to `source.source: "url"` with full git URL — `felixhopper` repo does not exist, corrected to `Git-Fg/taches-principled`
- **README.md**: Replaced all `felixhopper` references with `Git-Fg` (lines 13, 125)
- **README.md**: Corrected skills count (6 skills now) and commands count (10 → 2)
- **execute-plans/SKILL.md**: Removed duplicate "Strategy B" section header in Strategy A content
- **sequential-execution.md template**: Fixed `Sonnets/Large Context Executor` → `Sonnet` (valid model name)
- **autonomous-execution.md**: Removed duplicate rollback sections, clarified revert scope
- **autonomous-execution.md**: Removed invalid Task() spawn syntax, replaced with plain-text instruction
- **autonomous-execution.md**: Added spawn footer to worker prompt structure
- **segment-execution.md**: Added milestone self-review section, integrated critic.md reference, added spawn footer
- **sequential-execution.md**: Replaced inline deviation rules with reference to deviation-rules.md
- **execute-phase.md**: Added YAML frontmatter per skill anatomy standards
- **execute-prompts/SKILL.md**: Removed Task tool prose references, replaced with semantic delegation language
- **cli-automation.md**: Marked Railway as deprecated (discontinued 2024), added Cloudflare/AWS/GCP/Bun platforms
- **milestone-management.md**: Updated all 2025 dates to 2026, added hotfix branch model
- **plan-format.md**: Removed duplicate Summary Output section, cross-referenced SKILL.md, added Checkpoint field
- **checkpoints.md**: Added human-readable comment pattern, added Escalation and Timeout section
- **scope-estimation.md**: Defined context usage metrics, added sequential chain limit
- **create-plans SKILL.md**: Simplified fan-out description, removed Task: spawn examples
- **create-plans/references/**: Removed per-file version tracking (anti-pattern documented in CLAUDE.md)

## [0.0.1-alpha]

### Added
- **create-prompts skill**: Creates executable XML-structured prompts for Claude Code sessions
  - Adaptive intake gate with task type detection
  - Contextual questioning with templates (dashboard type, auth method, etc.)
  - Decision gate loop until user confirms
  - Single/parallel/sequential prompt generation
  - XML patterns for coding/analysis/research tasks
- **execute-prompts skill**: Executes prompts via delegated sub-tasks
  - Policy vs. Mechanism framing for strategy selection
  - Single/parallel/sequential execution via Task tool
  - Critical constraint: parallel Task calls in single message
  - Argument parsing and file resolution
  - Archival to `./prompts/completed/` and git workflow
- **create-prompts/workflows/execute-prompt.md**: Workflow reference for prompt execution

### Changed
- README updated: Skills count 4 → 6, Policy/Mechanism table expanded

## [1.1.0]

### Changed
- Renamed from `taches-modernized` to `taches-principled`
- All 4 skills enhanced with Policy/Mechanism framing sections
- All 4 skills enhanced with Anti-Patterns sections
- All 4 skills enhanced with Numeric Thresholds tables
- README updated with Skill Ecosystem dependency map
- README updated with Policy vs. Mechanism table

### Removed
- MCP server creation skill and command (builds on existing MCP tooling instead)

### Fixed
- create-hooks: UserPromptSubmit added to events table
- create-hooks: malformed hookSpecificOutput JSON fixed
- create-hooks: broken jq syntax in prettier example
- create-hooks: broken reference to user-gates.md removed
- create-plans: missing frontmatter added
- create-subagents: missing frontmatter added, broken file references removed
- create-mcp-servers: Rule 2 (cwd vs --directory) clarified
- All reference files gained frontmatter

## [1.0.0] — Initial release

### Added
- 4 principle-based skills: create-skills, create-subagents, create-hooks, create-plans
- 8 slash commands: /create-skill, /create-subagent, /create-hook, /create-plan, /audit-skill, /audit-subagent, /debug, /whats-next
- 3 agent types: code-reviewer, skill-auditor, subagent-auditor
- plugin.json and marketplace.json for GitHub marketplace
- MIT license

### Principles
- Goals over procedures
- Principles over steps
- Trust Claude's intelligence
- Concise by default
- Gotchas, not rules
