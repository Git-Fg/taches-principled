# Taches Principled — Development Guide

**For maintainers only.** This file is development practices and internal conventions for the human and the AI maintaining *this marketplace*. A Claude Code session that installs taches-principled as a marketplace plugin never reads it — that session only loads what ships under `plugins/`.

Treat every section as knowledge transfer from a human who worked on this codebase to future human maintainers (and to the AI assisting them).

## Maintainer-only vs end-user-visible

The single most important framing for every change in this repo:

| Path | Audience | When loaded |
|------|----------|-------------|
| `plugins/<plugin>/skills/<skill>/SKILL.md` (description) | **End-user Claude** | Pre-injected at startup |
| `plugins/<plugin>/skills/<skill>/SKILL.md` (body) | **End-user Claude** | On trigger |
| `plugins/<plugin>/skills/<skill>/references/*` | **End-user Claude** | When SKILL.md cites it imperatively |
| `plugins/<plugin>/agents/*.md` | **End-user Claude** | At spawn |
| `plugins/<plugin>/commands/*.md` | **End-user Claude** | On invocation |
| `plugins/<plugin>/hooks/*` | **End-user Claude** | At lifecycle events |
| `.claude-plugin/marketplace.json` | **Marketplace installer** | At plugin install |
| `CLAUDE.md` (this file) | **Maintainer only** (human + AI in this repo) | Only when working *in this repo* |
| `knowledge/` | **Maintainer only** | Read by us when authoring; invisible to anyone installing the marketplace |
| `README.md`, `CHANGELOG.md` | **Human readers** on GitHub | Never loaded into a Claude session |

The implication for every recommendation, reasoning artifact, or research note: **if it lives outside `plugins/`, end-user Claude never sees it.** Reasoning kept only in `knowledge/` or in this file is scaffolding for the maintainer. To change end-user behavior, the change has to materialize as edits inside `plugins/` (a skill body, an agent definition, a command body, a reference file cited by an SKILL.md, or a hook script).

When generic agents and specialized inline versions cover the same capability, prefer the generic agent. A generic agent's body becomes the canonical version; domain-specific knowledge lives in the skill that invokes it, not in the agent definition itself. An agent is only orphaned when no skill describes a capability it would resolve.

---

## Quick Start for New Maintainers

!`find plugins -mindepth 1 -maxdepth 1 -type d | wc -l` plugins, !`find plugins -name SKILL.md | wc -l` skills, !`find plugins -path '*/agents/*.md' | wc -l` agents, !`find plugins -name '*.md' -path '*/commands/*' | wc -l` commands — re-run any of these for current state.

1. `git clone` and run `python3 scripts/regenerate-marketplace.py --help` to see how `marketplace.json` is rebuilt from the two SSoT files.
2. Skim one hub SKILL.md end-to-end (e.g. `plugins/core-principled/skills/refine/SKILL.md`) to internalize the decision-router + policy/mechanism pattern.
3. Spawn the `tp-critic` subagent against any plugin to see the critique-loop pattern in action.
4. Read the **Self-Check** at the bottom of this file before opening a PR — it is the contract this marketplace commits to.

**Cross-session memory** for the human + AI working in this repo lives at `~/.claude/projects/<project>/memory/MEMORY.md` — where `<project>` is the URL-encoded absolute path slug of this repo (leading `/` → `-`, all other `/` → `-`). Run `ls ~/.claude/projects/ | grep $(basename $(pwd) \| tr '[:upper:]' '[:lower:]')` to locate your own slot. Populate it only with facts that would otherwise be lost between sessions (recurring gotchas, audit cadences, the *why* behind an architectural choice). Cross-skill cross-plugin cross-platform facts belong in `knowledge/`; transient session artifacts go in `.principled/`. End-user behavior is shaped by what ships under `plugins/`, not by any of the above.

---

## Core Design Principle

Every artifact is consumed by a Claude Code instance starting with zero context. Design as if Claude loads into a fresh session, reads only the plugin's files, and must decide what to do.

Ask: Does the routing make sense without external context? Does the description give enough trigger signal for the right skill to fire? Does the body teach judgment or just prescribe steps?

High trust means: write descriptions that route correctly, then stop. Don't add fallbacks, disclaimers, or routing logic for edge cases the model can handle.

---

## Orchestration Model

**The main agent implements. Subagents self-review.** The costly main agent (Sonnet/Opus) owns cognition AND implementation. Subagents are isolated-context workers — primarily reviewers that judge the main agent's work free of its accumulated biases, plus explorers/researchers that absorb large exploration tokens the main agent shouldn't carry.

The marketplace ships **6 named subagents**: `tp-critic` (universal reviewer, parameterized by a lens), `tp-explorer` (universal codebase mapper, parameterized by a scope), `tp-researcher` (universal external researcher), `mcp-quality-judge` (the MCP-server exemplar), `sadd-judge` (candidate scoring), and `wiki-searcher` (the single read-only-tools exception). All "specialized reviewer" roles — what used to be 50+ thin agents like `tp-bug-hunter`, `security-reviewer`, `rust-cargo-reviewer` — collapse into `tp-critic` with a one-sentence lens in the spawn prompt. Implementation, integration, edits, and trivial work run inline.

**The decision axis is context isolation, not task size.** Spawn a subagent when (a) the task burns ≥10k intermediate tokens, (b) the return is a small summary vs a huge journey, AND (c) the parent benefits from not carrying that journey. Fail any one → fold into inline work.

### Subagent-First Execution Contract (revised)

**Default: inline implementation. Spawn for isolated-context review.** The marketplace no longer defaults to "spawn subagents for everything." A specialized reviewer is now a one-sentence lens passed to `tp-critic`, not a separate agent file. Implementation lives in the main agent unless the files are not in its context.

The contract has two axes: **what kind of work** is being done (work-type table) and **what scale** the work is at (task-scale table). Pick the answer from both tables; the stricter of the two wins.

#### Work-type axis

