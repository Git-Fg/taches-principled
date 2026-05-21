---
name: issues
description: "Track deferred enhancements, logged issues, and non-critical deviations from plan execution."
when_to_use: |
  When a deviation is logged as non-blocking (Rule 5) or when enhancements are deferred to a future phase.
---

# Project Issues

## Deferred Enhancements

| ISS-XXX | Description | Target Phase | Status |
|---------|-------------|--------------|--------|
| ISS-001 | [description] | [phase] | open |

## Logged Deviations

| ISS-XXX | Source | Description | Resolution |
|---------|--------|-------------|------------|
| ISS-002 | [plan] | [what happened] | [how resolved] |

## Open Decisions

| DEC-XXX | Question | Options | Decision |
|---------|----------|---------|----------|
| DEC-001 | [open question] | A, B, C | pending |

---

## Usage

- Add ISS-XXX entries when Rule 5 (non-critical enhancement) is triggered
- Update status as items are resolved
- Reference from SUMMARY.md using `ISSUES.md: ISS-XXX` format