---
name: plugin-isolation
description: Enforces plugin self-containment, cross-plugin communication, and skill file reference rules.
paths: "plugins/**"
---

# Rule: MUST keep plugins fully standalone and skills self-contained

**Why:** Each plugin is installed independently — users may have only one plugin from this marketplace. Cross-plugin dependencies create silent failures. Skills that traverse parent paths (`../`) or cross-cite reference files break the skill loader's resolution logic. Reference files with routing logic create chicken-and-egg paradoxes where the file must be read to decide whether to read it.

## Rule

- Each plugin MUST work when installed alone. Zero code sharing, zero dependencies, zero runtime coupling between plugins.
- Cross-plugin references MUST cite by semantic role ("dispatch a judge subagent"), not by file path or plugin name.
- File paths within a skill MUST NOT use `../` to traverse outside the skill directory. All internal references resolve locally.
- ONLY the main SKILL.md file may cite supporting files. Reference files MUST NOT cross-cite other reference files.
- Reference files MUST be pure content — no frontmatter, no loading triggers, no "When to read" sections, no conditional loading logic. All routing lives in SKILL.md.
- Subagents that preload a skill via `skills:` frontmatter MAY cite that skill's `references/` files with a single imperative sentence.

## Bad / Good

**Bad:** A tp-sadd skill referencing `../../core-principled/skills/refine/references/patterns.md` for shared patterns.
**Good:** The tp-sadd skill has its own `references/` copy of the relevant patterns, or uses semantic vocabulary to let the orchestrator invoke the refine skill separately.

**Bad:** A `references/advanced.md` file containing "Read this file when the task involves complex multi-step workflows."
**Good:** SKILL.md body: "You MUST read `references/advanced.md` BEFORE planning multi-step workflows." The reference file contains only the content, no loading instructions.

**Bad:** Plugin tp-git importing a utility from tp-rust's skill references.
**Good:** Plugin tp-git is fully self-contained with its own references; it describes capabilities using shared workflow vocabulary.
