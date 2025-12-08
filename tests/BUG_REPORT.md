# Bug Report - The_Number Budget App
**Generated**: 2025-12-08
**Status**: ACTIVE ISSUES

---

## 🔴 CRITICAL BUGS (P0) - Fix Immediately

### BUG #1: Float Precision Errors in All Monetary Calculations
**Severity**: CRITICAL
**Status**: OPEN
**Affects**: All modules

**Description**:
All monetary values use Python `float` type, which causes precision errors in financial calculations.

**Example**:
```python
>>> 10.10 + 20.20
30.299999999999997  # Should be 30.30
```

**Impact**:
- Inaccurate budget calculations
- User sees wrong amounts
- Errors accumulate over time
- Violates financial accuracy requirements

**Files Affected**:
- `calculator.py` - All amount calculations
- `database.py` - All amount storage/retrieval
- `cli.py` - All amount displays

**How to Reproduce**:
1. Add income of $1000.00
2. Set expenses of $333.33 per month
3. Calculate daily budget for 3 days
4. Result: Precision errors in calculation

**Expected**: Exact decimal precision (e.g., $33.33)
**Actual**: Float approximation (e.g., $33.32999999)

**Fix Required**: Replace all `float` with `decimal.Decimal`

**Test Case**: `tests/test_budget_calculator.py::TestDecimalArithmetic`

---

### BUG #2: Transaction Data Not Encrypted
**Severity**: CRITICAL (Security)
**Status**: OPEN
**Affects**: database.py

**Description**:
Transaction amounts and descriptions are stored in PLAIN TEXT in the database. Only settings are encrypted.

**Location**: `database.py:254-256`

**Security Risk**: HIGH
- Anyone with file access can read ALL transactions
- Financial data fully exposed
- Defeats purpose of having encryption

**Current Code**:
```python
# NO ENCRYPTION - Plain text storage
cursor.execute("""
    INSERT INTO transactions (date, amount, description, category, created_at)
    VALUES (?, ?, ?, ?, ?)
""", (date.isoformat(), amount, description, category, datetime.now().isoformat()))
```

**What's Exposed**:
- All amounts: $50.00, $1500.00, etc.
- All descriptions: "Coffee", "Rent", etc.
- All categories: "Food", "Housing", etc.

**Fix Required**: Encrypt sensitive fields before storage

**Expected Behavior**:
```python
encrypted_amount = self._encrypt(str(amount))
encrypted_description = self._encrypt(description)
# Then store encrypted values
```

**Test Case**: `tests/test_security.py::TestEncryption::test_encrypted_data_not_readable`

---

### BUG #3: SQL Injection Risk in update_expense
**Severity**: CRITICAL (Security)
**Status**: OPEN
**Affects**: database.py:221

**Description**:
F-string used to build SQL query with column names. While not currently exploitable, this is DANGEROUS practice.

**Location**: `database.py:221`

**Vulnerable Code**:
```python
cursor.execute(
    f"UPDATE expenses SET {', '.join(updates)} WHERE id = ?",
    params
)
```

**Current Risk**: MEDIUM
- Column names are controlled by code (not user input)
- BUT: Dangerous pattern that could be exploited if code is modified

**Future Risk**: HIGH
- If anyone adds user-controlled column selection
- If code is copied to other projects

**Attack Vector**:
If code is modified to accept column names from user:
```python
# Hypothetical modification - VULNERABLE:
column_to_update = user_input  # User enters: "amount = 0; DROP TABLE expenses; --"
updates.append(f"{column_to_update} = ?")
```

**Fix Required**: Whitelist allowed columns

**Recommended Fix**:
```python
ALLOWED_COLUMNS = {'name', 'amount', 'is_fixed', 'updated_at'}
# Validate all update keys before building query
for column in updates:
    if column not in ALLOWED_COLUMNS:
        raise ValueError(f"Invalid column: {column}")
```

**Test Case**: `tests/test_security.py::TestSQLInjectionPrevention::test_update_expense_safety`

---

## 🟡 HIGH PRIORITY BUGS (P1) - Fix Soon

