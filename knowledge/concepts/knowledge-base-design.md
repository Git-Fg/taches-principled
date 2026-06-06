# Knowledge Base Design

**Purpose:** Defines what the `knowledge/` directory is, how it is structured, how its contents relate to skills and other artifacts, and how to maintain it.

**Audience:** Maintainer only. End-user Claude never reads this file or any file in `knowledge/`.

**When to read:** Before adding, moving, or removing any file under `knowledge/`. Also before creating a new concept, template, or official-doc refresh.

---

## What `knowledge/` Is

The `knowledge/` directory is **maintainer-only reference material**. It exists to support skill authoring, agent design, and marketplace maintenance. It is invisible to any Claude Code session that installs taches-principled as a marketplace plugin -- only sessions working directly in this repository (contributing to the marketplace) ever load it.

The boundary is architectural, not aspirational. Claude Code's plugin loader only ships content under `plugins/` and `.claude-plugin/`. Everything at the repository root and under `knowledge/` stays on the shelf. If a piece of information must reach end-user Claude, it must materialize as an edit inside `plugins/` (a skill body, an agent definition, a reference file, a command, or a hook). `knowledge/` is scaffolding for the human and AI maintaining the marketplace -- reasoning, methodology, and reference material that informs what ships, but does not ship itself.

This means:

- Research notes, brainstorming, and synthesis stored in `knowledge/` have zero effect on end-user behavior until they are translated into `plugins/` content.
- A `knowledge/` document that duplicates information already present in a skill reference file is a maintenance burden, not a safety net. Prefer a single source of truth.
- Cross-session notes for the maintainer live in `~/.claude/projects/<project>/memory/MEMORY.md`, not in `knowledge/`. `knowledge/` is for durable methodology and reference; transient session artifacts go in `.principled/`.

---

## Directory Structure

```
knowledge/
├── SCHEMA.md                          # Wiki format conventions (frontmatter, tags, page size)
├── raw/
│   ├── official/                      # Claude Code official docs (refreshed via curl)
│   │   ├── skills.md
│   │   ├── subagents.md
│   │   ├── hooks.md
│   │   ├── commands.md
│   │   ├── permissions.md
│   │   ├── agent-types.md
│   │   ├── agent-tool-params.md
│   │   ├── agent-skill-integration.md
│   │   ├── rules.md
│   │   ├── memory.md
│   │   └── plugins/
│   │       ├── creating.md
│   │       ├── marketplaces.md
│   │       ├── plugin-submission.md
│   │       └── plugins-reference.md
│   └── articles/                      # Reserved: community articles (not yet populated)
├── concepts/                          # Cross-cutting methodology documents
│   ├── contributing.md                # 3-phase testing, 6 design principles
│   ├── intent-format.md               # Structured user-task intent representation
│   ├── knowledge-base-design.md      # This document — directory design and maintenance
│   ├── llm-wiki-methodology.md        # LLM-as-wiki patterns
│   └── persistence-schema.md          # Cross-session persistence design
├── entities/                          # Reserved: per-plugin entity records (not yet populated)
├── queries/                           # Reserved: filed query results (not yet populated)
└── templates/                         # Reusable templates for artifact creation
    ├── changelog-entry.md             # CHANGELOG entry format and conventions
    └── command.md                     # Command authoring template
```

### Directory Roles

| Directory | Content type | Mutability | Who writes it |
|-----------|-------------|------------|---------------|
| `SCHEMA.md` | Wiki format conventions (tag taxonomy, frontmatter shape, page-size budget) | Evolves with wiki conventions | Maintainer |
| `raw/official/` | Downloaded Claude Code documentation | Replaced wholesale on refresh; never hand-edited | `curl` from `code.claude.com/docs/` |
| `raw/articles/` | Reserved for future community articles | Not yet populated | N/A |
| `concepts/` | Cross-cutting methodology and design documents | Evolves with marketplace practices | Maintainer |
| `entities/` | Reserved for per-plugin entity records | Not yet populated | N/A |
| `queries/` | Reserved for filed query results | Not yet populated | N/A |
| `templates/` | Reusable templates for creating new artifacts | Stable; updated when conventions change | Maintainer |

---

## How `knowledge/` Relates to Skills

The marketplace has two reference layers that serve different audiences and purposes:

| Layer | Location | Audience | Scope | Loading |
|-------|----------|----------|-------|---------|
| Skill references | `plugins/<plugin>/skills/<skill>/references/` | End-user Claude | Domain-specific mechanism content for one skill | Lazy-loaded when SKILL.md cites it imperatively |
| Knowledge concepts | `knowledge/concepts/` | Maintainer only | Cross-cutting methodology applying to ALL skills and plugins | Read by maintainer (human or AI) working in this repo |

