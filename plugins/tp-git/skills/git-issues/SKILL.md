---
name: git-issues
description: Load all open issues from GitHub and create structured technical specifications for implementation
argument-hint: fetch | analyze <number>
---

## Decision Router

IF loading all open issues → fetch from GitHub CLI, save to specs/issues/
IF analyzing a specific issue → locate or fetch it, then produce a spec document
IF repository has no open issues → report empty state
IF issue file is missing locally → fetch from GitHub first
IF issue is a bug fix → emphasize test plan and reproduction steps in the spec
IF issue is a feature → emphasize technical approach and implementation plan in the spec
IF gh CLI is unavailable → report error and suggest installation

# Git Issues

Fetch all open issues from the current GitHub repository and write each as a structured markdown file. Take any issue (by number) and produce a detailed technical specification. Both workflows use `gh` CLI and the `./specs/issues/` directory.

## Core Principle

One file per issue, consistently formatted. A specification is a contract between problem and solution — precise enough to implement without ambiguity, concise enough to review in one pass.

## Process

### Load Issues

1. List all open issues: `gh issue list --limit 100`
2. For each issue, fetch full details:

   ```bash
   gh issue view <number> --json number,title,body,state,createdAt,updatedAt,author,labels,assignees,url
   ```

3. Create output directory: `mkdir -p ./specs/issues`
4. Save each issue as `<number-padded-to-3-digits>-<kebab-case-title>.md`

#### Issue File Template

```markdown
# Issue #<number>: <title>

**Status:** <state>
**Created:** <createdAt>
**Updated:** <updatedAt>
**Author:** <author.name> (@<author.login>)
**URL:** <url>

## Description

<body>

## Labels

<labels or "None">

## Assignees

<assignees or "None">
```

5. Report summary: total issues loaded, list of created files

### Analyze Issue

1. Locate or fetch the issue:
   - Check `./specs/issues/` for a matching `<NNN>-<title>.md` file
   - If missing, fetch with `gh issue view <number>` and save to that path
2. Read the issue and understand requirements thoroughly
3. Review related code and project structure for context
4. Create technical specification using the format below
5. Save to `./specs/issues/<NNN>-<kebab-case-title>.specs.md`

#### Specification Template

```markdown
# Technical Specification for Issue #<number>

## Issue Summary
- Title, Description, Labels, Priority assessment

## Problem Statement
[1-2 paragraphs]

## Technical Approach
[Detailed approach with rationale]

## Implementation Plan
1. Step one
2. Step two

## Test Plan
- Unit tests
- Integration tests

## Files to Modify
- path: changes needed

## Files to Create
- path: purpose

## Success Criteria
- [ ] Measurable condition

## Out of Scope
- What this spec explicitly excludes
```

## Output

- `./specs/issues/<NNN>-<title>.md` — one file per open issue (load)
- `./specs/issues/<NNN>-<title>.specs.md` — specification document (analyze)
- Summary printed to conversation

## Design Decisions

### Why separate analysis before implementation

Separating analysis from implementation prevents premature commitment to an approach. The spec serves as a reviewable artifact before any code is written.

### Relationship to development pipeline

Produces specification documents consumed by downstream implementation processes. The Implementation Plan and Files to Modify sections drive task sequencing.
