# Taches Principled — Development Guide

**For maintainers only.** This file contains development practices and internal conventions for working on this repository. It is NOT loaded by Claude Code when this plugin is installed — it exists only in the source repository. A Claude instance that installs this plugin from the marketplace will never see this file.

Treat every section below as knowledge transfer from a human who worked on this codebase to future human maintainers. Claude Code instances that install the plugin learn from the plugin's skill descriptions, agent definitions, and command files — not from this guide.

When generic agents and specialized inline versions cover the same capability, prefer the generic agent. Specialized inline agents add value only when they teach Claude something the generic version cannot — different workflow, domain-specific judgment, or context that would require extensive re-prompting. If a specialized agent's body is the same as the generic equivalent with different names, delete it and use the generic one. The generic agent becomes the canonical version; domain-specific knowledge lives in the skill that invokes it, not in the agent itself.

An agent is not orphaned simply because it is not explicitly named — generic agents like reviewer, critic, and code-reviewer are discovered through semantic routing, not citation. A skill that says "verify quality before delivery" semantically routes to reviewer without naming it. The agent is the canonical resolution for that capability pattern. An agent is only orphaned when it has no semantic hook — no skill describes a capability it would resolve.

---

## Core Design Principle

Every artifact in this marketplace is consumed by a Claude Code instance that starts with zero context about this project — no prior conversation, no session history, no external knowledge of what the plugin does or why it exists. That instance is smart, autonomous, and non-deterministic. It will reason about what the plugin does from the descriptions it can read.

Design every skill, agent, and command as if the first thing that will happen is: Claude loads into a completely fresh session, reads only this plugin's files, and must decide what to do with it.

Ask: What will that instance understand from the skill descriptions alone? Which skill will it invoke for a given task? Does the routing make sense without external context? Does the description give enough trigger signal for the right skill to fire? Does the body teach judgment or just prescribe steps? Does the agent know its role without being told what other agents exist?

If the answer to any of these is "Claude would have to guess" — the artifact needs more signal. If it would make a reasonable choice — trust the model and stop adding instructions.

High trust means: write descriptions that route correctly, then stop. Don't add fallbacks, disclaimers, or routing logic for edge cases the model can handle. Let the model figure out the non-deterministic parts it excels at.

---

## Orchestration Principle

This marketplace is designed for a **costly, highly-capable main agent** orchestrating **cheap, fast subagents** in parallel with critique loops.

**The model:**
- Main agent (Sonnet/Opus) owns cognition — planning, decomposition, routing, aggregation, synthesis. This is the expensive brain that makes judgment calls.
- Subagents (Haiku or fast Sonnet) own execution — exploration, research, implementation, verification, critique. These are cheap workers that run in parallel.
- Critique loop: spawn a critic subagent after each milestone, loop until no HIGH findings remain
- The main agent never does work a subagent can do faster in parallel.

**When to spawn subagents (everything non-trivial):**
- Exploration: 3-5 parallel with disjoint scope
- Research: per-question subagents
- Implementation: per-task subagents for independent work
- Verification: per-segment subagents
- Critique: per-milestone subagents reviewing output
- Decision analysis: per-checkpoint subagents evaluating options

**When the main agent acts directly:**
- Lightweight edits (1-2 files, trivial change)
- Reading and synthesizing subagent output from scratchpad
- Making judgment calls between competing subagent recommendations
- Final aggregation, summary writing, and commit

**The rule:** If a task takes more than 5 minutes of inline work or touches more than 2 files, spawn a subagent for it (empirical heuristic — tuned to the point where coordination overhead costs less than context consumption). Never burn expensive main-agent context on work a cheap subagent can do.

### Subagent-First Execution Contract

**Default to subagents. Inline execution is the exception, not the norm.**

This contract inverts the usual framing. Most skills treat subagent spawning as an optional optimization ("spawn if the task is big"). That framing fails because Claude's default mode is to execute inline — it requires less cognitive effort and activates automatically. To override this default, the skill must make subagent spawning the path of least resistance.

**The contract:**

| Work Type | Default Mode | Exception (inline allowed) |
|-----------|-------------|---------------------------|
| Exploration | Spawn explorer subagent(s) | Directory listing of <5 files |
| Implementation | Spawn implementer subagent(s) | 1-file edit with <10 lines |
| Research | Spawn researcher subagent(s) | Single web search query |
| Verification | Spawn verification subagent(s) | Running a single test command |
| Critique/Review | Spawn critic subagent(s) | Glance-check of trivial output |
| Brainstorm/Ideate | Spawn ideation subagent(s) | Never — always parallel |
| Debate/Compare | Spawn competing subagent(s) | Never — always parallel |
| Reflection | Spawn self-review + self-critic subagents | Never — always after artifact |

**Why this works:** The skill body states the default mode as a standing instruction, not a conditional recommendation. Claude reads "Spawn a researcher subagent to investigate" as the intended path, not "Consider spawning if the task seems large" as a suggestion it can skip.

