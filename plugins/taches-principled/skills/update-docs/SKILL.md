---
name: update-docs
description: Update project documentation after code changes — READMEs, guides, API docs, and JSDoc. Preserves existing style and follows project conventions.
when_to_use: |
  Use when the user says:
  - "update the docs"
  - "document this"
  - "write documentation for this"
  - "the docs need updating"
  - "update documentation for these changes"
  - "doc this code change"
  - "add docs for the new feature"
  - "write the README updates"
  - "document the API changes"
  - "refresh the documentation"
  IMMEDIATELY after code changes affecting user-facing APIs or workflows, BEFORE committing.
argument-hint: "Optional: documentation type or area (api, guides, readme, jsdoc)"
---

## Decision Router

IF code changes affect user-facing APIs or workflows → Update documentation for those changes
IF 1-2 files with simple changes → Write documentation directly (no agents needed)
IF 3+ files or significant changes → Use multi-agent workflow with analysis + tech-writer + review agents
IF change introduces a new module or feature → Ensure index documents are updated (README, docs/index)
IF no uncommitted changes exist → Cover the latest commit

# Update Documentation

Ensure all code changes are properly documented with clear, maintainable documentation that helps users accomplish real tasks. Preserve existing documentation style — follow established patterns.

Not every code change needs documentation. Focus on user-facing impact.

## Workflow

### Preparation

1. **Read project config** (package.json, pyproject.toml) and root README.md to understand the project.
2. **Discover documentation infrastructure**: docs/ structure, README files, JSDoc patterns, doc generation tools (OpenAPI, JSDoc, TypeDoc).
3. **Inventory existing docs**:

```bash
find . -name "*.md" | grep -E "(README|CHANGELOG|CONTRIBUTING|docs/)"
find . -name "openapi.*" -o -name "*.graphql" -o -name "swagger.*"
```

### Analysis (parallel Haiku agents)

4. **Map documentation structure**: docs/ folder layout, all README files, API docs, JSDoc patterns.
5. **Analyze code changes**: Run `git status -u` (or `git show --name-status` for latest commit). Filter changes that impact documentation:
   - New/modified public APIs
   - Changed module structures
   - Updated configuration options
   - New features or workflows
   Launch parallel agents per changed file to identify documentation impact and index document needs.

### Documentation Planning

6. **Group changes by documentation area**:
   - **API Documentation**: All API changes
   - **Module READMEs**: Changes in same module
   - **User Guides**: Related feature changes
   - **JSDoc**: Complex logic changes
   - **Index Documents**: Navigation and discovery docs

**Index documents to check**:

| Document | Update When |
|----------|-------------|
| Root README.md | Features, modules, or overview changes |
| Module README.md | Module exports or purpose changes |
| docs/index.md | Docs structure changes |
| SUMMARY.md / _sidebar.md | Navigation structure changes |
| mkdocs.yml nav | Navigation changes |

### Documentation Writing

**Simple changes (1-2 files):** Write documentation directly. Follow project conventions, include working examples, avoid duplication.

**Multi-agent flow (3+ files or significant changes):**

7. **Launch doc-analysis agents** (Haiku, parallel) — one per documentation area. Each produces a prioritized list of documentation tasks (CRITICAL: breaking changes / IMPORTANT: new features / NICE_TO_HAVE: clarifications).

8. **Launch tech-writer subagents** (Sonnet or Opus, parallel) — one per documentation area. Provide them with: documentation requirements, target files, project conventions, and existing docs for style reference. Create/update documentation.

9. **Launch quality review agents** (Sonnet or Opus, parallel) — verify: all user-facing changes covered, code examples accurate, links valid, follows conventions, no bloat.

10. **Iterate** if needed — re-launch tech-writer agents only for areas with gaps.

11. **Final verification** — cross-references work, no conflicting information, documentation is navigable.

## Core Documentation Philosophy

**Documentation must justify its existence.** For every document ask: does it help users accomplish real tasks? Is it discoverable? Will it be maintained? Does it duplicate existing docs?

