# Contributing to taches-principled

This file documents the methodology marketplace maintainers use when adding
or modifying skills, subagents, hooks, or plugins. It is **maintainer-only**;
end-user Claude (loading the marketplace as a plugin) never reads it.

The audit of 2026-06-04 (CHANGELOG 1.14.0) introduced a subagent-contract
redesign with 6 design principles, 4 tool-source patterns, and a 3-phase
testing methodology. This file is the canonical home for that methodology.

---

## 3-Phase Testing Methodology

Every change to a skill, subagent, hook, or plugin MUST pass all 3 phases
before merge. Manual verification during the audit cycle is not repeatable;
codify the test, run it, capture the result.

### Phase 1: Static Read

Read the artifact under change and verify structural integrity without
running anything.

- **Skills / agents**: `python3 -c "import yaml; yaml.safe_load(open('FILE'))"` — no frontmatter parse errors
- **marketplace.json / plugin.json**: `jq empty FILE` — no JSON syntax errors
- **marketplace.json integrity**: `jq -e '.plugins | all(. as $p | ([keys[] | select(. == "version")] | length) == 1)' .claude-plugin/marketplace.json` — no duplicate `version:` keys per plugin entry (the regression class from CHANGELOG 1.14.0)
- **Cross-references**: every `references/X.md` cited from a SKILL.md exists; every `plugins/X` path referenced from a body is a real plugin
- **CONTRAST clause**: every skill that has an adjacent-domain neighbor has a CONTRAST section
- **Subagent contract**: `tools:` field matches operations stated in the contract body (no `Write` without a Write operation, no missing tool for stated operations)

### Phase 2: Real Invocation

Spawn the subagent (or invoke the skill) in a controlled condition and
observe behavior. For a real-condition test, the audit ran a subagent
whose contract claimed file I/O on a synthetic input and captured the
JSONL trace.

- **Subagent tools: contract test**: spawn the subagent with a task that
  requires each tool listed in its `tools:` field. Verify the JSONL
  trace contains calls to each tool. A `tools: []` agent making file
  I/O claims but never calling Read/Write/Edit is a contract violation
  (this is exactly the failure mode the 2026-06-04 audit caught).
- **Skill routing test**: pose 10 realistic user utterances; verify
  routing into the expected skill via description-match scoring.
