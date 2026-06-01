# Prompt Patterns Reference

XML-structured templates for coding, analysis, and research tasks. Use these as starting points for generating executable prompts.

## Coding Task Template

```xml
<?xml version="1.0" encoding="UTF-8"?>
<prompt name="coding-task" category="implementation">
  <metadata>
    <task_type>coding</task_type>
    <complexity>single-file|multi-file|system</complexity>
    <execution_strategy>sequential|parallel</execution_strategy>
    <reasoning_depth>low|medium|high|xhigh</reasoning_depth>
  </metadata>

  <objective>
    <statement><!-- What needs to happen, stated plainly --></statement>
    <rationale><!-- Why this matters — context for judgment calls --></rationale>
  </objective>

  <context>
    <project>
      <type><!-- CLI|server|TUI|browser-driven|library --></type>
      <stack><!-- Tech stack relevant to this task --></stack>
      <patterns><!-- File paths or patterns to follow --></patterns>
    </project>
    <constraints>
      <!-- Non-negotiable requirements -->
    </constraints>
  </context>

  <implementation>
    <files>
      <file path="./relative/path/file.ext">
        <action>create|modify|delete</action>
        <description><!-- What this file does and why --></description>
      </file>
    </files>
    <requirements>
      <!-- Specific, unambiguous instructions -->
    </requirements>
  </implementation>

  <verification>
    <success_criteria>
      <!-- Exact conditions that prove completion -->
    </success_criteria>
    <test_command><!-- Command that must pass --></test_command>
  </verification>
</prompt>
```

**Usage:** When the user says "implement", "build", "create", "add feature", or "write code".

---

## Analysis Task Template

```xml
<?xml version="1.0" encoding="UTF-8"?>
<prompt name="analysis-task" category="analysis">
  <metadata>
    <task_type>analysis</task_type>
    <scope><!-- full|partial|targeted --></scope>
    <output_format>markdown|json|structured-text</output_format>
  </metadata>

  <objective>
    <statement><!-- What needs to be understood or evaluated --></statement>
    <question><!-- Specific question to answer --></question>
  </objective>

  <analysis_framework>
    <dimensions>
      <dimension name="correctness">
        <!-- What to check -->
      </dimension>
      <dimension name="performance">
        <!-- What to check -->
      </dimension>
      <dimension name="security">
        <!-- What to check -->
      </dimension>
      <dimension name="maintainability">
        <!-- What to check -->
      </dimension>
    </dimensions>
    <approach><!-- How to investigate --></approach>
  </analysis_framework>

  <context>
    <target><!-- What is being analyzed --></target>
    <known_issues><!-- Pre-existing problems to consider --></known_issues>
  </context>

  <output_format>
    <structure>
      <!-- How findings should be organized -->
    </structure>
    <required_sections>
      <!-- Sections that must appear in output -->
    </required_sections>
  </output_format>

  <synthesis>
    <summary_required>true|false</summary_required>
    <recommendations_required>true|false</recommendations_required>
  </synthesis>
</prompt>
```

**Usage:** When the user says "analyze", "review", "evaluate", "assess", or "audit".

---

## Research Task Template

```xml
<?xml version="1.0" encoding="UTF-8"?>
<prompt name="research-task" category="research">
  <metadata>
    <task_type>research</task_type>
    <scope><!-- broad|focused|exhaustive --></scope>
    <sources_required><!-- web|codebase|docs|mixed --></sources_required>
  </metadata>

  <objective>
    <question><!-- Specific question to answer --></question>
    <goal><!-- What knowledge or answer is needed --></goal>
  </objective>

  <search_strategy>
    <primary_queries>
      <query><!-- Initial search terms --></query>
    </primary_queries>
    <secondary_queries>
      <query><!-- Follow-up searches based on initial findings --></query>
    </secondary_queries>
    <cross_reference>
      <!-- Claims that need multiple sources -->
    </cross_reference>
  </search_strategy>

  <context>
    <what_is_known><!-- Pre-existing knowledge to build on --></what_is_known>
    <what_is_unknown><!-- What this research should discover --></what_is_unknown>
    <constraints><!-- Time limits, source restrictions --></constraints>
  </context>

  <synthesis>
    <consensus_required>true|false</consensus_required>
    <contradictions_handling><!-- How to present disagreement --></contradictions_handling>
    <citation_format><!-- How to cite sources --></citation_format>
  </synthesis>

  <output_format>
    <format>markdown</format>
    <required_elements>
      <!-- What must appear in final output -->
    </required_elements>
  </output_format>
</prompt>
```

