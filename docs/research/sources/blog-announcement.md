# Source: Official Blog Announcement

**URL:** https://www.claude.com/blog/introducing-dynamic-workflows-in-claude-code
**Date:** May 28, 2026
**Author:** Anthropic Product Team
**Reading time stated:** 5 minutes
**Category:** Product announcements

## Core positioning

> "Today we're introducing dynamic workflows in Claude Code, helping Claude take on the most challenging tasks end-to-end. Work you'd normally plan in quarters now finishes in days. Claude dynamically writes orchestration scripts that run tens to hundreds of parallel subagents in a single session, checking its work before anything reaches you."

## The problem framing

> "Some problems are too big for one pass by a single agent, especially in complex, legacy codebases: a bug hunt across an entire service, a migration that touches hundreds of files, a plan you want stress-tested from every angle before you commit to it. Dynamic workflows can handle all of these end-to-end."

## How it ships

Research preview in: Claude Code CLI, Desktop, VS Code extension, the Claude API, Amazon Bedrock, Vertex AI, and Microsoft Foundry. **The runtime itself is local** — it calls the configured model API. For a custom Claude-compatible endpoint (minimax / MiniMax / MM-X / etc.), workflows should work the same way as long as the endpoint supports tool use with structured-output schema enforcement.

## Two ways to start

1. Ask Claude to create a dynamic workflow directly ("Create a workflow")
2. Switch on `ultracode` — sets effort to xhigh, lets Claude decide automatically when to use a workflow

## Customer quote that captures the positioning

**Klarna — Alessio Vallero, Senior Engineering Manager:**
> "Dynamic workflows have been especially valuable for discovery and review tasks across large codebases. We've seen strong results using it to identify dead code and surface cleanup opportunities that traditional static analysis missed, helping our engineers move faster on maintenance and refactoring work."

## The Bun case study (most striking concrete example)

> "An example of what dynamic workflows can unlock at scale is the recent rewrite of Bun. Jarred Sumner used dynamic workflows to port Bun from Zig to Rust with 99.8% of the existing test suite passing, roughly 750,000 lines of Rust, and eleven days from first commit to merge. One workflow mapped the right Rust lifetime for every struct field in the Zig codebase. The next wrote every .rs file as a behavior-identical port of its .zig counterpart, hundreds of agents working in parallel with two reviewers on each file. A fix loop then drove the build and test suite until both ran clean. After the port landed, an overnight workflow addressed unnecessary data copies and opened a PR for each for final review."

This is the single most important paragraph in the post. It teaches:
- The pattern is **mapping (lifetime per struct field) → translating (file-per-agent with reviewers) → fix-loop (build and test until clean) → optimization (overnight, PR per change)**.
- 750k LOC, 11 days, ~99.8% test parity.
- "Hundreds of agents working in parallel with two reviewers on each file" — adversarial-verify built in.

## How it works (the post's own framing)

> "When a workflow kicks off, Claude plans dynamically based on your prompt, breaks it into subtasks, and fans the work out across subagents running in parallel. Results are checked before they're folded in, and you come back to a single, coordinated answer. Agents address the problem from independent angles, other agents try to refute what they found, and the run keeps iterating until the answers converge — which is how a workflow reaches results a single pass can't."

The mechanism: **plan → fan-out → check → refute → converge.** This is the formalized version of patterns the community has been hand-rolling for months.

## Cost and control posture

> "It's important to note that dynamic workflows consume meaningfully more usage than a typical Claude Code session. The first time a workflow triggers, Claude Code shows what's about to run and asks you to confirm. Organization admins can also optionally disable workflows through managed settings."

## Surface area defaults the post asks for

> "For the best experience, turn on auto mode when using dynamic workflows."

`auto` + `ultracode` is the recommended combo.
