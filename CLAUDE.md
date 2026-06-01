# Taches Principled — Development Guide

**For maintainers only.** This file is development practices and internal conventions. It is NOT loaded by Claude Code when this plugin is installed — a marketplace-installed instance sees only skill descriptions, agent definitions, and commands.

Treat every section as knowledge transfer from a human who worked on this codebase to future human maintainers.

When generic agents and specialized inline versions cover the same capability, prefer the generic agent. A generic agent's body becomes the canonical version; domain-specific knowledge lives in the skill that invokes it, not in the agent definition itself. An agent is only orphaned when no skill describes a capability it would resolve.

---

## Core Design Principle

Every artifact is consumed by a Claude Code instance starting with zero context. Design as if Claude loads into a fresh session, reads only the plugin's files, and must decide what to do.

Ask: Does the routing make sense without external context? Does the description give enough trigger signal for the right skill to fire? Does the body teach judgment or just prescribe steps?

High trust means: write descriptions that route correctly, then stop. Don't add fallbacks, disclaimers, or routing logic for edge cases the model can handle.

---

## Orchestration Model

**Costly main agent** (Sonnet/Opus) owns cognition — planning, decomposition, routing, aggregation, synthesis. **Cheap subagents** (Haiku or fast Sonnet) own execution — exploration, research, implementation, verification, critique. Run in parallel with critique loops: spawn a critic subagent after each milestone, loop until no HIGH findings remain.

### Subagent-First Execution Contract

**Default to subagents. Inline execution is the exception, not the norm.** Claude's default mode is inline — it requires less cognitive effort and activates automatically. Override this default by making subagent spawning the path of least resistance.

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

**The rule: If the skill loaded, the work is non-trivial by definition — spawn subagents.** The skill exists precisely because the task exceeds trivial inline execution. Trust the skill's own existence as the signal.

**Spawn pattern for skill bodies:**
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

Anti-pattern: "If the task is complex, consider using subagents." Use declarative language: "Spawn subagents for [task type]."

### When the Main Agent Acts Directly

- Lightweight edits (1-2 files, trivial change)
- Reading and synthesizing subagent output from scratchpad
- Making judgment calls between competing subagent recommendations
- Final aggregation, summary writing, and commit

### Transformer Mandate

A system cannot transform itself. AI generates options with evidence scores; human makes the final decision. **Autonomous architectural choices are a protocol violation** — the AI suggests and scores, never commits unilaterally on structural decisions.

---

## Skill Discovery & Routing

**Discovery is a "Metadata-Only" Gate.** Claude decides which skill to load based **exclusively** on the text pre-injected into its system prompt. At the moment of routing, the skill **body is invisible.**

**Routing participants — fields only:**
- **Skills:** `description` + `when_to_use`
- **Agents:** `description` (NOT the body prompt)
- **Commands:** `description`

**Nesting limit:** Automatic skill discovery scans only 1 level deep (`skills/<name>/SKILL.md`). Skills nested 2+ levels deep require a manual `Glob` scan fallback.

### Metadata vs. Body Strategy

- **Metadata (The "Hook"):** Must use **User Vocabulary**. Speak how the user thinks (e.g., "Find the bug"). Avoid technical methodology. If the user doesn't say it, don't put it in the metadata.
- **Body (The "Method"):** Must use **Technical Precision**. This is where you teach the specialized framework. Once the skill is loaded, jargon is a tool for accuracy.

### Routing Rules

**The 200-Character Rule:** Triggers must appear in the first 200 characters of metadata. Anything later is subject to truncation in high-context sessions.

**The "Context: Fork" Signal:** If a skill uses `context: fork`, metadata **MUST** include words like "fan out," "delegate," or "spawn subagents."

**No Method Leaking in description:**
- *Bad:* "Uses A3 methodology to document root causes."
- *Bad:* "Complete test lifecycle — Red-Green-Refactor TDD"
- *Good:* "Document and solve major recurring problems or failures."
- *Good:* "Write tests first, then implementation."

**What kills routing:**
- Technical jargon in description/when_to_use ("fishbone", "CQRS", "ADI")
- Single ambiguous words ("fix", "do", "handle")
- Vague descriptions matching everything
- Missing negative cases (what NOT to match)
- Structured syntax ("ACTIVATES:", "LOOP:", "Output:") — breaks fuzzy semantic matching

