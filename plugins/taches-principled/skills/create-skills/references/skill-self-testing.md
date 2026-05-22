# Skill Self-Testing

## Sections
- [Frontmatter Validation](#1-frontmatter-validation)
- [Threshold Checks](#2-threshold-checks)
- [Trigger Testing](#3-trigger-testing)
- [Structure Checks](#4-structure-checks)
- [Markdown Quality](#5-markdown-quality)
- [Cross-Reference Audit](#6-cross-reference-audit)
- [Pre-Commit Checklist](#pre-commit-checklist)

---

Verify your skill before committing. Run these checks in order.

---

## 1. Frontmatter Validation

### Required Fields

```yaml
---
name: skill-name          # Required
description: "...150 chars max..."  # Required
when_to_use: |           # Required (can be single line or block)
  Do NOT use for ...
---
```

### Valid Field Names

Only use documented frontmatter fields:
- `name`
- `description`
- `when_to_use`
- `user-invocable`
- `allowed-tools`
- `disable-model-invocation`
- `paths`
- `hooks`
- `shell`
- `context`
- `agent`
- `effort`
- `model`
- `arguments`
- `argument-hint`

**Do NOT use:** `metadata`, `related_skills`, `tags`, or any undocumented field.

---

## 2. Threshold Checks

### Character Counts

```bash
# Description (max 150 chars)
description_length=$(echo -n "$(grep -A1 '^description:' SKILL.md | tail -1)" | wc -c)
echo "Description: $description_length/150"

# when_to_use (max 200 chars)
when_to_use_length=$(echo -n "$(grep -A10 '^when_to_use:' SKILL.md | tail -1)" | wc -c)
echo "when_to_use: $when_to_use_length/200"
```

### Line Count

```bash
# Body lines (max 500, excluding frontmatter)
body_lines=$(sed -n '/^---$/,/^---$/!p' SKILL.md | wc -l)
echo "Body: $body_lines/500 lines"
```

---

## 3. Trigger Testing

### Headless Test

```bash
claude -p --dangerously-auto-accept --system PromptFromSkill \
  "test input that should trigger skill" \
  2>/dev/null | grep -E "(skill-name|create-skills)"
```

If the skill name appears in output, it triggered correctly.

### Off-Topic Test

Verify the skill does NOT trigger for off-topic inputs:

```bash
claude -p --dangerously-auto-accept --system PromptFromSkill \
  "unrelated topic that should not trigger" \
  2>/dev/null | grep -c "skill-name"
```

Should return 0.

---

## 4. Structure Checks

### Policy vs. Mechanism

Verify the skill separates:
- Frontmatter: policy (name, description, when_to_use)
- Body: mechanism (principles, patterns, anti-patterns)

### Anti-Patterns Present

If the concept is invertible, there should be an Anti-Patterns section with concrete wrong/right pairs.

### Numeric Thresholds

If the skill involves limits (tokens, tools, tasks), verify thresholds are present with rationale.

---

## 5. Markdown Quality

### No XML Tags

Use markdown sections (##, ###) instead of XML-style tags.

❌ Bad:
```markdown
<policy>...</policy>
<mechanism>...</mechanism>
```

✅ Good:
```markdown
## Policy
...
## Mechanism
...
```

### No Checkpoint Headers

❌ Bad:
```markdown
### Step 1
### Step 2
### Step 3
```

✅ Good: Write the principle that makes the steps obvious.

---

## 6. Cross-Reference Audit

Check that any file paths referenced in the skill actually exist:

```bash
# From skill directory
while read -r path; do
  [ -f "$path" ] || echo "MISSING: $path"
done < <(grep -E '@[a-zA-Z]' SKILL.md | sed 's/@//')
```

---

## Pre-Commit Checklist

- [ ] Frontmatter has only documented fields
- [ ] Description ≤ 150 chars
- [ ] when_to_use ≤ 200 chars
- [ ] Body ≤ 500 lines
- [ ] Policy/Mechanism framing present
- [ ] Anti-Patterns present (if invertible)
- [ ] Numeric thresholds present (if applicable)
- [ ] No broken `@file` references
- [ ] Trigger test passes
- [ ] Off-topic test returns 0

---

## Automated Checks

Run these programmatic checks before committing a new skill:

```bash
#!/bin/bash
# Self-testing checks — verifies minimum structural requirements

SKILL="SKILL.md"
errors=0

# Description length (max 150)
desc_len=$(echo -n "$(grep -A1 '^description:' "$SKILL" | tail -1)" | wc -c)
if [ "$desc_len" -gt 150 ]; then
  echo "FAIL: description $desc_len/150 chars"
  errors=$((errors + 1))
else
  echo "PASS: description $desc_len/150 chars"
fi

# when_to_use length (max 200)
when_len=$(echo -n "$(grep -A10 '^when_to_use:' "$SKILL" | tail -1)" | wc -c)
if [ "$when_len" -gt 200 ]; then
  echo "FAIL: when_to_use $when_len/200 chars"
  errors=$((errors + 1))
else
  echo "PASS: when_to_use $when_len/200 chars"
fi

# Body lines (max 500)
body_lines=$(sed -n '/^---$/,/^---$/!p' "$SKILL" | wc -l)
if [ "$body_lines" -gt 500 ]; then
  echo "FAIL: body $body_lines/500 lines"
  errors=$((errors + 1))
else
  echo "PASS: body $body_lines/500 lines"
fi

# Valid frontmatter fields only
for field in name description when_to_use user-invocable allowed-tools disable-model-invocation paths hooks shell context agent effort model arguments argument-hint; do
  if grep -q "^${field}:" "$SKILL"; then
    echo "PASS: frontmatter field '$field' is valid"
  fi
done

# Check for invalid fields (metadata, related_skills, tags, etc.)
for invalid in metadata related_skills tags; do
  if grep -q "^${invalid}:" "$SKILL"; then
    echo "FAIL: invalid frontmatter field '$invalid'"
    errors=$((errors + 1))
  fi
done

# Skill name format (kebab-case)
skill_name=$(grep '^name:' "$SKILL" | sed 's/^name: //')
if echo "$skill_name" | grep -qv '^[a-z][a-z0-9-]*$'; then
  echo "FAIL: name '$skill_name' is not kebab-case"
  errors=$((errors + 1))
else
  echo "PASS: name '$skill_name' is kebab-case"
fi

if [ "$errors" -eq 0 ]; then
  echo ""
  echo "All structural checks passed."
else
  echo ""
  echo "Structural checks: $errors error(s) found."
fi
exit $errors
```

**What these checks verify:**
- Description ≤ 150 chars
- when_to_use ≤ 200 chars
- Body ≤ 500 lines
- Skill name in kebab-case
- No invalid frontmatter fields

**What they do NOT verify:**
- Teaching effectiveness
- Routing accuracy
- Trigger reliability

For full evaluation, use the grader and trigger benchmark. These automated checks are structural minimums only.