**A skill reference file teaches how to do one specific thing.** For example, `plugins/tp-rust/skills/rust/references/workspace-patterns.md` teaches Rust workspace layout patterns -- it is relevant only when the `rust` skill is active and the task involves Cargo workspace structure.

**A knowledge concept teaches how to think about a class of problems.** For example, `knowledge/concepts/contributing.md` teaches the 3-phase testing methodology that applies to every skill, agent, hook, and plugin change -- it is relevant whenever any artifact is being created or modified, regardless of which plugin it belongs to.

The distinction matters for maintenance:

- Skill reference content should stay focused on the skill's domain. If a reference file starts explaining general methodology that would apply equally to other skills, that methodology belongs in `knowledge/concepts/` instead.
- Knowledge concepts should not duplicate information that already exists in an official doc under `raw/official/`. Concepts add methodology and opinion on top of official reference material; they do not restate it.

### When to Create a Skill Reference vs a Knowledge Concept

| Situation | Create in |
|-----------|-----------|
| Mechanism specific to one skill's domain (e.g., how to write a Cargo.toml) | `plugins/<plugin>/skills/<skill>/references/` |
| Pattern used by multiple skills across plugins (e.g., subagent contract design) | `knowledge/concepts/` |
| Official Claude Code documentation on an artifact type | `knowledge/raw/official/` (refresh, do not author) |
| Reusable template for creating new instances | `knowledge/templates/` |
| Research notes, brainstorming, transient artifacts | `.principled/` (not `knowledge/`) |
| Cross-session memory for the maintainer | `~/.claude/projects/<project>/memory/MEMORY.md` (not `knowledge/`) |

---

## Access Patterns

The maintainer (human or AI working in this repo) reads `knowledge/` files at specific moments. The access pattern is not "read everything at session start" but "read the relevant file before performing the corresponding task."

### When to Read What

| File or directory | When to read |
|-------------------|-------------|
| `CLAUDE.md` (repo root) | Always. Governs every action in this repo. |
| `knowledge/raw/official/skills.md` | Before authoring or modifying any skill |
| `knowledge/raw/official/subagents.md` | Before creating or modifying any agent |
| `knowledge/raw/official/hooks.md` | Before configuring any hook |
| `knowledge/raw/official/commands.md` | Before creating any command |
| `knowledge/raw/official/permissions.md` | Before configuring permissions |
| `knowledge/raw/official/agent-types.md` | Before choosing an agent type |
| `knowledge/raw/official/agent-tool-params.md` | Before spawning subagents |
| `knowledge/raw/official/agent-skill-integration.md` | Before adding skills to agents |
| `knowledge/raw/official/rules.md` | Before writing rules or CLAUDE.md |
| `knowledge/raw/official/memory.md` | Before configuring CLAUDE.md hierarchy or `.claude/rules/` |
| `knowledge/raw/official/plugins/creating.md` | Before creating plugins |
| `knowledge/raw/official/plugins/marketplaces.md` | Before modifying marketplace.json |
| `knowledge/raw/official/plugins/plugin-submission.md` | Before submitting a plugin |
| `knowledge/raw/official/plugins/plugins-reference.md` | Before advanced plugin work |
| `knowledge/concepts/contributing.md` | Before modifying skills, subagents, hooks, or plugins |
| `knowledge/concepts/intent-format.md` | Before representing user-task intent in structured form |
| `knowledge/concepts/llm-wiki-methodology.md` | Before authoring wiki-methodology skills |
| `knowledge/concepts/persistence-schema.md` | Before designing cross-session persistence |
| `knowledge/templates/changelog-entry.md` | Before writing any CHANGELOG entry |
| `knowledge/templates/command.md` | Before authoring a new command |
| `knowledge/SCHEMA.md` | Before adding or modifying any wiki-format page |

### Reading Hierarchy

When multiple knowledge sources apply, read in this order:

1. **`CLAUDE.md`** first -- it governs all work in this repo.
2. **`knowledge/raw/official/<topic>.md`** -- authoritative reference for the artifact type.
3. **`knowledge/concepts/<topic>.md`** -- methodology that adds opinion and process on top of the official reference.
4. **`knowledge/templates/<topic>.md`** -- concrete format to follow for the artifact instance.

