# The Number - Private Beta Launch Roadmap

**Beta Context**: 5-10 friends, 1-week test, real financial data, quality-driven timeline

**Status**: v0.9.0 - Core features built, authentication working, needs deployment prep

---

## Executive Summary

This roadmap re-triages the 47 issues identified by senior-dev-skeptic for a **small private beta** context. Issues are prioritized into three tiers based on beta needs, not public launch requirements.

**Key Insight**: For 5-10 trusted friends testing for 1 week, many "production blockers" become post-beta tasks. Focus shifts to UX polish, data safety, and deployment basics.

---

## Priority Tier 1: BETA BLOCKERS (MUST FIX)
**Timeline**: 3-5 days | **Total Story Points**: 34

These issues MUST be resolved before inviting beta testers.

### 1.1 Critical Data Safety (13 points)
**Why Critical**: Users testing with real financial data, data loss unacceptable even for beta

#### Task 1.1.1: Database Backup System (5 points)
- **Issue**: SQLite local file with no backups (#6)
- **Beta Solution**: Automated daily backups to local directory + manual backup instructions
- **Implementation**:
  - Create `backups/` directory
  - Add cron job / scheduled task for daily SQLite backup
  - Create "Export All Data" feature in Settings UI
  - Add "Import Backup" feature for recovery
  - Document manual backup process for users
- **Acceptance Criteria**:
  - Daily automated backups run successfully
  - Users can manually export/import full database
  - Backup documentation in Settings view
- **Risk**: Medium - Backup systems can be fragile
- **Dependencies**: None
- **Deployer Guidance**: Create systemd timer (Linux) or Windows Task Scheduler job

#### Task 1.1.2: Encryption Key Persistence (3 points)
- **Issue**: Dangerous encryption key management (#12)
- **Beta Solution**: Ensure .env file is properly documented and backed up
- **Implementation**:
  - Update .env.example with clear warnings
  - Add startup check for DB_ENCRYPTION_KEY
  - Create "Setup Guide" documentation
  - Add health check endpoint that verifies encryption key
- **Acceptance Criteria**:
  - Server refuses to start without valid encryption key
  - Clear error message if key is missing
  - Documentation explains key backup importance
- **Risk**: Low - Simple validation check
- **Dependencies**: None

#### Task 1.1.3: JWT Secret Key Persistence (5 points)
- **Issue**: JWT secret regenerates on restart, invalidating all sessions (#3)
- **Beta Solution**: Move to environment variable, document in setup
- **Implementation**:
  - Update `api/auth.py`: Remove fallback generation, require env var
  - Add `JWT_SECRET_KEY` to .env.example
  - Generate secure key in setup documentation
  - Add startup validation check
- **Acceptance Criteria**:
  - Server refuses to start without JWT_SECRET_KEY
  - Existing tokens remain valid after server restart
  - Setup docs include key generation command
- **Risk**: Low - Simple config change
- **Dependencies**: None
- **File**: `C:\Users\watso\Dev\api\auth.py` lines 21-23

---

### 1.2 Critical UX Issues (8 points)
**Why Critical**: Beta testers (some with UX backgrounds) will notice broken features immediately

#### Task 1.2.1: Fix "Money In" Feature (5 points)
- **Issue**: "Money In" transaction recording broken (#16)
- **Current Status**: Backend exists, frontend integration missing
- **Implementation**:
  - Debug transaction creation endpoint
  - Verify frontend API call to `/api/transactions`
  - Test transaction persistence
  - Verify transaction appears in Dashboard
- **Acceptance Criteria**:
  - User can record positive "Money In" transactions
  - Transactions persist across sessions
  - Transactions affect "The Number" calculation
  - UI provides success/error feedback
- **Risk**: Medium - May reveal calculation bugs
- **Dependencies**: None
- **Files**: `C:\Users\watso\Dev\api\main.py` (lines 497-529)

#### Task 1.2.2: Add Frontend Input Validation (3 points)
- **Issue**: Missing client-side validation (#11)
- **Beta Solution**: Add basic validation to all forms
- **Implementation**:
  - Add Vuetify validation rules to all v-text-field components
  - Validate: amount > 0, text length limits, required fields
  - Add visual feedback for invalid input
  - Match backend validation rules
- **Acceptance Criteria**:
  - All forms show validation errors before submission
  - Clear error messages guide user corrections
  - Validation matches backend rules
- **Risk**: Low - Straightforward implementation
- **Dependencies**: None
- **Files**: All Vue components with forms

---

### 1.3 Deployment Essentials (8 points)
**Why Critical**: First-time deployer needs working infrastructure

#### Task 1.3.1: Production CORS Configuration (3 points)
- **Issue**: CORS only allows localhost (#5)
- **Beta Solution**: Configure for deployment domain
- **Implementation**:
  - Add `CORS_ORIGINS` to .env
  - Update `api/main.py` to use environment variable
  - Support both localhost (dev) and production domain
  - Document in deployment guide
- **Acceptance Criteria**:
  - Frontend can connect from production domain
  - Localhost still works for development
  - CORS errors don't appear in console
- **Risk**: Low - Simple configuration
- **Dependencies**: None
- **File**: `C:\Users\watso\Dev\api\main.py` lines 46-53

#### Task 1.3.2: Basic Deployment Guide (5 points)
- **Issue**: First-time solo deployer needs step-by-step guidance
- **Beta Solution**: Create comprehensive deployment documentation
- **Implementation**:
  - Document free tier options (Railway, Render, Fly.io)
  - Step-by-step deployment for chosen platform
  - Environment variable configuration
  - Database file persistence setup
  - Health check verification steps
  - Troubleshooting common issues
- **Deliverable**: `DEPLOYMENT_GUIDE.md`
- **Acceptance Criteria**:
  - Complete deploy-from-scratch instructions
  - Working health check endpoint
  - Successfully deployed test instance
- **Risk**: Medium - Deployment always has surprises
- **Dependencies**: 1.3.1 (CORS)

---

### 1.4 Critical Security (5 points)
**Why Critical**: Even for trusted beta, basic security is non-negotiable

#### Task 1.4.1: Remove Debug Logging (2 points)
- **Issue**: Debug logs expose user data (#8)
- **Beta Solution**: Remove all debug logging of sensitive data
- **Implementation**:
  - Search codebase for `print()`, `sys.stderr.write()`
  - Remove or redact sensitive data from logs
  - Replace with proper logging levels (INFO/ERROR only in prod)
  - Configure log level via environment variable
- **Acceptance Criteria**:
  - No user data in production logs
  - Errors still logged for debugging
  - Log level configurable via env var
- **Risk**: Low - Simple search and replace
- **Dependencies**: None
- **File**: `C:\Users\watso\Dev\api\main.py` lines 151-159, 193

#### Task 1.4.2: Password Reset Flow (3 points)
- **Issue**: No password reset mechanism (#10)
- **Beta Solution**: Admin-assisted manual reset for beta
- **Implementation**:
  - Create admin script: `reset_user_password.py`
  - Script prompts for username, generates new hash
  - Document process in admin guide
  - Post-beta: Build email-based self-service
- **Acceptance Criteria**:
  - Admin can reset any user's password via script
  - User can log in with new password
  - Process documented
- **Risk**: Low - Simple script
- **Dependencies**: None
- **Deliverable**: `scripts/reset_user_password.py`

---

## Priority Tier 2: POST-BETA PRIORITIES (BEFORE PUBLIC LAUNCH)
**Timeline**: 1-2 weeks after beta | **Total Story Points**: 55

Fix these based on beta feedback before public/paid launch.

### 2.1 PWA Implementation (13 points)
**Issues**: #1 - No PWA manifest, service worker, or icons

#### Task 2.1.1: PWA Manifest & Icons (5 points)
- Generate app icons (multiple sizes: 192x192, 512x512)
- Create `manifest.json` with app metadata
- Add to `index.html`
- Test "Add to Home Screen" on mobile

#### Task 2.1.2: Service Worker (8 points)
- Implement offline-first service worker
- Cache strategy for app shell
- Background sync for transactions when offline
- Update notification system
- **Risk**: High - Service workers are complex

---

### 2.2 Production Infrastructure (21 points)

#### Task 2.2.1: Replace In-Memory Rate Limiting (5 points)
- **Issue**: #4 - Rate limiter fails with multiple server instances
- **Solution**: Redis-based rate limiting
- **Beta Rationale**: Single server for 5-10 users doesn't need this

#### Task 2.2.2: HTTPS Enforcement (3 points)
- **Issue**: #7 - No HTTPS enforcement
- **Solution**: Add middleware to redirect HTTP to HTTPS
- **Beta Rationale**: Use platform's built-in HTTPS (Railway/Render provide free SSL)

#### Task 2.2.3: Exported File Cleanup (5 points)
- **Issue**: #14 - Exported files never cleaned up
- **Solution**: Scheduled cleanup job, temp file expiration
- **Implementation**:
  - Move exports to `/tmp` with TTL
  - Daily cleanup cron job
  - Track file creation timestamps

#### Task 2.2.4: Database Migration to PostgreSQL (8 points)
- **Why**: SQLite not ideal for multi-user production
- **Solution**: Migrate to PostgreSQL with automated backups
- **Beta Rationale**: SQLite fine for 5-10 users, migrate before scale

---

### 2.3 Authentication Improvements (13 points)

#### Task 2.3.1: Token Refresh Mechanism (8 points)
- **Issue**: #9 - 30-day token expiry, no refresh
- **Solution**: Implement refresh tokens
- **Implementation**:
  - Add refresh token endpoint
  - Short-lived access tokens (15 min)
  - Long-lived refresh tokens (30 days)
  - Frontend automatic token refresh

#### Task 2.3.2: Self-Service Password Reset (5 points)
- **Issue**: #10 - No password reset (beta uses admin script)
- **Solution**: Email-based password reset flow
- **Requirements**: Email service (SendGrid/Mailgun), reset token system

---

### 2.4 GDPR Compliance (8 points)
**Issue**: #13 - No data deletion or export for compliance

#### Task 2.4.1: Account Deletion (5 points)
- Add "Delete Account" UI in Settings
- Cascade delete all user data
- Generate deletion confirmation report
- 30-day soft delete before permanent removal

#### Task 2.4.2: Data Export (3 points)
- "Export All My Data" generates JSON
- Includes all expenses, transactions, settings
- GDPR-compliant format with metadata

---

## Priority Tier 3: NICE TO HAVE (DEFER)
**Timeline**: Post-public launch | **Total Story Points**: 30+

### 3.1 Gumroad Integration (13 points)
- **Issue**: #2 - No license validation
- **Beta Rationale**: Beta is free, testers get lifetime access
- **Implementation**: OAuth flow, license checking, payment webhook

### 3.2 Advanced Security (17+ points)
- Route guards (#15)
- API error boundaries (#17)
- Account lockout after failed logins
- 2FA support
- Session management UI
- Security audit logging

### 3.3 Enhanced UX Features
- Onboarding tutorial improvements
- Advanced reporting/analytics
- Budget templates
- Multi-currency support
- Recurring expense automation

---

## Beta Testing Protocol

### Pre-Beta Checklist
- [ ] All Priority 1 tasks completed
- [ ] Deployed to production environment
- [ ] Health check passing
- [ ] Test user account created
- [ ] Backup system verified
- [ ] Rollback plan documented

### Beta Week Activities
1. **Day 0**: Send invites with setup instructions
2. **Days 1-2**: Monitor for critical bugs, quick fixes if needed
3. **Days 3-5**: Collect UX feedback via external mechanism
4. **Days 6-7**: Analyze feedback, triage Priority 2 tasks

### Success Metrics
- All 5-10 users successfully onboard
- No data loss incidents
- Core workflow ("The Number" calculation) works reliably
- Collect 3+ actionable UX improvements per user

### Beta Feedback Collection
- Create Google Form or Notion page for structured feedback
- Categories: Bugs, UX Confusion, Feature Requests, General
- Weekly check-in with testers

---

## Risk Assessment

### HIGH RISK
1. **First deployment** - Expect surprises, plan 2x time estimate
2. **Service worker** (Tier 2) - Complex, defer to post-beta
3. **Database backups** - Test restore process before beta

### MEDIUM RISK
1. **"Money In" feature fix** - May reveal calculation logic bugs
2. **Production environment** - Free tier limitations unknown
3. **Data migrations** - SQLite → PostgreSQL tricky

### LOW RISK
1. Most configuration changes (CORS, env vars)
2. Frontend validation
3. Debug log removal

---

## Deployment Platform Recommendations

### Option 1: Railway (RECOMMENDED for first-timers)
**Pros**:
- Simple git-push deployment
- Free tier: $5 credit/month (plenty for beta)
- Auto HTTPS
- Easy environment variables
- File persistence with volumes

**Setup Time**: 2-3 hours

### Option 2: Render
**Pros**:
- Similar to Railway
- Free tier (with limitations)
- Good documentation

**Cons**:
- Free tier spins down after inactivity

### Option 3: Fly.io
**Pros**:
- Excellent free tier
- Better performance

**Cons**:
- Steeper learning curve
- Requires Dockerfile

---

## Estimated Timeline

### Sprint 1: Beta Blockers (5 days)
- **Day 1**: Data safety (1.1.1, 1.1.2, 1.1.3) - 13 points
- **Day 2**: UX fixes (1.2.1, 1.2.2) - 8 points
- **Day 3**: Security (1.4.1, 1.4.2) - 5 points
- **Day 4**: Deployment prep (1.3.1, 1.3.2) - 8 points
- **Day 5**: Testing, bug fixes, buffer

**Total**: 34 story points in 5 days

### Beta Week (7 days)
- Monitor, support users, collect feedback
- Quick bug fixes as needed

### Sprint 2: Post-Beta (10 days)
- Implement Priority 2 tasks based on beta learnings
- 55 points ÷ 5.5 points/day = 10 days

---

## Story Point Estimation Guide

- **1 point**: 1-2 hours (config change, simple script)
- **3 points**: Half day (feature enhancement, validation)
- **5 points**: Full day (new feature, complex fix)
- **8 points**: 2 days (service worker, auth refactor)
- **13 points**: 3+ days (PWA, major migration)

---

## First-Time Deployer Quick Start

1. **Choose Platform**: Railway (recommended)
2. **Create Account**: Sign up with GitHub
3. **Prepare Repository**:
   - Create `.env` with all required keys
   - Ensure `.env` in `.gitignore`
   - Push to GitHub
4. **Deploy**:
   - Click "New Project" → "Deploy from GitHub"
   - Select repository
   - Add environment variables in Railway dashboard
   - Set start command: `uvicorn api.main:app --host 0.0.0.0 --port $PORT`
5. **Verify**:
   - Visit `your-app.railway.app/health`
   - Should return `{"status": "healthy"}`
6. **Deploy Frontend**:
   - Build: `cd frontend && npm run build`
   - Serve: Use Railway static site or separate deployment

---

## Support Resources

### During Beta
- **Response Time**: Within 4 hours for critical bugs
- **Communication**: Dedicated Slack/Discord channel
- **Office Hours**: 2 scheduled Q&A sessions during beta week

### Documentation
- Setup guide for users
- Troubleshooting FAQ
- Known issues list (updated daily during beta)

---

## Post-Beta Decision Points

After 1-week beta, evaluate:

1. **Data Loss**: Any incidents? → Prioritize backup/restore improvements
2. **UX Friction**: Where did users struggle? → Adjust Priority 2 order
3. **Performance**: Slow for 10 users? → May need infrastructure upgrades
4. **Feature Gaps**: What did users request most? → New backlog items

---

## Appendix: Issue Reference

### Original 47 Issues (Re-triaged)

**Tier 1 (Beta Blockers)**: 7 issues
- #3, #5, #6, #8, #10, #12, #16 + deployment guidance + "Money In" fix

**Tier 2 (Pre-Public Launch)**: 10 issues
- #1, #2, #4, #7, #9, #11, #13, #14, #15, #17

**Tier 3 (Defer)**: 30 issues
- All remaining "nice to have" issues

---

## Success Criteria

**Beta Launch Ready**:
- All Tier 1 tasks complete
- Successfully deployed to production
- At least 1 test user can complete full workflow
- Data backup system tested with restore
- Health monitoring in place

**Public Launch Ready**:
- All Tier 2 tasks complete
- 0 critical bugs from beta
- Performance tested at 50+ concurrent users
- Email-based password reset working
- GDPR compliance implemented

---

**Last Updated**: 2025-12-26
**Version**: 1.0 (Beta Launch Plan)
**Next Review**: After beta week completion
