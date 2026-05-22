# Skill Trigger Benchmark Report — 2026-05-22

## Summary

Benchmark of 6 key skills in the taches-principled ecosystem. READ-ONLY evaluation — no file modifications.

## Per-Skill Scores

| Skill | Routing (5) | Delta (5) | Posture (5) | Anti-Patterns (5) | Average |
|-------|-------------|-----------|-------------|--------------------|---------| 
| reflexion | 4 | 4 | 5 | 4 | **4.25** |
| code-review | 4 | 4 | 4 | 4 | **4.00** |
| kaizen | 4 | 4 | 5 | 5 | **4.50** |
| fpf-propose | 4 | 4 | 4 | 4 | **4.00** |
| sadd-judge | 4 | 4 | 4 | 4 | **4.00** |
| plan-task | 4 | 4 | 5 | 4 | **4.25** |

**Scoring rubric:**
- Routing: Specific trigger phrases vs. generic language
- Delta: States what skill adds vs. restates default behavior
- Posture: Principles over procedures, concrete wrong/right pairs
- Anti-Patterns: Lower = more vague phrases ("improve", "enhance", "optimize")

---

## Dimension Analysis

### Routing Signal Density (1-5)

**Strongest:** reflexion (4/5)
- "self-reviewing completed work", "high-stakes work needing independent perspectives", "consolidating findings into durable project memory"
- Each method has a distinct trigger scenario
- User can self-diagnose which method they need

**Weakest:** kaizen (4/5)
- "Guardrails for continuous improvement" — "continuous improvement" is slightly generic
- The 5 conditional IF statements save it, but the description itself does not give immediate clarity
- A user seeing "continuous improvement" might not know this is a design-time constraint system

### Delta Clarity (1-5)

**Strongest:** tied across all — all skills clearly state what they add vs. default Claude behavior

Notable deltas:
- reflexion: adds structured quality workflows (reflect/critique/memorize cycle)
- kaizen: adds four design-time constraint pillars
- sadd-judge: adds meta-judge pattern separating criteria generation from application
- plan-task: adds multi-phase refinement with independent quality gates

**Weakest:** None significantly — all skills articulate their delta adequately.

### Teaching Posture (1-5)

**Strongest:** kaizen (5/5)
- Four pillars each with a **Core Principle**, concrete **Red Flags**, and wrong/right pairs with consequence
- "Make it work, then make it clear, then make it efficient — never all three at once"
- "Design systems that make errors impossible or immediately visible"
- Each pillar is a teachable principle, not a procedure

**Strongest runner-up:** plan-task (5/5)
- Complexity triage table with signal/depth/procedure for each level
- Weighted evaluation rubrics per phase
- Integrity rules with specific failure cases ("Score 5.0/5.0 is a hallucination — reject and re-run")
- Phase diagrams and dispatch requirements

**Weakest:** fpf-propose (4/5)
- Steps are concrete but the teaching is more process-oriented than principle-oriented
- "ADI cycle" is named but the why behind the cycle is not articulated as strongly

### Anti-Pattern Quality (0-5, higher=better)

**Best:** kaizen (5/5)
- Zero vague improvement verbs
- Red flags are specific: "Users should just be careful", "I prefer to do it my way", "We might need this someday"
- No filler content

**Weakest:** None significantly poor — all skills scored 4 or 5.

Notable anti-patterns found:
- plan-task: "--fast mode" could be more descriptive (user must read body to understand it skips verifications)
- sadd-judge: "high-stakes consensus" is slightly vague — how high is high stakes?
- fpf-propose: "complete First Principles Framework cycle" — "complete" is a mild filler word

---

## Rankings

### Best Scoring: kaizen (4.50 average)

**Praise:**
- The four-pillar structure with red flags is exemplary teaching posture
- "Poka-Yoke" concept (error-proofing at design time) is a genuinely teachable principle with concrete application
- Red flags are specific and consequential — each one describes a wrong approach with its specific failure mode
- No vague improvement language; everything is a constraint with a rationale
- The anti-pattern score of 5/5 is the highest possible and hardest to achieve

**Why it leads:** Strongest combination of delta clarity, teaching principles, and anti-pattern-free language.

