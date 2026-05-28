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

### Skill Discovery Optimization

**Claude under-triggers skills.** Research shows the model naturally under-invokes without explicit trigger phrases. This is the primary failure mode — not routing logic errors.

**Reliable triggering requires:**
- **User vocabulary in frontmatter**: "find the root cause" beats "A3 analysis" — speak how users think
- **Specific phrases**: 5-10 triggers, no generic words ("improve" matches everything)
- **CONTRAST sections**: Overlapping domains need explicit disambiguation
- **Front-load in first 200 chars**: Truncation happens from the end

**What kills routing:**
- Technical jargon in description/when_to_use ("fishbone", "CQRS", "ADI")
- Single ambiguous words ("fix", "do", "handle")
- Vague descriptions matching everything
- Missing negative cases (what NOT to match)

**Frontmatter vs Body — The Clear Distinction:**

| Layer | Purpose | Language |
|-------|---------|----------|
| **description** | Routing signal — triggers skill loading | User vocabulary only |
| **when_to_use** | Additional triggers | User vocabulary only |
| **Body** | Teaching methodology | Technical precision OK |

**Example (tp-fpf):**
- **Description:** "Generate and evaluate competing hypotheses" (user vocabulary)
- **Body:** "Execute complete FPF cycle with ADI (Abduction-Deduction-Induction)" (technical)

This separation is intentional: frontmatter must match user vocabulary for routing; body teaches domain experts with precise terminology after the skill loads. Never remove technical terms from the body — only from description and when_to_use.

**Validation (before shipping any skill):**
```bash
claude -p "<test-query>" --output-format stream-json 2>&1 | grep Skill
```
Test 15-20 real queries, hold out 20%. Overfit = description learned pattern-matching, not routing.

**Hook limitations:** Hooks inject context that nudges reasoning — they cannot directly activate skills. No hook event directly loads a skill. Skill activation is description-matching only.

### No Inline Tool Lists in Subagent Instructions

When a skill body describes spawning a subagent, never include a specific tool list (`tools: Read, Edit, Bash, WebSearch, Write`). Tool availability varies by environment — WebSearch may be an MCP server, Bash may be restricted, file paths differ per platform.

**Instead:** Describe the role and outcome. Let the agent definition in `agents/` or the default toolset handle tool configuration.

| ❌ Incorrect (inline tool list) | ✅ Correct (role + outcome) |
|--------------------------------|---------------------------|
| "Spawn a subagent (Haiku, tools: Read, Write, Grep, Glob, Bash) to scan the project" | "Spawn an explorer subagent to map project structure and report findings" |
| "Spawn a researcher (Sonnet, WebSearch, Read, Write) to search for patterns" | "Spawn a researcher subagent to investigate patterns and persist findings" |
| "Spawn a critic (Haiku, Read, Grep, Write) to review completeness" | "Spawn a critic subagent to review the work for gaps and inconsistencies" |

**Why:** Agent definitions in `plugins/taches-principled/agents/` already configure tools per role. Inline lists duplicate this, break when tools change or are unavailable, and force subagent dispatchers to know tool names they shouldn't need to care about.

### Orchestration Topology: Where Skills End and Agents Begin

**Skills** teach WHAT to decide: routing triggers, delegation boundaries, when to stop and ask.

**Agents** teach HOW to execute: verification protocols, reporting formats, artifact delivery standards.

This asymmetry is load-bearing:
- **Skills** reference agents by role (e.g., "spawn a critic subagent"). The main agent reads the agent file and uses its content as the system prompt for the spawned subagent.
- **Agents** are self-contained execution templates. Never spawn subagents from an agent prompt.

**The pattern:** When a skill says "spawn a [role] subagent", the main agent:
1. Reads `{baseDir}/agents/[role].md`
2. Uses the markdown body (after frontmatter) as the subagent's system prompt
3. Fills in placeholders (`{{context}}`, `{{task}}`, `{{scope}}`) with task-specific details

**The test:** "Is this describing WHAT to do or HOW to do it?" — Orchestration = skill. Execution details = agent prompt.

### Agent Description Pattern

Agent descriptions inject into Claude's system prompt for routing, but **agents cannot self-invoke** — skills explicitly spawn them via "spawn a [role] subagent". However, improved descriptions make the spawn intent explicit and self-documenting.

**Recommended structure:**
```yaml
description: |
  ACTIVATES: [explicit trigger condition — when to invoke]
  LOOP: [termination criterion — usually "until no HIGH findings"]
  Output: [what the agent produces]
```

