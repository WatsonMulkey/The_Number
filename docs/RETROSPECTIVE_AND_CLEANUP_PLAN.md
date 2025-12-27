# Retrospective and Cleanup Plan
**Date:** 2025-12-26
**Focus:** Root cause analysis of recent issues + comprehensive codebase audit

---

## 1. ROOT CAUSE ANALYSIS: Recent Issues

### Issue #1: 404 on /api/auth Endpoints ⚠️ CRITICAL
**What happened:** Authentication endpoints returned 404 despite being defined in code
**Root cause:** Two `main.py` files in the repository:
- `/main.py` (old CLI entry point)
- `/api/main.py` (FastAPI backend)

Python's import system loaded the wrong file, causing uvicorn to start with the old CLI code instead of the API.

**Why it wasn't caught:**
- ❌ No file naming convention enforcement
- ❌ No CI/CD checks for conflicting filenames
- ❌ No integration tests that would catch missing endpoints

**Similar issues that might exist:**
- ✅ Checked: No other duplicate filenames (only `__init__.py`, which is normal)
- ⚠️ Found: `main_cli_old.py` still exists (renamed but not deleted)

---

### Issue #2: bcrypt Compatibility Error ⚠️ HIGH
**What happened:** `bcrypt 5.0.0` incompatible with `passlib`
**Root cause:** bcrypt was installed but NOT pinned in `requirements.txt`

**Why it wasn't caught:**
- ❌ bcrypt not listed in requirements.txt at all
- ❌ No version pinning strategy
- ❌ No dependency scanning/auditing

**Similar issues that might exist:**
- ⚠️ Other dependencies might be unpinned or have breaking changes

**Fix required:** Add `bcrypt==4.3.0` to requirements.txt

---

### Issue #3: Database ON CONFLICT Error ⚠️ HIGH
**What happened:** `ON CONFLICT(user_id, key)` failed because UNIQUE constraint didn't exist
**Root cause:** Migration code added `user_id` column but didn't add the UNIQUE constraint

**Why it wasn't caught:**
- SQLite limitation: Can't add constraints to existing tables via ALTER TABLE
- Migration code should have documented this limitation
- ❌ No migration tests

**Resolution:** Correctly resolved by deleting old database and recreating with proper schema

**Lessons learned:**
- SQLite migrations are limited - document when full recreate is needed
- Consider using Alembic or similar migration tool for production
- Always test migrations on a copy of production data

---

### Issue #4: Daily Spending Limit Ignored 🐛 MEDIUM
**What happened:** Frontend displayed wrong number when user chose daily spending limit mode
**Root cause:** `calculatedNumber` computed property had incorrect logic - ignored user input

**Why it wasn't caught:**
- ❌ No unit tests for computed properties
- ❌ No E2E tests for onboarding flow
- ❌ Manual QA didn't test this specific flow

---

### Issue #5: Budget Not Persisting After Login 🐛 UNKNOWN
**What happened:** User's budget configuration lost after logout/login
**Current status:** Backend works (test proves it), frontend issue suspected but not confirmed

**Investigation needed:**
- Frontend may not be calling `/api/budget/configure`
- Added debug logging to frontend onboarding
- **Action:** User needs to check browser console logs

---

## 2. CODEBASE AUDIT FINDINGS

### 🔴 CRITICAL: Repository Contamination
**Issue:** Unrelated projects mixed into The Number repository

**Unrelated directories found:**
```
foil-industries/          (unrelated branding project)
foil-industries-v2/       (unrelated branding project)
foil-mockups/             (unrelated branding project)
foil-option1/             (unrelated branding project)
foil-option2/             (unrelated branding project)
foil-option3/             (unrelated branding project)
resume-tailor/            (unrelated resume tool)
temp-bmad/                (temporary directory)
output/                   (generated files)
```

**Impact:**
- Repository bloat
- Confusing for contributors
- Git history polluted with unrelated commits
- Potential security issues if these contain credentials

**Recommendation:**
- IMMEDIATE: Add to `.gitignore`
- Move these to separate repositories
- Clean up git history if they were committed

---

### 🟠 HIGH: Root Directory Clutter
**Issue:** 20+ markdown files in project root

