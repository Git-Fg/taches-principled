# LLM Wiki Methodology

Full operational guidance for the wiki skill. Subagents should read this
when performing ingest, query, lint, or maintenance operations.

---

## Architecture: Three Layers

```
wiki/
├── SCHEMA.md           # Conventions, structure rules, domain config
├── index.md            # Sectioned content catalog with one-line summaries
├── log.md              # Chronological action log (append-only, rotated yearly)
├── raw/                # Layer 1: Immutable source material
│   ├── articles/       # Web articles, clippings
│   ├── papers/         # PDFs, arxiv papers
│   ├── transcripts/    # Meeting notes, interviews
│   └── assets/         # Images, diagrams referenced by sources
├── entities/           # Layer 2: Entity pages (people, orgs, products, models)
├── concepts/           # Layer 2: Concept/topic pages
├── comparisons/        # Layer 2: Side-by-side analyses
└── queries/            # Layer 2: Filed query results worth keeping
```

**Layer 1 — Raw Sources:** Immutable. The agent reads but never modifies these.
**Layer 2 — The Wiki:** Agent-owned markdown files. Created, updated, and
cross-referenced by the agent.
**Layer 3 — The Schema:** `SCHEMA.md` defines structure, conventions, and tag taxonomy.

---

## Initializing a New Wiki

When the user asks to create or start a wiki:

1. Determine the wiki path — read `~/.claude/wiki-root.md` (the registry) to find an existing wiki the user wants to extend, or ask the user for a new path and a label. If creating a new wiki, append a `WIKI_ROOT_<label>=<absolute-path>` line to the registry so future operations can find it.
2. Create the directory structure (see Architecture above)
3. Ask the user what domain the wiki covers — be specific
4. Write `SCHEMA.md` customized to the domain
5. Write initial `index.md` with sectioned header
6. Write initial `log.md` with creation entry
7. Confirm the wiki is ready and suggest first sources to ingest

---

## SCHEMA.md Template

Adapt to the user's domain. The schema constrains agent behavior and ensures consistency:

```markdown
# Wiki Schema

## Domain
[What this wiki covers — e.g., "AI/ML research", "personal health", "startup intelligence"]

## Conventions
- File names: lowercase, hyphens, no spaces (e.g., `transformer-architecture.md`)
- Every wiki page starts with YAML frontmatter (see below)
- Use `[[wikilinks]]` to link between pages (minimum 2 outbound links per page)
- When updating a page, always bump the `updated` date
- Every new page must be added to `index.md` under the correct section
- Every action must be appended to `log.md`
- **Provenance markers:** On pages that synthesize 3+ sources, append `^[raw/articles/source-file.md]`
  at the end of paragraphs whose claims come from a specific source.

## Frontmatter
```yaml
---
title: Page Title
created: YYYY-MM-DD
updated: YYYY-MM-DD
type: entity | concept | comparison | query | summary
tags: [from taxonomy below]
sources: [raw/articles/source-name.md]
confidence: high | medium | low        # optional
contested: true                        # set when the page has unresolved contradictions
contradictions: [other-page-slug]      # pages this one conflicts with
---
```

`confidence` and `contested` are optional but recommended. Lint surfaces weak claims.

### raw/ Frontmatter

Raw sources also get a small frontmatter block so re-ingests can detect drift:

```yaml
---
source_url: https://example.com/article
ingested: YYYY-MM-DD
---

The `ingested` date is the load-bearing fact. It is the version identifier for
the raw archive. A re-ingest that finds an existing `raw/<name>.md` with a recent
`ingested` date can skip re-processing the source (the schema, tags, and
cross-references all need re-validation regardless of whether the bytes changed).
A re-ingest of a `raw/<name>.md` whose `ingested` date is older than the
SCHEMA.md stale threshold should re-fetch the source and re-validate.

---

## Tag Taxonomy
[Define 10-20 top-level tags for the domain. Add new tags here BEFORE using them.]

Example for AI/ML:
- Models: model, architecture, benchmark, training
- People/Orgs: person, company, lab, open-source
- Techniques: optimization, fine-tuning, inference, alignment, data
- Meta: comparison, timeline, controversy, prediction

