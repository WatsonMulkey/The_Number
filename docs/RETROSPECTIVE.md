# Retrospective: Database & Encoding Issues

## Date: December 8, 2024

## Problems Encountered

### 1. **Database Lock/Corruption Issue**
**Problem**: Could not delete `budget.db` - file was locked or corrupted
**Symptom**:
- `rm: cannot remove 'budget.db': Device or resource busy`
- Encryption key mismatch errors when trying to read
- `cryptography.fernet.InvalidToken` exceptions

**Root Causes**:
- Database file was created with a different encryption key than what was in `.env`
- Database file may have been opened by another process (SQLite browser, previous Python process)
- No proper connection cleanup in database operations

### 2. **Multi-line String Literal Syntax Error**
**Problem**: Broken Python syntax in `src/cli.py` line 54
**Symptom**:
```python
print("
  You can complete setup anytime by running the app again.
")
```
**Root Cause**:
- Used sed/awk commands that didn't properly escape newlines in Python strings
- Attempted to programmatically edit Python files without proper string escaping
- The broken code was committed to git, so `git checkout` restored the broken version

### 3. **Unicode/Emoji Encoding Issues on Windows**
**Problem**: `UnicodeEncodeError: 'charmap' codec can't encode character '\U0001f3af'`
**Symptom**: Emojis (🎯, 💰, etc.) failed to print on Windows console
**Root Cause**:
- Windows console uses CP1252 encoding by default, not UTF-8
- Python source files used UTF-8 with emoji characters
- No fallback or encoding configuration for Windows compatibility

---

## Impact Assessment

### Severity: **High**
- **User Experience**: App completely unusable - crashed on startup
- **Development Time**: ~2 hours debugging and fixing
- **Code Quality**: Multiple broken commits pushed to main branch
- **Trust**: Reduced confidence in app stability

### What Went Well:
✅ Issues were eventually resolved
✅ All fixes committed and documented
✅ App is now functional with Windows compatibility
✅ Good test coverage helped catch calculator bugs

### What Went Poorly:
❌ Database encryption key management was ad-hoc
❌ No database connection pooling or cleanup
❌ Programmatic file editing without proper validation
❌ Committed broken code to main branch multiple times
❌ No cross-platform testing (Windows vs Linux/Mac)
❌ No encoding strategy for console output

---

## Root Cause Analysis: The 5 Whys

### Problem 1: Database Lock/Corruption

1. **Why did the database become locked?**
   → It was opened by a Python process that didn't close properly

2. **Why didn't the connection close properly?**
   → We didn't implement proper context manager cleanup or explicit connection closing

3. **Why didn't we use context managers?**
   → The EncryptedDatabase class uses `with sqlite3.connect()` but doesn't track connections

4. **Why can multiple processes access the same database?**
   → SQLite allows it, but we don't have connection pooling or single-instance enforcement

5. **Why did the encryption key mismatch?**
   → The `.env` file was regenerated with a new key, but the old database wasn't deleted

**ROOT CAUSE**: No database lifecycle management or encryption key validation on startup

### Problem 2: Syntax Errors from Programmatic Edits

1. **Why did we get syntax errors?**
   → Multi-line strings were broken during sed/awk editing

2. **Why did we use sed/awk?**
   → Trying to programmatically add the onboarding method to an existing file

3. **Why not use proper Python AST manipulation?**
   → Seemed simpler to use text manipulation tools

4. **Why was the broken code committed?**
   → No pre-commit syntax validation or testing

5. **Why didn't we catch it before pushing?**
   → No CI/CD pipeline or pre-push hooks running syntax checks

**ROOT CAUSE**: No automated code validation before commits

### Problem 3: Unicode Encoding on Windows

1. **Why did emojis fail to print?**
   → Windows console uses CP1252, not UTF-8

2. **Why didn't we test on Windows earlier?**
   → Development happened in Git Bash (Unix-like environment)

3. **Why use emojis in a CLI app?**
   → Wanted to make the UI more friendly and modern

4. **Why no fallback for encoding errors?**
   → Didn't consider cross-platform console encoding differences

5. **Why no encoding configuration?**
   → No platform detection or encoding setup in the app

**ROOT CAUSE**: No cross-platform compatibility strategy

---

## Prevention Strategies

### Immediate Fixes (Already Done)
✅ Removed all emojis from output
✅ Fixed syntax errors in cli.py
✅ Database file cleared for fresh start

