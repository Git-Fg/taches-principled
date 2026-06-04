# Intent File Format

The intent file (`$WIKI_ROOT/.wiki/intent.md`) is a plain-text document
describing what the wiki should contain and how it should be maintained.

## Format Rules
- One statement per line
- Blank lines are ignored
- Lines starting with `#` are comments
- No structured syntax — plain English only

## Examples
```
Every entry should have a last-reviewed date
No orphan entries (all pages must have at least one inbound wikilink)
All entries in AI/ must have tags
No page should be older than 6 months without a review
Every comparison page must cite at least 2 sources
```

## How wiki-linter Uses It
1. wiki-linter reads `.wiki/intent.md` on each run
2. Parses each non-comment, non-blank line as an intent statement
3. Evaluates the wiki against each statement
4. Reports gaps — pages that violate or don't satisfy an intent
5. Auto-fixes safe violations (e.g., missing tags, orphan detection)
6. Flags structural violations for manual review

## Creating an Intent File
The user (or wiki-linter) can create `.wiki/intent.md` at the wiki root.
wiki-linter will detect it and incorporate it into verification automatically.