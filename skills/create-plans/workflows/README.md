# Workflows

## Sections
- [execute-phase.md](#execute-phasemd)

---

This directory contains executable workflows for the create-plans skill.

---

## execute-phase.md

**Purpose:** Execute a phase plan (PLAN.md) and produce a summary (SUMMARY.md).

**When used:** When user responds with "execute", "run", "do it", or invokes `/run-plan`.

**What it does:**
1. Identifies next unexecuted plan from ROADMAP.md
2. Loads and follows the PLAN.md prompt exactly
3. Handles deviations automatically (5 embedded rules)
4. Creates SUMMARY.md documenting what was done
5. Updates ROADMAP.md progress
6. Commits work to git

**Deviation Rules embedded:**
- Rule 1: Auto-fix bugs (broken behavior)
- Rule 2: Auto-add missing critical (security/correctness gaps)
- Rule 3: Auto-fix blockers (can't proceed)
- Rule 4: Ask about architectural changes (major structural)
- Rule 5: Log enhancements to ISSUES.md

**Key features:**
- Authentication gate handling (pauses for CLI login, resumes after)
- Verification failure gate (stops and asks user on failure)
- Context usage monitoring
- Git commit with phase-plan scoped messages

**Reference:** Used in SKILL.md Reference Index under "Workflows"
