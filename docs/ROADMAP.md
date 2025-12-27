# The Number - Production Readiness Roadmap

**Document Version:** 1.0
**Last Updated:** December 16, 2025
**Status:** CRITICAL - Application is NOT production-ready

---

## Executive Summary

This roadmap consolidates findings from four independent code reviews:
- **QA Agent:** 50 issues (14 Critical, 17 High, 15 Medium, 4 Low)
- **Testing Agent:** Comprehensive Vitest test suite created
- **UI Engineer:** B+ grade with TypeScript, bundle size, and props concerns
- **Senior Dev Skeptic:** Production blockers including data integrity and security issues

### Critical Assessment

**Current State: ALPHA - NOT SAFE FOR PRODUCTION USE**

The application has fundamental flaws that will cause:
1. **Data Loss:** Transaction deletions do not persist to the database
2. **Security Exposure:** Zero authentication, hardcoded localhost URLs
3. **Runtime Failures:** Router history bug will break navigation in production
4. **Race Conditions:** Concurrent operations can corrupt state
5. **Poor Accessibility:** Multiple WCAG violations blocking users with disabilities

### Estimated Effort to Production-Ready

| Phase | Duration | Team Size | Priority |
|-------|----------|-----------|----------|
| P0: Critical Fixes | 2-3 weeks | 2-3 devs | IMMEDIATE |
| P1: Security & Core | 3-4 weeks | 2-3 devs | Within 30 days |
| P2: Quality & UX | 4-6 weeks | 2 devs | Within 90 days |
| P3: Polish & Scale | Ongoing | 1-2 devs | Continuous |

---

## Issue Inventory by Category

### 1. DATA INTEGRITY ISSUES (P0)

#### CRIT-001: Fake Transaction Delete (Data Loss)
**File:** `C:\Users\watso\Dev\frontend\src\views\Transactions.vue` (lines 174-184)
**Severity:** CRITICAL
**Impact:** User data loss

```typescript
// CURRENT CODE - DELETE ONLY REMOVES FROM LOCAL STATE
async function deleteTransaction(id: number) {
  if (!confirm('Are you sure you want to delete this transaction?')) return

  try {
    budgetStore.transactions = budgetStore.transactions.filter(txn => txn.id !== id)
    // TODO: Implement API call to delete transaction
    // await budgetApi.deleteTransaction(id)  // <-- COMMENTED OUT!
  } catch (e) {
    console.error('Failed to delete transaction:', e)
  }
}
```

**Problem:** Users believe transactions are deleted, but they reappear on page refresh. This is a data integrity violation that will confuse users and break trust.

**Fix Required:**
1. Uncomment the API call
2. Implement optimistic update with rollback on failure
3. Add proper error handling and user feedback

#### CRIT-002: Race Conditions in Budget Store
**File:** `C:\Users\watso\Dev\frontend\src\stores\budget.ts`
**Severity:** CRITICAL
**Impact:** Data corruption, incorrect calculations

**Problem:** The store uses a single `loading` flag for multiple concurrent operations. When `addExpense()` calls `fetchExpenses()` and `fetchNumber()` in sequence, the loading state becomes unreliable. Concurrent user actions can cause:
- Stale data overwriting fresh data
- Incorrect budget calculations
- UI showing wrong state

**Example Race Condition:**
```typescript
async function addExpense(expense: ...) {
  loading.value = true  // Set loading
  try {
    await budgetApi.createExpense(expense)
    await fetchExpenses()     // Sets loading = false internally
    await fetchNumber()       // Sets loading = true then false again
  } finally {
    loading.value = false     // May conflict with concurrent operations
  }
}
```

**Fix Required:**
1. Implement per-operation loading states
2. Add request cancellation (AbortController)
3. Use optimistic updates with rollback
4. Consider state machine approach for complex flows

#### CRIT-003: No Input Validation on Amounts
**Files:** Multiple Vue components
**Severity:** HIGH
**Impact:** Invalid data, potential calculation errors

**Problem:** Negative amounts, NaN, Infinity, and extremely large numbers are not properly validated on the frontend. While the API has some validation, client-side protection is missing.

---

### 2. SECURITY VULNERABILITIES (P0/P1)

