# Pre-Launch Checklist for The Number Beta

**Quick reference for beta launch readiness**

---

## Sprint Progress Tracker

### Day 1: Data Safety ✓
- [ ] Task 1.1.2: Encryption Key Persistence (3 pts)
  - [ ] Update `.env.example` with required vars
  - [ ] Add startup validation in `api/main.py`
  - [ ] Update health check endpoint
  - [ ] Create `SETUP_GUIDE.md`
  - [ ] Test: Server fails without keys
  - [ ] Test: Health check verifies keys

- [ ] Task 1.1.3: JWT Secret Persistence (5 pts)
  - [ ] Remove fallback in `api/auth.py`
  - [ ] Require JWT_SECRET_KEY from env
  - [ ] Create session persistence test
  - [ ] Test: Token survives restart
  - [ ] Update documentation

- [ ] Task 1.1.1 Prep: Backup System Design (2 pts)
  - [ ] Create `backups/` directories
  - [ ] Write `scripts/backup_database.py`
  - [ ] Test backup creation

**Day 1 Total: 10 points**

---

### Day 2: Backups + UX ✓
- [ ] Task 1.1.1 Complete: Backup System (3 pts)
  - [ ] Add backup endpoints to API
  - [ ] Add Settings UI for backups
  - [ ] Setup automated backups (platform)
  - [ ] Create restore script
  - [ ] Test: Manual backup works
  - [ ] Test: Automated backup runs
  - [ ] Test: Restore process works

- [ ] Task 1.2.1: Fix "Money In" Feature (5 pts)
  - [ ] Test transaction endpoint directly
  - [ ] Verify frontend integration
  - [ ] Fix calculation update logic
  - [ ] Decide: How should income affect budget?
  - [ ] Test: User can record income
  - [ ] Test: Income persists
  - [ ] Test: "The Number" updates correctly

**Day 2 Total: 8 points**

---

### Day 3: Security + Validation ✓
- [ ] Task 1.4.1: Remove Debug Logging (2 pts)
  - [ ] Search for all print/debug statements
  - [ ] Remove lines 151-159 in `api/main.py`
  - [ ] Remove line 193 in `api/main.py`
  - [ ] Replace with proper logging
  - [ ] Configure log level via env var
  - [ ] Test: No sensitive data in logs

- [ ] Task 1.2.2: Frontend Validation (3 pts)
  - [ ] Add validation rules to all forms
  - [ ] Update Onboarding.vue
  - [ ] Update Dashboard.vue
  - [ ] Update Settings.vue
  - [ ] Update AuthModal.vue
  - [ ] Test: All forms validate before submit

- [ ] Task 1.4.2: Password Reset Script (3 pts)
  - [ ] Create `scripts/reset_user_password.py`
  - [ ] Create `ADMIN_GUIDE.md`
  - [ ] Test: Reset password for test user
  - [ ] Test: User can login with new password

**Day 3 Total: 8 points**

---

### Day 4: Deployment Ready ✓
- [ ] Task 1.3.1: Production CORS (3 pts)
  - [ ] Add CORS_ORIGINS to `.env.example`
  - [ ] Update CORS middleware in `api/main.py`
  - [ ] Test: CORS from production domain
  - [ ] Test: CORS still works for localhost

- [ ] Task 1.3.2: Deployment Guide (5 pts)
  - [ ] Write comprehensive `DEPLOYMENT_GUIDE.md`
  - [ ] Document Railway setup
  - [ ] Document environment variables
  - [ ] Document volume configuration
  - [ ] Document frontend deployment
  - [ ] Document troubleshooting steps
  - [ ] Test: Deploy to Railway test instance
  - [ ] Test: Health check passes
  - [ ] Test: User registration works
  - [ ] Test: Database persists

**Day 4 Total: 8 points**

---

### Day 5: Testing & Buffer ✓
- [ ] Full System Testing
  - [ ] New user onboarding flow
  - [ ] Data persistence testing
  - [ ] Error handling testing
  - [ ] Cross-browser testing
  - [ ] Performance testing
  - [ ] Mobile testing

- [ ] Bug Fixes (as discovered)

- [ ] Final Documentation
  - [ ] SETUP_GUIDE.md complete
  - [ ] DEPLOYMENT_GUIDE.md complete
  - [ ] ADMIN_GUIDE.md complete
  - [ ] BETA_TESTING_GUIDE.md complete
  - [ ] USER_GUIDE.md (if needed)

**Day 5 Total: Buffer (no new features)**

---

## Code Changes Reference

### Files to Modify

#### Backend
- [ ] `api/main.py`
  - Add startup validation (lines ~43-52)
  - Update health check (lines ~85-95)
  - Add backup endpoints (new section)
  - Update CORS configuration (lines 46-53)
  - Remove debug logging (lines 151-159, 193)
  - Add proper logging configuration

- [ ] `api/auth.py`
  - Remove JWT secret fallback (line 21)
  - Add required env var check (lines 21-26)

- [ ] `.env.example`
  - Add DB_ENCRYPTION_KEY with instructions
  - Add JWT_SECRET_KEY with instructions
  - Add CORS_ORIGINS
  - Add LOG_LEVEL