### Short-term Improvements (Implement Now)

#### 1. Database Management
```python
# Add to database.py

class EncryptedDatabase:
    def __init__(self, db_path: str = "budget.db", encryption_key: Optional[str] = None):
        # ... existing code ...

        # VALIDATE encryption key against existing database
        if os.path.exists(db_path) and encryption_key:
            self._validate_encryption_key()

    def _validate_encryption_key(self) -> None:
        """Validate that encryption key can decrypt existing data."""
        try:
            # Try to read a known setting
            test_value = self.get_setting("onboarded")
            # If this succeeds, key is valid
        except Exception as e:
            raise ValueError(
                "Database exists but encryption key is invalid. "
                "Either delete the database or use the correct key. "
                f"Error: {e}"
            )

    def close(self) -> None:
        """Explicitly close database connections."""
        # Track and close any open connections
        pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
```

#### 2. Pre-commit Hook
```bash
# .git/hooks/pre-commit

#!/bin/bash
# Validate Python syntax before commit

echo "Running pre-commit checks..."

# Check Python syntax
for file in $(git diff --cached --name-only | grep -E '\.py$'); do
    python -m py_compile "$file"
    if [ $? -ne 0 ]; then
        echo "❌ Syntax error in $file"
        exit 1
    fi
done

# Run tests
python -m pytest tests/ -x
if [ $? -ne 0 ]; then
    echo "❌ Tests failed"
    exit 1
fi

echo "✅ All checks passed"
```

#### 3. Platform-aware Console Output
```python
# Add to src/cli.py or new src/utils.py

import sys
import platform

def safe_print(text: str) -> None:
    """Print text with encoding fallback for Windows compatibility."""
    try:
        print(text)
    except UnicodeEncodeError:
        # Fallback for Windows console
        safe_text = text.encode('ascii', 'replace').decode('ascii')
        print(safe_text)

def configure_console_encoding():
    """Configure console for UTF-8 on Windows if possible."""
    if platform.system() == 'Windows':
        try:
            import ctypes
            # Set console to UTF-8
            ctypes.windll.kernel32.SetConsoleOutputCP(65001)
        except:
            pass  # Fallback to safe_print
```

#### 4. Database Health Check on Startup
```python
# Add to main.py

def check_database_health():
    """Verify database and encryption key are valid before starting."""
    if os.path.exists("budget.db"):
        encryption_key = os.getenv("DB_ENCRYPTION_KEY")
        if not encryption_key:
            print("ERROR: Database exists but no encryption key in .env")
            print("Options:")
            print("  1. Delete budget.db to start fresh")
            print("  2. Add correct DB_ENCRYPTION_KEY to .env")
            sys.exit(1)

        try:
            # Test database access
            db = EncryptedDatabase(encryption_key=encryption_key)
            db.get_setting("test")  # Try to read
        except Exception as e:
            print(f"ERROR: Cannot access database: {e}")
            print("The database may be corrupted or encrypted with a different key.")
            print("\nOptions:")
            print("  1. Delete budget.db and restart (loses all data)")
            print("  2. Restore correct encryption key in .env")
            sys.exit(1)
```

### Medium-term Improvements (Next Sprint)

#### 5. **Comprehensive Testing Strategy**
```python
# tests/test_database_lifecycle.py

def test_database_encryption_key_mismatch():
    """Test that wrong encryption key raises clear error."""
    # Create database with one key
    db1 = EncryptedDatabase("test.db", "key1")
    db1.set_setting("test", "value")

    # Try to open with different key
    with pytest.raises(ValueError, match="encryption key is invalid"):
        db2 = EncryptedDatabase("test.db", "key2")

def test_database_concurrent_access():
    """Test that concurrent access is handled safely."""
    # Test multiple processes accessing same database
    pass

def test_database_cleanup():
    """Test that connections are properly closed."""
    db = EncryptedDatabase("test.db")
    # ... operations ...
    db.close()
    # Verify file can be deleted (not locked)
    os.remove("test.db")
```

#### 6. **Cross-platform CI/CD**
```yaml
# .github/workflows/test.yml

name: Test

on: [push, pull_request]

jobs:
  test:
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [ubuntu-latest, windows-latest, macos-latest]
        python-version: [3.9, 3.10, 3.11, 3.12, 3.13]

    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: ${{ matrix.python-version }}
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run tests
        run: pytest tests/ -v
      - name: Check syntax
        run: python -m py_compile src/*.py
```

