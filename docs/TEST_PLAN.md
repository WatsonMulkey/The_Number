# The Number - Comprehensive Test Plan
**Date:** December 16, 2025
**Product:** Paid PWA Budgeting App
**Target:** Launch-ready test coverage

---

## Executive Summary

**Current Test Coverage:**
- ✅ Python Backend: 236 passing tests (excellent coverage)
- ⚠️  Vue Frontend: Basic Vitest tests exist
- ❌ Integration Tests: Missing
- ❌ E2E Tests: Missing
- ❌ PWA Tests: Missing (PWA not yet implemented)

**Testing Philosophy:**
Given the product scope (10k users, $10 one-time payment), we need **pragmatic test coverage** that catches bugs that would cost users money or data without over-engineering.

**Recommended Approach:**
- Keep backend unit tests (already comprehensive)
- Add critical integration tests (API → Database)
- Manual E2E testing for MVP (automate post-launch)
- PWA installation testing on real devices

---

## Test Priority Framework

### P0: Must Test Before Launch
Tests that prevent:
- Data loss
- Payment failures
- App crashes
- Security vulnerabilities

### P1: Should Test Soon After Launch
Tests that improve:
- User experience
- Data accuracy
- Performance

### P2: Nice to Have
Tests for:
- Edge cases
- Optimization
- Future features

---

## P0: Critical Test Coverage (Pre-Launch)

### 1. Transaction Delete Verification ⚠️ **CRITICAL**
**File to Create:** `frontend/src/views/__tests__/Transactions.integration.spec.ts`

**Test:** Verify that deleting a transaction calls the API and persists to database

```typescript
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import Transactions from '../Transactions.vue'
import { budgetApi } from '@/services/api'

describe('Transaction Delete Integration', () => {
  it('should call API when deleting transaction', async () => {
    const deleteSpy = vi.spyOn(budgetApi, 'deleteTransaction').mockResolvedValue()

    const wrapper = mount(Transactions)

    // Mock confirm dialog
    global.confirm = vi.fn(() => true)

    await wrapper.vm.deleteTransaction(123)

    expect(deleteSpy).toHaveBeenCalledWith(123)
  })

  it('should remove transaction from local state after API success', async () => {
    vi.spyOn(budgetApi, 'deleteTransaction').mockResolvedValue()

    const wrapper = mount(Transactions)
    const store = useBudgetStore()
    store.transactions = [
      { id: 1, description: 'Test', amount: 10, date: '2025-12-16' },
      { id: 2, description: 'Test 2', amount: 20, date: '2025-12-16' }
    ]

    global.confirm = vi.fn(() => true)
    await wrapper.vm.deleteTransaction(1)

    expect(store.transactions).toHaveLength(1)
    expect(store.transactions[0].id).toBe(2)
  })

  it('should NOT remove transaction if API call fails', async () => {
    vi.spyOn(budgetApi, 'deleteTransaction').mockRejectedValue(new Error('API Error'))

    const wrapper = mount(Transactions)
    const store = useBudgetStore()
    store.transactions = [{ id: 1, description: 'Test', amount: 10, date: '2025-12-16' }]

    global.confirm = vi.fn(() => true)

    try {
      await wrapper.vm.deleteTransaction(1)
    } catch (e) {
      // Expected to fail
    }

    // Transaction should still be in local state
    expect(store.transactions).toHaveLength(1)
  })
})
```

**Effort:** 2 hours
**Priority:** P0 - Must fix and test before launch

---

### 2. License Verification Tests
**File to Create:** `api/tests/test_license.py`

**Test:** Verify Gumroad license validation

```python
import pytest
from fastapi.testclient import TestClient
from api.main import app
from unittest.mock import patch, Mock

client = TestClient(app)

class TestLicenseVerification:
    @patch('api.main.requests.get')
    def test_valid_license_creates_user(self, mock_requests):
        """Test that valid license key creates user account"""
        # Mock Gumroad API response
        mock_response = Mock()
        mock_response.json.return_value = {"success": True, "purchase": {"email": "user@example.com"}}
        mock_requests.return_value = mock_response

        response = client.post("/api/auth/verify-license", json={
            "license_key": "VALID-KEY-123"
        })

        assert response.status_code == 200
        assert "token" in response.json()

    @patch('api.main.requests.get')
    def test_invalid_license_rejected(self, mock_requests):
        """Test that invalid license key is rejected"""
        mock_response = Mock()
        mock_response.json.return_value = {"success": False}
        mock_requests.return_value = mock_response

        response = client.post("/api/auth/verify-license", json={
            "license_key": "INVALID-KEY"
        })

        assert response.status_code == 401

    def test_duplicate_license_key_rejected(self):
        """Test that same license key cannot be used twice"""
        # This test requires database setup
        # Should reject if license key already exists in users table
        pass
```