**Reliable triggering requires:**
- User vocabulary in frontmatter: "find the root cause" beats "A3 analysis"
- Specific phrases: 5-10 triggers, no generic words ("improve" matches everything)
- CONTRAST sections for overlapping domains
- Subagent signal: "spawn subagents" or "fan out" signals orchestration capability

**Validation before shipping any skill:**
```bash
claude -p "<test-query>" --output-format stream-json 2>&1 | grep Skill
```
Test 15-20 real queries, hold out 20%. Overfit = learned pattern-matching, not routing.

**Hook limitations:** No hook event directly loads a skill. Skill activation is description-matching only.

---

## Hub-Spoke Skill Architecture

Skills can operate as **hubs** (orchestrate other skills via decision routing) or **spokes** (do one thing). Read [Skills](docs/official/skills.md) for hub-spoke patterns BEFORE adding or merging skills.

### Exempt Skills (Do Not Merge)

- `create-plans` + `execute-plans` — project planning lifecycle
- `create-prompts` + `execute-prompts` — prompt creation lifecycle
- `refine-task` + `implement-task` — task lifecycle (refine produces specs, implement executes)
- `ideation` + `add-task` — capture lifecycle (ideation explores, add-task persists)
- Marketplace hub skills — plugins with multi-mode routing

### Merge Criteria

**Merge when:** Skills share the same purpose; skills use different frameworks/methods for the same domain; trigger phrases overlap in meaning; the resulting hub has a clear decision router with distinct modes.

**Keep separate when:** Skills serve distinct workflow stages; skills have distinct entry/exit contracts other skills depend on; trigger density is high (5+) and routing is reliable.

### Decision: Merge or Keep?

| Hub Skill | Skills Merged | Rationale |
|-----------|---------------|-----------|
| `diagnose` | `analyse` + `analyse-problem` + `root-cause-tracing` | All problem investigation; different methods, same purpose |
| `refine` | `reflexion` (all modes) + `write-concisely` | All improve artifact quality |
| `subagent-orchestration` | `subagent-orchestration` + `create-subagents` | Both teach multi-agent patterns |
| `sadd` (tp-sadd) | `do-competitively` + `execute` + `sadd-judge` + `sadd-patterns` + `sadd-tot` | All structured agent-driven dev |
| `git` (tp-git) | `git-ship` + `git-review` + `git-issues` + `git-advanced` | All git workflow automation |
| `fpf` (tp-fpf) | `fpf-propose` + `fpf-maintenance` + `fpf-read` | All first-principles reasoning |
| `ddd` (tp-ddd) | `code-architecture` + `code-quality` + `code-transparency` + `code-api` | All domain-driven design |

Hub-and-spoke consolidation target: 22-28 skills. Run `find plugins -name SKILL.md | wc -l` for current inventory.

---

## Plugin Architecture

**Monolithic marketplace-centric model** — `marketplace.json` is the sole authoritative catalog for all plugins. Read [docs/official/plugins/marketplaces.md](docs/official/plugins/marketplaces.md) BEFORE modifying marketplace.json or adding plugins.

**Directory structure:**
```
plugins/
├── tp-git/                    # Independent plugin
├── tp-sadd/                   # Independent plugin
├── tp-fpf/                    # Independent plugin
└── tp-vps-governance/         # Independent plugin

.claude-plugin/
└── marketplace.json            # Single source of truth
```

Each plugin is fully standalone with its own `skills/`, `agents/`, and `commands/` directories. Zero code sharing, zero dependencies, zero runtime coupling.

**Plugin isolation:** Each plugin must work when installed alone, describe its workflow stage using semantic vocabulary (not plugin names), and include a decision router for trigger routing.

### Adding a New Plugin

1. Create `plugins/{name}/skills/{skill-name}/` directories
2. Write SKILL.md files following the decision router + policy/mechanism patterns
3. Add plugin entry to `.claude-plugin/marketplace.json` with `source` pointing to the plugin directory
4. Bump marketplace version

### Non-Brittle Cross-Plugin Communication

| Tier | Reference Pattern |
|------|-------------------|
| Same skill | Always reference freely |
| Same plugin | Reference by name with conditional framing ("use X if you have access to it") |
| Same marketplace (different plugin) | Reference by role or semantic domain ("dispatch a judge subagent") |
| External marketplace | Reference by capability ("for quality verification, spawn an auditor subagent") |

The pattern: cite the skill or role by name, not the file inside it.

---

## Artifact Standards

### Agent Tool Contract

**An agent's declared tools MUST match its stated capabilities.** When an agent claims to write findings to disk, it needs the Write tool. If the capability exists in the description but the tools field is missing, the agent cannot fulfill its contract.

