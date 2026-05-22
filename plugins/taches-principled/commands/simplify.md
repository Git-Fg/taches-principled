---
name: simplify
skill: code-simplify
description: Simplify and refine recently modified code for clarity and maintainability
argument-hint: [file-pattern]
---

# simplify

Invokes the code-simplify pipeline on files matching the given pattern (default: recently modified source files).

The pipeline runs 5 stages in sequence:

1. **Discover** — Find recently changed files matching the pattern
2. **Analyze** — Detect simplification opportunities per language (early returns, dict dispatch, object lookups, etc.)
3. **Simplify** — Apply the transformations, staying within scope boundaries
4. **Verify** — Run tests and lint to confirm behavior is preserved
5. **Report** — Summarize what changed and what was left alone

Scope defaults to Tight (single function) or File. Escalate only for purely mechanical cross-file changes. See the simplification-scope reference for level definitions, stop conditions, and the pre-start contract.

Usage: `/simplify [file-pattern]`