### What to Document
- Getting started (quick setup, first success in <5 minutes)
- How-to guides (task-oriented, problem-solving)
- API references (when manual adds value over generated)
- Troubleshooting (real problems with proven solutions)
- Complex business logic JSDoc

### What NOT to Document
- API docs duplicating generated schema docs
- Code comments explaining what code obviously does
- Process documentation for processes that don't exist
- Changelogs duplicating git history
- Documentation of temporary workarounds

## Quality Gates

**Before finishing:**
- [ ] All user-facing changes documented
- [ ] Code examples tested and working
- [ ] Links verified (no 404s)
- [ ] Documentation follows project conventions
- [ ] No duplication of generated docs
- [ ] Index documents link to new content

## Agent Instruction Templates

### Documentation Analysis Agent (Haiku)

```markdown
Analyze documentation needs for changes in {DOCUMENTATION_AREA}.

Context: These files were modified:
{CHANGED_FILES_LIST}

Git diff summary:
{GIT_DIFF_SUMMARY}

Your task:
1. Review the changes and understand their documentation impact
2. Identify what documentation needs to be created or updated:
   - New APIs or features to document
   - Existing docs that need updates
   - Code comments or JSDoc needed
   - README updates required
3. Identify index documents requiring updates:
   - Module README.md files affected by changes
   - Root README.md if features or modules changed
   - docs/ index files (index.md, SUMMARY.md, guides.md, getting-started.md)
   - Navigation files (_sidebar.md, mkdocs.yml nav section)
4. Check existing documentation to avoid duplication
5. Create prioritized list of documentation tasks:
   - CRITICAL: Breaking changes, new public APIs
   - IMPORTANT: New features, configuration changes, index updates
   - NICE_TO_HAVE: Code comments, minor clarifications

Output: List of documentation tasks with priorities, file locations, and index documents to update.
```

### Tech Writer Agent (Documentation Creation)

```markdown
Create/update documentation for {DOCUMENTATION_AREA}.

Documentation requirements identified:
{DOCUMENTATION_TASKS_LIST}

Your task:
1. Read the changed files and understand the impact
2. Read @README.md for project context and conventions
3. Review existing documentation for style and patterns
4. Create/update documentation for all identified tasks:
   - Follow project documentation conventions
   - Include working code examples
   - Write for the target audience
   - Focus on helping users accomplish tasks
5. Ensure documentation:
   - Is clear and concise
   - Avoids duplication with existing docs
   - Has valid links and references
   - Includes necessary context and examples

Target files: {TARGET_DOCUMENTATION_FILES}
```

### Quality Review Agent (Verification)

```markdown
Review documentation quality for {DOCUMENTATION_AREA}.

Context: Documentation was created/updated for local code changes.

Files to review:
{DOCUMENTATION_FILES}

Your task:
1. Read the documentation created/updated
2. Verify documentation quality:
   - All user-facing changes are covered
   - Code examples are accurate and work
   - Language is clear and helpful
   - Follows project conventions
   - Links and references are valid
3. Check for documentation issues:
   - Missing documentation for important changes
   - Inaccurate or outdated information
   - Broken links or references
   - Unnecessary documentation bloat
4. Verify no conflicts with existing documentation

Output: PASS confirmation or list of issues to fix.
```

## Documentation Patterns Reference

### README.md Best Practices

**Project Root README:**

```markdown
# Project Name

Brief description (1-2 sentences max).

## Quick Start
[Fastest path to success - must work in <5 minutes]

## Documentation
- [API Reference](./docs/api/) - if complex APIs
- [Guides](./docs/guides/) - if complex workflows
- [Contributing](./CONTRIBUTING.md) - if accepting contributions

## Status
[Current state, known limitations]
```

**Module README Pattern:**

```markdown
# Module Name

**Purpose**: One sentence describing why this module exists.

**Key exports**: Primary functions/classes users need.

**Usage**: One minimal example.

See: [Main documentation](../../README.md) for detailed guides.
```