#### SEC-001: Hardcoded API URL
**File:** `C:\Users\watso\Dev\frontend\src\services\api.ts` (line 4)
**Severity:** CRITICAL
**Impact:** Application non-functional in production

```typescript
// CURRENT CODE
const api = axios.create({
  baseURL: 'http://localhost:8000',  // HARDCODED - WON'T WORK IN PRODUCTION
  headers: {
    'Content-Type': 'application/json',
  },
})
```

**Fix Required:**
```typescript
const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '/api',
  headers: {
    'Content-Type': 'application/json',
  },
})
```

#### SEC-002: Zero Authentication
**Files:** All API endpoints and frontend routes
**Severity:** CRITICAL
**Impact:** Anyone can access and modify any user's financial data

**Current State:**
- No user authentication system
- No session management
- No route guards
- API endpoints are completely open
- No CSRF protection

**Fix Required:**
1. Implement authentication (OAuth, JWT, or session-based)
2. Add Vue Router navigation guards
3. Implement API authentication middleware
4. Add CSRF protection
5. Secure sensitive routes

#### SEC-003: Open CORS Configuration
**File:** `C:\Users\watso\Dev\api\main.py` (lines 43-54)
**Severity:** HIGH
**Impact:** Potential cross-origin attacks in production

```python
# CURRENT CODE - LOCALHOST ONLY
allow_origins=[
    "http://localhost:5173",
    "http://localhost:3000",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:3000",
],
```

**Fix Required:**
- Configure CORS from environment variables
- Whitelist only production domains
- Consider removing wildcard methods/headers

#### SEC-004: Verbose Error Messages
**Files:** Multiple API endpoints
**Severity:** MEDIUM
**Impact:** Information leakage to attackers

Error messages include internal details like `f"Error creating expense: {str(e)}"` which could expose system internals.

#### SEC-005: No Rate Limiting
**Files:** All API endpoints
**Severity:** MEDIUM
**Impact:** DoS vulnerability, abuse potential

---

### 3. FRONTEND BUGS (P0/P1)

#### BUG-001: Router History Bug
**File:** `C:\Users\watso\Dev\frontend\src\router\index.ts` (line 5)
**Severity:** CRITICAL
**Impact:** Navigation broken in production builds

```typescript
// CURRENT CODE - INCORRECT
const router = createRouter({
  history: createWebHistory(import.meta.url),  // WRONG: passes full file URL
  routes: [...]
})

// CORRECT CODE
const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),  // Correct: uses base path
  routes: [...]
})
```

#### BUG-002: Browser Confirm for Deletions
**Files:** `Transactions.vue`, `Expenses.vue`
**Severity:** MEDIUM
**Impact:** Poor UX, accessibility issues

Using native `confirm()` is:
- Not customizable
- Blocks the main thread
- Not accessible (screen readers)
- Not styled consistently

**Fix:** Use Vuetify dialog component instead.

#### BUG-003: Missing Error Boundaries
**Files:** All Vue components
**Severity:** MEDIUM
**Impact:** Unhandled errors crash the application

**Fix:** Implement Vue error handling:
```typescript
app.config.errorHandler = (err, vm, info) => {
  // Log to error tracking service
  console.error('Global error:', err, info)
}
```

#### BUG-004: Missing Loading States
**Files:** Multiple components
**Severity:** LOW
**Impact:** Users see stale data during API calls

---

### 4. ACCESSIBILITY ISSUES (P1)

#### A11Y-001: Missing Form Labels
**Files:** Multiple Vue components
**Severity:** HIGH
**Impact:** WCAG 2.1 Level A failure

Forms use placeholders but lack proper `<label>` elements with `for` attributes.

#### A11Y-002: Color Contrast Issues
**File:** `NumberDisplay.vue`
**Severity:** HIGH
**Impact:** WCAG 2.1 Level AA failure

White text on green background may not meet 4.5:1 contrast ratio.

#### A11Y-003: Missing ARIA Labels
**Files:** Navigation, buttons, icons
**Severity:** HIGH
**Impact:** Screen reader users cannot navigate effectively