**Minimal spawn instruction pattern (copy-paste into skill bodies):**

```
## Execution Mode

**Default: subagent delegation.** For [exploration/implementation/research/etc.], 
spawn a [role] subagent with the task scope below. The main agent synthesizes 
results; it never performs the work inline.

**Spawn pattern:**
- Scope: [specific files/questions to address]
- Role: [explorer/implementer/researcher/critic/etc.]
- Model: [haiku/sonnet based on complexity]
- Output: [what the subagent must return]

After subagent returns: synthesize findings, then spawn follow-up subagents 
for verification and critique. Loop until no HIGH findings.
```

**Anti-pattern:** "If the task is complex, consider using subagents." This is optional language — Claude's default mode wins. Use declarative language: "Spawn subagents for [task type]."

**The 5-minute/2-files heuristic is dead.** Replace it with: **"If the skill loaded, the work is non-trivial by definition — spawn subagents."** The skill exists precisely because the task exceeds trivial inline execution. Trust the skill's own existence as the signal.

### Transformer Mandate

A system cannot transform itself — this is a protocol principle, not a capability limitation:

- AI generates options with evidence scores
- Human makes the final decision
- **Autonomous architectural choices are a protocol violation** — the AI suggests and scores, never commits unilaterally on structural decisions

This principle applies to decision-making workflows; execution autonomy is separate and appropriate for implementation tasks.

### Deterministic Language for Execution Rules

**Execution-critical requirements use strong language (ALWAYS, NEVER, MUST). Exploratory guidance uses soft language (consider, prefer, typically).**

**Strong language** — Non-negotiable execution requirements:
- "ALWAYS verify git availability before spawning git-dependent subagents"
- "NEVER hardcode file paths in skill bodies"
- "MUST use `{baseDir}` for skill-internal file references"

**Soft language** — Heuristics and guidance:
- "Consider using parallel subagents for exploration"
- "Prefer Haiku for execution, Sonnet for reasoning"

**The test:** If removing the rule would produce visibly wrong output, use strong language. If removing it just means a different reasonable approach, use soft language.

**Anti-pattern:** "should", "can", "may" in execution-critical contexts — these signal optionality where the skill actually requires the behavior.

### Infrastructure Assumption Rule

**ALWAYS verify infrastructure prerequisites before executing dependent operations.**

Skills that rely on external tools (git, gh, npm, python, etc.) must check availability before assuming the environment provides them. This prevents mid-execution failures where the skill's logic is sound but the environment is missing a dependency.

### Path Configuration Rule

**Use command arguments and environment variables for paths — never hardcode absolute paths.**

- `{{CLAUDE_WORKING_DIR}}` for the current working directory
- `$ARGUMENTS` for user-provided path parameters
- `{baseDir}` for skill-internal file references (resolves at load time)
- Bash environment variables (`$HOME`, `$PWD`) for shell operations

This ensures skills work across environments: the same skill executes correctly whether the project is at `/work/repo`, `/home/user/project`, or any other path.

### Agent Tool Contract Rule

**An agent's declared tools MUST match its stated capabilities.**

When an agent claims to write findings to disk, it needs the Write tool. When it claims to execute shell commands, it needs Bash. If the capability exists in the description but the tools field is missing, the agent cannot fulfill its contract.

**The test:** Read the agent's description, then check its tools. Every capability described must have a corresponding tool available.

### Tool Scoping Fields — Critical Distinction

Three fields control tool access, each with different semantics:

| Field | Artifact | Effect | When Omitted |
|-------|----------|--------|-------------|
| `tools:` | Agent definitions | **Hard allowlist** — only listed tools accessible (Strictly filtered from registry; C1) | Inherits all tools |
| `allowed-tools:` | Skills, Commands | **Pre-approval** — partial enforcement (Write blocked in auto-mode, but Edit/Agent/Skill bypass; C8) | Normal permission settings apply |
| `disallowed-tools:` | Skills | **Hard block** — removes specific tools from pool | No tools blocked |

**Common mistake:** Treating `allowed-tools` as a security boundary. It only skips permission prompts — every tool remains callable. For true restriction, use agent `tools:` allowlists or skill `disallowed-tools:`.

**SDK & Bypass caveat:** `allowed-tools` only works in Claude Code CLI. Even there, empirical verification shows tools like `Edit`, `Agent`, and `Skill` routinely bypass the restriction while `Write` is caught. SDK consumers must use their own `allowedTools` parameter.

### Skill Discovery & Routing Metadata

**Discovery is a "Metadata-Only" Gate.** Claude decides which skill to load based **exclusively** on the text pre-injected into its system prompt. At the moment of routing, the skill **body is invisible.**

**Routing Participants — Fields Only:**
- **Skills:** `description` + `when_to_use`
- **Agents:** `description` (NOT the body prompt)
- **Commands:** `description`

**Nesting Limit:** The automatic skill discovery mechanism scans only **1 level deep** (`skills/<name>/SKILL.md`). Skills nested 2+ levels deep (`skills/<category>/<name>/SKILL.md`) will not be discovered by the `Skill` tool directly and require a manual `Glob` scan fallback.

