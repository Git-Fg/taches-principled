# Checkpoint Types Reference

Checkpoints mark points in execution where Claude yields to human input. They are NOT for Claude doing work — they are for verification and decisions.

---

## Core Principle

**If Claude CAN do it via CLI/API/tool, Claude MUST do it.**

Checkpoints exist only for:
1. Things that genuinely require human judgment
2. Actions with no CLI or API

---

## Checkpoint Types

### checkpoint:human-verify

**Trigger:** Claude automated, human confirms

**When to use:**
- Visual checks (UI appearance, layout, rendering)
- Content review (text, copy, generated assets)
- Manual testing scenarios
- Reviewing Claude's work before proceeding

**Protocol:**
1. Claude completes the automated work
2. Claude presents what was done (file paths, outputs, test results)
3. Claude waits for human confirmation
4. Human reviews and confirms or requests changes
5. Claude resumes or fixes based on feedback

**Example:**
```markdown
### Task 3: Create login page UI
Files: src/app/login/page.tsx
Action: Build login form with email/password fields, submit button, error handling
Verify: `npm run build` succeeds, page renders without console errors
Done: Login form displays, validates input, submits to /api/auth/login
Checkpoint: checkpoint:human-verify  # Human verifies UI matches brand guidelines
```

### checkpoint:decision

**Trigger:** Human makes implementation choice

**When to use:**
- Architecture decisions (auth provider, database choice)
- Library selection (state management, UI framework)
- API design (REST vs GraphQL, naming conventions)
- Third-party service integration decisions

**Protocol:**
1. Claude presents the decision context
2. Claude lays out options with pros/cons
3. Claude waits for human choice
4. Human selects option (or proposes alternative)
5. Claude documents decision and resumes with chosen approach

**Example:**
```markdown
### Task 2: Choose authentication method
Action: Implement JWT auth with refresh token rotation
Options:
  A) Use jose library (Edge runtime compatible, modern)
  B) Use jsonwebtoken (CommonJS only, wider ecosystem)
Verify: Selected library integrates without runtime errors
Done: Auth implementation complete with chosen library
Checkpoint: checkpoint:decision  # Human chooses auth library
```

### checkpoint:human-action

**Trigger:** Human performs action (no CLI or API available)

**When to use:**
- Email verification links (must open email client)
- Two-factor authentication (requires authenticator app)
- Account approval in web dashboard (requires web login)
- External service approvals (Stripe, AWS, Google Cloud)

**Protocol:**
1. Claude creates necessary credentials/config
2. Claude generates the verification link or instructions
3. Claude waits for human to complete the action
4. Human completes action externally
5. Claude verifies completion via API or by continuing

**Example:**
```markdown
### Task 4: Set up Stripe webhook
Files: .env, src/lib/stripe.ts
Action: Create Stripe webhook endpoint, set up event handling for checkout.session.completed
Verify: Stripe can reach webhook endpoint
Done: Webhook receives and processes test event
Checkpoint: checkpoint:human-action  # Human must log into Stripe dashboard and add webhook URL
```

---

## Checkpoint Anti-Patterns

### ❌ Using checkpoints for things Claude can do

```markdown
# WRONG - Claude has CLI for this
### Task: Deploy to Vercel
Checkpoint: checkpoint:human-action  # Human should deploy via Vercel CLI
```

Claude has `vercel deploy` CLI. No checkpoint needed.

### ❌ Checkpoint for "review my code"

```markdown
# WRONG - unless genuinely visual
### Task: Implement feature X
Checkpoint: checkpoint:human-verify  # Human reviews code (but code review isn't visual)
```

Code review is part of normal execution. Only use verify checkpoint if human needs to see rendered output.

### ❌ Missing checkpoint when genuinely needed

```markdown
# WRONG - will fail without human action
### Task: Set up GitHub OAuth app
Action: Create OAuth app, get client ID/secret
Done: OAuth app configured in GitHub
```

This requires human to log into GitHub and create the OAuth app. Missing checkpoint.

---

## Checkpoint Sizing

Checkpoints should be **infrequent**. Most tasks should execute autonomously.

**Good ratio:** 1 checkpoint per 5-10 tasks maximum

If every task needs a checkpoint, the plan is too granular or too ambitious.

---

## Documenting Checkpoints

Always include in checkpoint declaration:
1. **What** needs human attention (not "verify", but "verify the UI matches the design mockup")
2. **Why** it cannot be automated (no CLI, requires judgment)

```markdown
Checkpoint: checkpoint:human-verify  # Human verifies dark mode toggle matches brand colors
```

Not:

```markdown
Checkpoint: checkpoint:human-verify
```

---

## Escalation and Timeout

Checkpoints wait for user input, but users may not respond immediately.

**Timeout behavior:**
- If a checkpoint is reached and user is offline/unresponsive, the checkpoint remains pending
- Do NOT proceed past a checkpoint without user input — checkpoints exist to prevent execution errors
- After 3 reminders (1 per conversation turn), offer alternatives

**Reminder format:**
```
Checkpoint [{id}] pending — awaiting your confirmation/decision.
Type 'continue' to proceed or 'handoff' to pause execution.
```

**Escalation options:**
- `continue` — User approves and execution proceeds
- `handoff` — Create .continue-here.md and pause for later resumption
- `skip` — Only for informational checkpoints (not recommended for decision/human-action)