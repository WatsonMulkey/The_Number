# Deployment Status

**Last Updated:** December 28, 2024, 11:00 PM
**Status:** PWA Infrastructure Deployed, Onboarding Fix Pending

---

## Quick Status

| Component | Status | Version/Commit | Notes |
|-----------|--------|----------------|-------|
| **Production Frontend** | ✅ Live | Old build (pre-532f649) | PWA infrastructure working |
| **Production Backend** | ✅ Live | Includes bcrypt fix | Fly.io healthy |
| **Local Changes** | ⚠️ Uncommitted build | frontend/dist/ | Onboarding fix built, not uploaded |
| **Git** | ⚠️ Ahead | 6 commits ahead of origin | commit 532f649 not pushed |

---

## Production Deployment Details

### Frontend (foil.engineering/TheNumber)

**Location:** Namecheap `public_html/TheNumber/`
**Last Deployed:** December 28, 2024, ~3:00 PM
**Deployed By:** User (manual upload via Namecheap File Manager)

**What's Live:**
- ✅ PWA manifest (`manifest.webmanifest`)
- ✅ Service worker (`sw.js`, `workbox-3896e580.js`, `registerSW.js`)
- ✅ App icons (`icon-192.png`, `icon-512.png`)
- ✅ Vue 3 app bundle (`assets/index-0FdJLjdT.js`)
- ✅ Vuetify styles (`assets/index-BGnUAbG3.css`)

**Known Issues:**
- ❌ Onboarding flow: Authenticated users see registration form (step 0) instead of budget setup (step 1)
  - **Root Cause:** Onboarding component doesn't check auth state on mount
  - **Fixed In:** Commit 532f649 (local only, not deployed)
  - **Impact:** Users must click "Get Started" button after registration

**Files on Server:**
```
/public_html/TheNumber/
├── index.html
├── manifest.webmanifest
├── registerSW.js
├── sw.js
├── workbox-3896e580.js
├── icon-192.png
├── icon-512.png
└── assets/
    ├── index-0FdJLjdT.js
    ├── index-BGnUAbG3.css
    ├── materialdesignicons-webfont-*.woff2
    └── ... (other assets)
```

### Backend (the-number-budget.fly.dev)

**Platform:** Fly.io
**Region:** ord (Chicago)
**Last Deployed:** December 28, 2024, ~8:00 PM
**Deployed Via:** `flyctl deploy`

**Current State:**
- ✅ Health endpoint: `{"status":"healthy","encryption_configured":true,"auth_configured":true}`
- ✅ Database: Encrypted SQLite on 1GB persistent volume at `/data/budget.db`
- ✅ Authentication: JWT with 30-day tokens
- ✅ CORS: Configured for `https://foil.engineering` and localhost

**Dependencies:**
- ✅ bcrypt==4.2.1 (fixed - compatible with passlib 1.7.4)
- ✅ DB_ENCRYPTION_KEY (secret)
- ✅ JWT_SECRET_KEY (secret)
- ✅ CORS_ORIGINS (configured)

**Last Commit:** Includes bcrypt version fix in requirements.txt

---

## Local Changes (Not Deployed)

### Built But Not Uploaded

**Location:** `C:\Users\watso\Dev\frontend\dist\`
**Built:** December 28, 2024, 10:17 AM
**Contains:** Onboarding fix (commit 532f649)

**New Files (vs production):**
```diff
Modified:
  assets/index-DSO3C520.js  (was index-0FdJLjdT.js)
  assets/index-BDh4gtm_.css (was index-BGnUAbG3.css)

Unchanged:
  manifest.webmanifest
  sw.js, workbox-*.js, registerSW.js
  icon-192.png, icon-512.png
```

**Changes in Build:**
- ✅ Onboarding.vue: Added `onMounted()` hook to skip step 0 if authenticated
- ✅ Import added: `import { ref, computed, onMounted } from 'vue'`
- ✅ Logic: Checks `authStore.isAuthenticated` on mount, sets `currentStep.value = 1`

### Git Status

**Branch:** main
**Remote Status:** 6 commits ahead of origin/main (not pushed)
**Latest Local Commit:** 532f649 "Fix onboarding flow: Skip account creation when user is authenticated"

**Commits Not Pushed:**
1. 532f649 - Fix onboarding flow
2. 78cbc4a - Add PWA infrastructure
3. 58aa4e5 - Configure frontend for production
4. 9cd6832 - Add Fly.io deployment config
5. c32d141 - Prepare for production deployment
6. 63bebc2 - Major UX improvements

**Uncommitted Changes:** None

---

## Deployment Procedures

### Deploy Frontend (Manual Process)

**When:** After testing locally and committing to git

**Steps:**
1. Build frontend: `cd frontend && npm run build`
2. Verify build: `ls -lh frontend/dist/`
3. Access Namecheap File Manager (foil.engineering)
4. Navigate to `public_html/TheNumber/`
5. **Delete ONLY:** `assets/` folder, `index.html`, `registerSW.js`
6. **Upload from `frontend/dist/`:** All deleted files/folders
7. **DO NOT touch:** `manifest.webmanifest`, `sw.js`, `workbox-*.js`, `icon-*.png` (unless they changed)
8. Verify: Visit https://foil.engineering/TheNumber
9. Check: Browser console for errors
10. **Update this file** with new deployment info

**Rollback:**
- Keep a backup of the previous `assets/` folder before deploying
- Re-upload old files if new deployment breaks

### Deploy Backend

**When:** After testing locally and committing to git

**Steps:**
1. Commit changes: `git add . && git commit -m "..."`
2. Deploy: `flyctl deploy`
3. Check health: `curl https://the-number-budget.fly.dev/health`
4. View logs: `flyctl logs`
5. **Update this file** with deployment timestamp

