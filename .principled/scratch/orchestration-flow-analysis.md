# Skill Orchestration Flow Analysis

## Reference Graph

### create-plans (taches-principled)
- **Spawns**: explorer.md, researcher.md, architect.md, critic.md, verifier.md, implementer.md (from agents/ folder)
- **References skills**: `execute-plans` (compositional pair, implicit invoke)
- **References files**: plan-format.md, checkpoints.md, scope-estimation.md, cli-automation.md, milestone-management.md (all in create-plans/references/)

### execute-plans (taches-principled)
- **Spawns**: implementer, critic, researcher, verifier (from agents/ folder)
- **References skills**: None explicitly named
- **References files**:
  - execution-strategies.md (in execute-plans/references/)
  - checkpoint-protocols.md (in execute-plans/references/)
  - deviation-rules.md (in execute-plans/references/)
  - autonomous-execution.md, segment-execution.md (in execute-plans/templates/)
  - critic.md (in execute-plans/agents/)

### create-subagents (taches-principled)
- **Spawns**: General-purpose subagents using its agent templates
- **References files** (in create-subagents/references/):
  - writing-subagent-prompts.md
  - orchestration-core.md
  - failure-modes.md
  - memory-architecture.md
  - gotchas.md
  - subagents.md
  - context-management.md
  - automation-layers.md
  - tools-reference.md
  - anti-patterns.md
  - scratchpad-protocol.md
  - token-economics.md
  - error-handling-and-recovery.md
  - fault-tolerance.md

### implement-task (taches-principled)
- **Spawns**: Implementation subagents, judge subagents
- **References files**: patterns.md (in implement-task/references/)
- **References skills**: None explicitly named

### subagent-orchestration (taches-principled)
- **Spawns**: General-purpose subagents
- **References files** (described in Reference Index but NO references/ folder exists):
  - race-framework.md
  - orchestration-patterns.md
  - automation-layers.md
  - memory-architecture.md
  - failure-modes.md
  - context-management.md
  - gotchas.md

### plan-task (taches-principled)
- **Spawns**: Phase subagents for research, codebase analysis, business analysis, architecture, decomposition, parallelize, verifications
- **References files**: stages.md (in plan-task/references/)
- **References skills**: None explicitly named

### create-prompts (taches-principled)
- **References skills**: None (self-contained, compositional pair exemption noted)
- **References files**: None (self-contained)

### execute-prompts (taches-principled)
- **Spawns**: General-purpose subagents
- **References skills**: None explicitly named
- **References files**: execute-prompt.md (in execute-prompts/workflows/)
- **Cross-skill reference**: execute-plans anti-patterns (described Thought/Action/Observation anti-pattern as being documented in execute-plans)

---

### tp-sadd Skills

#### sadd-dispatch
- **Spawns**: Subagents with CoT reasoning
- **References skills**: `sadd-execute` (for multi-step plans with quality verification), `subagent-driven-development` (for sequential dependencies)
- **References files**: None explicitly

#### sadd-execute
- **Spawns**: Meta-judge, implementor, judge subagents
- **References files**: meta-judge.md (assumed in execute-plans/references/ or local)

#### sadd-judge
- **Spawns**: Judge subagents
- **References files**: patterns.md (in sadd-judge/references/) — CONFIRMED EXISTS

#### sadd-patterns
- **Spawns**: None (documentation skill)
- **References files**: patterns.md (CONFIRMED EXISTS)

#### sadd-tot
- **Spawns**: Tree-of-thought subagents
- **References skills**: `judge-with-debate` (competitive evaluation)

#### do-competitively
- **Spawns**: Competitive generation agents
- **References skills**: `judge-with-debate`

#### launch-subagent
- **References files**: SKILL.md only — NO references/ folder

#### subagent-driven-development
- **References skills**: `sadd-dispatch`, `sadd-execute`

---

### tp-sdd Skills

#### plan-task (tp-sdd)
- **Same name as taches-principled plan-task** — different plugin, functionally similar
- **References skills**: None explicitly named

#### implement-task (tp-sdd)
- **Same name as taches-principled implement-task** — different plugin, functionally similar
- **References skills**: `plan-task` (pipeline relationship)

---

## Dead Ends

### 1. subagent-orchestration references non-existent files
**File**: `plugins/taches-principled/skills/subagent-orchestration/SKILL.md`

The skill's Reference Index lists:
- race-framework.md
- orchestration-patterns.md
- automation-layers.md
- memory-architecture.md
- failure-modes.md
- context-management.md
- gotchas.md

**NONE of these files exist** — there is no `references/` folder under `subagent-orchestration/`.

These reference names match files that exist in OTHER skills' references folders (e.g., `create-subagents/references/`, `create-plans/references/`), suggesting the skill was designed to reference them but the references/ folder was never created.

### 2. execute-prompts references execute-plans anti-pattern
**File**: `plugins/taches-principled/skills/execute-prompts/SKILL.md` line 230

States: "The Thought/Action/Observation Anti-Pattern is documented in the execute-plans skill's anti-patterns reference."

