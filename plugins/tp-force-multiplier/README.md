# tp-force-multiplier

Hook-driven coaching plugin that steers Claude to use subagents and skills more.

## What It Does

Observes behavior patterns in real-time and surfaces immediate coaching hints. No tool injection, no hardcoded skill names — pure semantic coaching.

## How It Works

One hook handler:

| Hook | When | What It Does |
|------|------|--------------|
| `SessionStart` | Session begins | Lightweight reminder to use subagents/skills |

## Coaching Messages

```
SessionStart: "Tip: Spawn subagents for parallel investigation. Use skills for method frameworks when workflows are complex."
```

## Installation

This plugin is part of the taches-principled marketplace. Install via Claude Code plugin marketplace.

## Principles

- **Semantic only**: Describe behavior, don't name tools/skills
- **Coaching not policing**: Suggest, never mandate
- **Zero blocking**: Plugin never denies operations