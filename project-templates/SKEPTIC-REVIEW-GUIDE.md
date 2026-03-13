# Senior Dev Skeptic Review Guide

> **Purpose**: This guide defines when, how, and what to review during skeptic security reviews. It provides specific prompts and checklists to ensure consistent, thorough coverage.

---

## When to Invoke Skeptic Review

### Automatic Triggers

| Trigger | Review Type | Timing |
|---------|-------------|--------|
| High-risk classification | Design + Implementation | After spec approval, after Phase N completion |
| Medium-risk classification | Implementation | After security-critical phases |
| Spec mentions: encrypt, auth, credential, secret | Design | Before implementation begins |
| Phase gate failure | Targeted | Immediate |
| SECURITY-TODO accumulation (>3) | Targeted | Before next phase |

### Manual Triggers
- Developer requests review
- Unusual architecture decision
- Third-party security component integration
- Pre-release/pre-production checkpoint

---

## Review Types

### Design Review (After Spec, Before Implementation)

**Goal**: Validate that the security design addresses the threat model adequately.

**Inputs Required**:
- spec.md with Section 7 (Security Properties & Verification)
- Threat model with countermeasures
- Proposed verification criteria

**Review Prompts**:

1. **Threat Coverage**
   - "For each identified threat, is the countermeasure actually sufficient?"
   - "What threats are missing from this model?"
   - "Are there any 'assumes trusted' statements that might be wrong?"

2. **Verification Adequacy**
   - "For each countermeasure, does the verification test the *property* or just the *function*?"
   - "Could these tests pass while the security property is violated?"
   - "What manual verification steps are needed that tests can't cover?"

3. **Architecture Red Flags**
   - "Where does sensitive data flow? Is it protected at each point?"
   - "What happens if [component X] is compromised?"
   - "Are there any single points of failure for security?"

4. **Scope Concerns**
   - "Are the security non-goals actually acceptable?"
   - "What's explicitly out of scope that might bite us later?"

**Design Review Checklist**:
- [ ] All high-impact threats have countermeasures
- [ ] Countermeasures are technically feasible
- [ ] Verification criteria test properties, not just functions
- [ ] No obvious gaps between spec claims and verification
- [ ] Risk acceptances are documented and reasonable
- [ ] Security non-goals are explicitly stated

---

### Implementation Review (After Security-Critical Phases)

**Goal**: Verify that implemented code actually provides the documented security properties.

**Inputs Required**:
- Source code for security-critical components
- Security test suite
- Spec.md threat model and verification criteria
- Any SECURITY-TODO comments

**Review Methodology**:

#### Phase 1: Claim vs. Reality Audit

For each security claim in the spec, verify it's actually true:

| Spec Claim | How to Verify | Status |
|------------|---------------|--------|
| "Data encrypted at rest with AES-256-GCM" | Inspect raw storage files, check encryption calls | [ ] Verified / [ ] Gap found |
| "Passwords never stored, only derived keys" | Grep for password persistence, check all storage paths | [ ] Verified / [ ] Gap found |
| "Rate limiting on auth endpoint" | Check endpoint code, look for limiting middleware | [ ] Verified / [ ] Gap found |
| "Parameterized queries only" | Grep for string interpolation in SQL | [ ] Verified / [ ] Gap found |

#### Phase 2: Common Vulnerability Scan

Check for these specific issues regardless of threat model:

**Authentication & Authorization**:
- [ ] No hardcoded credentials in source
- [ ] Passwords use secure comparison (timing-safe)
- [ ] Session tokens have sufficient entropy
- [ ] Failed auth doesn't leak information (user exists vs. wrong password)
- [ ] Rate limiting prevents brute force

**Data Protection**:
- [ ] Sensitive data encrypted at rest (actually, not just "encrypt function exists")
- [ ] Sensitive data encrypted in transit
- [ ] No sensitive data in logs
- [ ] No sensitive data in error messages
- [ ] Secure deletion when required

**Input Handling**:
- [ ] No SQL injection (parameterized queries only)
- [ ] No command injection (no shell=True with user input)
- [ ] No path traversal (validate file paths)
- [ ] Input validation on all user-provided data

**Cryptography**:
- [ ] Using established libraries (not custom crypto)
- [ ] Appropriate algorithms (not MD5/SHA1 for security)
- [ ] Proper key management (keys not hardcoded)
- [ ] Secure random number generation

**Error Handling**:
- [ ] Errors don't leak sensitive information
- [ ] Failed operations don't leave partial/insecure state
- [ ] Exceptions are caught and handled securely

#### Phase 3: SECURITY-TODO Audit

For each SECURITY-TODO in codebase:
- [ ] Is this a real security issue or just a note?
- [ ] What's the actual risk if not addressed?
- [ ] Is there a plan to resolve before release?
- [ ] Should this block the phase gate?

