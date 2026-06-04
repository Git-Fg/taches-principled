> ## Documentation Index
> Fetch the complete documentation index at: https://code.claude.com/docs/llms.txt
> Use this file to discover all available pages before exploring further.

# Rules

> Reference for writing, organizing, and maintaining Claude Code instruction rules
> (`.claude/rules/*.md`, `~/.claude/rules/*.md`, and the CLAUDE.md hierarchy that surrounds them).

Rules are the durable, advisory layer of Claude Code's instruction system. They shape
how the model behaves across sessions without being tied to a specific task, a
specific tool, or a specific lifecycle event. A rule loads once at the start of
the session (or on demand when path-scoped), and it stays in context as long as
the conversation is alive. This page is the canonical maintainer reference for
writing rules that load predictably, stay terse, and survive iteration.

<Note>
  Rules are advisory context, not enforced configuration. A PreToolUse hook, a
  `permissions.deny` rule, or a sandboxed Bash tool will block an action no
  matter what Claude decides. A rule can only *ask* Claude to do the right
  thing. If the rule must run, use a hook instead.
</Note>

## When to use a rule

The Claude Code instruction system has four overlapping layers. Use this
decision tree to pick the right one:

| Layer                | File location                                | When to use it                                                                                                            |
| :------------------- | :------------------------------------------- | :------------------------------------------------------------------------------------------------------------------------ |
| **CLAUDE.md**        | `CLAUDE.md`, `~/.claude/CLAUDE.md`           | Project facts, build commands, coding standards, and team-shared conventions that apply to every session in the repo.    |
| **Rules**            | `.claude/rules/*.md`, `~/.claude/rules/*.md` | Topic-focused or path-scoped instructions you want to keep modular: API design rules, frontend conventions, test policies. |
| **Skills**           | `.claude/skills/<name>/SKILL.md`             | A procedure or multi-step workflow that should load only when the task matches it (lazy, content-aware).                  |
| **Hooks**            | `settings.json` → `hooks`                    | Hard enforcement at a lifecycle event: format on save, block `rm -rf`, prepend a checklist before every commit.           |
| **Auto memory**      | `~/.claude/projects/<repo>/memory/MEMORY.md` | Patterns Claude discovers itself and reuses in future sessions (build commands, debugging insights, preferences).        |

**Move a rule into a skill** when it has grown into a procedure with decision
points. **Move a rule into a hook** when it must happen on every matching event
regardless of what the model decides. **Move a rule into auto memory** when
Claude should be the author (it learned the convention, not you).

## Overview

A rule is a single markdown file with optional YAML frontmatter. The frontmatter
controls how the file is discovered and when it loads; the body is the
instruction itself. Rules are not functions and not scripts — they are
*context that gets read on your behalf*.

```text theme={null}
your-project/
├── CLAUDE.md                  # Project facts, in every session
└── .claude/
    ├── CLAUDE.md              # Modular alternative to root CLAUDE.md
    └── rules/
        ├── code-style.md      # Always-on rule
        ├── testing.md         # Always-on rule
        ├── api-design.md      # Path-scoped rule
        └── frontend/
            └── react.md       # Path-scoped rule under a subdirectory
```

**Always-on rules** load at session start. **Path-scoped rules** load when
Claude reads or edits a file that matches the `paths` glob. Both kinds live
side by side in the same `.claude/rules/` directory; the frontmatter is the
only thing that distinguishes them.

---

## Writing Rules

### File shape

The minimum viable rule is a markdown file. Frontmatter is optional but
recommended for any rule that scopes to a path or that you might grep for
later.

```markdown theme={null}
---
paths:
  - "src/api/**/*.ts"
---

# API Development Rules

- All API endpoints must validate input with a Zod schema
- Use the standard error response format from `src/lib/errors.ts`
- Include an OpenAPI summary in the route handler's JSDoc
```

Save the file under `.claude/rules/` (project) or `~/.claude/rules/` (user).
Restart the session to pick up changes — frontmatter changes are not
re-evaluated mid-session.

### Frontmatter reference

