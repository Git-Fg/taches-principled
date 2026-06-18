# Roster Rules — the canonical 5-rule discipline set

The `tp-discipline` plugin enforces marketplace discipline across 5 rule categories. The CI guard at `scripts/audit.py` is the mechanical implementation; this document is the human-readable explanation.

## R1 — Agent roster discipline

**Goal:** prevent agent-file proliferation. After the 1.23.0 consolidation, the marketplace ships **6 named subagents** plus **1 read-only-tools exception**. New specialists require an intentional CHANGELOG entry, not silent drift.

### Rules

1. **Count cap** (default 6): `find plugins -path '*/agents/*.md' | wc -l` must be ≤ 6. Exceeding this count is a **BLOCKER**.
2. **tools: lock exception** (currently 1 — `wiki-searcher`): only agents listed in `allowed_tools_locks` may have a `tools:` field. Adding another is a **BLOCKER** unless documented.
3. **No model lock**: zero agents may have a `model:` field. Agents inherit the orchestrator's model.
4. **Ground truth section**: every agent must have a `## Ground truth` (or `## Ground truth (P6)`) section. Missing is a **WARNING** because some agents (e.g., text-only synthesizers) may genuinely not need it.

### Why

55 → 6 was a load-bearing consolidation. The marketplace commits to the lens-prompt pattern: every new specialized reviewer should be a one-sentence lens passed to `tp-critic`, not a new file. The roster cap makes that decision explicit.

## R2 — Spawn discipline

**Goal:** prevent unprincipled subagent delegation. Every spawn of a generic keeper must carry a lens/scope/question argument that scopes the work.

### Rules

For every `spawn tp-critic|tp-explorer|tp-researcher` directive in any skill, command, or agent body, an argument must appear within 400 characters: `(lens: "...")` / `(scope: "...")` / `(question: "...")` or `with lens "..."` / `w/ scope "..."` / `w/ question "..."`.

Missing argument is a **WARNING**. Rationale: the script's regex can't catch every phrasing; manual review at PR time covers the rest.

### Why

The keeper agents are designed to receive a one-sentence scope. Without it, the spawn defaults to the agent's generic role, which is fine for `tp-explorer` but loses precision for `tp-critic` (no lens = generic review, not the targeted review the skill intended).

## R3 — Fork-skill discipline

**Goal:** prevent orphan fork skills. Every `context: fork` skill must have a `references/fork-rationale.md` citing what isolation value the fork provides.

### Rules

Every skill with `context: fork` frontmatter must include a `references/fork-rationale.md`. Missing is a **WARNING**.

### Why

After 1.23.0, fork skills (`plan-lifecycle`, `sadd`, `task-lifecycle`, `fpf`) implement inline within the fork and spawn only `tp-critic` for isolated review. The fork value is no longer "isolation from inner parallelism" (which was lost) — it's "isolation from the user's session for long multi-step reasoning." A fork-rationale file documents this trade-off so future maintainers don't strip the fork flag thinking it's unused.

## R4 — Description quality

**Goal:** keep routing signals clean. Descriptions are pre-injected into agent context at startup; verb-led first-200-char phrases are the routing signal; CONTRAST clauses prevent misrouting between adjacent-domain skills.

### Rules

1. **Length**: `description` ≤ 1536 chars total (including `when_to_use`). Exceeding is a **WARNING**.
2. **Verb-led first 200 chars**: the description must start with an action verb (Design, Find, Audit, etc.). Missing is a **NUDGE** — it's a soft quality signal.
3. **CONTRAST for SKILL.md**: every skill must contain a CONTRAST section or `NOT for:` clause, either in the body or in `when_to_use`. Missing is a **NUDGE**.

### Why

Per `.claude/rules/routing-signal.md`: triggers must appear in the first 200 chars; metadata-only gate; descriptions must be mutually exclusive across the marketplace. The R4 rules enforce the mechanics of that contract.

## R5 — Catalog discipline

**Goal:** keep `marketplace.json` in sync with per-plugin `plugin.json`. The marketplace catalog is the public-facing installation manifest; drift between it and the actual plugin is a packaging bug.

### Rules

1. **Every plugin.json has a matching marketplace.json entry.** Missing is a **BLOCKER** — it means the marketplace validator will reject the plugin.
2. **Versions match.** Plugin.json `version` and marketplace.json `version` for the same plugin must be equal. Mismatch is a **BLOCKER**.
3. **Description mentions roster** (nudge): if a plugin has 0 specialist agents, its description should mention that fact (e.g., "reviews via tp-critic w/ lens" or "no specialist agents").

### Why

The marketplace catalog is the only artifact users see before installing. Stale descriptions there misrepresent what they're getting.

## How to fix common findings

- **R1a (count cap exceeded):** reduce to ≤ 6 agents, OR bump the cap in `discipline.json` with a CHANGELOG entry.
- **R1b (tools: lock on a non-allowed agent):** remove the `tools:` field, OR add the agent to `allowed_tools_locks` with a justification.
- **R2 (spawn without lens):** add `(lens: "...")` next to the spawn directive. Common shapes: `spawn tp-critic with lens "OWASP Top 10"` or `spawn tp-explorer (scope: "map the structure under src/")`.
- **R3 (fork without rationale):** add `<skill>/references/fork-rationale.md` citing the isolation value.
- **R4b (description too long):** trim. Move detail to the body.
- **R5a (catalog drift):** run `python3 scripts/regenerate-marketplace.py`.

## Configuration

The default `agent_roster_cap` is 6. Override with a `--config discipline.json` argument:

```json
{
  "agent_roster_cap": 10,
  "allowed_tools_locks": ["wiki-searcher", "tp-roster-auditor"]
}
```

This makes the audit config-driven: a marketplace with a different roster philosophy just passes its own config.