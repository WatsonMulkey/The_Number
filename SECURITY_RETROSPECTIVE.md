# Security Issues Retrospective

**Date:** 2025-12-15
**Context:** QA review identified 10 critical/major security issues in The Number app
**Outcome:** All issues fixed, 192/192 tests passing

---

## Executive Summary

A comprehensive QA review revealed 10 critical and major security vulnerabilities in The Number budgeting application. These issues ranged from SQL injection patterns to improper error handling. This retrospective analyzes why these issues occurred, what we learned, and how to prevent similar problems in the future.

---

## Issues Found and Fixed

### Critical Issues (3)

1. **SQL Injection Pattern in database.py**
   - Location: `update_expense()` method, line 220-221
   - Impact: Could allow attackers to manipulate database queries
   - Fix: Added whitelist validation for column names before f-string interpolation

2. **Negative Daily Limit Handling**
   - Location: `calculate_paycheck_mode()`, line 110
   - Impact: User confusion when expenses exceed income
   - Fix: Added deficit detection and `max(0, ...)` to prevent negative limits

3. **Division by Zero in Fixed Pool Mode**
   - Location: `calculate_fixed_pool_mode()`, line 148
   - Impact: App crash when user has $0
   - Fix: Added zero-money check with early return

### Major Issues (7)

4. **Input Sanitization Missing**
   - Location: Multiple files
   - Impact: Unbounded string lengths could cause issues
   - Fix: Added MAX_STRING_LENGTH (200 chars) validation

5. **Large Number Overflow**
   - Location: Expense and Transaction classes
   - Impact: Unrealistic amounts could break calculations
   - Fix: Added MAX_AMOUNT ($10M) validation

6. **File Path Validation Missing**
   - Location: import_expenses.py, export_expenses.py
   - Impact: Path traversal attacks possible
   - Fix: Added validate_file_path() with path traversal prevention

7. **Encryption Key Display**
   - Location: `_save_key_warning()`, line 48
   - Impact: Full key visible in console/logs
   - Fix: Masked key to show only first/last 4 characters

8. **Transaction Validation Missing**
   - Location: `add_transaction()`, line 262
   - Impact: Invalid data could enter database
   - Fix: Added positive amount check, description validation

9. **CSV Sniffer Error Handling**
   - Location: parse_csv_expenses(), line 79
   - Impact: App crash on malformed CSV
   - Fix: Wrapped sniffer in try/except with comma fallback

10. **Bare Except Clauses**
    - Location: Multiple files
    - Impact: Silent failures, hard to debug
    - Fix: Replaced with specific exception types

---

## Root Cause Analysis

### Why Did These Issues Occur?

#### 1. **Security-First Mindset Was Not Primary During Initial Development**

**What Happened:**
When building features like import/export and database operations, the focus was primarily on functionality ("does it work?") rather than security ("is it safe?").

**Evidence:**
- No input length limits were added initially
- File path validation was an afterthought
- f-strings were used with user data without considering injection risks

**Why This Happened:**
- Time pressure to deliver working features quickly
- Security review was planned for later (QA phase) rather than built-in from the start
- Developer assumed benign users rather than adversarial attackers

#### 2. **Insufficient Edge Case Testing During Development**

**What Happened:**
Code handled "happy path" scenarios well, but edge cases like zero money, negative budgets, and malformed input weren't tested until QA.

**Evidence:**
- Division by zero wasn't caught until QA
- Negative daily limits passed initial tests
- CSV sniffer failures weren't anticipated

**Why This Happened:**
- Test cases focused on typical user scenarios
- Edge case test coverage was incomplete
- Manual testing didn't simulate adversarial or extreme inputs

#### 3. **Copy-Paste Pattern Without Security Review**

**What Happened:**
Similar patterns were reused across files (import/export, exception handling) without reviewing each instance for security implications.

**Evidence:**
- Bare except clauses appeared in multiple files
- Path validation was missing in both import AND export
- Similar validation gaps across multiple functions

