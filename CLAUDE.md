# Taches Principled — Development Guide

Development practices for maintaining this plugin. These are operational rules, not suggestions.

---

## Version Management

**Marketplace version** and **plugin version** are independent:

- **Plugin version** (`1.1.0`): Incremented for any content change to this plugin
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

## Skill Enhancement Protocol

When improving skills, follow the Tier system:

### Tier 1 — Teaching Patterns (Do First)
- Policy/Mechanism framing
- Anti-Patterns sections
- Numeric thresholds with rationale

### Tier 2 — Ecosystem (Do Second)
- Cross-references between related skills

### Tier 3 — Architectural (Do Third)
- Plugin split decisions
- Command vs. skill loading tradeoffs

### Tier 4 — Documentation (Do Last)
- README updates
- CHANGELOG entries
- Marketplace manifest sync

**Rule:** Complete Tier N before starting Tier N+1. Content quality comes before distribution.

---

## Skill Anatomy Standards

Every skill in this plugin follows a strict structure:

```yaml
---
name: skill-name
description: "[Verb] [artifact] for [domain]. Use when [trigger1], [trigger2]."
when_to_use: |
  Do NOT use for [exclusion1], [exclusion2].
---
```

**Body sections (in order):**
1. What this skill does (one clear paragraph)
2. Core principle (the key insight)
3. Policy vs. Mechanism framing
4. How-to guidance
5. Anti-Patterns (if applicable)
6. Numeric thresholds (if applicable)
7. Reference index

