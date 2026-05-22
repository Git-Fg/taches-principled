# Taches Principled — Development Guide

Development practices for maintaining this plugin. These are operational rules, not suggestions.

---

## Version Management

**Marketplace version** and **plugin version** are independent:

- **Plugin version** (`0.3.0`): Incremented for any content change to this plugin
- **Marketplace version** (root `marketplace.json`): Incremented when releasing a collective update across all plugins

**Update sequence:**
```bash
# 1. Make your changes
git add -A && git commit -m "message"

# 2. Bump plugin version (minor for features, patch for fixes)
# Edit .claude-plugin/plugin.json — bump "version" field

# 3. Push
git push
```

---

## Skill Authoring

Skill authoring is taught by the `create-skills` skill. See that skill for:
- **Skill categories**: Constraint/Guardrail, Orchestration, Domain Expertise, Quality Assurance, Creative Direction
- **Policy vs. Mechanism**: The unifying principle for skill design
- **Delta principle**: Only document what differs from default behavior
- **Skill anatomy**: Frontmatter and body structure
- **Anti-patterns**: What to avoid in skill design
- **Cross-skill references**: Never cite other skills' files with paths (e.g., `skills/create-plans/references/X.md`) — use natural language: "see the X.md file in the create-plans skill's references"
- **Decision router**: How to structure SKILL.md for strong reference steering

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

---

## Token Economy

- **Commands over skills for on-demand loading** — skills consume context always; commands load when invoked
- **Specialized agents with narrow context** — broad-context agents hallucinate more
- **Setup-commands for persistent context** — write to CLAUDE.md rather than relying on skill loading
- **Token estimation** — every skill should know its approximate cost

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

## Explorer Subagent Protocol

When spawning subagents for exploration/investigation, the orchestrator should:

1. **Read** any existing scratch notes BEFORE spawning — avoid redundant work
2. **Write** current context and questions to the scratch area — preserve institutional memory
3. **Use a general-purpose subagent with Write tool** — Haiku Explore subagents are read-only and cannot write findings; a general-purpose subagent with `[Read, Write, Grep, Glob, Bash]` is needed for investigation work
4. **Read** scratch notes AFTER subagents return, BEFORE synthesizing

**Guidance, not rigidity:** The goal is preventing the telephone game — information degrading as it passes through multiple agents. Writing findings to a shared artifact (rather than relying on subagent output alone) keeps the chain intact. The scratch area location is `.principled/scratch/` — use descriptive topic filenames.

---

## Evaluation Pipeline

taches-principled has a multi-agent evaluation system for skill quality assurance:

### The Four Evaluation Agents

| Agent | Purpose | Output |
|-------|---------|--------|
| **Grader** | Measures teaching effectiveness (not format compliance) | Dimension scores (routing, delta, posture, anti-patterns) |
| **Comparator** | Compares skill versions to understand what changed | Delta analysis with teaching impact |
| **Skill Auditor** | Quality signals and format audit | Severity-ranked findings |
| **Analyzer** | Synthesizes into prioritized improvement path | Max 3 changes with teaching outcomes |

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
[Trigger Benchmark] → 20-query routing accuracy test
    ↓
[Analyzer] → 3 prioritized changes with teaching outcomes
    ↓
Skill Improved
```

### Invoking the Pipeline

**Quick audit** (format + quality only):
```markdown
Agent(description = "Audit [skill] for quality",
      prompt = "Read [path]/SKILL.md and audit following skill-auditor.md.")
```

**Full evaluation** (teaching + routing + format):
```markdown
1. Grader: Grade for teaching effectiveness
2. Comparator: Compare versions if applicable
3. Skill Auditor: Audit for quality signals
4. Trigger Benchmark: python3 ${CLAUDE_SKILL_DIR}/scripts/run_trigger_benchmark.py [skill] --interactive
5. Analyzer: Synthesize into 3 prioritized changes
```

### Trigger Benchmark

Tests skill description reliability with 20 queries:

| Category | Count | Exit Target |
|----------|-------|------------|
| Core positive (must trigger) | 5 | 100% |
| Edge positive (should trigger) | 3 | >60% |
| Core negative (must not trigger) | 5 | 100% |
| Edge negative (should not) | 3 | >40% |
| Held-out (blind test) | 4 | >70% |

**The benchmark is a teaching instrument, not a gate.** Failed test cases teach where the description is unclear. If held-out < 70%, the description overfit to test cases — rebuild with genuinely different queries.

### Grading Dimensions

| Dimension | Weight | What It Measures |
|-----------|--------|-----------------|
| Routing Signal | 40% | Description gives clear trigger phrases |
| Delta Clarity | 30% | Skill states what it adds vs. default |
| Teaching Posture | 20% | Principles over procedures |
| Anti-Pattern Quality | 10% | Concrete wrong/right pairs with consequence |

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
plugins/{tp-sadd,tp-sdd,tp-fpf,tp-git,tp-tdd,tp-ddd}/
├── .claude-plugin/plugin.json     # Plugin manifest (name, version, author)
├── skills/{name}/SKILL.md         # One directory per skill
├── agents/                        # Bundled subagent definitions
└── rules/                         # Always-active guardrails (DDD, tech-stack)
```

### Naming Convention

All imported/ported plugins use the `tp-` prefix: `tp-sadd`, `tp-sdd`, `tp-fpf`, `tp-git`, `tp-tdd`, `tp-ddd`.

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
- ❌ "Feeds into tp-kaizen:analyse"
- ✅ "Produces analysis output for downstream improvement processes"

See the synergy map in the integration architecture document for the full shared vocabulary.

## References

- [Claude Code Skills Documentation](https://docs.claude.com)
- [context-engineering-kit](https://github.com/NeoLabHQ/context-engineering-kit) — inspiration source