---
name: shared-rules
description: "Shared project rules injected into all subagents. Ensures consistent behavior across the agent fleet."
when_to_use: |
  This skill is preloaded into subagents via rule-propagator.
  Do not invoke directly — use rule-propagator to manage.
disable-model-invocation: false
---

# Shared Project Rules

These rules are automatically injected into all subagents to ensure consistent behavior across the fleet.

## Coding Standards

- Use TypeScript strict mode for new code
- Follow existing code style in the target file
- Add tests for new functionality
- Run linter before committing

## Error Handling

- Never swallow exceptions silently
- Log errors with context before propagating
- Use typed errors where possible
- Fail fast on invalid state

## Communication

- Write concise, direct responses
- Use code blocks for all code examples
- Include file paths when referencing files
- Document decisions with rationale

## Tool Usage

- Prefer native tools over shell scripts
- Never use eval/exec on user input
- Verify file operations before committing
- Use Read before Write on existing files