**Forbidden:**
- Checkpoint types (### Step 1, ### Step 2...)
- XML-style tags (use markdown sections instead)
- Generic descriptions that could apply to anything
- Made-up frontmatter fields not in official docs

---

## Policy vs. Mechanism — The Unifying Principle

Every skill teaches this distinction:

| Skill | Policy | Mechanism |
|-------|--------|-----------|
| `create-plans` | What a good plan looks like | How to decompose and sequence |
| `create-subagents` | When to spawn vs. delegate | How to construct spawn prompts |
| `create-skills` | When to trigger | What the skill teaches |
| `execute-plans` | When to use autonomous/segmented/sequential | How to orchestrate parallel workers and milestone reviews |

**When writing a new skill:** State the policy first, then the mechanism. If you can't separate them, the skill is doing too much.

---

## User Interaction

**Interact with users when gathering information or making decisions — not while executing a plan.**

When you need user input, ask clearly. Present options as clickable choices, not numbered lists or free-form prompts. Make it easy to say yes or no to a specific direction.

During execution, trust your judgment for anything the plan didn't explicitly decide. If you find yourself asking "should I do X or Y?" — check whether the plan already commits to one. If it does, proceed. If neither was decided and the choice is significant, stop and ask.

Use checkpoints when verification is genuinely needed — not as a checkpoint for every task. A checkpoint that requires the user to think is often a sign the plan needed more specificity upstream.

The goal is a smooth handoff between thinking and doing. Questions belong in the thinking phase. Once you're implementing, focus on building.

---

## Numeric Thresholds

These limits are not arbitrary — they come from cognitive science and agent reliability research:

| Metric | Limit | Source |
|--------|-------|--------|
| Tasks per plan | 12 max (2-3 typical) | Quality degradation at ~50% context |
| Spawn prompt length | 1500 tokens max | Reliability drop beyond this |
| Tools per subagent | 7 max | Miller's number |
| Description length | 150 chars | Truncation at 1,536 combined with when_to_use |
| Skill body | 500 lines | Principle dilution beyond this |
| Default timeout | 60s | External commands can hang |

**When limits are exceeded:** Split, don't stretch. A broken-up task beats an overwhelmed agent.

---

## Anti-Patterns for Skills

### ❌ Vague description
"Helps with coding" — triggers on everything, means nothing.

### ✅ Specific description with trigger keywords
"Creates unit tests with edge cases. Use when user asks to 'write tests', 'add test coverage', or 'generate tests'."

### ❌ Generic skill name
"name: helper" — no specialization signal.

### ✅ Specific skill name
"name: security-auditor" — clear role.

### ❌ Overloaded skill
One skill handling skill creation, agent config, AND hooks — no clear identity.

### ✅ Focused skill
Each skill has one job. If it needs more than 7 tools or 500 lines, split.

### Per-File Version Tracking

**Anti-pattern:** Adding `version:` and `updated:` frontmatter to every file in a system.

**Why it's wrong:** Version numbers per file create maintenance overhead with no value. Git commit history already tracks when files changed. When a file is updated, you bump the version — but the version number never actually controls anything. It's ceremony.

**Examples:**
- `version: 1.0` in every markdown reference file
- `updated: 2026-05-22` timestamps that nobody reads
- CHANGELOG per file instead of per project

**Correct approach:**
- Version the project/package (plugin.json, package.json)
- Trust git history for file-level change tracking
- Use CHANGELOG.md for project-level release notes, not per-file timestamps

**Signal:** If you're adding metadata about when something changed instead of just changing it, stop.

---

## Documentation Sync

README.md lives in two places:
1. The plugin root (source of truth)
2. Any docs/ directory (for GitHub Pages or marketplace docs)

**When you update README:** Copy to all locations manually. Unlike context-engineering-kit, we don't use justfile sync commands.

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

- [ ] Frontmatter uses only documented fields
- [ ] Body uses markdown sections (not XML tags or checkpoint headers)
- [ ] Policy/Mechanism framing present
- [ ] Anti-Patterns present if the concept is invertible
- [ ] Numeric thresholds present where applicable
- [ ] README updated if structure changed
- [ ] CHANGELOG entry added
- [ ] No MCP references (plugin is MCP-free)
- [ ] No broken cross-references between skills
- [ ] User interaction uses clear, structured options

---

## Testing Skills

Test trigger behavior with headless Claude:
```bash
claude -p "write tests for auth" --dangerously-skip-permissions 2>&1 | grep "create-skills"
```

If the skill name appears in the output, it triggered correctly.

---

## Rule: Quality Over Quantity

Better a 100-line skill that teaches clearly than a 500-line skill that overwhelms.

Every line competes for context space. Every line must earn its place.

---

## Rule: No Generated Documentation

Do not create README summaries or changelog summaries using AI. Write them by hand. The effort of writing forces clarity of thought.

---

## Rule: Named Principles Over Procedures

If you find yourself writing "Step 1, Step 2, Step 3" — stop. Ask: what is the **principle** that makes these steps correct? Write the principle. The steps should be obvious from the principle, not from a checklist.

---

## Artifact Hygiene — `.principled/` Directory

**All Claude-generated artifacts live in `.principled/` — never pollute the codebase.**

Generated plans, prompts, scratch notes, and cross-session memory go here. This keeps git clean and makes it easy to archive or wipe generated content.

```
.principled/
├── plans/           # Plans, briefs, roadmaps, phases
│   ├── phases/     # Phase-specific plans and summaries
│   └── .attic/     # Archived completed phases
├── prompts/        # Generated prompts
│   ├── analyses/
│   ├── research/
│   ├── completed/
│   └── .attic/
├── scratch/        # Debug sessions, temp artifacts
└── memory/         # Architecture state, cross-session notes
```

**Archiving:** Skills define when to move content to `.attic/`. A plan moves to `.attic/` when its phase completes. Prompts move when execution finishes. The attic is not deleted — it preserves context for future audits.

**Not artifacts:** `.claude/agents/` and `.claude/skills/` are definitions, not generated content. They stay where they are.

---

## References

- [Claude Code Skills Documentation](https://docs.claude.com)
- [context-engineering-kit](https://github.com/NeoLabHQ/context-engineering-kit) — inspiration source