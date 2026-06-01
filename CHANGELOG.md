# Changelog

All notable changes are documented here.

## [0.11.1] — 2026-06-01

### Changed
- **Dissolved `scope-work` skill**: The hollow router (`add-task`/`refine-task`/`create-plans` routing) was removed — its three spoke files never existed and its triggers conflicted with `add-task`. Lifecycle skills now self-route via their existing CONTRAST frontmatter. References updated in `ideation`, `archive-plan`, `execute-plans`, and `refine`.
- **`sadd` DESIGN mode merged into `subagent-orchestration`**: Architecture design capability consolidated into the core `subagents` hub. `sadd` now redirects DESIGN to `subagent-orchestration` and focuses on COMPETE/JUDGE/EXECUTE/EXPLORE competitive evaluation. `sadd-architect` agent deleted as orphaned.
- **`kaizen` / `ddd` relationship clarified**: Both skills updated with explicit "Relationship" sections — `kaizen` as continuous design-time guardrails (the immune system), `ddd` as specialist structural analysis (called in for diagnosis). Mutual cross-references added.
- **Shared evaluation protocol extracted**: `execute-plans`, `refine-task`, and `implement-task` now reference `execute-plans/references/evaluation-protocol.md` for the shared judge pattern (chain-of-thought, MAX_ITERATIONS, 5.0/5.0 hallucination guard, scratchpad-first, weighted rubrics). Prevents drift across the three skills.
- **Memory/learnings handoff chain made explicit**: `archive-plan`, `refine` (MEMORIZE mode), and `rules-orchestration` (SYNC mode) now have explicit CONTRAST cross-references documenting the two-writers/one-reader chain feeding `.principled/memory/learnings.md`.

### Removed
- **`scope-work` skill** (4 files): `SKILL.md` + `references/{nano-spec,task-spec,roadmap}.md` — no spoke bodies, routing superseded by direct CONTRAST routing in lifecycle skills.
- **`sadd-architect` agent**: Orphaned when DESIGN mode moved to `subagent-orchestration`.

## [0.11.0] — 2026-06-01

### Added
- **scope-work skill** (canonical plugin): Unified entry point for task lifecycle — infers work scale from input and routes to `add-task` (nano-spec), `refine-task` (task-spec), or `create-plans` (roadmap). 261 lines across SKILL.md + 3 references.
- **New official docs**: `docs/official/permissions.md` and `docs/official/plugins/plugins-reference.md` (refreshed from source).

### Changed
- **Skills preloading philosophy — "Better too much than not enough"**: Retired the restrictive rule limiting skill preloading to evaluation/critique agents only. All potentially relevant skills MUST now be preloaded on all agent types (execution, research, explorer, etc.) for deterministic capability access. Properly authored skills use progressive disclosure — baseline context consumption is extremely low (~500 tokens frontmatter + body, references on-demand). AI retains full autonomy to lazy-load deeper reference files based on task requirements. Updated `docs/official/agent-skill-integration.md`, `plugins/taches-principled/skills/subagent-orchestration/SKILL.md`, and CLAUDE.md.

- **Skill file path referencing standardized**: Eradicated `{baseDir}` and `${CLAUDE_SKILL_DIR}` variables from all skill bodies and references (12 files). Established two canonical rules: (1) paths resolve within the skill's folder by default, (2) only SKILL.md may cite supporting files — reference files must never cross-cite. Converted all passive citations ("You can read", "See reference") to deterministic IF→BEFORE imperatives. Documented in CLAUDE.md and skill-authoring SKILL.md.
- **Native Tool Referencing standard**: Eradicated hardcoded tool names from orchestration directives across 11 files. `Write tool access` → `write access`, `"use the Read tool"` → `"use your native tools"`, etc. This ensures forward compatibility when the underlying API migrates (e.g., Task→Agent rename). Documented in CLAUDE.md and skill-authoring SKILL.md as a core best practice.
- **CLAUDE.md Skill Discovery**: Rewrote section as "Skill Discovery & Routing Metadata" — explicitly names routing-participant fields (description, when_to_use only), defines the "Metadata-Only Gate" concept, elevates 200-char rule, and adds Anti-Pattern "No Method Leaking" with bad/good examples.
- **Skill descriptions cleaned** (5 skills, jargon → user vocabulary):
  - `diagnose`: "A3, Five Whys, Fishbone, Stack Trace" → "Find root causes of recurring problems, failed fixes, and complex bugs"
  - `security`: "SAST, DEPENDENCY-AUDIT, SECRETS-DETECTION, COMPLIANCE" → "Scan for security vulnerabilities, exposed secrets, and broken authentication patterns"
  - `kaizen`: "YAGNI" → "avoid over-engineering"
  - `plan-do-check-act`: "PDCA cycle" → "Plan a change, try it at small scale, measure results"
  - `tdd`: "Red-Green-Refactor TDD" → "Write tests first, then implementation"