**Files found:**
```
AGENT_REVIEW_AND_RECOMMENDATIONS.md
API_LESSON.md
API_SECURITY_SPEC.md
API_TESTING_STRATEGY.md
AUTHENTICATION_DESIGN.md
BEST_PRACTICES.md
CODEBASE_REVIEW.md
DATABASE_MIGRATION_PLAN.md
FEATURE_BACKLOG.md
FRONTEND_SETUP.md
IMPORT_EXPENSES_GUIDE.md
ONBOARDING.md
ONBOARDING_DEMO.txt
PWA_IMPLEMENTATION_PLAN.md
QA_REPORT.md
QA_REPORT_ONBOARDING.md
TEST_COVERAGE_IMPROVEMENT.md
TEST_STRATEGY.md
TEST_STRATEGY_FRONTEND.md
THE_NUMBER_BRAND_GUIDELINES.md
... (and more)
```

**Recommendation:**
- Create `/docs` directory
- Move all documentation there
- Keep only README.md, CHANGELOG.md, LICENSE in root
- Update any hardcoded paths

---

### 🟠 HIGH: Dead Code and Temporary Files
**Files that should be deleted:**

```
main_cli_old.py                    (old CLI, renamed but not deleted)
fix_test_cleanup.py                (temporary debug script)
test_calc.py                       (temporary debug script)
test_onboarding_flow.py            (temporary debug script)
test_routes.py                     (temporary debug script)
nul                                (invalid Windows file - already attempted delete)
```

**Recommendation:** Delete all these files

---

### 🟡 MEDIUM: Missing Dependency Pinning
**Issue:** `bcrypt` not in requirements.txt

**Current requirements.txt:**
```txt
cryptography==41.0.7
pytest==7.4.3
python-dotenv==1.0.0
openpyxl==3.1.2
fastapi==0.124.4
uvicorn[standard]==0.38.0
pydantic==2.12.5
python-jose[cryptography]==3.5.0
passlib==1.7.4
python-multipart==0.0.20
slowapi==0.1.9
```

**Missing:**
- `bcrypt==4.3.0` (required by passlib)

**Recommendation:** Add missing dependency with version pin

---

### 🟡 MEDIUM: TODOs in Code
**Found:**
```
frontend/src/views/Dashboard.vue:149
  // TODO: Backend needs an endpoint to add money to fixed pool
```

**Assessment:** Legitimate TODO - feature not yet implemented

**Recommendation:**
- Create GitHub issue for this feature
- Link issue in comment
- Or implement the feature

---

### 🟢 LOW: Potential Over-Engineering
**Observation:** Multiple migration-related markdown docs but limited actual migration code

**Files:**
- DATABASE_MIGRATION_PLAN.md
- API_TESTING_STRATEGY.md (24KB)
- TEST_COVERAGE_IMPROVEMENT.md

**Assessment:** More planning docs than implementation

**Recommendation:**
- Focus on implementing rather than planning
- Consolidate overlapping docs

---

## 3. WHAT WENT WELL ✅

### Backend Design
- ✅ Proper authentication with JWT
- ✅ User data isolation working correctly
- ✅ Input sanitization implemented
- ✅ Rate limiting on auth endpoints
- ✅ CORS configured properly

### Database
- ✅ Encryption working correctly
- ✅ Foreign key constraints in place
- ✅ User scoping properly implemented

### Frontend
- ✅ Vue 3 + Vuetify setup clean
- ✅ Pinia state management
- ✅ Axios interceptors for auth
- ✅ Error boundaries

---

## 4. ANTI-PATTERNS TO AVOID

### ❌ Don't: Mix Multiple Projects in One Repo
- Leads to confusion and bloat
- Makes CI/CD complex
- Pollutes git history

### ❌ Don't: Leave Old Code "Just in Case"
- `main_cli_old.py` caused a production issue
- Either delete it or use git branches

### ❌ Don't: Skip Dependency Pinning
- bcrypt version issue could have been prevented
- Always pin dependencies in requirements.txt

### ❌ Don't: Add Columns Without Constraints in Migrations
- SQLite can't add constraints later
- Document when full recreate is needed

### ❌ Don't: Accumulate Temporary Debug Scripts
- test_*.py files in root are confusing
- Put tests in tests/ directory or delete them

---

## 5. CLEANUP PLAN (Prioritized)

### 🔴 PRIORITY 1: Critical Fixes (Do Immediately)

1. **Add bcrypt to requirements.txt**
   ```bash
   echo "bcrypt==4.3.0  # Required by passlib, v5.0+ incompatible" >> requirements.txt
   ```

2. **Delete conflicting/dead code**
   ```bash
   rm main_cli_old.py
   rm fix_test_cleanup.py
   rm test_calc.py
   rm test_onboarding_flow.py
   rm test_routes.py
   ```