**Metadata vs. Body Strategy:**
- **Metadata (The "Hook"):** Must use **User Vocabulary**. Speak how the user thinks (e.g., "Find the bug," "Clean up this code"). Avoid technical methodology (no "Fishbone," "ADI," or "Heuristics"). If the user doesn't say it, don't put it in the metadata.
- **Body (The "Method"):** Must use **Technical Precision**. This is where you teach the specialized framework. Once the skill is loaded, jargon is a tool for accuracy.

**The 200-Character Rule:** Triggers must appear in the first 200 characters of the metadata. Anything later is subject to truncation in high-context sessions and becomes an unreliable signal.

**The "Context: Fork" Signal:** If a skill uses `context: fork`, the metadata **MUST** include words like "fan out," "delegate," or "spawn subagents." This signals to the router that this is an orchestration capability, not an inline task.

**Anti-Pattern — No Method Leaking:** Never put the "How" in the `description`.
- *Bad:* "Uses A3 methodology to document root causes."
- *Bad:* "Complete test lifecycle — Red-Green-Refactor TDD"
- *Good:* "Document and solve major recurring problems or failures."
- *Good:* "Write tests first, then implementation."

This separation is intentional: frontmatter must match user vocabulary for routing; body teaches domain experts with precise terminology after the skill loads. Never remove technical terms from the body — only from description and when_to_use.

**Reliable triggering requires:**
- **User vocabulary in frontmatter**: "find the root cause" beats "A3 analysis" — speak how users think
- **Specific phrases**: 5-10 triggers, no generic words ("improve" matches everything)
- **CONTRAST sections**: Overlapping domains need explicit disambiguation
- **Subagent signal**: Descriptions of skills that delegate should mention "spawn subagents" or "fan out" — this signals to Claude that loading this skill means orchestration, not inline execution

**What kills routing:**
- Technical jargon in description/when_to_use ("fishbone", "CQRS", "ADI")
- Single ambiguous words ("fix", "do", "handle")
- Vague descriptions matching everything
- Missing negative cases (what NOT to match)
- Structured syntax ("ACTIVATES:", "LOOP:", "Output:") — breaks fuzzy semantic matching

**Validation (before shipping any skill):**
```bash
claude -p "<test-query>" --output-format stream-json 2>&1 | grep Skill
```
Test 15-20 real queries, hold out 20%. Overfit = description learned pattern-matching, not routing.

**Hook limitations:** Hooks inject context that nudges reasoning — they cannot directly activate skills. No hook event directly loads a skill. Skill activation is description-matching only.

See [Hooks](docs/official/hooks.md) for hook lifecycle events and patterns.

### No Inline Tool Lists in Subagent Instructions

Describe the role and outcome instead — agent definitions configure tools per role. See [Agent Types](docs/official/agent-types.md) for tool access by type.

### Orchestration Topology: Where Skills End and Agents Begin

Skills teach WHAT to decide (routing triggers, delegation boundaries); agents teach HOW to execute (verification protocols, reporting formats, artifact delivery standards). See [Subagents](docs/official/subagents.md) for all default frontmatter fields.

**Subagent Spawning Topology Constraint:**
Agent definition files (`agents/*.md`) MUST NEVER contain spawn, fan-out, or delegation instructions. Because the `Agent` tool is strictly removed from the subagent tool registry at the implementation level (subagents cannot spawn other subagents), any nested spawning directives inside an agent definition will result in a runtime failure. Whenever nested orchestration or workflow delegation is required, the developer MUST instead create an orchestration skill utilizing the `context: fork` frontmatter to establish an isolated orchestration environment.

*Note: While the `Agent` tool is blocked, subagents CAN invoke skills using the `Skill` tool (v2.1.133+). Subagent→Skill and Forked→Inline workflows are structurally supported.*

### `skill:` vs `skills:` Field Distinction

The two field names are **not interchangeable** — they have different schemas and live in different artifacts.

| Field | Where it lives | Semantics | Source |
|-------|---------------|-----------|--------|
| `skills:` (plural, YAML list) | Subagent frontmatter (`agents/*.md`) | Preloads skill content into the subagent's context at startup. Subagents can still invoke unlisted skills via the `Skill` tool. | Official — [subagents.md](docs/official/subagents.md) lines 274, 426-447 |
| `skill:` (singular, scalar) | Command frontmatter (`commands/*.md`) | Project extension: points the command at the canonical skill it dispatches into. Commands are merged into skills, so the `skill:` field is a navigation hint from a thin command shim to its underlying SKILL.md. | **Project extension — not in official docs.** Documented here for maintainer clarity. |

**The `skill:` (singular) field in commands is a project convention, not an official field.** It is not present in either the skill frontmatter reference ([skills.md](docs/official/skills.md)) or the subagent frontmatter reference ([subagents.md](docs/official/subagents.md)). Audits flagging it as non-standard are technically correct; the project uses it intentionally as a dispatcher hint.

