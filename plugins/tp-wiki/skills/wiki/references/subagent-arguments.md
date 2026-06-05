# Subagent Argument Contract and Registry Preamble

This file is the single source of truth for two things every wiki subagent (`wiki-searcher`, `wiki-ingester`, `wiki-linter`) needs to know at spawn time:

1. **The argument contract** — what arguments the hub is expected to pass, and what to do when the hub forgets.
2. **The registry preamble** — what the registry is, what `what_to_read` is for, and why walking it is non-negotiable.

The hub skill (`SKILL.md`) cites this file once. The three agents inherit the contract transitively via the `skills: [wiki]` frontmatter — they do NOT cite this file directly. Each agent body keeps only its role-specific content: its own argument (`query`, `mode`+`content`, or `directive`), its role-specific orientation tail, and its own failure-modes catalog.

---

## Argument Contract

The hub spawns you. It is **expected to pass `wiki_path` (preferred) or `alias` (fallback) as an argument**, plus any role-specific arguments:

| Argument | Type | Purpose |
|---|---|---|
| `wiki_path` | string (preferred) | Absolute path to the wiki to operate on. The hub resolves this from the registry before spawning you. |
| `alias` | string (fallback) | The label from `~/.claude/wiki-root.md` (e.g., "pharma", "work", "personal"). If you receive this instead of `wiki_path`, resolve it from the registry yourself. |
| `multi_wiki` | bool (default false) | If true, run the operation against every configured wiki and report per-wiki results. |

### Self-discovery fallback (last resort)

If neither `wiki_path` nor `alias` is provided, you should still try to infer the target by reading `~/.claude/wiki-root.md` directly:

- If the registry is unambiguous (exactly one wiki), use it.
- If the registry is ambiguous (multiple wikis and no clear signal), return an error to the hub rather than guessing. The hub will then ask the user to disambiguate.

The hub's job is to do the resolution before spawning you. Self-discovery is a fallback for the case where the hub skipped the resolution. Don't rely on it as the normal path.

### Confirmation before mutating

For INGEST and LINT operations — anything that writes or modifies files inside a wiki — confirm the chosen wiki with the user before doing anything destructive:

> "Operating on: `[<alias>]` at `<path>`. Proceed?"

The confirmation MUST happen after the disambiguation rules pick a wiki and BEFORE any subagent that can write is spawned. QUERY operations (read-only) skip the confirmation — they cannot mutate state.

The hub normally confirms before spawning. If the hub skipped the confirmation step, the writing subagent MUST confirm before its first write.

---

## Registry Preamble (multi-wiki)

The hub that spawned you will normally pass a resolved `wiki_path` (or an `alias` for you to resolve) — that resolution comes from `~/.claude/wiki-root.md`, which holds one TOML table per registered wiki along with the `path`, `tags`, `what_to_read` pointers, and a natural-language description of each. The wiki skill loaded with you teaches the registry schema in full, including the confirmation-before-mutating policy above.

Before you read or write anything inside the wiki, walk its `what_to_read` list in order — those files (typically `SCHEMA.md`, `index.md`, and optionally `log.md`) tell you the wiki's conventions, what pages already exist, and what's been done recently. Skipping that orientation is how duplicate pages, conflicting tag taxonomies, and rewrite loops end up in the wiki.

The `what_to_read` filenames are bare strings, relative to the wiki's `path`. The registry schema reference (`references/registry-schema.md`) defines the full field semantics.

---

## What each agent keeps local

Each subagent body still owns its role-specific content that does not generalize:

- The role-specific argument (`query` for searcher, `mode`+`content` for ingester, `directive` for linter).
- The role-specific orientation tail — the one or two sentences after the shared preamble that say WHY the orientation matters for THIS agent's job (search results worth citing; verification checks that compare against conventions; pages that get written correctly).
- The agent's own failure-modes catalog (read-only constraint, ingest bulk mode, lint auto-fix policy, etc.).
- The agent's own task procedure and output format.

If you find yourself writing the same argument definitions or self-discovery language in two agents, put it here instead.
