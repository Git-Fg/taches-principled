# Brief: Integrate CEK Plugins into taches-principled Ecosystem

## Vision

Transform taches-principled from a planning-and-execution skill collection into a **complete Claude Code development ecosystem** by integrating the 11 plugins from context-engineering-kit (sadd, sdd, reflexion, kaizen, fpf, review, docs, git, tdd, ddd, tech-stack) as native, refactored skills. Each skill works alone. All skills get better together through semantic synergy — not hard references.

## Why

The context-engineering-kit plugins solve real problems but suffer from:
- **Redundancy**: The meta-judge pattern is copy-pasted across 10 sadd skills (10,000+ lines of duplication)
- **Brittle cross-references**: Hard paths to other plugins' files, XML tags, agent file dependencies
- **Unprofessional tone**: "You will be killed" language that creates toxic context
- **No delta principle**: Skills restate what Claude already knows instead of documenting what's different
- **Token waste**: 15-25% of content is redundant scaffolding

taches-principled already has the right architecture: decision routers, policy/mechanism separation, non-brittle references, delta principle, clean markdown-native formatting. The CEK skills need this architecture applied to them.

## What Actually Exists

**6 separate plugins** (tp-ddd, tp-fpf, tp-git, tp-sadd, tp-sdd, tp-tdd) plus **5 plugin content areas merged into root** (reflexion, kaizen, review, docs, fpf).

Total: ~35 ecosystem skills across root + plugins.

**Separate plugins:**
- tp-ddd — Domain-driven design rules
- tp-fpf — First Principles Framework (6 skills)
- tp-git — Git operations (7 skills)
- tp-sadd — Structured Agent-Driven Development (5 skills)
- tp-sdd — Spec-Driven Development (5 skills)
- tp-tdd — Test-Driven Development (3 skills)

**Root-level skills (22):** reflexion, kaizen, review, docs, create-skills, create-subagents, create-plans, create-prompts, execute-prompts, execute-plans, subagent-orchestration, and more.

## Core Goal

> Each plugin works standalone. All plugins synergize through semantic meaning — not skill name references or file paths.

Synergy means: when a user invokes `/sadd:judge`, the system already understands how `/sdd:implement-task` produces artifacts and `/reflexion:reflect` evaluates outcomes — because the skills share a common vocabulary about what "judging", "implementing", and "reflecting" mean in the development workflow.

## Design Principles

### Semantic Synergy (Not Hard References)

Skills communicate through shared context about workflow stages, not by naming each other. A "judge" skill knows what "implementation" means because both skills describe their slot in the development pipeline — not because `judge.md` mentions `implement-task.md` by name.

**Concrete example:**
- ❌ `sadd/judge/SKILL.md`: "Call sdd:implement-task for execution"
- ✅ `sadd/judge/SKILL.md`: "Evaluates implementation artifacts against quality criteria"
- ✅ `sdd/implement-task/SKILL.md`: "Produces implementation artifacts ready for evaluation"

Both describe their relationship to "implementation artifacts" without naming each other. When both are present, Claude infers the workflow. When only one is present, it works alone.

### Delta Principle

Each skill documents ONLY what it adds vs. default Claude behavior. If Claude already knows how to use `git diff`, the skill doesn't explain `git diff`. It explains the workflow pattern.

### Decision Router Pattern

Every skill starts with a decision router — concrete "IF X → do Y" conditions that trigger specific behavior.

### Policy/Mechanism Separation

Skills define WHAT (policy) and reference external docs for HOW (mechanism). No inline implementation procedures.

## Synergy Map

```
┌─────────────────────────────────────────────────┐
│                  PLANNING LAYER                  │
│  create-plans → BRIEF → ROADMAP → PLAN.md        │
│  tp-sdd:brainstorm → tp-sdd:add-task →           │
│    tp-sdd:plan-task                              │
│  tp-sdd:create-ideas (divergent thinking)        │
└──────────────────────┬──────────────────────────┘
                       │ feeds
┌──────────────────────▼──────────────────────────┐
│                 EXECUTION LAYER                  │
│  execute-plans → spawns subagents                │
│  tp-sdd:implement-task → spec-driven dev        │
│  subagent-orchestration → parallel dispatch      │
│  tp-tdd:test-driven-development → test-first    │
│  tp-git:* → version control                     │
└──────────────────────┬──────────────────────────┘
                       │ produces
┌──────────────────────▼──────────────────────────┐
│               VERIFICATION LAYER                 │
│  tp-sadd:judge → meta-judge + judge pipeline    │
│  tp-sadd:do-in-steps → sequential + verify       │
│  tp-sadd:do-in-parallel → parallel + verify     │
│  tp-sadd:judge-with-debate → consensus eval    │
│  tp-sadd:tree-of-thoughts → exploration + verify│
│  review:review-local-changes → code review       │
│  review:review-pr → PR review                    │
└──────────────────────┬──────────────────────────┘
                       │ informs
┌──────────────────────▼──────────────────────────┐
│             REFLECTION & IMPROVEMENT LAYER       │
│  reflexion:reflect → self-critique              │
│  reflexion:critique → multi-perspective review   │
│  reflexion:memorize → CLAUDE.md curation         │
│  kaizen:* → continuous improvement methods      │
│  tp-fpf:* → first principles reasoning           │
└──────────────────────┬──────────────────────────┘
                       │ persists
┌──────────────────────▼──────────────────────────┐
│              INFRASTRUCTURE LAYER                │
│  docs:update-docs → documentation               │
│  docs:write-concisely → clear writing           │
│  tp-ddd → domain-driven design rules           │
└─────────────────────────────────────────────────┘
```

Plugin prefixes: `tp-ddd`, `tp-fpf`, `tp-git`, `tp-sadd`, `tp-sdd`, `tp-tdd`. Reflexion, kaizen, review, docs are root-level (no prefix).

Each layer imports from below, feeds into above. Skills within a layer reference shared semantic concepts ("implementation artifacts", "judgment criteria", "reflection output") without naming specific skills.

## What Success Looks Like

1. Every CEK skill is ported to taches-principled format (decision router, delta principle, no XML, no threats)
2. No skill names another skill by name — all references are semantic
3. Total line count is REDUCED vs. CEK originals (eliminating duplication)
4. Each skill can be used standalone (load only one)
5. When 2+ skills from complementary layers are present, Claude automatically composes workflows
6. Existing taches-principled skills are untouched (backward compatible)
