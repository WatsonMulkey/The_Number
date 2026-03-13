# Project Security Risk Classification Checklist

> **Purpose**: Use this checklist at project inception to determine security classification and required process rigor.

---

## Step 1: Automatic Keyword Detection

Scan the project description, requirements, and spec for these trigger keywords:

### High-Risk Triggers (any one = potentially High risk)
- [ ] "password" / "credential" / "secret" / "API key"
- [ ] "encrypt" / "decrypt" / "cryptographic"
- [ ] "authentication" / "authorization" / "auth"
- [ ] "PII" / "personal data" / "GDPR" / "HIPAA" / "SOC2"
- [ ] "payment" / "financial" / "credit card" / "PCI"
- [ ] "confidential" / "proprietary" / "trade secret"
- [ ] "medical" / "health" / "patient"
- [ ] "multi-tenant" / "user isolation"

### Medium-Risk Triggers (multiple = potentially Medium risk)
- [ ] "user data" / "user information"
- [ ] "login" / "session" / "token"
- [ ] "database" / "storage" / "persistence"
- [ ] "API" / "endpoint" / "webhook"
- [ ] "file upload" / "user input"
- [ ] "admin" / "privileged" / "role"

### Low-Risk Indicators
- [ ] Internal tooling only
- [ ] No user data handled
- [ ] No authentication required
- [ ] No persistence of sensitive data
- [ ] Development/testing utilities

---

## Step 2: Context Assessment

Answer these questions to refine classification:

### Data Sensitivity
| Question | Answer |
|----------|--------|
| What is the most sensitive data this system handles? | [Description] |
| Who would be harmed if this data leaked? | [ ] No one / [ ] Organization / [ ] Users / [ ] Public |
| Is there regulatory/compliance exposure? | [ ] No / [ ] Yes: _______ |

### Attack Surface
| Question | Answer |
|----------|--------|
| Is this exposed to the internet? | [ ] No / [ ] Yes |
| Does it accept untrusted user input? | [ ] No / [ ] Yes |
| Does it integrate with external systems? | [ ] No / [ ] Yes |
| Will it be deployed to production? | [ ] No / [ ] Yes |

### Impact Assessment
| Question | Answer |
|----------|--------|
| What's the worst-case breach scenario? | [Description] |
| Could a vulnerability affect other systems? | [ ] No / [ ] Yes |
| Is there reputational risk? | [ ] Low / [ ] Medium / [ ] High |

---

## Step 3: Classification Decision

Based on Steps 1 and 2, select classification:

### High Risk
Select if ANY of:
- Handles credentials, secrets, or encryption keys
- Processes PII or regulated data (HIPAA, PCI, GDPR)
- Internet-exposed authentication system
- Financial transactions or payment data
- Multi-tenant with data isolation requirements
- Worst-case breach = significant harm to users

**Required Process:**
- [ ] Full threat model in spec.md (Section 7.2)
- [ ] Security tests specified before implementation
- [ ] Skeptic review at design phase
- [ ] Skeptic review at implementation phase
- [ ] Phase gates with security verification
- [ ] SECURITY-TODO blocking in CI
- [ ] All threats must have verification criteria
- [ ] Risk acceptance requires documented approval

### Medium Risk
Select if:
- Handles user data but not credentials
- Internal system with authentication
- Accepts user input that's persisted
- No regulatory requirements
- Worst-case breach = moderate impact

**Required Process:**
- [ ] Abbreviated threat model (top 3-5 threats)
- [ ] Security tests for identified threats
- [ ] Skeptic review at implementation phase (design optional)
- [ ] Final phase gate with security verification
- [ ] SECURITY-TODO blocking in CI

### Low Risk
Select if ALL of:
- No sensitive data handled
- No authentication
- Internal/development use only
- No user-facing input
- Worst-case = minimal impact

**Required Process:**
- [ ] Standard development process
- [ ] Basic input validation
- [ ] Optional: quick skeptic review if desired

---

## Step 4: Document Classification

Add this to the project's requirements.md or spec.md:

```markdown
## Security Classification

| Attribute | Value |
|-----------|-------|
| **Risk Level** | [Low / Medium / High] |
| **Classification Date** | [Date] |
| **Classified By** | [Name/Role] |
| **Trigger Keywords Found** | [List keywords that triggered review] |
| **Primary Risk Factors** | [Brief description] |

### Required Security Process
- [ ] Threat model: [Not required / Abbreviated / Full]
- [ ] Security tests: [Standard / Required for threats / Required before implementation]
- [ ] Skeptic reviews: [None / Implementation only / Design + Implementation]
- [ ] Phase gates: [Standard / Security-enhanced]
- [ ] SECURITY-TODO enforcement: [Warning / Blocking]

### Classification Rationale
[1-2 sentences explaining why this classification was chosen]
```

---

## Step 5: Review Triggers

Re-evaluate classification if any of these occur during development:

- [ ] Scope changes to include authentication
- [ ] New requirement involves sensitive data
- [ ] Integration added with external system
- [ ] Deployment target changes (internal → production)
- [ ] Compliance requirement discovered
- [ ] Skeptic review identifies unexpected risks

---

## Quick Reference Card

```
┌─────────────────────────────────────────────────────────────────┐
│                 SECURITY CLASSIFICATION QUICK REF               │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  HIGH RISK (any trigger)           REQUIRED PROCESS             │
│  ├─ Credentials/secrets            ├─ Full threat model         │
│  ├─ PII/regulated data             ├─ Security tests first      │
│  ├─ Payment/financial              ├─ Skeptic: design + impl    │
│  ├─ Internet-exposed auth          ├─ Phase gates               │
│  └─ Multi-tenant                   └─ SECURITY-TODO blocks CI   │
│                                                                 │
│  MEDIUM RISK (multiple triggers)   REQUIRED PROCESS             │
│  ├─ User data (not creds)          ├─ Top 5 threat model        │
│  ├─ Internal auth                  ├─ Security tests            │
│  ├─ Persisted user input           ├─ Skeptic: impl only        │
│  └─ No compliance                  └─ Final gate                │
│                                                                 │
│  LOW RISK (all conditions)         REQUIRED PROCESS             │
│  ├─ No sensitive data              ├─ Standard process          │
│  ├─ No auth                        ├─ Basic validation          │
│  ├─ Internal only                  └─ Optional skeptic          │
│  └─ Minimal impact                                              │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```