**Usage:** When the user says "research", "find out", "investigate", "look into", or "understand".

---

## Multi-Prompt Chaining Template

```xml
<?xml version="1.0" encoding="UTF-8"?>
<prompt name="chain" category="sequential">
  <prompts>
    <prompt index="1" name="discovery">
      <!-- Exploration phase -->
      <objective><!-- What to find --></objective>
      <output><!-- Files/questions to surface --></output>
    </prompt>

    <prompt index="2" name="analysis" depends_on="1">
      <!-- Analysis phase using discovery output -->
      <objective><!-- Building on discovery --></objective>
      <input><!-- Reference to prompt 1 output --></input>
    </prompt>

    <prompt index="3" name="synthesis" depends_on="2">
      <!-- Final synthesis -->
      <objective><!-- Bring it together --></objective>
      <input><!-- Reference to prompt 2 output --></input>
    </prompt>
  </prompts>
</prompt>
```

**Usage:** When the task requires investigation → analysis → synthesis, or any dependency chain.

---

## Parallel Prompt Template

```xml
<?xml version="1.0" encoding="UTF-8"?>
<prompt name="parallel" category="concurrent">
  <prompts>
    <prompt index="1" name="worker-a" isolation="independent">
      <scope><!-- Files/topic for this worker --></scope>
      <objective><!-- What this worker owns --></objective>
    </prompt>

    <prompt index="2" name="worker-b" isolation="independent">
      <scope><!-- Files/topic for this worker --></scope>
      <objective><!-- What this worker owns --></objective>
    </prompt>

    <prompt index="3" name="worker-n" isolation="independent">
      <scope><!-- Files/topic for this worker --></scope>
      <objective><!-- What this worker owns --></objective>
    </prompt>
  </prompts>

  <aggregation>
    <strategy><!-- merge|intersect|synthesize --></strategy>
    <output_format><!-- How results combine --></output_format>
  </aggregation>
</prompt>
```

**Usage:** When independent workstreams can run concurrently without file conflicts.

---

## Pattern Selection Guide

| Task Type | Primary Template | Alternative |
|-----------|------------------|-------------|
| Single file implementation | Coding Task | — |
| Multi-file feature | Coding Task + Multi-Prompt Chain | Parallel for discovery |
| Bug investigation | Analysis Task | Research Task for root cause |
| Security audit | Analysis Task | Coding Task for fixes |
| Architecture review | Analysis Task | — |
| API research | Research Task | — |
| Library evaluation | Research Task + Analysis | — |

## Anti-Patterns

| Wrong | Right |
|-------|-------|
| "Implement auth" | "Build JWT login at ./src/auth/login.ts following ./src/auth/patterns/" |
| "Fix the bug" | "Fix NPE at ./src/service/UserService.ts:45 — add null check" |
| "Make it faster" | "Optimize DB query in ./src/api/users.ts:23 to use index scan" |
| "Add tests" | "Add 3 edge-case tests to ./tests/unit/auth.test.ts covering X, Y, Z" |
| "Improve code quality" | Specific refactor target with file:line reference |

## Quality Signals

Every generated prompt must include:

1. **Objective statement** — plain language description of what and why
2. **Context anchors** — specific files, patterns, or constraints to follow
3. **Output paths** — exact file paths using relative notation
4. **Success criteria** — verifiable conditions, not "looks good"

Missing any of these four produces a prompt that will produce vague results.