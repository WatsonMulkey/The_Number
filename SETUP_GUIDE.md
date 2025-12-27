# Setup Guide for The Number

Complete setup instructions for getting The Number running locally or in production.

---

## Initial Setup (Local Development)

### 1. Clone Repository

```bash
git clone <your-repository-url>
cd the-number
```

### 2. Install Dependencies

**Backend (Python):**
```bash
cd api
pip install -r requirements.txt
```

**Frontend (Node.js):**
```bash
cd frontend
npm install
```

### 3. Generate Encryption Keys

The Number requires two critical encryption keys that must be generated and stored securely.

**Generate Database Encryption Key:**
```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

**Generate JWT Secret:**
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 4. Configure Environment Variables

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and paste your generated keys:
   ```bash
   DB_ENCRYPTION_KEY=<paste database encryption key here>
   JWT_SECRET_KEY=<paste JWT secret here>
   ```

3. Verify your `.env` file looks like this:
   ```
   DB_ENCRYPTION_KEY=gAAAAABh...actual_key_here...XYZ=
   JWT_SECRET_KEY=abc123...actual_secret_here...xyz789
   CORS_ORIGINS=http://localhost:5173
   LOG_LEVEL=INFO
   ```

### 5. **CRITICAL: Backup Your Keys**

⚠️ **WITHOUT THESE KEYS, ALL USER DATA IS PERMANENTLY LOST** ⚠️

You MUST backup these keys immediately:

1. **Save `.env` to Password Manager**
   - 1Password, Bitwarden, LastPass, etc.
   - Create a secure note with both keys
   - Title it "The Number - Production Keys"

2. **Create Offline Backup**
   - USB drive stored in safe location
   - OR printed copy in physical safe/lockbox
   - Keep separate from main computer

3. **Verify `.env` is in `.gitignore`**
   ```bash
   # Check that .env is ignored
   git status
   # .env should NOT appear in untracked files
   ```

4. **Test Restore Process**
   - Try restoring keys from backup
   - Ensure you can access them when needed

### 6. Start the Application

**Terminal 1 - Backend:**
```bash
cd api
python -m uvicorn main:app --reload --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

**Access the app:**
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/api/docs

### 7. Verify Installation

1. **Check Health Endpoint:**
   ```bash
   curl http://localhost:8000/health
   ```

   Should return:
   ```json
   {
     "status": "healthy",
     "encryption_configured": true,
     "auth_configured": true
   }
   ```

2. **Register Test User:**
   - Open http://localhost:5173
   - Click "Register"
   - Create test account
   - Complete onboarding flow

3. **Verify Data Persistence:**
   - Create some test data
   - Restart backend server
   - Verify data is still there

---

## Production Setup (Railway Deployment)

See [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md) for complete production deployment instructions.

**Quick checklist:**
- [ ] Generate new production keys (NEVER reuse dev keys)
- [ ] Configure Railway environment variables
- [ ] Set up database volume for persistence
- [ ] Configure CORS for production domain
- [ ] Test backup/restore process
- [ ] Set LOG_LEVEL=INFO (no debug logging)

---

## Security Best Practices

### Environment Variables

✅ **DO:**
- Generate unique keys for each environment (dev, staging, prod)
- Store keys in password manager
- Keep offline backup of production keys
- Use `.env.example` as template (no real keys)
- Set restrictive file permissions: `chmod 600 .env` (Unix/Mac)

❌ **DON'T:**
- Commit `.env` to git (check `.gitignore`)
- Share keys via email, Slack, or messaging
- Reuse development keys in production
- Store keys in plain text files without encryption
- Use default/example keys

### Key Rotation

If you need to rotate keys (security breach, employee departure, etc.):

**Database Encryption Key:**
1. ⚠️ **Cannot be rotated easily** - all data is encrypted with this key
2. Would require decrypting all data and re-encrypting with new key
3. For beta: If compromised, start fresh with new key (acceptable data loss)
4. For production: Contact support for key rotation procedure