### Tool Scoping Fields

| Field | Artifact | Effect | When Omitted |
|-------|----------|--------|-------------|
| `tools:` | Agent definitions | **Hard allowlist** — only listed tools accessible | Inherits all tools |
| `allowed-tools:` | Skills, Commands | **Pre-approval** — skips prompts but all tools remain callable (Edit/Agent/Skill bypass Write) | Normal permission settings |
| `disallowed-tools:` | Skills | **Hard block** — removes specific tools from pool | No tools blocked |

**Common mistake:** Treating `allowed-tools` as a security boundary. It only skips permission prompts. For true restriction, use agent `tools:` allowlists or skill `disallowed-tools:`.

### Artifact Taxonomy

Four artifact types with distinct loading behaviors and token costs:
- **Commands** — user-invoked, zero context until used
- **Skills** — auto-loaded, always present in context
- **Agents** — per-spawn, loaded at spawn time
- **Workflow Commands** — per-spawn with coordination overhead

### Path Configuration

**Use command arguments and environment variables for paths — never hardcode absolute paths.**

- `{{CLAUDE_WORKING_DIR}}` for the current working directory
- `$ARGUMENTS` for user-provided path parameters
- Bash environment variables (`$HOME`, `$PWD`) for shell operations

### Skill-Internal File References

**Two canonical rules govern skill file referencing:**

1. **Default resolution**: Any path written within a skill that points to its own supporting content is, by default, resolved within that skill's folder. For example, a reference to `references/plan-format.md` from within the `create-plans` skill resolves to `plugins/taches-principled/skills/create-plans/references/plan-format.md`.

2. **Centralized routing**: ONLY the main SKILL.md file is permitted to cite supporting files. Reference files (in `references/`, `agents/`, `workflows/`, `templates/`, `scripts/` folders) must never cross-cite other reference files. The SKILL.md is the sole, centralized router for all internal citations.

**Strong language requirements:**
- Use deterministic, imperative citations. Never use passive language like "You can read", "See reference", or "Optional guide available at".
- Write: "You MUST read `references/X.md` BEFORE writing any code. Do not proceed or make assumptions without reading this file."
- Passive citations are ignored by LLMs 99% of the time — every reference must be a strict imperative.

### Native Tool Referencing

**Principle:** Never hardcode tool names in orchestration directives. Use semantic natural language that delegates to the dynamically injected tool registry.

| Brittle (breaks on rename) | Native (forward-compatible) |
|----------------------------|-----------------------------|
| `Use the Agent tool to spawn` | `Use your native tools to spawn a subagent` |
| `Use the Task tool` | `delegate work via your native tools` |
| `Use the Write tool` | `Use your native tools to write the file` |
| `Use the Edit tool` | `Use your native tools to make the change` |
| `Spawn with Write tool access` | `Spawn with write access` |

**Why "native tools" works:** "Use your native tools" forces the model to actively consult its dynamically injected tool registry rather than blindly executing a hardcoded string. The Task→Agent rename is the canonical example: hardcoding "Task tool" would break silently, while "spawn a subagent with write access" remains correct regardless of what the underlying API calls the capability.

**When to use exact tool names:**
- MCP fully-qualified names (`BigQuery:bigquery_schema`) — server-level identities that never change
- Documenting tool behavior in skill bodies ("The Read tool returns...") — describing behavior, not invoking
- NEVER in orchestration directives: spawning, delegating, or directing workflow

### Artifact Hygiene — `.principled/` Directory

**All Claude-generated artifacts live in `.principled/` — never pollute the codebase.**

```
.principled/
├── plans/           # Plans, briefs, roadmaps, phases
│   └── phases/     # Phase-specific plans and summaries
├── scratch/        # Debug sessions, temp artifacts
└── memory/         # Architecture state, cross-session notes
```

Skills define when to move content to `.attic/`. The attic preserves context for future audits.

**Not artifacts:** `.claude/agents/` and `.claude/skills/` are definitions, not generated content. They stay where they are.

---

## Execution Rules

### Deterministic Language

**Execution-critical requirements use strong language (ALWAYS, NEVER, MUST). Exploratory guidance uses soft language (consider, prefer, typically).**

- "ALWAYS verify git availability before spawning git-dependent subagents"
- "NEVER hardcode file paths in skill bodies"
- "Consider using parallel subagents for exploration"
- "Prefer Haiku for execution, Sonnet for reasoning"