**Examples:**

| Agent | ACTIVATES | LOOP | Output |
|-------|-----------|------|--------|
| `self-review` | after any artifact creation | until no HIGH findings | severity-ranked findings |
| `self-critic` | after any artifact creation | until no HIGH findings | real-world impact assessment |
| `critic` | after every 2-3 tasks or phase boundary | until no HIGH (blocker) | blocker/warning/suggestion |
| `grader` | after any skill modification | once per evaluation | grade out of 10 + top change |

**Why this matters:**
- Frontmatter is parsed for semantic routing
- Loop invariants make activation conditions explicit
- Skills that spawn agents match by role, not description — but humans reading agent files understand intent
- The pattern future-proofs for potential agent self-invocation if routing improves

### Artifact Taxonomy

Four distinct artifacts with different loading behaviors and token costs:

| Artifact | Loading | Token Cost | Use Case |
|----------|---------|------------|----------|
| **Command** | User-invoked with `/name` | Zero until used | Trigger accelerators |
| **Skill** | Auto-loaded into context | Always present | Method teaching, routing |
| **Agent** | Fresh Claude instance per spawn | Per-spawn | Parallel execution, independent context |
| **Workflow Command** | Orchestrates agents via filesystem prompts | Per-spawn + coordination | Complex multi-phase workflows |

**Key insight:** Commands preferred over skills for token efficiency — skills populate context every session, commands only load when invoked.

---

## Version Management

**Marketplace version** and **plugin version** are independent:

- **Plugin version**: Incremented for any content change to this plugin (see `plugins/taches-principled/.claude-plugin/plugin.json` for current version)
- **Marketplace version** (`.claude-plugin/marketplace.json`): Incremented when releasing a collective update across all plugins

**Update sequence:**
```bash
# 1. Make your changes
git add -A && git commit -m "message"

# 2. Bump plugin version (minor for features, patch for fixes)
# Edit plugins/taches-principled/.claude-plugin/plugin.json — bump "version" field

# 3. Push
git push
```

---

## Skill Authoring

Skills are auto-invoked by default by Claude Code — a cold-start instance discovers and routes to them based on description matching, not prior conversation. Skill authoring is taught by the `create-skills` skill. See that skill for:
- **Skill categories**: Constraint/Guardrail, Orchestration, Domain Expertise, Quality Assurance, Creative Direction
- **Policy vs. Mechanism**: The unifying principle for skill design — declare intent before implementation. Policy is *what* the skill decides (trigger scope, routing, boundaries); mechanism is *how* the skill executes (tools, steps, details)
- **Progressive disclosure**: The loading pattern that shows policy upfront and mechanism on demand (frontmatter → body → references); the official tactic for staying under the 500-line guideline
- **Delta principle**: Only document what differs from default behavior
- **Skill anatomy**: Frontmatter and body structure
- **Anti-patterns**: What to avoid in skill design
- **Cross-skill references**: Never cite other skills' files with paths — use natural language: "see the X.md file in the create-plans skill's references"
- **Shared references anti-pattern**: Don't create `references/` files expecting cross-skill reuse — paths break on plugin install, content must be inlined or documented here
- **Decision router**: How to structure SKILL.md for strong reference steering
- **Description length**: Official cap is 1,536 combined description+when_to_use; routing density ideal is ~200 chars. `description` names the trigger phrase; `when_to_use` adds scope boundaries. Full routing optimization guide in "Skill Discovery Optimization" section.
- **Congruence Level (CL)**: Evidence validation for claims about techniques — CL3 (benchmark on identical hardware/OS/software), CL2 (similar but not identical), CL1 (general principle from blog post). Apply congruence penalty when evidence comes from mismatched contexts.
- **Command format**: See `commands-standard.md` in `plugins/taches-principled/` for lightweight command standards (no markdown in body, 1-3 sentence outcome instruction, conditional skill hints)

**How to access:** The `create-skills` skill is auto-discovered. Use `/create-skills` or invoke via the Skill tool.

---

## Commands

Commands are trigger accelerators, not method carriers. Their value is in the first three words Claude hears when a user invokes them — not in the body content.

**Both commands and skills are auto-invoked by default.** A cold-start Claude instance discovers and invokes them based on their descriptions — no prior conversation, no session history. Commands and skills with the same name: the skill takes precedence. Commands without a matching skill are still usable as standalone triggers.

**Never evaluate a command by comparing its body to the skill's body.** Structural overlap analysis is insufficient. A command that seems redundant may be teaching the trigger while the skill teaches the method.

