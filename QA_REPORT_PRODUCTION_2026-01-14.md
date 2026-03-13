# Production QA Test Report - The Number

**Test Date:** January 14, 2026
**Production URL:** https://foil.engineering/TheNumber
**Tester:** Automated QA with Playwright
**Overall Success Rate:** 77.8% (7 passed / 9 total tests)

---

## Executive Summary

The Number PWA is live and functional, with the frontend successfully loading and displaying the onboarding flow. However, there are **2 CRITICAL ISSUES** preventing the app from fully functioning:

### Critical Issues Found:
1. **CORS Configuration Error** - API requests are being blocked
2. **API Health Endpoint Missing** - Backend health check returns 404

### Positive Findings:
- Frontend loads successfully (200 OK)
- PWA infrastructure is working (manifest + service worker)
- UI renders correctly on desktop and mobile
- Responsive design works well
- Onboarding screen displays properly

---

## Test Results by Category

### ✅ PASSED Tests (7/9)

#### 1. Initial Page Load
- **Status:** PASS
- **Details:** Status 200 OK
- **Screenshot:** screenshots/01_initial_load.png
- **Notes:** Page loads successfully with no HTTP errors

#### 2. PWA Elements
- **Status:** PASS
- **Details:** Manifest present, Service Worker support detected
- **Notes:** PWA infrastructure is correctly configured

#### 3. Page Title & Branding
- **Status:** PASS
- **Title:** "The Number - Budget Tracker"
- **Notes:** Proper branding and page title

