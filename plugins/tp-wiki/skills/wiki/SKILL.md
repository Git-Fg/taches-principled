---
name: wiki
description: "Search, query, ingest, or verify a personal wiki, knowledge base, or notes system. Use when user mentions 'wiki', 'KB', 'knowledge base', 'look up in my notes', 'find in my wiki', 'search my docs', 'lint wiki', 'check wiki consistency', 'add to wiki', 'ingest into wiki', 'populate wiki', or 'build wiki'."
when_to_use: |
  - "Find something in my wiki / KB / notes"
  - "Search the wiki for X"
  - "Lint / verify / check consistency of the wiki"
  - "Add to the wiki / ingest into the wiki / populate the wiki"
  - "Build the wiki from a URL / file / notes"
  - NOT for: general web search (use web-search), code search, reading project documentation outside the wiki, real-time meeting notes
argument-hint: "[query|ingest|lint] [args...]"
---

# Wiki Hub — Routing and Operations

Build, query, and maintain a persistent, compounding knowledge base as interlinked markdown files.
Based on [Karpathy's LLM Wiki pattern](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f).

## Wiki Root Resolution

**The wiki root is not a single value — it's a registry of zero or more wikis.** Run `cat ~/.claude/wiki-root.md` at the start of every operation to discover what's configured. The file is a plain-text registry of `WIKI_ROOT_*` env var names, one per line.

### The registry file (`~/.claude/wiki-root.md`)

Format: one env var name per line. Blank lines and lines starting with `#` are ignored.

```
# ~/.claude/wiki-root.md
WIKI_ROOT_main
WIKI_ROOT_work
WIKI_ROOT_personal
WIKI_ROOT_research
```

Each name refers to an env var the user has set in their shell with the actual folder path:

```bash
# in ~/.zshrc / ~/.bashrc
export WIKI_ROOT_main=/Users/felix/notes/main
export WIKI_ROOT_work=/Users/felix/notes/work
export WIKI_ROOT_personal=/Users/felix/notes/personal
export WIKI_ROOT_research=/Users/felix/notes/research
```

The registry file is the source of truth for **which wikis exist**; the env vars are the source of truth for **where each wiki lives**. The user updates one or both as their setup changes.

### Resolution algorithm

At the start of every wiki operation, do this in order:

1. **`cat ~/.claude/wiki-root.md`** — discover the configured wikis. If the file doesn't exist, jump to "no registry" below.
2. **For each non-blank, non-comment line in the file**, treat it as an env var name and read its value from the environment. Build a list of `{alias, path}` pairs.
3. **Apply the disambiguation rules** (see below).
4. **Fall through to "no registry"** if no env vars resolve.

**Legacy single-wiki shortcut:** if `WIKI_ROOT` (no suffix) is set in the environment AND the registry file is missing or empty, use it. This preserves the original 0.1.0 behavior for users who haven't migrated.

### Disambiguation — picking the right wiki when several are configured

| User signal | Action |
|---|---|
| User named a specific wiki: "the work wiki", "my main notes", "wiki 2" | Match against aliases/numbers, use that one. If no match, ask. |
| User's intent implies a domain: "search the project wiki", "ingest into research" | Match alias containing the keyword. If ambiguous, ask. |
| User says nothing about which wiki | If exactly one is configured → use it without asking. If multiple → ask: "Which wiki? You have: main, work, personal, research. (or 'set up a new one')" |
| User says "all wikis" or wants an operation across them | Run the operation once per configured wiki. Aggregate results. |

**Alias numbering:** if the user says "wiki 2", number is 1-based by the order lines appear in the registry file. So `WIKI_ROOT_main` is wiki 1, `WIKI_ROOT_work` is wiki 2, etc.

### No registry — first-time setup

If `~/.claude/wiki-root.md` doesn't exist AND `WIKI_ROOT` is unset, ask the user to set up the registry:

> "No wikis configured. To set up:
> 1. Create the directory for your wiki (e.g., `mkdir -p ~/notes/main`)
> 2. Set an env var: `export WIKI_ROOT_<alias>=/path/to/wiki`"
> 3. Add the alias to `~/.claude/wiki-root.md` (one per line)
> 4. Re-run the command. Or say 'create a new wiki at <path>' and I'll do steps 1-3 for you."

### Confirming the chosen wiki before destructive operations

For `INGEST` and `LINT` operations, after picking the wiki from the registry, **confirm the choice with the user** before doing anything that mutates files:

> "Operating on: `WIKI_ROOT_work` = `/Users/felix/notes/work`. Proceed?"

The confirmation can be skipped for `QUERY` (read-only) operations.

## Decision Router

Classify the user's intent, then spawn the matching subagent. When in doubt, ask the user to disambiguate ("Do you want to search the wiki, or add something to it?").

| User intent (signal words) | Spawn | Pass to the subagent |
|---|---|---|
| **Query / Search**: "find", "look up", "search", "what does my wiki say about", "do I have notes on" | `wiki-searcher` (read-only) | The user's natural-language query + the resolved `wiki_path` |
| **Ingest / Build / Add**: "add to wiki", "ingest", "save to wiki", "import", "file this into wiki", "populate wiki", "build wiki from <source>" | `wiki-ingester` | Mode (`url` / `text` / `file` / `bulk`) + the content + the resolved `wiki_path` |
| **Lint / Verify**: "lint", "check consistency", "verify", "find broken links", "reconcile", "audit" | `wiki-linter` | The verification directive + the resolved `wiki_path` |

**Dispatch notes:**
- `wiki-searcher` is the only subagent that can run on every load — it does no writes.
- `wiki-linter` and `wiki-ingester` both read AND write. The hub does NOT touch the wiki directly; the subagents are the only paths that can mutate the resolved wiki.
- If the user's intent is ambiguous between `ingest` and `lint` (e.g., "fix my wiki"), default to `lint` (read-only path) and let the user escalate to `ingest` if needed.
- For multi-source bulk ingest, prefer `bulk` mode — it does one search pass instead of N.
- **Multi-wiki operation:** if the user says "lint all my wikis" or "ingest this into all my wikis", pass the operation to the subagent once per resolved wiki. The subagent reports per-wiki results.

## Reference Index

This hub skill ships with three specialist agents. Pick by intent:

- **wiki-searcher** (blue, sonnet, read-only tools) — `QUERY` mode. Retrieves and synthesizes information from the user's wiki. Cites source pages. Never writes.
- **wiki-linter** (yellow, sonnet, restricted tools) — `LINT` mode. Verifies consistency: orphan pages, broken wikilinks, missing frontmatter, index drift, tag sprawl, intent violations, stale content. Auto-fixes safe violations; flags structural ones.
- **wiki-ingester** (green, sonnet, restricted tools) — `INGEST` mode. Adds new content to the wiki. Supports `url` (fetch web page), `text`/`notes` (pasted content), `file` (read a file), `bulk` (batch of N). Never modifies `raw/` once written.

The agents compose: a typical ingest run reads `SCHEMA.md` → fetches the source → cross-references existing pages → writes new pages with 2+ outbound wikilinks → updates `index.md` and `log.md`. A typical lint run reads `SCHEMA.md` + `index.md` + (optional) `.wiki/intent.md` → runs 7 checks (A–G) → groups findings by severity → auto-fixes safe items.

## Mandatory Orientation — Every Wiki Operation

**Before touching the wiki, always orient yourself first.** This applies to all three subagents before they read or write anything.

1. **Read `$WIKI_ROOT/SCHEMA.md`** — domain, conventions, tag taxonomy, page thresholds
2. **Read `$WIKI_ROOT/index.md`** — what pages already exist (prevents duplicates)
3. **Scan `$WIKI_ROOT/log.md`** (last 20-30 lines) — what's been done recently

(These three files live in the user's wiki at `$WIKI_ROOT/`, not in this plugin. They are the wiki's own configuration and state, not the plugin's.)

## Cross-plugin dependencies

This skill is part of the `tp-wiki` plugin and depends on **optional** MCP tools. The skill works without them, falling back to the noted substitute.

| MCP tool | Used in | Fallback if absent |
|---|---|---|
| `mcp__mcp-searxng__fetch` | `wiki-ingester` mode `url` (fetch the web page) | `WebFetch` (Claude Code's built-in) — slower but always available |
| `mcp__mcp-searxng__extract` | `wiki-ingester` mode `url` (RAG-ranked chunks for better summarization) | Fetch full page and post-process locally |
| `web_extract` (alias) | Same as `mcp__mcp-searxng__extract` | Same as above |

**Why these aren't hard dependencies:** `tp-wiki` ships standalone — a user who only wants wiki management should be able to install just this plugin. The MCP tools are accelerators (faster, RAG-ranked), not requirements. The fallback path uses Claude Code's built-in `WebFetch`.

**No marketplace-plugin dependencies.** This plugin does not import any other `tp-*` plugin. It is self-contained.

## Anti-patterns

❌ **Modifying `raw/` files after they are written.** Sources are immutable. The ingester writes them once with `source_url` / `source_path` / `ingested` / `sha256` frontmatter and never re-touches them. Re-fetching for a new ingest is a separate event with a new sha.

❌ **Creating a page from a single mention.** Page threshold is 2+ sources OR central to one source. A single mention in passing doesn't earn its own page — it goes in a more general page or stays as a wikilink target stub.

❌ **Adding a new tag without updating `SCHEMA.md` first.** Tag sprawl is the wiki's version of type-system rot. New tag → add to `SCHEMA.md` taxonomy → THEN use it.

❌ **Skipping the orientation step.** Reading `SCHEMA.md` / `index.md` / `log.md` first is not optional. Skipping it is how you end up with duplicate pages, conflicting tag taxonomies, and rewrite loops in `log.md`.

❌ **Returning a "no results found" without checking the wiki root.** The wiki may not be configured. Resolve the root first; if unresolved, ask the user for the path. Don't return empty from a misconfigured wiki root — that's a setup bug, not a search miss.

❌ **Ingesting into the wiki while another ingester is running.** `bulk` mode assumes a single writer. Concurrent ingests will produce duplicate pages, conflicting `index.md` updates, and torn `log.md` entries. The hub should serialize ingest operations.

❌ **Linting then auto-fixing in one shot.** `wiki-linter` should report findings first; the user should approve the auto-fix policy (e.g., "yes, auto-fix orphan detection and missing frontmatter, but flag broken wikilinks for me"). Don't conflate the two phases.

## CONTRAST

- NOT for: general web search, code search, or reading project documentation outside the wiki
- NOT for: replacing a database, CRM, or structured data store
- NOT for: real-time note-taking during a meeting (use a dedicated notes tool)
- NOT a static site generator — the wiki is agent-maintained, not published

## Detailed Methodology

For full operational guidance (ingest, query, lint, archiving, Obsidian sync, pitfalls),
read `references/llm-wiki-methodology.md`. The wiki format itself is documented in
`references/wiki-format.md`. The intent file format (`.wiki/intent.md`) is in
`references/intent-format.md`.