**Verify before assuming:** When you see `skill:` or `skills:` in frontmatter, check which artifact (skill, subagent, command) it sits in. They are different fields with different purposes.

### Agent Description Pattern

Agent descriptions inject into Claude's system prompt for routing, but agents cannot self-invoke. Use natural language sentences, not structured syntax. See [Subagents](docs/official/subagents.md) for pattern guidance.

### Artifact Taxonomy

Four artifact types exist with distinct loading behaviors and token costs: Commands (user-invoked, zero until used), Skills (auto-loaded, always present), Agents (per-spawn), and Workflow Commands (per-spawn with coordination). See [Skills](docs/official/skills.md) for the full taxonomy and loading mechanics.

---

## Skill Budget Management

**Claude Code enforces a 1% context limit for skill metadata.** Exceeded skills are silently dropped. Run `/context` and `/doctor` before commits. See [Skills](docs/official/skills.md) for mechanics.

---

## Version Management

**Marketplace version** and **plugin version** are independent:

- **Plugin version**: Incremented for any content change to a plugin (see `marketplace.json` for current versions)
- **Marketplace version** (`.claude-plugin/marketplace.json`): Incremented when releasing a collective update across all plugins

**Update sequence:**
```bash
# 1. Make your changes
git add -A && git commit -m "message"

# 2. Bump plugin version in marketplace.json (minor for features, patch for fixes)
# Edit .claude-plugin/marketplace.json — bump the "version" field for the affected plugin

# 3. Push
git push
```

---

## Skill Authoring

For detailed guidance on skill categories, policy/mechanism pattern, progressive disclosure, frontmatter fields, cross-skill references, decision routers, description optimization, and command format, see the `skill-authoring` skill.

For frontmatter field reference, see [Skills](docs/official/skills.md).

---

## Commands

**Commands are trigger accelerators, not method carriers.** Use direct native vocabulary. See [Commands](docs/official/commands.md) for format standards. Commands with the same name as a skill: the skill takes precedence.

---

## User Interaction

**Interact with users when gathering information or making decisions — not while executing a plan.**

When you need user input, ask clearly. Present options as clickable choices, not numbered lists or free-form prompts. Make it easy to say yes or no to a specific direction.

During execution, trust your judgment for anything the plan didn't explicitly decide. If you find yourself asking "should I do X or Y?" — check whether the plan already commits to one. If it does, proceed. If neither was decided and the choice is significant, stop and ask.

Use checkpoints when verification is genuinely needed — not as a checkpoint for every task. A checkpoint that requires the user to think is often a sign the plan needed more specificity upstream.

The goal is a smooth handoff between thinking and doing. Questions belong in the thinking phase. Once you're implementing, focus on building.

**When to use Claude's native user-interaction tool:** When pausing for user input, say verbatim: "use your tool to ask users your questions and prefill answers". This is the canonical phrase — names the capability generically, not the tool — stays robust if tool names change. Never hardcode tool names like "AskUserQuestion" — that breaks when the tool is renamed.

**Exception — descriptive constraints:** When documenting what subagents cannot do, the tool name is acceptable because it describes a constraint, not prescribing an invocation.

---

## User Interview Pattern

When gathering context before proceeding, use the interview pattern — not a fixed formula.

**The canonical invocation:** Use your tool to ask users your questions and prefill answers.

---

## Hub-Spoke Skill Architecture

Skills can operate as **hubs** (orchestrate other skills) or **spokes** (do one thing). Hub-and-spoke enables consolidation without capability loss. See [Skills](docs/official/skills.md) for patterns.

### Exempt Skills (Do Not Merge)

These are foundational compositional pairs or serve distinct workflow stages:

- `create-plans` + `execute-plans` — project planning lifecycle, separation is intentional
- `create-prompts` + `execute-prompts` — prompt creation lifecycle, separation is intentional
- `refine-task` + `implement-task` — task lifecycle (refine produces implementation-ready specs, implement executes with verification gates)
- `ideation` + `add-task` — capture lifecycle (ideation explores options, add-task persists formal backlog items)
- Marketplace hub skills — plugins with multi-mode routing; see marketplace.json for current inventory

### Completed Consolidations

These tables are evidence of principle application, not protocol for future decisions. Apply the principles in "Decision Criteria" directly — do not use these tables as checklists.

These skills were merged into hub skills using the hub-and-spoke pattern:

| Hub Skill | Skills Merged | Rationale |
|----------|---------------|-----------|
| `diagnose` | `analyse` + `analyse-problem` + `root-cause-tracing` | All do problem investigation; different methods (Five Whys, A3, call-stack) rather than different purposes |
| `refine` (hub) | `reflexion` (all modes) + `write-concisely` | All improve artifact quality; critique/memorize/polish are modes of "make better" |
| `subagent-orchestration` (hub) | `subagent-orchestration` + `create-subagents` | Both teach multi-agent patterns; design vs orchestration are modes of the same capability |
| `sadd` (tp-sadd) | `do-competitively` + `execute` + `sadd-judge` + `sadd-patterns` + `sadd-tot` | All structured agent-driven development; compete/execute/judge/design/explore are execution modes |
| `git` (tp-git) | `git-ship` + `git-review` + `git-issues` + `git-advanced` | All git workflow automation; ship/review/issues/advanced are git operation modes |
| `fpf` (tp-fpf) | `fpf-propose` + `fpf-maintenance` + `fpf-read` | All first-principles reasoning; propose/maintain/query are FPF lifecycle modes |
| `ddd` (tp-ddd) | `code-architecture` + `code-quality` + `code-transparency` + `code-api` | All domain-driven design; architecture/quality/transparency/API are code design dimensions |

Marketplace plugins merged in their own phase.

### Consolidation History

Hub-and-spoke consolidation reduced skill count by merging related skills into routing-coherent hubs. Run `find plugins -name SKILL.md | wc -l` for accurate inventory. The empirical routing target is 22-28 skills.

Past consolidations followed the Decision Criteria. See git history for prior skill names.

### Decision Criteria: Merge or Keep Separate?

**Merge when:**
- Skills share the same purpose (not just similar words in descriptions)
- Skills use different frameworks/methods for the same domain
- Trigger phrases are <5 per skill and overlap in meaning
- The resulting hub has a clear decision router with distinct modes

**Keep separate when:**
- Skills serve distinct workflow stages (ideation vs add-task)
- Skills have distinct entry/exit contracts that other skills depend on
- Trigger density is high (5+ specific phrases) and routing is reliable

### Target Skill Count

The routing quality breaking point is an empirical range; below it fat skill complexity dominates, above it routing conflation accumulates. Hub-and-spoke consolidation reduced skill count by merging related skills into routing-coherent hubs.

**Target skill count:** Run `find plugins -name SKILL.md | wc -l` for current inventory. The empirical routing target is 22-28 skills.

### Hub-Spoke Pattern in Existing Skills

The `refine` skill is the canonical hub-and-spoke template. Its modes are defined in the skill's Decision Router section — read the actual skill file for current mode inventory.

`subagent-orchestration` is the second hub example with 2 modes (DESIGN/ORCHESTRATE). Use these patterns for other multi-mode skills. The mode router lives in each hub skill's Decision Router section.

---

## Plugin Path Portability

Skills use `{baseDir}` for internal file paths. Cross-skill references use natural language naming the skill. See [docs/official/skills.md](docs/official/skills.md) for reference patterns.

**References/ folders are lazy-loaded only when explicitly named in skill body**.

**Rule:** Each skill owns its `docs/` folder — do not expect cross-skill reuse.

---

## Token Economy

- **Commands over skills for on-demand loading** — skills consume context always; commands load when invoked
- **Tool outputs dominate context** — typically 80-90% of total usage (Context Engineering Kit); apply progressive disclosure to avoid lost-in-middle effect
- **Specialized agents with narrow context** — broad-context agents hallucinate more
- **Token estimation** — every skill should know its approximate cost
- **500-line guideline** — official stance is under 500 lines for optimal performance; split into separate reference files via progressive disclosure if content exceeds this. Hub skills (e.g., `refine`, `diagnose`) aggregate multiple formerly separate skills and may legitimately exceed this limit — the guideline applies to individual modes within a hub, not the total hub file

---

## Documentation Sync

README.md lives in two places:
1. The plugin root (source of truth)
2. Any docs/ directory (for GitHub Pages or marketplace docs)

**When you update README:** Copy to all locations manually.

CLAUDE.md targets human maintainers (development conventions, governance, architecture). README.md targets plugin consumers (capabilities, installation, getting started). Their audiences and depth expectations differ.

---

## CHANGELOG Convention

Version format: `[1.2.3]` — semantic versioning

**Entry structure:**
```markdown
## [1.2.3] — YYYY-MM-DD

### Added
- What was added

### Changed
- What changed and why

### Removed
- What was removed and why

### Fixed
- Bug fixes with file:line or conceptual reference
```

**Default is minor version bump.** Patch for typos and docs only. Major only for architectural changes.

---

## Commit Messages

Format: `<type>: <short description>`

Types: `feat`, `fix`, `refactor`, `docs`, `chore`

```bash
feat: add Policy/Mechanism sections to create-plans
fix: correct malformed hookSpecificOutput JSON in hook-types
docs: update README with skill ecosystem map
chore: rename to taches-principled across all files
```

---

## Git Workflow

Create feature branches, commit with conventional messages, push, and create PRs via gh. Example: `feat: add new skill`, `fix: resolve routing trigger ambiguity`.

---

## Before Any Commit — Self-Check

