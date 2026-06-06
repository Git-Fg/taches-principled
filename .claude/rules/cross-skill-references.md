---
name: cross-skill-references
description: Skill/agent references resolve locally within their containing folder. Citing a sibling skill's references requires the skill-name prefix.
---

# Rule: MUST prefix cross-skill reference citations with the skill name

**Why:** Claude Code resolves relative paths within the containing file's directory tree. An orchestrator at `plugins/<plugin>/skills/<skill>/SKILL.md` citing `references/X.md` resolves to `plugins/<plugin>/skills/<skill>/references/X.md` — even when the file actually lives in a sibling skill. Bare `references/` paths silently fail at runtime: the cited file is not found, the model improvises, and the orchestrator's contract breaks without an error. This PR shipped an orchestrator + 8 spawned judges that cited `references/quality-rubric.md` with no prefix — the files lived in `mcp-expertise/references/`, and the entire 8-dimension evaluation was unsupportable until the prefix was added.

## Rule

- A file at `plugins/<plugin>/skills/<skill>/SKILL.md` (or `plugins/<plugin>/agents/<name>.md`) cites its OWN `references/` with a bare `references/X.md` path.
- A file citing references from a SIBLING skill MUST prefix the path with the sibling skill name: `mcp-expertise/references/X.md` (not `references/X.md`).
- A subagent that preloads a skill via `skills: [X]` frontmatter MAY cite that preloaded skill's `references/` files using the skill-name prefix.
- A subagent that did NOT preload a skill MUST NOT cite that skill's references — the citation is unsupported by the load chain. Cite the role semantically instead ("dispatch a judge subagent").

## Verification

Before shipping a SKILL.md or agent that cites `references/X.md`, run:
```
ls <containing-skill>/references/X.md
```
If the file does not exist at that path, the citation is broken. Either add the skill-name prefix, copy the file, or remove the citation.

## Bad / Good

**Bad:** An orchestrator at `plugins/tp-mcp/skills/mcp-quality-evaluate/SKILL.md` cites `references/quality-rubric.md` — the file lives in `mcp-expertise/references/`, not in `mcp-quality-evaluate/references/`. The orchestrator has no `references/` directory; the path silently fails.
**Good:** The orchestrator cites `mcp-expertise/references/quality-rubric.md`. The skill-name prefix makes the resolution explicit and verifiable.

**Bad:** A subagent preloads `mcp-expertise` via `skills: [mcp-expertise]`, then cites `references/quality-rubric.md` (bare). The agent's containing directory is `plugins/tp-mcp/agents/`, not `mcp-expertise/` — the path resolves to nothing.
**Good:** The subagent cites `mcp-expertise/references/quality-rubric.md`. The preloaded skill name is the prefix; the file resolves correctly.
