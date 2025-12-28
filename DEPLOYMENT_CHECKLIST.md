# Deployment Checklist for foil.engineering/TheNumber

## Production URL
- **Frontend**: https://foil.engineering/TheNumber
- **API**: (your API endpoint URL)
- **Contact**: watson@foil.engineering

---

## Required Environment Variables

### On Your Production Server:

```bash
# CRITICAL: Database Encryption Key
# Generate with: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
DB_ENCRYPTION_KEY=your_generated_key_here

# CRITICAL: JWT Secret for Authentication
# Generate with: python -c "import secrets; print(secrets.token_urlsafe(32))"
JWT_SECRET_KEY=your_generated_secret_here

# CORS Origins - REQUIRED FOR PRODUCTION
# Use HTTPS in production!
CORS_ORIGINS=https://foil.engineering

# Optional: Database path (if using persistent volume)
# DB_PATH=/app/data/budget.db
```

---

## Pre-Deployment Checklist

### Security (CRITICAL):
- [ ] Generated and set `DB_ENCRYPTION_KEY`
- [ ] Generated and set `JWT_SECRET_KEY`
- [ ] Set `CORS_ORIGINS=https://foil.engineering`
- [ ] Backed up encryption keys securely (password manager + offline backup)
- [ ] Using HTTPS (not HTTP) in production

### Application:
- [ ] Tested registration flow locally
- [ ] Tested onboarding flow locally
- [ ] Verified CSV/Excel exports work
- [ ] Tested with real budget data
- [ ] Confirmed database backups work

### Known Limitations for Beta:
- [ ] Password reset requires admin intervention (security issue identified)
- [ ] Email notifications not configured yet
- [ ] Rate limiting is per-process (will reset on deploy)

---

## Post-Deployment Testing

Once deployed, test these critical flows:

1. **Registration**:
   - Visit https://foil.engineering/TheNumber
   - Create new account
   - Should redirect to onboarding

2. **Onboarding**:
   - Complete budget setup
   - Add expenses
   - Should land on dashboard with "The Number" visible

3. **Data Export**:
   - Go to Settings
   - Download CSV export
   - Download Excel export
   - Verify data is correct

4. **CORS Test**:
   - Open browser console (F12)
   - Should see NO CORS errors
   - API calls should succeed

---

## Namecheap Email Setup (For Future)

For password reset emails via watson@foil.engineering:

1. SMTP Server: `mail.privateemail.com`
2. Port: 587 (TLS) or 465 (SSL)
3. Username: `watson@foil.engineering`
4. Password: (your Namecheap email password)

**Not implemented yet** - currently password resets require admin intervention.

---

## Emergency Contacts

- **Developer**: Watson Mulkey
- **Email**: watson@foil.engineering
- **Issues**: Report via email for beta testing

---

## Rollback Plan

If deployment fails:

1. Revert to previous version
2. Check environment variables are set correctly
3. Verify CORS_ORIGINS matches your domain
4. Check backend logs for errors
5. Ensure database encryption key matches your backup

---

## What to Monitor

After deployment, watch for:

- CORS errors in browser console
- 500 errors in API (check backend logs)
- Authentication failures (JWT issues)
- Database encryption errors
- Slow response times

---

## Next Steps After Beta

1. Fix password reset security issue (implement email)
2. Add proper rate limiting (Redis or similar)
3. Set up automated backups
4. Add monitoring/alerting
5. Consider adding refresh tokens for better security