**The test:** If removing the rule would produce visibly wrong output, use strong language. Anti-pattern: "should", "can", "may" in execution-critical contexts — these signal optionality where the skill actually requires the behavior.

**Why mandatory language compensates for lazy reference loading.** Reference files (in `references/` directories) load lazily — they consume zero tokens until explicitly cited with a strict imperative in SKILL.md. This is efficient by design. However, LLMs tend to skip reference files that use passive citations ("You can read...") or soft language. Mandatory language (ALWAYS, NEVER, MUST) in citation directives counteracts this default laziness. When SKILL.md says "You MUST read `references/X.md` BEFORE proceeding", the LLM treats the reference as load-bearing rather than optional. This is why even conditional rules use mandatory language for activation — the "when/if" condition determines WHEN to apply the rule, but the language itself ensures the reference file is actually read.

**Conditional rules are normal.** When a rule should only apply in specific situations, express that condition explicitly: "ALWAYS verify X **when** Y" or "NEVER do Z **if** W". The condition is part of the rule and determines activation scope. The mandatory language ensures deterministic behavior regardless of context load.

### Infrastructure Assumption

**ALWAYS verify infrastructure prerequisites before executing dependent operations.** Skills that rely on external tools (git, gh, npm, python, etc.) must check availability before assuming the environment provides them.

### Skills Preloading Principle

**"Better too much than not enough."**

All potentially relevant skills MUST be preloaded on all subagent types unconditionally. This applies to execution agents, research agents, and all other agent types — not just evaluation or critique agents.

The outdated rule restricting skill preloading exclusively to evaluation/critique agents is retired. Capability access must be deterministic — an agent that might need a capability must have it preloaded before task execution begins.

**Why this works:** Properly authored skills use progressive disclosure. Base skill content (frontmatter metadata + body) is lightweight — typically under 500 tokens. Deep reference files load only when the skill body explicitly references them and the agent's task requires them. Preloading delivers the base; the AI decides depth.

**The AI retains lazy-loading autonomy.** While base skills are preloaded deterministically, the AI retains full autonomy to decide whether it needs to lazily load deeper reference files from those skills based on the specific task at hand. Preloading is not the same as processing all referenced content.

Do not filter, conditionally load, or optimize skill preloads for narrow scope. Cast wide — deterministic capability access over narrow optimization.

### Cross-Plugin Skill Preloading

**It is perfectly safe and highly recommended to preload skills from plugins that may not currently be installed on the user's machine.** Claude Code evaluates the `skills:` frontmatter array dynamically at startup; if a requested skill is unavailable or uninstalled, the system gracefully ignores it without throwing an error. Because properly authored skills rely on progressive disclosure, their baseline context consumption is extremely low. Aggressively preloading all potentially relevant methodology skills ensures maximum deterministic capability access with zero risk of breaking the agent. An agent can list `sadd`, `fpf`, `tdd`, and `ddd` in its `skills:` array even when the user has only the core plugin installed — unsupported skills are silently skipped.

### Orchestration Topology Constraint

Agent definition files (`agents/*.md`) **MUST NEVER** contain spawn, fan-out, or delegation instructions. The `Agent` tool is strictly removed from the subagent tool registry — any nested spawning directives in an agent definition result in runtime failure. When nested orchestration is required, create an orchestration skill using `context: fork` frontmatter.

Subagents CAN invoke skills using the `Skill` tool (v2.1.133+). Subagent→Skill and Forked→Inline workflows are structurally supported.

---

## Skill Authoring

You MUST consult the `skill-authoring` skill for detailed guidance on skill categories, policy/mechanism pattern, progressive disclosure, frontmatter fields, cross-skill references, decision routers, description optimization, and command format BEFORE authoring or modifying any skill.

You MUST read [Skills](docs/official/skills.md) for frontmatter field reference BEFORE writing skill frontmatter.

---

## Version & Release

**Marketplace version** and **plugin version** are independent. Plugin versions increment on any content change. Marketplace version increments when releasing a collective update across all plugins.

### Update Sequence

```bash
# 1. Make your changes
git add -A && git commit -m "message"

# 2. Bump plugin version in marketplace.json (minor for features, patch for fixes)
# Edit .claude-plugin/marketplace.json — bump the "version" field for the affected plugin

# 3. Push
git push
```

### CHANGELOG Convention

Version format: `[1.2.3]` — semantic versioning. Default is minor bump. Patch for typos and docs only. Major only for architectural changes.

