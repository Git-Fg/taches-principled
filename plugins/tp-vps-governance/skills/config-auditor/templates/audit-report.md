# Config Audit Report

**Generated:** {timestamp}
**Scope:** {root_path}
**Files scanned:** {file_count}
**Total lines:** {line_count}
**Total tokens:** ~{token_count}

---

## Hierarchy Map

```
{hierarchy_tree}
```

---

## Critical Issues

| # | Type | Files | Description | Suggested Action |
|---|------|-------|-------------|-----------------|
| {issues} |

---

## Warnings

| # | Type | Files | Description | Token Waste |
|---|------|-------|-------------|-------------|
| {warnings} |

---

## Optimization Opportunities

| Priority | Action | From → To | Token Savings |
|----------|--------|-----------|---------------|
| {opportunities} |

---

## Recommendations

1. **Critical**: Fix conflicts first — contradictory rules cause unpredictable agent behavior
2. **High**: Consolidate duplicated rules to single source of truth
3. **Medium**: Add path: frontmatter to project-specific rules
4. **Low**: Split large rule files into domain-specific files with path scoping

**Total potential token savings:** ~{savings} ({percentage}%)