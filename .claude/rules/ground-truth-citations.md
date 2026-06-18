---
name: ground-truth-citations
description: The P6 / Ground Truth rule applies to all agents. Volatile provenance (issue numbers, file paths, PR numbers) belongs in commit messages, not agent bodies.
---

# Rule: MUST keep agent bodies free of volatile provenance; the P6 verification rule is universal

**Why:** Agents ship to end users. The P6 / "Ground truth" rule ("Read or Grep the relevant files first; do not assert specific file paths, line numbers, function names, or content based on speculation") is a marketplace-wide pattern. When an agent body adds attribution to the rule — for example, "(Adapted from a marketplace subagent's P6 rule — see audit issue and finding for the original failure mode.)" — it bakes volatile provenance (issue numbers, file paths from a specific PR) into the artifact. When the issues close, the file moves, or the rules refactor, the attribution becomes a dead link that the end user can never verify. Worse, the P6 rule itself forbids citing specific file paths without reading them — the attribution violates the rule it is documenting.

## Rule

- An agent's "Ground truth" / "P6" / "Verify before asserting" section MUST contain the rule itself, verbatim or paraphrased.
- The section MUST NOT include: issue numbers, PR numbers, GitHub URLs, file paths from a specific PR, contributor names, dates, or any other reference that becomes stale.
- The section MUST be labeled consistently across agents. The project's standard is `## Ground truth (P6)` (or `## Ground truth` for plugins that do not use the P6 numbering).
- Provenance and historical context belong in:
  - The CHANGELOG entry that introduced the rule
  - The commit message that first added the agent
  - A `knowledge/concepts/` doc if the rule itself is the documentation subject
- NEVER in the agent body, the SKILL.md body, or any reference file that ships to end users.

## Standard P6 wording

When an agent needs a "Ground truth" section, use this canonical form (paraphrasing is fine, attribution is not):

> When making claims about files, code, or runtime behavior, you MUST Read or Grep the relevant files first. Do not assert specific file paths, line numbers, function names, or content based on speculation. If you cannot verify a claim with the available tools, mark the claim as "unverified" rather than asserting it.

## Verification

Before shipping an agent with a "Ground truth" section, grep for volatile provenance:
```
grep -E "Issue #[0-9]+|PR #[0-9]+|github\.com/.*/issues\|github\.com/.*/pull" plugins/<plugin>/agents/<agent>.md
```
Any match is volatile provenance that belongs in a commit message, not the agent body.

## Bad / Good

**Bad:** An agent's Ground truth section reads "When making claims about a server, you MUST Read or Grep the relevant files first. Do not assert specific file paths, line numbers, function names, or content based on speculation. If you cannot verify a claim with the available tools, mark the claim as 'unverified' rather than asserting it. (Adapted from a marketplace subagent's P6 rule — see historical audit issue and finding for the original failure mode.)"

The trailing parenthetical bakes issue numbers, a file path, and historical context into the agent body. When issues close, this becomes a dead reference. The parenthetical also violates the P6 rule it documents (it cites a file path that the agent itself is not reading).

**Good:** "When making claims about a server, you MUST Read or Grep the relevant files first. Do not assert specific file paths, line numbers, function names, or content based on speculation. If you cannot verify a claim with the available tools, mark the claim as 'unverified' rather than asserting it."

The rule is universal; the agent's job is to enforce it, not to document its own history.
