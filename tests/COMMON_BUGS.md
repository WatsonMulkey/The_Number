# Common Bugs and Issues to Watch For

## Python-Specific Issues

### 1. Float Precision Errors (CRITICAL for budgeting app)
```python
# WRONG - Will cause precision errors
price = 10.10
tax = 0.20
total = price + tax  # May not be exactly 10.30

# CORRECT - Use Decimal for money
from decimal import Decimal
price = Decimal('10.10')
tax = Decimal('0.20')
total = price + tax  # Exactly 10.30
```

### 2. Mutable Default Arguments
```python
# WRONG - Default list is shared across calls
def add_transaction(amount, transactions=[]):
    transactions.append(amount)
    return transactions

# CORRECT
def add_transaction(amount, transactions=None):
    if transactions is None:
        transactions = []
    transactions.append(amount)
    return transactions
```

### 3. Uncaught Exceptions on User Input
```python
# WRONG - Will crash on invalid input
amount = float(input("Enter amount: "))

# CORRECT - Validate and handle errors
try:
    amount_str = input("Enter amount: ")
    amount = float(amount_str)
    if amount < 0:
        raise ValueError("Amount cannot be negative")
except ValueError as e:
    print(f"Invalid amount: {e}")
    # Handle error appropriately
```

---

## Database Issues

### 4. SQL Injection Vulnerability
```python
# WRONG - Vulnerable to SQL injection
category = input("Enter category: ")
query = f"SELECT * FROM transactions WHERE category='{category}'"
cursor.execute(query)

# CORRECT - Use parameterized queries
category = input("Enter category: ")
query = "SELECT * FROM transactions WHERE category=?"
cursor.execute(query, (category,))
```

### 5. Not Closing Database Connections
```python
# WRONG - Connection may not close
conn = sqlite3.connect('budget.db')
cursor = conn.cursor()
cursor.execute("SELECT * FROM transactions")
results = cursor.fetchall()
# Forgot to close!

# CORRECT - Use context manager
with sqlite3.connect('budget.db') as conn:
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM transactions")
    results = cursor.fetchall()
# Automatically closed
```

### 6. No Transaction Rollback on Errors
```python
# WRONG - Partial changes may persist
conn.execute("UPDATE budget SET amount=?", (100,))
conn.execute("UPDATE transactions SET amount=?", ("invalid",))  # Crashes
conn.commit()

# CORRECT - Use transactions
try:
    with conn:
        conn.execute("UPDATE budget SET amount=?", (100,))
        conn.execute("UPDATE transactions SET amount=?", (200,))
except Exception as e:
    # Automatically rolled back
    print(f"Transaction failed: {e}")
```

---

## Encryption Issues

### 7. Hardcoded Encryption Keys
```python
# WRONG - Key is in source code
KEY = b'hardcoded-secret-key-12345678901234567890123456789012'
cipher = Fernet(KEY)

# CORRECT - Load from environment
import os
from dotenv import load_dotenv
load_dotenv()
KEY = os.getenv('ENCRYPTION_KEY')
if not KEY:
    raise ValueError("ENCRYPTION_KEY not found in environment")
cipher = Fernet(KEY.encode())
```

### 8. Not Encrypting Sensitive Data
```python
# WRONG - Storing plain text
conn.execute("INSERT INTO transactions (amount) VALUES (?)", (100.50,))

# CORRECT - Encrypt before storage
from cryptography.fernet import Fernet
cipher = Fernet(key)
encrypted_amount = cipher.encrypt(str(100.50).encode())
conn.execute("INSERT INTO transactions (amount) VALUES (?)", (encrypted_amount,))
```

---

## Input Validation Issues

### 9. Not Validating Date Formats
```python
# WRONG - Accepts any string
date_str = input("Enter date: ")
# User enters "banana" - crash later

# CORRECT - Validate format
from datetime import datetime
date_str = input("Enter date (YYYY-MM-DD): ")
try:
    date_obj = datetime.strptime(date_str, '%Y-%m-%d')
except ValueError:
    print("Invalid date format. Please use YYYY-MM-DD")
```

### 10. No Maximum Length Validation
```python
# WRONG - User can enter unlimited text
description = input("Enter description: ")

# CORRECT - Enforce limits
description = input("Enter description (max 200 chars): ")
if len(description) > 200:
    print("Description too long")
    description = description[:200]
```

### 11. Not Stripping Whitespace
```python
# WRONG - Accepts "  50  " as input
amount = float(input("Enter amount: "))

# CORRECT - Strip whitespace
amount_str = input("Enter amount: ").strip()
amount = float(amount_str)
```

---

## Logic Errors

