# Environment Variable Patterns

When to use `{baseDir}` vs `${CLAUDE_SKILL_DIR}` for path references in skills.

---

## `{baseDir}` — SKILL.md Body References

**Use `{baseDir}` in SKILL.md body for Read/Grep tool references.**

`{baseDir}` resolves to the directory containing the SKILL.md file at runtime. It is the skill-relative root.

| Pattern | Example | Use Case |
|---------|---------|----------|
| `{baseDir}/agents/critic.md` | Read reference | Internal agent templates |
| `{baseDir}/references/checkpoint-protocols.md` | Cross-reference | Other reference docs in same skill |
| `{baseDir}/../create-plans/references/plan-format.md` | Adjacent skill reference | References in sibling skills |

**Why:** The SKILL.md body uses Read/Grep tools, not Bash. `{baseDir}` is the correct substitution for file-to-file references within the skill.

---

## `${CLAUDE_SKILL_DIR}` — Bash Tool Commands

**Use `${CLAUDE_SKILL_DIR}` in Bash tool commands for script execution.**

`${CLAUDE_SKILL_DIR}` is the shell environment variable containing the skill's install path. It is used when executing scripts, invoking CLI tools, or running code.

| Pattern | Example | Use Case |
|---------|---------|----------|
| `${CLAUDE_SKILL_DIR}/scripts/generate.sh` | Bash script | Running build/generate scripts |
| `source ${CLAUDE_SKILL_DIR}/scripts/helpers.bash` | Sourcing | Shell helper functions |
| `${CLAUDE_SKILL_DIR}/bin/tool --flag` | CLI invocation | Running tools from skill bin/ |

**Why:** Bash runs in a shell subprocess. Only shell environment variables (starting with `$`) are expanded in Bash commands. `{baseDir}` is a Claude Read/Grep substitution, not a shell variable.

---

## Plugin Portability Warning

**First-attempt failure pattern:** Absolute skill paths assume fixed install location.

Anti-pattern:
```
Read(skills/execute-plans/agents/critic.md)
```

Problem: If this skill is installed in a plugin with a different directory structure, or if Claude Code changes skill loading paths, the reference breaks.

Correct pattern:
```markdown
Read({baseDir}/agents/critic.md)
```

`{baseDir}` adapts to the skill's actual location at runtime. The skill becomes portable across plugins and install contexts.

---

## Summary

| Tool | Variable | Example |
|------|----------|---------|
| Read/Grep in SKILL.md body | `{baseDir}` | `Read({baseDir}/agents/critic.md)` |
| Bash commands | `${CLAUDE_SKILL_DIR}` | `source ${CLAUDE_SKILL_DIR}/scripts/helpers.bash` |

**Rule:** If using Read/Grep, use `{baseDir}`. If using Bash, use `${CLAUDE_SKILL_DIR}`.