**JWT Secret:**
1. Generate new secret:
   ```bash
   python -c "import secrets; print(secrets.token_urlsafe(32))"
   ```
2. Update `.env` with new JWT_SECRET_KEY
3. Restart server
4. All users will be logged out (must re-login)
5. This is safe and doesn't affect data

**Testing JWT Persistence:**

To verify that JWT tokens persist across server restarts:

```bash
# Run the automated test
python tests/test_session_persistence.py
```

This test confirms that:
- JWT_SECRET_KEY is loaded from `.env` (not randomly generated)
- User sessions remain valid after server restart
- Tokens don't expire when server restarts

**Why This Matters:**
- Users stay logged in across server deployments
- No session invalidation during maintenance windows
- Predictable user experience

---

## Troubleshooting

### "Missing required environment variables"

**Error:**
```
RuntimeError: Missing required environment variables: DB_ENCRYPTION_KEY, JWT_SECRET_KEY
Copy .env.example to .env and fill in all values.
```

**Solution:**
1. Ensure `.env` file exists in project root
2. Check that both keys are set (no "REQUIRED_CHANGE_THIS")
3. Verify no extra spaces around `=` in `.env`
4. Restart server after updating `.env`

### "Database encryption key not configured"

**Error during API calls:**
```json
{
  "detail": "Database encryption key not configured"
}
```

**Solution:**
- Check health endpoint: `curl http://localhost:8000/health`
- If `encryption_configured: false`, your DB_ENCRYPTION_KEY is not loading
- Verify `.env` is in the correct directory (project root)
- Check file is named `.env` exactly (not `.env.txt`)

### "Invalid encryption key"

**Error:**
```
cryptography.fernet.InvalidToken
```

**Causes:**
1. Wrong encryption key (using different key than data was encrypted with)
2. Corrupted database file
3. Key was changed after data was created

**Solution:**
- Restore correct key from backup
- If key is lost: database is unrecoverable (start fresh)
- For development: Delete `api/budget.db` and regenerate

### Health check shows "degraded"

**Response:**
```json
{
  "status": "degraded",
  "encryption_configured": false,
  "auth_configured": true
}
```

**Solution:**
- One or more critical env vars is missing
- Check which is `false` and add that key to `.env`
- Restart server

---

## File Structure

```
the-number/
├── .env                    # YOUR KEYS (DO NOT COMMIT)
├── .env.example           # Template with placeholders
├── .gitignore            # Ensures .env is not committed
├── SETUP_GUIDE.md        # This file
├── api/
│   ├── main.py           # FastAPI app (validates keys on startup)
│   ├── auth.py           # Uses JWT_SECRET_KEY
│   ├── budget.db         # SQLite database (encrypted)
│   └── requirements.txt
├── src/
│   ├── database.py       # Uses DB_ENCRYPTION_KEY
│   └── calculator.py
└── frontend/
    ├── src/
    └── package.json
```

---

## Next Steps

After successful setup:

1. **For Development:**
   - Read [CONTRIBUTING.md](./CONTRIBUTING.md) for development guidelines
   - Check [ROADMAP.md](./ROADMAP.md) for planned features
   - Review [THE_NUMBER_BRAND_GUIDELINES.md](./THE_NUMBER_BRAND_GUIDELINES.md)

2. **For Beta Testing:**
   - Read [BETA_TESTING_GUIDE.md](./BETA_TESTING_GUIDE.md)
   - Set up feedback form/channel
   - Document any issues encountered

3. **For Production Deployment:**
   - Follow [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md)
   - Set up monitoring and alerts
   - Test backup/restore process
   - Configure automated backups

---

## Getting Help

**Issues during setup:**
- Check troubleshooting section above
- Review error messages carefully
- Verify all steps were completed in order

**Still stuck:**
- Open GitHub issue with error details
- Include relevant log output (redact any keys!)
- Describe what you've tried

---

**Last Updated:** 2025-12-26
**Version:** 1.0 (Beta Launch Preparation)
