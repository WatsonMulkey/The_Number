# Security-Enhanced Plan Template

> **Purpose**: This template shows how to integrate security verification into plan.md implementation steps. Each step that has security implications includes explicit security verification checkboxes.

---

## Plan.md Security Integration Pattern

### Standard Step Format (Non-Security)

```markdown
### Step 3.1: Implement Data Model

**Tasks:**
- [ ] Create SQLAlchemy models for documents
- [ ] Add migration scripts
- [ ] Implement CRUD operations

**Verification:**
```bash
uv run pytest tests/unit/test_models.py -v
uv run mypy src/models/ --strict
```

**Exit Criteria:**
- [ ] All tests pass
- [ ] Type checking clean
```

---

### Security-Enhanced Step Format

> Use this format for any step that implements security-relevant functionality.

```markdown
### Step 3.2: Implement Encrypted Storage [SECURITY]

> **Security Tag**: This step implements countermeasures for Threat 1 (Data at Rest Exposure)

**Tasks:**
- [ ] Implement encryption service using AES-256-GCM
- [ ] Integrate encryption with document storage
- [ ] Ensure vector store uses encryption layer
- [ ] Add key derivation from master password

**Functional Verification:**
```bash
uv run pytest tests/unit/test_encryption.py -v
uv run mypy src/encryption/ --strict
```

**Security Verification:**
```bash
# Run security-specific tests for this step
uv run pytest tests/test_security/test_data_at_rest.py -v

# Verify no SECURITY-TODO added
grep -r "SECURITY-TODO" src/encryption/ src/storage/ && exit 1 || echo "OK"
```

**Security Checklist:**
- [ ] Database file is binary garbage without correct password (manually verify)
- [ ] Vector store files are encrypted (manually verify with `hexdump`)
- [ ] No plaintext sensitive data in any persisted file
- [ ] Encryption keys are not logged or persisted
- [ ] All security tests for Threat 1 pass

**Exit Criteria:**
- [ ] Functional tests pass
- [ ] Security tests pass
- [ ] Security checklist complete
- [ ] No new SECURITY-TODO comments
```

---

## Phase Gate Template

> Add this at the end of each phase that contains security-relevant steps.

```markdown
## Phase 3 Security Gate

**Security Steps in This Phase:**
- Step 3.2: Encrypted Storage [SECURITY]
- Step 3.4: Secure Key Management [SECURITY]

**Gate Requirements:**

### Automated Checks
```bash
# All security tests pass
uv run pytest tests/test_security/ -v --tb=long

# No SECURITY-TODO in codebase
! grep -r "SECURITY-TODO\|# TODO:.*\[SECURITY\]" src/

# Static analysis clean
uv run bandit -r src/ -ll
```

### Manual Verification
- [ ] Reviewed: Data at rest is actually encrypted (inspected raw files)
- [ ] Reviewed: No sensitive data in logs (checked log output)
- [ ] Reviewed: Authentication cannot be bypassed (tested edge cases)

### Threat Coverage
- [ ] Threat 1 (Data at Rest): All verification criteria pass
- [ ] Threat 2 (Credential Theft): All verification criteria pass
- [ ] Threat 3 (Auth Bypass): All verification criteria pass

### Skeptic Review (if required)
- [ ] Design review complete (for Medium/High risk)
- [ ] Implementation review scheduled or complete
- [ ] All critical findings resolved
- [ ] All high findings resolved or risk-accepted

**Phase Sign-off:**
- [ ] All automated checks pass
- [ ] All manual verification complete
- [ ] Threat coverage confirmed
- [ ] Skeptic review requirements met
- [ ] Ready to proceed to Phase 4
```

---

## Example: Complete Phase with Security Integration

