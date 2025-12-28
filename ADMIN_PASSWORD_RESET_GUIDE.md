# Admin Password Reset Guide

## Overview

This guide is for **admin use only** to manually reset user passwords when needed. Password reset functionality has been removed from the UI for beta testing due to security concerns.

**Contact for Help**: watson@foil.engineering

---

## When to Use This

- User forgets their password
- User is locked out of their account
- User requests a password change for security reasons

---

## Method 1: Using the Admin Script (Recommended)

### Prerequisites

1. Access to the server/computer where the database is stored
2. Python 3 installed
3. The encryption key (`DB_ENCRYPTION_KEY`) from your `.env` file

### Steps

1. **SSH into your server** (or open terminal if local):
   ```bash
   cd /path/to/your/app
   ```

2. **Run the password reset script**:
   ```bash
   python reset_password.py
   ```

3. **Follow the prompts**:
   ```
   Enter username: john_doe
   Enter new password: NewSecurePass123!
   Confirm new password: NewSecurePass123!

   ✓ Password updated successfully for user: john_doe
   ```

4. **Notify the user** that their password has been changed and provide them with the new temporary password.

5. **Recommend they change it** after logging in (Settings page).

---

## Method 2: Direct Database Update (Advanced)

### Prerequisites

- SQLite3 installed
- Database encryption key
- Python with required packages

### Steps

1. **Generate a bcrypt hash** of the new password:
   ```bash
   python -c "from passlib.context import CryptContext; pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto'); print(pwd_context.hash('NewPassword123!'))"
   ```

   This will output something like:
   ```
   $2b$12$XYZ123...abcdef
   ```

2. **Open the database**:
   ```bash
   sqlite3 api/budget.db
   ```

3. **Update the user's password**:
   ```sql
   UPDATE users
   SET hashed_password = '$2b$12$XYZ123...abcdef'
   WHERE username = 'john_doe';
   ```

   **Important**: Replace `$2b$12$XYZ123...abcdef` with the actual hash from step 1!

4. **Verify the update**:
   ```sql
   SELECT username, created_at FROM users WHERE username = 'john_doe';
   ```

5. **Exit**:
   ```sql
   .quit
   ```

---

## Security Best Practices

### For Password Generation

Generate strong temporary passwords using:
```bash
python -c "import secrets; import string; chars = string.ascii_letters + string.digits + '!@#$%'; print(''.join(secrets.choice(chars) for _ in range(16)))"
```

This creates passwords like: `aB3!kM@9xQ#2pR%7`

### Password Requirements

Ensure temporary passwords meet these requirements:
- Minimum 8 characters
- At least one uppercase letter
- At least one lowercase letter
- At least one number
- Recommended: At least one special character

### After Reset

1. **Notify user immediately** via email (watson@foil.engineering)
2. **Provide temporary password** securely (not via email - use encrypted messaging or phone)
3. **Recommend immediate change** after login
4. **Log the reset** for security records

---

## Troubleshooting

### "User not found"
- Double-check the username spelling
- List all users to verify:
  ```bash
  sqlite3 api/budget.db "SELECT username FROM users;"
  ```

### "bcrypt error" or "hash doesn't match"
- Ensure you're using bcrypt, NOT SHA-256
- The hash should start with `$2b$`
- Verify passlib is installed: `pip install passlib[bcrypt]`

### "Database is locked"
- Stop the API server temporarily
- Try the reset again
- Restart the API server

### Script fails with "ModuleNotFoundError"
Install required packages:
```bash
pip install passlib[bcrypt] cryptography python-dotenv
```

---

## Example Session

```bash
$ python reset_password.py

=== Password Reset Tool ===

Enter username: sarah_jones
Enter new password: TempPass123!@#
Confirm new password: TempPass123!@#

Validating password...
✓ Password meets requirements

Updating password for user: sarah_jones...
✓ Password updated successfully!

The user can now log in with:
  Username: sarah_jones
  Password: TempPass123!@#

Remember to:
1. Notify the user securely
2. Recommend they change their password immediately
```

---

## Security Notes

**CRITICAL**:
- Never share the database encryption key
- Never commit passwords to git
- Always use bcrypt hashes (not SHA-256 or plain text)
- Keep a secure log of password resets for audit purposes
- Use secure channels to communicate temporary passwords

---

## Future Improvements

Once email integration is complete (using watson@foil.engineering with Namecheap):
- Users can reset their own passwords
- Automated email with reset token
- Time-limited reset links
- No admin intervention needed

**For now**: Manual resets are the secure approach for beta testing.

---

## Questions?

Contact: watson@foil.engineering
