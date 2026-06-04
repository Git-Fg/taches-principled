# Changelog

All notable changes are documented here.

## [1.13.0] — 2026-06-04

Resolves the post-initial-release audit of the new `tp-wiki` plugin.
Six small commits covering the manifest-hygiene, hub-skill structure,
agent safety, and prose-clarity findings.

### Fixed

- **Missing `plugins/tp-wiki/.claude-plugin/plugin.json`** (tp-wiki 0.1.1). The plugin shipped with a marketplace catalog entry but no per-plugin manifest — the same bug class we fixed for `claude-cli-wrapper` / `tp-mcp` / `tp-rust` in #11 Commit 4. Without it, install would have fallen back to marketplace.json-derived metadata for tp-wiki only.
- **`wiki-searcher` tool-scope safety gap** (tp-wiki 0.1.1). The agent body said "NEVER write or modify any wiki file" but had no `tools:` field, so it inherited Write / Edit / Bash. The body policy was a request, not a guarantee. Now `tools: [Read, Glob, Grep]` enforces read-only at the tool boundary. Matches the sister agents and the focused-agent pattern across the marketplace.

### Added

- **Hub-skill `## Reference Index`** (tp-wiki 0.1.1). Names the 3 shipped agents (wiki-searcher, wiki-linter, wiki-ingester) and maps each to its mode, color, model, and tool scope. Same pattern as the sadd Reference Index from #14 D2.
- **Hub-skill `## Cross-plugin dependencies`** (tp-wiki 0.1.1). Documents the soft deps on `mcp__mcp-searxng__fetch` and `mcp__mcp-searxng__extract` for `wiki-ingester` mode `url`, both with Claude Code built-in fallbacks (WebFetch). The plugin has no hard cross-plugin deps — it's self-contained.
- **Hub-skill `## Decision Router`** (tp-wiki 0.1.1). Replaces the informal "Routing — Delegate to Subagents" section with an intent-signal → subagent table, plus disambiguation guidance for ambiguous intents.
- **Hub-skill `## Anti-patterns`** (tp-wiki 0.1.1). 7 specific failure modes with "don't do this" framing — mutating `raw/`, single-source pages, tag sprawl, skipping orientation, etc.

### Changed