Icon-only buttons lack `aria-label` attributes:
```vue
<!-- CURRENT -->
<v-btn icon="mdi-delete" />

<!-- FIXED -->
<v-btn icon="mdi-delete" aria-label="Delete transaction" />
```

#### A11Y-004: Keyboard Navigation
**Files:** Data tables, dialogs
**Severity:** MEDIUM
**Impact:** Keyboard-only users cannot access all features

#### A11Y-005: Focus Management
**Files:** Dialogs, form submissions
**Severity:** MEDIUM
**Impact:** Focus not properly managed after actions

---

### 5. PERFORMANCE ISSUES (P1/P2)

#### PERF-001: Bundle Size Not Optimized
**Impact:** Slow initial load, poor mobile experience

**Issues:**
- Vuetify not tree-shaken (importing all components)
- No code splitting for routes
- @mdi/font includes 7000+ icons (only using ~10)

**Fixes:**
1. Configure Vuetify a-la-carte import
2. Use dynamic imports for route components (partially done)
3. Use `@mdi/js` instead of font, import only needed icons

#### PERF-002: No Request Caching
**Files:** API calls, store actions
**Severity:** MEDIUM
**Impact:** Unnecessary network requests, slower UX

#### PERF-003: Redundant API Calls
**File:** `budget.ts` store
**Severity:** MEDIUM
**Impact:** Extra network traffic

After adding expense, both `fetchExpenses()` AND `fetchNumber()` are called. Could be optimized.

#### PERF-004: No Pagination
**Files:** Transactions.vue, Expenses.vue
**Severity:** MEDIUM (becomes HIGH at scale)
**Impact:** Performance degrades with data growth

---

### 6. CODE QUALITY ISSUES (P2/P3)

#### CODE-001: TypeScript `any` Usage
**Files:** Multiple
**Severity:** MEDIUM
**Impact:** Loss of type safety

Examples:
```typescript
// Transactions.vue line 153
const txn: any = {
  amount: newTransaction.value.amount,
  ...
}

// Settings.vue line 152
const currentConfig = ref<any>(null)
```

#### CODE-002: Missing Prop Defaults
**File:** `NumberDisplay.vue`
**Severity:** LOW
**Impact:** Potential runtime errors

```typescript
// CURRENT - No defaults for optional props
const props = defineProps<{
  theNumber: number
  mode: string
  todaySpending?: number
  remainingToday?: number
  isOverBudget?: boolean
  daysRemaining?: number
}>()

// SHOULD USE withDefaults()
```

#### CODE-003: Inconsistent Error Handling
**Files:** All components
**Severity:** MEDIUM
**Impact:** Silent failures, poor debugging

Most errors just log to console:
```typescript
} catch (e) {
  console.error('Failed to add expense:', e)
}
```

#### CODE-004: Missing API Response Typing
**File:** `api.ts`
**Severity:** LOW
**Impact:** Type safety gaps

#### CODE-005: No Environment Configuration
**Severity:** HIGH
**Impact:** Cannot deploy to different environments

Missing `.env` files and environment-specific configuration.

---

### 7. TESTING GAPS (P2)

#### TEST-001: Tests Don't Verify API Integration
**Severity:** MEDIUM
**Impact:** Integration bugs not caught

Tests mock the store, but don't test actual API integration.

#### TEST-002: Fake Delete Test Passes
**File:** `Transactions.spec.ts`
**Severity:** HIGH
**Impact:** False confidence

The test for delete transaction PASSES even though the feature is broken:
```typescript
it('should delete transaction with confirmation', async () => {
  // This test only checks local state, not API persistence!
  expect(store.transactions).toHaveLength(1)  // PASSES but data not persisted
})
```

#### TEST-003: No E2E Tests
**Severity:** MEDIUM
**Impact:** User flows not validated

#### TEST-004: No API Contract Tests
**Severity:** MEDIUM
**Impact:** Frontend/backend contract drift

---

### 8. UX ISSUES (P2/P3)

#### UX-001: No Confirmation After Actions
**Severity:** MEDIUM
**Impact:** Users unsure if actions succeeded

Only Settings page shows success snackbar. Other pages silently complete.

#### UX-002: Form Validation Feedback
**Severity:** MEDIUM
**Impact:** Users don't know why submission fails