#### 4. Critical UI Elements
- **Status:** PASS
- **Details:** App container (#app) renders successfully
- **Screenshot:** screenshots/02_app_loaded.png

#### 5. App State Detection
- **Status:** PASS
- **Current State:** Onboarding flow
- **Screenshot:** screenshots/03_app_state.png
- **Notes:** App correctly shows onboarding for new users

#### 6. Network Errors
- **Status:** PASS
- **Details:** No HTTP network failures detected
- **Notes:** All static assets load successfully

#### 7. Mobile Responsiveness
- **Status:** PASS
- **Test Viewport:** 375x667 (iPhone SE)
- **Screenshot:** screenshots/04_mobile_view.png
- **Notes:** UI adapts well to mobile viewport, bottom navigation visible

---

### ❌ FAILED Tests (2/9)

#### 1. Console Errors (CRITICAL)
- **Status:** FAIL
- **Severity:** CRITICAL - App cannot function properly
- **Error Count:** 4 errors detected

**Console Errors:**
```
[1] Failed to load resource: the server responded with a status of 404 ()

[2] Access to XMLHttpRequest at 'https://the-number-budget.fly.dev/api/number'
    from origin 'https://www.foil.engineering' has been blocked by CORS policy:
    No 'Access-Control-Allow-Origin' header is present on the requested resource.

[3] Failed to load dashboard: je

[4] Failed to load resource: net::ERR_FAILED
```

**Root Cause Analysis:**
The API backend (`https://the-number-budget.fly.dev`) is not configured to accept requests from `https://www.foil.engineering` (note the "www" prefix). The frontend is being served from the www subdomain, but CORS is likely only configured for the non-www domain.

**Impact:**
- Users cannot load their budget number
- Dashboard data cannot be fetched
- App is essentially non-functional beyond the onboarding UI

#### 2. API Health Check (CRITICAL)
- **Status:** FAIL
- **Severity:** CRITICAL
- **Expected:** 200 OK from /api/health endpoint
- **Actual:** 404 Not Found
- **API URL Tested:** https://the-number-budget.fly.dev/api/health

**Root Cause:**
The backend API does not have a `/api/health` endpoint, or it's located at a different path.

**Impact:**
- Cannot verify backend status programmatically
- Health monitoring/alerts will not work
- Unclear if backend is actually running

---

## Visual Analysis

### Desktop View (1920x1080)
The onboarding screen displays correctly with:
- Clean, centered layout
- Clear branding: "The Number - A different way to budget"
- Well-designed account creation form
- Informational blue banner explaining privacy and data usage
- Form fields: Username, Email (Optional), Password, Confirm Password
- "Login Instead" link for existing users
- Bottom navigation rail visible (Number, Expenses, Spending, Settings)

### Mobile View (375x667 - iPhone SE)
- Layout adapts well to narrow viewport
- All text remains readable
- Form fields are appropriately sized
- Bottom navigation compresses correctly
- No horizontal scrolling required
- Touch targets appear adequately sized

---

## Critical Issues - Action Required

### Issue #1: CORS Configuration (BLOCKING)

**Problem:**
The production frontend is served from `https://www.foil.engineering/TheNumber` (with www), but the backend CORS is likely only configured for `https://foil.engineering` (without www).

**Current Backend CORS (Suspected):**
```python
CORS_ORIGINS=https://foil.engineering
```

**Required Fix:**
```python
# In backend .env or fly.toml
CORS_ORIGINS=https://foil.engineering,https://www.foil.engineering
```

**Where to Fix:**
- File: `api/main.py` (CORS middleware configuration)
- Or: Fly.io environment variables
- Or: Backend `.env` file

**Verification Steps:**
1. Update CORS origins to include both www and non-www domains
2. Redeploy backend to Fly.io
3. Test by visiting https://www.foil.engineering/TheNumber
4. Check browser console - CORS errors should be gone
5. Verify API calls succeed

**Alternative Solution:**
Configure DNS to redirect www to non-www (or vice versa) to maintain a single canonical domain.

---

### Issue #2: Missing Health Endpoint (NON-BLOCKING)

**Problem:**
The `/api/health` endpoint returns 404, making it impossible to monitor backend status.

**Recommended Implementation:**
```python
# In api/main.py
@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }
```

**Benefits:**
- Enables automated health monitoring
- Useful for uptime monitoring services
- Helps diagnose backend issues quickly
- Required for production-grade systems

**Priority:** Medium (non-blocking but highly recommended)

---

## Recommendations

### Immediate Actions (Required for functionality)
1. **Fix CORS configuration** - Add www subdomain to allowed origins
2. **Verify backend is running** - Check Fly.io dashboard
3. **Test after CORS fix** - Verify all API calls succeed
4. **Consider DNS redirect** - Standardize on www or non-www

### Nice to Have (Non-blocking)
1. **Add health endpoint** - Implement `/api/health` for monitoring
2. **Add error tracking** - Integrate Sentry or similar for production error monitoring
3. **Add analytics** - Track user flow through onboarding
4. **Test PWA installation** - Verify "Add to Home Screen" works on iOS/Android

### Testing Recommendations
1. **Manual Test:** Try creating an account after CORS fix
2. **Manual Test:** Verify onboarding flow completes
3. **Manual Test:** Test on real mobile devices (iOS Safari, Android Chrome)
4. **Automated Test:** Set up CI/CD integration of this QA script
5. **Load Test:** Verify backend can handle concurrent users

---

## Screenshots Reference

All screenshots saved to: `screenshots/`

1. **01_initial_load.png** - Desktop view, initial page load
2. **02_app_loaded.png** - App rendered with onboarding
3. **03_app_state.png** - Onboarding state detected
4. **04_mobile_view.png** - Mobile responsive layout (375x667)

---

## Test Environment

**Browser:** Chromium (Playwright build v1200)
**User Agent:** Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36
**Viewport (Desktop):** 1920x1080
**Viewport (Mobile):** 375x667
**Network:** Standard connection (no throttling)

---

## Next Steps

1. **CRITICAL:** Fix CORS configuration on backend (add www subdomain)
2. Redeploy backend to Fly.io with updated CORS settings
3. Re-run this QA test to verify fixes: `python qa_test_production.py`
4. Test manually on real devices after CORS fix
5. Monitor error logs for 24 hours post-fix
6. Consider implementing health endpoint for monitoring

---

## Conclusion

The Number PWA has successfully deployed to production with proper PWA infrastructure, responsive design, and correct UI rendering. However, a critical CORS misconfiguration is preventing the app from communicating with the backend API, making it non-functional for end users.

**Estimated Time to Fix:** 10-15 minutes (CORS config + redeploy)
**Risk Level:** Low (simple configuration change)
**Testing Required:** Manual verification + re-run automated QA

Once the CORS issue is resolved, the app should be fully functional for beta users.

---

**Report Generated:** 2026-01-14
**Test Automation:** qa_test_production.py
**Results JSON:** qa_test_results.json