**What commands do:**
- Teach Claude what mental frame to reach for when a user types `/something`
- Provide a memorable trigger phrase shorter than the skill description
- Add semantic framing the skill can't provide without being bloated

**What commands don't need to do:**
- Carry unique logic the skill doesn't have
- Restate the skill's methodology in fewer words
- Add information the skill already teaches

**Important — "outcome not method" reconciled:** The "tell the outcome, not the method" rule means don't restate the *skill's internal methodology* (e.g., "apply A3 problem-solving with five whys and fishbone diagram"). It does NOT mean avoid naming native capabilities. "Fan out subagents", "create a task list", "use web search" are direct capability names that tell Claude WHAT to do — they are the outcome. Contrast with skill methodology: "use diagnose's A3 mode with severity scoring" — that's method. Commands name what, skills teach how.

**Example:** `/debug` teaches "when you see a bug, think root cause first." The `diagnose` skill's decision router covers five investigation modes (A3, Five Whys, Fishbone, Stack Trace, Auto). The command doesn't need to repeat that — it just needs to make Claude reach for the right skill with the right mindset.

**Anti-pattern:** Evaluating commands by word-for-word overlap with the skill body. This misses the semantic framing value. A command that says "Find the root cause and verify the fix" teaches a different trigger than a skill description that starts "Apply systematic debugging methodology."

**When a command IS hollow:** It adds nothing to the trigger — not the framing, not the mindset, not the prioritization. If the command body could be replaced with `$ARGUMENTS` and nothing would be lost, it's hollow. But `$ARGUMENTS` alone is a valid command if the description provides the trigger.

**Direct language principle:** Command bodies must name native capabilities explicitly, not describe them indirectly. Use direct keywords the model routes to immediately — "fan out subagents", "create a task list", "use web search", "spawn a critic subagent", "capture output to a file". Direct language = immediate routing = zero context drift.

**Why:** Every instance of indirect language for a native capability adds interpretation overhead. "Divide into independent streams" requires the model to recognize this means subagent fan-out. "Maintain a visible record of progress" requires inference to reach "create a task list". "Consult external references" requires deduction to land on "use web search". That overhead is context drift — tokens spent on semantic disambiguation that could be spent on execution. One sentence of direct language routes to the right behavior in a single pass. One sentence of vague semantics fragments across 3-5 possible interpretations, each consuming model capacity without advancing the goal.

**The balance with skills:**
- **Commands** name native capabilities directly — WHAT to do
- **Skills** teach method and judgment — HOW to do it
- **Command descriptions (frontmatter)** route to skills — WHICH skill to load
- Command bodies never cite skill names or skill methodology. They only state the outcome using the native vocabulary the model already understands.

**Good vs bad examples:**

| Instead of this (vague) | Use this (direct) | Why |
|--------------------------|--------------------|-----|
| "Divide into independent streams of work" | "Fan out subagents to explore in parallel" | "Fan out subagents" maps immediately to subagent spawn. The vague version drifts through 5 syntactic parses. |
| "Maintain a visible record of progress" | "Create a task list tracking all items" | Indirect language requires inference. |
| "Consult external references for up-to-date information" | "Use web search to verify current state" | "Use web search" routes to the search tool. The vague version sounds like reading local docs. |
| "Organize your approach and track what needs doing" | "Create a task list for each step, then fan out subagents" | Both native capacities named explicitly. No inference needed. |

**What direct language prevents:**
- **Ambiguous tool routing:** "Consult external references" could mean web search, local docs, MCP resources, or skill references. "Use web search" is unambiguous.
- **Paraphrase decay:** Vague phrasing gets re-paraphrased at every turn, drifting further from the intended action. Direct keywords can't decay — they route identically every time.
- **Skill bleed:** When a command body sounds like a skill, the model loads both skill and command context for the same trigger. Direct language keeps the command lightweight and the skill focused.

**The test:** Read the command body. Can the model act on it without interpreting any phrase? If a phrase could mean two different actions, replace it with the specific native capability name.

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

When gathering context before proceeding, use the interview pattern — not a fixed formula. The goal is to understand intent, clarify scope, and set execution expectations.

**The canonical invocation:** Use your tool to ask users your questions and prefill answers.

**What to achieve (not how many questions):**
1. Understand the goal — what does the user want to accomplish
2. Clarify scope — boundaries, constraints, priorities
3. Set execution mode — autonomous or human-in-the-loop