```markdown
## [1.2.3] — YYYY-MM-DD

### Added
### Changed
### Removed
### Fixed
```

### Commit Messages

Format: `<type>: <short description>` with types: `feat`, `fix`, `refactor`, `docs`, `chore`.

### Git Workflow

Create feature branches, commit with conventional messages, push, and create PRs via gh.

---

## Before Any Commit — Self-Check

### Project Checks

- [ ] README updated if structure changed; synced to all docs/ locations
- [ ] CHANGELOG entry added
- [ ] `marketplace.json` plugin description, version, and keywords updated
- [ ] No MCP runtime dependencies
- [ ] No broken cross-references between skills
- [ ] No shared docs/ folders expecting cross-skill reuse

### Skill Quality Checks

- [ ] **Subagent spawn check**: Every skill that explores, implements, researches, or creates has explicit spawn instructions in its body — not optional tips, not conditional recommendations
- [ ] **Critique loop check**: Every skill that produces artifacts ends with "spawn self-review and self-critic subagents, loop until no HIGH findings" or equivalent
- [ ] **Skill budget check**: Run `/context` and `/doctor` — verify no skills dropped or descriptions truncated
- [ ] **Description length check**: Combined `description` + `when_to_use` ≤1,536 chars; front-load trigger phrases in the first 200 chars
- [ ] **Tool field check**: Agent definitions use `tools:` (allowlist). Skills use `allowed-tools:` (pre-approval). Commands use `allowed-tools:` (pre-approval). Never confuse these semantics.
- [ ] **Orchestration separation**: Skill body describes outcomes/roles; agent prompt describes execution only
- [ ] **No hardcoded drift targets**: Replace specific counts/versions with references or filesystem queries
- [ ] **Discovery over enumeration**: Use filesystem queries over reimplemented enumerations

### README Hygiene

The README uses **curated examples, not catalogs**. Tables show 3-5 representative items; full enumerations live in `marketplace.json` and the filesystem. Counts in headers (`### 23 Skills`) are forbidden — they go stale the moment a skill is added or removed.

When you add, remove, or rename a skill, command, agent, or plugin:
- [ ] The README still reads accurately *without counting items*
- [ ] The "Try These First" / "Quick Start" examples still exist
- [ ] The "Manual (without marketplace)" install snippet still works

---

## Quality Standards

**Skills are behavior-shaping code, not prose.** Changes require:
- Adversarial testing (does it actually trigger when expected?)
- Eval evidence (does it improve outcomes?)
- No speculative fixes (must be real problem, not theoretical)

**Human partner protection:** When this plugin produces code for external repos, protect the human partner from embarrassment. Low-quality PRs waste maintainer time and damage reputation.

**Real problem verification:** Every change should describe a specific session, error, or user experience that motivated it.

---

## Evaluation Pipeline

taches-principled has a multi-agent evaluation system: **grader** scores teaching effectiveness, **comparator** analyzes version deltas, **skill-auditor** reviews format and frontmatter, and **analyzer** synthesizes into 3 prioritized changes.

### Grading Dimensions

| Dimension | Weight | Measures |
|-----------|--------|----------|
| Routing Signal | 40% | Whether description gives clear trigger phrases |
| Delta Clarity | 30% | Whether the skill states what it changes from default |
| Teaching Posture | 20% | Whether it teaches principles over procedures |
| Anti-Pattern Quality | 10% | Whether wrong/right pairs include consequence explanation |

Format without teaching is decoration.

### Quick Audit

To audit a skill for quality, spawn a skill-auditor subagent: read the agent definition and use it as a subagent prompt with the skill path as context.

### Two-Claude Ad-hoc Testing

Draft candidate descriptions, create a small eval set of representative queries, test routing with two independent Claude instances, and refine based on results. The eval is a teaching instrument, not a gate.

---

## User Interaction

**Interact with users when gathering information or making decisions — not while executing a plan.**

When you need user input, ask clearly. Present options as clickable choices, not numbered lists or free-form prompts. Use checkpoints when verification is genuinely needed — not as a checkpoint for every task.

**When pausing for user input, say verbatim:** "use your tool to ask users your questions and prefill answers." This is the canonical phrase — names the capability generically, not the tool. Never hardcode tool names like "AskUserQuestion."

---

## Token Economy

