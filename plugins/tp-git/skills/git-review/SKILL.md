---
name: git-review
description: "Add line-specific review comments on pull requests — single comments and batched multi-file reviews."
when_to_use: "Use when the user says 'review PR', 'inline comment', 'add comment to PR', 'comment on PR', 'review comment', 'leave feedback on PR', or 'GitHub review'. IMMEDIATELY when the user asks to 'add a comment on line X', 'review this pull request', 'post review comments', or 'add inline feedback'. BEFORE merging any PR — use when the user wants to provide specific line-by-line feedback."
---

## Decision Router

IF a single comment on one line is needed → use the single comment endpoint with the commit SHA
IF multiple comments across files are needed → batch them as one review via the reviews endpoint
IF a pending review already exists for this user → submit it first, or use individual comments
IF MCP inline comment tools are available → prefer them over the gh API

# Git Review

Place line-specific comments on pull request diffs. Supports individual comments and batched multi-file reviews. Use MCP inline comment tools when available; fall back to the GitHub REST API via `gh api`.

## Core Principle

Every inline comment must reference a specific line, file, and commit. Group related comments into a single review to reduce notification noise.

## Quick Reference

| Goal | Method |
|------|--------|
| Single inline comment | `gh api repos/{owner}/{repo}/pulls/{pr}/comments -f body='...' -f commit_id='<sha>' -f path='<file>' -F line=<n> -f side='RIGHT'` |
| Multi-comment review | `echo '{ "event": "COMMENT", "body": "...", "comments": [...] }' \| gh api repos/{owner}/{repo}/pulls/{pr}/reviews --input -` |
| Get latest commit SHA | `gh api repos/{owner}/{repo}/pulls/{pr} --jq '.head.sha'` |
| List changed files | `gh api repos/{owner}/{repo}/pulls/{pr}/files --jq '.[] \| {filename, additions, deletions}'` |

## Process

1. Gather PR info: latest commit SHA and list of changed files
2. Review the diff to identify specific lines needing comments
3. Choose method — single comment or batch review — and post

### Single Comment

```bash
gh api repos/{owner}/{repo}/pulls/{pr}/comments \
  -f body='Your observation or suggestion' \
  -f commit_id='<sha>' \
  -f path='path/to/file.ts' \
  -F line=<line-number> \
  -f side='RIGHT'
```

For multi-line comments, add `-F start_line=<start>` and `-f start_side='RIGHT'`.

### Batch Review

```bash
echo '{
  "event": "COMMENT",
  "body": "Overall review summary (optional)",
  "comments": [
    {"path": "file1.ts", "body": "Comment", "side": "RIGHT", "line": 15},
    {"path": "file2.ts", "body": "Comment", "side": "RIGHT", "line": 30}
  ]
}' | gh api repos/{owner}/{repo}/pulls/{pr}/reviews --input -
```

Review events: `COMMENT` (feedback), `APPROVE` (approve), `REQUEST_CHANGES` (block).

## Common Issues

| Issue | Cause | Fix |
|-------|-------|-----|
| `user_id can only have one pending review` | Existing unsubmitted review blocks new ones | Submit pending review, or use individual comment endpoint |
| `line must be part of the diff` | Line number not in the diff | Verify line in the "Files changed" tab |
| `commit_sha is not part of the pull request` | Wrong commit SHA | Get `.head.sha` from PR: `gh api .../pulls/{pr} --jq '.head.sha'` |

## Output

- GitHub review comments posted to the PR
- Single comments appear as individual discussion threads
- Batch reviews appear as one grouped review block

## Design Decisions

### Why batch reviews over individual comments

A single review with multiple comments generates one notification instead of N. This matches the GitHub UI behavior of "Start a review" followed by "Finish review" for coherent review sessions.

### Relationship to development pipeline

Operates during the review stage. Consumes diffs from open PRs and produces inline feedback that the PR author addresses.