#### UX-003: Empty States
**Severity:** LOW
**Impact:** Poor experience when no data exists

#### UX-004: Mobile Responsiveness
**Severity:** MEDIUM
**Impact:** Poor mobile experience

Navigation rail doesn't collapse on mobile.

---

## Prioritized Implementation Plan

### Phase 0: STOP THE BLEEDING (Week 1)

**Goal:** Fix issues that cause data loss or complete failure

| ID | Task | File(s) | Est. Hours |
|----|------|---------|------------|
| CRIT-001 | Fix fake transaction delete | Transactions.vue | 2h |
| BUG-001 | Fix router history bug | router/index.ts | 0.5h |
| SEC-001 | Environment-based API URL | api.ts, .env files | 2h |

**Success Metrics:**
- [ ] Transaction deletions persist to database
- [ ] Application builds and runs in production mode
- [ ] API URL configurable per environment

### Phase 1: CORE SECURITY (Weeks 2-4)

**Goal:** Implement authentication and fix security vulnerabilities

| ID | Task | Est. Hours |
|----|------|------------|
| SEC-002 | Implement authentication system | 40h |
| SEC-002 | Add Vue Router guards | 8h |
| SEC-003 | Production CORS configuration | 4h |
| SEC-004 | Sanitize error messages | 4h |
| CRIT-002 | Fix race conditions in store | 16h |

**Success Metrics:**
- [ ] Users must authenticate to access data
- [ ] Route guards prevent unauthorized access
- [ ] No internal errors exposed to clients
- [ ] Concurrent operations don't corrupt state

### Phase 2: ACCESSIBILITY COMPLIANCE (Weeks 4-6)

**Goal:** Achieve WCAG 2.1 Level AA compliance

| ID | Task | Est. Hours |
|----|------|------------|
| A11Y-001 | Add proper form labels | 4h |
| A11Y-002 | Fix color contrast | 4h |
| A11Y-003 | Add ARIA labels to all interactive elements | 8h |
| A11Y-004 | Keyboard navigation audit | 8h |
| A11Y-005 | Focus management | 8h |
| BUG-002 | Replace confirm() with Vuetify dialogs | 4h |

**Success Metrics:**
- [ ] axe-core audit passes
- [ ] Lighthouse accessibility score > 90
- [ ] Full keyboard navigation support
- [ ] Screen reader tested

### Phase 3: PERFORMANCE OPTIMIZATION (Weeks 6-8)

**Goal:** Optimize bundle size and runtime performance

| ID | Task | Est. Hours |
|----|------|------------|
| PERF-001 | Tree-shake Vuetify | 4h |
| PERF-001 | Optimize icon imports | 2h |
| PERF-002 | Implement request caching | 8h |
| PERF-003 | Optimize redundant API calls | 4h |
| PERF-004 | Add pagination | 16h |

**Success Metrics:**
- [ ] Initial bundle < 250KB gzipped
- [ ] Lighthouse performance score > 80
- [ ] Time to Interactive < 3s on 3G

### Phase 4: CODE QUALITY (Weeks 8-12)

**Goal:** Improve maintainability and type safety

| ID | Task | Est. Hours |
|----|------|------------|
| CODE-001 | Eliminate `any` types | 8h |
| CODE-002 | Add prop defaults | 2h |
| CODE-003 | Implement error handling strategy | 16h |
| CODE-005 | Environment configuration system | 8h |
| TEST-002 | Fix fake delete test to fail | 2h |
| TEST-003 | Add E2E tests with Playwright | 24h |

**Success Metrics:**
- [ ] Zero `any` types in production code
- [ ] 80%+ code coverage
- [ ] E2E tests cover critical user flows
- [ ] Consistent error handling throughout

### Phase 5: UX POLISH (Ongoing)

**Goal:** Improve user experience and mobile support

| ID | Task | Est. Hours |
|----|------|------------|
| UX-001 | Add success/error feedback to all actions | 8h |
| UX-002 | Improve form validation UX | 8h |
| UX-003 | Design empty states | 4h |
| UX-004 | Mobile navigation | 12h |
| SEC-005 | Implement rate limiting | 8h |

---

## Technical Debt Register

