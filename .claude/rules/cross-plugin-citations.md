---
name: cross-plugin-citations
description: Cross-plugin references cite by semantic role, not plugin name or file path. Cross-skill references (same plugin) follow the same rule with relaxed naming.
---

# Rule: MUST cite cross-plugin references by semantic role, never by plugin name or file path

**Why:** A user may install only one plugin from this marketplace. A skill that cites "the `tp-sadd` parallel-judge pattern" or "see `tp-sadd/agents/sadd-judge.md`" creates a broken coupling: the user does not have `tp-sadd` installed, the cited file is unreachable, and the reference becomes a dangling pointer. Even when both plugins are installed, naming a plugin by identifier creates a maintenance tax: every rename, deprecation, or refactor in the cited plugin ripples into the citing plugin's documentation. The semantic role ("a judge subagent", "a parallel-judge pattern") is the universal vocabulary that survives plugin reorg.

## Rule

- A reference to a pattern, file, or concept from ANOTHER plugin cites the SEMANTIC ROLE only. Examples: "a parallel-judge pattern", "a judge subagent", "a 5-mode hub", "a quality rubric".
- A reference MUST NOT name another plugin by its identifier (`tp-sadd`, `core-principled`, etc.) in any artifact that ships to end users.
- A reference MUST NOT cite another plugin's file path (`tp-sadd/agents/sadd-judge.md`) — file paths break when files move.
- A reference to a feature unique to another plugin MUST describe the role, not the name. If the role is the point, the role is enough. If naming the plugin is necessary for navigation, link to a knowledge base doc, not a file path.
- The rule applies to: SKILL.md bodies, reference files, agent bodies, CHANGELOG entries, comments in code, and commit messages that ship in PRs.

## Same-plugin citations

- A reference to a sibling skill within the same plugin MAY name the skill (`"see the `mcp-expertise` hub's DESIGN mode"`) but MUST still avoid file paths.
- A reference to the SAME skill's own references/ files uses bare `references/X.md` paths (per `cross-skill-references.md`).

## Verification

Before shipping any artifact that mentions another plugin, grep for the other plugin's identifier:
```
grep -rn "tp-sadd\|core-principled\|tp-mcp\|tp-fpf\|tp-git\|tp-rust\|tp-security\|tp-session-audit\|tp-wiki\|claude-cli-wrapper" plugins/<your-plugin>/
```
Any match is a candidate for replacement with the semantic role.

## Bad / Good

**Bad:** A `quality-judge-pattern.md` §6 reads "The pattern is the same parallel-judge approach the `tp-sadd` plugin uses for code evaluation, specialized for MCP servers." A user with only `tp-mcp` installed sees the dangling reference; even users with both plugins installed have a brittle cross-plugin coupling.

**Good:** "The pattern is a parallel-judge approach specialized for MCP servers." The semantic role is what the user needs; the plugin name adds no information.

**Bad:** A SKILL.md CONTRAST section reads "**CONTRAST with `tp-sadd` judge pattern:** QUALITY mode applies the `tp-sadd` parallel-judge pattern to MCP servers specifically."

**Good:** "**CONTRAST with generic parallel-judge patterns:** QUALITY mode applies a parallel-judge pattern specialized for MCP servers (one judge per dimension of the Claude-Optimal rubric)."
