---
name: cross-skill-references
description: Skill/agent references resolve locally within their containing folder. Citing a sibling skill's references names the skill in natural language.
---

# Rule: MUST cite sibling skill references as bare `references/X.md` from the skill name in natural language

**Why:** Claude Code resolves relative paths within the containing file's directory tree. An orchestrator at `plugins/<plugin>/skills/<skill>/SKILL.md` citing `references/X.md` resolves to `plugins/<plugin>/skills/<skill>/references/X.md` — even when the file actually lives in a sibling skill. Bare `references/` paths silently fail at runtime when the containing file doesn't own them. The skill-name prefix in a natural-language sentence tells the reader (and the model) which skill owns the reference, without constructing a filesystem path that may drift.

## Rule

- A file at `plugins/<plugin>/skills/<skill>/SKILL.md` (or `plugins/<plugin>/agents/<name>.md`) cites its OWN `references/` with a bare `references/X.md` path.
- A file citing references from a SIBLING skill MUST name the skill in the sentence and use the bare `references/X.md` path: "see `references/X.md` from `skill-name`" (not `skill-name/references/X.md`).
- A subagent that preloads a skill via `skills: [X]` frontmatter MAY cite that preloaded skill's `references/` files using the same natural-language pattern.
- A subagent that did NOT preload a skill MUST NOT cite that skill's references — the citation is unsupported by the load chain. Cite the role semantically instead ("dispatch a judge subagent").

## Verification

Before shipping a SKILL.md or agent that cites `references/X.md`, run:
```
ls <containing-skill>/references/X.md
```
If the file does not exist at that path, check whether the reference is from a sibling skill. If so, rewrite the citation as natural language with the skill name. If the reference is from your own skill, the path is correct.

## Bad / Good

**Bad:** An orchestrator at `plugins/tp-mcp/skills/mcp-quality-evaluate/SKILL.md` cites `references/quality-rubric.md` bare — the file lives in `mcp-expertise/references/`, not in `mcp-quality-evaluate/references/`. The orchestrator has no `references/` directory; the path silently fails.
**Good:** The orchestrator writes "see `references/quality-rubric.md` from `mcp-expertise`". The skill name makes ownership explicit; the bare path is what the model looks up within the preloaded skill's context.

**Bad:** An orchestrator cites `mcp-expertise/references/quality-rubric.md` — a filesystem path that constructs the sibling skill's tree. This couples to the file layout and breaks if the skill reorganizes.
**Good:** The orchestrator writes "see `references/quality-rubric.md` from `mcp-expertise`". The bare path is how the preloaded skill resolves it; the skill name is for the reader.

**Bad:** A subagent preloads `mcp-expertise` via `skills: [mcp-expertise]`, then cites `references/quality-rubric.md` bare without naming the skill. The reader cannot tell which skill owns the reference.
**Good:** The subagent writes "see `references/quality-rubric.md` from `mcp-expertise`". The preloaded skill name is explicit; the bare path resolves correctly.