**Why This Happened:**
- DRY (Don't Repeat Yourself) applied to implementation but not security review
- Each file was treated as isolated rather than part of a cohesive security posture
- No checklist or standard validation template existed

#### 4. **Overly Broad Exception Handling**

**What Happened:**
Used `except Exception as e:` or bare `except:` to "be safe" and prevent crashes, but this masked problems and made debugging harder.

**Evidence:**
- Multiple bare except clauses found
- Generic Exception catches instead of specific errors
- No logging of caught exceptions in some cases

**Why This Happened:**
- Defensive programming mindset: "catch everything to prevent crashes"
- Didn't consider that silent failures are worse than loud crashes during development
- Lacked knowledge of specific exception types to catch

---

## What We Learned

### Key Insights

1. **Security Must Be Built In, Not Bolted On**
   - Waiting for QA to find security issues is too late
   - Each feature should have security requirements from day one
   - Code reviews should include security checklist items

2. **Input Validation is Not Optional**
   - Every user input is potentially malicious
   - Validation rules should be defined before implementation
   - Constants for limits (MAX_AMOUNT, MAX_STRING_LENGTH) should exist from the start

3. **Error Handling Should Be Specific**
   - Bare except clauses are code smells
   - Understanding what can go wrong is part of the design
   - Specific exceptions make debugging easier and safer

4. **Path Operations Need Special Care**
   - File paths are a common attack vector
   - Path traversal (../) must always be prevented
   - Consider sandboxing file operations to safe directories

5. **Display of Sensitive Data Requires Thought**
   - Encryption keys, passwords, tokens should never be fully displayed
   - Masking or truncation is standard practice
   - Consider whether data needs to be shown at all

---

## Prevention Strategies

### What We're Implementing Now

#### 1. **Security Checklist for New Features**

Before any PR is merged, verify:

- [ ] All user inputs have validation (type, length, range)
- [ ] SQL queries use parameterization, not string interpolation
- [ ] File paths are validated and sanitized
- [ ] Error handling uses specific exception types
- [ ] Sensitive data is masked or not displayed
- [ ] Constants exist for all limits (amounts, lengths, days)
- [ ] Edge cases are tested (zero, negative, max, min values)

#### 2. **Security-Focused Code Review Process**

Every code review must include:

1. **Threat Modeling**: "How could an attacker abuse this?"
2. **Input Analysis**: "What's the worst thing a user could input?"
3. **Error Path Review**: "What happens when this fails?"
4. **Data Flow Tracing**: "Where does user data go?"

#### 3. **Comprehensive Test Coverage Requirements**

For each feature, require tests for:

- **Happy path**: Normal, expected usage
- **Edge cases**: Zero, negative, maximum, minimum values
- **Error cases**: Invalid input, missing data, malformed data
- **Security cases**: SQL injection attempts, path traversal, XSS patterns

Example test cases we should have written initially:
```python
def test_update_expense_sql_injection_attempt():
    # Try to inject SQL via name parameter
    db.update_expense(1, name="'; DROP TABLE expenses; --")
    # Should raise ValueError, not execute SQL

def test_calculate_paycheck_mode_expenses_exceed_income():
    # Expenses > Income should handle gracefully
    result = calc.calculate_paycheck_mode(2000, 14)  # $3000 expenses
    assert result['is_deficit'] is True
    assert result['daily_limit'] == 0  # Not negative!

def test_parse_csv_path_traversal():
    # Try to read file outside allowed directory
    with pytest.raises(ValueError):
        parse_csv_expenses("../../etc/passwd")
```

#### 4. **Validation Library/Module**

Create `src/validation.py` with reusable validation functions:

```python
# Centralized validation reduces copy-paste errors
def validate_amount(amount: float, allow_zero: bool = False) -> float:
    """Validate monetary amount."""
    if not allow_zero and amount <= 0:
        raise ValueError("Amount must be positive")
    if amount > MAX_AMOUNT:
        raise ValueError(f"Amount exceeds maximum (${MAX_AMOUNT:,})")
    return amount

def validate_string(s: str, field_name: str, max_length: int = MAX_STRING_LENGTH) -> str:
    """Validate string input."""
    if not s or not s.strip():
        raise ValueError(f"{field_name} is required")
    if len(s) > max_length:
        raise ValueError(f"{field_name} too long (max {max_length} characters)")
    return s.strip()

def validate_file_path(path: str, for_writing: bool = False) -> Path:
    """Validate file path (prevents path traversal)."""
    # Implementation from our fix
    ...
```

#### 5. **Static Analysis Integration**

Integrate tools to catch issues automatically:

- **Bandit**: Security linter for Python
- **Safety**: Check dependencies for known vulnerabilities
- **Pylint**: Code quality and potential bugs
- **MyPy**: Type checking to catch type-related errors

Add to pre-commit hooks:
```bash
bandit -r src/ -ll  # Check for security issues
safety check         # Check dependencies
pylint src/          # Code quality
mypy src/            # Type checking
```

#### 6. **Security Documentation**

Create `SECURITY_GUIDELINES.md` with:

- Common attack vectors (SQL injection, XSS, path traversal)
- Secure coding patterns for this project
- Examples of secure vs insecure code
- Checklist for security-sensitive operations

#### 7. **Regular Security Reviews**

Schedule recurring security reviews:

- **Weekly**: Quick scan of PRs merged that week
- **Monthly**: Comprehensive security audit of new features
- **Quarterly**: Full penetration testing exercise
- **Annually**: Third-party security audit (if budget allows)

---

## Metrics and Success Criteria

### How We'll Measure Improvement

#### Short-term (Next 2 Weeks)

- [ ] Zero security issues in next QA review
- [ ] All PRs pass security checklist
- [ ] 100% test coverage for validation functions
- [ ] Validation library created and integrated

#### Medium-term (Next 2 Months)

- [ ] Bandit, Safety, Pylint integrated into CI/CD
- [ ] SECURITY_GUIDELINES.md created and reviewed by team
- [ ] All team members trained on secure coding practices
- [ ] Zero security issues found by static analysis tools

#### Long-term (Next 6 Months)

- [ ] External security audit with zero critical findings
- [ ] Security-first culture embedded in development process
- [ ] Automated security testing in CI/CD pipeline
- [ ] Public bug bounty program (if product goes public)

---

## Action Items

### Immediate (This Week)

1. [x] Fix all 10 security issues identified by QA
2. [x] Ensure all tests pass (192/192 passed)
3. [ ] Commit security fixes to GitHub
4. [ ] Create SECURITY_GUIDELINES.md
5. [ ] Set up Bandit and Safety in pre-commit hooks

### Short-term (Next 2 Weeks)

1. [ ] Create src/validation.py with centralized validation
2. [ ] Refactor existing code to use validation library
3. [ ] Add security test cases for all critical functions
4. [ ] Integrate static analysis tools into CI/CD
5. [ ] Conduct team training on secure coding

### Medium-term (Next 2 Months)

1. [ ] Implement automated security scanning in CI/CD
2. [ ] Add security review step to PR template
3. [ ] Create security-focused documentation
4. [ ] Conduct internal penetration testing
5. [ ] Review all third-party dependencies for vulnerabilities

---

## Lessons for Future Projects

### What to Do From Day One

1. **Define security requirements alongside functional requirements**
   - Example: "Allow CSV import" should include "with path validation and sanitization"

2. **Create validation constants immediately**
   - MAX_AMOUNT, MAX_STRING_LENGTH, etc. should exist before first feature

3. **Write security test cases early**
   - SQL injection tests, path traversal tests, overflow tests from the start

4. **Use specific exceptions, never bare except**
   - Forces you to think about what can go wrong

5. **Review third-party libraries for security**
   - Check CVE databases before adding dependencies

6. **Assume all users are adversarial**
   - Even internal tools should be secure by default

### Cultural Changes

- **Slow down to speed up**: Taking time for security upfront saves time fixing issues later
- **Security is everyone's responsibility**: Not just the "security person" or QA
- **Fail loudly during development**: Crashes are better than silent failures
- **Document threat models**: Write down how features could be attacked

---

## Conclusion

This security review revealed significant gaps in our security posture, but also provided an opportunity to strengthen our processes. The issues found were not due to a lack of skill, but rather a lack of security-first mindset during initial development.

By implementing the prevention strategies outlined above—security checklists, comprehensive testing, validation libraries, and cultural changes—we can ensure that future features are secure by design rather than requiring post-hoc fixes.

The fact that we found and fixed these issues before production deployment is a success. The real test will be whether we apply these lessons going forward and build security into our development DNA.

---

## Appendix: Resources

### Secure Coding Resources

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Python Security Best Practices](https://python.readthedocs.io/en/latest/library/security_warnings.html)
- [SQL Injection Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/SQL_Injection_Prevention_Cheat_Sheet.html)
- [Input Validation Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Input_Validation_Cheat_Sheet.html)

### Tools

- **Bandit**: https://bandit.readthedocs.io/
- **Safety**: https://pyup.io/safety/
- **Pylint**: https://pylint.org/
- **MyPy**: http://mypy-lang.org/

### Training

- Free: OWASP's Secure Coding Practices Guide
- Paid: PluralSight "Secure Coding in Python" course
- Practice: OWASP WebGoat for hands-on security training

---

**Retrospective Created By:** Claude Sonnet 4.5
**Date:** December 15, 2025
**Status:** Complete - All issues fixed and retrospective documented