**Rollback:**
```bash
# Get previous deployment ID
flyctl releases

# Rollback to previous release
flyctl releases rollback <release-id>
```

---

## Testing Checklist

### Before Deploying Frontend

- [ ] Run `npm run build` successfully
- [ ] Test locally with `npm run preview`
- [ ] Check no TypeScript errors in components
- [ ] Verify manifest and service worker files exist
- [ ] Check icon files (192x192, 512x512)
- [ ] Commit all changes to git

### After Deploying Frontend

- [ ] Visit https://foil.engineering/TheNumber
- [ ] Check browser console (F12) - no errors
- [ ] Verify manifest loads (Network tab)
- [ ] Verify service worker registers (Application tab)
- [ ] Test user flow: Register → Onboard → Add Expense
- [ ] Check PWA installability (Mobile browsers)

### Before Deploying Backend

- [ ] Run tests: `pytest`
- [ ] Check requirements.txt versions
- [ ] Verify secrets are set: `flyctl secrets list`
- [ ] Test locally: `uvicorn api.main:app --reload`
- [ ] Commit all changes to git

### After Deploying Backend

- [ ] Health check: `curl https://the-number-budget.fly.dev/health`
- [ ] Check logs: `flyctl logs`
- [ ] Test API endpoints from frontend
- [ ] Verify database encryption working
- [ ] Check CORS headers in Network tab

---

## Environment Configuration

### Frontend (.env.production)

```env
VITE_API_URL=https://the-number-budget.fly.dev
```

### Backend (Fly.io Secrets)

```bash
# View secrets (values hidden)
flyctl secrets list

# Set secret
flyctl secrets set SECRET_NAME=value

# Current secrets:
# - DB_ENCRYPTION_KEY
# - JWT_SECRET_KEY
# - CORS_ORIGINS=http://localhost:5173,http://localhost:5174,https://foil.engineering
```

---

## URLs

| Service | URL | Purpose |
|---------|-----|---------|
| Production Frontend | https://foil.engineering/TheNumber | User-facing PWA |
| Production Backend | https://the-number-budget.fly.dev | API server |
| Backend Health | https://the-number-budget.fly.dev/health | Status check |
| Backend API Docs | https://the-number-budget.fly.dev/docs | FastAPI Swagger UI |
| Fly.io Dashboard | https://fly.io/dashboard | Backend management |
| Namecheap cPanel | (User access) | Frontend file management |

---

## Production Issues Log

### Active Issues

1. **WCAG Accessibility Violations (CRITICAL)**
   - **Severity:** HIGH - Blocks public release
   - **Description:** Multiple WCAG AA contrast failures, mobile usability issues
   - **Impact:** Users with low vision cannot read text; mobile users lose 25% screen width
   - **Details:** See `docs/UX_OVERHAUL_PLAN.md`
   - **Key Issues:**
     - Sage green + text-secondary = 2.5:1 contrast (need 4.5:1)
     - 96px navigation rail on mobile (wastes space)
     - No link back to foil.engineering
     - Missing safe-area CSS for notches
   - **Fix:** 3-phase implementation plan ready
   - **ETA:** Phase 1 implementation next session

2. **Onboarding Flow Bug**
   - **Severity:** Medium (workaround exists)
   - **Description:** After registration, user sees step 0 again instead of step 1
   - **Workaround:** Click "Get Started" button
   - **Fix:** Commit 532f649 (built, pending deployment)
   - **ETA:** Deploy with UX Phase 1 fixes

### Resolved Issues

1. ✅ **bcrypt Version Incompatibility** (Dec 28, 2024)
   - **Problem:** Password registration failed with "cannot be longer than 72 bytes"
   - **Cause:** bcrypt 5.0.0 incompatible with passlib 1.7.4
   - **Fix:** Pinned bcrypt==4.2.1 in requirements.txt
   - **Deployed:** Dec 28, 8:00 PM

2. ✅ **Missing PWA Infrastructure** (Dec 28, 2024)
   - **Problem:** App not installable, no offline support
   - **Cause:** Initial deployment missing manifest/service worker
   - **Fix:** Uploaded PWA files to production
   - **Deployed:** Dec 28, 3:00 PM

---

## Change History

| Date | Time | What Changed | Who | Notes |
|------|------|--------------|-----|-------|
| Dec 28 | 11:00 PM | Onboarding fix committed | Claude | Commit 532f649, not deployed |
| Dec 28 | 8:00 PM | Backend: bcrypt fix | Claude & User | flyctl deploy |
| Dec 28 | 3:00 PM | Frontend: PWA infrastructure | User | Manual upload |
| Dec 28 | 2:00 PM | Backend: Initial deploy | Claude & User | Fly.io setup |
| Dec 28 | 1:00 PM | Frontend: Initial deploy | User | Initial non-PWA version |

---

## Quick Reference Commands

```bash
# Frontend
cd frontend
npm run dev           # Local development
npm run build         # Production build
npm run preview       # Preview production build

# Backend
cd api
uvicorn main:app --reload  # Local development
pytest                     # Run tests
flyctl deploy              # Deploy to production
flyctl logs                # View logs
flyctl ssh console         # SSH into container

# Git
git status
git log -3 --oneline
git diff origin/main
git push origin main
```

---

**Instructions for Updating This File:**

1. **After Every Deployment:** Update timestamps, commit hashes, file lists
2. **When Issues Found:** Add to "Active Issues" with severity and workaround
3. **When Issues Fixed:** Move to "Resolved Issues" with fix details
4. **At Session End:** Update "Change History" and "Last Updated" timestamp
5. **Before Deployment:** Review this file to ensure understanding of current state

---

**Last Updated By:** Claude
**Next Update Due:** After next deployment or significant change