| Work Type | Default Mode | Exception (inline always) |
|-----------|--------------|----------------------------|
| Implementation | **Inline** (main agent edits) | Files not in main context → spawn `tp-critic` w/ lens "audit the implementation" for isolated review |
| Exploration | Spawn `tp-explorer` w/ scope | Directory listing of <5 files |
| Research | Spawn `tp-researcher` w/ question | Single web search query |
| Verification (read-only checks) | **Inline** (run the command) | Large log dump → spawn `tp-explorer` w/ scope to parse |
| Critique/Review | Spawn `tp-critic` w/ lens (parameterized) | Glance-check of trivial output |
| Brainstorm/Ideate | **Inline** (generate inline; optionally spawn `tp-critic` to stress-test) | Multi-perspective adversarial scoring |
| Debate/Compare | Spawn multiple `tp-critic` w/ different lenses | Never inline |
| Reflection | Spawn `tp-critic` w/ lens "audit this decision" | Never inline |

#### Task-scale axis

| Task scale | Right primitive | Why |
|---|---|---|
| Trivial — 1 file, <10 lines, or single search | Inline | Setup overhead exceeds task complexity |
| Non-trivial single-context — 3–10 files, single methodology, side task | Inline + `tp-critic` w/ lens for review | Main agent has the context; isolated review earns its cost |
| Multi-stage with fan-out → verify → synthesize | Multiple `tp-critic` w/ different lenses + inline work | Same isolation benefit, no specialized agent proliferation |
| Codebase-wide, many-file, multi-methodology | `tp-explorer` w/ scope for the map + inline implementation + `tp-critic` w/ lens for review | The 6-agent roster covers it |
| Long-running with external triggers | Orchestration script + recurring checks + push channels | Reacts to CI, alerts, scheduled events; survives idle time |

**The rule: If the skill loaded, the work is non-trivial by definition — pick the mode from the task-scale table.** The skill exists precisely because the task exceeds trivial inline execution. Trust the skill's own existence as the signal.

The 6 named subagents under each plugin's `agents/` directory are the durable role library. Both inline spawns and orchestration-script spawns dispatch to them by name. Specialized reviewer roles that previously required new agent files now pass a lens prompt to `tp-critic` at the call site.

**Spawn pattern for skill bodies:**
```
## Execution Mode

**Default: inline implementation, isolated-context review.** Implement the work directly; spawn [role] subagents only when the review/exploration earns its isolation cost.

**Spawn pattern (when spawning is justified):**
- Lens (for tp-critic): "[specific review angle]"
- Scope (for tp-explorer): "[specific exploration question]"
- Question (for tp-researcher): "[specific external research question]"
- Output: [what the subagent must return — bounded summary, not raw exploration]

After subagent returns: synthesize, then optionally spawn another [role] subagent
for verification. Loop until no HIGH findings.
```

Anti-pattern: "If the task is complex, consider using subagents." Use declarative language: "Spawn `tp-critic` w/ lens Y for isolated review."

### When the Main Agent Acts Directly

- Implementation: edits to files in the main context
- Reading and synthesizing subagent output from scratchpad
- Making judgment calls between competing subagent recommendations
- Final aggregation, summary writing, and commit
- Verification: running a single test command, reading the output
- Wiki ingest and lint (inline operations on the resolved wiki path)

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

**Mandatory description uniqueness check:** If two skill descriptions can be paraphrased to mean the same thing, they will misroute. Before shipping, verify each description's trigger set is mutually exclusive from all others. The diagnostic: ask "Could a user naturally phrase this request so it matches either skill?" If yes, split or reword.

**CONTRAST section required for overlapping domains.** When two skills operate in adjacent domains, explicitly state what each does NOT cover. Example:
```
CONTRAST:
- NOT for: CSS styling, HTML templates, frontend framework questions
- NOT for: database schema design, SQL query optimization, ORM usage
```

**Hook limitations:** No hook event directly loads a skill. Skill activation is description-matching only.

---

## Hub-Spoke Skill Architecture

Skills can operate as **hubs** (orchestrate other skills via decision routing) or **spokes** (do one thing). You MUST read [Skills](knowledge/raw/official/skills.md) for hub-spoke patterns BEFORE adding or merging skills.

### Hub Skills — The `Modes:` Directive

For hub skills with distinct invocation contexts (audit, coding, review, etc.), use the **top-of-body `Modes:` directive**. This keeps the hub under 50 lines and defers all domain depth to `references/`.

```
--- name: taches-hub
description: Routes tasks to domain specialists. Use for any pharmacology, diagnostic imagery, or Anki automation request.
---
**Persona:** You are the taches-principled orchestrator. You do not execute tasks yourself; you delegate to domain specialists.

**Modes:**
- **coding**: Delegate to the `rust-dev` agent. Focus: async patterns, Cargo workspaces.
- **review**: Delegate to the `audit` agent. Focus: security review, dependency checks.
- **medical**: Delegate to the `pharma` agent. Focus: CGRP drug comparisons, prescription logic.
- **anki**: Delegate to the `anki` agent. Focus: card generation, occlusion workflows.

## Shared Workflow
1. Identify the user's domain from their request.
2. Load the appropriate domain skill via `SkillTool`.
3. Pass all relevant context explicitly; do not assume the sub-skill retains state.
```

**Token math:** Hub <500 tokens + each domain <2,000 tokens + `references/` unlimited = safe active budget even with 3 domains loaded.

**Anti-pattern:** Fat hub with inlined domain logic. If the hub exceeds 500 tokens, it is doing too much — move the domain procedures to `references/` and keep the hub as a pure router.

### Exempt Skills (Do Not Merge)

- `refine-task` + `implement-task` — task lifecycle (refine produces specs, implement executes)
- `ideation` + `add-task` — capture lifecycle (ideation explores, add-task persists)
- Marketplace hub skills — plugins with multi-mode routing

### Merge Criteria

**Merge when:** Skills share the same purpose; skills use different frameworks/methods for the same domain; trigger phrases overlap in meaning; the resulting hub has a clear decision router with distinct modes.

**Keep separate when:** Skills serve distinct workflow stages; skills have distinct entry/exit contracts other skills depend on; trigger density is high (5+) and routing is reliable.

### Decision: Merge or Keep?

