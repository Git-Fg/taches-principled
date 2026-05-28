---
name: security
description: "Security scan: vulnerabilities, secrets, auth patterns. Modes: SAST, DEPENDENCY-AUDIT, SECRETS-DETECTION, COMPLIANCE."
when_to_use: |
  SAST: 'security audit', 'XSS', 'SQL injection', 'auth review'
  DEPENDENCY-AUDIT: 'scan dependencies', 'npm audit', 'vulnerable dependencies'
  SECRETS-DETECTION: 'API key exposed', 'hardcoded secret', 'credentials in code'
  COMPLIANCE: 'compliance check', 'GDPR', 'SOC2', 'OWASP'
  IMMEDIATELY before production deployment, before merging security-related PRs, or when fixing vulnerabilities.
  Do NOT use for architecture design (use ddd) or general code quality (use refine REVIEW).
user-invocable: true
argument-hint: "[mode] [target] [--severity critical|high|medium|low]"
---

## Routing Guidance

| If you need to... | Use this mode |
|-------------------|---------------|
| Find code vulnerabilities (injection, auth, access control) | SAST |
| Check for outdated/vulnerable dependencies | DEPENDENCY-AUDIT |
| Find API keys or credentials in code | SECRETS-DETECTION |
| Verify compliance with security standards | COMPLIANCE |

**Quick routing:** Scan code patterns = SAST. Scan packages = DEPENDENCY-AUDIT. Scan for secrets = SECRETS-DETECTION. Audit compliance = COMPLIANCE.
---

## Decision Router

IF scanning for injection, auth, or access control patterns in code → **SAST** mode
  **ALWAYS spawn pattern-matching subagents per OWASP category**
IF checking for vulnerable or outdated dependencies → **DEPENDENCY-AUDIT** mode
  **ALWAYS spawn audit subagents per package manager**
IF finding exposed API keys, tokens, or credentials in code → **SECRETS-DETECTION** mode
  **ALWAYS spawn scanner subagents per secret type**
IF verifying compliance with security standards or certifications → **COMPLIANCE** mode
  **ALWAYS spawn compliance checker subagents for each regulation**
IF ambiguous → ask: "Are you scanning code patterns, dependencies, exposed secrets, or compliance standards?"

---

# Security Hub

Four modes targeting distinct security surfaces. Each mode addresses a different attack vector or compliance requirement.

| Mode | Attack Surface | Tools |
|------|---------------|-------|
| **SAST** | Code-level vulnerabilities | Pattern matching, AST analysis |
| **DEPENDENCY-AUDIT** | Supply chain vulnerabilities | Package audit, CVE databases |
| **SECRETS-DETECTION** | Credential exposure | Pattern scanning, entropy analysis |
| **COMPLIANCE** | Standards compliance | Checklist mapping, gap analysis |

---

# SAST Mode

Static Application Security Testing — identify code-level vulnerabilities through pattern analysis.

## OWASP Top 10 Coverage

| OWASP Category | What to Find | Common Patterns |
|----------------|--------------|-----------------|
| **A01 Broken Access Control** | Missing authorization, IDOR, privilege escalation | Direct object references, role checks without DB verification, client-side auth |
| **A02 Cryptographic Failures** | Weak crypto, hardcoded keys, improper storage | MD5/SHA1 for passwords, ECB mode, keys in source |
| **A03 Injection** | SQL, NoSQL, OS, LDAP injection | String concatenation in queries, unsanitized input |
| **A04 Insecure Design** | Business logic flaws, missing rate limits | No throttling, predictable tokens, missing validation |
| **A05 Security Misconfiguration** | Default creds, verbose errors, open cloud storage | Stack traces in production, CORS wildcard, debug mode |
| **A06 Vulnerable Components** | Outdated libraries with known CVEs | (see DEPENDENCY-AUDIT) |
| **A07 Auth Failures** | Weak auth, session fixation, credential stuffing | No rate limiting on login, predictable session IDs |
| **A08 Data Integrity Failures** | Deserialization attacks, CI/CD injection | Pickle/yaml unsafe deserialization, unvalidated pipeline inputs |
| **A09 Logging Failures** | Missing audit trails, no breach detection | No login failure logging, missing transaction logs |
| **A10 SSRF** | Server-side request forgery | URL validation without allowlist, redirect following |

## Decision Criteria

| Situation | Action |
|-----------|--------|
| User input flows to database query | Flag injection risk, check parameterization |
| Auth checks missing on data access | Flag broken access control |
| External URL constructed from user input | Flag SSRF risk |
| Cryptographic operation with hardcoded key | Flag critical, suggest env vars |
| Error messages expose stack traces | Flag security misconfiguration |
| File upload without type validation | Flag injection and path traversal |
| Deserialization of untrusted input | Flag A08, suggest schema validation |

## Code Patterns to Flag

### Injection Patterns (Critical)