### BUG #4: No Input Sanitization
**Severity**: HIGH
**Status**: OPEN
**Affects**: cli.py

**Description**:
User input is validated for type but not sanitized for content.

**Issues**:
- No maximum length limits
- No special character filtering
- Could accept SQL injection attempts (safe only because of parameterized queries)
- Could accept very long strings causing display/storage issues

**Example Inputs Not Handled**:
```
Description: <script>alert('xss')</script>
Category: '; DROP TABLE transactions; --
Amount: [10000 character string]
```

**Current Protection**: Parameterized queries prevent SQL injection

**Remaining Risk**:
- Database bloat from huge strings
- Display issues with special characters
- No audit trail of suspicious inputs

**Fix Required**: Add sanitization:
```python
def _sanitize_input(self, text: str, max_length: int = 200) -> str:
    # Remove control characters
    # Limit length
    # Log suspicious patterns
    cleaned = ''.join(c for c in text if c.isprintable())
    return cleaned[:max_length].strip()
```

**Test Case**: `tests/test_security.py::TestInputValidation::test_special_characters_in_text_fields`

---

### BUG #5: No Transaction Rollback
**Severity**: HIGH
**Status**: OPEN
**Affects**: cli.py, database.py

**Description**:
If multi-step operation fails, partial changes persist. Database and calculator can get out of sync.

**Scenario**:
```python
# In CLI._add_expense():
self.db.add_expense(name, amount, is_fixed)  # ✅ Succeeds - written to DB
self.calculator.add_expense(name, amount, is_fixed)  # ❌ Fails - exception
# Result: Database has expense, calculator doesn't - OUT OF SYNC!
```

**Impact**:
- Data inconsistency
- Budget calculations wrong
- Requires app restart to fix

**Fix Required**: Use database transactions:
```python
try:
    with sqlite3.connect(self.db_path) as conn:
        # All operations here
        # Auto-commits on success, rolls back on exception
except Exception:
    # All changes automatically rolled back
```

**Test Case**: `tests/test_integration.py::TestErrorRecovery::test_recovery_from_partial_failure`

---

### BUG #6: Encryption Key Printed to Console
**Severity**: HIGH (Security)
**Status**: OPEN
**Affects**: database.py:42-50

**Description**:
On first run, encryption key is printed to console in plain text.

**Code**:
```python
print(f"\nEncryption Key: {key.decode()}\n")
```

**Security Risks**:
- Key visible in terminal history
- Could be screenshot
- Could be logged to file
- Could be observed over shoulder
- Violates key management best practices

**Better Approach**:
1. Save key to `.env` file automatically
2. Show instructions how to back it up
3. Don't print the key itself

**Fix Required**: Save to file, don't print

**Test Case**: `tests/test_security.py::TestEncryption::test_key_not_printed`

---

## 🟠 MEDIUM PRIORITY BUGS (P2) - Fix When Possible

### BUG #7: No Database Indexes
**Severity**: MEDIUM (Performance)
**Status**: OPEN
**Affects**: database.py

**Description**:
No indexes on frequently queried columns. Queries will slow down as database grows.

**Missing Indexes**:
- `transactions.date` - Used in date range queries
- `transactions.category` - Used for filtering
- `expenses.created_at` - Used for ordering

**Impact**:
- Slow queries with 1000+ transactions
- O(n) scans instead of O(log n) index lookups

**Fix Required**:
```sql
CREATE INDEX IF NOT EXISTS idx_transaction_date ON transactions(date);
CREATE INDEX IF NOT EXISTS idx_transaction_category ON transactions(category);
CREATE INDEX IF NOT EXISTS idx_expense_created ON expenses(created_at);
```

**Test Case**: `tests/test_database.py::TestDatabasePerformance::test_query_performance`

---

### BUG #8: Hardcoded 30 Days Per Month
**Severity**: MEDIUM
**Status**: OPEN
**Affects**: calculator.py:135

**Description**:
Fixed pool mode assumes all months have 30 days.

**Code**:
```python
days_remaining = months_remaining * 30  # Approximate
```

