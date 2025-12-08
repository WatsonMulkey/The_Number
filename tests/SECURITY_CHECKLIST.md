# Security Testing Checklist for The_Number

## Critical Security Concerns

### 1. SQL Injection Prevention
- [ ] All database queries use parameterized statements
- [ ] No string concatenation in SQL queries
- [ ] User input is never directly inserted into SQL
- [ ] Test with malicious inputs: `'; DROP TABLE--`, `' OR '1'='1`
- [ ] Category and description fields are sanitized

### 2. Data Encryption
- [ ] Sensitive data is encrypted at rest
- [ ] Encryption key is NOT hardcoded
- [ ] Encryption key stored in .env file
- [ ] .env file is in .gitignore
- [ ] Using strong encryption (AES-128 minimum via Fernet)
- [ ] Encrypted data cannot be read without key
- [ ] Encryption/decryption maintains data integrity

### 3. Input Validation
- [ ] All numeric inputs validated before use
- [ ] Date inputs validated for correct format
- [ ] Amount inputs reject negative values where inappropriate
- [ ] Maximum amount limits enforced (prevent overflow)
- [ ] Special characters handled safely
- [ ] Null/empty inputs handled gracefully
- [ ] String length limits enforced

### 4. File System Security
- [ ] Database file has restricted permissions
- [ ] Database files not committed to git (in .gitignore)
- [ ] .env file not committed to git
- [ ] No sensitive data in source code
- [ ] Backup files are also secured

### 5. Error Handling
- [ ] Error messages don't expose:
  - File paths
  - Database schema details
  - Encryption keys
  - Stack traces (in production)
- [ ] Errors are logged appropriately
- [ ] User sees friendly error messages
- [ ] Application doesn't crash on errors

### 6. Authentication & Authorization
- [ ] No default passwords in code
- [ ] Passwords/keys not logged
- [ ] Session handling (if multi-user)
- [ ] User data isolation (if multi-user)

### 7. Data Integrity
- [ ] Transaction amounts maintain precision (no float errors)
- [ ] Calculations are accurate
- [ ] Data consistency maintained across operations
- [ ] No data loss on crashes
- [ ] Atomic transactions where needed

### 8. Code Security
- [ ] Dependencies are up-to-date
- [ ] No known vulnerabilities in dependencies
- [ ] Code doesn't use eval() or exec()
- [ ] No hardcoded credentials
- [ ] Sensitive data cleared from memory when no longer needed

## Common Vulnerabilities to Test

### SQL Injection Patterns
```
'; DROP TABLE transactions; --
' OR '1'='1
1; UPDATE transactions SET amount=0; --
' UNION SELECT * FROM users; --
```

### XSS Patterns (if web interface added)
```
<script>alert('xss')</script>
<img src=x onerror=alert('xss')>
```

### Path Traversal Patterns
```
../../../etc/passwd
..\\..\\..\\windows\\system32
```

### Null Byte Injection
```
\x00
%00
```

### Integer Overflow
```
999999999999999999999
-999999999999999999999
```

## Security Best Practices

### Encryption
- Use cryptography library's Fernet (AES-128)
- Generate keys using Fernet.generate_key()
- Store keys in environment variables
- Never commit keys to version control

### Database
- Always use parameterized queries
- Validate all inputs before database operations
- Use transactions for multi-step operations
- Regular backups of database

### Input Validation
- Whitelist approach (allow known good, reject rest)
- Validate type, length, format, range
- Sanitize before storage
- Re-validate after retrieval

### Error Handling
- Log errors for debugging (but not sensitive data)
- Show generic messages to users
- Handle all exceptions gracefully
- Test error paths thoroughly

## Testing Priority Levels

### P0 (Critical - Must Test)
- SQL injection prevention
- Data encryption
- Input validation for amounts
- Database file security

### P1 (High - Should Test)
- Error message information leakage
- File permission security
- Decimal precision in calculations
- Data integrity

### P2 (Medium - Good to Test)
- Performance with large datasets
- Concurrent access handling
- Recovery from corruption
- Unicode handling

## Security Review Schedule
- [ ] Before initial release
- [ ] After any database changes
- [ ] After any input handling changes
- [ ] After dependency updates
- [ ] Monthly security review

## Incident Response Plan
If a security issue is found:
1. Assess severity and impact
2. Document the vulnerability
3. Create a fix
4. Test the fix thoroughly
5. Update all tests
6. Review for similar issues
7. Update this checklist

## Resources
- OWASP Top 10: https://owasp.org/www-project-top-ten/
- Python Security Best Practices
- SQLite Security Guidelines
- Cryptography Library Documentation