### 12. Division by Zero
```python
# WRONG - Will crash if days is 0
days = int(input("Days until paycheck: "))
daily_budget = total / days

# CORRECT - Check for zero
days = int(input("Days until paycheck: "))
if days <= 0:
    print("Days must be positive")
else:
    daily_budget = total / days
```

### 13. Off-by-One Errors in Date Ranges
```python
# WRONG - May miss last day
start_date = datetime(2025, 12, 1)
end_date = datetime(2025, 12, 31)
days = (end_date - start_date).days  # 30, should be 31

# CORRECT - Add 1 for inclusive range
days = (end_date - start_date).days + 1  # 31
```

### 14. Integer Division When Float Expected
```python
# WRONG - Python 2 style integer division
daily = 100 / 3  # May be 33 in Python 2

# CORRECT - Explicit float division
from decimal import Decimal
daily = Decimal('100') / Decimal('3')  # 33.333...
```

---

## File System Issues

### 15. Hardcoded File Paths
```python
# WRONG - Won't work on different systems
DB_PATH = "C:\\Users\\username\\budget.db"

# CORRECT - Use relative paths or environment variables
import os
DB_PATH = os.path.join(os.getcwd(), 'budget.db')
# Or use environment variable
DB_PATH = os.getenv('DB_PATH', 'budget.db')
```

### 16. Not Checking File Existence
```python
# WRONG - Crashes if file doesn't exist
with open('config.txt', 'r') as f:
    config = f.read()

# CORRECT - Check first
import os
if os.path.exists('config.txt'):
    with open('config.txt', 'r') as f:
        config = f.read()
else:
    print("Config file not found")
```

---

## Error Handling Issues

### 17. Catching Too Broad Exceptions
```python
# WRONG - Catches everything, even system exits
try:
    process_transaction()
except:
    print("Error occurred")

# CORRECT - Catch specific exceptions
try:
    process_transaction()
except ValueError as e:
    print(f"Invalid value: {e}")
except DatabaseError as e:
    print(f"Database error: {e}")
```

### 18. Not Logging Errors
```python
# WRONG - Error disappears
try:
    risky_operation()
except Exception:
    pass  # Silent failure

# CORRECT - Log for debugging
import logging
try:
    risky_operation()
except Exception as e:
    logging.error(f"Operation failed: {e}", exc_info=True)
    print("An error occurred. Please try again.")
```

### 19. Exposing Stack Traces to Users
```python
# WRONG - Shows internal details to user
try:
    process_data()
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()  # User sees full stack trace

# CORRECT - Log details, show friendly message
import logging
try:
    process_data()
except Exception as e:
    logging.error(f"Process failed: {e}", exc_info=True)
    print("Something went wrong. Please contact support.")
```

---

## Performance Issues

### 20. N+1 Query Problem
```python
# WRONG - One query per transaction
transactions = get_all_transactions()
for trans in transactions:
    category = get_category(trans.category_id)  # Separate query each time

# CORRECT - Load all at once
transactions = get_all_transactions_with_categories()  # JOIN query
```

### 21. Not Using Indexes
```sql
-- WRONG - Slow query without index
SELECT * FROM transactions WHERE date = '2025-12-08';

-- CORRECT - Create index first
CREATE INDEX idx_transaction_date ON transactions(date);
SELECT * FROM transactions WHERE date = '2025-12-08';
```

---

## Testing Edge Cases

### Critical Edge Cases to Test
1. **Zero values**: 0 income, 0 expenses, 0 days
2. **Negative values**: -100 income, -5 days
3. **Very large values**: 999,999,999.99
4. **Very small values**: 0.01
5. **Empty strings**: "", " ", None
6. **Special characters**: `', ", \, ;, --`
7. **Null bytes**: `\x00`
8. **Unicode**: emoji, foreign characters
9. **Date boundaries**: Feb 29, Dec 31, Jan 1
10. **Precision**: 10.10 + 20.20 = 30.30 exactly

---

## Quick Security Checklist

Before committing any code, verify:
- [ ] All database queries use parameterized statements
- [ ] All user input is validated
- [ ] Sensitive data is encrypted
- [ ] No hardcoded secrets
- [ ] Error messages don't expose internal details
- [ ] All file operations check for existence
- [ ] Using Decimal for monetary calculations
- [ ] All exceptions are caught and handled
- [ ] .env and .db files are in .gitignore
- [ ] Tests exist for all edge cases

---

## Testing Commands for Each Issue

```bash
# Test SQL injection
pytest tests/test_security.py::TestSQLInjectionPrevention -v

# Test encryption
pytest tests/test_security.py::TestEncryption -v

# Test input validation
pytest tests/test_security.py::TestInputValidation -v

# Test decimal precision
pytest tests/test_budget_calculator.py::TestDecimalArithmetic -v

# Test all security issues
pytest tests/test_security.py -v

# Run with coverage
pytest --cov=src --cov-report=html
```
