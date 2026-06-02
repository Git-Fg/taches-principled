# Research: Claude Code Dynamic Workflows & Adjacent Primitives

**Date captured:** 2026-06-02
**Trigger:** User-directed survey of *new* Claude Code capacities related to dynamic workflows, using kimi-webbridge for browser-driven discovery and screenshot capture.
**Scope filter:** Only primitives that work against **any Claude-compatible API endpoint** (including custom providers like minimax / MiniMax / MM-X). Features that depend on Anthropic-managed sign-in or cloud-side session execution are out of scope.
**Status:** Live research log — files in this directory are the raw findings, written as they were discovered rather than retrofitted into a clean narrative.

---

## What landed in May–June 2026 (custom-endpoint compatible only)

Anthropic shipped a coordinated wave of dynamic execution primitives in spring 2026. After filtering to what runs locally against a custom API endpoint, this is what matters:

| Primitive | What it is | Doc |
|---|---|---|
| **Dynamic Workflows** | JavaScript orchestration script Claude writes; runtime runs 10s–100s of subagents locally, calling the configured model API | [`primitives/dynamic-workflows.md`](primitives/dynamic-workflows.md) |
| **Scheduled tasks** | `/loop`, `CronCreate`, `CronList`, `CronDelete`, ScheduleWakeup for dynamic-paced loops — local scheduler, fires between turns | [`primitives/scheduled-tasks.md`](primitives/scheduled-tasks.md) |
| **`/goal`** | Completion-condition Stop hook — keeps the session turn-looping until an evaluator says done | [`primitives/goal.md`](primitives/goal.md) |
| **Channels** | MCP servers that *push* events (webhooks, chat bridges) into a running local session | [`primitives/channels.md`](primitives/channels.md) |
| **Run agents in parallel** | The canonical comparison page that helps pick subagents vs workflows vs worktrees | [`primitives/run-agents-in-parallel.md`](primitives/run-agents-in-parallel.md) |
| **Ultracode mode** | `/effort ultracode` — xhigh effort + automatic Workflow orchestration on every substantive task (works on xhigh-capable models, including custom-endpoint Opus when the endpoint supports xhigh) | covered in dynamic-workflows.md |
| **`/batch` skill** | Bundled skill: split one large change into 5–30 worktree-isolated subagents, each opens a PR — purely local | covered in run-agents-in-parallel.md |
| **Monitor tool** | Background script with line-streamed output back to Claude — alternative to polling | covered in scheduled-tasks.md |

## Source artifacts

- [`sources/blog-announcement.md`](sources/blog-announcement.md) — official Anthropic blog post (May 28, 2026)
- [`sources/infoq-coverage.md`](sources/infoq-coverage.md) — third-party framing (InfoQ, Jun 1, 2026)
- [`sources/whats-new-w22.md`](sources/whats-new-w22.md) — Claude Code release notes for the launch week
- [`sources/llms-txt-index.md`](sources/llms-txt-index.md) — full docs index that surfaced everything else
- [`screenshots/`](screenshots/) — visual captures: workflows doc top/mid/bottom + overview

## The synthesis (read this if nothing else)

[`synthesis.md`](synthesis.md) — implications for taches-principled. The short version: **most of what taches-principled invents — fan-out, critique loops, adversarial verification, plan/judge/execute — is now a first-class primitive in Claude Code, available against any endpoint.** Our value moves from "providing the orchestration plumbing" to "providing the *quality patterns* that go into the workflow scripts Claude writes."

[`brainstorm-marketplace-fit.md`](brainstorm-marketplace-fit.md) — per-skill classification: which skills KEEP, which WRAP into orchestration scripts, which COLLAPSE; the orchestration shapes for each WRAP candidate; and the semantic-language guide for replacing brittle tool-name citations with verbs and role nouns.

## How this research was conducted

1. **Discovery pass** (Google search through kimi-webbridge): surfaced the official `/docs/en/workflows` page and the announcement blog within seconds.
2. **Doc index pull** (`code.claude.com/docs/llms.txt`): the canonical agent-readable index revealed the full surface of adjacent primitives.
3. **Per-page deep fetch** (mcp-searxng): each primitive's canonical doc captured verbatim into [`primitives/`](primitives/).
4. **Cross-reference**: the comparison tables on `run-agents-in-parallel`, `scheduled-tasks`, and `goal` docs clarify which primitive is the right fit for which task.
5. **Custom-endpoint filter** applied after capture: cloud-only features removed; only what runs against any Claude-compatible API endpoint is kept.
6. **Screenshots** captured via kimi-webbridge for visual references.

Browser automation hit one limitation — the active tab occasionally entered a chrome-extension state that blocked further screenshots; the canonical markdown was always recoverable through the searxng fetch fallback.
