# Plugin Investigation Scratchpad

## Current State
- taches-principled plugin (0.0.2-alpha) has 7 skills: create-plans, execute-plans, create-skills, create-subagents, create-prompts, execute-prompts, subagent-orchestration + code-simplify
- 3 commands: debug, whats-next, simplify
- 7 agents (shared): analyzer, code-reviewer, comparator, grader, prompt-engineer, skill-auditor, subagent-auditor
- .principled/plans/inline-agents-plan.md — existing plan for consolidating agents into skills

## Target Plugins from context-engineering-kit (all v3.0.0, already installed):
- reflexion: reflect/memorize/critique skills
- sadd: judge, do-in-steps, do-in-parallel, do-competitively, tree-of-thoughts, subagent-driven-development, multi-agent-patterns, launch-sub-agent, judge-with-debate, do-and-judge
- sdd: brainstorm, create-ideas, add-task, plan-task, implement-task
- ddd: DDD rules (call-site-honesty, clean-architecture, command-query-separation, etc.)
- docs: update-docs, write-concisely
- fpf: First Principles Framework (query, status, reset, actualize, decay, propose-hypotheses)
- git: load-issues, create-pr, git-worktrees, attach-review-to-pr, analyze-issue, git-notes, commit
- kaizen: root-cause-tracing, plan-do-check-act, why, cause-and-effect, kaizen, analyse, analyse-problem
- review: review-pr, review-local-changes, bug-hunter, code-reviewer, contracts-reviewer, historical-context-reviewer, security-auditor, test-coverage-reviewer
- tech-stack: typescript-best-practices rules
- tdd: write-tests, test-driven-development, fix-tests

## Goal
Integrate selected plugins from context-engineering-kit into taches-principled, refactoring them to:
1. Follow taches-principled skill design principles (policy/mechanism, delta principle, non-brittle)
2. Be individually useful but synergistic when combined
3. Use semantic meaning and shared context for cross-plugin improvement
4. Follow the non-brittle principle — no hard skill references, natural language only