**Project-specific checks:**
- [ ] README updated if structure changed
- [ ] CHANGELOG entry added
- [ ] No MCP runtime dependencies
- [ ] No broken cross-references between skills
- [ ] No shared docs/ folders expecting cross-skill reuse
- [ ] User interaction uses clear, structured options
- [ ] README synced to all docs/ locations if marketplace docs are present
- [ ] Skill changes backed by eval evidence (tested against real routing scenarios, not hypothetical)
- [ ] Skill changes describe actual problems encountered (not theoretical improvements)
- [ ] **Subagent spawn check**: Every skill that explores, implements, researches, or creates has explicit spawn instructions in its body — not optional tips, not conditional recommendations. The default execution mode is subagent delegation.
- [ ] **Critique loop check**: Every skill that produces artifacts ends with "spawn self-review and self-critic subagents, loop until no HIGH findings" or equivalent
- [ ] **Skill budget check**: Run `/context` and `/doctor` — verify no skills dropped or descriptions truncated
- [ ] **Description length check**: Combined `description` + `when_to_use` ≤1,536 chars (the official skill metadata cap, raised April 2026); front-load trigger phrases in the first 200 chars to survive truncation in high-context sessions
- [ ] **Tool field check**: Agent definitions use `tools:` (allowlist). Skills use `allowed-tools:` (pre-approval). Commands use `allowed-tools:` (pre-approval). Never confuse these semantics.

### Skill Quality Gate

- [ ] **Orchestration separation:** Skill body describes outcomes/roles; agent prompt describes execution only
- [ ] **No hardcoded drift targets:** Replace specific counts/versions with references or filesystem queries
- [ ] **Discovery over enumeration:** Use filesystem queries over reimplemented enumerations

### README Hygiene

The README uses **curated examples, not catalogs**. Tables show 3-5 representative
items; full enumerations live in `marketplace.json` and the filesystem. Counts in
headers (`### 23 Skills`) are forbidden — they go stale the moment a skill is
added or removed.

When you add, remove, or rename a skill, command, agent, or plugin:
- [ ] The README still reads accurately *without counting items* — no header
      claims a count that must be kept in sync. The 3-5 representative rows
      are intentional; the rest is discoverable via `/skills`, `/help`, or
      browsing `plugins/*/`.
- [ ] The "Try These First" / "Quick Start" examples still exist (do not
      delete a row that documents a user-facing workflow).
- [ ] The "Manual (without marketplace)" install snippet still works
      (paths: `plugins/taches-principled/{skills,commands,agents}/`).
- [ ] `marketplace.json` plugin description, version, and keywords are
      updated for the affected plugin(s).

---

## Artifact Hygiene — `.principled/` Directory

**All Claude-generated artifacts live in `.principled/` — never pollute the codebase.**

Generated plans, prompts, scratch notes, and cross-session memory go here. This keeps git clean and makes it easy to archive or wipe generated content.

```
.principled/
├── plans/           # Plans, briefs, roadmaps, phases
│   └── phases/     # Phase-specific plans and summaries
├── scratch/        # Debug sessions, temp artifacts
└── memory/         # Architecture state, cross-session notes
```

**Archiving:** Skills define when to move content to `.attic/`. A plan moves to `.attic/` when its phase completes. Prompts move when execution finishes. The attic preserves context for future audits.

**Not artifacts:** `.claude/agents/` and `.claude/skills/` are definitions, not generated content. They stay where they are.

---

## Explorer Subagent Protocol

Use general-purpose agents (not Explore type) for exploration with Write tool. Read scratch notes before/after. See [docs/official/subagents.md](docs/official/subagents.md).

---

## Evaluation Pipeline

taches-principled has a multi-agent evaluation system for skill quality assurance. Four specialized agents handle the pipeline: **grader** scores teaching effectiveness, **comparator** analyzes version deltas, **skill-auditor** reviews format and frontmatter, and **analyzer** synthesizes into 3 prioritized changes. All four are available as auto-discovered plugin-level agents.

### Quick Audit

To audit a skill for quality, spawn a skill-auditor subagent: read the agent definition and use it as a subagent prompt with the skill path as context. This gives format and frontmatter validation without full pipeline overhead.

### Two-Claude Ad-hoc Testing

Official approach for trigger verification: draft candidate descriptions, create a small eval set of representative queries, test routing with two independent Claude instances, and refine based on results. The eval is a teaching instrument, not a gate — failed test cases teach where description language is unclear.

### Grading Dimensions

Skills are graded on four weighted dimensions. **Routing Signal** (40%) measures whether the description gives clear trigger phrases. **Delta Clarity** (30%) measures whether the skill states what it changes from default. **Teaching Posture** (20%) measures whether it teaches principles over procedures. **Anti-Pattern Quality** (10%) measures whether wrong/right pairs include consequence explanation. Format without teaching is decoration.

---

## Quality Standards

**Skills are behavior-shaping code, not prose.** Changes to skill content require:
- Adversarial testing (does it actually trigger when expected?)
- Eval evidence (does it improve outcomes?)
- No speculative fixes (must be real problem, not theoretical)

**Human partner protection:** When this plugin produces code destined for external repos, it should protect the human partner from embarrassment. Low-quality PRs waste maintainer time and damage reputation.

**Real problem verification:** Every change should describe a specific session, error, or user experience that motivated it.

---