**Impact**:
- Inaccurate for months with 28, 29, or 31 days
- Calculation errors of up to 10% for February

**Example**:
- User has $1000, $500/month expenses
- 2 months remaining
- Code calculates: 60 days (2 * 30)
- Actual: Could be 59, 61, or 62 days depending on months

**Fix Required**: Use actual calendar days or average 30.42 days/month

**Test Case**: `tests/test_budget_calculator.py::TestFixedPoolMode::test_accurate_days_per_month`

---

### BUG #9: Generic Error Messages Expose Details
**Severity**: MEDIUM (Security)
**Status**: OPEN
**Affects**: cli.py:374

**Description**:
Generic exception handler prints exception details to user.

**Code**:
```python
except Exception as e:
    print(f"\n  ❌ Error: {e}\n")
```

**Risk**: Could expose:
- File paths: "Cannot open /Users/john/budget.db"
- Database schema: "Column 'xyz' doesn't exist"
- Python internals: Stack traces

**Better**:
```python
import logging
except Exception as e:
    logging.error(f"Error: {e}", exc_info=True)  # Log details
    print("\n  ❌ An error occurred. Please try again.\n")  # Generic message to user
```

**Test Case**: `tests/test_security.py::TestErrorHandling::test_error_messages_not_verbose`

---

### BUG #10: Inconsistent Error Handling
**Severity**: MEDIUM
**Status**: OPEN
**Affects**: calculator.py

**Description**:
Some methods raise ValueError, others return special values (0, inf).

**Examples**:
```python
# Raises ValueError:
if days_until_paycheck <= 0:
    raise ValueError("Days until paycheck must be positive")

# Returns special value:
daily_limit = total_money / days_remaining if days_remaining > 0 else 0

# Returns infinity:
months_remaining = float('inf')
```

**Impact**:
- Hard to predict behavior
- Hard to handle errors consistently
- Inconsistent user experience

**Fix Required**: Choose one strategy and use everywhere

**Test Case**: `tests/test_budget_calculator.py::TestBudgetEdgeCases`

---

## 🟢 LOW PRIORITY ISSUES (P3) - Nice to Have

### ISSUE #11: No Logging
**Severity**: LOW
**Status**: OPEN
**Affects**: All modules

**Description**: No logging for debugging or audit trail.

**Recommendation**: Add Python logging module

---

### ISSUE #12: No Data Validation on Retrieval
**Severity**: LOW
**Status**: OPEN
**Affects**: database.py

**Description**: Data from database not validated. Could cause errors if database manually edited.

**Recommendation**: Validate data when loading

---

### ISSUE #13: Emoji May Not Display on All Terminals
**Severity**: LOW
**Status**: OPEN
**Affects**: cli.py

**Description**: Unicode emoji used throughout CLI. May not display on older terminals.

**Recommendation**: Make emoji optional or provide fallback

---

## BUG STATISTICS

**Total Bugs**: 13
- 🔴 Critical (P0): 3
- 🟡 High (P1): 3
- 🟠 Medium (P2): 4
- 🟢 Low (P3): 3

**Security Bugs**: 5
**Performance Bugs**: 2
**Functional Bugs**: 6

---

## TESTING STATUS

**Tests Written**: 279 test stubs
**Tests Passing**: 0 (not yet run)
**Tests Failing**: Unknown
**Coverage**: 0%

---

## RECOMMENDED FIX ORDER

1. **BUG #1**: Float → Decimal (affects all calculations)
2. **BUG #2**: Encrypt transactions (critical security)
3. **BUG #3**: Fix SQL injection risk (security)
4. **BUG #4**: Add input sanitization (security)
5. **BUG #5**: Add transaction rollback (data integrity)
6. **BUG #6**: Don't print encryption key (security)
7. **BUG #7**: Add database indexes (performance)
8. **BUG #8**: Fix days per month (accuracy)
9. **BUG #9**: Better error messages (security)
10. **BUG #10**: Consistent error handling (code quality)

---

**Report Status**: COMPLETE
**Next Update**: After bugs are fixed and tests run