#### Frontend
- [ ] `frontend/src/views/Settings.vue`
  - Add backup section UI
  - Add validation to expense forms

- [ ] `frontend/src/views/Dashboard.vue`
  - Fix "Money In" integration
  - Add validation to transaction form

- [ ] `frontend/src/components/Onboarding.vue`
  - Add validation to all steps

- [ ] `frontend/src/components/AuthModal.vue`
  - Add validation to login/register forms

#### Scripts
- [ ] `scripts/backup_database.py` (create new)
- [ ] `scripts/restore_database.py` (create new)
- [ ] `scripts/reset_user_password.py` (create new)

#### Documentation
- [ ] `SETUP_GUIDE.md` (create new)
- [ ] `DEPLOYMENT_GUIDE.md` (create new)
- [ ] `ADMIN_GUIDE.md` (create new)
- [ ] `BETA_TESTING_GUIDE.md` (created)
- [ ] `BETA_LAUNCH_ROADMAP.md` (created)
- [ ] `SPRINT_PLAN_BETA.md` (created)

---

## Deployment Checklist

### Pre-Deployment
- [ ] All code changes committed
- [ ] All tests passing locally
- [ ] `.env.production` created (not committed)
- [ ] Production secrets generated
- [ ] Railway account created
- [ ] GitHub repository accessible

### Railway Setup
- [ ] Project created in Railway
- [ ] Service connected to GitHub repo
- [ ] Environment variables configured:
  - [ ] DB_ENCRYPTION_KEY
  - [ ] JWT_SECRET_KEY
  - [ ] CORS_ORIGINS
  - [ ] LOG_LEVEL=INFO
- [ ] Volume mounted at `/app/data`
- [ ] Start command set: `uvicorn api.main:app --host 0.0.0.0 --port $PORT`
- [ ] First deployment successful

### Post-Deployment
- [ ] Health check returns 200: `curl https://your-app.railway.app/health`
- [ ] Can register test user
- [ ] Can complete onboarding
- [ ] Can record transaction
- [ ] "The Number" calculates correctly
- [ ] Data persists after server restart
- [ ] Backup system works

### Frontend Deployment
- [ ] Frontend deployed (Railway or Vercel)
- [ ] VITE_API_URL configured
- [ ] Can access app at public URL
- [ ] Can connect to backend API
- [ ] No CORS errors in console

---

## Testing Checklist

### Critical Path (Must Work)
- [ ] User can register account
- [ ] User can log in
- [ ] User can complete onboarding
- [ ] User can add expenses
- [ ] User can see "The Number"
- [ ] "The Number" is calculated correctly
- [ ] User can record spending
- [ ] Spending updates "The Number"
- [ ] Data persists across sessions
- [ ] User can log out and back in

### Important Features (Should Work)
- [ ] User can record "Money In"
- [ ] User can view transaction history
- [ ] User can edit expenses
- [ ] User can delete expenses
- [ ] User can export data
- [ ] User can create backup
- [ ] All forms validate input
- [ ] Error messages are helpful

### Nice to Have (Bonus)
- [ ] Works on mobile browser
- [ ] Works on multiple browsers
- [ ] UI is responsive
- [ ] No console errors
- [ ] Fast page loads

---

## Security Checklist

### Configuration
- [ ] JWT_SECRET_KEY from environment (not hardcoded)
- [ ] DB_ENCRYPTION_KEY from environment (not hardcoded)
- [ ] CORS limited to production domains
- [ ] HTTPS enforced (Railway auto)
- [ ] Log level set to INFO in production

### Code Review
- [ ] No debug logging of sensitive data
- [ ] No secrets in code
- [ ] No secrets in git history
- [ ] Input validation on all forms
- [ ] SQL injection prevention (parameterized queries)
- [ ] XSS prevention (sanitization in place)

### Access Control
- [ ] All API endpoints require authentication (except login/register)
- [ ] User can only access their own data
- [ ] Rate limiting on login/register endpoints

---

## Beta Launch Checklist

### Documentation Ready
- [ ] BETA_TESTING_GUIDE.md complete
- [ ] Feedback form created (Google Form/Typeform)
- [ ] Support channel set up (Discord/Slack/Email)
- [ ] Known issues documented

### Infrastructure Ready
- [ ] Production app deployed and tested
- [ ] Database backups working
- [ ] Monitoring/logging accessible
- [ ] Rollback plan documented

### Communication Ready
- [ ] Beta invite email drafted
- [ ] Contains app URL
- [ ] Contains setup instructions
- [ ] Contains link to BETA_TESTING_GUIDE.md
- [ ] Contains feedback form link
- [ ] Contains support channel link
- [ ] Office hours scheduled

### Support Ready
- [ ] Support channel monitored
- [ ] Response plan for critical bugs
- [ ] Admin tools ready (password reset script)
- [ ] Backup/restore procedures documented

---

## Go/No-Go Decision