## Plugin Management

This repository uses a **monolithic marketplace-centric model** — see [docs/official/plugins/marketplaces.md](docs/official/plugins/marketplaces.md) for the canonical architecture explanation.

### Architecture

**Single source of truth:** `marketplace.json` is the sole authoritative catalog for all plugins. It contains all plugin metadata including versions and locations.

**Distribution:** Single `marketplace.json` bundles all plugins. Users install one marketplace, receive everything.

**Runtime:** Each plugin is fully independent — zero code sharing, zero dependencies, zero runtime coupling. Plugins remain architecturally isolated even though all metadata lives in one file.

**Version management:** Plugin versions live in `marketplace.json`, not in per-plugin files.

### Marketplace Configuration

The `marketplace.json` uses the `source` field (not `path`) to specify plugin locations:

```json
{
  "plugins": [
    {
      "name": "plugin-name",
      "version": "1.0.0",
      "source": "plugins/plugin-name"
    }
  ]
}
```

For the full schema and `strict: false` behavior, see the [marketplaces documentation](docs/official/plugins/marketplaces.md).

### Directory Structure

```
plugins/
├── tp-git/                    # Git workflow automation (independent plugin)
│   └── skills/{name}/SKILL.md
├── tp-sadd/                   # Structured agent-driven dev (independent plugin)
├── tp-fpf/                    # First-principles reasoning (independent plugin)
└── tp-vps-governance/         # Memory management (independent plugin)

.claude-plugin/
└── marketplace.json            # Single source of truth for all plugin metadata
```

Each plugin under `plugins/` is fully standalone. The `marketplace.json` is the sole source of truth for the plugin catalog.

### Naming Convention

All imported/ported plugins use the `tp-` prefix. Current marketplace plugins are listed in `.claude-plugin/marketplace.json`. Each plugin is self-contained with its own `skills/`, `agents/`, and `commands/` directories.

### Adding a New Plugin

1. Create `plugins/{name}/skills/{skill-name}/` directories
2. Write SKILL.md files following the decision router + policy/mechanism patterns used by existing skills
3. Add plugin entry to `.claude-plugin/marketplace.json` with `source` pointing to the plugin directory
4. Bump marketplace version

**Remember:** The new plugin must work standalone. It cannot import or reference other plugins' files.

### Plugin Isolation Principle

Each plugin must:
- Work when installed alone (zero dependencies on other plugins)
- Describe its workflow stage using semantic vocabulary (not plugin names)
- Include a decision router for trigger routing

### Non-Brittle Cross-Plugin Communication

**Cross-skill references by name are acceptable. Cross-skill file paths are not.**

It is correct to cite another skill by name in DO NOT boundaries, CONTRAST sections, or conditional hints — "use diagnose instead" is fine, "read skills/diagnose/SKILL.md" is not. Naming another skill teaches routing and maintains coherence across the plugin. The key constraint is conditional framing: the reference must not be load-bearing for the skill to function. A skill that says "use X for step 2" is brittle if X doesn't exist. A skill that says "CONTRAST with X: X does A, this skill does B" works standalone — the user just doesn't get the cross-reference.

**Synergy tiers:**
- **Same skill**: Always reference freely — internal consistency
- **Same plugin**: Reference by name with conditional framing ("use X if you have access to it") — works standalone, synergizes when both installed
- **Same marketplace (different plugin)**: Reference by role or semantic domain, not plugin name — "for independent evaluation, dispatch a judge subagent" works whether the judge comes from tp-sadd or a third-party plugin
- **External marketplace**: Reference by capability ("for quality verification, spawn an auditor subagent") — no plugin name, no file paths

The pattern: cite the skill or role by name, not the file inside it. Let the routing system discover the right implementation.

---

## Design Principles

### High Freedom, High Trust

Every artifact in this ecosystem — skills, agents, commands — must default to maximum autonomy for the AI invoking them. **High freedom** means telling the AI what outcome to produce, not how to produce it. **High trust** means omitting constraints, steps, and boundaries that the AI can infer from context. When in doubt about whether an instruction is needed, omit it — the AI will ask or figure it out.

**Skills** are triggers, not recipes — describe what to accomplish and when, not step-by-step procedure. **Agents** are system prompts, not scripts — they must be plain text with **NO markdown formatting** (no bold, no headers, no bullet lists). Write one coherent high freedom, high trust paragraph. **No precise output schema is expected** or enforced (no JSON templates, no exact markdown structures). Tell the agent its role and goal, and trust it to format its output naturally. **Commands** are lightweight pointers — no markdown body, no structural decomposition, 1-3 sentences of outcome, conditional hints for skills/subagents/web search when useful.

### Marketplace Synergy

This marketplace must synergize with any other marketplace or plugin the user may have installed. Every plugin and skill must work standalone with zero dependencies on other plugins in this marketplace. Skills describe their domain using shared workflow vocabulary — never referencing plugins by name. When another plugin provides a capability that overlaps, let routing sort it out: the AI chooses the best match from all installed plugins. Do not add disclaimers, compatibility notes, or installation requirements referencing other plugins. The user's plugin ecosystem is the AI's to navigate — not ours to constrain.