Rule: every tag on a page must appear in this taxonomy. Add new tags to SCHEMA.md first.

---

## Page Thresholds
- **Create a page** when an entity/concept appears in 2+ sources OR is central to one source
- **Add to existing page** when a source mentions something already covered
- **DON'T create a page** for passing mentions, minor details, or things outside the domain
- **Split a page** when it exceeds ~200 lines — break into sub-topics with cross-links
- **Archive a page** when its content is fully superseded — move to `_archive/`, remove from index

---

## Entity Pages
One page per notable entity. Include:
- Overview / what it is
- Key facts and dates
- Relationships to other entities ([[wikilinks]])
- Source references

## Concept Pages
One page per concept or topic. Include:
- Definition / explanation
- Current state of knowledge
- Open questions or debates
- Related concepts ([[wikilinks]])

## Comparison Pages
Side-by-side analyses. Include:
- What is being compared and why
- Dimensions of comparison (table format preferred)
- Verdict or synthesis
- Sources

---

## Update Policy
When new information conflicts with existing content:
1. Check the dates — newer sources generally supersede older ones
2. If genuinely contradictory, note both positions with dates and sources
3. Mark the contradiction in frontmatter: `contradictions: [page-name]`
4. Flag for user review in the lint report

---

## index.md Template

```markdown
# Wiki Index

> Content catalog. Every wiki page listed under its type with a one-line summary.
> Read this first to find relevant pages for any query.
> Last updated: YYYY-MM-DD | Total pages: N

## Entities
<!-- Alphabetical within section -->

## Concepts

## Comparisons

## Queries
```

**Scaling rule:** When any section exceeds 50 entries, split into sub-sections.
When the index exceeds 200 entries total, create `_meta/topic-map.md`.

---

## log.md Template

```markdown
# Wiki Log

> Chronological record of all wiki actions. Append-only.
> Format: `## [YYYY-MM-DD] action | subject`
> Actions: ingest, update, query, lint, create, archive, delete
> When this file exceeds 500 entries, rotate: rename to log-YYYY.md, start fresh.

## [YYYY-MM-DD] create | Wiki initialized
- Domain: [domain]
- Structure created with SCHEMA.md, index.md, log.md
```

---

## Ingest Operation

When the user provides a source (URL, file, paste), integrate it into the wiki:

① **Capture the raw source:**
   - URL → fetch as markdown, save to `raw/articles/`
   - PDF → fetch as markdown, save to `raw/papers/`
   - Pasted text → save to appropriate `raw/` subdirectory
   - Name the file descriptively: `raw/articles/source-title-2026.md`
   - **Add raw frontmatter** (`source_url`, `ingested`).
     On re-ingest: compare the new source's `Last-Modified` (or fetch time) to
     the existing `ingested` date. If newer, re-process. If older or same, skip
     re-processing of the raw archive (the schema, tags, and cross-references
     may still need re-validation per the lint Check F stale threshold).

② **Discuss takeaways** with the user — what's interesting for the domain.
   (Skip in automated/cron contexts.)

③ **Check what already exists** — search index.md and grep for existing pages
   on mentioned entities/concepts.

④ **Write or update wiki pages:**
   - **New entities/concepts:** Create only if they meet Page Thresholds
   - **Existing pages:** Add new information, bump `updated` date.
     Follow the Update Policy on contradictions.
   - **Cross-reference:** Every new or updated page must link to ≥2 other pages
   - **Tags:** Only use tags from SCHEMA.md taxonomy
   - **Provenance:** On pages with 3+ sources, append `^[raw/articles/source.md]`
     markers to paragraphs tracing to a specific source.
   - **Confidence:** Set `confidence: medium` on single-source pages.

⑤ **Update navigation:**
   - Add new pages to `index.md` under the correct section
   - Update "Total pages" count and "Last updated" in index header
   - Append to `log.md`: `## [YYYY-MM-DD] ingest | Source Title`

⑥ **Report every file created or updated.**

---

## Query Operation

When the user asks a question about the wiki's domain:

① **Read `index.md`** to identify relevant pages.
② **For wikis with 100+ pages**, also grep across all `.md` files for key terms.
③ **Read the relevant pages.**
④ **Synthesize an answer.** Cite source pages: "Based on [[page-a]] and [[page-b]]..."
⑤ **File valuable answers back** — substantial comparisons or novel synthesis go
   in `queries/` or `comparisons/`. Skip trivial lookups.
⑥ **Update log.md** with the query and whether it was filed.

---

## Lint Operation

When the user asks to lint or health-check the wiki:

① **Orphan pages:** Find pages with no inbound `[[wikilinks]]` from other pages.
② **Broken wikilinks:** Find `[[links]]` that point to pages that don't exist.
③ **Index completeness:** Every wiki page should appear in `index.md`.
④ **Frontmatter validation:** Every wiki page must have title, created, updated, type, tags.
⑤ **Stale content:** Pages whose `updated` date is >90 days old.
⑥ **Contradictions:** Pages with `contested: true` or `contradictions:` frontmatter.
⑦ **Quality signals:** Pages with `confidence: low` or single-source pages without a confidence field.
⑧ **Source drift:** For each `raw/` file, check the `ingested` date against
    SCHEMA.md's stale threshold. Files older than the threshold are flagged for
    potential re-ingest. (Note: this is "drift" in the sense of "the source
    might have changed since we archived it" — a separate concept from the
    `updated:` field of a wiki page, which tracks when we last edited the
    synthesis, not the source.)
⑨ **Page size:** Flag pages over 200 lines — candidates for splitting.
⑩ **Tag audit:** List all tags in use, flag any not in the SCHEMA.md taxonomy.
⑪ **Log rotation:** If log.md exceeds 500 entries, rotate it.
⑫ **Report findings** grouped by severity (broken > orphans > drift > stale > style).
⑬ **Append to log.md:** `## [YYYY-MM-DD] lint | N issues found`

---

## Bulk Ingest

When ingesting multiple sources at once:
1. Read all sources first
2. Identify all entities and concepts across all sources
3. Check existing pages for all of them (one search pass, not N)
4. Create/update pages in one pass
5. Update index.md once at the end
6. Write a single log entry covering the full batch

---

## Archiving

When content is fully superseded:
1. Create `_archive/` directory if it doesn't exist
2. Move the page to `_archive/` with its original path
3. Remove from `index.md`
4. Update any pages that linked to it — replace wikilink with plain text + "(archived)"
5. Log the archive action

---

## Obsidian Integration

The wiki directory works as an Obsidian vault:
- `[[wikilinks]]` render as clickable links
- Graph View visualizes the knowledge network
- YAML frontmatter powers Dataview queries
- `raw/assets/` holds images referenced via `![[image.png]]`

For best results:
- Set Obsidian's attachment folder to `raw/assets/`
- Install Dataview plugin for queries like `TABLE tags FROM "entities" WHERE contains(tags, "company")`

---

## Obsidian Headless (servers)

```bash
# Requires Node.js 22+
npm install -g obsidian-headless

# Login and create remote vault
ob login --email <email> --password '<password>'
ob sync-create-remote --name "LLM Wiki"

# Connect wiki directory
cd ~/wiki
ob sync-setup --vault "<vault-id>"
ob sync --continuous
```

---

## Pitfalls

- **Always orient first** — read SCHEMA + index + recent log before ANY wiki operation
- **Never modify raw/ files** — sources are immutable. Corrections go in wiki pages only.
- **Always update index.md and log.md** — these are the navigational backbone
- **Don't create pages for passing mentions** — follow Page Thresholds
- **Don't create pages without cross-references** — every page must link to ≥2 other pages
- **Frontmatter is mandatory** — enables search, filtering, and staleness detection
- **Tags must come from the taxonomy** — freeform tags decay into noise
- **Keep pages scannable** — readable in ~30 seconds. Split pages over 200 lines.
- **Ask before mass-updating** — if an ingest would touch 10+ existing pages, confirm first
- **Handle contradictions explicitly** — note both claims, mark in frontmatter, flag for review
- **Rotate the log** — when log.md exceeds 500 entries, rename to `log-YYYY.md`
- **Trust the schema, not memory** — re-read SCHEMA.md when unsure