- **Must-do cleanup pass** (commit `55a6ba0`):
  - H1: Removed 2 tracked `.pyc` files; broadened `.gitignore` to `plugins/**/__pycache__/`
  - H2: Fixed broken CONTRAST references to non-existent `rule-propagator`
  - H4: Standardized `tp-force-multiplier` author to "Felix" across all 9 plugins
  - H5: Added `repository`, `license`, `keywords` to all marketplace.json entries
  - M3: Moved `commands-standard.md` to `docs/templates/command.md`
  - M4: Stripped redundant `shell: bash` from 33 files
  - M5: Stripped redundant `user-invocable: true` from 2 files
  - M6: Stripped dead YAML frontmatter from 15 templates/workflows
- **Plugin subagent rename for global uniqueness**: prefixed plugin subagents to avoid collisions when the `Agent` tool resolves across the marketplace:
  - `plugins/taches-principled/skills/create-plans/agents/{architect,explorer,implementer}` → `plan-{architect,explorer,implementer}`
  - `plugins/taches-principled/skills/rules-orchestration/agents/{rules-analyzer,rules-auditor,rules-integrator}` → `transcript-rules-{analyzer,auditor,integrator}`
  - `plugins/tp-sadd/agents/{architect,explorer}` → `sadd-{architect,explorer}`
  - `plugins/taches-principled/agents/implementer` → `global-implementer`
  - `plugins/taches-principled/skills/execute-plans/agents/researcher` → `execute-researcher`
- **README brittleness reduction**:
  - Stripped 4 magic-number count headers (`### 23 Skills`, `### 14 Commands`, `### 13 Agents`, `### 8 Marketplace Plugins`).
  - Collapsed 3 enumeration tables (Skills, Commands, Agents) to 5 curated examples each + filesystem pointers.
  - Fixed unclosed code block fence in "Full Marketplace Setup" (line 110).
  - Added `### README Hygiene` subsection to CLAUDE.md "Before Any Commit" self-check to make the discipline explicit.
- **CLAUDE.md description cap reconciliation**: changed self-check from `≤150 chars` to `≤1,536 chars` (combined `description` + `when_to_use`) to match the official cap per `docs/official/skills.md`.

### Removed
- **Orphan agent files** (untracked, unreferenced, superseded): `global-rules-{analyzer,auditor,integrator}.md` — the `transcript-rules-*` agents in `rules-orchestration/` do this work.
- **Empty directories**: `plugins/taches-principled/rules/`, `plugins/tp-vps-governance/agents/`.
- **Tracked Python bytecode** (2 files in `tp-force-multiplier/hooks/__pycache__/`).
- **Stale `.gitignore` line** referencing the removed `launch-subagent` skill directory.

## [0.10.0] — 2026-05-29

### Added
- **tp-meta plugin**: Session meta-review and behavioral analysis plugin with 3 skills, 1 agent, and 3 commands.
  - `session-inspect` skill: parses Claude Code session transcripts (JSONL) into structured data — tool calls, errors, cost, loaded plugins, behavioral events.
  - `meta-review` skill: reviews sessions for behavioral anti-patterns, investigates root causes with parallel subagent fan-out, and produces scoped findings.
  - `meta-issue` skill: creates GitHub issues from meta-review findings, sanitized for public sharing with privacy audit gate.
  - `meta-reviewer` agent: diagnostic agent that reads JSONL transcripts and identifies tool misuse, skipped verifications, and instruction-following failures with root cause scoping (PLUGIN/USER-FILE/ENVIRONMENT/MODEL).

## [0.9.0] — 2026-05-27

### Added
- **tp-force-multiplier plugin**: Hook-driven coaching plugin that steers Claude to use subagents and skills more via real-time semantic coaching. Three hooks: SessionStart (lightweight hint), Stop (pattern detection with 5+ tools), PostCompact (pre-pressure reminder). No tool injection, zero blocking, semantic patterns only.
- **CLAUDE.md rules**: Added 4 new rules for instruction clarity
  - Deterministic Language for Execution Rules (strong vs soft language calibration)
  - Infrastructure Assumption Rule (verify prerequisites before dependent operations)
  - Path Configuration Rule (use arguments, not hardcoded paths)
  - Agent Tool Contract Rule (tools must match stated capabilities)