| Hub Skill | Skills Merged | Rationale |
|-----------|---------------|-----------|
| `plan-lifecycle` | `create-plans` + `execute-plans` | Compositional pair; project planning to execution lifecycle |
| `diagnose` | `analyse` + `analyse-problem` + `root-cause-tracing` | All problem investigation; different methods, same purpose |
| `refine` | `reflexion` (all modes) + `write-concisely` | All improve artifact quality |
| `subagent-orchestration` | `subagent-orchestration` + `create-subagents` | Both teach multi-agent patterns |
| `sadd` (tp-sadd) | `do-competitively` + `execute` + `sadd-judge` + `sadd-patterns` + `sadd-tot` | All structured agent-driven dev |
| `git` (tp-git) | `git-ship` + `git-review` + `git-issues` + `git-advanced` | All git workflow automation |
| `fpf` (tp-fpf) | `fpf-propose` + `fpf-maintenance` + `fpf-read` | All first-principles reasoning |
| `ddd` (tp-ddd) | `code-architecture` + `code-quality` + `code-transparency` + `code-api` | All domain-driven design |
| `rust` (tp-rust) | `rust-scaffold` + `rust-workspace` + `rust-quality` + `rust-release` | All Rust project lifecycle (init → structure → quality → release) |

Hub-and-spoke consolidation target: 22-28 skills. Run `find plugins -name SKILL.md | wc -l` for current inventory.

---

## Plugin Architecture

**Two-source catalog model** — `marketplace.json` is generated from two sources, not hand-edited:
- `name` / `version` / `description` per plugin: `plugins/*/.claude-plugin/plugin.json` (spec-authoritative per CHANGELOG 1.12.0)
- `source` / `homepage` / `repository` / `license` / `category` / `keywords` per plugin: `.claude-plugin/_meta.json` (catalog-only metadata)

You MUST read [knowledge/raw/official/plugins/marketplaces.md](knowledge/raw/official/plugins/marketplaces.md) and [knowledge/concepts/contributing.md](knowledge/concepts/contributing.md) BEFORE modifying marketplace.json or adding plugins.