This is a cross-skill natural language reference (not a path), which is acceptable per CLAUDE.md guidelines. However, execute-plans/references/anti-patterns.md does exist, so this is **NOT a dead end** — just verifying.

---

## Circular Dependencies

### No circular dependencies detected

The skill graph does not contain any A→B→A circular chains. The closest relationships are:

- `create-plans` → `execute-plans` (compositional pair, execute-plans does not reference back)
- `create-prompts` → `execute-prompts` (documented as compositional pair exemption)
- `sadd-dispatch` → `sadd-execute` (but sadd-execute does not reference back to dispatch)

---

## Missing Orchestrations

### 1. tp-sadd has inconsistent skill pairings

| Skill | Says to use | Does partner exist? |
|-------|-------------|---------------------|
| `sadd-dispatch` | "use sadd-execute instead" for quality verification | YES |
| `sadd-dispatch` | "use subagent-driven-development instead" for sequential deps | YES |
| `sadd-tot` | "use judge-with-debate" for evaluation | YES |
| `do-competitively` | "use judge-with-debate" for evaluation | YES |
| `subagent-driven-development` | References sadd-dispatch, sadd-execute | YES |

All partner skills exist — no missing orchestration.

### 2. tp-sdd plan-task → implement-task pipeline

The `tp-sdd/plan-task` skill produces refined tasks, and `tp-sdd/implement-task` consumes them. This is a natural workflow pair. Both exist.

---

## Zombie References

### 1. launch-subagent skill appears orphaned
**File**: `plugins/tp-sadd/skills/launch-subagent/SKILL.md`

This skill has no references/ folder and minimal content. The git status shows it was deleted (`D` status in initial status), but the file still exists on disk. This suggests the skill may be in transition.

### 2. execute-prompts execute-prompt workflow reference
The skill says "Read the execute-prompt workflow file from the workflows folder" — the file `execute-prompts/workflows/execute-prompt.md` **exists** (confirmed).

---

## Broken Reference Index Entries

### subagent-orchestration — ALL missing

**Location**: `plugins/taches-principled/skills/subagent-orchestration/SKILL.md` Reference Index section

The skill lists these files as references but **NO `references/` folder exists**:

```
- `race-framework.md` — MISSING (exists in create-plans/references/)
- `orchestration-patterns.md` — MISSING (exists in create-plans/references/)
- `automation-layers.md` — MISSING (exists in create-subagents/references/)
- `memory-architecture.md` — MISSING (exists in create-subagents/references/)
- `failure-modes.md` — MISSING (exists in create-subagents/references/)
- `context-management.md` — MISSING (exists in create-subagents/references/ and create-skills/references/)
- `gotchas.md` — MISSING (exists in create-subagents/references/)
```

**Recommendation**: Either create the `references/` folder with the referenced files, OR update the Reference Index to use natural language pointing to the files in other skills' references directories.

### implement-task patterns.md — verified
**Location**: `plugins/taches-principled/skills/implement-task/SKILL.md` line 554

States: "Implementation patterns are documented in the patterns.md file in this skill's references."

**File check**: `plugins/taches-principled/skills/implement-task/references/patterns.md` — **EXISTS** ✓

### sadd-judge patterns.md — verified
**Location**: `plugins/tp-sadd/skills/sadd-judge/SKILL.md`

References `patterns.md` in references/

**File check**: `plugins/tp-sadd/skills/sadd-judge/references/patterns.md` — **EXISTS** ✓

---

## Summary of Issues

| Severity | Issue | Location |
|----------|-------|----------|
| HIGH | subagent-orchestration has no references/ folder but lists 7 reference files | subagent-orchestration/SKILL.md |
| LOW | launch-subagent skill may be orphaned (deleted in git, still on disk) | tp-sadd/skills/launch-subagent/ |
| LOW | execute-prompts cites execute-plans anti-pattern via natural language (acceptable but verify) | execute-prompts/SKILL.md:230 |
| OK | create-plans agents/ folder has all templates | create-plans/agents/ |
| OK | execute-plans templates/ and agents/ folders complete | execute-plans/ |
| OK | implement-task references patterns.md which exists | implement-task/ |

---

## Working Reference Files (Complete)

### create-plans/references/
- checkpoints.md
- cli-automation.md
- milestone-management.md
- orchestration-patterns.md
- plan-format.md
- race-framework.md
- scope-estimation.md
- task-model-fit.md

### execute-plans/references/
- anti-patterns.md
- checkpoint-protocols.md
- context-efficiency.md
- deviation-rules.md
- env-variable-pattern.md
- execution-strategies.md
- meta-judge.md

### execute-plans/templates/
- autonomous-execution.md
- segment-execution.md
- sequential-execution.md

### create-subagents/references/
- anti-patterns.md
- automation-layers.md
- context-management.md
- error-handling-and-recovery.md
- failure-modes.md
- fault-tolerance.md
- gotchas.md
- memory-architecture.md
- orchestration-core.md
- scratchpad-protocol.md
- subagents.md
- token-economics.md
- tools-reference.md
- writing-subagent-prompts.md

### plan-task/references/
- stages.md

### implement-task/references/
- patterns.md