3. **Add unrelated directories to .gitignore**
   ```bash
   echo -e "\n# Unrelated projects\nfoil-*/\nresume-tailor/\ntemp-*/\noutput/" >> .gitignore
   ```

### 🟠 PRIORITY 2: Important Cleanup (Do This Week)

4. **Organize documentation**
   ```bash
   mkdir -p docs
   mv *.md docs/  # except README.md and CHANGELOG.md
   mv docs/README.md .
   mv docs/CHANGELOG.md .
   ```

5. **Fix frontend debug issue**
   - Add console logging to onboarding (already done)
   - User needs to test and report browser console output
   - Fix based on findings

6. **Create .gitignore for Python/Node**
   - Add common Python patterns (__pycache__, *.pyc, venv/, .env)
   - Add common Node patterns (node_modules/, dist/, .vite/)

### 🟡 PRIORITY 3: Nice to Have (Do When Time Permits)

7. **Move unrelated projects out**
   - Create separate repos for foil-* projects
   - Remove from this repo entirely

8. **Set up proper test structure**
   ```bash
   mkdir -p tests/unit tests/integration tests/e2e
   mv tests/test_database_errors.py tests/unit/
   ```

9. **Implement the TODO feature**
   - Add endpoint to add money to fixed pool
   - Or remove the TODO if not needed

10. **Consider migration tool**
    - Evaluate Alembic for database migrations
    - Would prevent future constraint issues

---

## 6. METRICS & IMPACT

### Code Health Before Cleanup:
- ❌ 6 unrelated directories in repo
- ❌ 20+ docs in root directory
- ❌ 5 temporary test files in root
- ❌ 1 dead code file causing production bug
- ❌ 1 missing dependency in requirements.txt
- ⚠️ 1 TODO in codebase

### Expected After Cleanup:
- ✅ Clean repository structure
- ✅ All dependencies pinned
- ✅ No dead code
- ✅ Organized documentation
- ✅ Clear separation of concerns

### Estimated Effort:
- Priority 1: **15 minutes**
- Priority 2: **1-2 hours**
- Priority 3: **4-6 hours**

---

## 7. PREVENTION STRATEGIES

### To Prevent File Conflicts:
- [ ] Add pre-commit hook to check for duplicate filenames
- [ ] Document file naming conventions
- [ ] Use CI/CD to validate project structure

### To Prevent Version Issues:
- [ ] Always pin dependencies in requirements.txt
- [ ] Use `pip freeze > requirements.txt` to capture all deps
- [ ] Run `pip-audit` to check for known vulnerabilities
- [ ] Set up Dependabot or similar for automated updates

### To Prevent Migration Issues:
- [ ] Document SQLite limitations in migration code
- [ ] Test migrations on copy of prod data
- [ ] Consider Alembic for complex migrations
- [ ] Always backup database before migration

### To Prevent Frontend Bugs:
- [ ] Add unit tests for computed properties
- [ ] Add E2E tests for critical user flows (onboarding, login)
- [ ] Use TypeScript strict mode
- [ ] Add Vue DevTools for debugging

---

## 8. LESSONS FOR FUTURE

### ✅ What Worked:
1. **Incremental fixes** - Fixed issues one at a time
2. **Testing with curl** - Proved backend works independently
3. **Debug logging** - Console logs help identify frontend issues
4. **User feedback loop** - User caught issues in real usage

### ❌ What Didn't Work:
1. **Assuming without testing** - Should have tested migration on old DB
2. **Not documenting dependencies** - bcrypt should have been in requirements.txt
3. **Keeping old code** - main.py caused production issue

### 🎯 Apply to Next Sprint:
1. Add tests BEFORE merging features
2. Document all dependencies immediately
3. Delete code, don't rename it
4. Keep repository focused on one project
5. Organize files from day one

---

## CONCLUSION

The recent issues were all **preventable** with better practices:
- File conflicts → Better organization
- Version issues → Dependency pinning
- Migration gaps → SQLite limitations documented
- Frontend bugs → Unit tests
- Persistence issues → Integration tests

**The good news:** None of the issues are architectural problems. They're all fixable with better discipline and tooling.

**Priority actions:**
1. Clean up dead code (15 min)
2. Add bcrypt to requirements.txt (1 min)
3. Organize documentation (1 hour)
4. Fix frontend persistence issue (pending user feedback)

**Long term:**
- Set up CI/CD with linting, tests, and structure validation
- Implement E2E tests for critical flows
- Consider migration to Alembic for complex schema changes