---

### Second Tier: reflexion and plan-task (4.25 average)

**reflexion praise:**
- "Your value is measured by what you prevent from shipping broken" is a crisp, memorable principle
- Complexity triage table with Quick/Standard/Deep paths gives users clear self-routing
- Scoring scale with frequency context (e.g., "< 5% of evaluations" for 5/5) teaches calibration
- The three-method cycle (reflect → critique → memorize) is well-explained with clear relationships

**reflexion gap:**
- "structured quality workflows" in description is slightly generic — user needs to read body to understand the three methods

**plan-task praise:**
- Phase structure with weighted rubrics is the most technically rigorous teaching in the ecosystem
- Integrity rules prevent common evaluation failures
- Configuration table with argument definitions is exemplary documentation

**plan-task gap:**
- Description is dense but includes technical details better suited for body
- Flags like `--fast` and `--one-shot` are abbreviated aliases that require reading body to understand

---

### Third Tier: code-review, fpf-propose, sadd-judge (4.00 average)

**code-review (4.00):**
- Decision router with explicit IF/THEN statements is strong
- Agent table with roles and "Best For" column is clear
- Phase structure (Preparation → Multi-Agent → Consolidation) is well-defined

**code-review gap:**
- "confidence-scored filtering" is somewhat technical jargon — could be clearer about what confidence scoring means for the user
- "security, bugs, contracts, and coverage" — contracts is ambiguous (API contracts? legal contracts?)

**fpf-propose (4.00):**
- Artifact table with explicit paths is helpful
- Step-by-step process is concrete and reproducible
- Evidence hierarchy (L0/L1/L2) is well-structured

**fpf-propose gap:**
- "First Principles Framework" — acronym FPF is introduced but not defined in description
- Step 1 "Initialize Context" is vague about what "context" means
- Process is more procedural than principle-based

**sadd-judge (4.00):**
- Decision router with clear binary choice (routine vs. high-stakes) is strong
- Meta-judge separation principle is teachable
- Design Decisions section explains the "why" behind the pattern

**sadd-judge gap:**
- "meta-judge" is a jargon term introduced without explanation in the description
- "judge sub-agents" — user may not know this refers to the sadd-judge skill itself
- The 5 design decision explanations are thorough but feel like they're filling space rather than teaching principles

---

## Overall Trigger Reliability Verdict

**RELIABLE**

All six skills score 4.00 or above. No skill scored below "adequate" on any dimension. The trigger routing is sufficient for users to self-select the correct skill in most cases.

**Confidence: HIGH** — these skills will route correctly when invoked by description matching.

---

## Specific Recommendations

### For kaizen (keep as-is):
No changes recommended. This skill exemplifies the teaching posture and anti-pattern-free writing the ecosystem should aim for.

### For reflexion:
Consider a slightly more descriptive tagline — "structured quality workflows" is the weakest part of an otherwise strong description. Possible alternative: "Self-reflection, multi-perspective critique, and durable learning capture for completed work."

### For code-review:
Clarify "contracts" — is this API contracts, legal contracts, or something else? The agent table uses it generically, but users may not understand what "Contracts Reviewer" evaluates.

### For fpf-propose:
Define FPF in the description: "First Principles Framework (FPF)" would make the description stand-alone readable.

### For sadd-judge:
"meta-judge" is a coined term that may confuse new users. Consider describing the pattern briefly: "Evaluate work by generating evaluation criteria first, then applying them with isolated judges."

### For plan-task:
The `--fast` and `--one-shot` flags are powerful but invisible in the description. Consider whether these should appear in a secondary line or whether the description should hint at the different refinement modes.

---

## Methodology

Evaluated by reading SKILL.md frontmatter (name + description only) then scoring dimensions based on description content. Anti-pattern scoring based on full description analysis.

Scoring criteria applied per CLAUDE.md Teaching Effectiveness dimensions:
- Routing Signal (40% weight): Does description give clear trigger phrases?
- Delta Clarity (30%): Does it state what adds vs. default?
- Teaching Posture (20%): Principles over procedures?
- Anti-Pattern Quality (10%): Concrete wrong/right pairs with consequence?