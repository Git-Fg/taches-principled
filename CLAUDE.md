# Taches Principled — Development Guide

**For maintainers only.** This file contains development practices and internal conventions for working on this repository. It is NOT loaded by Claude Code when this plugin is installed — it exists only in the source repository. A Claude instance that installs this plugin from the marketplace will never see this file.

Treat every section below as knowledge transfer from a human who worked on this codebase to future human maintainers. Claude Code instances that install the plugin learn from the plugin's skill descriptions, agent definitions, and command files — not from this guide.

When generic agents and specialized inline versions cover the same capability, prefer the generic agent. Specialized inline agents add value only when they teach Claude something the generic version cannot — different workflow, domain-specific judgment, or context that would require extensive re-prompting. If a specialized agent's body is the same as the generic equivalent with different names, delete it and use the generic one. The generic agent becomes the canonical version; domain-specific knowledge lives in the skill that invokes it, not in the agent itself.

An agent is not orphaned simply because it is not explicitly named — generic agents like self-review, self-critic, and code-reviewer are discovered through semantic routing, not citation. A skill that says "verify quality before delivery" semantically routes to self-review without naming it. The agent is the canonical resolution for that capability pattern. An agent is only orphaned when it has no semantic hook — no skill describes a capability it would resolve.

---

## Core Design Principle

Every artifact in this marketplace is consumed by a Claude Code instance that starts with zero context about this project — no prior conversation, no session history, no external knowledge of what the plugin does or why it exists. That instance is smart, autonomous, and non-deterministic. It will reason about what the plugin does from the descriptions it can read.

Design every skill, agent, and command as if the first thing that will happen is: Claude loads into a completely fresh session, reads only this plugin's files, and must decide what to do with it.

Ask: What will that instance understand from the skill descriptions alone? Which skill will it invoke for a given task? Does the routing make sense without external context? Does the description give enough trigger signal for the right skill to fire? Does the body teach judgment or just prescribe steps? Does the agent know its role without being told what other agents exist?

If the answer to any of these is "Claude would have to guess" — the artifact needs more signal. If it would make a reasonable choice — trust the model and stop adding instructions.

High trust means: write descriptions that route correctly, then stop. Don't add fallbacks, disclaimers, or routing logic for edge cases the model can handle. Let the model figure out the non-deterministic parts it excels at.

---

## Version Management

**Marketplace version** and **plugin version** are independent:

- **Plugin version** (`0.4.0`): Incremented for any content change to this plugin
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

Skill authoring is taught by the `create-skills` skill. See that skill for:
- **Skill categories**: Constraint/Guardrail, Orchestration, Domain Expertise, Quality Assurance, Creative Direction
- **Policy vs. Mechanism**: The unifying principle for skill design (official term: progressive disclosure)
- **Delta principle**: Only document what differs from default behavior
- **Skill anatomy**: Frontmatter and body structure
- **Anti-patterns**: What to avoid in skill design
- **Cross-skill references**: Never cite other skills' files with paths (e.g., `skills/create-plans/references/X.md`) — use natural language: "see the X.md file in the create-plans skill's references"
- **Decision router**: How to structure SKILL.md for strong reference steering
- **Description length**: Official cap is 1,536 combined description+when_to_use (raised April 2026); routing density ideal is ~200 chars for optimal trigger clarity
- **Command format**: See `commands-standard.md` for lightweight command standards (no markdown in body, 1-3 sentence outcome instruction, conditional skill hints)

---

## User Interaction

**Interact with users when gathering information or making decisions — not while executing a plan.**

When you need user input, ask clearly. Present options as clickable choices, not numbered lists or free-form prompts. Make it easy to say yes or no to a specific direction.

During execution, trust your judgment for anything the plan didn't explicitly decide. If you find yourself asking "should I do X or Y?" — check whether the plan already commits to one. If it does, proceed. If neither was decided and the choice is significant, stop and ask.

Use checkpoints when verification is genuinely needed — not as a checkpoint for every task. A checkpoint that requires the user to think is often a sign the plan needed more specificity upstream.

The goal is a smooth handoff between thinking and doing. Questions belong in the thinking phase. Once you're implementing, focus on building.

---

## Compositional Skill Pairs

The create/execute skill pairs (`create-plans`/`execute-plans`, `create-prompts`/`execute-prompts`) are compositional by design. `create-plans` creates a plan and explicitly invokes `execute-plans` to execute it.

This is not a violation of the self-contained principle — it's explicit compositional intent. The create skill must state that execution requires the execution partner skill.

---

## Hub-Spoke Skill Architecture

Skills can operate as **hubs** (orchestrate other skills) or **spokes** (do one thing). Hub-and-spoke enables consolidation without capability loss.

### The Hub-Spoke Principle