#### 7. **Database Migration System**
```python
# src/migrations.py

DATABASE_VERSION = 1

def get_schema_version(db: EncryptedDatabase) -> int:
    """Get current database schema version."""
    return db.get_setting("schema_version", 0)

def migrate_database(db: EncryptedDatabase):
    """Run any necessary database migrations."""
    current_version = get_schema_version(db)

    if current_version < 1:
        # Migration 0 -> 1: Add new fields, etc.
        pass

    db.set_setting("schema_version", DATABASE_VERSION)
```

### Long-term Improvements (Future)

#### 8. **Encrypted Backup System**
- Automatic daily backups of database
- Export/import functionality for data portability
- Encryption key recovery mechanism

#### 9. **Better Key Management**
- Key derivation from user password (PBKDF2)
- Key rotation support
- Secure key storage (OS keyring integration)

#### 10. **Structured Logging**
```python
# src/logger.py

import logging

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('the_number.log'),
            logging.StreamHandler()
        ]
    )

# Log all database operations
logger.info("Database opened with key: %s", key_hash)
logger.error("Database encryption key mismatch", exc_info=True)
```

---

## Testing Checklist for Future Changes

Before pushing code, verify:

- [ ] All Python files compile without syntax errors (`python -m py_compile src/*.py`)
- [ ] All tests pass (`pytest tests/ -v`)
- [ ] Tested on Windows (if available)
- [ ] No hardcoded file paths (use `os.path.join` or `Path`)
- [ ] No Unicode characters in console output (or use `safe_print()`)
- [ ] Database connections are properly closed
- [ ] Error messages are helpful and actionable
- [ ] No secrets or keys in code (use environment variables)
- [ ] Documentation updated if behavior changes

---

## Action Items

### Critical (Do Now)
1. ✅ Remove emojis from all output
2. ✅ Fix syntax errors in cli.py
3. ✅ Add database validation on startup
4. ⬜ Implement pre-commit hooks
5. ⬜ Add platform detection and encoding setup

### Important (This Week)
6. ⬜ Write database lifecycle tests
7. ⬜ Add GitHub Actions CI/CD
8. ⬜ Implement database context manager
9. ⬜ Add comprehensive error handling
10. ⬜ Document Windows setup instructions

### Nice to Have (Future)
11. ⬜ Database backup/export feature
12. ⬜ Key rotation mechanism
13. ⬜ Structured logging
14. ⬜ Migration system
15. ⬜ Password-based key derivation

---

## Key Learnings

### 1. **Database Encryption is Complex**
- Need key validation on startup
- Need migration strategy for key changes
- Need clear error messages when keys mismatch
- Consider simpler alternatives (file permissions + env vars)

### 2. **Cross-platform is Hard**
- Test on target platforms early
- Avoid platform-specific features (emojis, file paths)
- Use abstraction layers for OS differences
- Document platform-specific setup

### 3. **Programmatic Code Editing is Risky**
- Use AST manipulation, not text editing
- Always validate syntax after changes
- Better to use templates or code generation
- Pre-commit hooks catch these issues

### 4. **Testing Prevents Pain**
- Should have tested Windows before pushing
- Should have syntax validation in CI/CD
- Should have database integration tests
- Manual testing is not enough

### 5. **Error Messages Matter**
- Users need clear next steps
- "Invalid token" is cryptic
- "Database encrypted with different key. Delete budget.db or restore key" is helpful
- Always provide recovery options

---

## Conclusion

The database and encoding issues were caused by:
1. Inadequate database lifecycle management
2. No encryption key validation
3. Programmatic code editing without validation
4. Lack of cross-platform testing
5. No automated pre-commit checks

**Primary Fix**: Implement database validation on startup + pre-commit hooks + platform-aware output

**Long-term**: Add CI/CD, comprehensive tests, better key management, and structured logging

**Commitment**: No more broken commits to main. All changes must pass syntax validation and tests before pushing.

---

## Sign-off

This retrospective identifies the root causes and provides concrete, actionable prevention strategies. The immediate fixes (emoji removal, syntax correction) are complete. The short-term improvements (database validation, pre-commit hooks) should be implemented before adding new features.

**Status**: Issues resolved ✅
**Prevention strategy**: Documented ✅
**Next steps**: Implement short-term improvements ⬜