#### Phase 4: Test Quality Assessment

For each security test:
- [ ] Does it test the security *property* or just the *function*?
- [ ] Could this test pass while the vulnerability exists?
- [ ] Does it test the right thing (actual stored data, not just API response)?
- [ ] Are edge cases covered?

---

### Review Output Format

```markdown
# Skeptic Review: [Project Name] - [Phase/Scope]

**Reviewer**: senior-dev-skeptic
**Date**: [Date]
**Review Type**: [Design / Implementation / Targeted]
**Classification**: [High / Medium / Low risk]

## Executive Summary
[2-3 sentences: Overall assessment and key concerns]

## Findings

### Critical (Must fix before proceeding)

#### [CRIT-001]: [Title]
- **Location**: [File:line or spec section]
- **Issue**: [Description of the problem]
- **Risk**: [What could happen if exploited]
- **Evidence**: [Code snippet, test result, or observation]
- **Recommendation**: [How to fix]

### High (Should fix before proceeding)

#### [HIGH-001]: [Title]
[Same format as critical]

### Medium (Fix before release)

#### [MED-001]: [Title]
[Same format]

### Low (Consider fixing)

#### [LOW-001]: [Title]
[Same format]

### Observations (Not findings, but worth noting)
- [Observation 1]
- [Observation 2]

## Verification Checklist Results

| Spec Claim | Status | Notes |
|------------|--------|-------|
| [Claim 1] | Pass/Fail/Partial | [Details] |
| [Claim 2] | Pass/Fail/Partial | [Details] |

## SECURITY-TODO Audit

| Location | Description | Risk | Recommendation |
|----------|-------------|------|----------------|
| [file:line] | [TODO text] | [Risk level] | [Block/Track/Accept] |

## Test Quality Assessment

| Test Category | Coverage | Quality | Issues |
|---------------|----------|---------|--------|
| Data at rest | [%] | [Good/Fair/Poor] | [Issues] |
| Authentication | [%] | [Good/Fair/Poor] | [Issues] |
| Injection | [%] | [Good/Fair/Poor] | [Issues] |

## Recommendations

1. [Recommendation 1]
2. [Recommendation 2]

## Gate Decision

- [ ] **PASS**: No critical/high issues. May proceed.
- [ ] **CONDITIONAL PASS**: May proceed after addressing: [list]
- [ ] **FAIL**: Must address critical issues before proceeding: [list]

## Sign-off

Reviewed by: [Name/Agent]
Date: [Date]
Next review: [If applicable]
```

---

## Skeptic Review Prompts for AI Agents

When invoking senior-dev-skeptic agent, use this prompt structure:

```markdown
## Review Request

**Project**: [Name]
**Phase**: [Phase being reviewed]
**Risk Level**: [High/Medium/Low]
**Review Type**: [Design/Implementation/Targeted]

## Context
[Brief description of what's being built and its security requirements]

## Specific Review Focus
[What aspects need particular attention]

## Materials to Review
1. Spec: [path or content]
2. Source files: [paths]
3. Test files: [paths]
4. Previous findings: [if any]

## Key Questions
1. Does the implementation match the security claims in the spec?
2. Are there gaps between "documented" and "actually implemented"?
3. What vulnerabilities exist that the tests don't catch?
4. Are there any "trust assumptions" that could be violated?

## Expected Output
Please provide findings in the standard Skeptic Review format with:
- Severity-ranked findings
- Evidence for each finding
- Specific recommendations
- Gate decision (Pass/Conditional/Fail)
```

---

## Integration Points

### In plan.md
```markdown
### Phase 3 Completion

**Skeptic Review Checkpoint**
- [ ] Review materials prepared (spec, source, tests)
- [ ] Review request submitted
- [ ] Findings documented in spec.md Section 7 (Skeptic Review)
- [ ] Critical findings resolved
- [ ] High findings resolved or risk-accepted
- [ ] Gate decision: [Pass/Conditional/Fail]
```

### In CI/CD
```yaml
# .github/workflows/security-gate.yml
security-review-check:
  if: contains(github.event.pull_request.labels.*.name, 'security-critical')
  steps:
    - name: Check skeptic review status
      run: |
        # Verify skeptic review section exists and shows PASS
        grep -A5 "## Gate Decision" spec.md | grep -q "PASS" || exit 1
```

### In spec.md
Reference the guide:
```markdown
### Skeptic Review Schedule

| Review | Timing | Status |
|--------|--------|--------|
| Design Review | After spec approval | [ ] Scheduled / [ ] Complete |
| Phase 3 Implementation | After Phase 3 | [ ] Scheduled / [ ] Complete |
| Pre-release | Before v1.0 | [ ] Scheduled / [ ] Complete |

See: SKEPTIC-REVIEW-GUIDE.md for review process and prompts.
```
