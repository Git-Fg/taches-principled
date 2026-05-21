# Changelog

All notable changes are documented here.

## [0.0.2-alpha]

### Added
- **create-prompts skill**: Creates executable XML-structured prompts for Claude Code sessions
  - Adaptive intake gate with task type detection
  - Contextual questioning with templates (dashboard type, auth method, etc.)
  - Decision gate loop until user confirms
  - Single/parallel/sequential prompt generation
  - XML patterns for coding/analysis/research tasks
- **execute-prompts skill**: Executes prompts via delegated sub-tasks
  - Policy vs. Mechanism framing for strategy selection
  - Single/parallel/sequential execution via Task tool
  - Critical constraint: parallel Task calls in single message
  - Argument parsing and file resolution
  - Archival to `./prompts/completed/` and git workflow
- **create-prompts/workflows/execute-prompt.md**: Workflow reference for prompt execution

### Changed
- README updated: Skills count 4 → 6, Policy/Mechanism table expanded

## [0.0.1-alpha]

### Added
- CLAUDE.md development guide with operational rules and best practices

### Changed
- Downgraded version to `0.0.1-alpha` for early development

## [1.1.0]

### Changed
- Renamed from `taches-modernized` to `taches-principled`
- All 4 skills enhanced with Policy/Mechanism framing sections
- All 4 skills enhanced with Anti-Patterns sections
- All 4 skills enhanced with Numeric Thresholds tables
- README updated with Skill Ecosystem dependency map
- README updated with Policy vs. Mechanism table

### Removed
- MCP server creation skill and command (builds on existing MCP tooling instead)

### Fixed
- create-hooks: UserPromptSubmit added to events table
- create-hooks: malformed hookSpecificOutput JSON fixed
- create-hooks: broken jq syntax in prettier example
- create-hooks: broken reference to user-gates.md removed
- create-plans: missing frontmatter added
- create-subagents: missing frontmatter added, broken file references removed
- create-mcp-servers: Rule 2 (cwd vs --directory) clarified
- All reference files gained frontmatter

## [1.0.0] — Initial release

### Added
- 4 principle-based skills: create-skills, create-subagents, create-hooks, create-plans
- 8 slash commands: /create-skill, /create-subagent, /create-hook, /create-plan, /audit-skill, /audit-subagent, /debug, /whats-next
- 3 agent types: code-reviewer, skill-auditor, subagent-auditor
- plugin.json and marketplace.json for GitHub marketplace
- MIT license

### Principles
- Goals over procedures
- Principles over steps
- Trust Claude's intelligence
- Concise by default
- Gotchas, not rules