**Criteria for Launch**:
- [ ] All Priority 1 tasks complete (34 story points)
- [ ] Critical path tested and working
- [ ] Security checklist passed
- [ ] Documentation complete
- [ ] Support infrastructure ready
- [ ] Comfortable with beta testers using real data

**If NOT Ready**:
- Document blocking issues
- Estimate time to resolve
- Communicate delay to beta testers
- Set new target date

**If READY**:
- Send beta invites
- Monitor support channel closely
- Log all feedback systematically
- Plan daily check-ins during beta week

---

## Beta Week Daily Checklist

### Day 0 (Launch Day)
- [ ] Send beta invites
- [ ] Post in support channel welcome message
- [ ] Monitor for first user registrations
- [ ] Respond quickly to any blockers
- [ ] Log all feedback in central doc

### Days 1-2 (Early Beta)
- [ ] Check support channel 3x daily
- [ ] Review server logs for errors
- [ ] Track user onboarding success rate
- [ ] Fix critical bugs immediately
- [ ] Document all reported issues

### Days 3-5 (Mid Beta)
- [ ] Collect structured feedback
- [ ] Identify patterns in UX feedback
- [ ] Triage reported bugs
- [ ] Plan fixes for Priority 2 sprint
- [ ] Check in with users who've gone quiet

### Days 6-7 (Late Beta)
- [ ] Final feedback push
- [ ] Analyze all collected feedback
- [ ] Prioritize post-beta improvements
- [ ] Thank beta testers
- [ ] Schedule retrospective

---

## Metrics to Track

### Technical Metrics
- **Uptime**: Target 99%+ during beta week
- **Response Time**: API calls < 500ms
- **Error Rate**: < 1% of requests
- **Database Size**: Monitor growth

### User Metrics
- **Registration Rate**: X of Y invitees register
- **Onboarding Completion**: X% complete setup
- **Daily Active Users**: X users/day
- **Retention**: X% return next day

### Feedback Metrics
- **Bug Reports**: Count and severity
- **UX Issues**: Count and frequency
- **Feature Requests**: Count and popularity
- **Net Satisfaction**: Would you recommend?

---

## Emergency Procedures

### Critical Bug Discovered
1. **Assess Severity**:
   - Can't register/login? CRITICAL
   - Data loss? CRITICAL
   - Wrong calculations? CRITICAL
   - UI glitch? Not critical

2. **Immediate Action**:
   - Post in support channel (acknowledge)
   - Reproduce locally
   - Fix if possible within 2 hours
   - Deploy fix
   - Verify fix in production
   - Follow up with affected users

3. **Can't Fix Quickly**:
   - Document workaround if possible
   - Communicate timeline
   - Consider pausing new signups
   - Extreme: Roll back deployment

### Server Down
1. Check Railway status
2. Check logs for errors
3. Verify environment variables
4. Restart service if needed
5. Check database volume mounted
6. Communicate status to users

### Data Loss Incident
1. STOP - don't make it worse
2. Identify scope (one user or all?)
3. Attempt restore from backup
4. Document what happened
5. Communicate to affected users
6. Implement safeguards

---

## Post-Beta Tasks

### Immediate (Week After)
- [ ] Sprint retrospective
- [ ] Analyze all feedback
- [ ] Prioritize Priority 2 tasks
- [ ] Fix critical bugs
- [ ] Update roadmap based on learnings

### Before Public Launch
- [ ] Complete Priority 2 tasks (55 points)
- [ ] Implement most-requested features
- [ ] Polish UX based on feedback
- [ ] Performance optimization
- [ ] Final security audit

---

## Success Criteria

**Beta Success Looks Like**:
- 80%+ of invitees register
- 60%+ complete onboarding
- 40%+ use for multiple days
- 0 data loss incidents
- 5+ actionable UX improvements identified
- 3+ quality feature requests
- Would recommend: 70%+

**Ready for Public Launch When**:
- All Priority 2 tasks complete
- All critical bugs fixed
- UX polished based on feedback
- Performance acceptable
- Documentation complete
- Payment integration working (Gumroad)
- Confident in product quality

---

**Last Updated**: 2025-12-26
**Sprint Start**: [Date]
**Beta Launch**: [Date]
**Public Launch**: [Date]

---

## Quick Commands Reference

```bash
# Generate encryption key
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"

# Generate JWT secret
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Run backend locally
cd C:\Users\watso\Dev
source .env  # or `set` on Windows
python -m uvicorn api.main:app --reload

# Run frontend locally
cd frontend
npm run dev

# Create backup
python scripts/backup_database.py

# Reset user password
python scripts/reset_user_password.py

# Deploy to Railway
git push origin main
# (if connected to Railway auto-deploy)

# Check production health
curl https://your-app.railway.app/health

# View Railway logs
railway logs

# Test API endpoint
curl -X POST https://your-app.railway.app/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"test","password":"testpass123"}'
```

---

## Contact Info

**Support Channels**:
- Email: [your-email]
- Discord: [invite-link]
- GitHub Issues: [repo-url]

**Beta Coordinator**: [Your Name]
**Emergency Contact**: [Phone/Email]

---

Good luck with the beta launch! 🚀