- **Commands over skills for on-demand loading** — skills consume context always; commands load when invoked
- **Tool outputs dominate context** — typically 80-90% of total usage; apply progressive disclosure to avoid lost-in-middle effect
- **Specialized agents with narrow context** — broad-context agents hallucinate more
- **500-line guideline** — official stance is under 500 lines for optimal performance; split via progressive disclosure if content exceeds this. Hub skills may legitimately exceed this limit — the guideline applies to individual modes, not the total hub file.

---

## Design Principles

### High Freedom, High Trust

Every artifact must default to maximum autonomy for the AI invoking it. **High freedom** means telling the AI what outcome to produce, not how to produce it. **High trust** means omitting constraints, steps, and boundaries that the AI can infer from context.

- **Skills** are triggers, not recipes — describe what to accomplish and when, not step-by-step procedure
- **Agents** are system prompts, not scripts — they must be plain text with **NO markdown formatting** (no bold, no headers, no bullet lists). Write one coherent high freedom, high trust paragraph. **No precise output schema is expected** or enforced.
- **Commands** are lightweight pointers — no markdown body, no structural decomposition, 1-3 sentences of outcome

### Marketplace Synergy

This marketplace must synergize with any other marketplace or plugin the user may have installed. Every plugin and skill must work standalone with zero dependencies on other plugins. Skills describe their domain using shared workflow vocabulary — never referencing plugins by name. Do not add disclaimers, compatibility notes, or installation requirements referencing other plugins.

---

## Reference Tables

**When to read these docs:** Claude Code documentation is authoritative. You MUST read the relevant doc BEFORE working on the corresponding task — never proceed on assumptions. Don't memorize — know when to look.

### Official References

| Doc | When to Read |
|-----|-------------|
| [subagents.md](docs/official/subagents.md) | Before creating agents |
| [skills.md](docs/official/skills.md) | Before authoring skills |
| [hooks.md](docs/official/hooks.md) | Before configuring hooks |
| [commands.md](docs/official/commands.md) | Before creating commands |
| [permissions.md](docs/official/permissions.md) | Before configuring permissions |
| [agent-types.md](docs/official/agent-types.md) | Before choosing agent type |
| [agent-tool-params.md](docs/official/agent-tool-params.md) | Before spawning subagents |
| [agent-skill-integration.md](docs/official/agent-skill-integration.md) | Before adding skills to agents |

### Plugin References

| Doc | When to Read |
|-----|-------------|
| [plugins/creating.md](docs/official/plugins/creating.md) | Before creating plugins |
| [plugins/marketplaces.md](docs/official/plugins/marketplaces.md) | Before setting up marketplace |
| [plugins/plugins-reference.md](docs/official/plugins/plugins-reference.md) | Before advanced plugin work |

### Refreshing Official Docs

```bash
curl -sL "https://code.claude.com/docs/en/<topic>.md" -o docs/official/<topic>.md
```

Where `<topic>` matches the URL slug from `code.claude.com/docs/llms.txt`. Always verify the download starts with `> ## Documentation Index`.

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
| **Transformer Mandate** | Protocol principle: AI generates and scores, human makes final structural decisions |
| **Subagent-first** | Design principle where subagent spawning is the default execution mode, inline work is the exception |
| **Critique loop** | Pattern of spawning review subagents after artifact creation, iterating until no HIGH findings remain |
| **Skill budget** | Claude Code's 1% context limit for skill metadata; exceeded skills are silently dropped |
| **Front-load** | Placing trigger keywords at the start of descriptions so they survive truncation from the end |
| **CONTRAST section** | Explicit negative cases in descriptions to prevent false positive routing |
| **Under-triggering** | Claude's tendency to not invoke skills without explicit trigger phrases — primary routing failure mode |

---

## Meta-Rule

**Governs itself — all revisions must remain:**
- **Accurate** — Reflects current project state; outdated sections removed, not annotated
- **Actionable** — Every section answers "what do I do?" not just "what exists?"
- **Self-contained** — A new maintainer can understand the project from this file alone

---

## References

- [Claude Code Plugin Creation Guide](https://code.claude.com/docs/en/plugins.md)
- [Claude Code Plugin Marketplaces Documentation](https://code.claude.com/docs/en/plugin-marketplaces.md)
- [Claude Code Hooks Reference](https://code.claude.com/docs/en/hooks.md)
- [Claude Code Commands Reference](https://code.claude.com/docs/en/commands.md)
- [Plugin Submission Guide](https://claude.com/docs/plugins/submit.md)
- [context-engineering-kit](https://github.com/NeoLabHQ/context-engineering-kit) — token economy and subagent orchestration patterns