**Effort:** 4 hours (including Gumroad API mock setup)
**Priority:** P0 - Payment is core functionality

---

### 3. Budget Calculation Tests (Already Exist)
**Location:** `tests/test_calculator.py` (236 tests already passing ✅)

**Verify coverage includes:**
- [x] Paycheck mode calculation
- [x] Fixed pool mode calculation
- [x] Today's spending deduction
- [x] Negative amounts validation
- [x] Zero income handling
- [x] Division by zero protection

**Status:** Excellent coverage already exists. No additional tests needed.

---

### 4. Authentication Flow Tests
**File to Create:** `api/tests/test_auth.py`

**Test:** User registration and login

```python
def test_user_registration_with_license():
    """Test user can register after license verification"""
    response = client.post("/api/auth/register", json={
        "username": "testuser",
        "password": "securepassword",
        "license_key": "VALID-LICENSE"
    })
    assert response.status_code == 201
    assert "token" in response.json()

def test_user_login():
    """Test user can log in with credentials"""
    # First register
    client.post("/api/auth/register", json={
        "username": "testuser",
        "password": "securepassword",
        "license_key": "VALID-LICENSE"
    })

    # Then login
    response = client.post("/api/auth/login", json={
        "username": "testuser",
        "password": "securepassword"
    })
    assert response.status_code == 200
    assert "token" in response.json()

def test_protected_endpoint_requires_auth():
    """Test that API endpoints require authentication"""
    response = client.get("/api/expenses")
    assert response.status_code == 401  # Unauthorized

def test_protected_endpoint_with_valid_token():
    """Test that valid token grants access"""
    # Login and get token
    login_response = client.post("/api/auth/login", json={
        "username": "testuser",
        "password": "securepassword"
    })
    token = login_response.json()["token"]

    # Access protected endpoint
    response = client.get("/api/expenses", headers={
        "Authorization": f"Bearer {token}"
    })
    assert response.status_code == 200
```

**Effort:** 4 hours
**Priority:** P0 - Required for multi-user support

---

### 5. Data Isolation Tests
**File:** `api/tests/test_user_isolation.py`

**Test:** Users can only access their own data

```python
def test_user_can_only_see_own_expenses():
    """Test that expenses are user-scoped"""
    # Create two users
    user1_token = create_test_user("user1", "pass1")
    user2_token = create_test_user("user2", "pass2")

    # User 1 creates expense
    client.post("/api/expenses",
        headers={"Authorization": f"Bearer {user1_token}"},
        json={"name": "Rent", "amount": 1500, "is_fixed": True}
    )

    # User 2 should not see User 1's expense
    response = client.get("/api/expenses", headers={"Authorization": f"Bearer {user2_token}"})
    assert len(response.json()) == 0

def test_user_cannot_delete_other_users_expense():
    """Test that users cannot delete other users' data"""
    user1_token = create_test_user("user1", "pass1")
    user2_token = create_test_user("user2", "pass2")

    # User 1 creates expense
    expense_response = client.post("/api/expenses",
        headers={"Authorization": f"Bearer {user1_token}"},
        json={"name": "Rent", "amount": 1500, "is_fixed": True}
    )
    expense_id = expense_response.json()["id"]

    # User 2 tries to delete it
    delete_response = client.delete(f"/api/expenses/{expense_id}",
        headers={"Authorization": f"Bearer {user2_token}"}
    )
    assert delete_response.status_code == 404  # Not found (user 2 can't see it)
```

**Effort:** 3 hours
**Priority:** P0 - Security critical

---

## P1: Important Test Coverage (Post-Launch)

### 6. Offline Functionality Tests
**Requires:** PWA implementation complete

```typescript
describe('Offline Functionality', () => {
  it('should show cached data when offline', async () => {
    // Load data while online
    const store = useBudgetStore()
    await store.fetchNumber()

    // Go offline
    window.dispatchEvent(new Event('offline'))

    // Should still show cached data
    expect(store.theNumber).toBeGreaterThan(0)
  })

  it('should queue transactions when offline', async () => {
    window.dispatchEvent(new Event('offline'))

    // Record transaction while offline
    await store.recordTransaction({
      amount: 25,
      description: 'Coffee'
    })

    // Should be in queue, not sent to server
    expect(store.pendingTransactions).toHaveLength(1)
  })

  it('should sync pending transactions when back online', async () => {
    // Add pending transaction
    store.pendingTransactions.push({
      amount: 25,
      description: 'Coffee'
    })

    // Go back online
    window.dispatchEvent(new Event('online'))

    // Wait for sync
    await store.syncPendingTransactions()

    // Queue should be empty
    expect(store.pendingTransactions).toHaveLength(0)
  })
})
```