- **`wiki/SKILL.md` frontmatter tightened** (tp-wiki 0.1.1). Description now wrapped in double-quotes (the bug class from #10 Bug 4 — the original bare multi-line value was fragile). Added `when_to_use:` and `argument-hint:` (the latter was missing across the hub skill).
- **`wiki-linter` Check A–G each get an explicit `Action` line** (tp-wiki 0.1.1). The Auto-Fix section at the bottom said "auto-fix safe violations" but the per-check prose didn't say what to do for any individual check. Now each check has an explicit Action: report-only by default, with auto-fix gated behind user approval.
- **`wiki-linter` Check F documents the 90-day default as overridable** (tp-wiki 0.1.1). If `intent.md` has a line of the form "no page older than N months/days without review", use that; otherwise default to 90 days.
- **`wiki-searcher` description gets more trigger phrases** (tp-wiki 0.1.1). Aligned to the same trigger surface as the hub skill's `when_to_use` and the marketplace entry, so routing into the agent doesn't have a narrower signal.
- **`Mandatory Orientation` backtick disambiguation** (tp-wiki 0.1.1). The `SCHEMA.md` / `index.md` / `log.md` references are conceptual files in the user's wiki, not files in this plugin. Added a one-line note so future maintainers don't grep the plugin for them and conclude they're missing.

### Skip notes

- Findings 11 (agent description style consistency) was already resolved — all 3 agents used quoted multi-line YAML; the SKILL.md was the inconsistent one, fixed in the frontmatter-tightening change above.
- Findings 13, 14, 15, 16 from the audit were minor polish items, addressed in the wiki-linter Action lines + the wiki-searcher trigger coverage + the Mandatory Orientation disambiguation.

### Changed

- **`tp-wiki`** 0.1.0 → 0.1.1 (patch — manifest hygiene, safety gap, hub-skill structure; no new features).
- **Marketplace** 0.21.0 → 0.22.0 (catalog change for the tp-wiki patch).

## [1.12.0] — 2026-06-04

Resolves issues #11–#16 opened by `MiaouLeChat929` on the post-#10 audit
batch. Twelve commits, three tiers (user-breaking → polish → housekeeping).
All commits land direct to main, no PR machinery (consistent with how
#6/#7 were handled).

### Tier A — user-breaking (fixed first)

- **`mcp-server-implement` skill aligned to the rmcp 0.3 API actually shipping in `claude-cli-wrapper`** (tp-mcp 0.1.1, fixes #13 C1/C2/C3). The §2 `Cargo.toml` example was pinned to rmcp 0.16 (actual: 0.3.2). The §3 macro cheat sheet showed `#[tool_handler(name = ..., version = ..., instructions = ...)]` and `Implementation::from_build_env()` (both don't exist in 0.3). The §11 error mapping aliased `McpError` (the alias is gone; use `rmcp::ErrorData` directly) and used `anyhow::Error::backtrace()` (requires the anyhow backtrace feature). The §16 anti-patterns and §12 (output construction) had one leftover stale `McpError::invalid_request` reference. All rewritten against the working API; `cargo check` clean on `claude-cli-wrapper` 0.2.2.
- **`tp-mcp` schemars cheat-sheet + Consuming-in-Claude-Code section** (tp-mcp 0.1.1, fixes #13 C4/C5). New `## §14. Schemars attribute cheat-sheet` in `mcp-tool-surface` maps every schemars attribute to its JSON Schema keyword, lists the `serde` attributes that affect schema generation, and documents the `extend("keyword" = value)` / `schema_with` escape hatches. New `## §14. Consuming in Claude Code` in `mcp-server-design` covers the actual discovery handshake Claude Code performs, the install paths, what the model sees vs. doesn't see, and a symptom → cause → fix table for common consumer-side debugging. Trailing §14–§16 renumbered to §15–§17 in both skills.
- **`claude-cli-wrapper` MCP server design tightened** (claude-cli-wrapper 0.2.2, fixes #12 H1/H2/H3/H4):
  - **H1**: `#[schemars(extend("additionalProperties" = false))]` added to all 6 input structs (`ExecuteInput`, `SessionInput`, `ContextInput`, `ReviewInput`, `AgentInput`, `ConfigInput`). `#[serde(deny_unknown_fields)]` alone does not auto-emit `additionalProperties: false` in schemars 1.0. Smoke test asserts the schema property.
  - **H2**: `annotations(title, read_only_hint, destructive_hint, idempotent_hint, open_world_hint)` added to all 6 `#[tool(...)]` macros. Annotations reflect actual semantics: `claude_review` is the only read-only tool; `claude_execute` and `claude_agent` carry `open_world_hint: true`; etc.
  - **H3**: replaced the single `internal_error` mapping with a typed `WrapperError` enum. `CliNonzeroExit` → JSON-RPC `-32001` (custom) with the full envelope in the `data` field, replacing the old `is_error: true` behavior. `Internal(anyhow::Error)` → JSON-RPC `-32603` (standard) for real wrapper failures. The MCP server, script mode, and the typed-error path all share the same mapping (`impl From<WrapperError> for ErrorData`).
  - **H4**: `WrapperResultEnvelope` struct added to `schema.rs` documenting the output shape. rmcp 0.3.2 predates the MCP 2025-11-25 `Tool::output_schema` / `CallToolResult::structured_content` fields, so the envelope is currently delivered as a JSON-encoded `text` content item and the schema is declared here for the day rmcp 0.4+ lands. Each tool's description now references the envelope shape explicitly.

### Tier B — polish

- **Three plugins received the missing `.claude-plugin/plugin.json`** (fixes #11 items 1/2/3): `claude-cli-wrapper`, `tp-mcp`, `tp-rust`. Content sourced from the existing `marketplace.json` entries so install-time metadata is byte-identical to what the index advertises. The per-plugin manifest is the spec-authoritative source; the marketplace catalog is just an index.
- **MCP/hooks manifest hygiene** (fixes #11 items 4/6): dropped the redundant `"type": "stdio"` from `claude-cli-wrapper/.mcp.json` (stdio is the default), dropped the meaningless `"matcher": "*"` from the `core-principled` `SessionStart` hook (SessionStart has no tool name to match against), added the missing `"hooks": "./hooks/hooks.json"` declaration to `core-principled/.claude-plugin/plugin.json` (the hook file existed all along but was never advertised, so installs were silently dropping it).
- **Per-plugin `author` blocks dropped from `marketplace.json`** (fixes #11 item 7). All 8 plugins now ship a per-plugin `plugin.json` with their own `author`, which the spec treats as the authoritative source. The per-plugin `plugins[].author` field was duplicating the same info for every entry. The marketplace-level `owner` block stays (different concept — "owner of the marketplace" per spec).
- **`web-search` `when_to_use` trimmed 507 → 191 chars** (core-principled 0.15.0, fixes #14 D1). The 200-char metadata cap is a hard routing budget; descriptions that overshoot get silently truncated in high-context sessions and the tail (the NOT clause, which prevents false-positive routing to code/local search) disappears. Trim keeps the trigger list, the tool-agnostic framing, and the NOT-for list; example phrasings moved into the skill body.
- **`sadd` Reference Index added** (tp-sadd 0.3.4, fixes #14 D2). New section names all 6 shipped agents (`sadd-expander`, `sadd-explorer`, `sadd-generator`, `sadd-judge`, `sadd-meta-judge`, `sadd-synthesizer`) and maps each to its mode. Previously the only way to discover the agent roster was to read each agent's `description` field and infer the dispatch pattern from context.
- **`session-analytics` cross-plugin dependencies documented** (tp-session-audit 0.3.1, fixes #14 D3). New `## Cross-plugin dependencies` section makes the soft-dep contract on `tp-debug-tracer`, `tp-fpf:fpf-evidence-validator`, and `tp-sadd:sadd-judge` greppable for maintainers, names the fallback per dep, and explains why these are soft (the plugin ships standalone).
- **`sadd-meta-judge` model: opus → sonnet** (tp-sadd 0.3.4, fixes #15 E2). The agent's only job is to generate a YAML evaluation spec (objective, rubric, pass/fail checklist, pass threshold). Structured generation work — sonnet handles it well and the marginal quality of opus on a 3-5-criterion rubric is not worth the cost multiplier.
- **Two single-Bash agents converted to skills** (tp-git 0.3.3, fixes #15 E3). `git-preflight-checker` (`tools: [Bash]`) and `git-worktree-manager` (`tools: [Bash]`) are now `tp-git/skills/git-preflight-checker/SKILL.md` and `tp-git/skills/git-worktree-manager/SKILL.md`. An agent that only runs Bash commands pays subagent overhead (context load, model invocation, message passing) for what the main agent can do with one Bash tool call. Updated `tp-git/skills/git/SKILL.md` to use the new skill names.
- **44 agent skill blocks audited and cargo-cult removed** (fixes #15 E4; the issue said 27 — actual count is 44, all agents). Every agent was preloading the same 13–17 general-purpose skills regardless of purpose. After the audit: 9 pure-reasoning agents get `skills: []` (Claude picks on demand); 35 domain-focused agents get exactly 1 relevant skill (e.g., `tp-secrets-detector → security`, `fpf-evidence-validator → fpf`, `sadd-judge → sadd`). All 44 files re-validated for YAML frontmatter correctness after the rewrite.

### Tier C — housekeeping

- **`core-principled` keywords pruned 31 → 14** (fixes #16 F1). The original list mixed universal product labels, cross-cutting workflow names, and individual skill/agent handles. The third category is too granular for marketplace discovery — when a user types `fact-check` they want the fact-check skill, not the whole plugin. Kept only stable cross-cutting workflow nouns and product-level labels; individual tool names belong in skill frontmatter.

### Documentation

- **`/improve` command body clarified** (fixes #16 F2). Both `/improve` and `refine` were discoverable entry points to the same CRITIQUE machinery and the overlap was unclear. `/improve` is the shorthand ("make this better, your call"); `refine` is the skill with explicit mode selection (SIMPLIFY / REVIEW / CRITIQUE / POLISH / MEMORIZE). The command body now spells out the relationship and includes a routing table.
- **Agent prefix rule documented in `CLAUDE.md`** (fixes #16 F3). The marketplace ships with an asymmetric naming convention: `core-principled` agents use `tp-*` (legacy namespace disambiguator), sub-plugins use `<plugin>-*` (the plugin name itself is the namespace). The rule is a historical artifact, not a flaw to be smoothed out — do not "fix" it with a mechanical rename, which would break every hardcoded spawn.

### Skip notes

- **E5** (`tools:` missing on subagents is expected) — skipped per user instruction. The convention is: `tools:` on an agent is a hard allowlist; absent `tools:` means inherit everything. The 23-of-46 number from the issue is real but `tools:` is only appropriate for read-only / restricted agents, not for general-purpose workers.
- **#11 item 5** (email `felix@example.com`) — `example.com` is a placeholder, not a real privacy concern. No change.
- **#14 D4** (fpf Reference Index) — issue was wrong, fpf already has a Reference Index. No change.

### Changed

- **`core-principled`** 0.14.0 → 0.15.0 (minor — new hooks field, `/improve` rewrite, 9 agents moved to `skills: []`, keywords trimmed 31→14).
- **`claude-cli-wrapper`** 0.2.1 → 0.2.2 (minor — H1/H2/H3/H4 MCP server design fixes; new `error.rs` module).
- **`tp-mcp`** 0.1.0 → 0.1.1 (patch — skill content fixes; schemars cheat-sheet + Consuming-in-Claude-Code sections).
- **`tp-git`** 0.3.2 → 0.3.3 (minor — 2 single-Bash agents → skills).
- **`tp-sadd`** 0.3.3 → 0.3.4 (minor — sadd-meta-judge opus→sonnet, Reference Index).
- **`tp-fpf`** 0.3.2 → 0.3.3 (patch — 4 agent skill blocks trimmed).
- **`tp-session-audit`** 0.3.0 → 0.3.1 (minor — cross-plugin deps doc).
- **`tp-rust`** 0.1.0 → 0.1.0 (no change — not touched in this batch; bumped only for the new `plugin.json`).
- **Marketplace** 0.19.0 → 0.20.0 (catalog change for the seven per-plugin bumps above; new `plugin.json` files for `claude-cli-wrapper`, `tp-mcp`, `tp-rust`; per-plugin `author` blocks dropped; `core-principled` keywords pruned).

## [1.11.1] — 2026-06-04

### Added
- **`/cc-docs` slash command** (core-principled 0.14.0): 7-line command body that spawns the `tp-cc-docs` subagent and returns its cited answer. `argument-hint: "[question about Claude Code, Agent SDK, or Claude API]"`. Description in user vocabulary ("Ask a Claude Code, Agent SDK, or Claude API documentation question and get a cited answer from the live docs"). Body is 1 sentence, no markdown, semantic subagent reference — follows the marketplace's "high trust + high freedom" command convention. Recreates the content of PR #7 directly on main to avoid PR-merge machinery.
- **`.github/workflows/refresh-cc-docs.yml`** (157 lines): Weekly cron (Mondays 07:17 UTC) downloads `https://code.claude.com/llms.txt`, compares its sha256 to the embedded snapshot inside `plugins/core-principled/agents/tp-cc-docs.md`, and opens a single `chore/refresh-cc-docs-snapshot` PR via `peter-evans/create-pull-request` if the upstream has drifted. `delete-branch: true` keeps the auto-PR graveyard clean. Also fires on `workflow_dispatch` and on any push that touches the agent file. Recreates the content of PR #6 directly on main for the same reason.

### Changed
- **`core-principled`** 0.13.0 → 0.14.0 (minor — new `/cc-docs` slash command).
- **Marketplace** 0.18.0 → 0.19.0 (catalog change for new slash command).

### Why this is on main, not via PR
The user instructed to land the PR #6 + #7 content on main directly to avoid the merge-conflict overhead of three-way merging each PR branch against the post-#5 main line. The content is preserved exactly as the contributor wrote it in PRs #6 and #7. Both PRs are closed in GitHub and the closeout commit (`9904da1`) documents the rationale.

## [1.11.0] — 2026-06-04

### Added
- **`tp-cc-docs` agent** (core-principled 0.13.0): Reference oracle that answers questions about Claude Code, the Claude Agent SDK, and the Claude API by fetching the official documentation on every call rather than from training data. Embeds a point-in-time mirror of `https://code.claude.com/llms.txt` (145 doc pages) as a routing hint, then delegates to the canonical `https://code.claude.com/docs/en/<page>.md` URLs for the actual content. Description uses user-vocabulary triggers ("how do I X in Claude Code", "can Claude do Y", "what is the difference between hooks and skills", "where is setting Z documented"). CONTRAST clause distinguishes it from `tp-researcher` (general technology research). Color `orange` (general purpose, documentation). Tools: Bash, Read, WebFetch, WebSearch. Skills preloaded broadly per "better too much than not enough" — matches `tp-researcher`'s skill set plus `web-search`. Merged from open PR #5.
- **Marketplace keywords**: `claude-code-docs`, `llms-txt`, `documentation-lookup`, `reference-oracle`.

### Fixed
- **`claude-cli-wrapper` cross-platform launcher** (claude-cli-wrapper 0.2.1): the previously shipped `bin/claude-cli-wrapper` was a `Mach-O 64-bit arm64` binary only, causing `ENOEXEC` on every Linux / Intel Mac host (#10 Bug 1, critical). Replaced with a 50-line bash launcher at the same path that resolves the right binary in this order: (1) per-host prebuilt (`bin/claude-cli-wrapper.${OS}-${ARCH}`), (2) cached local build at `target/release/claude-cli-wrapper`, (3) freshly built binary via `cargo build --release` (~2-3 min one-time cost, then cached). Apple Silicon hosts continue to use the prebuilt unchanged. Adds `plugins/claude-cli-wrapper/README.md` with per-platform install contract. Follow-up: CI release pipeline for per-platform prebuilts (tracked in #10 §"Recommended upstream guardrails").
- **3 SKILL.md YAML frontmatter parse errors** (regression from 1.10.0 commit `2a77f23`): all three skills now parse cleanly under PyYAML safe_load and the Claude Code runtime parser. Closes #10 Bugs 2, 3, 4. The fixes were already in the working tree from the 1.11.0 prep pass (handoff.md B1–B3) and are now committed.
  - **`claude-cli/SKILL.md`** — unquoted `description:` contained YAML-significant colons (`lifecycle:`, `tuning:`). Wrapped in double-quotes and replaced inner colons with em-dashes.
  - **`kaizen/SKILL.md`** — closing `---` was stranded at line 25 after `user-invocable: false` was added; moved to line 7 so the body is no longer parsed as frontmatter.
  - **`mcp-tool-surface/SKILL.md`** — unquoted `description:` contained YAML-significant punctuation (`` `additionalProperties: false` ``, `oneOf`, `$ref`, `draft-2020-12`). Wrapped in double-quotes and removed the backticks.

### Changed
- **`claude-cli-wrapper`** 0.2.0 → 0.2.1 (patch — binary-arch fix).
- **`core-principled`** 0.12.0 → 0.13.0 (minor — new `tp-cc-docs` agent).
- **Marketplace** 0.17.0 → 0.18.0 (minor — catalog change for new agent).

### Verification
- Re-ran the frontmatter audit (PyYAML safe_load on every `plugins/**/SKILL.md` and `agents/*.md`): **73 / 73 files parse cleanly**, 0 errors.
- Local smoke test on Apple Silicon: `./plugins/claude-cli-wrapper/bin/claude-cli-wrapper --version` resolves to the renamed prebuilt (`bin/claude-cli-wrapper.darwin-arm64`) and prints `claude-cli-wrapper 0.1.0`. Pre-arm64 verification still needs the cross-platform CI guardrail noted above.

## [1.10.0] — 2026-06-04

### Changed
- **Skill frontmatter discoverability pass** — second pass after the 1.9.0 routing audit, focused on separation of concerns at the frontmatter level. Sourced from `docs/official/skills.md` and web search on Anthropic's skill authoring guidance.
  - **`description` rewrite to lead with user-facing triggers, not method jargon** — 6 skills whose `description` opened with abstract nouns (ideation, kaizen, project-maintenance, refine, fpf, sadd) now lead with what the USER is doing ("Explore a vague idea", "Apply four design-time guardrails", "Archive completed plans", "Review a PR", "Analyze from first principles", "Solve by generating multiple solutions").
  - **`when_to_use` added to 8 skills** missing the field (claude-cli, all 3 tp-mcp, all 4 tp-rust). Each `when_to_use` is a multi-line YAML block with 5-7 quoted user utterances that should trigger the skill — concrete phrases, not methodology.
  - **`user-invocable: false` added to 2 background-knowledge skills** (kaizen, fpf) — these are guardrails / methodology that the LLM should apply automatically, never something a user types `/kaizen` to invoke.

### Verification
- Re-ran the 10-utterance routing test against the marketplace: **8/10 clear winners, 2/10 legitimate two-skill-fits** (up from 7/10 in 1.9.0). The two remaining ties are both plan-lifecycle vs task-lifecycle on "add a new feature" — both legitimately apply.
- Audit script (description length, verb-leading, kitchen-sink detection, CONTRAST presence) re-run: 0 errors, 2 false-positive warnings from the audit's own verb list, all real issues resolved.

### Methodology
- Read `docs/official/skills.md` for the official 1,536-char cap, front-load trigger guidance, and invocation discipline (`disable-model-invocation`, `user-invocable`).
- Read `docs/templates/command.md` for the project's "high trust + high freedom" convention: skills tell what to do, not how; commands are just triggers.
- Web search on current skill-authoring best practices (2026): description quality, trigger vocabulary, avoidance of method-leaking.
- Wrote `/tmp/skill-frontmatter-audit.py` — 8-check audit (length cap, verb-leading, when_to_use coverage, trigger distinctness, kitchen-sink detection, invocation discipline, body length, when_to_use format).

## [1.9.0] — 2026-06-04

### Changed
- **Marketplace discoverability audit pass** — fixed routing and CONTRAST gaps surfaced by a 10-utterance routing test. No new skills; pure quality improvements to existing descriptions and structure.
  - **`tp-git/SKILL.md`** — added explicit §CONTRAST section listing what `git` does NOT do (plan / review / diagnose / security / task-lifecycle) and cross-links to `plan-lifecycle`, `refine`, `diagnose`, `security`, `task-lifecycle`.
  - **`test-orchestration/SKILL.md`** — added §CONTRAST distinguishing "plan and fix tests" from "just run the tests" and from `refine` / `diagnose` / `plan-lifecycle` / `security`.
  - **`claude-cli/SKILL.md`** — tightened `description` to fire only for programmatic agent-driven use, NOT for direct user-driven Claude Code. Removed the over-trigger on the word "claude" in casual mentions.
  - **`plan-lifecycle/SKILL.md`** — added "add a new feature" / "where do I start" / "start a new project" to the trigger vocabulary, and rewrote the `description` to lead with user-facing phrases.
  - **`task-lifecycle/SKILL.md`** — added "add a new feature" to the `description` and trigger vocabulary.
- **Routing test (verification):** before the fix, 5/10 utterances had a clear winner; after, 7/10 have a clear winner and the remaining 3 are legitimate "two skills could both fit" ties (plan-lifecycle vs task-lifecycle, both with trigger scores of 3).

### Verification methodology
- Ran a routing test of 10 realistic user utterances against the marketplace's 27 skills. For each utterance, the test scores each skill by counting how many of the utterance's content words appear in the skill's `description` field. The top-3 skills are reported, and the marketplace is considered well-routed when each utterance has a clear winner (top score > second score).
- Routing test script kept at `/tmp/marketplace-routing-test.py` for re-runs after future skill additions.

## [1.8.1] — 2026-06-04

### Added
- **Integrate open PRs #8 + #9** from `MiaouLeChat929` (external fork). Two new slash commands under `core-principled/commands/`:
  - **`/plan <topic>`** — wraps `plan-lifecycle` in PLAN mode. Asks 2-5 clarifying questions, spawns explorer + researcher subagents in parallel, then hands off to the skill for the full create-plans protocol.
  - **`/plan-execute <path>`** — wraps `plan-lifecycle` in EXECUTE mode against an existing PLAN.md. Picks the right strategy (autonomous/segmented/sequential) and runs workers + critics.
  - These complete the lifecycle surface: `/plan` (create) → `/plan-execute` (run) → `/archive plan-archive` (finalize).
  - File content preserved exactly as the contributor wrote it; commits/CHANGELOG batched at release time per marketplace discipline.

## [1.8.0] — 2026-06-03

### Added
- **`tp-mcp` plugin (0.1.0)**: New domain-specific plugin for MCP (Model Context Protocol) server design and implementation. Three skills covering the full server lifecycle, derived from the design thesis documented in the Kimi brainstorm on the `claude-cli-wrapper` schema:
  - **`mcp-server-design`** (the hub) — Design principles: equilibrated recursivity (flat schema, deep data via pass-through), tool decomposition (1 tool vs N, when to split, the `claude-cli-wrapper` 6-tool case study), output contract (`CallToolResult` text+JSON vs other content types), JSON-RPC error code discipline (`-32602` for schema violations, custom codes for domain failures, `-32603` only for wrapper crashes), tool annotations (readOnlyHint/destructiveHint/idempotentHint/openWorldHint), pass-through principle for deep structures, context budget (≤12 KB total schema, ≤2 KB per tool), capability negotiation (tools/resources/prompts/sampling/elicitation), security MUST/SHOULD checklist (Origin header validation, OAuth Resource Server since June 2025 spec, treat annotations as untrusted), naming conventions, the Claude-Optimal validation checklist.
  - **`mcp-server-implement`** (the production) — Build an MCP server in Rust with `rmcp` + `schemars` + `tokio`. Cargo.toml setup with the right features (`server`, `transport-io`, `transport-streamable-http-server`, `macros`), the macro cheat sheet (`#[tool_router]`, `#[tool_handler]`, `#[tool]`, `Parameters<T>`, `JsonSchema`), schemars attribute mapping table (length/range/regex/format → JSON Schema), enum idioms (rename_all, hyphenated variants), optional field patterns (`skip_serializing_if`), state management with `Arc<Mutex<...>>`, server lifecycle (initialize → capabilities → shutdown), transport choice (stdio vs Streamable HTTP vs legacy HTTP+SSE, decision matrix), stderr-only logging (`tracing-subscriber` with `with_writer(stderr)`), error mapping (`McpError::invalid_request/invalid_params/method_not_found/internal_error`), output construction, testing with the MCP Inspector, building and shipping (cross-compile, LTO/strip).
  - **`mcp-tool-surface`** (the meta) — JSON Schema authoring for tools. Constraint design (enum/pattern/range/format/length for every property), `additionalProperties: false` discipline, `oneOf` vs discriminator-enum tradeoff (the 95/5 rule), `$ref` vs inline, draft-2020-12 selection, required vs optional decisions, the "schema is an LLM instruction manual" framing, description-writing recipe (what/format/constraints/safety), tool name conventions (snake_case, verb_noun, domain prefix when 5+), nested objects (2-level rule), defaults that help, output schemas, common-pitfalls catalog.
- **`claude-cli` skill (claude-cli-wrapper plugin 0.2.0)**: New skill body for the existing `claude-cli-wrapper` plugin. Documents the 6 tools (`claude_execute`, `claude_session`, `claude_context`, `claude_review`, `claude_agent`, `claude_config`), per-tool semantics, key parameters, common workflows (one-shot / multi-turn / background agent / code review / structured output), output contract, and anti-patterns. The skill is the user-facing map of the binary; the design rationale lives in `mcp-server-design`.
- **marketplace.json**: `tp-mcp` plugin entry added (category: development, version 0.1.0). Marketplace catalog version bumped to 0.15.0 (from 0.14.0).

### Design decisions
- **Plugin namespace:** `tp-mcp` (sibling of `tp-git`, `tp-fpf`, `tp-sadd`, `tp-rust`) — keeps the MCP knowledge in its own plugin rather than bloating `core-principled`.
- **3 skills, not 4-5:** The 3 skills have non-overlapping triggers (design / implement / schema authoring) — that's the routing test for whether to split. Quality evaluation and client patterns are deferred follow-ups.
- **JSON Schema 2020-12 default:** Per the MCP spec. Explicit `$schema` field recommended for clarity.
- **Streamable HTTP over legacy HTTP+SSE:** The new standard for remote MCP servers. Legacy HTTP+SSE retained only for backward compatibility with 2024-11-05 clients.

## [1.7.0] — 2026-06-03

### Added
- **`tp-rust` plugin (0.1.0)**: New domain-specific plugin with four skills covering the full Rust project lifecycle, derived from a 4-track research effort (workspace, project layout, tooling, release/dependencies) analyzing 25+ production repositories and 150+ sources:
  - **`rust-scaffold`** — Scaffold a single-crate Rust project (lib, bin, or both) with modern defaults. Default edition 2024, MSRV 1.81, resolver 2, cargo-nextest-ready structure, doctests, MSRV-aware lints. Includes Cargo.toml template, MSRV policy (api-guidelines + RustCrypto camp split), feature flag playbook ("should be additive" with mutual-exclusion escape hatch), rustdoc conventions, edition migration checklist.
  - **`rust-workspace`** — Manage a Cargo workspace: when to split, three workspace anatomy templates, workspace inheritance (1.64+) with the additive-defaults pitfall (cargo #12162), MSRV coordination, cross-crate patterns (reqwest `__internal` feature), real-world patterns table (tokio, axum, ripgrep, cargo, rust-analyzer, deno).
  - **`rust-quality`** — Set up CI + clippy + nextest + coverage + supply-chain ladder. Copy-pasteable GitHub Actions workflow (dtolnay + Swatinem + taiki-e stack), clippy policy (pedantic for libs), nextest profile, cargo-deny `deny.toml` (verified against 0.19+ schema, no `vulnerability`/`unlicensed` removed keys), cargo-vet Stage 2, DX tools (bacon, sccache, mold), criterion benchmarking.
  - **`rust-release`** — Manage the release lifecycle. Cargo semver (pre-1.0 vs 1.0+, MSRV policy decision), changelog tooling decision (git-cliff vs release-please vs hand-curated), publishing playbook (3 hard rules, yank semantics, workspace lockstep), dependency management (MSRV-aware updates, `[patch.crates-io]`, vendoring), supply-chain ongoing maintenance (cargo-vet, Dependabot), feature deprecation 3-step cycle.
- **marketplace.json**: `tp-rust` plugin entry added (category: development, version 0.1.0). Marketplace catalog version bumped to 0.14.0 (from 0.13.0).

### Design decisions
- **Plugin namespace:** `tp-rust` (sibling of `tp-git`, `tp-fpf`, `tp-sadd`) rather than bolting onto `core-principled`. The 4 skills are cohesive and distinct from the existing principles.
- **4 skills, not 3 or 5:** Maps 1:1 to the natural Rust lifecycle (scaffold → structure → quality → release) with minimal overlap. Cross-skill handoffs documented in each skill (e.g., `rust-quality` → `rust-release` for supply-chain ongoing maintenance).
- **Edition 2024 + MSRV 1.81 as defaults:** edition 2024 is stable since Rust 1.85 (Feb 2025); MSRV 1.81 unlocks the MSRV-aware resolver (Sept 2024). Both are ahead of much of the ecosystem but right for new projects.

## [1.6.0] — 2026-06-03

### Added
- **`web-search` skill** (core-principled 0.12.0): tool-agnostic best practices for finding, verifying, and evaluating information on the open web. Merges two competing drafts (information-retrieval lens + epistemology lens) into a single hub: cognitive discipline, query reformulation, source hierarchy (primary → secondary → tertiary), cross-reference verification with 3 gates, 17-row failure-modes table, and the discipline of stopping when an answer is unfindable. Description uses user-vocabulary triggers ("find X", "look up Y", "is this claim true", "what do experts say"). Files: `SKILL.md` + `references/{query-shapes,source-hierarchy,verification-protocol,when-not-to-search}.md`.

### Changed
- **core-principled bumped to 0.12.0** (from 0.11.0) for the new `web-search` skill.
- **marketplace.json**: `core-principled` description updated to mention web search best practices; keywords gain `web-search`, `web-research`, `fact-check`, `source-evaluation`.

### Fixed
- **ddd SKILL.md** (core-principled): Description rewritten from method-leaking to user vocabulary; "What This Skill Changes" section added; QUALITY mode expanded with 5-step Process, 4 Anti-Patterns, 4 Failure Cases; Failure Signal JSON schemas added for ARCHITECTURE and API modes; CONTRAST section added. Token budget ~1,688 tokens (well under 2,000 safe limit).
- **diagnose SKILL.md** (core-principled): H1 renamed to `## Routing Guidance`; original `## Routing Guidance` renamed to `## Activation Triggers`; orphaned Gemba Walk/VSM/Muda Analysis rows removed; CONTRAST section added.
- **ideation SKILL.md** (core-principled): "Create Ideas Mode" expanded from 1-line stub to full 9-line section with anchor/tail subagent roles, synthesis rule, ranked output format; CONTRAST section added.
- **8 skills CONTRAST sections** (core-principled + tp-fpf + tp-sadd + tp-session-audit): Added CONTRAST sections to kaizen, plan-do-check-act, refine, task-lifecycle, subagent-orchestration, fpf, sadd, session-analytics for routing mutual exclusivity.
- **plan-do-check-act SKILL.md** (core-principled): Corrupted fragment "ting why." removed; "Reference Index" renamed to "Agent Spawn Map".
- **session-analytics references** (tp-session-audit): `cross-analyze-protocol.md` and `adjudicate-protocol.md` expanded from stubs to full reference content.
- **CLAUDE.md**: Git Safety Protocol section added — "NEVER use `git reset --hard`" with surgical recovery alternatives.

## [1.5.0] — 2026-06-03

### Changed
- **tp-session-audit plugin**: Merged standalone `capture` skill into `session-analytics` hub as CAPTURE mode. The skill now has four modes: CAPTURE, INSPECT, REVIEW, ISSUE. Added trigger phrases for "capture session", "collect artifacts", "headless capture", "run verification capture", "profile a skill invocation", "audit skill routing", "measure hook in vivo". Removed standalone `plugins/tp-session-audit/skills/capture/` directory.
- **tp-session-audit commands**: Added `commands/capture.md` as thin router to `session-analytics` CAPTURE mode. All four commands now route through the unified hub skill.
- **marketplace.json**: tp-session-audit version bumped to 0.3.0. Description updated to reflect four modes.

### Changed
- **Structural demotion: multi-agent-patterns, tool-design, claude-headless** — These three skills have been demoted from standalone top-level skills to markdown reference files within hub skill `references/` directories:
  - `multi-agent-patterns` → `plugins/core-principled/skills/subagent-orchestration/references/patterns-reference.md`
  - `tool-design` → `plugins/core-principled/skills/subagent-orchestration/references/tool-design.md`
  - `claude-headless` → `plugins/tp-session-audit/skills/session-analytics/references/claude-headless.md`
- **subagent-orchestration SKILL.md**: Updated to imperatively cite both new reference files. `when_to_use` updated to reference `references/patterns-reference.md`. `references/patterns-reference.md` (Architecture Design section) updated to reference `references/frameworks.md` for LangGraph/AutoGen/CrewAI implementations.
- **core-principled plugin.json**: Removed references to deleted skills. Bumped version.
- **Deleted skill directories**: `plugins/core-principled/skills/multi-agent-patterns/`, `plugins/core-principled/skills/tool-design/`, `plugins/core-principled/skills/claude-headless/`.

### Changed
- **task-lifecycle skill**: Added DOCUMENT mode absorbing `update-docs` workflow. New mode handles documentation after IMPLEMENT completes: multi-agent tech-writer flow with analysis + tech-writer + review agents. Task-lifecycle now has four modes: CAPTURE, REFINE, IMPLEMENT, DOCUMENT. IMPLEMENT mode routes to DOCUMENT after Phase 3 (DoD verification) before moving task to done.
- **task-lifecycle/references/documentation.md**: New reference file with README templates, JSDoc patterns, index document checklist, and quality gates migrated from `update-docs`.
- **Deleted skill**: `plugins/core-principled/skills/update-docs/` — capabilities merged into task-lifecycle DOCUMENT mode.

### Changed
- **Agent color standardization**: Assigned semantic `color:` fields to all 27 agent definitions across the marketplace per the Agent Color Convention table in CLAUDE.md:
  - `red` (judges/critics/security): tp-critic, sadd-judge, fpf-logic-verifier, tp-code-reviewer
  - `blue` (architecture/generation/analysis): tp-analyzer, sadd-generator, fpf-hypothesis-generator, tp-plan-architect
  - `green` (implementation/integration): sadd-synthesizer, fpf-evidence-validator, tp-global-implementer, tp-transcript-rules-integrator
  - `yellow` (caution/validation/audit): tp-skill-auditor, fpf-trust-auditor, tp-plan-verifier
  - `purple` (complex reasoning/scoring): tp-comparator, sadd-expander, tp-grader
  - `orange` (meta-evaluator/diagnostic): tp-subagent-auditor, sadd-meta-judge, meta-reviewer, tp-transcript-rules-analyzer
  - `pink` (distinctive specialist): tp-transcript-rules-auditor
  - `cyan` (investigation/research/tracing): sadd-explorer, tp-test-strategist, tp-explorer, tp-researcher, tp-debug-tracer

## [1.4.0] — 2026-06-02

### Changed
- **tp-sadd agents**: Renamed with `sadd-` prefix in both filename and frontmatter `name` field to match spawn directives in `sadd` skill. Agents affected: `explorer` → `sadd-explorer`, `judge` → `sadd-judge`, `meta-judge` → `sadd-meta-judge`, `generator` → `sadd-generator`, `synthesizer` → `sadd-synthesizer`, `expander` → `sadd-expander`.
- **tp-fpf agents**: Renamed with `fpf-` prefix in both filename and frontmatter `name` field to match spawn directives in `fpf` skill. Agents affected: `hypothesis-generator` → `fpf-hypothesis-generator`, `evidence-validator` → `fpf-evidence-validator`, `logic-verifier` → `fpf-logic-verifier`, `trust-auditor` → `fpf-trust-auditor`.
- **session-analytics CROSS-ANALYZE**: Fixed cross-plugin reference from `taches-principled:debug-tracer` to `core-principled:tp-debug-tracer`.
- **session-analytics ADJUDICATE**: Fixed agent references: `tp-sadd:judge` → `tp-sadd:sadd-judge`, fallback updated to `core-principled:tp-critic`.
- **marketplace.json**: Bumped to 0.12.0.
- **core-principled plugin.json**: Bumped to 0.10.1.
- **README.md**: Updated version to 0.12.0.

## [1.3.0] — 2026-06-02

### Changed
- **core-principled project-maintenance skill**: Merged `archive-plan` (plan archival + learnings extraction) and `memory-curator` (memory audit/dedup/archive/clean) into a single hub skill with five modes — `PLAN-ARCHIVE`, `MEMORY-AUDIT`, `MEMORY-DEDUP`, `MEMORY-ARCHIVE`, `MEMORY-CLEAN`. The /archive command now routes to the unified skill. Removed the two old skills; bumped `core-principled` to 0.10.0.
- **/archive command**: Now a thin router into the unified skill (no body duplication). Argument-hint exposes all five modes plus `--abandoned` (PLAN-ARCHIVE override) and `--days` (memory age threshold).
- **refine MEMORIZE + rules-orchestration SYNC**: Updated CONTRAST references from `archive-plan` to `project-maintenance PLAN-ARCHIVE`. The writer/reader topology is unchanged.
- **MEMORY-DEDUP / MEMORY-CLEAN accuracy**: Replaced the false `--directory` and `--yes` flag claims (which `dedup.py` does not implement) with the script's actual CLI (`directory` positional, `--threshold`, `--format`) and clarified that the script is read-only — resolution is performed by the agent via MEMORY-ARCHIVE. The safety boundary is now explicit user confirmation in conversation, not a `--yes` flag. SKILL.md `argument-hint` and body are now consistent (no `--yes`/`--dry-run` claim).
- **MEMORY-ARCHIVE archive location**: Aligned all mode examples on `~/.claude/archive/memory/{category}/{date}/` (the manifest format). The MEMORY-DEDUP example previously showed `~/.claude/archive/memory/2025-05/` (missing the `{category}/` segment) — now correct.
- **marketplace.json**: Bumped to 0.11.2 (was 0.11.1). `tp-force-multiplier` removed (no longer in this marketplace); `tp-session-audit` retained.

### Added
- **project-maintenance references/memory-locations.md**: New tiny reference extracting the memory-location list that was previously inlined in both AUDIT and CLEAN modes.

### Removed
- `core-principled/skills/archive-plan/` (moved into `project-maintenance`)
- `core-principled/skills/memory-curator/` (moved into `project-maintenance`)

## [1.2.0] — 2026-06-02

### Added
- **tp-meta capture skill**: New skill that runs `claude -p` headless capture with canonical behavioral-verification flags. Produces three artifacts: debug log, stream-json output, persisted JSONL. Triggers on "capture session", "profile a skill invocation", "run verification capture".
- **tp-meta session-inspect multi-artifact routing**: Extended INSPECT mode to route by artifact type — `.jsonl` → JSONL parser, `.debug.log` → debug-log parser (extracts [HOOK]/[API]/[PERMISSION]/[ERROR] events), `.stream.jsonl` → stream-json parser (per-turn delta events).
- **tp-meta meta-review CROSS-ANALYZE mode**: New mode fans out three parallel specialists (forensic-analyst on stream-json, meta-reviewer on JSONL, debug-tracer on debug log), detects convergence across analysts. High-convergence findings (≥2 analysts) are the highest-signal outputs.
- **tp-meta meta-review ADJUDICATE mode**: New mode validates each cross-analyze finding with parallel evidence-validator + adversarial challenge. Classifies findings as validated/speculative/rejected. Uses `background: true` for concurrent per-finding validation.

### Changed
- **session-inspect description**: Added trigger phrases for parsing debug logs and stream-json ("parse debug log", "analyze hook events", "extract hook fires")

## [1.1.0] — 2026-06-02

### Fixed
- **meta-issue skill**: Fixed label creation order for non-admin users — issue now creates cleanly without label when gh label create fails due to insufficient permissions
- **tp-force-multiplier hook**: Rewrote SessionStart hook with conditional three-gate coaching instead of "all capabilities are mandatory" anti-pattern
- **tp-critic agent**: Commented out cross-plugin dead skill references (fpf, sadd, ddd, tdd, kaizen) for partial-install safety

### Changed
- **10 agent renames**: Dropped `fpf-` and `sadd-` filename prefixes across tp-fpf (4 agents) and tp-sadd (6 agents)
- **sadd JUDGE triggers**: Replaced bare-verb triggers with phrase-level specific ones to resolve routing collisions
- **create-plans skill**: All critic-loop sites now reference MAX_ITERATIONS=3 (per evaluation-protocol.md); vague template paths replaced with explicit `templates/brief.md`
- **execute-plans skill**: All critic-loop sites now bounded by MAX_ITERATIONS (3 for milestone, 2 for pre-execution/per-task); template paths now explicit
- **orchestrate command**: Expanded from 3-line stub to 8-step protocol referencing scratchpad, evaluation-protocol, and subagent-orchestration skill

### Added
- **orchestrate-solo command**: New first-class lightweight mode command — no subagents, no scratchpad, no critic loop; sequential in-context execution for small tasks
- **archive-plan hard precondition**: Phase 1 now enforces SUMMARY.md existence with structured JSON failure signal and --abandoned override path
- **subagent-orchestration routing**: Added --solo/--lightweight decision rules to skill Decision Router

### Removed
- **sadd JUDGE**: 5 bare-verb trigger phrases that caused routing collisions with refine/diagnose/git/create-plans

## [0.12.1] — 2026-06-02

### Added
- **`memory-curator` skill** (moved from `tp-vps-governance`): Audits, deduplicates, and archives Claude Code memory files. Modes: AUDIT, DEDUP, ARCHIVE, CLEAN. Includes `scripts/dedup.py` for semantic deduplication via Jaccard similarity.
- **`rules-orchestration` AUDIT mode**: Analyzes CLAUDE.md hierarchy for conflicts, duplications, and cross-file contradictions. Extracted from `config-auditor`.
- **`plan-verifier` agent tools**: Added `Write` and `Edit` to the allowlist for scratchpad-first evaluation protocol compliance.

### Removed
- **`tp-vps-governance` plugin**: Deleted after capability migration to core plugin. `config-auditor` absorbed into `rules-orchestration` AUDIT mode; `memory-curator` moved to `plugins/taches-principled/skills/memory-curator/`.

## [0.12.0] — 2026-06-01

### Changed
- **`tp-meta` consolidated into single hub skill `session-analytics`**: Merged `meta-issue`, `meta-review`, and `session-inspect` into one skill with INSPECT / REVIEW / ISSUE decision router. Each mode has its own reference file (`references/inspect-reference.md`, `references/review-reference.md`, `references/issue-reference.md`). Commands updated to target the new hub skill. Plugin version bumped to 0.2.0.

### Removed
- **`meta-issue`, `meta-review`, `session-inspect` skills** (3 directories): Superseded by `session-analytics` hub.

## [0.11.1] — 2026-06-01

### Changed
- **Dissolved `scope-work` skill**: The hollow router (`add-task`/`refine-task`/`create-plans` routing) was removed — its three spoke files never existed and its triggers conflicted with `add-task`. Lifecycle skills now self-route via their existing CONTRAST frontmatter. References updated in `ideation`, `archive-plan`, `execute-plans`, and `refine`.
- **`sadd` DESIGN mode merged into `subagent-orchestration`**: Architecture design capability consolidated into the core `subagents` hub. `sadd` now redirects DESIGN to `subagent-orchestration` and focuses on COMPETE/JUDGE/EXECUTE/EXPLORE competitive evaluation. `sadd-architect` agent deleted as orphaned.
- **`kaizen` / `ddd` relationship clarified**: Both skills updated with explicit "Relationship" sections — `kaizen` as continuous design-time guardrails (the immune system), `ddd` as specialist structural analysis (called in for diagnosis). Mutual cross-references added.
- **Shared evaluation protocol extracted**: `execute-plans`, `refine-task`, and `implement-task` now reference `execute-plans/references/evaluation-protocol.md` for the shared judge pattern (chain-of-thought, MAX_ITERATIONS, 5.0/5.0 hallucination guard, scratchpad-first, weighted rubrics). Prevents drift across the three skills.
- **Memory/learnings handoff chain made explicit**: `archive-plan`, `refine` (MEMORIZE mode), and `rules-orchestration` (SYNC mode) now have explicit CONTRAST cross-references documenting the two-writers/one-reader chain feeding `.principled/memory/learnings.md`.

### Removed
- **`scope-work` skill** (4 files): `SKILL.md` + `references/{nano-spec,task-spec,roadmap}.md` — no spoke bodies, routing superseded by direct CONTRAST routing in lifecycle skills.
- **`sadd-architect` agent**: Orphaned when DESIGN mode moved to `subagent-orchestration`.

## [0.11.0] — 2026-06-01

### Added
- **scope-work skill** (canonical plugin): Unified entry point for task lifecycle — infers work scale from input and routes to `add-task` (nano-spec), `refine-task` (task-spec), or `create-plans` (roadmap). 261 lines across SKILL.md + 3 references.
- **New official docs**: `docs/official/permissions.md` and `docs/official/plugins/plugins-reference.md` (refreshed from source).

### Changed
- **Skills preloading philosophy — "Better too much than not enough"**: Retired the restrictive rule limiting skill preloading to evaluation/critique agents only. All potentially relevant skills MUST now be preloaded on all agent types (execution, research, explorer, etc.) for deterministic capability access. Properly authored skills use progressive disclosure — baseline context consumption is extremely low (~500 tokens frontmatter + body, references on-demand). AI retains full autonomy to lazy-load deeper reference files based on task requirements. Updated `docs/official/agent-skill-integration.md`, `plugins/taches-principled/skills/subagent-orchestration/SKILL.md`, and CLAUDE.md.

- **Skill file path referencing standardized**: Eradicated `{baseDir}` and `${CLAUDE_SKILL_DIR}` variables from all skill bodies and references (12 files). Established two canonical rules: (1) paths resolve within the skill's folder by default, (2) only SKILL.md may cite supporting files — reference files must never cross-cite. Converted all passive citations ("You can read", "See reference") to deterministic IF→BEFORE imperatives. Documented in CLAUDE.md and skill-authoring SKILL.md.
- **Native Tool Referencing standard**: Eradicated hardcoded tool names from orchestration directives across 11 files. `Write tool access` → `write access`, `"use the Read tool"` → `"use your native tools"`, etc. This ensures forward compatibility when the underlying API migrates (e.g., Task→Agent rename). Documented in CLAUDE.md and skill-authoring SKILL.md as a core best practice.
- **CLAUDE.md Skill Discovery**: Rewrote section as "Skill Discovery & Routing Metadata" — explicitly names routing-participant fields (description, when_to_use only), defines the "Metadata-Only Gate" concept, elevates 200-char rule, and adds Anti-Pattern "No Method Leaking" with bad/good examples.
- **Skill descriptions cleaned** (5 skills, jargon → user vocabulary):
  - `diagnose`: "A3, Five Whys, Fishbone, Stack Trace" → "Find root causes of recurring problems, failed fixes, and complex bugs"
  - `security`: "SAST, DEPENDENCY-AUDIT, SECRETS-DETECTION, COMPLIANCE" → "Scan for security vulnerabilities, exposed secrets, and broken authentication patterns"
  - `kaizen`: "YAGNI" → "avoid over-engineering"
  - `plan-do-check-act`: "PDCA cycle" → "Plan a change, try it at small scale, measure results"
  - `tdd`: "Red-Green-Refactor TDD" → "Write tests first, then implementation"
- **Must-do cleanup pass** (commit `55a6ba0`):
  - H1: Removed 2 tracked `.pyc` files; broadened `.gitignore` to `plugins/**/__pycache__/`
  - H2: Fixed broken CONTRAST references to non-existent `rule-propagator`
  - H4: Standardized `tp-force-multiplier` author to "Felix" across all 9 plugins
  - H5: Added `repository`, `license`, `keywords` to all marketplace.json entries
  - M3: Moved `commands-standard.md` to `docs/templates/command.md`
  - M4: Stripped redundant `shell: bash` from 33 files
  - M5: Stripped redundant `user-invocable: true` from 2 files
  - M6: Stripped dead YAML frontmatter from 15 templates/workflows
- **Plugin subagent rename for global uniqueness**: prefixed plugin subagents to avoid collisions when the `Agent` tool resolves across the marketplace:
  - `plugins/taches-principled/skills/create-plans/agents/{architect,explorer,implementer}` → `plan-{architect,explorer,implementer}`
  - `plugins/taches-principled/skills/rules-orchestration/agents/{rules-analyzer,rules-auditor,rules-integrator}` → `transcript-rules-{analyzer,auditor,integrator}`
  - `plugins/tp-sadd/agents/{architect,explorer}` → `sadd-{architect,explorer}`
  - `plugins/taches-principled/agents/implementer` → `global-implementer`
  - `plugins/taches-principled/skills/execute-plans/agents/researcher` → `execute-researcher`
- **README brittleness reduction**:
  - Stripped 4 magic-number count headers (`### 23 Skills`, `### 14 Commands`, `### 13 Agents`, `### 8 Marketplace Plugins`).
  - Collapsed 3 enumeration tables (Skills, Commands, Agents) to 5 curated examples each + filesystem pointers.
  - Fixed unclosed code block fence in "Full Marketplace Setup" (line 110).
  - Added `### README Hygiene` subsection to CLAUDE.md "Before Any Commit" self-check to make the discipline explicit.
- **CLAUDE.md description cap reconciliation**: changed self-check from `≤150 chars` to `≤1,536 chars` (combined `description` + `when_to_use`) to match the official cap per `docs/official/skills.md`.

### Removed
- **Orphan agent files** (untracked, unreferenced, superseded): `global-rules-{analyzer,auditor,integrator}.md` — the `transcript-rules-*` agents in `rules-orchestration/` do this work.
- **Empty directories**: `plugins/taches-principled/rules/`, `plugins/tp-vps-governance/agents/`.
- **Tracked Python bytecode** (2 files in `tp-force-multiplier/hooks/__pycache__/`).
- **Stale `.gitignore` line** referencing the removed `launch-subagent` skill directory.

## [0.10.0] — 2026-05-29

### Added
- **tp-meta plugin**: Session meta-review and behavioral analysis plugin with 3 skills, 1 agent, and 3 commands.
  - `session-inspect` skill: parses Claude Code session transcripts (JSONL) into structured data — tool calls, errors, cost, loaded plugins, behavioral events.
  - `meta-review` skill: reviews sessions for behavioral anti-patterns, investigates root causes with parallel subagent fan-out, and produces scoped findings.
  - `meta-issue` skill: creates GitHub issues from meta-review findings, sanitized for public sharing with privacy audit gate.
  - `meta-reviewer` agent: diagnostic agent that reads JSONL transcripts and identifies tool misuse, skipped verifications, and instruction-following failures with root cause scoping (PLUGIN/USER-FILE/ENVIRONMENT/MODEL).

## [0.9.0] — 2026-05-27

### Added
- **tp-force-multiplier plugin**: Hook-driven coaching plugin that steers Claude to use subagents and skills more via real-time semantic coaching. Three hooks: SessionStart (lightweight hint), Stop (pattern detection with 5+ tools), PostCompact (pre-pressure reminder). No tool injection, zero blocking, semantic patterns only.
- **CLAUDE.md rules**: Added 4 new rules for instruction clarity
  - Deterministic Language for Execution Rules (strong vs soft language calibration)
  - Infrastructure Assumption Rule (verify prerequisites before dependent operations)
  - Path Configuration Rule (use arguments, not hardcoded paths)
  - Agent Tool Contract Rule (tools must match stated capabilities)

### Changed
- **references/official/**: Updated hooks.md, skills.md, subagents.md, commands.md, and marketplaces.md with marketplace conventions (effort/effort field, shell: bash, hub skills, {baseDir} syntax, CONTRAST sections, maxTurns:15, memory:local, canonical spawn vocab, command format)

### Changed
- **Lifecycle hints removed**: Removed soft-orchestration lifecycle hints from add-task, create-prompts, implement-task per debate WEAK verdict — CONTRAST sections and decision routers are sufficient for routing
- **test-orchestration**: Added CONTRAST section clarifying distinction from test strategy skill
- **refine-task**: Trimmed business analysis section (70 lines removed) — procedure condensed to principle
- **implement-task**: Trimmed Pattern B/C detailed walkthroughs (150 lines removed) — step-by-step scripts condensed to policy

### Fixed
- **tp-force-multiplier hooks.json**: Fixed format from array-based to nested object structure per Claude Code hooks reference — changed `{"hooks": [{event:..., ...}]}` to `{"hooks": {"EventName": [{matcher:..., hooks:[...]}]}}`
- **Routing BLOCKERs** (3): Removed overlapping trigger phrases causing routing conflicts
  - refine-task: removed "plan this out", "/plan", "make this actionable", "break this down into steps"
  - execute-plans: removed "execute" from description and when_to_use
- **Failure signal BLOCKERs** (2): Added missing Failure Signal sections
  - ideation: added no-viable-options/user-abandoned/scope-too-broad failure modes
  - claude-headless: added session-timeout/permission-denied/tool-unavailable failure modes
- **Git availability**: Added `git --version` checks to implement-task and refine-task
- **Judge tool mismatch**: Added Write tool to judge.md for filesystem communication
- **TDD Iron Law contradiction**: Removed "write tests" from TDD triggers (Iron Law forbids without failing test first)
- **tp-force-multiplier hooks**: Fixed prescriptive language → advisory ("Pattern: X suggests Y")
- **tp-sadd agent tools**: Added Bash to meta-judge/judge, removed unused Edit from generator
- **create-plans/agents**: Added missing spawn footer to implementer

### Changed
- **METHOD over-specification** (249 lines removed across 4 skills):
  - fpf: 7-step procedure → principle statements
  - diagnose: A3/Five Whys/Fishbone condensed
  - create-plans: 11-item fan-out → 4 principles
  - execute-plans: Strategy A 12-step → 5 principles, deviation rules trimmed
- **Trigger optimization** (5 skills improved):
  - tp-fpf: removed jargon (ADI, R_eff), lead with user vocabulary
  - multi-agent-patterns: rewritten for cold-start clarity
  - tp-ddd: modes moved out of first line
  - security: triggers capped at 3-4 per mode
  - tp-sadd: softened jargon ("meta-judge" → "quality verification")
- **METHOD reduction round 2** (1,212 lines removed across 6 skills):
  - implement-task: 520→181 (-65%), subagent-orchestration: 592→213 (-64%)
  - create-prompts: 493→187 (-62%), execute-prompts: 273→149 (-45%)
  - add-task: 94→58 (-38%), ideation: 94→66 (-30%)
- **Skill discovery optimization**: Added CLAUDE.md section on reliable triggering, hook limitations, validation protocol

## [0.7.0] — 2026-05-25

### Added
- **rules-orchestration skill**: Full lifecycle orchestration hub (6 modes: DESIGN/BUILD/ANALYZE/SYNC/REVIEW/EXECUTE) — orchestrates multiple rule sources into unified rule sets with fan-out/subagent coordination, 3-phase plan, 8 tasks committed

### Changed
- **Lifecycle continuation handoffs**: Implemented 6 lifecycle chains across ideation→add-task→refine-task→implement-task→create-prompts→execute-prompts with soft-orchestration pattern via description hints

## [0.6.0] — 2026-05-25

### Added
- **5 new skills**: Integrated from local ~/.claude/skills/
  - `claude-headless` — Claude Code headless execution patterns, evaluation pipeline anchor
  - `multi-agent-patterns` — Architecture design patterns (supervisor/swarm/hierarchical)
  - `tool-design` — Agent tool and MCP integration design with production evidence
  - `security` — SAST, dependency audit, secrets detection, compliance (OWASP Top 10)
  - `test` — Test strategy decisions (coverage, mock strategy, fixtures, property-based)

### Changed
- **subagent-orchestration**: Merged with `subagent-creator` — now a 2-mode hub (DESIGN/ORCHESTRATE)
- **plugin.json**: Version bumped to 0.6.0, description updated with new capabilities, new keywords
- **Skill count**: 20 → 25 skills (within optimal 22-28 range)

### Removed
- **subagents**: Deleted as duplicate — `subagent-orchestration` is now the canonical hub
- **14 absorbed skills** (from 0.5.0): `reflexion`, `write-concisely`, `create-subagents`, `subagent-orchestration` (root), and 10 individual tp-* skill files superseded by hub equivalents

## [0.5.0] — 2026-05-24

### Added
- **6 new commands**: `/improve`, `/critique`, `/learn`, `/polish`, `/orchestrate`, `/design-subagents` — direct capability triggers routing to hub decision routers
- **Hub-and-spoke consolidation**: reduced marketplace from 34 skills to 20 (41% reduction, 5,952 lines removed)
  - Root: `refine` now a 5-mode hub (SIMPLIFY/REVIEW/CRITIQUE/MEMORIZE/POLISH) absorbing `reflexion` + `write-concisely`
  - Root: `subagents` now a 2-mode hub (DESIGN/ORCHESTRATE) absorbing `create-subagents` + `subagent-orchestration`
  - tp-sadd: 5 skills merged into `sadd` hub
  - tp-git: 4 skills merged into `git` hub
  - tp-fpf: 3 skills merged into `fpf` hub
  - tp-ddd: 3 skills merged into `ddd` hub

### Changed
- **CLAUDE.md**: comprehensive audit — Meta-Rule rewritten for human maintainers, dispatch/launch terminology standardized to spawn, reflexion/refine narrative corrected, direct-language principle enforced, Self-Check strengthened, logical weaknesses fixed, missing definitions added
- **Commands**: 6 existing commands updated with hub skill routing, all 12 commands verified against commands-standard.md

### Removed
- **14 absorbed skills**: `reflexion`, `write-concisely`, `create-subagents`, `subagent-orchestration` (root), and 10 individual tp-* skill files superseded by hub equivalents
- **`coordination.py`** script and design reference files consolidated into hub skill bodies

### Fixed
- **Token Economy**: removed contradictory line advising writing to non-loaded CLAUDE.md
- **Subagent spawn instructions**: all inline tool lists replaced with role + outcome descriptions
- **Cross-references**: all stale references to deleted skills cleaned before deletion
- **marketplace.json**: root skill count corrected 18→15

## [0.4.1] — 2026-05-23

### Fixed
- **tp-ddd plugin**: Converted 14 invalid rules (in `rules/` with `title`/`impact` frontmatter) to 12 valid skills (in `skills/` with `name`/`description`/`when_to_use` frontmatter)
- **tp-ddd**: Merged overlapping skills (call-site-honesty→explicit-side-effects, clean-architecture-ddd→separation-of-concerns)
- **tp-ddd**: Improved when_to_use triggers with natural developer phrases

### Changed
- **tp-ddd**: Collapsed 12 skills → 3 hub skills (code-transparency, code-architecture, code-quality) via multi-agent consolidation pipeline
- **tp-ddd**: description updated to reflect new skill structure

### Fixed
- **tp-ddd**: Lost concepts (early returns, file size limits) restored after Skeptic-Advocate reconciliation

## [0.4.0] — 2026-05-23

### Changed
- **marketplace.json**: Bumped to 0.4.0, 7 entries (root + 6 separate plugins)
- **plugin.json**: Version remains 0.4.0
- **CHANGELOG**: Removed 68 skills count claim (was inaccurate)

### Added
- **when_to_use frontmatter**: Added to all 34 skills with user-quoted trigger phrases and IMMEDIATELY/FIRST/BEFORE conditionals

### Fixed
- **sadd-dispatch**: Added missing when_to_use section entirely
- **tp-sadd/tp-sdd plugins**: All skills now have proper trigger phrase quoting and temporal markers (tp-sdd deprecated, consolidated into root)

### Refactored
- **All 34 skill descriptions**: Normalized to third-person framing with trigger phrases (note: official docs confirm verb-first is valid)
- **Agent definitions**: XML Structure Rules converted to markdown Structure Conventions

## [0.3.0] — 2026-05-22

### Added
- **22 root skills**: Integrated review (review-pr, review-local-changes), kaizen (kaizen, analyse, analyse-problem, cause-and-effect, plan-do-check-act, root-cause-tracing, why), and docs (update-docs, write-concisely) into root plugin
- **5 separate plugins**: Ported from context-engineering-kit — tp-sadd (9 skills), tp-fpf (3 skills), tp-git (4 skills), tp-session-audit, tp-ddd (14 rules) (tp-sdd deprecated and consolidated into root)
- **Decision routers**: All 60 skills now have IF/THEN decision routers at top
- **Semantic vocabulary**: Cross-plugin synergy through shared workflow vocabulary (no plugin name references)
- **Integration architecture**: `.principled/plans/BRIEF.md`, `ROADMAP.md`, `scratch/integration-architecture.md`, `scratch/fan-out-plan.md`
- **Phase summaries**: `.principled/plans/phases/00-scaffold/SUMMARY.md`, `01-reflexion/SUMMARY.md`

### Changed
- **plugin.json**: Bumped to 0.3.0, updated description with full lifecycle scope
- **marketplace.json**: Bumped to 0.4.0, 7 entries (root + 6 separate plugins)
- **CLAUDE.md**: Added Plugin Management section for multi-plugin marketplace operations

### Fixed
- Cross-plugin naming violations: all 60 skills use semantic vocabulary instead of plugin name references
- XML tags removed from all ported content (markdown headings only)
- Threatening language removed from SADD and reflexion skills (professional tone)
- Meta-judge pattern deduplicated across 10 SADD skills (was 4,000 lines of copy-paste)

## [0.2.0] — 2026-05-22

### Added
- **code-simplify skill**: Simplification pipeline with 5 stages (Extract & Name, Reduce Nesting, Remove Duplication, Eliminate Dead Code, Replace State Machines with Data), anti-patterns with wrong/right pairs, inline agent template, Policy/Mechanism framing, numeric thresholds, and language-specific references for JS/TS, Python, Go, and Ruby
- **code-simplify skill**: `references/language-patterns.md` with language-specific patterns
- **code-simplify skill**: `references/simplification-scope.md` with scope boundaries and file ownership rules
- **commands/simplify.md**: `/simplify` command for direct invocation with optional file-pattern argument
- **plugin.json**: Bumped to 0.2.0, added code-simplify keyword

## [0.1.0] — 2026-05-22

### Added
- **create-skills skill**: Decision Router with IF→FIRST/IMMEDIATELY/BEFORE imperative conditionals at top
- **create-skills skill**: Five skill categories with inspirational examples (Constraint/Guardrail, Orchestration, Domain Expertise, QA, Creative Direction)
- **create-skills skill**: Added Success Criteria section with measurable outcomes
- **create-skills skill**: Added `trigger-benchmark.md` reference (305 lines): 20-query framework, exit criteria, overfitting detection, headless testing method
- **create-skills skill**: Added Automated Checks section to `skill-self-testing.md`: programmatic pre-commit validation script
- **create-skills skill**: Added `scripts/run_trigger_benchmark.py`: automated 20-query test harness with streaming JSONL detection
- **create-skills skill**: Added `scripts/grader-output-template.md`: structured output format for grader → analyzer pipeline
- **execute-plans skill**: Decision Router with strategy selection based on checkpoint types
- **execute-plans skill**: Added Numeric Thresholds section
- **agents/**: New grader, comparator, and analyzer agents for evaluation pipeline
  - `grader.md` (161 lines): Teaching effectiveness rubric with 4 dimensions (Routing Signal, Delta Clarity, Teaching Posture, Anti-Pattern Quality)
  - `comparator.md` (115 lines): Skill version comparison for delta analysis
  - `analyzer.md` (96 lines): Synthesizes evaluations into prioritized improvement path
- **agents/skill-auditor.md**: Added Trigger Benchmark Integration section; added Evaluation Pipeline section documenting multi-agent evaluation workflow
- **CLAUDE.md**: Added Evaluation Pipeline section documenting the grader/comparator/auditor/benchmark/analyzer multi-agent system
- **create-subagents skill**: Multi-agent patterns import from taches-modernized research
  - `references/gotchas.md` (443 lines): Eight critical production gotchas (supervisor bottleneck with 3-5 worker cap, 15x token cost, sycophantic consensus, agent sprawl, telephone game, error propagation cascades, over-decomposition, missing shared state)
  - `references/fault-tolerance.md` (310 lines): Circuit breaker pattern, checkpoint/resume, exponential backoff, idempotent operations
  - `references/token-economics.md` (230 lines): Real multi-agent cost breakdown (~15x baseline), when justified, model selection vs token budget
  - `references/consensus.md` (386 lines): Weighted voting (confidence × expertise), debate protocol, adversarial critique, convergence detection
- **create-subagents skill**: Extended decision router with 5 new routes to new references
- **create-subagents skill**: Added Multi-Agent Gotchas section with hard cap enforcement
- **orchestration-patterns.md**: Added Swarm pattern (peer-to-peer), forward_message pattern (telephone game mitigation), 4 new anti-patterns
- **context-management.md**: Added Context Isolation Mechanisms (3-mechanism taxonomy), Context Degradation Signals
- **execute-plans skill**: Added supervisor bottleneck warning with 3-5 worker cap enforcement
- **create-plans skill**: Added context degradation signals to scope-estimation.md
- **execute-plans skill**: Critical fixes from second round of critic review
- **create-skills skill**: Comprehensive improvements from critic review
- **create-skills skill**: Now teaches bundled agents pattern
- **create-skills skill**: Native task lists + semantic-first skill refactor
- **execute-plans skill**: Added agents/critic.md for milestone self-review
- **create-plans skill**: Added agents folder with subagent prompt templates
- **execute-plans skill**: Added env-variable-pattern reference doc for portable skill paths
- **subagent-orchestration skill**: Integrated as 7th skill with RACE framework, five parallel patterns, three automation layers, memory architecture, and failure modes
- **create-subagents skill**: Added plugin scope gotcha (hooks/mcpServers/permissionMode silently ignored for plugin subagents), Task→Agent renaming note (v2.1.63), missing frontmatter fields (skills, memory, background, maxTurns, isolation)
- **create-skills skill**: Added 3-level progressive disclosure pattern (Level 1 ~100 tokens always, Level 2 ~5k on trigger, Level 3 0 via bash injection)
- **create-plans skill**: Added bash injection = 0 context cost pattern
- **execute-plans skill**: Added Explorer Subagent Protocol for investigation tasks via scratchpad coordination
- **execute-prompts skill**: Added Explorer Subagent Protocol and Thought/Action/Observation anti-pattern
- **create-skills skill**: Added Fresh Context Warning for subagent spawning (no inheritance from orchestrator)
- **all root agents**: Added spawn footers and failure signal sections to all 7 root-level agents

### Fixed
- **execute-plans skill**: Fixed broken {baseDir} reference — orchestration-patterns.md now uses natural language (file lives in create-plans skill)
- **execute-plans skill**: Fixed critic agent name collision with create-plans (critic → execute-critic)
- **README.md**: Fixed skill count (6→7) and agent count (4→7), added subagent-orchestration rows
- **CLAUDE.md**: Fixed stale version example (1.1.0→0.1.0)
- **marketplace.json**: Added missing top-level description for validation cleanliness
- **CHANGELOG.md**: Fixed stale agent line counts for comparator.md and analyzer.md
- **execute-plans skill**: Use agents/critic.md template for milestone reviews
- **create-plans skill**: Resolve inconsistencies found during reference review
- **create-plans skill**: Resolve critical issues found during reference review
- **execute-plans skill**: Fixed agent template paths to use {baseDir} for plugin portability
- **create-plans skill**: Fixed agent folder references to use {baseDir} for plugin portability
- Corrected GitHub repo references across plugin

### Changed
- **Version**: Bumped from 0.0.2-alpha to 0.1.0 (plugin now has 7 skills, 7 root agents, evaluation pipeline)
- **CLAUDE.md**: Reduced from ~475 lines to ~178 lines by moving teaching content to skills ( marketplace operations only)
- **create-plans skill**: Complete remaining deferred improvements from reference review
- Marked all deferred improvements from reference review as resolved
- **create-plans skill**: Remove per-file version tracking (anti-pattern)

## [0.0.2-alpha]

### Added
- **create-plans skill**: Added `agents/` folder with subagent prompt templates (explorer, researcher, architect, implementer, verifier)
- **create-plans skill**: Added fan-out exploration pattern with parallel subagent spawning guidance
- **create-plans skill**: Natural language instructions for reading agent prompts and filling placeholders
- **execute-plans skill**: Added `agents/critic.md` for formalizing milestone self-review pattern
- **CLAUDE.md**: Added Semantic-First Skill Design section with progressive disclosure architecture

### Fixed
- **marketplace.json**: Changed `source.github.repo` to `source.source: "url"` with full git URL — `felixhopper` repo does not exist, corrected to `Git-Fg/taches-principled`
- **README.md**: Replaced all `felixhopper` references with `Git-Fg` (lines 13, 125)
- **README.md**: Corrected skills count (6 skills now) and commands count (10 → 2)
- **execute-plans/SKILL.md**: Removed duplicate "Strategy B" section header in Strategy A content
- **sequential-execution.md template**: Fixed `Sonnets/Large Context Executor` → `Sonnet` (valid model name)
- **autonomous-execution.md**: Removed duplicate rollback sections, clarified revert scope
- **autonomous-execution.md**: Removed invalid Task() spawn syntax, replaced with plain-text instruction
- **autonomous-execution.md**: Added spawn footer to worker prompt structure
- **segment-execution.md**: Added milestone self-review section, integrated critic.md reference, added spawn footer
- **sequential-execution.md**: Replaced inline deviation rules with reference to deviation-rules.md
- **execute-phase.md**: Added YAML frontmatter per skill anatomy standards
- **execute-prompts/SKILL.md**: Removed Task tool prose references, replaced with semantic delegation language
- **cli-automation.md**: Marked Railway as deprecated (discontinued 2024), added Cloudflare/AWS/GCP/Bun platforms
- **milestone-management.md**: Updated all 2025 dates to 2026, added hotfix branch model
- **plan-format.md**: Removed duplicate Summary Output section, cross-referenced SKILL.md, added Checkpoint field
- **checkpoints.md**: Added human-readable comment pattern, added Escalation and Timeout section
- **scope-estimation.md**: Defined context usage metrics, added sequential chain limit
- **create-plans SKILL.md**: Simplified fan-out description, removed Task: spawn examples
- **create-plans/references/**: Removed per-file version tracking (anti-pattern documented in CLAUDE.md)

## [0.0.1-alpha]

### Added
- **create-prompts skill**: Creates executable XML-structured prompts for Claude Code sessions
  - Adaptive intake gate with task type detection
  - Contextual questioning with templates (dashboard type, auth method, etc.)
  - Decision gate loop until user confirms
  - Single/parallel/sequential prompt generation
  - XML patterns for coding/analysis/research tasks
- **execute-prompts skill**: Executes prompts via delegated sub-tasks
  - Policy vs. Mechanism framing for strategy selection
  - Single/parallel/sequential execution via Task tool
  - Critical constraint: parallel Task calls in single message
  - Argument parsing and file resolution
  - Archival to `./prompts/completed/` and git workflow
- **create-prompts/workflows/execute-prompt.md**: Workflow reference for prompt execution

### Changed
- README updated: Skills count 4 → 6, Policy/Mechanism table expanded

## [1.1.0]

### Changed
- Renamed from `taches-modernized` to `taches-principled`
- All 4 skills enhanced with Policy/Mechanism framing sections
- All 4 skills enhanced with Anti-Patterns sections
- All 4 skills enhanced with Numeric Thresholds tables
- README updated with Skill Ecosystem dependency map
- README updated with Policy vs. Mechanism table

### Removed
- MCP server creation skill and command (builds on existing MCP tooling instead)

### Fixed
- create-hooks: UserPromptSubmit added to events table
- create-hooks: malformed hookSpecificOutput JSON fixed
- create-hooks: broken jq syntax in prettier example
- create-hooks: broken reference to user-gates.md removed
- create-plans: missing frontmatter added
- create-subagents: missing frontmatter added, broken file references removed
- create-mcp-servers: Rule 2 (cwd vs --directory) clarified
- All reference files gained frontmatter

## [1.0.0] — Initial release

### Added
- 4 principle-based skills: create-skills, create-subagents, create-hooks, create-plans
- 8 slash commands: /create-skill, /create-subagent, /create-hook, /create-plan, /audit-skill, /audit-subagent, /debug, /whats-next
- 3 agent types: code-reviewer, skill-auditor, subagent-auditor
- plugin.json and marketplace.json for GitHub marketplace
- MIT license

### Principles
- Goals over procedures
- Principles over steps
- Trust Claude's intelligence
- Concise by default
- Gotchas, not rules
