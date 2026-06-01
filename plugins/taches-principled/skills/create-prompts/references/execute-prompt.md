# Workflow: Execute Prompt

## Sections
- [Identification](#identification)
- [Resolution](#resolution)
- [Execution](#execution)
- [Archival](#archival)
- [Git Commit](#git-commit)

---

Execute a prompt from `.principled/prompts/` and manage its lifecycle.

---

## Identification

### Find the Target

**Single prompt specified:**
- Empty argument → Most recent: `ls -t .principled/prompts/*.md | head -1`
- Number → Zero-padded match: `"5"` matches `005-*.md`
- Text → Fuzzy match: filename contains string

**Multiple prompts specified:**
- List all identifiers
- Default to sequential execution (safety)
- Use `--parallel` flag only when independence is confirmed

---

## Resolution

For each identifier, resolve to concrete file:

| Type | Method |
|------|--------|
| Empty/"last" | `ls -t .principled/prompts/*.md \| head -1` |
| Number | Zero-padded glob: `005` → `glob *005*.md` |
| Text | Contains match: `*auth*` → `*auth*.md` |

**Resolution outcomes:**
- Exactly one match → proceed
- Multiple matches → list candidates, ask user to choose
- No match → report error with available prompts

---

## Execution

### Single Prompt

1. Read complete prompt file
2. Dispatch to subagent for execution
3. Wait for completion
4. Proceed to archival

### Parallel Execution

**Critical:** ALL subagent dispatches in a SINGLE message.

```
[Subagent: prompt 005]
[Subagent: prompt 006]
[Subagent: prompt 007]
(All in one message - concurrent dispatch)
```

1. Read all prompt files
2. Dispatch ALL subagents in one message
3. Wait for all completions
4. Proceed to archival

### Sequential Execution

1. Read first prompt file
2. Dispatch to subagent for execution
3. Wait for completion
4. Archive completed prompt
5. Read next prompt file
6. Repeat until all complete

**Failure handling:** Stop on first failure. Do not continue dependent chain.

---

## Archival

After successful completion:

1. Move prompt to `.principled/prompts/completed/`
2. Preserve original filename
3. Add completion metadata if desired

```bash
mv .principled/prompts/005-*.md .principled/prompts/completed/
```

---

## Git Commit

**Stage files explicitly** (never `git add .`):
```bash
git add [modified files]
git commit -m "[type]: [specific description]"
```

**Commit types:**
| Change | Type |
|--------|------|
| New feature | `feat:` |
| Bug fix | `fix:` |
| Refactor | `refactor:` |
| Style | `style:` |
| Docs | `docs:` |
| Tests | `test:` |
| Maintenance | `chore:` |

---

## Success Criteria

- Target prompt correctly identified
- File resolution returns exactly one match
- Subagent dispatched with correct prompt content
- Prompts archived after completion
- Git commit with explicit file staging