# QA Report: The Number Budgeting App
**Date:** 2025-12-15
**Review Type:** Security, Logic, and Edge Case Analysis
**Files Reviewed:** calculator.py, database.py, cli.py, import_expenses.py, export_expenses.py, onboarding.py, utils.py

---

## Critical Issues (Blocks Release)

### 1. SQL Injection Vulnerability in database.py
**File:Line:** `database.py:220-221`
**Issue:** Dynamic SQL query construction using f-string with user-controlled column names
```python
cursor.execute(
    f"UPDATE expenses SET {', '.join(updates)} WHERE id = ?",
    params
)
```
**Impact:** Potential SQL injection attack if column names are somehow manipulated. While current code only uses hardcoded column names, this pattern is dangerous and could lead to vulnerabilities if code is modified.
**Fix:** Whitelist allowed column names before constructing the query:
```python
allowed_columns = {'name', 'amount', 'is_fixed', 'updated_at'}
if not all(col.split('=')[0].strip() in allowed_columns for col in updates):
    raise ValueError("Invalid column name")
```

### 2. Negative Daily Limit Not Handled Properly
**File:Line:** `calculator.py:101`, `cli.py:162-165`
**Issue:** When expenses exceed income, daily_limit becomes negative. The calculator returns this negative value, and the CLI shows warnings but doesn't prevent users from trying to use a negative budget.
**Impact:** Users with negative budgets see confusing negative "daily limit" numbers (-$50.25 per day). The app should handle this as a special case rather than treating it as a valid budget.
**Fix:** In calculator.py, add a check:
```python
daily_limit = max(0, remaining_money / days_until_paycheck)
```
Add a flag in the return dictionary to indicate deficit state for proper UI messaging.

### 3. Division by Zero in Fixed Pool Mode
**File:Line:** `calculator.py:136`
**Issue:** When `total_expenses` is 0 and `total_money` is 0, the division on line 136 would fail, but it's protected by the `if total_expenses > 0` check. However, if total_money is 0 and expenses > 0, we get `months_remaining = 0 / total_expenses = 0` which then causes `daily_limit = 0 / 0` on line 136.
**Impact:** Potential division by zero error when user has no money but has expenses.
**Fix:** Add explicit check for total_money == 0 case before calculations.

---

## Major Issues (Should Fix Soon)

### 4. No Input Sanitization for Special Characters
**File:Line:** `cli.py:214`, `onboarding.py:233`, `import_expenses.py:68`
**Issue:** Expense names accept any string input including special characters, SQL-like syntax, or extremely long strings (10,000+ characters). No length limits enforced.
**Impact:** Could cause display issues, database bloat, or CSV/Excel export problems with special characters.
**Fix:** Add validation in `get_input()`:
```python
if input_type == str and len(value) > 200:
    print("  Input too long (max 200 characters)")
    continue
```

### 5. Large Number Overflow Not Handled
**File:Line:** `calculator.py:22-23`, `cli.py:218-221`
**Issue:** No upper bounds on expense amounts. User could enter amounts like `9999999999999999999999`, causing float overflow or precision loss.
**Impact:** Calculation errors, display issues, database corruption with extremely large values.
**Fix:** Add validation for reasonable upper bounds (e.g., $1,000,000 per expense):
```python
if amount > 1_000_000:
    raise ValueError("Amount exceeds maximum allowed ($1,000,000)")
```

### 6. File Path Injection in Import/Export
**File:Line:** `import_expenses.py:38`, `export_expenses.py:25`
**Issue:** User-provided file paths are used directly with `open()` without validation. Paths like `../../etc/passwd` or `C:\Windows\System32\config\SAM` could be accessed.
**Impact:** Users could potentially read or write files outside intended directory.
**Fix:** Validate file paths are in expected directory:
```python
from pathlib import Path
file_path = Path(file_path).resolve()
allowed_dir = Path.cwd().resolve()
if not str(file_path).startswith(str(allowed_dir)):
    raise ValueError("File path must be in current directory")
```