**Effort:** 6 hours
**Priority:** P1 - Core PWA feature

---

### 7. PWA Installation Tests
**Type:** Manual testing on real devices

**Test Checklist:**
- [ ] App can be installed on Android Chrome
- [ ] App can be installed on iOS Safari
- [ ] App icon appears on home screen
- [ ] App launches in standalone mode (no browser chrome)
- [ ] App works offline after installation
- [ ] App updates when new version is available

**Devices to Test:**
- Android phone (Chrome)
- iPhone (Safari)
- Desktop (Chrome, Edge, Firefox)

**Effort:** 4 hours
**Priority:** P1 - PWA is core product

---

### 8. Bundle Size & Performance Tests
**Tools:** Lighthouse, Bundle Analyzer

```bash
# Run build and analyze
npm run build
npx vite-bundle-visualizer

# Check bundle size
ls -lh dist/assets/*.js
```

**Success Criteria:**
- Initial bundle < 250KB gzipped
- Lighthouse performance score > 80
- Time to Interactive < 3s on 3G

**Effort:** 2 hours
**Priority:** P1 - Affects user experience

---

### 9. Accessibility Tests
**Tools:** axe-core, Lighthouse Accessibility

```bash
# Install axe-core
npm install -D @axe-core/playwright

# Run accessibility tests
npx playwright test --grep accessibility
```

**Test Cases:**
- [ ] All form inputs have labels
- [ ] Color contrast meets WCAG AA (4.5:1)
- [ ] All interactive elements keyboard accessible
- [ ] Screen reader announces correctly
- [ ] Focus management on dialogs

**Effort:** 4 hours
**Priority:** P1 - Legal requirement in some regions

---

## P2: Nice-to-Have Test Coverage

### 10. E2E User Flow Tests (Playwright)
**Setup:**
```bash
npm install -D @playwright/test
npx playwright install
```

**Test:** Complete user journey
```typescript
test('complete user journey', async ({ page }) => {
  // User visits landing page
  await page.goto('https://yourapp.com')

  // Purchases via Gumroad (use Gumroad test mode)
  await page.click('text=Buy Now')
  // ... Gumroad checkout flow

  // Receives license key, enters it
  await page.fill('[name="license"]', 'TEST-LICENSE-KEY')
  await page.click('text=Activate')

  // Creates account
  await page.fill('[name="username"]', 'testuser')
  await page.fill('[name="password"]', 'securepass')
  await page.click('text=Create Account')

  // Configures budget
  await page.click('text=Setup Budget')
  await page.fill('[name="income"]', '5000')
  await page.fill('[name="days"]', '30')
  await page.click('text=Save')

  // Views "The Number"
  await expect(page.locator('.the-number')).toContainText('$')

  // Records spending
  await page.click('text=Record Spending')
  await page.fill('[name="amount"]', '25')
  await page.fill('[name="description"]', 'Coffee')
  await page.click('text=Add')

  // Verifies spending is recorded
  await expect(page.locator('text=Coffee')).toBeVisible()
})
```

**Effort:** 8-12 hours
**Priority:** P2 - Can test manually for MVP

---

### 11. Load Testing
**Tool:** k6 or Artillery

```javascript
import http from 'k6/http';
import { check } from 'k6';

export let options = {
  stages: [
    { duration: '2m', target: 100 }, // Ramp up to 100 users
    { duration: '5m', target: 100 }, // Stay at 100 users
    { duration: '2m', target: 0 },   // Ramp down
  ],
};

export default function () {
  // Login
  let loginRes = http.post('http://api.yourapp.com/api/auth/login', JSON.stringify({
    username: 'testuser',
    password: 'testpass'
  }));

  check(loginRes, {
    'login successful': (r) => r.status === 200,
  });

  let token = loginRes.json('token');

  // Get the number
  let numberRes = http.get('http://api.yourapp.com/api/number', {
    headers: { Authorization: `Bearer ${token}` }
  });

  check(numberRes, {
    'got the number': (r) => r.status === 200,
    'response time OK': (r) => r.timings.duration < 500,
  });
}
```

