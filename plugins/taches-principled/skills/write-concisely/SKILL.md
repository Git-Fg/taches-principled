---
name: write-concisely
description: Make documentation clearer and more professional using Strunk & White's principles. Use when user says 'make this clearer', 'write this more concisely', 'clean up this text', or 'improve the writing'.
when_to_use: |
  Use when the user says "make this clearer", "write this more concisely", "clean up this text", "improve the writing", "fix the prose", "tighten this", "remove the filler", or "sound more professional".
  IMMEDIATELY when producing documentation, READMEs, comments, changelogs, or any human-readable text.
  FIRST after writing any documentation longer than one paragraph.
  DO NOT use on code itself (use refine for code), on structured data, or on error messages (use kaizen principles for error design).
  CONTRAST with update-docs: that updates existing docs; this improves the quality of the writing itself.
  CONTRAST with refine: that simplifies code logic; this improves prose clarity and conciseness.
---

## Decision Router

IF writing or editing documentation for human readers → Apply the full set of composition principles
IF reviewing existing text for conciseness → Apply Omit Needless Words, Active Voice, Positive Form
IF writing code comments or internal docs → Focus on clarity and concreteness, skip usage rules
IF translating technical content to user-facing docs → Prioritize concrete language and positive form

# Write Concisely

Apply Strunk & White's *Elements of Style* principles to any text a human will read. Claude already knows these rules — this skill exists to remind you to apply them. Do not explain the rules in your output; simply apply them.

## Principles of Composition

1. **Use the active voice** — more direct and vigorous than passive
2. **Put statements in positive form** — say what is, not what isn't
3. **Use definite, specific, concrete language** — prefer specifics to generalities
4. **Omit needless words** — every word must tell
5. **Keep related words together** — position shows relationship
6. **Place emphatic words at the end** — the end is the position of prominence
7. **Use parallel construction** — coordinate ideas in similar form
8. **One paragraph per topic** — begin with a topic sentence

## Words to Watch

| Avoid | Prefer |
|-------|--------|
| the fact that | since, because |
| in a hasty manner | hastily |
| he is a man who | he |
| due to (adverbial) | because of |
| along these lines | rephrase directly |
| the question as to whether | whether |
| there is no doubt but that | no doubt |

## Application

When writing documentation, run through each principle mentally and check your text for violations. The most impactful ones to apply:

1. Scan for passive voice — rewrite to active where the subject is performing the action
2. Scan for "there is/are" constructions — replace with a stronger verb
3. Scan for negative statements — replace with positive form
4. Scan for wordy phrases — replace with their concise equivalents
5. Scan for vague language — replace with concrete specifics

Do not enumerate which rules you applied in your output. Simply produce cleaner text.

## Design Decisions

### Why not include the full text of Elements of Style
Claude already knows these rules from training. The skill's only job is to trigger their application. Full rule text wastes context and adds no behavioral change.

### Relationship to development pipeline
- Applied during documentation creation and review
- Complements update-docs by enforcing quality on the output
- Operates on the final text layer, not the code or structure layer