```
# SQL Injection — flag all of these
query = "SELECT * FROM users WHERE id=" + userId
cursor.execute(f"SELECT * FROM users WHERE id={userId}")

# Safe patterns
cursor.execute("SELECT * FROM users WHERE id=%s", (userId,))
query = db.select(User).where(User.id == userId)
```

### Broken Access Control (High)

```
# IDOR — direct object reference without ownership check
def get_invoice(invoice_id):
    return db.get(Invoice, invoice_id)  # No user check

# Safe pattern
def get_invoice(invoice_id):
    invoice = db.get(Invoice, invoice_id)
    if invoice.user_id != current_user.id:
        raise Forbidden()
    return invoice
```

### SSRF Patterns (High)

```
# Unsafe — user input in URL construction
response = requests.get(user_provided_url)

# Safe patterns
parsed = urlparse(url)
if parsed.hostname not in ALLOWED_HOSTS:
    raise ValidationError()
if parsed.hostname.endswith('.internal'):
    raise ValidationError()
```

## Anti-Patterns with Consequences

| Wrong | Right | Consequence |
|-------|-------|-------------|
| Client-side auth checks only | Server-side authorization on every request | Client-side checks are trivially bypassed |
| Input validation with allowlist bypass | Strict allowlist validation | Blocklists miss edge cases, allowlists miss future bypasses |
| Storing passwords with reversible encryption | Password hashing with salt (bcrypt/argon2) | Reversible encryption enables credential theft |
| Generic error messages | Structured error codes | Stack traces reveal internal architecture to attackers |
| Debug mode in production | Environment-specific logging levels | Debug output exposes sensitive context |
| CORS wildcard for development | Explicit origin allowlist | Wildcard allows cross-site data exfiltration |

---

# DEPENDENCY-AUDIT Mode

Scan dependencies for known vulnerabilities and supply chain risks.

## Decision Criteria

| Situation | Action |
|-----------|--------|
| After adding new dependency | Audit immediately, check for known CVEs |
| Periodic security review | Check for outdated packages with known vulnerabilities |
| After vulnerability disclosure | Identify affected projects and prioritize updates |
| Before major release | Full dependency audit with remediation plan |

## Audit Process

1. **Inventory** — List all direct and transitive dependencies with versions
2. **Vulnerability Check** — Query CVE databases (NVD, OSV, GitHub Advisory)
3. **Severity Assessment** — Rate by CVSS score, exploitability, impact
4. **Remediation** — Update to patched version, find alternative, or accept risk with mitigation

## Vulnerability Severity Mapping

| CVSS Score | Rating | Action |
|------------|--------|--------|
| 9.0-10.0 | Critical | Update immediately, consider removal |
| 7.0-8.9 | High | Update within 7 days |
| 4.0-6.9 | Medium | Update within 30 days |
| 0.1-3.9 | Low | Update at next release cycle |

## Common Supply Chain Risks

| Risk | Indicator | Remediation |
|------|-----------|-------------|
| Typosquatting | Similar names to popular packages | Verify exact package name, check publisher |
| Maintainer takeover | Abandoned packages with new commits | Find maintained alternative |
| Malicious code | Unexpected network calls, file I/O | Review source, use lockfiles |
| Dependency confusion | Internal package shadowing public | Use scoped namespaces, verify registry |

## Anti-Patterns with Consequences

| Wrong | Right | Consequence |
|-------|-------|-------------|
| No lockfile committed | Commit lockfiles for reproducible builds | Mismatched versions expose vulnerabilities |
| Auto-update without review | Review changelogs before updating | Breaking changes introduce new vulnerabilities |
| Ignoring audit warnings | Treat audit output as blocking | Known vulnerabilities become exploitable |
| Using latest without checking | Pin to tested versions in CI | Latest may introduce regressions |

---

# SECRETS-DETECTION Mode

Detect API keys, tokens, credentials, and sensitive data in code.

## What Counts as a Secret

| Category | Examples | Risk |
|----------|----------|------|
| **API Keys** | AWS access keys, Stripe keys, SendGrid API keys | Financial loss, service abuse |
| **Authentication Tokens** | JWT secrets, session secrets, OAuth client secrets | Account takeover |
| **Credentials** | Database passwords, SSH keys, certificates | System compromise |
| **Private Keys** | RSA/EC private keys, signing keys | Identity forgery |
| **Config Files** | .env with production values, config with secrets | Lateral movement |
| **Tokens** | GitHub tokens, Slack tokens, Twilio tokens | Service abuse, data exfiltration |

## Detection Patterns

### High-Confidence Patterns

```
# AWS credentials
AKIA[0-9A-Z]{16}
aws_secret_access_key|w.aws_access_key_id
xox[baprs]-[0-9a-zA-Z]{10,48}

# API keys
sk_live_[0-9a-zA-Z]{24,}
AIza[0-9A-Za-z_-]{35}
SG\.[0-9A-Za-z_-]{22}\.[0-9A-Za-z_-]{43}
```