**Success Criteria:**
- API handles 100 concurrent users
- 95th percentile response time < 500ms
- 0% error rate

**Effort:** 4 hours
**Priority:** P2 - 10k users won't all be concurrent

---

## Testing Strategy Summary

### Pre-Launch (P0)
**Focus:** Critical bugs and security
- [x] Backend unit tests (236 tests exist)
- [ ] Transaction delete integration test
- [ ] License verification tests
- [ ] Authentication tests
- [ ] Data isolation tests

**Estimated Effort:** 12-16 hours

---

### Launch Week (P1)
**Focus:** PWA functionality and UX
- [ ] Offline functionality tests
- [ ] PWA installation manual testing
- [ ] Performance/bundle size checks
- [ ] Basic accessibility tests

**Estimated Effort:** 16-20 hours

---

### Post-Launch (P2)
**Focus:** Optimization and scale
- [ ] E2E automated tests (Playwright)
- [ ] Load testing
- [ ] Advanced accessibility audit
- [ ] Browser compatibility testing

**Estimated Effort:** 20-30 hours

---

## Test Execution Plan

### Week 1: Fix + Test Critical Bugs
**Day 1:**
- Fix router bug, delete bug, API URL
- Write integration tests for delete functionality
- Verify all backend tests still pass

**Day 2-3:**
- Implement Gumroad license verification
- Write license verification tests
- Test payment flow end-to-end (manual)

**Day 4-5:**
- Implement authentication
- Write auth and data isolation tests
- Run full test suite

### Week 2: PWA Testing
**Day 1-2:**
- Implement PWA (manifest + service worker)
- Write offline functionality tests
- Test on real devices (Android, iOS)

**Day 3-4:**
- Bundle size optimization
- Performance testing (Lighthouse)
- Accessibility testing (axe-core)

**Day 5:**
- Manual E2E testing
- Bug fixes
- Final test run

### Week 3: Pre-Launch Testing
**Day 1-2:**
- Full regression testing
- Cross-browser testing
- Mobile device testing

**Day 3-5:**
- Beta user testing (5-10 users)
- Fix reported bugs
- Performance monitoring setup

---

## Test Infrastructure Setup

### Required Tools
```bash
# Frontend testing
npm install -D vitest @vitest/ui @vitest/coverage-v8
npm install -D @vue/test-utils happy-dom
npm install -D @axe-core/playwright

# Backend testing (already installed)
pip install pytest pytest-cov

# E2E testing (optional for MVP)
npm install -D @playwright/test

# Performance testing (optional)
npm install -D lighthouse
```

### CI/CD Integration
**GitHub Actions** (`.github/workflows/test.yml`):
```yaml
name: Test Suite

on: [push, pull_request]

jobs:
  test-backend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run tests
        run: pytest tests/ --cov=src

  test-frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Node
        uses: actions/setup-node@v2
        with:
          node-version: '18'
      - name: Install dependencies
        run: cd frontend && npm install
      - name: Run tests
        run: cd frontend && npm test
      - name: Build
        run: cd frontend && npm run build
```

---

## Success Metrics

### Pre-Launch
- ✅ All P0 tests passing
- ✅ No critical bugs
- ✅ Payment flow works end-to-end
- ✅ PWA installs on mobile devices

### Post-Launch (Week 1)
- User-reported bugs < 5
- Payment success rate > 95%
- App crash rate < 1%

### Post-Launch (Month 1)
- Test coverage > 80%
- Lighthouse score > 80
- Accessibility score > 90

---

## Risk-Based Testing Priorities

| Risk | Test Focus | Priority |
|------|------------|----------|
| Data loss | Transaction persistence | P0 |
| Payment failure | License verification | P0 |
| Security breach | Auth + data isolation | P0 |
| Can't install PWA | PWA setup | P1 |
| Poor performance | Bundle size | P1 |
| Accessibility lawsuit | A11y compliance | P1 |
| Scale issues | Load testing | P2 |

---

## Conclusion

**Minimum Viable Test Suite for Launch:**
- Backend unit tests (already exist ✅)
- Critical integration tests for delete + auth
- Manual PWA installation testing
- Basic accessibility checks

**Total Testing Effort for MVP:** ~20-30 hours

**Post-Launch Testing Investment:** ~40-60 hours over 3 months

This pragmatic approach balances shipping quickly with maintaining quality. For a 10k-user paid app, comprehensive automated E2E testing can wait until after validating product-market fit.

---

**Document Version:** 1.0
**Last Updated:** December 16, 2025
