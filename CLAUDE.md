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

**Archiving:** Skills define when to move content to `.attic/`. A plan moves to `.attic/` when its phase completes. Prompts move when execution finishes. The attic preserves context for future audits.

**Not artifacts:** `.claude/agents/` and `.claude/skills/` are definitions, not generated content. They stay where they are.

---

## References

- [Claude Code Skills Documentation](https://docs.claude.com)
- [context-engineering-kit](https://github.com/NeoLabHQ/context-engineering-kit) — inspiration source