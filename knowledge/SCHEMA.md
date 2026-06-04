# Wiki Format Conventions

## Directory Structure
wiki/
├── SCHEMA.md              # Wiki constitution — conventions, tag taxonomy, page thresholds
├── index.md              # Sectioned content catalog
├── log.md                # Chronological action log (append-only)
├── raw/                  # Layer 1: Immutable source material
│   ├── articles/
│   ├── papers/
│   ├── transcripts/
│   └── assets/
├── entities/             # Layer 2: People, orgs, products
├── concepts/             # Layer 2: Topics, techniques, ideas
├── comparisons/           # Layer 2: Side-by-side analyses
└── queries/              # Layer 2: Filed query results worth keeping

## Frontmatter (required on every wiki page)
---
title: Page Title
created: YYYY-MM-DD
updated: YYYY-MM-DD
type: entity | concept | comparison | query | summary
tags: [from taxonomy below]
sources: [raw/articles/source.md]
confidence: high | medium | low   # optional
contested: true                   # optional
contradictions: [other-page-slug]  # optional
---

## Wikilinks
- Use `[[pagename]]` to link between pages
- Minimum 2 outbound links per page
- Orphan pages (no inbound links) are flagged by wiki-linter

## Tag Rules
- Every tag on a page must appear in the taxonomy in SCHEMA.md
- New tags: add to SCHEMA.md first, then use
- Tag audit is part of wiki-linter verification

## Provenance
On pages synthesizing 3+ sources, append `^[raw/articles/source.md]` to paragraphs
whose claims trace to a specific source.

## Page Size
- Target: readable in ~30 seconds (~150-200 lines max)
- Split pages over 200 lines into sub-topics with cross-links