This applies to all external plugins and marketplaces, not just within this project. A user running taches-principled alongside any third-party plugin should experience zero conflicts, zero duplicate routing, and zero assumptions about what else is installed.

---

## Glossary

| Term | Definition |
|------|------------|
| **Semantic routing** | AI matches task intent to agent/skill capabilities based on description meaning, not file names |
| **Hub skill** | Skill using decision routing to dispatch to internal modes (contrast with spoke) |
| **Spoke skill** | Single-purpose skill doing one thing (contrast with hub) |
| **Compositional pair** | Two skills with intentional separation for create/execute lifecycle |
| **Load-bearing** | Separation that serves a functional purpose — removing it breaks the design |
| **Progressive disclosure** | Loading pattern: frontmatter → body → references (shows policy first, mechanism on demand) |
| **Native capabilities** | Built-in Claude Code actions: spawn subagent, create task list, use web search, read/write files, use Bash |
| **Transformer Mandate** | Protocol principle: AI generates and scores, human makes final structural decisions |
| **Subagent-first** | Design principle where subagent spawning is the default execution mode, inline work is the exception |
| **Critique loop** | Pattern of spawning review subagents after artifact creation, iterating until no HIGH findings remain |
| **Skill budget** | Claude Code's 1% context limit for skill metadata; exceeded skills are silently dropped |
| **Front-load** | Placing trigger keywords at the start of descriptions so they survive truncation from the end |
| **CONTRAST section** | Explicit negative cases in descriptions to prevent false positive routing |
| **Under-triggering** | Claude's tendency to not invoke skills without explicit trigger phrases — primary routing failure mode |

---

## Documentation Reference

**When to read these docs:** Claude Code documentation is authoritative. Read the relevant doc when working on related tasks. Don't memorize — know when to look.

### Refreshing Official Docs

Official docs in `docs/official/` are raw Anthropic markdown fetched directly from source. To refresh any doc:

```bash
curl -sL "https://code.claude.com/docs/en/<topic>.md" -o docs/official/<topic>.md
```

Where `<topic>` matches the URL slug from `code.claude.com/docs/llms.txt` (e.g., `hooks`, `skills`, `sub-agents`, `commands`, `permissions`, `plugins`, `plugin-marketplaces`, `plugins-reference`). Always verify the download starts with `> ## Documentation Index` and ends at a natural section boundary.

### Official References

| Doc | Description | When to Read |
|-----|-------------|--------------|
| [subagents.md](docs/official/subagents.md) | Subagent frontmatter fields, spawn patterns, tool access | **Before creating agents** |
| [skills.md](docs/official/skills.md) | Skill frontmatter, trigger optimization, hub-and-spoke | **Before authoring skills** |
| [hooks.md](docs/official/hooks.md) | Hook events, configuration, JSON I/O, exit codes | **Before configuring hooks** |
| [commands.md](docs/official/commands.md) | Command creation and conventions | **Before creating commands** |
| [permissions.md](docs/official/permissions.md) | Permission modes, rules, managed policies | **Before configuring permissions** |
| [agent-types.md](docs/official/agent-types.md) | Built-in agent types and tool access | **Before choosing agent type** |
| [agent-tool-params.md](docs/official/agent-tool-params.md) | Agent tool spawn parameters | **Before spawning subagents** |
| [agent-skill-integration.md](docs/official/agent-skill-integration.md) | When to preload skills in agents | **Before adding skills to agents** |

### Plugin References

| Doc | Description | When to Read |
|-----|-------------|--------------|
| [plugins/creating.md](docs/official/plugins/creating.md) | Plugin structure and components | **Before creating plugins** |
| [plugins/marketplaces.md](docs/official/plugins/marketplaces.md) | Marketplace configuration | **Before setting up marketplace** |
| [plugins/plugins-reference.md](docs/official/plugins/plugins-reference.md) | Plugin system reference — schemas, CLI, specs | **Before advanced plugin work** |

---

## Meta-Rule (applies to this file only)

**Governs itself — all revisions must remain:**
- **Accurate** — Reflects current project state; outdated sections removed, not annotated.
- **Actionable** — Every section answers "what do I do?" not just "what exists?"
- **Self-contained** — A new maintainer can understand the project from this file alone.

---

## References

- [Claude Code Plugin Creation Guide](https://code.claude.com/docs/en/plugins.md)
- [Claude Code Plugin Marketplaces Documentation](https://code.claude.com/docs/en/plugin-marketplaces.md)
- [Claude Code Hooks Reference](https://code.claude.com/docs/en/hooks.md)
- [Claude Code Commands Reference](https://code.claude.com/docs/en/commands.md)
- [Plugin Submission Guide](https://claude.com/docs/plugins/submit.md)
- [context-engineering-kit](https://github.com/NeoLabHQ/context-engineering-kit) — token economy and subagent orchestration patterns