### Entropy Detection

Secrets have high entropy. Flag strings where:
- Length > 20 characters
- Contains mixed case, numbers, special characters
- Matches no common word patterns
- Assigned to variables named `key`, `token`, `secret`, `password`, `credential`

## Decision Criteria

| Situation | Action |
|-----------|--------|
| After commit to main | Alert immediately, rotate keys |
| During code review | Flag before merge, block if critical |
| Scanning entire repo | Prioritize by secret type and environment |
| Found in PR | Comment inline, require rebase with secret removal |

## Remediation Workflow

1. **Immediate** — Rotate the exposed secret (it is compromised)
2. **Revoke** — Invalidate the exposed credential in the service
3. **Clean** — Remove secret from git history (git filter-repo or BFG)
4. **Prevent** — Add pre-commit hook, update detection patterns

## Anti-Patterns with Consequences

| Wrong | Right | Consequence |
|-------|-------|-------------|
| `.env` in version control | `.env` in .gitignore, .env.example committed | Full secret exposure on push |
| Reverting to remove secret | Rotating secret + history rewrite | Old commit still exposes credential |
| Commenting out secrets | Moving secrets to environment or secrets manager | Commented secrets often still searchable |
| Using secrets in tests | Using test fixtures or mock credentials | Real credentials appear in test output |

---

# COMPLIANCE Mode

Verify adherence to security standards and compliance frameworks.

## Supported Frameworks

| Framework | Focus Areas | Key Requirements |
|-----------|------------|------------------|
| **OWASP ASVS** | Application security | 14 requirement categories, 3 assurance levels |
| **GDPR** | Data privacy | Consent, right to erasure, breach notification |
| **SOC2** | Service organization controls | Security, availability, confidentiality |
| **PCI-DSS** | Payment card data | Secure transmission, access control, testing |
| **HIPAA** | Healthcare data | PHI protection, access controls, audit trails |

## Decision Criteria

| Situation | Action |
|-----------|--------|
| Pre-audit preparation | Map requirements to implementation, identify gaps |
| Security review for compliance | Score against framework, prioritize gaps |
| New feature compliance | Verify feature meets applicable requirements |
| Third-party vendor review | Assess against security questionnaire |

## Compliance Assessment Process

1. **Scope Definition** — Identify applicable frameworks and requirements
2. **Evidence Collection** — Gather implementation evidence (code, configs, logs)
3. **Gap Analysis** — Map evidence to requirements, identify missing controls
4. **Risk Assessment** — Evaluate gaps by likelihood and impact
5. **Remediation Planning** — Prioritize fixes, assign owners, set timelines

## Key Compliance Areas

### Access Control (OWASP A01, SOC2 CC6)

- [ ] Authentication enforced on all sensitive endpoints
- [ ] Authorization checked server-side, not just client-side
- [ ] Session management with appropriate timeout and rotation
- [ ] Principle of least privilege applied

### Data Protection (GDPR, PCI-DSS)

- [ ] Sensitive data encrypted at rest and in transit
- [ ] No sensitive data in logs or error messages
- [ ] Data retention policies implemented
- [ ] Right to erasure implemented

### Security Configuration (OWASP A05)

- [ ] Default credentials changed
- [ ] Debug mode disabled in production
- [ ] Error messages don't expose stack traces
- [ ] Security headers configured (CSP, HSTS, X-Frame-Options)

### Logging and Monitoring (OWASP A09)

- [ ] Authentication events logged
- [ ] Authorization failures logged
- [ ] Logs protected from tampering
- [ ] Alerts configured for suspicious activity

## Anti-Patterns with Consequences

| Wrong | Right | Consequence |
|-------|-------|-------------|
| Self-certifying compliance | Independent audit verification | False sense of security, audit failures |
| Checking only new code | Continuous compliance monitoring | Legacy code accumulates compliance debt |
| Paper compliance (docs only) | Evidence-based verification | Gap between policy and implementation |
| One-time audit | Ongoing compliance monitoring | New code introduces new gaps |

---

## Mode Relationships

| Mode | Depends On | Informs |
|------|------------|--------|
| SAST | None | Code patterns for COMPLIANCE |
| DEPENDENCY-AUDIT | None | Vulnerability data for COMPLIANCE |
| SECRETS-DETECTION | None | Credential hygiene for COMPLIANCE |
| COMPLIANCE | SAST, DEPENDENCY-AUDIT, SECRETS-DETECTION | Overall security posture |

---

## Failure Signal

```json
{"status": "failed" | "success", "reason": "...", "completed_portion": "...", "retry_possible": true/false}
```

| status | reason | retry_possible |
|--------|--------|----------------|
| `failed` | `sast-inconclusive` | `false` |
| `failed` | `dependency-scan-error` | `true` |
| `failed` | `secrets-found-critical` | `false` |
| `failed` | `compliance-scope-unclear` | `true` |
| `failed` | `no-evidence-collected` | `false` |