### JSDoc Best Practices

**Document These:**

```typescript
/**
 * Processes payment with retry logic and fraud detection.
 *
 * @param payment - Payment details including amount and method
 * @param options - Configuration for retries and validation
 * @returns Promise resolving to transaction result with ID
 * @throws PaymentError when payment fails after retries
 *
 * @example
 * ```typescript
 * const result = await processPayment({
 *   amount: 100,
 *   currency: 'USD',
 *   method: 'card'
 * });
 * ```
 */
async function processPayment(payment: PaymentRequest, options?: PaymentOptions): Promise<PaymentResult>
```

**Don't Document These:**

```typescript
// Obvious functionality
getName(): string

// Simple CRUD
save(user: User): Promise<void>

// Self-explanatory utilities
toLowerCase(str: string): string
```

### When to Generate vs Write

**Use Automated Generation For:**
- OpenAPI/Swagger: REST API reference, request/response examples
- GraphQL Schema: Type definitions and queries
- JSDoc: Function signatures and basic parameter docs
- Database Schemas: Prisma, TypeORM, Sequelize models

**Write Manual Documentation For:**
- Integration examples: Real-world usage patterns
- Business logic explanations: Why decisions were made
- Troubleshooting guides: Solutions to actual problems
- Getting started workflows: Curated happy paths

## Index Document Update Checklist

When documentation changes affect a module or feature:

| Document | Update When |
|----------|-------------|
| `README.md` (root) | New features, modules, or overview changes |
| `README.md` (module) | Module exports, purpose, or usage changes |
| `docs/index.md` | New documentation pages or structure changes |
| `getting-started.md` | Setup steps or quickstart changes |
| `guides.md` | New guides or guide categories |
| `reference.md` | New API references or structure |
| `SUMMARY.md` | Documentation structure changes (GitBook) |
| `_sidebar.md` | Navigation structure changes (Docsify) |
| `mkdocs.yml` nav | Documentation navigation changes (MkDocs) |

**Example: Adding a New Feature**

```text
Files to update:
├── src/reporting/README.md      → Add to key exports
├── docs/guides/index.md         → Link to new guide
├── docs/guides/exporting.md     → Create new guide
├── docs/reference/index.md      → Link to API reference
├── README.md                    → Mention in features list
└── SUMMARY.md                   → Add navigation entries
```

## Output

Report of documentation updates completed:

```markdown
## Documentation Updates

### Files Updated
- [ ] Root README.md
- [ ] Module README files
- [ ] docs/ content files
- [ ] JSDoc comments

### Index Documents Updated
- [ ] Root README.md
- [ ] docs/index.md / SUMMARY.md
- [ ] Module README files

### Changes Documented
- [List of changes covered]

### Quality Review
- [ ] All criteria passed
```

## Design Decisions

### Why multi-agent for docs
Analysis, writing, and review require different expertise and perspective. Parallel agents with distinct focuses produce more complete documentation coverage.

### Why index document checklist
Index documents (READMEs, docs/index, navigation) are the most commonly missed update — they connect users to content. Explicitly checking them prevents orphaned documentation.

### Why simple change shortcut
For 1-2 file changes, the overhead of spawning agents exceeds the value. Direct writing is faster and equally effective.

### Why documentation hierarchy
Not all docs are equal. The CRITICAL/IMPORTANT/NICE_TO_HAVE triage ensures effort goes where it matters most — breaking changes and new APIs before polish.

### Relationship to development pipeline
- Operates after code changes are made but before commit
- Complements code review by ensuring documentation quality
- Produces documentation updates ready for commit alongside code

After drafting documentation updates, spawn a self-review subagent if you have access to one — it verifies completeness, accuracy, and coverage of all doc targets before commit. For critical documentation (public API docs, migration guides), spawn a self-critic subagent as well to stress-test for blind spots and unstated assumptions.