### 7. Database Encryption Key Displayed in Plain Text
**File:Line:** `database.py:48`, `utils.py:114`
**Issue:** Encryption key is printed to console in plain text during initial setup.
**Impact:** Key exposure if someone is screen-sharing, recording terminal, or if terminal history is logged.
**Fix:** Provide option to save key to file instead of printing, or mask/redact when displaying.

### 8. No Transaction Validation
**File:Line:** `database.py:234-258`, `cli.py:474-491`
**Issue:** Transactions accept any amount (including negative, zero, or huge values) and empty descriptions pass validation in some flows.
**Impact:** Data quality issues, impossible to track spending accurately with invalid transactions.
**Fix:** Add validation:
```python
if amount <= 0:
    raise ValueError("Transaction amount must be positive")
if not description or not description.strip():
    raise ValueError("Description required")
```

### 9. CSV Import Delimiter Detection Failure
**File:Line:** `import_expenses.py:43-47`
**Issue:** `csv.Sniffer()` can fail on small files or files with uncommon formats, causing crashes.
**Impact:** App crashes instead of providing helpful error message when importing malformed CSV.
**Fix:** Add try/except around sniffer with fallback to comma:
```python
try:
    delimiter = sniffer.sniff(sample).delimiter
except Exception:
    delimiter = ','  # Default fallback
```

### 10. Excel Column Width Calculation Exception Silently Ignored
**File:Line:** `export_expenses.py:110`
**Issue:** Bare `except:` clause silently ignores all exceptions including KeyboardInterrupt and SystemExit.
**Impact:** Could mask important errors and make debugging difficult.
**Fix:** Use specific exception:
```python
except (TypeError, AttributeError):
    pass
```

---

## Minor Issues (Nice to Have)

### 11. Inconsistent Date Handling
**File:Line:** `calculator.py:65`, `database.py:317`
**Issue:** Some functions use `.date()` to extract date from datetime, others compare datetime directly. Could cause bugs if time components matter.
**Impact:** Minor edge case issues around midnight transitions.
**Fix:** Standardize date comparison approach throughout codebase.

### 12. No Validation for Days Until Paycheck Upper Bound
**File:Line:** `calculator.py:96-97`
**Issue:** User could enter 999999 days until paycheck, creating meaningless daily budgets.
**Impact:** Confusing results if user enters unrealistic values.
**Fix:** Add reasonable upper limit (e.g., 365 days):
```python
if days_until_paycheck > 365:
    raise ValueError("Days until paycheck cannot exceed 365")
```

### 13. Duplicate Expense Names Allowed in Database
**File:Line:** `database.py:147-168`
**Issue:** No uniqueness constraint on expense names. Users can add "Rent" multiple times.
**Impact:** Confusing for users, potential for accidental duplicates.
**Fix:** Add duplicate detection before insert or add database constraint.

### 14. Float Precision Issues in Currency Calculations
**File:Line:** `calculator.py:101`, `calculator.py:136`
**Issue:** Using float for currency can cause precision issues (0.1 + 0.2 != 0.3).
**Impact:** Minor rounding errors over time, especially with many transactions.
**Fix:** Consider using `Decimal` type for currency calculations.

### 15. No Logging for Errors
**File:Line:** Throughout all files
**Issue:** No error logging mechanism. When exceptions occur, details are lost.
**Impact:** Difficult to debug user-reported issues.
**Fix:** Add logging module with file output for errors.

### 16. Hardcoded Database and File Paths
**File:Line:** `cli.py:21`, `utils.py:88`
**Issue:** Database path "budget.db" is hardcoded, making it difficult to have multiple budgets or test environments.
**Impact:** Inflexibility for power users or testing scenarios.
**Fix:** Allow database path configuration via environment variable or CLI argument.