| Field          | Type                                       | Effect                                                                                  |
| :------------- | :----------------------------------------- | :-------------------------------------------------------------------------------------- |
| `paths`        | `string[]` of glob patterns                | Limits the rule to files matching the patterns. Omit for an always-on rule.             |
| `description`  | `string`                                   | Optional human label; not used for routing (rules are not skills).                      |
| `globs`        | `string[]`                                 | Legacy alias for `paths`. Prefer `paths` in new rules.                                 |
| `name`         | `string`                                   | Optional human label. Not used for routing.                                             |
| `type`         | `string`                                   | Convention metadata (`meta`, `domain`, `policy`). Ignored by Claude Code.                |
| `scope`        | `string`                                   | Convention metadata (`global`, `project`). Ignored by Claude Code.                      |

Rules do not have a `user-invocable` field, no `when_to_use`, no `model`, and
no `allowed-tools`. Those belong to skills and agents. Treat rules as plain
context.

### Content organization

A good rule reads like a page from a team handbook, not like a script. The
sections below are the most useful patterns.

**Lead with intent.** Open with one or two sentences explaining *why* the rule
exists. The model reasons better when it knows the purpose, not just the
procedure.

```markdown theme={null}
# Database migrations

Migrations are append-only. We never edit a migration after it has been
applied to any environment, including a developer's local database. The
purpose of this rule is to make rollback safe and to keep the audit trail
honest.
```

**Group related instructions under named headers.** Use second-level
headings (`## Migrations`, `## Seeding`) so the model can scan for the
section it needs.

**Prefer bullet lists to prose.** One bullet per instruction. The model is
more reliable at following a list than a paragraph of mixed obligations.

**Distinguish MUST from SHOULD in the wording.** The first line of a rule
that *requires* a behavior should say so. Soft language ("consider",
"preferably") reads as optional to the model.

**Close with a verifiable example.** A short, complete example — the kind
that fits in five lines — is worth more than three paragraphs of explanation.

### Language and tone

The strength of the language in a rule determines how reliably the model
follows it. Choose deliberately.

| Strength   | Words to use                                              | When to use it                                                |
| :--------- | :-------------------------------------------------------- | :------------------------------------------------------------ |
| Mandatory  | `MUST`, `NEVER`, `ALWAYS`, `REQUIRED`                     | Invariants. Breaking the rule is a bug.                       |
| Strong     | `do not`, `do`, `use X instead of Y`                     | Defaults. The rule is correct unless the user explicitly says otherwise. |
| Soft       | `consider`, `prefer`, `typically`                         | Style preferences. The model should follow them but can deviate when justified. |

**Test:** if removing the rule would produce visibly wrong output, use
mandatory language. If the rule is a stylistic preference that the model can
reason about from context, use soft language. Anti-pattern: "you can also"
or "feel free to" inside a rule — both signal optionality where the rule
itself is non-optional.

### Common anti-patterns

