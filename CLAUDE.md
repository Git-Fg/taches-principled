# Taches Principled — Development Guide

Development practices for maintaining this plugin. These are operational rules, not suggestions.

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

### Consolidation Candidates

When skills fragment a single capability across incompatible frameworks, merge into a hub with mode routing:

| Merge Into | Skills Combined | Rationale |
|------------|-----------------|-----------|
| `diagnose` | `analyse` + `analyse-problem` + `root-cause-tracing` | All do problem investigation; different methods (Five Whys, A3, call-stack) rather than different purposes |
| `refine` | `code-review` + `code-simplify` + `reflexion` (Reflect mode) | All do quality improvement; review vs transform vs self-critique are modes of "make better" |
| `judge` | `sadd-judge` (absorbed judge-with-debate) | Single vs consensus evaluation are modes of quality assessment |

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

**Current: 31 skills → Target: 22-28 skills**

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

```bash
# Create feature branch
git checkout -b feature/my-improvement

# Make changes, commit
git add -A && git commit -m "type: description"

# Push and create PR
git push -u origin feature/my-improvement
gh pr create --title "feat: description" --body "$(cat <<'EOF'
## Summary
- What changed
- Why it changed

## Test plan
- [ ] Tested locally
- [ ] Skill triggers correctly
- [ ] No regressions in existing skills
EOF
)"
```

---

## Before Any Commit — Self-Check

- [ ] README updated if structure changed
- [ ] CHANGELOG entry added
- [ ] No MCP references (plugin is MCP-free)
- [ ] No broken cross-references between skills (never use file paths to other skills' references/agents/workflows — use natural language like "see the plan-format.md file in the create-plans skill")
- [ ] User interaction uses clear, structured options

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

**Plugin-level agents** are stored in `plugins/taches-principled/agents/` and are auto-discovered system-wide. They appear in the `/agents` interface and Claude can invoke them automatically based on task context. When spawning these, use their documented role name:

| Agent File | Spawn Example |
|------------|---------------|
| `code-reviewer.md` | "spawn a code-reviewer subagent" |
| `grader.md` | "spawn a grader subagent" |
| `skill-auditor.md` | "spawn a skill-auditor subagent" |
| `subagent-auditor.md` | "spawn a subagent-auditor subagent" |
| `comparator.md` | "spawn a comparator subagent" |
| `analyzer.md` | "spawn an analyzer subagent" |
| `prompt-engineer.md` | "spawn a prompt-engineer subagent" |

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

taches-principled has a multi-agent evaluation system for skill quality assurance:

### The Four Evaluation Agents

The evaluation pipeline uses four specialized agents. The **Grader** measures teaching effectiveness — not format compliance — scoring routing signal density, delta clarity, teaching posture, and anti-pattern quality. The **Comparator** analyzes what changed between skill versions and assesses teaching impact. The **Skill Auditor** reviews quality signals, format, and frontmatter, producing severity-ranked findings. The **Analyzer** synthesizes all input into a maximum of three prioritized changes with explicit teaching outcomes.

### The Evaluation Pipeline

```
Skill Author creates/changes a skill
    ↓
[Grader] → Dimension scores (what to improve)
    ↓
[Comparator] → Delta analysis (what changed between versions)
    ↓
[Skill Auditor] → Quality signals (format, structure, frontmatter)
    ↓
[Two-Claude Ad-hoc Test] → Evaluation-driven routing verification
    ↓
[Analyzer] → 3 prioritized changes with teaching outcomes
    ↓
Skill Improved
```

### Invoking the Pipeline

**Note:** The evaluation pipeline is **aspirational** — an intended design documented here for reference. The agent definitions (grader, comparator, skill-auditor, analyzer) exist as reference implementations in `plugins/taches-principled/agents/`, but no skill currently orchestrates the full pipeline. The pipeline serves as a design template if a future skill-audit skill is created.

**Quick audit** (format + quality only): Read the skill-auditor agent definition at `plugins/taches-principled/agents/skill-auditor.md` and use it as a subagent prompt following the pattern:

```markdown
Agent(description = "Audit [skill] for quality",
      prompt = "Read [path]/SKILL.md and audit following skill-auditor.md.")
```

**Full evaluation** (teaching + routing + format): To build the pipeline manually:
1. Grader: Grade for teaching effectiveness — use `grader.md` as subagent prompt
2. Comparator: Compare versions if applicable — use `comparator.md` as subagent prompt
3. Skill Auditor: Audit for quality signals — use `skill-auditor.md` as subagent prompt
4. Two-Claude Ad-hoc Test: Run evaluation-driven routing verification
5. Analyzer: Synthesize into 3 prioritized changes — use `analyzer.md` as subagent prompt

### Two-Claude Ad-hoc Testing

Official approach for trigger verification: create evaluations before writing documentation, then test with two independent Claude instances. The goal is evaluation-driven development — verify routing works with real queries before committing to description language.

**Process:**
1. Draft candidate descriptions for the skill
2. Create a small eval set of representative queries
3. Test routing with two Claude instances (ad-hoc, not scripted benchmark)
4. Refine description based on routing results

**The eval is a teaching instrument, not a gate.** Failed test cases teach where the description is unclear. If ad-hoc performance is poor, rebuild with genuinely different query language.

### Grading Dimensions

Skills are graded on four dimensions. **Routing Signal** (40% weight) measures whether the description gives clear trigger phrases for when to invoke the skill. **Delta Clarity** (30%) measures whether the skill states what it changes from default behavior. **Teaching Posture** (20%) measures whether the skill teaches principles over procedures. **Anti-Pattern Quality** (10%) measures whether the skill provides concrete wrong/right pairs with consequence explanation.

A perfectly formatted skill that teaches nothing scores 0/10 on teaching. Format without teaching is decoration.

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

Skills must NOT reference other plugins by name. Use shared workflow vocabulary:
- ❌ "Use tp-sadd:judge for verification"
- ✅ "For independent evaluation, dispatch a judge with isolated context"
- ❌ "Feeds into another plugin's analyse"
- ✅ "Produces analysis output for downstream improvement processes"

## Meta-Rule (applies to this file only)

**Governs itself — all revisions must remain:**
- **Concise** — Minimum text for correct autonomous dispatch; no explanation, no prose ornamentation.
- **Non-interactive** — No user-input dependency; describes only what Claude Code executes without prompting.
- **Self-contained** — A cold-start instance must dispatch correctly from this file alone (skill priority, hook timing, rule merge order, subagent spawn mode).

---

## End-of-Turn Follow-Up Discipline

When a task concludes, identify what remains undone across the full stack — code, docs, skills, rules, and git state — without being asked. Surface it as a short numbered list so the user can pick direction rather than tediously extracting it from conversation.

The goal is a clean handoff: thinking is done when the work is verified, not when a response is sent.

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