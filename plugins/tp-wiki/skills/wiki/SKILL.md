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

Resolve the wiki root in this order:
1. `$WIKI_ROOT` env var
2. `~/.claude/wiki-root` file (single-line path)
3. Ask user: "Where is your wiki? (enter the folder path)"

After resolving, use that path for all wiki operations.

## Decision Router

Classify the user's intent, then spawn the matching subagent. When in doubt, ask the user to disambiguate ("Do you want to search the wiki, or add something to it?").

| User intent (signal words) | Spawn | Pass to the subagent |
|---|---|---|
| **Query / Search**: "find", "look up", "search", "what does my wiki say about", "do I have notes on" | `wiki-searcher` (read-only) | The user's natural-language query |
| **Ingest / Build / Add**: "add to wiki", "ingest", "save to wiki", "import", "file this into wiki", "populate wiki", "build wiki from <source>" | `wiki-ingester` | Mode (`url` / `text` / `file` / `bulk`) + the content + optional `wiki_path` hint |
| **Lint / Verify**: "lint", "check consistency", "verify", "find broken links", "reconcile", "audit" | `wiki-linter` | The verification directive + optional `wiki_path` hint |

**Dispatch notes:**
- `wiki-searcher` is the only subagent that can run on every load — it does no writes.
- `wiki-linter` and `wiki-ingester` both read AND write. The hub does NOT touch the wiki directly; the subagents are the only paths that can mutate `$WIKI_ROOT/`.
- If the user's intent is ambiguous between `ingest` and `lint` (e.g., "fix my wiki"), default to `lint` (read-only path) and let the user escalate to `ingest` if needed.
- For multi-source bulk ingest, prefer `bulk` mode — it does one search pass instead of N.

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