**Recapping tools.** A rule that says "use the Read tool to read files" wastes
context that already includes the tool's description. Only state tool behavior
when it deviates from the default (e.g., "always use ripgrep via Bash, never
the built-in Grep tool").

**Inventing conventions.** A rule that invents a project structure ("API
handlers live in `src/api/handlers/`") when the directory does not yet exist
will cause the model to misbehave. Either create the structure first or
remove the rule.

**Cross-file path references.** A rule that links to a specific skill
internal file (`skills/create-plans/references/X.md`) creates a brittle
dependency. The skill might be renamed; the link breaks. Reference skills
by name, not by file path.

**Stale rules.** A rule that contradicts the current code is worse than no
rule. Audit `.claude/rules/` when you reorganize the codebase. Move dead
rules to a `.attic/` directory or delete them.

**Drift from CLAUDE.md.** A rule that contradicts a `CLAUDE.md` in the same
repo will be picked arbitrarily. Keep them in sync; if a rule supersedes a
section of `CLAUDE.md`, cut the section.

---

## File Organization

### CLAUDE.md hierarchy

Claude Code loads CLAUDE.md files by walking up the directory tree from the
current working directory. They merge into a single context block rather than
overriding each other.

```text theme={null}
~/.claude/CLAUDE.md                     (personal — every project)
  → ~/.claude/rules/*.md                (personal rules)
  → {project}/CLAUDE.md                 (project)
  → {project}/.claude/CLAUDE.md         (alternative location)
  → {project}/.claude/rules/*.md        (project rules)
  → {project}/packages/*/CLAUDE.md      (package-level, when present)
```

Within a single directory, files are loaded in this order: `CLAUDE.md` first,
`CLAUDE.local.md` last. The "last" position is intentional — local
overrides always win when both files give different instructions.

### `.claude/rules/` structure

Rules are flat markdown files. They can live in subdirectories; subdirectories
are purely organizational and do not affect load order.

```text theme={null}
your-project/.claude/rules/
├── code-style.md
├── testing.md
├── security.md
├── api-design.md            # frontmatter: paths: src/api/**
├── frontend/
│   └── react.md             # frontmatter: paths: src/components/**
└── backend/
    └── postgres.md          # frontmatter: paths: src/db/**
```

**Symlinks are supported.** Link a shared rule into multiple projects with
`ln -s ~/shared-rules/security.md .claude/rules/security.md`. Circular
symlinks are detected and ignored.

**User-level rules.** `~/.claude/rules/*.md` applies to every project on the
machine. They load *before* project rules, so project rules have higher
priority when they conflict.

### When to use each level

| Need                                                                  | Use                                                       |
| :-------------------------------------------------------------------- | :-------------------------------------------------------- |
| "Always run `npm test` before committing"                             | Project `CLAUDE.md` (one line, every session)             |
| "API endpoints in `src/api/` must validate input with Zod"           | Path-scoped rule under `.claude/rules/api-design.md`      |
| "I always use 2-space indentation in my personal projects"            | `~/.claude/rules/code-style.md`                           |
| "When Claude makes the same mistake a second time, codify it"        | Either a rule or auto memory — prefer auto memory unless the rule needs to be deterministic |
| "A new teammate needs the build commands and directory layout"        | `CLAUDE.md` in the repo root                              |
| "I have local notes about a side project that shouldn't be committed" | `CLAUDE.local.md` (add to `.gitignore`)                    |
| "Org-wide compliance: no PII in prompts"                              | Managed CLAUDE.md in `/etc/claude-code/CLAUDE.md` (cannot be excluded) |

---

## Iteration Workflow

### Testing rule changes

Rules are context, so the way to test them is to read them in a fresh
session and observe behavior. The minimum viable test:

1. Edit the rule.
2. Start a new session in the same directory (`claude`).
3. Ask three representative questions.
4. Verify the rule's instructions show up in the model's behavior.

For a faster loop, use headless mode with the streaming output captured to
disk:

```bash theme={null}
claude -p "Refactor the user endpoint to use Zod validation" \
  --output-format stream-json \
  --verbose \
  --debug 2>&1 | tee .principled/scratch/rule-test.jsonl
```

The `--debug` flag surfaces what was loaded from `.claude/rules/` and when.
Audit the JSONL with a subagent to confirm the rule reached the model in
the form you wrote it.

For path-scoped rules, test with a file inside the glob *and* a file
outside it. The rule should apply to the first and be silent on the
second.

### Version control practices

Commit rules alongside the code they govern. The diff is a useful artifact
when triaging "when did this convention change?" later.

- Commit `.claude/rules/*.md` in the same PR as the refactor that
  motivated them.
- Use a `chore:` or `docs:` commit prefix; never mix rule changes with
  feature work.
- If a rule is being added, the PR description should cite the specific
  mistake or code review that motivated it.
- If a rule is being deleted, the PR description should cite the rule
  being superseded or the file/behavior that made it obsolete.

### Incremental improvement

Rules are easy to over-engineer. The maintainer loop:

1. **Catch the mistake in chat.** Note the rule that would have prevented
   it (or that, if added now, would catch the next one).
2. **Add the minimum rule.** One sentence, one bullet, no preamble.
3. **Re-run the failing scenario.** Verify the rule actually changes
   behavior. If it does not, the rule is wrong; cut it.
4. **Leave the rule in for two weeks.** If the rule has not fired in
   that time, the model has internalized the behavior — consider moving
   it to auto memory or deleting it.

### Adversarial verification

Before merging a rule, run an adversarial review:

- **Stress test the wording.** Find a phrasing that, when slightly
  rephrased, contradicts the rule. If the contradiction is reasonable
  (i.e., the model could legitimately follow either reading), the rule
  is ambiguous.
- **Look for conflicts.** Grep the rest of `.claude/rules/` and `CLAUDE.md`
  for instructions that overlap with the new rule. Resolve conflicts in
  writing: "Rule A supersedes Rule B in cases of contradiction."
- **Read it cold.** Open the file in a fresh editor and read it as if
  you had never seen the project. If the rule's intent is not obvious
  from the body alone, add a "Why" sentence at the top.

---

## Maintenance

### Organization strategies

A `.claude/rules/` directory grows over time. The patterns that scale:

- **One file per topic.** `testing.md`, `security.md`, `frontend.md`.
  Do not split a single topic across multiple files; merge them.
- **Subdirectories for subdomains.** `frontend/`, `backend/`, `infra/`
  are useful when a project has clearly distinct areas with distinct
  rules. Avoid them when the project is small enough that one flat
  directory is easier to scan.
- **Filename = topic, not audience.** Prefer `database.md` over
  `for-juniors.md`. Audience-targeted filenames age badly.
- **No index file.** A `README.md` in `.claude/rules/` is mostly noise;
  the directory listing is self-explanatory. If you need an index, put
  it in the project `CLAUDE.md` as a one-line "see `.claude/rules/`".

### Deprecation and cleanup

Rules rot. The same session that reveals a stale rule is the right time
to delete it.

- **Delete first, archive second.** When in doubt, delete. An archive
  of old rules in `.attic/` is useful only if someone is going to grep
  it; if not, the archive is just litter.
- **Keep one canonical place per convention.** If the same rule lives
  in `CLAUDE.md` and `.claude/rules/X.md`, cut one of them. The
  canonical home is whichever the model loads first in the merge
  order — usually the more specific file wins.
- **Date-sensitive rules get a TTL.** A rule about a temporary
  migration, a flagged library, or a deprecation timeline should
  include the date in the rule body and a follow-up task in the
  project tracker to revisit it.

### Cross-file consistency

Three patterns catch most cross-file drift:

1. **Symlink shared rules.** If two projects share a rule, symlink
   the file from a shared location. Editing the symlink edits both.
2. **Single source of truth in code.** A rule like "API handlers live
   in `src/api/handlers/`" should be verifiable by reading the
   filesystem. Rules that reference phantom structures drift.
3. **Lint with a subagent.** Spawn a critic subagent against
   `.claude/rules/` and the project `CLAUDE.md` with the task "find
   any pair of instructions that contradict each other or that have
   become stale relative to the code." Loop until no HIGH findings
   remain.

### Documentation sync

A rule that says "see the project wiki for X" is a broken promise the
moment the wiki is restructured. The project `CLAUDE.md` and
`.claude/rules/` are the durable copy; the wiki is a mirror. Either:

- **Inline the canonical content** in the rule, and link to the wiki
  for "more context"; or
- **Generate the wiki from the rules** at build time, so the rules
  remain the source of truth.

---

## Advanced Patterns

### Meta-rules (rules about rules)

A meta-rule is a rule whose audience is the human maintainer, not the
model. It is hidden from the runtime by convention — typically a
`type: meta` frontmatter field that the loader filters out, or a
filename prefix (`_meta-*.md`) that the maintainer team has agreed to
ignore.

Use meta-rules for:

- The "rules of writing rules" (this entire document, internalized).
- Maintainer-only conventions (e.g., "always run
  `claude-md-improver` before committing a CLAUDE.md change").
- Cross-references to the maintainer handbook.

Avoid meta-rules for:

- Anything the model needs to follow at runtime — that is a regular
  rule, not a meta-rule.

### Conditional rules

A rule can include a "when" condition in its body. The model is
generally good at following conditional instructions, but only when the
condition is unambiguous. The reliable pattern is to lead with the
condition:

```markdown theme={null}
# Database migrations

When modifying a file under `migrations/`:

- The file name must end in a new sequential number
- The file must be append-only (never edit a committed migration)
- The up and down methods must both be present
```

A conditional rule with three branches ("when X do A, when Y do B, when
Z do C") is harder to follow than three separate rules, each
path-scoped to the relevant file. Prefer path scoping over inline
branching when the conditions are file-driven.

### Priority and precedence

When two rules give contradictory instructions, Claude Code does not
have a built-in conflict resolution policy. The model picks whichever
it parses as more recent or more specific. To make the resolution
deterministic:

- **Write the precedence into the rule.** "If this rule contradicts
  `.claude/rules/security.md`, security wins." Hard-coded, no
  ambiguity.
- **Path-scoped rules beat always-on rules.** A `paths: src/api/**`
  rule is more specific than an always-on rule and is read after it
  for matching files.
- **Project rules beat user rules.** `your-project/.claude/rules/`
  wins over `~/.claude/rules/` when both apply and contradict.
- **Managed CLAUDE.md cannot be excluded.** Org-wide policy in
  `/etc/claude-code/CLAUDE.md` is the only layer that always wins.

### Scope limiting (paths field)

The `paths` frontmatter field restricts a rule to files matching the
glob. Use it when a rule only matters for a part of the codebase.

```markdown theme={null}
---
paths:
  - "src/api/**/*.ts"
  - "src/api/**/*.tsx"
---

# API Development Rules

- Validate input with Zod
- Use the standard error response format
- Include an OpenAPI summary in the JSDoc
```

Glob patterns:

| Pattern                | Matches                                          |
| :--------------------- | :----------------------------------------------- |
| `**/*.ts`              | Every TypeScript file in any directory           |
| `src/**/*`             | Every file under `src/`                          |
| `*.md`                 | Markdown files in the project root               |
| `src/components/*.tsx` | React components in a specific directory         |
| `src/**/*.{ts,tsx}`    | TypeScript or TSX files under `src/` (brace expansion) |

A path-scoped rule loads when Claude reads a file that matches the
pattern. It does not fire on every tool use. The `paths` field accepts
an array, so a single rule can cover several globs.

---

## Quick Reference

### Rule file checklist

Before committing a new rule or a rule change, verify:

- [ ] The rule is a single topic, with one named file under
      `.claude/rules/` (or `~/.claude/rules/` for personal rules).
- [ ] The body is under 100 lines; trim aggressively.
- [ ] The body opens with intent (a "why" sentence), not just
      instructions.
- [ ] Mandatory language (`MUST`, `NEVER`) is reserved for
      invariants; soft language (`consider`, `prefer`) is used for
      style.
- [ ] Any cross-reference to other rules or skills is by *name*, not
      by file path.
- [ ] Path-scoped rules have a `paths` frontmatter; always-on rules
      do not.
- [ ] The rule has been tested in a fresh session against at least
      one representative query.
- [ ] The PR description cites the specific mistake or review that
      motivated the rule.
- [ ] No other rule in the repo contradicts the new rule.

### Red flags to watch for

- **The rule is longer than 100 lines.** Probably a procedure in
  disguise; move to a skill.
- **The rule has 5+ bullets under a single header.** Split into
  related rules or move to a skill.
- **Two rules in the same directory give contradictory advice.** Cut
  one, or write the precedence into the surviving rule.
- **The rule references a file that does not exist.** The model will
  act on the wrong mental model.
- **The rule has been in `.claude/rules/` for a year without
  changing.** Either the codebase has caught up (delete the rule) or
  the rule is being silently ignored (rewrite it).
- **The rule duplicates the body of a skill.** The skill is loaded on
  demand; the rule is always on. Pick one.
- **The rule is mostly a rephrasing of Claude Code defaults.** Cut
  it — the model already follows the default.

### Recommended file structure

```text theme={null}
your-project/
├── CLAUDE.md                          # Project facts, in every session
└── .claude/
    ├── CLAUDE.md                      # Optional modular alternative to root
    └── rules/
        ├── code-style.md              # Always-on
        ├── testing.md                 # Always-on
        ├── security.md                # Always-on
        ├── api-design.md              # paths: src/api/**
        ├── database.md                # paths: src/db/**, migrations/**
        ├── frontend/
        │   ├── react.md               # paths: src/components/**
        │   └── styles.md              # paths: **/*.{css,scss}
        └── backend/
            └── grpc.md                # paths: proto/**, src/grpc/**
```

Keep the directory shallow (one level of subdirectories is fine; two is
too many). Keep filenames topic-shaped, not audience-shaped. Delete rules
that have not fired in a quarter. The maintainer of a healthy rules
directory is, on average, removing rules more often than adding them.

---

**Governs itself — all revisions to this file must remain:**
- **Accurate** — Reflects current Claude Code behavior; outdated sections removed, not annotated.
- **Actionable** — Every section answers "what do I do?" not just "what exists?".
- **Self-contained** — A cold-start instance can author a working rule from this file alone.
