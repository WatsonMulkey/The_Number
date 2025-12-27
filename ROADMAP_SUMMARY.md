# The Number - Beta Roadmap Summary

**One-page visual guide to beta launch priorities**

---

## The Big Picture

```
Current State: v0.9.0 - Core features built, needs deployment prep
        ↓
    5 DAYS OF WORK (Sprint 1)
        ↓
Beta Launch: 5-10 friends, 1 week testing
        ↓
    COLLECT FEEDBACK
        ↓
    10 DAYS OF WORK (Sprint 2)
        ↓
Public Launch: Paid version with Gumroad
```

---

## Priority Tiers (Re-Triaged for Beta)

### 🔴 TIER 1: BETA BLOCKERS (Must Fix Now)
**Timeline**: 5 days | **Points**: 34

**Why**: Can't launch beta without these

| Priority | Issue | Points | Days | Risk |
|----------|-------|--------|------|------|
| 1 | JWT secret persistence (#3) | 5 | 1 | Low |
| 2 | Database backups (#6) | 5 | 1 | Med |
| 3 | Encryption key safety (#12) | 3 | 0.5 | Low |
| 4 | Fix "Money In" feature (#16) | 5 | 1 | Med |
| 5 | Frontend validation (#11) | 3 | 0.5 | Low |
| 6 | Remove debug logs (#8) | 2 | 0.5 | Low |
| 7 | Production CORS (#5) | 3 | 0.5 | Low |
| 8 | Deployment guide (new) | 5 | 1 | Med |
| 9 | Password reset script (#10) | 3 | 0.5 | Low |

---

### 🟡 TIER 2: POST-BETA (Fix Before Public)
**Timeline**: 10 days after beta | **Points**: 55

**Why**: Not needed for small beta, essential for public launch

| Priority | Issue | Points | Why Wait? |
|----------|-------|--------|-----------|
| A | PWA manifest & icons (#1) | 5 | Nice to have, not critical |
| B | Service worker offline (#1) | 8 | Complex, defer to post-beta |
| C | Redis rate limiting (#4) | 5 | Single server handles 10 users |
| D | HTTPS enforcement (#7) | 3 | Platform provides SSL |
| E | Token refresh (#9) | 8 | 30-day expiry fine for 1-week beta |
| F | Self-service password reset (#10) | 5 | Admin script works for beta |
| G | GDPR compliance (#13) | 8 | Not legally required for private beta |
| H | File cleanup (#14) | 5 | Not many exports in 1 week |
| I | PostgreSQL migration (new) | 8 | SQLite fine for 10 users |

---

### 🟢 TIER 3: NICE TO HAVE (Defer)
**Timeline**: After public launch | **Points**: 30+

**Why**: Not needed for launch, future enhancements

- Gumroad integration (#2) - Beta is free
- Route guards (#15) - Auth working, polish later
- Advanced error boundaries (#17)
- 30 other "nice to have" issues from senior-dev review

---

## Sprint 1 Daily Breakdown

```
Day 1: DATA SAFETY (13 points)
├─ Morning:   Encryption key persistence (3 pts)
├─ Afternoon: JWT secret persistence (5 pts)
└─ Evening:   Backup system design (2 pts)

Day 2: BACKUPS + UX (10 points)
├─ Morning:   Complete backup system (3 pts)
└─ Afternoon: Fix "Money In" feature (5 pts)

Day 3: SECURITY + VALIDATION (8 points)
├─ Morning:   Remove debug logging (2 pts)
└─ Afternoon: Validation + password reset (6 pts)

Day 4: DEPLOYMENT (8 points)
├─ Morning:   Production CORS config (3 pts)
└─ Afternoon: Deployment guide + deploy (5 pts)

Day 5: TESTING & BUFFER
└─ Full system testing, bug fixes, no new features
```

---

## Key Decisions Made

### ✅ What Changed from Senior-Dev Review?

**Original Assessment**: 7 blockers for "production launch"
**Beta Assessment**: 7 blockers for "beta launch" (different priorities)

#### Moved DOWN in Priority:
1. **PWA Implementation** (#1): Was blocker → Now Tier 2
   - Reason: Not needed for friends testing on web

2. **Gumroad Integration** (#2): Was blocker → Now Tier 3
   - Reason: Beta is free, testers get lifetime access

3. **Rate Limiting to Redis** (#4): Was blocker → Now Tier 2
   - Reason: In-memory works for single server, 10 users

4. **HTTPS Enforcement** (#7): Was blocker → Now Tier 2
   - Reason: Railway provides HTTPS automatically

#### Moved UP in Priority:
1. **Deployment Guide** (new): Added to Tier 1
   - Reason: First-time deployer needs step-by-step help

2. **"Money In" Fix** (#16): Was critical → Now blocker
   - Reason: Beta testers will definitely try this feature

#### Stayed Same:
1. **JWT Secret** (#3): Still blocker
   - Data safety non-negotiable

2. **Database Backups** (#6): Still blocker
   - Real financial data requires backups

3. **Encryption Keys** (#12): Still blocker
   - Prevent catastrophic data loss

---

## Risk Assessment

### 🔥 HIGH RISK (Plan Extra Time)
1. **First Deployment**: No production experience
   - Mitigation: Comprehensive guide, test instance first

2. **"Money In" Feature**: May reveal calculation bugs
   - Mitigation: Thorough testing, decide on calculation logic

3. **Backup/Restore**: Must work perfectly
   - Mitigation: Test restore before beta launch

### ⚠️ MEDIUM RISK (Monitor Closely)
1. **Production Environment**: Free tier limitations unknown
   - Mitigation: Railway has good free tier, can upgrade

2. **User Data Safety**: Real financial data in beta
   - Mitigation: Multiple backup systems, clear warnings

3. **Time Estimation**: First time doing many tasks
   - Mitigation: Buffer day built in, can cut scope

### ✅ LOW RISK (Should Be Fine)
- Configuration changes (CORS, env vars)
- Frontend validation (straightforward)
- Debug log removal (search and replace)
- Documentation writing (time-consuming but not risky)

---

## Success Metrics

### Sprint 1 Success:
- [ ] All 34 story points complete
- [ ] Deployed to production
- [ ] Test user completes full workflow
- [ ] Backups working and tested
- [ ] Ready for beta invites

### Beta Week Success:
- [ ] 80%+ invitees register
- [ ] 60%+ complete onboarding
- [ ] 0 data loss incidents
- [ ] 5+ actionable UX improvements
- [ ] Would recommend: 70%+

### Public Launch Ready:
- [ ] All Tier 2 tasks complete (55 points)
- [ ] All critical bugs fixed
- [ ] UX polished
- [ ] Gumroad payment working
- [ ] Confident in product quality

---

## What This Roadmap Doesn't Include

**Out of Scope for Beta**:
- Mobile apps (web-only)
- Advanced analytics/reporting
- Multi-user accounts (family sharing)
- Multi-currency support
- Recurring expense automation
- Budget templates
- AI features
- Third-party integrations

**These can be added post-launch based on user demand**

---

## Resource Requirements

### Time
- **Sprint 1**: 5 days (solo developer)
- **Beta Week**: 7 days (monitoring + support)
- **Sprint 2**: 10 days (post-beta improvements)
- **Total to Public Launch**: ~4 weeks

### Money
- **Railway Hosting**: $0-5/month (free tier likely sufficient)
- **Domain**: $12/year (optional for beta)
- **Email Service**: $0 (defer to Tier 2)
- **Total Beta Cost**: ~$5

### Skills Needed
- Python/FastAPI (have)
- Vue.js/Frontend (have)
- Basic DevOps (learning - deployment guide will help)
- SQL/Database (have)

---

## The Golden Rule for Beta

> **Better to launch with 80% polish to 5 friends than wait for 100% perfection**

Why this matters:
- Beta testers are forgiving (they're friends)
- Real user feedback > speculation
- Can fix issues quickly for small user base
- Builds momentum and accountability
- Prevents over-engineering

---

## Next Steps (Right Now)

1. **Read**: `SPRINT_PLAN_BETA.md` for detailed tasks
2. **Start**: Day 1, Task 1.1.2 (Encryption Key Persistence)
3. **Track**: Use `LAUNCH_CHECKLIST.md` to mark progress
4. **Reference**: `BETA_LAUNCH_ROADMAP.md` for full context

---

## Quick Reference

### Key Files Created
- `BETA_LAUNCH_ROADMAP.md` - Comprehensive roadmap with all 47 issues triaged
- `SPRINT_PLAN_BETA.md` - Detailed day-by-day execution plan
- `LAUNCH_CHECKLIST.md` - Task-by-task checklist with code snippets
- `BETA_TESTING_GUIDE.md` - Guide for beta testers
- `ROADMAP_SUMMARY.md` - This file (visual overview)

### Key Locations
- Backend: `C:\Users\watso\Dev\api\`
- Frontend: `C:\Users\watso\Dev\frontend\`
- Scripts: `C:\Users\watso\Dev\scripts\` (to be created)
- Backups: `C:\Users\watso\Dev\backups\` (to be created)
- Docs: `C:\Users\watso\Dev\*.md`

### Key Commands
```bash
# Start backend
python -m uvicorn api.main:app --reload

# Start frontend
cd frontend && npm run dev

# Run backup
python scripts/backup_database.py

# Deploy
git push origin main
```

---

## Estimation Accuracy

**Story Points**:
- 1 pt = 1-2 hours
- 3 pts = 4 hours (half day)
- 5 pts = 8 hours (full day)
- 8 pts = 2 days

**Sprint 1**: 34 points ÷ 7 points/day = ~5 days
**Sprint 2**: 55 points ÷ 5.5 points/day = ~10 days

**Confidence Level**: 70%
- Have done similar tasks before
- First deployment adds uncertainty
- Buffer day accounts for unknowns

---

## When Things Go Wrong

### If You're Behind Schedule:
1. **Cut Scope**: Move lower priority Tier 1 items to Tier 2
   - Example: Automated backups → Manual only
2. **Simplify**: Reduce feature scope
   - Example: Basic error messages instead of perfect ones
3. **Ask for Help**: Developer communities, documentation

### If Beta Has Issues:
1. **Quick Fixes**: Critical bugs get immediate patches
2. **Workarounds**: Document temporary solutions
3. **Communication**: Keep testers informed
4. **Delay if Needed**: Better to delay than launch broken

### If You're Ahead of Schedule:
1. **Don't Add Scope**: Resist temptation to add features
2. **More Testing**: Extra testing always valuable
3. **Polish**: Improve error messages, documentation
4. **Start Tier 2**: Get head start on post-beta tasks

---

**Remember**: This is a BETA for FRIENDS. They want to help you succeed. They'll forgive rough edges. Focus on core workflow working reliably.

---

**Last Updated**: 2025-12-26
**Created by**: Scrum Master / Project Manager Agent
**Version**: 1.0

Good luck! 🚀
