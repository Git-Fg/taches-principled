# Simplification Scope

> Scope boundaries, stop conditions, and the pre-start contract.

---

## Scope Levels

| Level | Range | Typical Changes | Review Required |
|-------|-------|-----------------|-----------------|
| **Tight** | Single function | Inline variable, extract helper, flatten control flow | None |
| **File** | One file | Rename symbols, reorder methods, consolidate imports | Self-review |
| **Bounded** | 2-5 related files | Extract shared logic, align interfaces, deduplicate across modules | Peer review |
| **Sweep** | Package / module | Consistent patterns across module (e.g. all error handling to early return) | PR review |
| **Repo-wide** | Multiple packages | Breaking change to internal API, renaming a public symbol, changing a shared pattern | PR review + stakeholder notification |

**Default scope:** Tight or File. Escalate only when the simplification is impossible within a single file and the cross-file change is purely mechanical (rename, extract, inline).

---

## When to Stop

Stop simplifying when any of these are true:

| Condition | Example |
|-----------|---------|
| **Logic changes** | Extracting a helper changes evaluation order or side effects |
| **Tests need updates beyond renames** | Changing a function signature that's tested by name |
| **Public API surface** | A function is exported/exported and consumed by other packages |
| **Performance cliff** | Replacing a loop with a comprehension that doubles memory |
| **Readability unchanged** | The simplified form is as long or longer than the original |
| **Third-party boundary** | A dependency's return type or error shape dictates the pattern |

---

## File Classification

### Simplify freely (no approval needed)

- Source files in packages you own
- Test files (collateral cleanup from source changes)
- Configuration files (remove dead keys, normalize format)

### Flag for awareness (mention in output)

- Files with `TODO`, `FIXME`, or `HACK` comments — simplify around them but don't touch the debt
- Files that have open git modifications (uncommitted changes) — avoid conflicts
- Generated files with a `@generated` or `do not edit` header — skip entirely

### Never simplify

- Vendor / `node_modules` / `.venv` / `third_party/`
- Lockfiles and manifest files (`package-lock.json`, `go.sum`, `Cargo.lock`)
- Database migrations (order and content are historical records)
- Public API surface of published packages
- Files outside the project root
- Files with CI/CD configuration that has implicit structure (e.g. YAML anchors, templated values)

---

## The Simplification Contract

Before starting, answer these 3 questions:

1. **What pattern am I removing?** (e.g. "nested if/else around error handling")
2. **What pattern am I replacing it with?** (e.g. "flat early returns")
3. **How will I verify the behavior is preserved?** (e.g. "run the existing test suite for this file")

If you cannot answer all 3 clearly, do not start — the change is not yet well-understood enough to simplify safely.
