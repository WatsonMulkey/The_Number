# Security Properties & Verification Template

> **Purpose**: This template section should be added to spec.md for any project classified as security-sensitive. It ensures security requirements are captured as *verifiable properties*, not just *features to implement*.

---

## 7. Security Properties & Verification

> Add this as Section 7 (or appropriate number) in your spec.md

### 7.1 Security Classification

| Attribute | Value |
|-----------|-------|
| **Risk Level** | [ ] Low / [ ] Medium / [ ] High |
| **Classification Trigger** | [What keyword/concept triggered security review - e.g., "handles confidential documents"] |
| **Data Sensitivity** | [What sensitive data is handled - e.g., "user credentials, proprietary documents"] |
| **Compliance Requirements** | [Any regulatory requirements - e.g., "none", "SOC2", "HIPAA"] |
| **Skeptic Review Required** | [ ] Design phase / [ ] Implementation phase / [ ] Both |

### 7.2 Threat Model

> For each identified threat, document: what could go wrong, what countermeasure addresses it, and how we verify the countermeasure actually works.

#### Threat 1: [Name - e.g., "Data at Rest Exposure"]

| Attribute | Description |
|-----------|-------------|
| **Threat Description** | [What could go wrong - e.g., "Attacker gains filesystem access and reads stored documents"] |
| **Threat Actor** | [Who would exploit this - e.g., "Malicious insider, compromised server"] |
| **Impact** | [ ] Low / [ ] Medium / [ ] High / [ ] Critical |
| **Likelihood** | [ ] Low / [ ] Medium / [ ] High |

**Countermeasure:**
- [Specific technical countermeasure - e.g., "All stored data encrypted with AES-256-GCM using per-vault keys"]

**Verification Criteria (MUST be testable):**
- [ ] Property: [What must be true - e.g., "Database file is unreadable without correct password"]
  - Test: `test_security/test_data_at_rest.py::test_database_unreadable_without_key`
- [ ] Property: [e.g., "Vector store chunks are encrypted on disk, not plaintext"]
  - Test: `test_security/test_data_at_rest.py::test_vector_store_encrypted`
- [ ] Property: [e.g., "No sensitive data appears in application logs"]
  - Test: `test_security/test_data_at_rest.py::test_no_sensitive_data_in_logs`

---

#### Threat 2: [Name - e.g., "Credential Theft"]

| Attribute | Description |
|-----------|-------------|
| **Threat Description** | [e.g., "Attacker extracts master password or encryption keys from memory/disk"] |
| **Threat Actor** | [e.g., "Memory dump attack, cold boot attack"] |
| **Impact** | [ ] Low / [ ] Medium / [ ] High / [ ] Critical |
| **Likelihood** | [ ] Low / [ ] Medium / [ ] High |

**Countermeasure:**
- [e.g., "Keys derived at runtime, never stored. Memory cleared after use where possible."]

**Verification Criteria:**
- [ ] Property: [e.g., "Master password is never written to disk"]
  - Test: `test_security/test_credential_handling.py::test_password_not_persisted`
- [ ] Property: [e.g., "Encryption keys are not present in memory after vault lock"]
  - Test: `test_security/test_credential_handling.py::test_keys_cleared_on_lock`
  - Note: [Document known limitations - e.g., "Python immutable bytes limitation - document risk acceptance"]

---

#### Threat 3: [Name - e.g., "Authentication Bypass"]

| Attribute | Description |
|-----------|-------------|
| **Threat Description** | [e.g., "Attacker brute-forces password or bypasses authentication"] |
| **Threat Actor** | [e.g., "External attacker with access to application"] |
| **Impact** | [ ] Low / [ ] Medium / [ ] High / [ ] Critical |
| **Likelihood** | [ ] Low / [ ] Medium / [ ] High |

**Countermeasure:**
- [e.g., "Rate limiting on auth attempts, account lockout after N failures, timing-safe comparison"]

**Verification Criteria:**
- [ ] Property: [e.g., "Cannot attempt more than 5 passwords per minute"]
  - Test: `test_security/test_auth.py::test_rate_limiting`
- [ ] Property: [e.g., "Account locks after 10 failed attempts"]
  - Test: `test_security/test_auth.py::test_lockout`
- [ ] Property: [e.g., "Password comparison is timing-safe"]
  - Test: `test_security/test_auth.py::test_timing_safe_comparison`

---

#### Threat 4: [Name - e.g., "Injection Attacks"]