- **Hook test**: trigger the hook event; verify the hook ran (look
  for the hook's log line in the JSONL trace) and produced the
  expected output.

### Phase 3: JSONL Trace Analysis

The JSONL trace from a real invocation is the source of truth for whether
the contract was honored. Inspect:

- **Tool call count**: if `tools:` lists 4 tools and the trace shows 0,
  the agent is self-acknowledging the contradiction. The model will
  write "I cannot do X" in the response and produce no work.
- **Tool sequencing**: contracts that say "first read, then write" must
  show that order in the trace. Out-of-order is a contract violation.
- **Error handling**: every failed tool call must be followed by an
  error path that the contract declared. Silently swallowing errors
  is a violation.
- **Output contract**: the final assistant message must match the
  contract's stated output format (markdown table, JSON envelope, etc.)

Save the trace to `.principled/scratch/agent-{id}.jsonl` and reference
it from the CHANGELOG entry. The trace is the audit evidence.

---

## 6 Design Principles for Subagent Contracts

The full reference is at
`plugins/core-principled/skills/subagent-orchestration/references/subagent-contract-design.md`.
This is the maintainer's checklist when writing a new agent.

| # | Principle | Test |
|---|-----------|------|
| **P1** | Source of truth for every value | For every fact in the agent's output, the body identifies where it came from (Read X, Grep Y, etc.). No values asserted without a source. |
| **P2** | Bind Writes to Reads explicitly | If the agent writes a file, the body states what it Read first and what transformation produced the write. No ungrounded generation. |
| **P3** | Ordered operations with verification | Multi-step contracts state the order and what success looks like at each step. The trace must show that order. |
| **P4** | Explicit link resolution algorithm | If the contract references files, IDs, or URLs, the body states how the agent finds them. No "go look it up." |
| **P5** | Failure-mode footer on every contract | The last paragraph of every agent body lists the failure modes and what the agent does in each. If a mode isn't listed, the agent improvises. |
| **P6** | Ground truth | Subagents that make factual claims about the codebase MUST have Read access. The body MUST state that the agent Reads/Grabs the relevant files before making claims. **This principle was added in CHANGELOG 1.14.0** in response to a marketplace subagent run that asserted file paths and line numbers without ever reading any files. |

---

## 4 Tool-Source Patterns

**The default is no `tools:` field.** Subagents inherit the full tool pool.
Only add `tools:` when the body has a NEVER-do-X policy that the tool
boundary must enforce. The canonical example: `wiki-searcher` whose body
says "NEVER write or modify any wiki file" and whose
`tools: [Read, Glob, Grep]` enforces it.

The `tools:` field can be set in 4 ways. Patterns 3 and 4 (no field) are
the default for agents without NEVER policies. Patterns 1 and 2 are
exceptional — only when a tool boundary is the enforcement mechanism.

| Pattern | When to use | Example |
|---------|-------------|---------|
| **Default: no `tools:` field** | Most subagents. Agent inherits the full tool pool from the host environment. | 43 of 47 marketplace agents currently use this (wiki-searcher is the exception). |
| **Explicit full list** | Agent has a NEVER-do-X boundary requiring all listed tools (e.g., a generator whose body says "NEVER run destructive Bash"). | Rare — the marketplace has zero current examples. |
| **Explicit restricted list** | Agent is a focused read-only tool where the boundary enforces "NEVER write" (e.g., `wiki-searcher`). | `tools: [Read, Glob, Grep]` for `tp-wiki:wiki-searcher` only. |
| **`tools: []` with orchestrator handling** | Agent's output is text-only; any file I/O is the orchestrator's job. | Historical `sadd-*` examples (pre-1.23.0). The 1.23.0 consolidation removed all such agents; current keepers return rich output, not text-only. |

**Only add `tools:` when the body says "NEVER do X" and the tool boundary
is the enforcement layer.** The restriction cost is real: the agent
loses user-configured MCP servers, project-specific tools, and
`settings.json` quirks. The benefit is imaginary unless the NEVER policy
is load-bearing.

**The bug class caught by the 2026-06-04 audit:** agents with `tools: []`
but file-I/O contracts in their body. Real testing revealed the model
would self-acknowledge the contradiction ("I don't have Write access")
and produce zero tool calls. The fix was NOT to add tool lists
indiscriminately — it was to audit whether the agent actually needs to
write, and if so, remove the `tools: []` or let it inherit.

---

## 3 Maintenance Patterns

| Pattern | When to use |
|---------|-------------|
| **Reference files (lazy load)** | Long reference tables, schemars cheat-sheets, decision matrices. Cited imperatively from SKILL.md with `You MUST read X BEFORE [action]`. Zero cost when not loaded. |
| **Pure SKILL.md body** | Routing, decision framework, anti-patterns. Always loaded. Keep under 2,500 tokens of dense prose. |
| **Subagent (hot-path execution)** | Operations that would be expensive in the main agent context (parallel exploration, evidence-gathering, generation, judging). Spawn via subagent-orchestration patterns. |

---

## 4 Audit Cadence Triggers

Trigger a full re-audit when any of these change:

1. A new plugin is added
2. A plugin's `tools:` list changes (re-test with Phase 2)
3. A new CHANGELOG entry documents a "skip notes" rationale that
   contradicts a previous entry (see CHANGELOG Skip notes sections)
4. A subagent makes a factual claim that turns out to be wrong (the
   P6 ground-truth failure mode)

---

## Marketplace Regeneration

The catalog file `.claude-plugin/marketplace.json` is **derived**, not hand-edited.
It is regenerated from two SSoT sources:

| Source file | Fields contributed |
|---|---|
| `plugins/<name>/.claude-plugin/plugin.json` | `name`, `version`, `description` |
| `.claude-plugin/_meta.json` | `source`, `homepage`, `repository`, `license`, `category`, `keywords` |

### When to run

After editing any per-plugin `plugin.json` or `.claude-plugin/_meta.json`.

### How to run

```bash
python3 scripts/regenerate-marketplace.py
```

### How to verify

Run the same structural check that CI performs:

```bash
jq -e '.plugins | all(. as $p | ([keys[] | select(. == "version")] | length) == 1)' .claude-plugin/marketplace.json
```

If it prints nothing and exits 0, the catalog is clean. If it reports duplicate
`version:` keys, the regeneration wrote malformed output — fix the script, do
not hand-edit marketplace.json.
