---
name: context-fork-blackbox
description: context: fork transforms a skill into an isolated blackbox (input → output). The skill body becomes the subagent's task prompt; only the final result returns to the main conversation. Optional `agent:` field selects the subagent type — a "subagent++" you can specialize with preloaded skills.
---

# Rule: MUST treat `context: fork` skills as isolated blackbox contracts (input → output)

**Why:** A skill with `context: fork` does not execute inline in the main conversation. The harness spawns a fresh subagent whose context starts empty; the skill's frontmatter + body are injected as that subagent's task prompt; only the final result of that subagent returns to the main conversation. The forked skill therefore cannot see the main conversation's history, the user's earlier turns, or any sibling skill's reasoning. Its only inputs are: its own frontmatter, the user's literal request (passed via `$ARGUMENTS`), and any preloaded skills from the `agent:` field. Its output is whatever text the subagent produces as its final response. **This is the blackbox input/output model.** A forked skill that does not document its input contract in frontmatter (`description`, `when_to_use`, `argument-hint`, `arguments`) and does not spec its output format in the body is unsable — the subagent has nothing to steer on and produces output that may not match the caller's expectations. This rule was authored after the 1.22.3 code-review caught a forked skill with a generic 162-char description and no input/output contract.

## The blackbox mental model

```
┌─────────────────────────────────┐
│  Main conversation (Claude)     │
│  ┌───────────────────────────┐  │
│  │ Subagent (forked skill)   │  │
│  │                           │  │
│  │  IN:                      │  │
│  │   - skill frontmatter     │  │
│  │   - skill body            │  │
│  │   - $ARGUMENTS (user)     │  │
│  │   - preloaded skills      │  │
│  │                           │  │
│  │  [runs in isolation:      │  │
│  │   tool calls, file reads, │  │
│  │   reasoning, all hidden]  │  │
│  │                           │  │
│  │  OUT:                     │  │
│  │   final text response     │  │
│  │                           │  │
│  └───────────────────────────┘  │
│       ↑ only the OUT escapes ↑  │
└─────────────────────────────────┘
```

The skill's body is the **task prompt** for the subagent. The skill's frontmatter is the **invocation contract**. Treat both as if you were writing a function signature + docstring for an API.

## Rule

### What `context: fork` does (and does NOT do)

- `context: fork` does NOT mean "this skill orchestrates subagents." Orchestration is a *consequence* of fork, not its purpose.
- `context: fork` DOES mean "this skill runs in a fresh, isolated subagent context with no main-conversation history."
- The skill body becomes the subagent's task prompt. The subagent's response is the skill's output.
- The subagent's intermediate work (tool calls, file reads, reasoning) NEVER reaches the main conversation.

### When to use `context: fork`

Use `context: fork` when the skill:
- Reads many files / makes many tool calls to produce a small summary
- Performs exploratory reasoning the main agent should not see in full
- Has side effects the user wants sandboxed (e.g. `disable-model-invocation: true` + `context: fork` for deploys)
- Must not see the main conversation's state (TDD: don't let the implementation context see what the tests expect)
- Produces a clean final artifact (a report, a verdict, a transformed file) the main conversation can use directly

Do NOT use `context: fork` when:
- The skill is a one-line lookup
- The user needs the skill's intermediate work visible (debugging, transparency)
- The skill's value IS in-context application (e.g. a style guide the main agent must read while writing)
- The subagent's spawn overhead exceeds the context savings

### The `agent:` field — a "subagent++" you can customize

`agent: <type>` selects which subagent type runs the forked skill. Options:

- `general-purpose` (default) — full tool pool, full reasoning. Use for complex multi-step work.
- `Explore` — fast read-only codebase search, optimized for understanding.
- `Plan` — architecture analysis, step planning. Use when the skill produces an implementation plan.
- `Bash` — command execution only. Use for shell-heavy operations.
- Any custom subagent defined in `.claude/agents/<name>.md` or `plugins/*/agents/*.md` — the forked skill runs AS that agent, inheriting its system prompt and any preloaded skills.

**The "subagent++" insight:** by picking a custom agent that preloads other skills via `skills: [X, Y]` frontmatter, you can create a forked skill that runs with extra domain knowledge the default subagent would not have. Example: a `code-review-fork` skill that runs as a `senior-reviewer` custom agent which preloads `fpf` (first-principles reasoning) and `ddd` (domain-driven design) — the forked skill gets to use both at runtime without polluting the main conversation's context.

### Frontmatter is the input contract

A forked skill's frontmatter is the ONLY contract the caller sees. The caller (main agent or another skill) has no access to the skill's body until the fork happens, and the body becomes a task prompt the subagent reads in isolation. Therefore:

- `description` MUST describe what the skill does AND what the caller can expect to receive (a report, a verdict, a transformed file, a verdict, a plan, etc.). Front-load output format. First 200 chars survive truncation.
- `when_to_use` MUST list the trigger phrases and use cases. The main agent uses this to decide when to invoke the skill. The forked subagent uses this as additional context for what kind of request it is processing.
- `argument-hint` SHOULD specify the expected arguments. Format: `[issue-number] [format]` or `[file] [mode]`. Visible during autocomplete, but also tells callers what to pass.
- `arguments` SHOULD declare named positional arguments when the skill expects structured input. Example: `arguments: [server-path, output-format]`. The forked subagent can use `$server-path` and `$output-format` substitutions in the body.
- `disable-model-invocation: true` SHOULD be combined with `context: fork` for skills with side effects (deploys, commits, sends) — prevents the main agent from auto-firing the skill while the fork provides isolation for the actual operation.

### Body is the task prompt

The skill body is what the forked subagent reads as its instructions. It MUST be written as a self-contained task prompt:

- "You are a `<role>`." — the subagent needs a role statement since it has no main-conversation context.
- "Your input is `<input description>`. It will be provided via `$ARGUMENTS` or in your conversation." — explicit input contract.
- "Produce `<output format>`." — explicit output contract with shape.
- "Do not do `<boundary>`." — negative scope to prevent the subagent from drifting.
- Examples of expected input → expected output — the subagent has no prior examples to anchor on, so include 1-2 in the body.

### Output format is the output contract

A forked skill's output is whatever the subagent writes as its final response. The main agent sees only this. Therefore the body MUST specify the output format explicitly:

- "Return a JSON object with `{ score, evidence, recommendation }`." (structured output)
- "Return a markdown report with sections X, Y, Z." (document output)
- "Return a single line: `PASS` or `FAIL`." (minimal output)
- "Write the result to `<path>` AND return a one-line summary." (side effect + summary)

Without an explicit output spec, the forked subagent produces whatever prose seems natural, and the main agent has no structured way to consume it.

## Verification

Before shipping a `context: fork` skill, verify:

```
head -10 plugins/<plugin>/skills/<skill>/SKILL.md
```

Then check:

1. **`description` has the output format in the first 200 chars.** "Run a full quality evaluation ... and return a markdown report with ..." beats "Run a full quality evaluation."
2. **`when_to_use` lists trigger phrases** the main agent will see in routing.
3. **`argument-hint` is set** if the skill expects arguments.
4. **Body starts with "You are a `<role>`"** — the subagent has no role context otherwise.
5. **Body has an explicit "Produce `<format>`"** section — the subagent needs an output spec.
6. **Body has 1-2 input/output examples** — the subagent needs anchors.
7. **`agent: <type>` matches the work** — `Explore` for search, `Plan` for plans, `general-purpose` for general, custom for specialized.

## Bad / Good

**Bad:** A forked skill that looks like a normal skill:
```
---
name: quality-evaluate
description: "Run a full quality evaluation of an MCP server. Use when the user says 'evaluate my MCP server'."
context: fork
agent: general-purpose
---

You are a quality orchestrator. Your job is to run a full 8-dimension evaluation of an MCP server by spawning 8 judge subagents in parallel, reading their outputs, applying the tiebreak rule, and synthesizing a markdown report.
```
The description is user-vocabulary only — no output format. The body says "your job is to ..." but does not say "produce a markdown report with these sections". The forked subagent has no role anchor ("a quality orchestrator" presupposes context the subagent does not have) and no output spec. The main agent receives whatever prose the subagent invents.

**Good:** A forked skill that documents its blackbox contract:
```
---
name: quality-evaluate
description: "Spawn subagents to fan out a full 8-dimension quality evaluation of an MCP server. Returns a markdown report with per-dimension scores, evidence, and verdict. Use when the user says 'evaluate my MCP server', 'audit MCP quality', or 'run quality judge'."
context: fork
agent: general-purpose
argument-hint: "[server-path]"
---

You are a quality orchestrator. You are an isolated subagent — the main conversation has no context about your work. You will receive the path to an MCP server via $ARGUMENTS (or as a literal in the conversation). Produce a markdown report with these sections:

1. **Header**: server name, date, verdict (PASS/FAIL)
2. **Summary table**: `| dimension | score | evidence |`
3. **Findings**: one section per PARTIAL or FAIL with evidence and recommendation
4. **EXEMPLARY dimensions**: brief list

## Workflow

1. **Establish server artifacts** at $ARGUMENTS[0]. Reject the task if the server is not built.
2. **Spawn 8 mcp-quality-judge subagents in parallel**, one per dimension...
3. **Wait for all 8 JSON outputs.** ...
4. **Synthesize the report** in the format above.
```

The description front-loads the output format ("Returns a markdown report with per-dimension scores, evidence, and verdict"). The body starts with a role statement and an explicit output spec. The forked subagent has everything it needs to produce a structured artifact the main agent can use.