| Attribute | Description |
|-----------|-------------|
| **Threat Description** | [e.g., "Attacker injects malicious SQL/commands via user input"] |
| **Threat Actor** | [e.g., "External attacker providing malicious input"] |
| **Impact** | [ ] Low / [ ] Medium / [ ] High / [ ] Critical |
| **Likelihood** | [ ] Low / [ ] Medium / [ ] High |

**Countermeasure:**
- [e.g., "All database queries use parameterized statements, never string interpolation"]

**Verification Criteria:**
- [ ] Property: [e.g., "SQL injection attempts are safely handled"]
  - Test: `test_security/test_injection.py::test_sql_injection_prevented`
- [ ] Property: [e.g., "No string interpolation in any database query"]
  - Test: `Static analysis - grep for f-string/format in query construction`

---

> Copy the threat template above for additional threats. Common threats to consider:
> - Data at rest exposure
> - Data in transit exposure
> - Credential theft/exposure
> - Authentication bypass
> - Authorization bypass
> - Injection attacks (SQL, command, XSS)
> - Denial of service
> - Information disclosure (logs, errors, timing)
> - Supply chain (dependencies)

### 7.3 Security Test Requirements

> These tests MUST exist and pass before the project is considered complete.

```
tests/
  test_security/
    test_data_at_rest.py      # Threat 1 verification
    test_credential_handling.py # Threat 2 verification
    test_auth.py              # Threat 3 verification
    test_injection.py         # Threat 4 verification
    conftest.py              # Security test fixtures
```

**Security Test Principles:**
1. Tests verify *properties*, not just *functions*
   - BAD: `test_encrypt_returns_bytes()` - tests function works
   - GOOD: `test_database_file_unreadable_without_key()` - tests property holds
2. Tests should attempt to break security, not just use happy path
3. Tests should verify the *actual stored data*, not just the API response

### 7.4 Security Verification Commands

> Add to CI/CD pipeline and run before each phase completion.

```bash
# Run all security tests
uv run pytest tests/test_security/ -v --tb=long

# Check for SECURITY-TODO comments (must be zero)
grep -r "SECURITY-TODO\|# TODO:.*\[SECURITY\]" src/ && echo "FAIL: Unresolved security TODOs" && exit 1

# Check for dangerous patterns (customize per project)
grep -rn "f\".*SELECT\|f\".*INSERT\|f\".*UPDATE\|f\".*DELETE" src/ && echo "WARN: Possible SQL injection"
grep -rn "password.*=.*\"[^\"]\+\"\|secret.*=.*\"[^\"]\+\"" src/ && echo "WARN: Possible hardcoded credential"

# Static security analysis (if using bandit)
uv run bandit -r src/ -ll
```

### 7.5 Known Limitations & Risk Acceptance

> Document security limitations that cannot be fully addressed, with explicit risk acceptance.

| Limitation | Reason | Risk Level | Accepted By | Date |
|------------|--------|------------|-------------|------|
| [e.g., "Python immutable bytes prevent reliable memory clearing"] | [Technical limitation of language] | Medium | [Name/Role] | [Date] |
| [e.g., "Rate limiting is per-process, not distributed"] | [MVP scope - will address in v2] | Low | [Name/Role] | [Date] |

---

## Skeptic Review Sections

> Add these sections to capture skeptic review findings. One section per review.

### Skeptic Review - [Phase Name] ([Date])

**Reviewer:** [Name or "senior-dev-skeptic agent"]

**Review Scope:** [What was reviewed - e.g., "Encryption implementation, key management"]

**Findings:**

| ID | Finding | Severity | Status | Resolution |
|----|---------|----------|--------|------------|
| SR-001 | [e.g., "Vector store data stored in plaintext despite spec claiming encryption"] | Critical | [ ] Open / [ ] Resolved / [ ] Risk-Accepted | [How resolved or why accepted] |
| SR-002 | [e.g., "Rate limiting not implemented on auth endpoint"] | High | [ ] Open / [ ] Resolved / [ ] Risk-Accepted | [Resolution] |
| SR-003 | [e.g., "SQL queries use string interpolation"] | High | [ ] Open / [ ] Resolved / [ ] Risk-Accepted | [Resolution] |

**Blocking Issues:** [List any findings that block phase completion]

**Recommendations:** [Additional suggestions not captured as findings]

**Sign-off:** [ ] All critical/high findings resolved or risk-accepted. Phase may proceed.