**When to run an interview:**
- Beginning of a creation workflow (create-plans, create-prompts, ideation)
- Beginning of an execution workflow when invoked directly (execute-plans, execute-prompts)
- When task input is empty or vague (add-task)
- At any decision point where user input is genuinely needed

**When to skip an interview:**
- Context already exists (handoff file, existing artifacts)
- Input is already specific and complete
- User explicitly specified execution mode via flags

**Generalist guidance for skills:**

```
Before proceeding, ensure you have sufficient context:
1. Understand the goal
2. Clarify scope
3. Set execution mode

Use your tool to ask users your questions and prefill answers. See "User Interaction" section for the canonical invocation phrase and exception — descriptive constraints.
```

The phrasing varies per skill. See individual skill files for exact wording.

---

## Hub-Spoke Skill Architecture

Skills can operate as **hubs** (orchestrate other skills) or **spokes** (do one thing). Hub-and-spoke enables consolidation without capability loss.

### The Hub-Spoke Principle

A hub skill uses decision routing to dispatch to spoke modes internally, rather than having separate skills. This differs from compositional pairs:

| Pattern | When to Use | Example |
|---------|-------------|---------|
| **Compositional pair** | Create/execute lifecycle — separation is load-bearing | `create-plans` / `execute-plans` |
| **Hub-and-spoke** | One capability with distinct modes — merge for routing coherence | `refine` (simplify/review/critique/memorize/polish) |

**The test for hub-vs-compositional:** If one skill explicitly invokes another as its execution partner (one direction, not mutual), they're a compositional pair. If one skill has independent modes that each cover different situations, it's a hub.

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

Skills must work whether installed as personal (`~/.claude/skills/`), project (`.claude/skills/`), or plugin (`~/.claude/plugins/cache/*/`).

**Rule:** Every file reference within a skill's own directory must use a `{baseDir}` path. Never describe a file's location in vague natural language — state its path exactly.

