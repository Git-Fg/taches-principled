---
name: create-prompts
description: "Creates executable prompts for Claude Code. Use when user says 'create a prompt', 'generate a prompt for a task', or 'write a prompt for another agent'."
when_to_use: |
  Use when the user says "write me a prompt", "generate a prompt", "create a prompt for this task", or "write a prompt for another agent".
  Do NOT use for executing prompts directly, reviewing existing prompts, or one-off questions.
---

## Decision Router

IF adaptive intake required → BEFORE gathering requirements read section below on intake workflow
IF generating for coding task → Use XML-structured prompts with `<implementation>` and `<verification>` sections
IF generating for analysis task → Use XML-structured prompts with `<analysis_framework>` and `<output_format>` sections
IF generating for research task → Use XML-structured prompts with `<search_strategy>` and `<synthesis>` sections

This skill is self-contained — no external skill references needed.

---

# Create Prompts Skill

Create highly effective prompts that another Claude Code session can execute. Produces XML-structured prompts—not explanations or documentation.

## Core Principle

**A prompt is a contract.** It specifies what to do, why it matters, and how to verify success. A vague prompt produces vague results. A precise prompt produces precise results.

---

## Sections

1. [What Good Looks Like](#what-good-looks-like)
2. [Adaptive Intake](#adaptive-intake)
3. [Contextual Questioning](#contextual-questioning)
4. [Decision Gate Loop](#decision-gate-loop)
5. [Prompt Generation](#prompt-generation)
6. [Execution Strategies](#execution-strategies)
7. [Quality Standards](#quality-standards)
8. [Anti-Patterns](#anti-patterns)
9. [Numeric Thresholds](#numeric-thresholds)

---

## What Good Looks Like

### Policy (What Makes a Good Prompt)

A good prompt contains:

- **Objective**: Clear statement of what needs to happen and why it matters
- **Context**: Project type, tech stack, relevant constraints, who will use the output
- **Requirements**: Specific, unambiguous instructions
- **Output**: Exact file paths using relative notation (`./path/to/file`)
- **Verification**: Explicit success criteria and how to confirm completion

### Mechanism (How to Gather Requirements)

1. Detect whether input is empty or vague
2. Ask structured questions to fill genuine gaps
3. Present decision gate before generating
4. Generate single, parallel, or sequential prompts based on task analysis
5. Save to `.principled/prompts/[slug]-[number]-[name].md` with sequential numbering

### Indicators of Quality

| Signal | Good | Bad |
|--------|------|-----|
| Objective | "Build login with JWT because stateless auth scales better" | "Implement auth" |
| Context | "@src/auth/* patterns, users table schema" | "auth stuff" |
| Requirements | "Create ./src/auth/login.ts with email/password form" | "create login" |
| Output | "Save token to HttpOnly cookie, return 200" | "handle login" |
| Verification | "POST /api/auth/login returns 200 + sets cookie" | "test it works" |

---

## Adaptive Intake

### Policy

The intake gate determines whether you need more information before generating. Empty or vague input requires questioning. Specific input proceeds directly to generation.

### Mechanism

**Before analyzing anything**, check if the input contains a task description.

**If input is empty or vague** (user ran `/create-prompt` without details):
- Use AskUserQuestion immediately with task type selection
- Ask user to describe what they want to accomplish

**If input contains a task description**:
- Proceed directly to adaptive analysis

### Analysis Factors

From the input, extract and infer:

- **Task type**: Coding, analysis, or research
- **Complexity**: Simple (single file, clear goal) vs complex (multi-file, research needed)
- **Prompt structure**: Single prompt vs multiple prompts
- **Execution strategy**: Parallel (independent) vs sequential (dependencies)
- **Depth needed**: Standard vs extended thinking triggers

### Inference Rules

| Observed | Likely Inference |
|----------|------------------|
| Dashboard/feature with multiple components | Multiple prompts needed |
| Bug fix with clear location | Single prompt, simple |
| "Optimize" or "refactor" | Needs specificity about what/where |
| Authentication, payments, complex features | Complex, needs context |

---

## Contextual Questioning

### Policy

Ask only about genuine gaps. Don't ask what's already stated. Each question needs options with explanations. User can always select "Other" for custom input.

### Mechanism

Generate 2-4 questions per round based on remaining gaps.

### Question Templates

**For ambiguous scope** ("build a dashboard"):
- What kind of dashboard is this?
  - Admin dashboard: Internal tools, user management, system metrics
  - Analytics dashboard: Data visualization, reports, business metrics
  - User-facing dashboard: End-user features, personal data, settings

**For unclear target** ("fix the bug"):
- Where does this bug occur?
  - Frontend/UI: Visual issues, user interactions, rendering
  - Backend/API: Server errors, data processing, endpoints
  - Database: Queries, migrations, data integrity

**For auth/security tasks**:
- What authentication approach?
  - JWT tokens: Stateless, API-friendly
  - Session-based: Server-side sessions, traditional web
  - OAuth/SSO: Third-party providers, enterprise

**For performance tasks**:
- What's the main performance concern?
  - Load time: Initial render, bundle size, assets
  - Runtime: Memory usage, CPU, rendering performance
  - Database: Query optimization, indexing, caching

**For output/deliverable clarity**:
- What will this be used for?
  - Production code: Ship to users, needs polish
  - Prototype/POC: Quick validation, can be rough
  - Internal tooling: Team use, moderate polish

### Question Rules

- Only ask about genuine gaps
- Each option needs a description explaining implications
- Prefer options over free-text when choices are knowable
- 2-4 questions max per round

---

## Decision Gate Loop

### Policy

Never proceed without explicit user confirmation. Keep asking questions until user selects "Proceed."

### Mechanism

After receiving answers, present decision gate:

**"I have enough context to create your prompt. Ready to proceed?"**

| Response | Action |
|----------|--------|
| Proceed | Create the prompt with current context |
| Ask more questions | Generate 2-4 new questions based on remaining gaps, then present gate again |
| Let me add context | Receive additional context, then re-evaluate |

### Loop Rule

Keep the decision gate loop active until user selects "Proceed." Do not skip this step even if you feel you have enough context.

---

## Prompt Generation

### Policy

Prompts are XML-structured artifacts that define the contract between the user and the executing agent. The XML structure provides semantic clarity; the content provides execution guidance.

### Mechanism

#### Pre-Generation Analysis

Before generating, determine:

1. **Single vs Multiple Prompts**:
   - Single: Clear dependencies, single cohesive goal, sequential steps
   - Multiple: Independent sub-tasks that could be parallelized

2. **Execution Strategy** (if multiple):
   - Parallel: Independent, no shared file modifications
   - Sequential: Dependencies, one must finish before next starts

3. **Reasoning depth**:
   - Simple: Standard prompt
   - Complex: Extended thinking triggers

4. **Required tools**: File references, bash commands, MCP servers

5. **Quality signals**:
   - "Go beyond basics" for ambitious work
   - WHY explanations for constraints
   - Examples for ambiguous requirements

### Prompt Patterns

#### For Coding Tasks

```xml
<objective>
[Clear statement of what needs to be built/fixed/refactored]
Explain the end goal and why this matters.
</objective>

<context>
[Project type, tech stack, relevant constraints]
[Who will use this, what it's for]
@[relevant files to examine]
</context>

<requirements>
[Specific functional requirements]
[Performance or quality requirements]
Be explicit about what Claude should do.
</requirements>

<implementation>
[Any specific approaches or patterns to follow]
[What to avoid and WHY - explain the reasoning behind constraints]
</implementation>

<output>
Create/modify files with relative paths:
- `./path/to/file.ext` - [what this file should contain]
</output>

<verification>
Before declaring complete, verify your work:
- [Specific test or check to perform]
- [How to confirm the solution works]
</verification>

<success_criteria>
[Clear, measurable criteria for success]
</success_criteria>
```

#### For Analysis Tasks

```xml
<objective>
[What needs to be analyzed and why]
[What the analysis will be used for]
</objective>

<data_sources>
@[files or data to analyze]
![relevant commands to gather data]
</data_sources>

<analysis_requirements>
[Specific metrics or patterns to identify]
[Depth of analysis needed - use "thoroughly analyze" for complex tasks]
[Any comparisons or benchmarks]
</analysis_requirements>

<output_format>
[How results should be structured]
Save analysis to: `.principled/prompts/analyses/[descriptive-name].md`
</output_format>

<verification>
[How to validate the analysis is complete and accurate]
</verification>
```

#### For Research Tasks

```xml
<research_objective>
[What information needs to be gathered]
[Intended use of the research]
For complex research, include: "Thoroughly explore multiple sources and consider various perspectives"
</research_objective>

<scope>
[Boundaries of the research]
[Sources to prioritize or avoid]
[Time period or version constraints]
</scope>

<deliverables>
[Format of research output]
[Level of detail needed]
Save findings to: `.principled/prompts/research/[topic].md`
</deliverables>

<evaluation_criteria>
[How to assess quality/relevance of sources]
[Key questions that must be answered]
</evaluation_criteria>

<verification>
Before completing, verify:
- [All key questions are answered]
- [Sources are credible and relevant]
</verification>
```

### Conditional Enhancements

Based on analysis, include these conditionally:

| Enhancement | When to Use | Example |
|-------------|-------------|---------|
| Extended thinking triggers | Complex reasoning/optimization | "thoroughly analyze", "consider multiple approaches" |
| "Go beyond basics" | Creative/ambitious tasks | "Include as many relevant features as possible" |
| WHY explanations | Constraints and requirements | "Never use ellipses because text-to-speech can't pronounce them" |
| Parallel tool calling | Agentic/multi-step workflows | "Invoke all relevant tools simultaneously" |
| Research tags | Codebase exploration needed | `<research>` tags |
| Validation tags | Verification required | `<validation>` tags |
| Examples tags | Complex/ambiguous requirements | `<examples>` demonstrating desired behavior |

---

## Execution Strategies

### Single Prompt

A single coherent prompt with clear dependencies and sequential steps.

**When**: Clear goal, single cohesive task, sequential execution required.

**Output**: `.principled/prompts/[slug]-XXX-[name].md`

### Parallel Prompts

Multiple independent prompts that can run simultaneously.

**When**: Independent sub-tasks, no shared file modifications, can be parallelized.

**Output**: `.principled/prompts/[slug]-XXX-[name1].md`, `.principled/prompts/[slug]-XXX+1-[name2].md`, etc.

**Post-creation**: Present execution strategy to user.

### Sequential Prompts

Multiple prompts with dependencies where one must complete before the next starts.

**When**: Dependencies exist, shared files, ordering matters.

**Output**: `.principled/prompts/[slug]-XXX-[name1].md` → `.principled/prompts/[slug]-XXX+1-[name2].md` → etc.

**Post-creation**: Present execution strategy with dependency chain to user.

---

## Quality Standards

### Clarity First

If anything is unclear, ask before proceeding. A few clarifying questions save time.

**Test**: Would a colleague with minimal context understand this prompt?

### Context is Critical

Always include WHY the task matters, WHO it's for, and WHAT it will be used for.

### Be Explicit

Generate prompts with explicit, specific instructions. Default to precision over brevity.

### Scope Assessment

| Task Type | Prompt Length | Structure |
|-----------|---------------|-----------|
| Simple | Concise | Minimal tags |
| Complex | Comprehensive | Full structure with extended thinking |

### Context Loading

Only request file reading when the task explicitly requires understanding existing code:

- "Examine @package.json for dependencies" (when adding new packages)
- "Review @src/database/* for schema" (when modifying data layer)
- Skip file reading for greenfield features

### Output Clarity

Every prompt must specify exactly where to save outputs using relative paths.

### Verification Always

Every prompt should include clear success criteria and verification steps.

---

## Anti-Patterns

### Vague Objective

**Bad**: "Implement auth"

**Good**: "Build JWT-based login with refresh token rotation because stateless auth scales better for API-first architecture"

### Missing Context

**Bad**: "Fix the bug in the code"

**Good**: "Fix the null pointer exception in ./src/services/UserService.ts:45 that occurs when user.email is undefined during registration"

### No Verification

**Bad**: "Create the feature" (no success criteria)

**Good**: "Verify: `npm test` passes, manual smoke test at localhost:3000 shows new UI"

### Generic Instructions

**Bad**: "Go ahead and implement this however you think best"

**Good**: "Follow the existing patterns in ./src/api/*.ts for consistency with error handling"

### No Output Specification

**Bad**: "Generate some tests"

**Good**: "Save test file to ./tests/unit/auth.test.ts with coverage for valid/invalid credentials and token refresh"

### Over-Structuring

**Bad**: Including `<metadata>`, `<history>`, `<notes>` tags that no executing agent will use

**Good**: Only tags that contribute to execution: objective, context, requirements, output, verification

---

## Numeric Thresholds

| Metric | Limit | Rationale |
|--------|-------|-----------|
| Questions per round | 2-4 max | Cognitive load; more = decision fatigue |
| Prompts per generation | 2-4 typical (12 max) | Beyond this suggests task should be split |
| Tasks per prompt | 2-3 typical | Quality degradation at higher task counts |
| Filename words | 5 max | Keep concise for globbing |
| Prompt length | As needed for clarity | Precision over brevity |

**Split signal**: If a task has >3 subsystem touches, >5 files, or requires research + implementation, split into multiple prompts.

---

---

## Success Criteria

- Intake gate completes before generation
- Questioning fills only genuine gaps
- Decision gate loop continues until user confirms
- Prompt structure matches task type (coding/analysis/research)
- Execution strategy matches task dependencies
- Sequential numbering applied correctly
- Output saved to `.principled/prompts/[slug]-[number]-[name].md`
- Decision tree presented to user

---

## Reference Index

**Self-contained:** This skill produces prompts as standalone artifacts. Prompts created by this skill flow to a companion execution skill as a compositional pair (see CLAUDE.md for the compositional pair exemption).