```markdown
# Phase 3: Secure Data Management

## Step 3.1: Database Schema Design

**Tasks:**
- [ ] Design schema for documents, chunks, metadata
- [ ] Create migration scripts
- [ ] Document schema decisions

**Verification:**
```bash
uv run pytest tests/unit/test_schema.py -v
```

**Exit Criteria:**
- [ ] Schema documented
- [ ] Migrations work forward and backward

---

## Step 3.2: Implement Encrypted Storage [SECURITY]

> **Threat Coverage**: Threat 1 (Data at Rest Exposure)

**Tasks:**
- [ ] Implement AES-256-GCM encryption service
- [ ] Create encrypted file wrapper
- [ ] Integrate with SQLite (SQLCipher or application-level)
- [ ] Integrate with vector store

**Functional Verification:**
```bash
uv run pytest tests/unit/test_encryption.py -v
uv run pytest tests/unit/test_storage.py -v
```

**Security Verification:**
```bash
uv run pytest tests/test_security/test_data_at_rest.py -v
```

**Security Checklist:**
- [ ] `test_database_unreadable_without_key` passes
- [ ] `test_vector_store_encrypted` passes
- [ ] `test_no_sensitive_data_in_logs` passes
- [ ] Manually verified: `hexdump vault.db | head` shows encrypted data
- [ ] Manually verified: `strings vault.db | grep -i password` returns nothing

**Exit Criteria:**
- [ ] Functional tests pass
- [ ] Security tests pass
- [ ] Security checklist complete

---

## Step 3.3: Implement Document CRUD

**Tasks:**
- [ ] Create document service
- [ ] Implement add/get/update/delete operations
- [ ] Add chunking for vector storage

**Verification:**
```bash
uv run pytest tests/unit/test_document_service.py -v
```

**Exit Criteria:**
- [ ] All CRUD operations work
- [ ] Chunking produces correct output

---

## Step 3.4: Secure Key Management [SECURITY]

> **Threat Coverage**: Threat 2 (Credential Theft)

**Tasks:**
- [ ] Implement key derivation (Argon2id)
- [ ] Create secure key storage (OS keyring integration)
- [ ] Implement key rotation capability
- [ ] Add secure key destruction

**Functional Verification:**
```bash
uv run pytest tests/unit/test_key_management.py -v
```

**Security Verification:**
```bash
uv run pytest tests/test_security/test_credential_handling.py -v
```

**Security Checklist:**
- [ ] `test_password_not_persisted` passes
- [ ] `test_keys_cleared_on_lock` passes (with documented limitations)
- [ ] `test_key_derivation_timing` shows consistent time (no timing leak)
- [ ] Reviewed: No keys in logs, config files, or environment dumps

**Known Limitations:**
- Python immutable bytes prevent guaranteed memory clearing
- Documented in spec.md Section 7.5 with risk acceptance

**Exit Criteria:**
- [ ] Functional tests pass
- [ ] Security tests pass
- [ ] Limitations documented and accepted

---

## Phase 3 Security Gate

[Use gate template from above]
```

---

## SECURITY-TODO Convention

### When to Use

Use `# SECURITY-TODO:` (not regular `# TODO:`) when:
- Implementing a temporary workaround for a security feature
- Noting a security improvement needed before production
- Marking code that needs security review

### Format

```python
# SECURITY-TODO: [Brief description] - [Ticket/Issue reference if any]
# Risk: [What could go wrong if not addressed]
# Deadline: [When this must be resolved - e.g., "Before Phase 4", "Before production"]
```

### Examples

```python
# SECURITY-TODO: Implement rate limiting on auth endpoint
# Risk: Brute force attacks possible without this
# Deadline: Before Phase 4 gate

def authenticate(password: str) -> bool:
    # Currently no rate limiting
    return verify_password(password)
```

```python
# SECURITY-TODO: Replace string interpolation with parameterized query
# Risk: SQL injection vulnerability
# Deadline: Before any PR review

def get_document(doc_id: str) -> Document:
    # INSECURE - temporary for testing
    query = f"SELECT * FROM documents WHERE id = '{doc_id}'"  # SECURITY-TODO
    ...
```

### Enforcement

Add to CI/CD:
```bash
#!/bin/bash
# security-todo-check.sh

SECURITY_TODOS=$(grep -rn "SECURITY-TODO" src/ tests/ || true)

if [ -n "$SECURITY_TODOS" ]; then
    echo "ERROR: Unresolved SECURITY-TODO comments found:"
    echo "$SECURITY_TODOS"
    echo ""
    echo "These must be resolved before merge. Options:"
    echo "  1. Implement the security fix"
    echo "  2. Convert to risk acceptance in spec.md Section 7.5"
    exit 1
fi

echo "OK: No SECURITY-TODO comments found"
```

### Lifecycle

1. **Created**: When implementing, if security shortcut taken
2. **Tracked**: Must reference in spec.md or issue tracker
3. **Resolved**: Either fixed or converted to documented risk acceptance
4. **Never**: Merged to main with SECURITY-TODO present