This is the "never proceed on assumptions" rule from CLAUDE.md: read the relevant doc before working on the corresponding task. The knowledge/ directory exists precisely so that the maintainer does not need to memorize any of this -- know when to look, not what it says.

---

## Content Standards

Every file in `knowledge/` must follow these structural conventions.

### Required Elements

1. **One-line purpose** -- The first paragraph after any frontmatter states what the file is for, in one sentence. This allows a directory listing or skim to establish the file's role without reading the entire document.

2. **Audience tag** -- The file must explicitly state its audience. For all files in `knowledge/`, the audience is "maintainer only." If a file's content is intended to reach end-user Claude, it belongs in `plugins/`, not here.

3. **"When to read" section** -- Every knowledge file must include a "When to read" section (or equivalent) that specifies the triggering condition. This is not a loading trigger (the chicken-and-egg anti-pattern from CLAUDE.md); it is a navigation aid for the maintainer scanning the directory.

### Formatting Conventions

- `raw/official/` files are downloaded directly from Claude Code docs and are **never hand-edited**. They retain whatever format the source provides.
- `concepts/` files use standard Markdown with clear section headers. Each concept document is self-contained -- it can be read without loading other knowledge files (though it may reference them for deeper context).
- `templates/` files contain a concrete template block (in a code fence) followed by explanatory conventions. The template is the artifact; the conventions explain how to fill it in.
- `SCHEMA.md` defines wiki-wide conventions and is the authority for any wiki-format page.

### Size Guidelines

Knowledge files have no hard token budget (unlike skills, which must stay under 2,500 tokens). They are not loaded into an end-user Claude context. However, keep them focused:

- A concept document should address one methodology or design pattern. If it covers two distinct topics, split it.
- A template should be immediately usable -- the template block plus a short explanation, not a treatise.
- An official doc is whatever length it downloads at; do not truncate or summarize.

---

## Maintenance

### Adding a New Knowledge File

1. Determine the correct subdirectory:
   - Is it an official Claude Code doc? Put it in `raw/official/`. Consider refreshing via `curl` instead of hand-authoring.
   - Is it a cross-cutting methodology or design pattern? Put it in `concepts/`.
   - Is it a reusable template for creating artifacts? Put it in `templates/`.
   - Is it a wiki-format page? Follow `SCHEMA.md` conventions.

2. Add the three required elements: one-line purpose, audience tag, "When to read" section.

3. If the file introduces a new methodology that affects CLAUDE.md's reference tables or self-check, update CLAUDE.md to cite it.

4. Verify no existing skill reference file already covers the same content. If it does, decide which is the canonical location and remove or reduce the duplicate.

5. If the file relates to official docs, verify it adds value on top of `raw/official/` rather than restating what is already there.

### Refreshing Official Docs

Official docs are refreshed by downloading the latest version from the Claude Code docs site:

```bash
curl -sL "https://code.claude.com/docs/en/<topic>.md" -o knowledge/raw/official/<topic>.md
```

Where `<topic>` matches the URL slug from `code.claude.com/docs/llms.txt`. After downloading:

1. Verify the file starts with valid Markdown content (not an error page).
2. Check that no `concepts/` or `templates/` files reference specific line numbers or content from the old version that may have shifted.
3. If the official doc now covers a methodology that was previously only in `concepts/`, evaluate whether the concept doc is still needed or should be simplified to reference the official doc.

Refresh cadence: before any major audit cycle, or when a new Claude Code release changes the plugin/skill/agent API.

### Auditing for Staleness

Knowledge files can go stale when:
- The Claude Code API changes and `raw/official/` docs are not refreshed.
- A methodology in `concepts/` is superseded by a better approach that has been adopted in practice but not documented.
- A template in `templates/` does not match the current CHANGELOG or command conventions.
- CLAUDE.md's reference tables cite knowledge files that have been moved or removed.

Audit checklist (run as part of any major release or quarterly review):

1. Compare each `raw/official/` file against the current Claude Code docs site. Refresh if the checksum differs.
2. For each `concepts/` file, verify the methodology it describes matches current practice. If the team has evolved away from the documented approach, update the file.
3. For each `templates/` file, verify the template matches the most recent example in CHANGELOG.md or commands/.
4. Verify every file cited in CLAUDE.md's reference tables still exists at the cited path.
5. Check that no `concepts/` file duplicates information already in `raw/official/` without adding methodology or opinion.

### Reserved Directories

`raw/articles/`, `entities/`, and `queries/` are reserved but not yet populated. Do not remove them -- they exist as placeholders for future use. When populating them, add a README or index file explaining their role, and update this design document to reflect the new content.