### 17. Empty Expense Name Handling
**File:Line:** `import_expenses.py:68`, `import_expenses.py:162`
**Issue:** In Excel import, empty name causes row to be skipped silently. In CSV, empty name might pass through.
**Impact:** Silent data loss if spreadsheet has formatting issues.
**Fix:** Report skipped rows to user with reason.

### 18. Infinity Values in Fixed Pool Mode
**File:Line:** `calculator.py:139-140`, `cli.py:343`
**Issue:** When no expenses exist, `months_remaining` and `days_remaining` are set to `float('inf')`, which displays as "inf" or "Indefinitely!" in UI.
**Impact:** While technically correct, could confuse users or cause JSON serialization issues.
**Fix:** Cap at a large reasonable number (e.g., 9999 days) or use special flag.

### 19. KeyboardInterrupt Not Consistently Handled
**File:Line:** `cli.py:108`, `onboarding.py:84`
**Issue:** Some functions catch KeyboardInterrupt and return None, others let it propagate.
**Impact:** Inconsistent user experience when pressing Ctrl+C.
**Fix:** Standardize interrupt handling across all user input functions.

### 20. No Data Export Validation
**File:Line:** `export_expenses.py:38`, `export_expenses.py:88`
**Issue:** Export functions don't verify file was written successfully or is readable.
**Impact:** User thinks export succeeded but file might be corrupt or in use.
**Fix:** Verify file exists and is readable after write operation.

---

## Positive Findings

### What's Well Done

1. **Strong Encryption Implementation**
   Uses industry-standard Fernet symmetric encryption (AES-128 in CBC mode). Properly encrypts sensitive settings while keeping schema readable.

2. **Good Input Type Validation**
   The `get_input()` functions properly validate types (str, int, float) with clear error messages.

3. **Proper Context Manager Usage**
   SQLite connections use `with` statements ensuring proper cleanup even on errors.

4. **Comprehensive CSV/Excel Import**
   Import functions handle multiple column name variations, currency formatting ($, commas), and flexible formats.

5. **Clear Error Messages**
   User-facing errors are well-formatted and actionable (e.g., telling users what went wrong and how to fix it).

6. **Transaction Safety**
   Database operations use transactions properly with commit/rollback behavior.

7. **Cross-Platform Compatibility**
   Code handles Windows vs Unix differences (`cls` vs `clear`, UTF-8 encoding issues).

8. **Good Code Organization**
   Clean separation of concerns: calculator logic, database layer, CLI, import/export in separate modules.

9. **Parameterized SQL Queries**
   Most database queries use proper parameterization (except issue #1), preventing SQL injection.

10. **User-Friendly Onboarding**
    Excellent first-time user experience with guided setup, clear explanations, and helpful tips.

---

## Recommended Testing Focus Areas

1. **Boundary Testing**: Test with $0 income, $0 expenses, maximum float values
2. **Security Testing**: Test file paths with directory traversal attempts
3. **Data Validation**: Test CSV/Excel imports with malformed data, special characters, Unicode
4. **Error Recovery**: Test database corruption scenarios, wrong encryption key
5. **Edge Cases**: Test negative numbers, extremely large numbers, empty inputs
6. **Concurrent Access**: Test what happens if database accessed by multiple instances

---

## Summary

**Critical Issues:** 3 (SQL injection pattern, negative budget handling, division by zero risk)
**Major Issues:** 7 (input validation, file security, large numbers, transaction validation)
**Minor Issues:** 10 (consistency, user experience, edge cases)

**Overall Assessment:** The application has a solid foundation with good security practices (encryption, parameterized queries), but needs hardening around input validation, edge case handling, and error management before production release. The critical issues are relatively easy to fix and should be addressed immediately.

**Recommended Action:** Fix critical issues before any release. Address major issues for production readiness. Minor issues can be tracked for future releases but shouldn't block launch.