### Changed
- **references/official/**: Updated hooks.md, skills.md, subagents.md, commands.md, and marketplaces.md with marketplace conventions (effort/effort field, shell: bash, hub skills, {baseDir} syntax, CONTRAST sections, maxTurns:15, memory:local, canonical spawn vocab, command format)

### Changed
- **Lifecycle hints removed**: Removed soft-orchestration lifecycle hints from add-task, create-prompts, implement-task per debate WEAK verdict — CONTRAST sections and decision routers are sufficient for routing
- **tp-tdd/tdd**: Added CONTRAST section clarifying distinction from test strategy skill
- **refine-task**: Trimmed business analysis section (70 lines removed) — procedure condensed to principle
- **implement-task**: Trimmed Pattern B/C detailed walkthroughs (150 lines removed) — step-by-step scripts condensed to policy

### Fixed
- **tp-force-multiplier hooks.json**: Fixed format from array-based to nested object structure per Claude Code hooks reference — changed `{"hooks": [{event:..., ...}]}` to `{"hooks": {"EventName": [{matcher:..., hooks:[...]}]}}`
- **Routing BLOCKERs** (3): Removed overlapping trigger phrases causing routing conflicts
  - refine-task: removed "plan this out", "/plan", "make this actionable", "break this down into steps"
  - execute-plans: removed "execute" from description and when_to_use
- **Failure signal BLOCKERs** (2): Added missing Failure Signal sections
  - ideation: added no-viable-options/user-abandoned/scope-too-broad failure modes
  - claude-headless: added session-timeout/permission-denied/tool-unavailable failure modes
- **Git availability**: Added `git --version` checks to implement-task and refine-task
- **Judge tool mismatch**: Added Write tool to judge.md for filesystem communication
- **TDD Iron Law contradiction**: Removed "write tests" from TDD triggers (Iron Law forbids without failing test first)
- **tp-force-multiplier hooks**: Fixed prescriptive language → advisory ("Pattern: X suggests Y")
- **tp-sadd agent tools**: Added Bash to meta-judge/judge, removed unused Edit from generator
- **create-plans/agents**: Added missing spawn footer to implementer

### Changed
- **METHOD over-specification** (249 lines removed across 4 skills):
  - fpf: 7-step procedure → principle statements
  - diagnose: A3/Five Whys/Fishbone condensed
  - create-plans: 11-item fan-out → 4 principles
  - execute-plans: Strategy A 12-step → 5 principles, deviation rules trimmed
- **Trigger optimization** (5 skills improved):
  - tp-fpf: removed jargon (ADI, R_eff), lead with user vocabulary
  - multi-agent-patterns: rewritten for cold-start clarity
  - tp-ddd: modes moved out of first line
  - security: triggers capped at 3-4 per mode
  - tp-sadd: softened jargon ("meta-judge" → "quality verification")
- **METHOD reduction round 2** (1,212 lines removed across 6 skills):
  - implement-task: 520→181 (-65%), subagent-orchestration: 592→213 (-64%)
  - create-prompts: 493→187 (-62%), execute-prompts: 273→149 (-45%)
  - add-task: 94→58 (-38%), ideation: 94→66 (-30%)
- **Skill discovery optimization**: Added CLAUDE.md section on reliable triggering, hook limitations, validation protocol

## [0.7.0] — 2026-05-25

### Added
- **rules-orchestration skill**: Full lifecycle orchestration hub (6 modes: DESIGN/BUILD/ANALYZE/SYNC/REVIEW/EXECUTE) — orchestrates multiple rule sources into unified rule sets with fan-out/subagent coordination, 3-phase plan, 8 tasks committed

### Changed
- **Lifecycle continuation handoffs**: Implemented 6 lifecycle chains across ideation→add-task→refine-task→implement-task→create-prompts→execute-prompts with soft-orchestration pattern via description hints

## [0.6.0] — 2026-05-25

### Added
- **5 new skills**: Integrated from local ~/.claude/skills/
  - `claude-headless` — Claude Code headless execution patterns, evaluation pipeline anchor
  - `multi-agent-patterns` — Architecture design patterns (supervisor/swarm/hierarchical)
  - `tool-design` — Agent tool and MCP integration design with production evidence
  - `security` — SAST, dependency audit, secrets detection, compliance (OWASP Top 10)
  - `test` — Test strategy decisions (coverage, mock strategy, fixtures, property-based)

### Changed
- **subagent-orchestration**: Merged with `subagent-creator` — now a 2-mode hub (DESIGN/ORCHESTRATE)
- **plugin.json**: Version bumped to 0.6.0, description updated with new capabilities, new keywords
- **Skill count**: 20 → 25 skills (within optimal 22-28 range)

### Removed
- **subagents**: Deleted as duplicate — `subagent-orchestration` is now the canonical hub
- **14 absorbed skills** (from 0.5.0): `reflexion`, `write-concisely`, `create-subagents`, `subagent-orchestration` (root), and 10 individual tp-* skill files superseded by hub equivalents

## [0.5.0] — 2026-05-24

### Added
- **6 new commands**: `/improve`, `/critique`, `/learn`, `/polish`, `/orchestrate`, `/design-subagents` — direct capability triggers routing to hub decision routers
- **Hub-and-spoke consolidation**: reduced marketplace from 34 skills to 20 (41% reduction, 5,952 lines removed)
  - Root: `refine` now a 5-mode hub (SIMPLIFY/REVIEW/CRITIQUE/MEMORIZE/POLISH) absorbing `reflexion` + `write-concisely`
  - Root: `subagents` now a 2-mode hub (DESIGN/ORCHESTRATE) absorbing `create-subagents` + `subagent-orchestration`
  - tp-sadd: 5 skills merged into `sadd` hub
  - tp-git: 4 skills merged into `git` hub
  - tp-fpf: 3 skills merged into `fpf` hub
  - tp-ddd: 3 skills merged into `ddd` hub

### Changed
- **CLAUDE.md**: comprehensive audit — Meta-Rule rewritten for human maintainers, dispatch/launch terminology standardized to spawn, reflexion/refine narrative corrected, direct-language principle enforced, Self-Check strengthened, logical weaknesses fixed, missing definitions added
- **Commands**: 6 existing commands updated with hub skill routing, all 12 commands verified against commands-standard.md

### Removed
- **14 absorbed skills**: `reflexion`, `write-concisely`, `create-subagents`, `subagent-orchestration` (root), and 10 individual tp-* skill files superseded by hub equivalents
- **`coordination.py`** script and design reference files consolidated into hub skill bodies

### Fixed
- **Token Economy**: removed contradictory line advising writing to non-loaded CLAUDE.md
- **Subagent spawn instructions**: all inline tool lists replaced with role + outcome descriptions
- **Cross-references**: all stale references to deleted skills cleaned before deletion
- **marketplace.json**: root skill count corrected 18→15

## [0.4.1] — 2026-05-23

### Fixed
- **tp-ddd plugin**: Converted 14 invalid rules (in `rules/` with `title`/`impact` frontmatter) to 12 valid skills (in `skills/` with `name`/`description`/`when_to_use` frontmatter)
- **tp-ddd**: Merged overlapping skills (call-site-honesty→explicit-side-effects, clean-architecture-ddd→separation-of-concerns)
- **tp-ddd**: Improved when_to_use triggers with natural developer phrases

### Changed
- **tp-ddd**: Collapsed 12 skills → 3 hub skills (code-transparency, code-architecture, code-quality) via multi-agent consolidation pipeline
- **tp-ddd**: description updated to reflect new skill structure

### Fixed
- **tp-ddd**: Lost concepts (early returns, file size limits) restored after Skeptic-Advocate reconciliation

## [0.4.0] — 2026-05-23

### Changed
- **marketplace.json**: Bumped to 0.4.0, 7 entries (root + 6 separate plugins)
- **plugin.json**: Version remains 0.4.0
- **CHANGELOG**: Removed 68 skills count claim (was inaccurate)

### Added
- **when_to_use frontmatter**: Added to all 34 skills with user-quoted trigger phrases and IMMEDIATELY/FIRST/BEFORE conditionals

### Fixed
- **sadd-dispatch**: Added missing when_to_use section entirely
- **tp-sadd/tp-sdd plugins**: All skills now have proper trigger phrase quoting and temporal markers (tp-sdd deprecated, consolidated into root)

### Refactored
- **All 34 skill descriptions**: Normalized to third-person framing with trigger phrases (note: official docs confirm verb-first is valid)
- **Agent definitions**: XML Structure Rules converted to markdown Structure Conventions

## [0.3.0] — 2026-05-22

### Added
- **22 root skills**: Integrated review (review-pr, review-local-changes), kaizen (kaizen, analyse, analyse-problem, cause-and-effect, plan-do-check-act, root-cause-tracing, why), and docs (update-docs, write-concisely) into root plugin
- **6 separate plugins**: Ported from context-engineering-kit — tp-sadd (9 skills), tp-fpf (3 skills), tp-git (4 skills), tp-tdd (1 skill), tp-ddd (14 rules) (tp-sdd deprecated and consolidated into root)
- **Decision routers**: All 60 skills now have IF/THEN decision routers at top
- **Semantic vocabulary**: Cross-plugin synergy through shared workflow vocabulary (no plugin name references)
- **Integration architecture**: `.principled/plans/BRIEF.md`, `ROADMAP.md`, `scratch/integration-architecture.md`, `scratch/fan-out-plan.md`
- **Phase summaries**: `.principled/plans/phases/00-scaffold/SUMMARY.md`, `01-reflexion/SUMMARY.md`

### Changed
- **plugin.json**: Bumped to 0.3.0, updated description with full lifecycle scope
- **marketplace.json**: Bumped to 0.4.0, 7 entries (root + 6 separate plugins)
- **CLAUDE.md**: Added Plugin Management section for multi-plugin marketplace operations

### Fixed
- Cross-plugin naming violations: all 60 skills use semantic vocabulary instead of plugin name references
- XML tags removed from all ported content (markdown headings only)
- Threatening language removed from SADD and reflexion skills (professional tone)
- Meta-judge pattern deduplicated across 10 SADD skills (was 4,000 lines of copy-paste)

## [0.2.0] — 2026-05-22

### Added
- **code-simplify skill**: Simplification pipeline with 5 stages (Extract & Name, Reduce Nesting, Remove Duplication, Eliminate Dead Code, Replace State Machines with Data), anti-patterns with wrong/right pairs, inline agent template, Policy/Mechanism framing, numeric thresholds, and language-specific references for JS/TS, Python, Go, and Ruby
- **code-simplify skill**: `references/language-patterns.md` with language-specific patterns
- **code-simplify skill**: `references/simplification-scope.md` with scope boundaries and file ownership rules
- **commands/simplify.md**: `/simplify` command for direct invocation with optional file-pattern argument
- **plugin.json**: Bumped to 0.2.0, added code-simplify keyword

## [0.1.0] — 2026-05-22

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
  - `grader.md` (161 lines): Teaching effectiveness rubric with 4 dimensions (Routing Signal, Delta Clarity, Teaching Posture, Anti-Pattern Quality)
  - `comparator.md` (115 lines): Skill version comparison for delta analysis
  - `analyzer.md` (96 lines): Synthesizes evaluations into prioritized improvement path
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
- **subagent-orchestration skill**: Integrated as 7th skill with RACE framework, five parallel patterns, three automation layers, memory architecture, and failure modes
- **create-subagents skill**: Added plugin scope gotcha (hooks/mcpServers/permissionMode silently ignored for plugin subagents), Task→Agent renaming note (v2.1.63), missing frontmatter fields (skills, memory, background, maxTurns, isolation)
- **create-skills skill**: Added 3-level progressive disclosure pattern (Level 1 ~100 tokens always, Level 2 ~5k on trigger, Level 3 0 via bash injection)
- **create-plans skill**: Added bash injection = 0 context cost pattern
- **execute-plans skill**: Added Explorer Subagent Protocol for investigation tasks via scratchpad coordination
- **execute-prompts skill**: Added Explorer Subagent Protocol and Thought/Action/Observation anti-pattern
- **create-skills skill**: Added Fresh Context Warning for subagent spawning (no inheritance from orchestrator)
- **all root agents**: Added spawn footers and failure signal sections to all 7 root-level agents

### Fixed
- **execute-plans skill**: Fixed broken {baseDir} reference — orchestration-patterns.md now uses natural language (file lives in create-plans skill)
- **execute-plans skill**: Fixed critic agent name collision with create-plans (critic → execute-critic)
- **README.md**: Fixed skill count (6→7) and agent count (4→7), added subagent-orchestration rows
- **CLAUDE.md**: Fixed stale version example (1.1.0→0.1.0)
- **marketplace.json**: Added missing top-level description for validation cleanliness
- **CHANGELOG.md**: Fixed stale agent line counts for comparator.md and analyzer.md
- **execute-plans skill**: Use agents/critic.md template for milestone reviews
- **create-plans skill**: Resolve inconsistencies found during reference review
- **create-plans skill**: Resolve critical issues found during reference review
- **execute-plans skill**: Fixed agent template paths to use {baseDir} for plugin portability
- **create-plans skill**: Fixed agent folder references to use {baseDir} for plugin portability
- Corrected GitHub repo references across plugin

### Changed
- **Version**: Bumped from 0.0.2-alpha to 0.1.0 (plugin now has 7 skills, 7 root agents, evaluation pipeline)
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