| Reference type | Syntax | Example |
|---------------|--------|---------|
| Skill-internal file (agents/, references/, templates/, scripts/) | `{baseDir}/folder/file.md` | `{baseDir}/agents/critic.md` |
| Bash-executed script | `${CLAUDE_SKILL_DIR}` | `python3 ${CLAUDE_SKILL_DIR}/scripts/validate.py` |
| Cross-skill reference (another skill's file) | Natural language naming the skill | "see plan-format.md in the create-plans skill" |

**Why `{baseDir}` in natural language, not just in Read calls:** The instruction "read the critic agent template from the agents folder" forces the AI to guess which file is meant. `{baseDir}/agents/critic.md` is unambiguous — one file, one path, zero ambiguity. The variable resolves when the skill loads regardless of install location.

**Wrong vs right for skill-internal files:**

```
❌ "read the execution-strategies reference file"
❌ "read the critic agent template from the agents folder"
✅ "{baseDir}/references/execution-strategies.md"
✅ "{baseDir}/agents/critic.md"
```

**Never use:**
- Hard-coded paths like `skills/create-plans/agents/explorer.md`
- Vague descriptions like "the agents folder" or "the reference file" when a specific file is meant
- Paths pointing to other skills' internals (use natural language naming the skill)

**Do NOT boundary concision:** In Do NOT boundaries, skill names are acceptable for brevity — but only when the boundary is self-contained and unambiguous:
- ✅ `DO NOT use when X — use sadd instead` (concise, unambiguous)
- ❌ `DO NOT use when X — use sadd or execute instead` (ambiguous — which mode?)

The goal is disambiguation, not elimination of names. If a skill name alone is unambiguous, use it. If it needs explanation, describe the role.

### References/ Lazy Loading

References/ folders are **lazy-loaded only when explicitly named in skill body**. They are NOT auto-discovered or auto-loaded.

**Cross-skill vs skill-internal references:**

| Type | Syntax | Example |
|------|--------|---------|
| **Cross-skill** | Natural language naming the skill | "see format-guide.md in the create-plans skill" |
| **Skill-internal** | `{baseDir}/path/to/file.md` | `{baseDir}/references/my-ref.md` |

Do NOT wrap the path in a Read() call — just state the path. `{baseDir}` resolves when the skill loads regardless of install location, so `{baseDir}/references/my-ref.md` is a portable, unambiguous file reference.

**Rule:** Each skill owns its `references/` folder — do not expect cross-skill reuse. If multiple skills need the same content, inline it or document the pattern here. Never create shared references/ folders expecting other skills to reference them by path.

**Migration:** To migrate existing cross-skill references: (1) search for `references/` in SKILL.md bodies, (2) inline the content or replace path with natural language reference to the skill name.

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

- [ ] README updated if structure changed
- [ ] CHANGELOG entry added
- [ ] No MCP runtime dependencies (documentation references to MCP concepts are acceptable; plugin must not require MCP servers at runtime)
- [ ] No broken cross-references between skills (never use file paths to other skills' references/agents/workflows — use natural language naming the skill)
- [ ] No shared references/ folders expecting cross-skill reuse (inline content instead — references/ only loads when explicitly named in parent SKILL.md)
- [ ] Skill-internal file references use `{baseDir}/path/to/file.md` syntax (no vague "from the agents folder", no Read() wrappers, no hardcoded paths like `skills/create-plans/...`)
- [ ] No inline tool lists in subagent spawn instructions (describe role + outcome, never `tools: Read, Edit, Bash`)
- [ ] User interaction uses clear, structured options
- [ ] Command files conform to commands-standard.md in `plugins/taches-principled/` (no method prescription, 1-3 sentence outcome instruction, no markdown in body)
  - [Current commands](plugins/taches-principled/commands/): all slash command files in that directory
- [ ] README synced to all docs/ locations if marketplace docs are present
- [ ] Skill changes backed by eval evidence (tested against real routing scenarios, not hypothetical)
- [ ] Skill changes describe actual problems encountered (not theoretical improvements)

### Skill Quality Gate

- [ ] **Orchestration separation:** Skill body describes outcomes/roles; agent prompt describes execution only. If you see "spawn" or "orchestrate" in an agent body, move it to the calling skill.
- [ ] **No hardcoded drift targets:** Avoid specific counts or versions in prose. Replace with references: "run `find plugins -name SKILL.md | wc -l` for accurate count."
- [ ] **Discovery over enumeration:** Don't enumerate what could be queried from filesystem. The filesystem is ground truth — don't reimplement it in prose.

For skill-authoring self-check, see `create-skills` skill.

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

## Subagent Spawn Pattern

When referencing subagent spawning in skills, use the canonical form: **"spawn a [role] subagent"**.

**Agent file pattern:** When a skill says "spawn a [role] subagent", the main agent:
1. Reads the agent file from `{baseDir}/agents/[role].md` (or plugin-level `agents/[role].md`)
2. Uses the markdown body as the subagent's system prompt
3. Fills in task-specific placeholders (`{{context}}`, `{{task}}`, `{{scope}}`)

**Cost model:** Subagents should default to Haiku (fast, cheap) for exploration, research, implementation, verification, and critique. Reserve Sonnet/Opus for the main orchestrator's reasoning and judgment calls, and for complex subagent tasks requiring deep reasoning.

| Current | Correct |
|---------|---------|
| "dispatch a sub-agent" | "spawn a [role] subagent" |
| "launch an agent" | "spawn a [role] subagent" |
| "spawn critic" | "spawn a critic subagent" |
| "spawn workers" | "spawn worker subagents" |

**Why "spawn" over "dispatch/launch":**
- "Spawn" is the canonical verb for subagent creation in Claude Code
- "dispatch" and "launch" are non-canonical — avoid them in new skill documentation; existing uses are tolerable but should be migrated over time
- Always pair with role name: "spawn a researcher subagent", "spawn a critic subagent"

**When citing subagents in natural language:**
- ✅ "spawn a critic subagent" — explicit spawn verb + role
- ✅ "The explorer subagent handles..." — role-based reference
- ❌ "spawn critic" — missing "subagent" designation
- ❌ "launch an agent" — vague, no role designation

**Role naming convention:** Use kebab-case for multi-word roles: "code-reviewer subagent", "meta-judge subagent", "verification subagent".

**Plugin-level agents** are stored in `plugins/taches-principled/agents/` and are auto-discovered system-wide. They appear in the `/agents` interface and Claude can invoke them automatically based on task context. When spawning these, describe the role: "spawn a reviewer subagent for code", "spawn a critic subagent for plans", "spawn a grader subagent for skills". The agent files are discoverable by description — no need to reference filenames.

**Skills pre-loading:** Plugin-level agents carrying a `skills:` field preload the named skill's full SKILL.md body into context at startup. This eliminates duplicated methodology in spawn prompts. Use when the agent's role maps to a skill's methodology — the agent should carry the framework it evaluates against. Agent files are authoritative for their mappings; no need to enumerate them here.

**Skill-internal agents** are stored in skill-specific `agents/` folders (e.g., `create-plans/agents/`, `execute-plans/agents/`). These are **prompt templates**, not auto-invoked subagents. They are workflow-specific and only available when that skill is loaded. To use one: read the agent file, then use its content as the basis for spawning a general-purpose subagent with your task context.

**Examples:**

*Plugin-level (auto-discovered):*
> "spawn a code-reviewer subagent" — the agent file is in `plugins/taches-principled/agents/`, available system-wide

*Skill-internal (prompt template):*
> Read the critic agent at `{baseDir}/agents/critic.md`, then spawn a general-purpose subagent using that structure to review the implementation

> Read the explorer agent at `{baseDir}/agents/explorer.md`, then use that agent's system prompt — adapted with your task context — as the prompt when spawning a general-purpose subagent

---

## Explorer Subagent Protocol

When spawning subagents for exploration/investigation, the orchestrator should:

1. **Read** any existing scratch notes BEFORE spawning — avoid redundant work
2. **Write** current context and questions to the scratch area — preserve institutional memory
3. **Use a general-purpose subagent with Write tool** — the built-in Explore subagent type is read-only and cannot write findings; an agent that can read files, write findings, search content, and run shell commands is needed for investigation work
4. **Read** scratch notes AFTER subagents return, BEFORE synthesizing

**Guidance, not rigidity:** The goal is preventing the telephone game — information degrading as it passes through multiple agents. Writing findings to a shared artifact (rather than relying on subagent output alone) keeps the chain intact. The scratch area location is `.principled/scratch/` — use descriptive topic filenames.

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

This repository serves as both a **single plugin** (taches-principled) and a **marketplace** hosting multiple plugins under `plugins/`.

### Directory Structure

```
plugins/
├── taches-principled/              # Root plugin (skills, agents, commands, rules)
│   ├── .claude-plugin/plugin.json # Plugin manifest (name, version, author)
│   ├── skills/{name}/SKILL.md     # One directory per skill
│   ├── agents/                    # Bundled subagent definitions
│   ├── commands/                  # Slash commands
│   └── rules/                    # Guardrails (placeholder — currently empty)
├── references/
│   └── official/                  # Cached Claude Code docs for offline access
└── tp-*/  # Marketplace plugins (see marketplace.json for current list)
    ├── .claude-plugin/plugin.json
    ├── skills/{name}/SKILL.md
    ├── agents/
    └── rules/
```

### Naming Convention

All imported/ported plugins use the `tp-` prefix. Current marketplace plugins are listed in `.claude-plugin/marketplace.json`. Each plugin is self-contained with its own `skills/`, `agents/`, and `commands/` directories.

### Adding a New Plugin

1. Create `plugins/{name}/.claude-plugin/plugin.json` with version `0.1.0`
2. Create `plugins/{name}/skills/{skill-name}/` directories
3. Write SKILL.md files following the decision router + policy/mechanism patterns used by existing skills
4. Add plugin entry to `.claude-plugin/marketplace.json`
5. Bump marketplace version

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

**Skills** are triggers, not recipes — describe what to accomplish and when, not step-by-step procedure. **Agents** are system prompts, not scripts — one coherent paragraph, no numbered steps, no output format templates, no JSON schemas. **Commands** are lightweight pointers — no markdown body, no structural decomposition, 1-3 sentences of outcome, conditional hints for skills/subagents/web search when useful.

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

---

## Meta-Rule (applies to this file only)

**Governs itself — all revisions must remain:**
- **Accurate** — Reflects current project state; outdated sections removed, not annotated.
- **Actionable** — Every section answers "what do I do?" not just "what exists?"
- **Self-contained** — A new maintainer can understand the project from this file alone.

---

## References

- [Claude Code Skills Documentation](https://code.claude.com/docs/en/skills)
- [Claude Code Subagents Documentation](https://code.claude.com/docs/en/sub-agents)
- [Claude Code Plugin Creation Guide](https://code.claude.com/docs/en/plugins)
- [Claude Code Plugin Marketplaces Documentation](https://code.claude.com/docs/en/plugin-marketplaces)
- [Claude Code Hooks Reference](https://code.claude.com/docs/en/hooks)
- [Claude Code Commands Reference](https://code.claude.com/docs/en/commands)
- [Plugin Submission Guide](https://claude.com/docs/plugins/submit)
- [context-engineering-kit](https://github.com/NeoLabHQ/context-engineering-kit) — foundational influence on the token economy model and subagent orchestration patterns

**Official documentation** is cached locally in `references/official/` for offline access and consistency across team members.