---
name: create-prompts
description: "Creates executable prompts for Claude Code. Use when user says 'write me a prompt', 'generate a prompt', or 'create a prompt for this task'."
when_to_use: |
  Use when the user says:
  - "write me a prompt"
  - "generate a prompt"
  - "create a prompt for this task"
  - "write a prompt for another agent"
  - "write a prompt for X" (where X is a specific task)
  - "create a prompt that does X"
  - "I need a prompt to [task]"
  - "write an executable prompt for [task]"
  - "craft a prompt for [goal]"
  IMMEDIATELY when the user wants to create a reusable prompt artifact that another Claude Code session can execute.
  Do NOT use for executing prompts directly, reviewing existing prompts, or one-off questions.
  Do NOT use when the goal is to create a reusable Claude Code skill (use create-skills).
argument-hint: [task description]
---

## Decision Router

IF adaptive intake required → BEFORE gathering requirements read section below on intake workflow
IF generating for coding task → Use XML-structured prompts with `<implementation>` and `<verification>` sections
IF generating for analysis task → Use XML-structured prompts with `<analysis_framework>` and `<output_format>` sections
IF generating for research task → Use XML-structured prompts with `<search_strategy>` and `<synthesis>` sections

This skill is self-contained — no external skill references needed.

---

# Create Prompts Skill

Create highly effective prompts that another Claude Code session can execute.

## Core Principle

**A prompt is a contract.** It specifies what to do, why it matters, and how to verify success. A vague prompt produces vague results. A precise prompt produces precise results.

---

## What Good Looks Like

### Policy

A good prompt contains:
- **Objective**: Clear statement of what needs to happen and why it matters
- **Context**: Project type, tech stack, relevant constraints, who will use the output
- **Requirements**: Specific, unambiguous instructions
- **Output**: Exact file paths using relative notation (`./path/to/file`)
- **Verification**: Explicit success criteria and how to confirm completion

### Quality Indicators

| Signal | Good | Bad |
|--------|------|-----|
| Objective | "Build login with JWT because stateless auth scales better" | "Implement auth" |
| Context | "@src/auth/* patterns, users table schema" | "auth stuff" |
| Requirements | "Create ./src/auth/login.ts with email/password form" | "create login" |
| Output | "Save token to HttpOnly cookie, return 200" | "handle login" |
| Verification | "POST /api/auth/login returns 200 + sets cookie" | "test it works" |

---

## Adaptive Intake

### Intake Gate Principle

The intake gate determines whether you need more information before generating. Empty or vague input requires questioning. Specific input proceeds directly to generation.

### Intake Directive

**ALWAYS spawn a researcher subagent to gather project context before questioning.** The researcher should explore the codebase structure, existing patterns, and relevant files to inform the questioning phase. This ensures questions target genuine gaps rather than discoverable information.

### Analysis Principle

From the input, infer task type (coding, analysis, research), complexity (simple vs complex), prompt structure (single vs multiple), execution strategy (parallel vs sequential), and reasoning depth.

### Inference Heuristics

| Observed | Likely Inference |
|----------|------------------|
| Dashboard/feature with multiple components | Multiple prompts needed |
| Bug fix with clear location | Single prompt, simple |
| "Optimize" or "refactor" | Needs specificity about what/where |
| Authentication, payments, complex features | Complex, needs context |

---

## Contextual Questioning

### Questioning Principle

Ask only about genuine gaps. Don't ask what's already stated. Each question needs options with explanations. User can always select "Other" for custom input.

### Question Focus Areas

- **Ambiguous scope** — What kind of dashboard/admin/interface?
- **Unclear target** — Where does this occur (frontend/backend/database)?
- **Auth/security tasks** — What authentication approach?
- **Performance tasks** — Load time, runtime, or database concern?
- **Output clarity** — Production, prototype, or internal tooling?

Generate 2-4 questions per round based on remaining gaps. Keep the decision gate loop active until user selects "Proceed."

---

## Decision Gate Loop

### Gate Principle

Never proceed without explicit user confirmation. Present decision gate: "I have enough context to create your prompt. Ready to proceed?" Keep asking questions until user selects "Proceed."

---

## Prompt Generation

### Generation Principle

Prompts are XML-structured artifacts that define the contract between the user and the executing agent. Determine single vs multiple prompts, execution strategy, reasoning depth, required tools, and quality signals before generating.

### Multi-Prompt Generation Directive

**ALWAYS spawn parallel subagents for tasks with >2 independent prompts.** When generating multiple prompts, dispatch them in parallel rather than sequentially. Each subagent handles one prompt independently, ensuring focused execution and reduced generation time.

### Conditional Enhancements

| Enhancement | When to Use |
|-------------|-------------|
| Extended thinking triggers | Complex reasoning/optimization |
| "Go beyond basics" | Creative/ambitious tasks |
| WHY explanations | Constraints and requirements |
| Parallel tool calling | Agentic/multi-step workflows |

### Prompt Patterns

See {baseDir}/references/prompt-patterns.md for full XML templates for coding, analysis, and research tasks.

---

## Execution Strategies

### Strategy Selection Principle

Match execution strategy to task dependencies:
- **Single Prompt**: Clear goal, sequential execution required
- **Parallel Prompts**: Independent sub-tasks, no shared file modifications
- **Sequential Prompts**: Dependencies exist, ordering matters

---

## Quality Standards

### Quality Verification Directive

**ALWAYS spawn a critic subagent to review generated prompts before delivery.** The critic evaluates clarity, completeness, specificity, and adherence to the prompt structure standards. Iterate until the critic finds no HIGH-severity issues.

- **Clarity First**: Would a colleague with minimal context understand this?
- **Context is Critical**: Include WHY, WHO, and WHAT.
- **Be Explicit**: Precision over brevity.
- **Verification Always**: Every prompt includes clear success criteria.

---

## Anti-Patterns

| Bad | Good |
|-----|------|
| "Implement auth" | "Build JWT-based login with refresh token rotation because stateless auth scales better" |
| "Fix the bug" | "Fix the null pointer exception in ./src/services/UserService.ts:45" |
| "Create the feature" | "Verify: npm test passes, manual smoke test at localhost:3000" |
| "Go ahead and implement" | "Follow existing patterns in ./src/api/*.ts" |
| "Generate some tests" | "Save test file to ./tests/unit/auth.test.ts" |
| Include unused tags | Only tags that contribute to execution |

---

## Numeric Thresholds

| Metric | Limit | Rationale |
|--------|-------|-----------|
| Questions per round | 2-4 max | Cognitive load; more = decision fatigue |
| Prompts per generation | 2-4 typical (12 max) | Beyond this suggests task should be split |
| Tasks per prompt | 2-3 typical | Quality degradation at higher task counts |
| Filename words | 5 max | Keep concise for globbing |

**Split signal**: If a task has >3 subsystem touches, >5 files, or requires research + implementation, split into multiple prompts.

---

## Success Criteria

- Intake gate completes before generation
- Questioning fills only genuine gaps
- Decision gate loop continues until user confirms
- Prompt structure matches task type (coding/analysis/research)
- Execution strategy matches task dependencies
- Sequential numbering applied correctly
- Output saved to `.principled/prompts/[slug]-[number]-[name].md`