**Directory structure (one entry per plugin under `plugins/`):**
```
plugins/
├── core-principled/           # Full dev lifecycle — planning, review, debugging, contract design
├── claude-cli-wrapper/        # Skill teaching direct Claude Code CLI usage via Bash
├── tp-sadd/                   # Structured agent-driven development
├── tp-fpf/                    # First principles reasoning
├── tp-git/                    # Git workflow automation
├── tp-mcp/                    # MCP server design, implementation, tool-surface
├── tp-rust/                   # Rust project lifecycle (single hub, 4 modes; reviews via `tp-critic` w/ lens, polish inline)
├── tp-session-audit/          # Session meta-review and behavioral analysis
└── tp-wiki/                   # Personal wiki tools (search, lint, ingest)

.claude-plugin/
├── _meta.json                 # Catalog metadata SSoT (source, keywords, etc.)
└── marketplace.json            # Derived from per-plugin plugin.json + _meta.json
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

## Agent and Skill Naming Convention

Naming is **asymmetric by design**. After the 55→6 subagent consolidation (see `CHANGELOG`), the marketplace ships **6 named subagents**:

| Plugin | Agent | Role |
|---|---|---|
| `core-principled` | `tp-critic` | Universal isolated-context reviewer (lens-prompted) |
| `core-principled` | `tp-explorer` | Universal isolated-context codebase mapper (scope-prompted) |
| `core-principled` | `tp-researcher` | Universal isolated-context external researcher (question-prompted) |
| `tp-mcp` | `mcp-quality-judge` | MCP-server domain exemplar; preloads `mcp-expertise` |
| `tp-sadd` | `sadd-judge` | Candidate scoring against a rubric |
| `tp-wiki` | `wiki-searcher` | Read-only wiki query (the single allowed `tools:` exception) |

**The naming rule, as it ships today:**

| Plugin | Agent name prefix | Skill name prefix | Examples |
|---|---|---|---|
| `core-principled` (the legacy meta-plugin) | `tp-*` | (no prefix) | `tp-critic`, `tp-explorer`, `tp-researcher`; skills like `refine`, `diagnose`, `plan-lifecycle` |
| `tp-sadd`, `tp-fpf`, `tp-git`, `tp-mcp`, `tp-rust`, `tp-session-audit`, `tp-wiki` (the newer sub-plugins) | `<plugin-name-without-tp-prefix>-*` | `<plugin-name-without-tp-prefix>-*` | `sadd-judge`, `mcp-quality-judge`, `wiki-searcher` |

**Why the asymmetry exists:** `core-principled` was the first plugin
and the `tp-` prefix (short for "taches-principled") was a
namespace disambiguator in case a user installed multiple
marketplaces with overlapping agent names. When we started
extracting focused sub-plugins (`tp-sadd`, `tp-fpf`, etc.), each
sub-plugin became its own namespace, so the inner prefix became
redundant — the plugin name itself is the namespace.

**New agents/skills MUST follow the sub-plugin rule:** if you add
an agent or skill to `core-principled`, use `tp-*`; if you add one
to `tp-sadd`/`tp-fpf`/etc., use the sub-plugin prefix.

**Before adding a new specialized reviewer agent, ask: "Could this be a one-sentence lens passed to `tp-critic` instead?"** If yes, do not add an agent file. The 55→6 consolidation removed ~50 thin wrapper agents; the lens-prompt pattern is the canonical way to specialize review without file proliferation.

**Why we don't rename in a sweep:** every hardcoded spawn (e.g.,
`Agent(name="tp-critic", prompt=...)`) is a maintenance contract. The
6 keepers each have hardcoded spawns across multiple plugins; mechanical
renames are breaking changes.

When documenting a new agent in body text or commit messages,
spell the full name once (e.g., "`tp-critic`") and then use
the short form.

---

## Artifact Standards

### Agent Tool Contract

**An agent's declared tools MUST match its stated capabilities.** When an agent claims to write findings to disk, it needs the Write tool. If the capability exists in the description but the tools field is missing, the agent cannot fulfill its contract.

### Agent Color Convention

**Use `color` in agent frontmatter to signal role archetype.** This helps maintainers and auditors quickly identify agent purpose at a glance.

| Color    | Typical Use                                  |
| -------- | -------------------------------------------- |
| `red`    | Critical, security, "red team" tasks         |
| `blue`   | Analysis, review, architecture               |
| `green`  | Success-oriented, implementation, "go" tasks |
| `yellow` | Caution, validation, code review             |
| `purple` | Creative, complex reasoning                  |
| `orange` | General purpose, documentation               |
| `pink`   | Distinctive/specialist roles                 |
| `cyan`   | Research, exploration, debugging             |

### Tool Scoping Fields

| Field | Artifact | Effect | When Omitted |
|-------|----------|--------|-------------|
| `tools:` | Agent definitions | **Hard allowlist** — only listed tools accessible | Inherits all tools |
| `allowed-tools:` | Skills, Commands | **Pre-approval** — skips prompts but all tools remain callable (Edit/Agent/Skill bypass Write) | Normal permission settings |
| `disallowed-tools:` | Skills | **Hard block** — removes specific tools from pool | No tools blocked |

**Common mistake:** Treating `allowed-tools` as a security boundary. It only skips permission prompts. For true restriction, use agent `tools:` allowlists or skill `disallowed-tools:`.

## Agent Frontmatter Best Practices

Three rules for plugin agent frontmatter. Apply these on every
agent you author or audit. The rules are deliberately permissive
in the default direction (don't restrict) and restrictive in
the override direction (don't tune).

### Rule 1: Never set `tools:` unless you really mean to restrict

**Default:** no `tools:` field. The agent inherits the full
tool pool, including:
- All built-in tools (Read, Write, Edit, Bash, Glob, Grep, etc.)
- All MCP servers the user has configured globally
- All custom tools from the user's `settings.json` quirks
- All subagent and Skill tools

**Why this matters:** A `tools:` field is a HARD allowlist.
Anything not in the list is invisible to the agent. If the
user has an MCP server they use everywhere, the subagent
silently loses access to it. The same for any project-specific
tool the user has configured.

**When to set `tools:`:** only when the restriction IS the
point — when the agent's body policy says "NEVER do X" and
the tool boundary enforces it. The current example is
`wiki-searcher`, which is declared read-only
(`tools: [Read, Glob, Grep]`) because the body says
"NEVER write or modify any wiki file". Without the tool
boundary, the body policy is a request, not a guarantee.

**Anti-pattern:** setting `tools:` for "principle of least
privilege" hygiene on agents that have no specific reason
to be restricted. The cost is real (loses user tools, loses
MCP servers, loses settings.json quirks) and the benefit
is imaginary (the agent has no specific tool boundary to
enforce — its body policy is enforced by the model, not
the runtime).

### Rule 2: Never set `model:` unless you need `opus`

**Default:** no `model:` field. The agent inherits the model
of the spawning orchestrator. No field at all = inherit.

**Why this matters:** Setting `model:` is a tuning knob that
breaks in three ways:
1. **Cost multiplier** — a Sonnet agent spawned by an Opus
   orchestrator wastes 5-10x budget for no quality gain
   (the agent's task is usually simple enough that the
   orchestrator's model handles it just as well).
2. **Quality demotion** — a Haiku agent spawned by a Sonnet
   orchestrator drops the reasoning quality below the
   orchestrator's expectation.
3. **Static lock-in** — the model assignment in frontmatter
   doesn't track the user's current model. If the user
   upgrades from Sonnet to Opus, the agent stays on whatever
   was hardcoded.

**When to set `model:`:** only in the ultra-rare case where
the agent needs `model: opus` for genuinely hard reasoning —
multi-step inference over a large body of code, evaluating
subtle trade-offs, or synthesizing across many sources. No
agent in the current marketplace qualifies; if you find
yourself reaching for `model: opus`, justify it in the
commit message and add a one-line comment in the body.

**Anti-pattern:** sprinkling `model: sonnet` across all
agents because "Sonnet is the safe default". It isn't — the
safe default is to inherit. Sonnet is only safe if you've
measured the agent's task complexity and confirmed Sonnet
is the right ceiling. For a typical review/analyze agent,
Sonnet ≠ safe; inherit = the orchestrator's choice.

### Rule 3: Set `background: true` proactively when the agent is long-running

**Default:** no `background:` field (equivalent to `false`).
The agent runs synchronously and the orchestrator blocks
until it returns.

**When to set `background: true`:** as soon as the agent's
typical runtime exceeds ~30s, OR the agent is parallel-by-
design (fanned out, competitive generation, multi-wiki
operations), OR the user would benefit from "fire and
report" UX.

| Typical runtime | Recommendation |
|---|---|
| < 5s | foreground (background adds notification overhead with no benefit) |
| 5–30s | foreground (user expects an answer soon) |
| 30s–5min | **background: true** |
| > 5min | **background: true** |
| Parallel-by-design (fanned out, N candidates, multi-wiki) | **background: true** |

**Why this matters:** Background lets the orchestrator
proceed with the next step while the agent works. The user
can issue another command instead of staring at a spinner.
For competitive generation (sadd-generator in COMPETE mode,
fanned-out file reviewers in `git-pr-reviewer`), background
is the only way to get parallelism without explicit
`TaskOutput` coordination.

**Anti-pattern:** leaving every agent foreground because
"the user might want to see the result inline". For ops
>30s, the user has gone back to another tab. Foreground
just blocks the orchestrator for no benefit and serializes
work that could be parallel.

For the 6 marketplace keepers: `tp-critic`, `tp-explorer`, `tp-researcher` are typically short-lived (foreground). `mcp-quality-judge`, `sadd-judge`, `wiki-searcher` may be parallel-by-design depending on call site.

### How the three rules interact

The three rules are independent but combine cleanly:

- An agent that follows Rule 1 (no `tools:`), Rule 2 (no
  `model:`), and Rule 3 (`background: true` when relevant)
  is a "natural subagent" — it inherits everything from the
  host environment and runs non-blocking. The user gets
  fire-and-report UX with full tool access.
- An agent that sets `tools:` is "restricted by design" —
  the body policy is enforced at the tool boundary. Only
  do this when the restriction IS the point.
- An agent that sets `model: opus` is "tuned for depth" —
  pays the cost multiplier for genuinely hard reasoning.
  Only do this when the task actually requires it.

**Reference implementation:** ground your next audit in current state — the numbers below are point-in-time, recompute at every audit:

!`find plugins -path '*/agents/*.md' -type f | wc -l` agents, total
!`grep -l '^tools:' plugins/*/agents/*.md 2>/dev/null` agents still carrying a `tools:` allowlist (should be ≤ 1: only `wiki-searcher`)
!`grep -l '^model:' plugins/*/agents/*.md 2>/dev/null` agents still carrying an explicit `model:` (should be 0)
!`grep -L 'background:' plugins/*/agents/*.md 2>/dev/null | wc -l` foreground agents — flag any with typical runtime >30s as candidates for `background: true`

The audit that produced the original rules applied them: stripped `tools:` from every agent except `wiki-searcher` (read-only enforcement is the point), stripped `model:` everywhere (let agents inherit), and added `background: true` to long-running agents per the decision table.

The only `tools:` allowed-list remaining in the marketplace
is `wiki-searcher`'s read-only enforcement, which is the
canonical use case for the field.

### Artifact Taxonomy

Five artifact types with distinct loading behaviors, token costs, and **audiences**:

| Artifact | Audience | Loading behavior |
|---|---|---|
| **Skill description** (frontmatter) | End-user Claude | Pre-injected at startup, always present |
| **Skill body** (SKILL.md content) | End-user Claude | Loaded on trigger; reference files load lazily on imperative citation |
| **Agent definition** | End-user Claude | Per-spawn, loaded at spawn time |
| **Command body** | End-user Claude | User-invoked, zero context until used |
| **CLAUDE.md / `knowledge/`** | **Maintainer only** | Loaded only when working in this repo as a contributor; **end-user Claude never sees it** |

The first four ship under `plugins/` and `.claude-plugin/`. The fifth lives at the repo root and under `knowledge/` — it is scaffolding for the human and AI maintaining the marketplace, not for the marketplace's users. Every reasoning artifact written to `knowledge/`, every brainstorm, every synthesis: invisible to end users unless its conclusions materialize as edits inside `plugins/`.

### Path Configuration

**Use command arguments and environment variables for paths — never hardcode absolute paths.**

- `{{CLAUDE_WORKING_DIR}}` for the current working directory
- `$ARGUMENTS` for user-provided path parameters
- Bash environment variables (`$HOME`, `$PWD`) for shell operations

### Skill-Internal File References

**Three canonical rules govern skill file referencing:**

1. **Default resolution**: Any path written within a skill that points to its own supporting content is, by default, resolved within that skill's folder. For example, a reference to `references/plan-format.md` from within the `plan-lifecycle` skill resolves to `plugins/core-principled/skills/plan-lifecycle/references/plan-format.md`.

2. **No parent traversal**: File paths MUST NOT use relative parent paths (`../`) to traverse outside their containing skill directory. Skills are self-contained units; all internal references must resolve locally within the skill's root folder. Cross-skill references must be semantic (citing a skill or role by name) rather than filesystem-based.

3. **Centralized routing**: ONLY the main SKILL.md file is permitted to cite supporting files. Reference files (in `references/`, `agents/`, `templates/`, `scripts/` folders) must never cross-cite other reference files. The SKILL.md is the sole, centralized router for all internal citations.

4. **Subagent → preloaded-skill references (exception to Rule 3)**: When a subagent declares a skill in its `skills:` frontmatter, the subagent's body prompt MAY cite that skill's own `references/` files. The skill is already loaded for the agent, so its references are in scope. The citation MUST be a single natural-language imperative sentence ("you MUST start by reading the `wiki` skill's `references/subagent-arguments.md`") — not a procedural step and not a numbered list. The directive's job is to guarantee the reference is loaded, not to prescribe how the agent uses it. **The generalist principle still wins:** after the imperative, prefer natural-language steering prose over rigid procedure, and let the agent decide how to apply what it read. Cross-skill citations (citing references from a skill the agent has NOT loaded) remain forbidden — the gate is "if you preload it, you can cite it; if you don't, you can't." The official Claude Code docs confirm the parent's citation directive is NOT transitive to spawned subagents ([`agent-sdk/subagents.md`](https://code.claude.com/docs/en/agent-sdk/subagents.md#what-subagents-inherit) — "Preloaded skill content, unless listed in `AgentDefinition.skills`" is explicitly excluded from inheritance), so the subagent needs its own `skills:` entry to receive the parent's body OR an independent citation in its own prompt. This rule codifies the second path.

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

### The Chicken-and-Egg Reference Anti-Pattern

**The Paradox:** Placing loading triggers or "When to read" instructions inside a reference file is a logical impossibility. The AI agent must consume the context tokens to read the file before it ever sees the instruction on whether it should have read it. If the agent reads the file because the trigger was satisfied, the trigger's condition is already fulfilled — making the condition self-referential and meaningless.

**Why it fails:**
1. The agent must load the reference file to see the "When to read" instruction
2. Loading the file consumes the very tokens the instruction is trying to govern
3. The instruction cannot prevent the agent from reading the file — by the time the agent sees the instruction, it has already read the file
4. Any conditional logic inside the reference file creates a circular dependency

**The strict rule:** Reference files must be pure content — no frontmatter, no loading triggers, no "When to read" sections, no conditional loading paragraphs. All conditional loading logic must reside exclusively in the parent SKILL.md router. The SKILL.md cites references imperatively; reference files never cite themselves or contain routing logic.

**Orthogonal to Rule 4 above:** The chicken-and-egg rule governs what a reference file may contain (no routing logic inside the reference). Rule 4 governs who may issue a citation from outside the file (a subagent that has preloaded the parent skill may). The two rules do not conflict — a reference file remains pure content, and a subagent body may still cite it from outside.

**Correct pattern:**
- SKILL.md body: "You MUST read `references/patterns.md` BEFORE writing code."
- references/patterns.md: Pure content, no loading instructions

**Wrong pattern (chicken-and-egg):**
- references/patterns.md: "When to read this file: before writing code" — LOGICAL IMPOSSIBILITY
- The agent reads the file to see the instruction; the instruction cannot prevent reading

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

### Git Safety Protocol

**NEVER use `git reset --hard` or any destructive git command.** These wipe working tree state that cannot be recovered from git alone. If you need to restore code to a known-good state:

1. **Use `git diff` or `git show`** to identify exactly what changed and what the original content was
2. **Use surgical `Edit` or `Write` tools** to restore specific files or sections — never wipe an entire tree
3. **Use `git stash`** to safely set aside changes you want to preserve but not commit
4. **Use `git checkout HEAD -- <path>`** to restore a single file to HEAD state (non-destructive overwrite)
5. **Use `git log` + `git show`** to inspect history and reconstruct what you need

**The hard reset anti-pattern:** `git reset --hard HEAD` was used in this session and wiped staged skill improvements (flattened `references/modes/`, expanded stubs). The changes were recovered by re-reading this summary and re-executing. Future agents must not repeat this — use selective restoration instead.

**Recovery protocol when you've lost track of what was staged:**
1. Run `git status` to see what files are modified vs staged
2. Use `git diff --staged` to recover staged content you thought was lost
3. Re-apply any work product that existed before the destructive command using what you can reconstruct from this session's summary

---

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

## Security Boundaries

### The Two-Layer Model

Claude Code's tool control operates at two independent layers:

| Layer | Mechanism | Effect |
|-------|-----------|--------|
| **Availability** | `tools:` list, bare `disallowedTools:` | Controls whether the tool appears in Claude's context at all. If omitted, Claude never attempts it. |
| **Permission** | `allowedTools:`, scoped `disallowedTools:` | Controls whether a tool call is approved once Claude attempts it. |

A bare `"Bash"` in `disallowedTools` removes Bash from the model's context entirely (availability). A scoped `"Bash(rm *)"` leaves Bash visible but blocks matching calls at execution time (permission).

### The `.mcp.json` Bug — Do Not Rely On It

**Confirmed bug:** `allowedTools` and `disallowedTools` fields inside `.mcp.json` are **completely ignored**. The MCP server exposes all tools regardless of user-defined restrictions. This is a genuine security boundary violation — the config file provides false confidence.

**What actually works today:**
- **CLI flags:** `--disallowedTools "Bash(rm *)"` and `--allowedTools "Read,Write"` are strictly enforced
- **PreToolUse hooks:** Fire even in `bypassPermissions` mode — the only layer that survives it
- **`settings.json` permissions:** Evaluated at runtime but primarily advisory, not strictly enforced

### The Precedence Cascade

Rules are evaluated in order: **deny → ask → allow**. The first match wins. Critically, deny rules from **any scope** block allow rules from **any other scope**. If managed settings deny a tool, no CLI flag can override it.

```
Managed settings (unoverridable)
  ↓ CLI arguments (--disallowedTools, --allowedTools)
  ↓ Local project settings (.claude/settings.local.json)
  ↓ Shared project settings (.claude/settings.json)
  ↓ User settings (~/.claude/settings.json)
```

### Defense-in-Depth for Plugins

For plugins exposing MCP servers, implement this stack:

1. **PreToolUse hooks** for deterministic blocks (e.g., block `rm -rf`, block `mcp__*__delete_*`). Hooks survive `bypassPermissions` — they are the only reliable enforcement layer.
2. **CLI flags** in automation scripts: `--disallowedTools "Bash(rm *),mcp__*__delete_*"` for headless execution.
3. **`settings.json`** for team-wide defaults (auto-allow Read/Grep, ask for Bash, deny destructive MCP patterns).
4. **Sandboxing** (`sandbox.filesystem`, `sandbox.allowedDomains`) as the OS-level backstop.

### The Tool Pool Assembly Pipeline

Claude Code assembles the tool pool in this order:

1. Base tool enumeration (54 tools max)
2. Mode filtering (e.g., `CLAUDE_CODE_SIMPLE` drops most tools)
3. **Deny rule pre-filtering** — strips blanket-denied tools before MCP tools are merged
4. MCP tool integration (merges `.mcp.json` servers)
5. **Deduplication by name** — built-ins win over MCP tools

Deny rules are applied **before** MCP tools are merged. But the `.mcp.json` bug means step 4 ignores per-server `allowedTools`/`disallowedTools` — the server dumps all tools into the pool, and only step 5 deduplicates them.

---

## MCP Server Naming

### The Convention Is Claude Code's Internal Implementation

The `mcp__{server_name}__{tool_name}` format is **Claude Code's internal convention**, not the MCP protocol standard. It is enforced at tool discovery time in `McpToolBuilder` (or equivalent). The double-underscore serves two purposes:

- **Collision prevention:** A built-in `search` tool and an MCP `search` tool become distinct names (`search` vs `mcp__github__search`)
- **Provenance visibility:** In logs and transcripts, `mcp__github__create_issue` immediately shows the GitHub MCP server as the source

### Where Collisions Actually Happen

**Two collision surfaces:**

1. **Server name collisions:** Claude Desktop includes built-in MCP extensions (Filesystem, Google Drive, etc.). If you name a custom MCP server `filesystem` in `.mcp.json`, it collides with the built-in — the built-in typically wins or crashes, and your config is ignored.

2. **Tool name collisions across servers:** If two MCP servers both expose `search`, they become `mcp__serverA__search` and `mcp__serverB__search` — no direct collision. But if you have two servers with the **same server name** in different scopes (user vs project settings), deduplication applies and **built-ins take precedence over MCP**.

**Security risk:** A malicious MCP server can register tools with names similar to legitimate ones. If the host deduplicates naively or the user approves based on name familiarity, the malicious tool hijacks the execution path.

### Naming Rules for This Marketplace

| Anti-pattern | Recommended |
|---|---|
| `mcp__filesystem__read_file` (generic server name) | `mcp__taches-anki__read_apkg` |
| `mcp__taches-rust__search` (generic verb) | `mcp__taches-rust__grep_cargo_toml` |
| 30 tools per server | 5–15 outcome-oriented tools per server |
| `allowedTools` in `.mcp.json` | `--disallowedTools` CLI flag + PreToolUse hooks |

**Namespace your servers as `taches-{domain}`** (e.g., `taches-rust`, `taches-pharma`, `taches-anki`). This makes tool names unambiguous and grep-friendly. Avoid generic names like `search`, `db`, or `filesystem`.

**Avoid overlapping tool names across domains.** Even with server namespacing, if `taches-rust` and `taches-pharma` both expose `validate`, the model may confuse them in its planning phase. Use domain-specific verbs: `rust_check_workspace` vs `pharma_validate_prescription`.

**Curate ruthlessly to 5–15 tools per server.** One server, one job. This reduces collision surface and improves model routing accuracy.

---

## Skill Authoring

You MUST consult the `skill-authoring` skill for detailed guidance on skill categories, policy/mechanism pattern, progressive disclosure, frontmatter fields, cross-skill references, decision routers, description optimization, and command format BEFORE authoring or modifying any skill.

You MUST read [Skills](knowledge/raw/official/skills.md) for frontmatter field reference BEFORE writing skill frontmatter.

---

## Version & Release

**Marketplace version** and **plugin version** are independent. Plugin versions increment on any content change. Marketplace version increments when releasing a collective update across all plugins.

### Update Sequence

```bash
# 1. Make your changes
git add -A && git commit -m "message"

# 2. Bump plugin version in its plugin.json (minor for features, patch for fixes)
# Edit plugins/<name>/.claude-plugin/plugin.json — bump the "version" field

# 3. Re-generate marketplace.json
python3 scripts/regenerate-marketplace.py

# 4. Push
git push
```

> **Single source of truth:** `name`, `version`, `description` come from the per-plugin `plugin.json`. All other catalog fields (`source`, `category`, `keywords`, `homepage`, `repository`, `license`) come from `.claude-plugin/_meta.json`. Never edit `marketplace.json` directly — it is regenerated from these two sources.

### CHANGELOG Convention

Version format: `[1.2.3]` — semantic versioning. Default is minor bump. Patch for typos and docs only. Major only for architectural changes.

You MUST follow the template in `knowledge/templates/changelog-entry.md` for every entry.

### Commit Messages

Format: `<type>: <short description>` with types: `feat`, `fix`, `refactor`, `docs`, `chore`.

### Git Workflow

Create feature branches, commit with conventional messages, push, and create PRs via gh.

---

## Before Any Commit — Self-Check

### Project Checks

- [ ] README updated if structure changed; synced to all knowledge/ locations
- [ ] CHANGELOG entry added
- [ ] `marketplace.json` plugin description, version, and keywords updated
- [ ] `marketplace.json` has no duplicate `version:` keys per plugin entry (CHANGELOG 1.14.0 regression class) — run `jq -e '.plugins | all(. as $p | ([keys[] | select(. == "version")] | length) == 1)' .claude-plugin/marketplace.json`
- [ ] No MCP runtime dependencies
- [ ] No broken cross-references between skills
- [ ] No shared knowledge/ folders expecting cross-skill reuse

### Skill Quality Checks

- [ ] **Spawn-when-isolated check**: Skills that need isolated-context review (adversarial judgment, exploration of many files, external research) name the spawn target (`tp-critic` w/ lens, `tp-explorer` w/ scope, `tp-researcher` w/ question). Skills whose work is inline (implementation, single-command verification, file edits in main context) do NOT need spawn instructions.
- [ ] **No-specialized-agent check**: Before adding a new specialized reviewer agent, ask "could this be a one-sentence lens passed to `tp-critic` instead?" If yes, do not add an agent file. The marketplace ships 6 named subagents; specialization lives in lens prompts.
- [ ] **Subagent contract check**: For any new or modified agent, the `tools:` field matches the operations stated in the contract body. 6 design principles (P1-P6) at `plugins/core-principled/skills/subagent-orchestration/references/subagent-contract-design.md` apply. Test with the 3-phase methodology (static read → real invocation → JSONL trace) per [knowledge/concepts/contributing.md](knowledge/concepts/contributing.md) — read it BEFORE authoring or modifying an agent.
- [ ] **Critique loop check**: Every skill that produces artifacts ends with "spawn `tp-critic` w/ lens Y, loop until no HIGH findings" or equivalent
- [ ] **Skill budget check**: Run `/context` and `/doctor` — verify no skills dropped or descriptions truncated. Calculate: hub (<500 tokens) + active domains (<2,000 each) + references/ (unlimited). If total loaded SKILL.md content approaches 10k, truncate or move to references/.
- [ ] **Description length check**: Combined `description` + `when_to_use` ≤1,536 chars; front-load trigger phrases in the first 200 chars
- [ ] **Tool field check**: Agent definitions use `tools:` (allowlist) ONLY when the restriction is the point (currently only `wiki-searcher`). Skills use `allowed-tools:` (pre-approval). Commands use `allowed-tools:` (pre-approval). Never confuse these semantics. Remember: `allowed-tools` in `.mcp.json` is IGNORED (confirmed bug) — use CLI flags or PreToolUse hooks for real restriction.
- [ ] **Routing mutual exclusivity check**: Each skill's description trigger set is mutually exclusive from all others. If two descriptions can be paraphrased to mean the same thing, they will misroute.
- [ ] **CONTRAST section check**: For any skill with adjacent-domain overlap, a CONTRAST section explicitly states what the skill does NOT cover.
- [ ] **Orchestration separation**: Skill body describes outcomes/roles; agent prompt describes execution only
- [ ] **No hardcoded drift targets**: Replace specific counts/versions with references or filesystem queries
- [ ] **Discovery over enumeration**: Use filesystem queries over reimplemented enumerations
- [ ] **MCP naming check**: If plugin exposes MCP servers, verify server names are namespaced as `taches-{domain}`, tool names are domain-specific verbs, and tool count per server is 5–15.
- [ ] **Cross-skill reference path check**: A SKILL.md or agent citing a sibling skill's `references/X.md` MUST prefix the path with the sibling skill name (e.g. `mcp-expertise/references/X.md`). Bare `references/X.md` only resolves within the containing skill. See [`.claude/rules/cross-skill-references.md`](.claude/rules/cross-skill-references.md).
- [ ] **Hub router budget check**: Hub SKILL.md body MUST be under 500 tokens (~30 lines). Mode bodies are one-paragraph descriptions + imperative reference citations. Procedural logic (multi-step workflows, conditional branches, pre-conditions) belongs in `references/`, not the hub. See [`.claude/rules/hub-router-budget.md`](.claude/rules/hub-router-budget.md).
- [ ] **context:fork blackbox check**: A SKILL.md with `context: fork` frontmatter MUST document its blackbox contract: output format in the first 200 chars of `description`, explicit role statement + output spec in the body, input/output examples when arguments are non-trivial, and `argument-hint` set if the skill expects structured input. The forked subagent has no main-conversation history — frontmatter + body are the only contract. See [`.claude/rules/context-fork-blackbox.md`](.claude/rules/context-fork-blackbox.md).
- [ ] **Cross-plugin citation check**: References to another plugin's pattern, file, or concept MUST cite by semantic role only (e.g. "a parallel-judge pattern", "a judge subagent"). NEVER name another plugin by identifier or cite its file paths. See [`.claude/rules/cross-plugin-citations.md`](.claude/rules/cross-plugin-citations.md).
- [ ] **Ground truth citation check**: An agent's "Ground truth" / "P6" section MUST contain the rule only — no issue numbers, PR numbers, file paths from a specific PR, contributor names, or dates. Volatile provenance belongs in commit messages and CHANGELOG. See [`.claude/rules/ground-truth-citations.md`](.claude/rules/ground-truth-citations.md).

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

### Skill Token Budgets — Hard Limits

Exceeding these limits causes **silent truncation** — the model loses the tail of skill instructions and invents its own behavior, no error is raised. This is the primary quality failure mode for fat skills.

| Budget | Limit | What happens when exceeded |
|--------|-------|----------------------------|
| Per-skill (spec ceiling) | <5,000 tokens | Response quality degrades; later instructions ignored |
| Per-skill (project ceiling) | <2,500 tokens | Empirically the safe operating limit |
| Total loaded SKILL.md content | ~10,000 tokens | Context pressure; earlier loaded skills truncated or ignored |
| Background task output | 30,000 chars | Output truncated, full log path returned |

In a typical session, **2–4 skills are loaded simultaneously**. With hub + 3 domain skills each at 3,000 tokens, you hit the 10k ceiling and silent truncation begins.

**Safe budget formula:**
```
hub SKILL.md:       <500 tokens  (pure router, no domain logic)
each domain SKILL.md: <2,000 tokens (core workflow + 2-3 examples)
domain references/:   unlimited    (loaded only when cited)
```

**The failure mode in practice:** Hub (4k) + Rust (3k) + Pharma (3k) = 10k. Claude loads all three. The Pharma skill's last 500 tokens are silently dropped. The model follows the Pharma skill's opening instructions but improvises the closing procedure — because the closing procedure was truncated, not because the model chose to ignore it.

**Dynamic grounding prevents hallucination.** Use ``!`command` `` injection at skill invocation time:
```
!`git diff HEAD`
!`cat config.json`
```
This grounds the skill in actual state rather than stale context.

### 500-Line Guideline — Budget, Not Hard Wall

The 500-line / 2,500-token recommendation is a **quality budget**, not a compiler error. The spec allows up to 5,000 tokens. The community consensus: beyond ~2,500 tokens, instruction-following drops measurably — the model remembers the opening persona and closing examples, but invents its own rules for the middle.

For hub skills with multiple modes, use the `Modes:` directive (see Hub-Spoke Architecture). The guideline applies to **individual modes**, not the total hub file. A hub with 5 modes at 80 lines each = 400 lines total, well within budget.

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
| [subagents.md](knowledge/raw/official/subagents.md) | Before creating agents |
| [skills.md](knowledge/raw/official/skills.md) | Before authoring skills |
| [hooks.md](knowledge/raw/official/hooks.md) | Before configuring hooks |
| [commands.md](knowledge/raw/official/commands.md) | Before creating commands |
| [permissions.md](knowledge/raw/official/permissions.md) | Before configuring permissions |
| [agent-types.md](knowledge/raw/official/agent-types.md) | Before choosing agent type |
| [agent-tool-params.md](knowledge/raw/official/agent-tool-params.md) | Before spawning subagents |
| [agent-skill-integration.md](knowledge/raw/official/agent-skill-integration.md) | Before adding skills to agents |
| [rules.md](knowledge/raw/official/rules.md) | Before writing rules or CLAUDE.md |
| [memory.md](knowledge/raw/official/memory.md) | Before configuring CLAUDE.md hierarchy or .claude/rules/ |

### Plugin References

| Doc | When to Read |
|-----|-------------|
| [plugins/creating.md](knowledge/raw/official/plugins/creating.md) | Before creating plugins |
| [plugins/marketplaces.md](knowledge/raw/official/plugins/marketplaces.md) | Before setting up marketplace |
| [plugins/plugin-submission.md](knowledge/raw/official/plugins/plugin-submission.md) | Before submitting a plugin to the official Anthropic directory |
| [plugins/plugins-reference.md](knowledge/raw/official/plugins/plugins-reference.md) | Before advanced plugin work |

### Concepts & Templates

These are maintainer-only methodology and template files. Cited where relevant in this document; also discoverable from this table.

| Doc | When to Read |
|-----|-------------|
| [SCHEMA.md](knowledge/SCHEMA.md) | Before adding or modifying any wiki-format page (frontmatter shape, tag taxonomy, page-size budget) |
| [knowledge-base-design.md](knowledge/concepts/knowledge-base-design.md) | Before adding, moving, or removing any `knowledge/` file |
| [contributing.md](knowledge/concepts/contributing.md) | Before modifying skills, subagents, hooks, or plugins (3-phase testing, 6 design principles, marketplace regeneration) |
| [intent-format.md](knowledge/concepts/intent-format.md) | Before representing user-task intent in a structured form |
| [llm-wiki-methodology.md](knowledge/concepts/llm-wiki-methodology.md) | Before authoring a wiki-methodology skill or applying LLM-as-wiki patterns |
| [persistence-schema.md](knowledge/concepts/persistence-schema.md) | Before designing cross-session persistence for any artifact |
| [changelog-entry.md](knowledge/templates/changelog-entry.md) | Before writing any CHANGELOG entry |
| [command.md](knowledge/templates/command.md) | Before authoring a new command |

### Refreshing Official Docs

```bash
curl -sL "https://code.claude.com/docs/en/<topic>.md" -o knowledge/raw/official/<topic>.md
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
| **Critique loop** | Pattern of spawning review subagents after artifact creation, iterating until no HIGH findings remain |
| **Skill budget** | Claude Code's 1% context limit for skill metadata; exceeded skills are silently dropped |
| **Front-load** | Placing trigger keywords at the start of descriptions so they survive truncation from the end |
| **CONTRAST section** | Explicit negative cases in descriptions to prevent false positive routing |
| **Under-triggering** | Claude's tendency to not invoke skills without explicit trigger phrases — primary routing failure mode |
| **Silent truncation** | Failure mode where skill content past the token budget is dropped without error; model invents behavior |
| **Modes: directive** | Top-of-body directive in hub skills listing distinct invocation contexts and their delegation targets |
| **Two-layer tool model** | Claude Code's Availability layer (tools: allowlist, bare disallowedTools) vs Permission layer (allowedTools, scoped disallowedTools) |
| **MCP naming convention** | `mcp__{server}__{tool}` format — Claude Code's internal implementation, not MCP protocol standard |

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