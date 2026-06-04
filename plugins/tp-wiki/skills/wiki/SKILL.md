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

## Routing — Delegate to Subagents

Classify the user's intent, then spawn the matching subagent:

**Query / Search** → Spawn `wiki-searcher` subagent.
Pass: the user's natural language query.

**Ingest / Build / Add to wiki** → Spawn `wiki-ingester` subagent.
Pass: mode (`url`, `text`, `file`, or `bulk`) + the content + optional `wiki_path` hint.

**Lint / Verify / Check consistency** → Spawn `wiki-linter` subagent.
Pass: the verification directive + optional `wiki_path` hint.

## Mandatory Orientation — Every Wiki Operation

**Before touching the wiki, always orient yourself first.**

1. **Read `SCHEMA.md`** — domain, conventions, tag taxonomy, page thresholds
2. **Read `index.md`** — what pages already exist (prevents duplicates)
3. **Scan `log.md`** (last 20-30 lines) — what's been done recently

This applies to all three subagents before they read or write anything.

## CONTRAST

- NOT for: general web search, code search, or reading project documentation outside the wiki
- NOT for: replacing a database, CRM, or structured data store
- NOT for: real-time note-taking during a meeting (use a dedicated notes tool)
- NOT a static site generator — the wiki is agent-maintained, not published

## Detailed Methodology

For full operational guidance (ingest, query, lint, archiving, Obsidian sync, pitfalls),
read `references/llm-wiki-methodology.md`.