A hub skill uses decision routing to dispatch to spoke modes internally, rather than having separate skills. This differs from compositional pairs:

| Pattern | When to Use | Example |
|---------|-------------|---------|
| **Compositional pair** | Create/execute lifecycle — separation is load-bearing | `create-plans` / `execute-plans` |
| **Hub-and-spoke** | One capability with distinct modes — merge for routing coherence | `reflexion` (reflect/critique/memorize) |

**The test for hub-vs-compositional:** If two skills always invoke each other in sequence, they're compositional. If one skill has independent modes that each cover different situations, it's a hub.

### Exempt Skills (Do Not Merge)

These are foundational compositional pairs or serve distinct workflow stages:

- `create-plans` + `execute-plans` — project planning lifecycle, separation is intentional
- `create-prompts` + `execute-prompts` — prompt creation lifecycle, separation is intentional
- `plan-task` + `implement-task` — different scope (task refinement vs task execution)
- `ideation` + `add-task` — different workflow stages (exploration vs capture)
- Plugin-specific skills (`git-ship`, `fpf-propose`, `tdd`) — no meaningful overlap with other plugins

### Completed Consolidations

These skills were merged into hub skills using the hub-and-spoke pattern:

| Hub Skill | Skills Merged | Rationale |
|----------|---------------|-----------|
| `diagnose` | `analyse` + `analyse-problem` + `root-cause-tracing` | All do problem investigation; different methods (Five Whys, A3, call-stack) rather than different purposes |
| `refine` | `code-review` + `code-simplify` + `reflexion` (Reflect mode) | All do quality improvement; review vs transform vs self-critique are modes of "make better" |

### Decision Criteria: Merge or Keep Separate?

**Merge when:**
- Skills share the same purpose (not just similar words in descriptions)
- Skills use different frameworks/methods for the same domain
- Trigger phrases are <5 per skill and overlap in meaning
- The resulting hub has a clear decision router with distinct modes

**Keep separate when:**
- Skills serve different workflow stages (ideation vs add-task)
- Skills have distinct entry/exit contracts that other skills depend on
- Trigger density is high (5+ specific phrases) and routing is reliable
- Skills are compositional pairs (create/execute lifecycle)

### Target Skill Count

The routing quality breaking point is **22-28 skills**. Below 22, fat skill complexity dominates. Above 28, routing confusion accumulates.

**Current: 34 skills across all plugins → Target: 22-28 skills for the root plugin**

### Hub-Spoke Pattern in Existing Skills

The `reflexion` skill is the canonical hub-and-spoke template:
```
Three modes in one skill:
- REFLECT: Self-critique with severity scoring
- CRITIQUE: Multi-judge consensus review
- MEMORIZE: Learning capture into project memory
```

Use this pattern for other multi-mode skills. The mode router lives in the skill's Decision Router section.

---

## Plugin Path Portability

Skills must work whether installed as personal (`~/.claude/skills/`), project (`.claude/skills/`), or plugin (`~/.claude/plugins/cache/*/`).

**Rule:** In SKILL.md body and templates, use `{baseDir}` for all skill-internal paths:

| Type | Use | Example |
|------|-----|---------|
| Read/Grep tool references | `{baseDir}` | `Read({baseDir}/agents/critic.md)` |
| Bash tool / script execution | `${CLAUDE_SKILL_DIR}` | `python3 ${CLAUDE_SKILL_DIR}/scripts/validate.py` |
| Reference files (references/*.md) | Relative or natural language | "see plan-format.md in the create-plans skill" |

**Why:** `{baseDir}` is a prompt-injection variable resolved when the skill loads. `${CLAUDE_SKILL_DIR}` is an environment variable available to Bash tool at runtime. Plugin-installed skills have a known bug where relative paths resolve from CWD on first attempt — using both variables ensures portability.

**Never use:**
- Hard-coded paths like `skills/create-plans/agents/explorer.md`
- Paths pointing to other skills' internals (use natural language instead)

**Do NOT boundary concision:** In Do NOT boundaries, skill names are acceptable for brevity — but only when the boundary is self-contained and unambiguous:
- ✅ `DO NOT use when X — use sadd-execute instead` (concise, unambiguous)
- ❌ `DO NOT use when X — use sadd-execute or sadd-dispatch instead` (ambiguous — which one?)
- ❌ `sadd-execute` as the only reference in a boundary that doesn't explain what it does

The goal is disambiguation, not elimination of names. If a skill name alone is unambiguous, use it. If it needs explanation, describe the role.

---

## Token Economy

- **Commands over skills for on-demand loading** — skills consume context always; commands load when invoked
- **Specialized agents with narrow context** — broad-context agents hallucinate more
- **Setup-commands for persistent context** — write to CLAUDE.md rather than relying on skill loading
- **Token estimation** — every skill should know its approximate cost
- **500-line guideline** — official stance is under 500 lines for optimal performance; split into separate reference files via progressive disclosure if content exceeds this

---

## Documentation Sync

README.md lives in two places:
1. The plugin root (source of truth)
2. Any docs/ directory (for GitHub Pages or marketplace docs)

**When you update README:** Copy to all locations manually.

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
)"
```

---

## Before Any Commit — Self-Check

- [ ] README updated if structure changed
- [ ] CHANGELOG entry added
- [ ] No MCP references (plugin is MCP-free)
- [ ] No broken cross-references between skills (never use file paths to other skills' references/agents/workflows — use natural language like "see the plan-format.md file in the create-plans skill")
- [ ] User interaction uses clear, structured options
- [ ] Command files conform to commands-standard.md (no method prescription, 1-3 sentence outcome instruction, no markdown in body)

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

| Current | Correct |
|---------|---------|
| "dispatch a sub-agent" | "spawn a [role] subagent" |
| "launch an agent" | "spawn a [role] subagent" |
| "spawn critic" | "spawn a critic subagent" |
| "spawn workers" | "spawn worker subagents" |

**Why "spawn" over "dispatch/launch":**
- "Spawn" is the canonical verb for subagent creation in Claude Code
- "dispatch" and "launch" are acceptable but inconsistent across the ecosystem
- Always pair with role name: "spawn a researcher subagent", "spawn a critic subagent"

**When citing subagents in natural language:**
- ✅ "spawn a critic subagent" — explicit spawn verb + role
- ✅ "The explorer subagent handles..." — role-based reference
- ❌ "spawn critic" — missing "subagent" designation
- ❌ "launch an agent" — vague, no role designation

**Role naming convention:** Use kebab-case for multi-word roles: "code-reviewer subagent", "meta-judge subagent", "verification subagent".

**Plugin-level agents** are stored in `plugins/taches-principled/agents/` and are auto-discovered system-wide. They appear in the `/agents` interface and Claude can invoke them automatically based on task context. When spawning these, describe the role: "spawn a reviewer subagent for code", "spawn a critic subagent for plans", "spawn a grader subagent for skills". The agent files are discoverable by description — no need to reference filenames.

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
3. **Use a general-purpose subagent with Write tool** — Haiku Explore subagents are read-only and cannot write findings; an agent that can read files, write findings, search content, and run shell commands is needed for investigation work
4. **Read** scratch notes AFTER subagents return, BEFORE synthesizing

**Guidance, not rigidity:** The goal is preventing the telephone game — information degrading as it passes through multiple agents. Writing findings to a shared artifact (rather than relying on subagent output alone) keeps the chain intact. The scratch area location is `.principled/scratch/` — use descriptive topic filenames.

---

## Evaluation Pipeline

taches-principled has a multi-agent evaluation system for skill quality assurance. Four specialized agents handle the pipeline: **Grader** scores teaching effectiveness, **Comparator** analyzes version deltas, **Skill Auditor** reviews format and frontmatter, and **Analyzer** synthesizes into 3 prioritized changes. All four are available as auto-discovered plugin-level agents.

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
│   └── rules/                    # Always-active guardrails
└── {tp-sadd,tp-fpf,tp-git,tp-tdd,tp-ddd}/  # Marketplace plugins
    ├── .claude-plugin/plugin.json
    ├── skills/{name}/SKILL.md
    ├── agents/
    └── rules/
```

### Naming Convention

All imported/ported plugins use the `tp-` prefix: `tp-sadd`, `tp-fpf`, `tp-git`, `tp-tdd`, `tp-ddd`.

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

## Meta-Rule (applies to this file only)

**Governs itself — all revisions must remain:**
- **Concise** — Minimum text for correct autonomous dispatch; no explanation, no prose ornamentation.
- **Non-interactive** — No user-input dependency; describes only what Claude Code executes without prompting.
- **Self-contained** — A cold-start instance must dispatch correctly from this file alone (skill priority, hook timing, rule merge order, subagent spawn mode).

---

## References

- [Claude Code Skills Documentation](https://code.claude.com/docs/en/skills)
- [Claude Code Subagents Documentation](https://code.claude.com/docs/en/sub-agents)
- [Claude Code Plugin Creation Guide](https://code.claude.com/docs/en/plugins)
- [Claude Code Plugin Marketplaces Documentation](https://code.claude.com/docs/en/plugin-marketplaces)
- [Claude Code Hooks Reference](https://code.claude.com/docs/en/hooks)
- [Claude Code Commands Reference](https://code.claude.com/docs/en/commands)
- [Plugin Submission Guide](https://claude.com/docs/plugins/submit)
- [context-engineering-kit](https://github.com/NeoLabHQ/context-engineering-kit) — inspiration source

**Official documentation** is cached locally in `references/official/` for offline access and consistency across team members.