| ID | Description | Impact | Effort | Priority |
|----|-------------|--------|--------|----------|
| TD-001 | Store uses single loading flag | Race conditions | Medium | P0 |
| TD-002 | No API error standardization | Inconsistent UX | Low | P2 |
| TD-003 | Tests mock too much | False confidence | Medium | P2 |
| TD-004 | No request deduplication | Wasted resources | Low | P3 |
| TD-005 | No global state persistence | State lost on refresh | Medium | P2 |
| TD-006 | No TypeScript strict mode | Missed type errors | Low | P3 |
| TD-007 | Direct store mutation in components | Maintainability | Low | P3 |

---

## Definition of Done

### For P0 Issues:
- [ ] Fix implemented and tested
- [ ] Regression test added
- [ ] Code reviewed by senior developer
- [ ] Deployed to staging
- [ ] Manually verified in staging

### For P1 Issues:
- [ ] Fix implemented with unit tests
- [ ] Documentation updated if needed
- [ ] Code reviewed
- [ ] Deployed to staging

### For P2/P3 Issues:
- [ ] Fix implemented
- [ ] Basic testing complete
- [ ] Code reviewed

---

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Data loss from fake delete | HIGH | CRITICAL | P0 fix immediately |
| Security breach (no auth) | HIGH | CRITICAL | Don't deploy without auth |
| Production failure (router bug) | CERTAIN | HIGH | P0 fix immediately |
| Accessibility lawsuit | LOW | HIGH | Complete Phase 2 before public launch |
| Performance issues at scale | MEDIUM | MEDIUM | Phase 3 before heavy usage |

---

## Monitoring & Success Metrics

### Phase 0 Completion
- All P0 issues resolved
- No data loss possible
- Application deployable to production environment

### Phase 1 Completion
- Security audit passed
- Authentication in place
- No known vulnerabilities

### Phase 2 Completion
- WCAG 2.1 Level AA compliant
- Lighthouse accessibility > 90

### Phase 3 Completion
- Bundle size < 250KB gzipped
- Lighthouse performance > 80
- No N+1 query patterns

### Phase 4 Completion
- Code coverage > 80%
- TypeScript strict mode enabled
- E2E test suite passing

### Production Ready Checklist
- [ ] All P0 and P1 issues resolved
- [ ] Security audit completed
- [ ] Accessibility audit passed
- [ ] Performance benchmarks met
- [ ] Error tracking in place (Sentry or similar)
- [ ] Monitoring dashboards configured
- [ ] Incident response plan documented
- [ ] Backup and recovery tested

---

## Appendix: File Reference

### Critical Files Requiring Immediate Attention

| File | Issues | Priority |
|------|--------|----------|
| `frontend/src/views/Transactions.vue` | CRIT-001 (fake delete) | P0 |
| `frontend/src/services/api.ts` | SEC-001 (hardcoded URL) | P0 |
| `frontend/src/router/index.ts` | BUG-001 (history bug) | P0 |
| `frontend/src/stores/budget.ts` | CRIT-002 (race conditions) | P0 |
| `api/main.py` | SEC-002, SEC-003 (auth, CORS) | P1 |

### All Source Files

```
Frontend (C:\Users\watso\Dev\frontend\src\)
├── main.ts
├── App.vue
├── services/
│   └── api.ts                 # SEC-001
├── stores/
│   └── budget.ts              # CRIT-002
├── router/
│   └── index.ts               # BUG-001
├── views/
│   ├── Dashboard.vue
│   ├── Expenses.vue           # BUG-002
│   ├── Transactions.vue       # CRIT-001, BUG-002
│   └── Settings.vue
├── components/
│   ├── NavigationRail.vue     # A11Y issues
│   └── NumberDisplay.vue      # A11Y-002, CODE-002
└── plugins/
    └── vuetify.ts

API (C:\Users\watso\Dev\api\)
├── main.py                    # SEC-002, SEC-003, SEC-004
└── models.py
```

---

## Document History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2025-12-16 | Senior Dev Review | Initial comprehensive roadmap |

---

**IMPORTANT:** This document should be reviewed and updated weekly during active development. All P0 issues must be resolved before any production deployment. The application in its current state should be considered ALPHA quality and not suitable for production use with real user data.
