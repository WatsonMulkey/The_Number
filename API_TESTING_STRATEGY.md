# API Testing Strategy
**Project:** The Number - PWA Backend API
**Date:** 2025-12-15
**Status:** Draft for Review

---

## Overview

This document defines the testing approach for The Number PWA backend API, addressing the critical finding from the Skeptical Senior Dev review: **happy path bias in current tests**.

**Goal:** Achieve 30%+ error case coverage in all test suites.

---

## Testing Pyramid

```
        /\
       /  \        E2E Tests (10%)
      /____\       - Full user flows
     /      \      - PWA + API integration
    /________\     Integration Tests (30%)
   /          \    - API + Database
  /____________\   - Multi-endpoint flows
 /              \  Unit Tests (60%)
/__________    __\ - Individual functions
                   - Edge cases, errors
```

---

## 1. Unit Tests

### Current State (From Skeptical Dev Review)

| Test Suite | Error Tests | Total Tests | Coverage |
|-----------|-------------|-------------|----------|
| test_budget_calculator.py | 1 | 36 | 3% ❌ |
| test_cli.py | 4 | 36 | 11% ❌ |
| test_database.py | 0 | 28 | 0% ❌ |
| test_export_expenses.py | 0 | 8 | 0% ❌ |
| test_import_expenses.py | 1 | 15 | 7% ❌ |
| test_integration.py | 1 | 30 | 3% ❌ |
| test_security.py | 4 | 21 | 19% ❌ |

**Target:** 30%+ error coverage per suite

### Improvement Plan

**For each module, add tests for:**

1. **Invalid Input:**
   - Negative numbers where positive expected
   - Zero where non-zero expected
   - Empty strings where required
   - Strings too long (>MAX_STRING_LENGTH)
   - Numbers too large (>MAX_AMOUNT)

2. **Boundary Conditions:**
   - Maximum values (MAX_AMOUNT, MAX_DAYS_UNTIL_PAYCHECK)
   - Minimum values (0.01, 1 day)
   - Edge of valid range

3. **Type Mismatches:**
   - String instead of number
   - None instead of required value
   - Wrong object type

4. **State Issues:**
   - Operating on non-existent resources (404 scenarios)
   - Duplicate operations (creating same expense twice)
   - Conflicting operations (deleting then updating)

### Example: test_budget_calculator.py Improvements

**Add 10+ new error tests:**

```python
class TestBudgetCalculatorErrors:
    """Test error handling and edge cases."""

    def test_negative_expense_amount_rejected(self):
        calc = BudgetCalculator()
        with pytest.raises(ValueError, match="cannot be negative"):
            calc.add_expense("Rent", -1500.0, True)

    def test_excessive_expense_amount_rejected(self):
        calc = BudgetCalculator()
        with pytest.raises(ValueError, match="exceeds maximum"):
            calc.add_expense("Mansion", 20_000_000.0, True)

    def test_empty_expense_name_rejected(self):
        calc = BudgetCalculator()
        with pytest.raises(ValueError, match="cannot be empty"):
            calc.add_expense("", 1500.0, True)

    def test_expense_name_too_long_rejected(self):
        calc = BudgetCalculator()
        long_name = "A" * 201
        with pytest.raises(ValueError, match="too long"):
            calc.add_expense(long_name, 1500.0, True)

    def test_zero_days_until_paycheck_rejected(self):
        calc = BudgetCalculator()
        with pytest.raises(ValueError, match="must be positive"):
            calc.calculate_paycheck_mode(3000.0, 0)

    def test_excessive_days_until_paycheck_rejected(self):
        calc = BudgetCalculator()
        with pytest.raises(ValueError, match="cannot exceed"):
            calc.calculate_paycheck_mode(3000.0, 500)

    def test_negative_monthly_income_rejected(self):
        calc = BudgetCalculator()
        with pytest.raises(ValueError, match="must be positive"):
            calc.calculate_paycheck_mode(-3000.0, 15)

    def test_calculation_with_no_expenses(self):
        """Edge case: No expenses added."""
        calc = BudgetCalculator()
        result = calc.calculate_paycheck_mode(3000.0, 15)
        assert result['daily_limit'] == 200.0

    def test_calculation_with_extreme_deficit(self):
        """Edge case: Expenses >> Income."""
        calc = BudgetCalculator()
        calc.add_expense("Huge Expense", 100_000.0, False)
        result = calc.calculate_paycheck_mode(3000.0, 15)
        assert result['is_deficit'] is True
        assert result['daily_limit'] == 0

    def test_transaction_amount_zero_rejected(self):
        calc = BudgetCalculator()
        with pytest.raises(ValueError, match="must be positive"):
            calc.add_transaction(0.0, "Free coffee")
```

**Target:** Increase error coverage from 3% → 35%

---

## 2. Integration Tests

### API Endpoint Tests

**Test Structure:**
```python
# tests/test_api.py
from fastapi.testclient import TestClient
from src.api import app

client = TestClient(app)

class TestAuthenticationAPI:
    """Test authentication endpoints."""

    def test_signup_success(self):
        """Happy path: User signs up successfully."""
        response = client.post("/api/auth/signup", json={
            "email": "test@example.com",
            "password": "SecurePass123"
        })
        assert response.status_code == 201
        assert "access_token" in response.json()
        assert "refresh_token" in response.cookies

    def test_signup_duplicate_email_rejected(self):
        """Error case: Email already exists."""
        # Create user
        client.post("/api/auth/signup", json={
            "email": "test@example.com",
            "password": "SecurePass123"
        })

        # Try to create again
        response = client.post("/api/auth/signup", json={
            "email": "test@example.com",
            "password": "DifferentPass456"
        })
        assert response.status_code == 400
        assert "already exists" in response.json()["message"]

    def test_signup_weak_password_rejected(self):
        """Error case: Password too weak."""
        response = client.post("/api/auth/signup", json={
            "email": "test@example.com",
            "password": "weak"
        })
        assert response.status_code == 400
        assert "password" in response.json()["message"].lower()

    def test_login_invalid_credentials(self):
        """Error case: Wrong password."""
        # Create user
        client.post("/api/auth/signup", json={
            "email": "test@example.com",
            "password": "SecurePass123"
        })

        # Try wrong password
        response = client.post("/api/auth/login", json={
            "email": "test@example.com",
            "password": "WrongPassword"
        })
        assert response.status_code == 401

    def test_login_nonexistent_user(self):
        """Error case: User doesn't exist."""
        response = client.post("/api/auth/login", json={
            "email": "nonexistent@example.com",
            "password": "SecurePass123"
        })
        assert response.status_code == 401

class TestBudgetAPI:
    """Test budget endpoints."""

    def test_get_budget_number_authenticated(self):
        """Happy path: User gets their budget number."""
        # Sign up and get token
        signup_response = client.post("/api/auth/signup", json={
            "email": "test@example.com",
            "password": "SecurePass123"
        })
        token = signup_response.json()["access_token"]

        # Get budget number
        response = client.get(
            "/api/budget/number",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        assert "daily_limit" in response.json()

    def test_get_budget_number_unauthenticated(self):
        """Error case: No auth token provided."""
        response = client.get("/api/budget/number")
        assert response.status_code == 401

    def test_get_budget_number_invalid_token(self):
        """Error case: Invalid JWT token."""
        response = client.get(
            "/api/budget/number",
            headers={"Authorization": "Bearer invalid_token_here"}
        )
        assert response.status_code == 401

    def test_get_budget_number_expired_token(self):
        """Error case: Expired JWT token."""
        # Create expired token (mocked)
        expired_token = create_expired_token()
        response = client.get(
            "/api/budget/number",
            headers={"Authorization": f"Bearer {expired_token}"}
        )
        assert response.status_code == 401

class TestTransactionAPI:
    """Test transaction endpoints."""

    def test_create_transaction_success(self):
        """Happy path: User creates transaction."""
        token = get_auth_token()
        response = client.post(
            "/api/transactions",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "amount": 12.50,
                "description": "Coffee"
            }
        )
        assert response.status_code == 201
        assert response.json()["amount"] == 12.50

    def test_create_transaction_negative_amount_rejected(self):
        """Error case: Negative transaction amount."""
        token = get_auth_token()
        response = client.post(
            "/api/transactions",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "amount": -10.00,
                "description": "Refund"
            }
        )
        assert response.status_code == 400
        assert "must be positive" in response.json()["message"]

    def test_create_transaction_empty_description_rejected(self):
        """Error case: Empty description."""
        token = get_auth_token()
        response = client.post(
            "/api/transactions",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "amount": 10.00,
                "description": ""
            }
        )
        assert response.status_code == 400

    def test_create_transaction_excessive_amount_rejected(self):
        """Error case: Amount > MAX_AMOUNT."""
        token = get_auth_token()
        response = client.post(
            "/api/transactions",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "amount": 20_000_000.00,
                "description": "Lottery win"
            }
        )
        assert response.status_code == 400
        assert "exceeds maximum" in response.json()["message"]

    def test_get_transactions_filters_by_user(self):
        """Security test: User A cannot see User B's transactions."""
        # Create two users
        user_a_token = create_user("user_a@test.com", "Pass123")
        user_b_token = create_user("user_b@test.com", "Pass456")

        # User A creates transaction
        client.post(
            "/api/transactions",
            headers={"Authorization": f"Bearer {user_a_token}"},
            json={"amount": 50.0, "description": "User A transaction"}
        )

        # User B gets transactions
        response = client.get(
            "/api/transactions",
            headers={"Authorization": f"Bearer {user_b_token}"}
        )

        # User B should NOT see User A's transaction
        assert response.status_code == 200
        transactions = response.json()
        assert len(transactions) == 0

class TestRateLimiting:
    """Test rate limiting."""

    def test_login_rate_limit(self):
        """Error case: Too many login attempts."""
        # Attempt 6 logins (limit is 5)
        for i in range(6):
            response = client.post("/api/auth/login", json={
                "email": "test@example.com",
                "password": "wrong"
            })

        # 6th attempt should be rate limited
        assert response.status_code == 429
        assert "too many" in response.json()["message"].lower()

    def test_transaction_creation_rate_limit(self):
        """Error case: Too many transactions created."""
        token = get_auth_token()

        # Create 31 transactions (limit is 30/min)
        for i in range(31):
            response = client.post(
                "/api/transactions",
                headers={"Authorization": f"Bearer {token}"},
                json={"amount": 1.0, "description": f"Transaction {i}"}
            )

        # 31st should be rate limited
        assert response.status_code == 429
```

**Target:** 100+ integration tests covering:
- All endpoints (happy path)
- All endpoints (error cases)
- User isolation/security
- Rate limiting
- JWT expiration/refresh

---

## 3. End-to-End Tests

### PWA + API Integration

**Tools:**
- Playwright or Cypress for browser automation
- Test against deployed staging environment

**Test Scenarios:**

```javascript
// tests/e2e/user_journey.spec.js

test('User can sign up, add expenses, and see budget number', async ({ page }) => {
  // Sign up
  await page.goto('https://staging.thenumber.app/signup');
  await page.fill('#email', 'test@example.com');
  await page.fill('#password', 'SecurePass123');
  await page.click('button[type="submit"]');

  // Verify redirected to dashboard
  await expect(page).toHaveURL('/dashboard');

  // Add expense
  await page.click('#add-expense');
  await page.fill('#expense-name', 'Rent');
  await page.fill('#expense-amount', '1500');
  await page.click('#is-fixed');
  await page.click('#save-expense');

  // Verify budget number updated
  const budgetNumber = await page.textContent('#daily-budget');
  expect(parseFloat(budgetNumber)).toBeGreaterThan(0);
});

test('User cannot access another user\'s data', async ({ page }) => {
  // Create User A
  await signUp(page, 'user_a@test.com', 'Pass123');
  await addExpense(page, 'Rent', 1500);
  await logout(page);

  // Create User B
  await signUp(page, 'user_b@test.com', 'Pass456');

  // User B should not see User A's expenses
  const expenses = await page.locator('.expense-item').count();
  expect(expenses).toBe(0);
});

test('PWA works offline', async ({ page }) => {
  await page.goto('https://staging.thenumber.app');
  await login(page, 'test@example.com', 'Pass123');

  // Go offline
  await page.context().setOffline(true);

  // App should still load cached data
  const budgetNumber = await page.textContent('#daily-budget');
  expect(budgetNumber).toBeTruthy();

  // Trying to create transaction should queue it
  await addTransaction(page, 25.50, 'Coffee');

  // Go back online
  await page.context().setOffline(false);

  // Transaction should sync
  await page.waitForTimeout(2000);
  const transactions = await page.locator('.transaction-item').count();
  expect(transactions).toBeGreaterThan(0);
});
```

**Target:** 20-30 E2E tests covering critical user journeys

---

## 4. Security Testing

### Automated Security Tests

**SQL Injection:**
```python
def test_sql_injection_in_expense_name():
    """Try to inject SQL via expense name."""
    token = get_auth_token()
    response = client.post(
        "/api/expenses",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "name": "'; DROP TABLE expenses; --",
            "amount": 100.0,
            "is_fixed": False
        }
    )

    # Should either reject OR sanitize (not execute SQL)
    assert response.status_code in [201, 400]

    # Verify table still exists
    expenses_response = client.get(
        "/api/expenses",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert expenses_response.status_code == 200
```

**XSS Prevention:**
```python
def test_xss_in_transaction_description():
    """Try to inject JavaScript via transaction description."""
    token = get_auth_token()
    response = client.post(
        "/api/transactions",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "amount": 10.0,
            "description": "<script>alert('XSS')</script>"
        }
    )

    # Should accept but escape when rendered
    assert response.status_code == 201

    # Verify description is stored but escaped
    transaction = response.json()
    assert "<script>" not in transaction["description"] or \
           transaction["description"] == "&lt;script&gt;alert('XSS')&lt;/script&gt;"
```

**Authorization Bypass:**
```python
def test_cannot_modify_other_user_expense():
    """User A cannot update User B's expense."""
    user_a_token = create_user("user_a@test.com", "Pass123")
    user_b_token = create_user("user_b@test.com", "Pass456")

    # User A creates expense
    response = client.post(
        "/api/expenses",
        headers={"Authorization": f"Bearer {user_a_token}"},
        json={"name": "Rent", "amount": 1500.0, "is_fixed": True}
    )
    expense_id = response.json()["id"]

    # User B tries to update it
    response = client.put(
        f"/api/expenses/{expense_id}",
        headers={"Authorization": f"Bearer {user_b_token}"},
        json={"amount": 100.0}
    )

    # Should be forbidden
    assert response.status_code == 403
```

**JWT Security:**
```python
def test_tampered_jwt_rejected():
    """Modified JWT should be rejected."""
    token = get_auth_token()

    # Tamper with token
    tampered_token = token[:-5] + "XXXXX"

    response = client.get(
        "/api/budget/number",
        headers={"Authorization": f"Bearer {tampered_token}"}
    )

    assert response.status_code == 401
```

---

## 5. Performance Testing

### Load Testing with Locust

```python
# tests/performance/locustfile.py
from locust import HttpUser, task, between

class BudgetUser(HttpUser):
    wait_time = between(1, 3)

    def on_start(self):
        """Sign up and log in."""
        response = self.client.post("/api/auth/signup", json={
            "email": f"user_{self.userId}@test.com",
            "password": "Test123"
        })
        self.token = response.json()["access_token"]

    @task(3)
    def get_budget_number(self):
        """Get daily budget number (most common operation)."""
        self.client.get(
            "/api/budget/number",
            headers={"Authorization": f"Bearer {self.token}"}
        )

    @task(2)
    def get_transactions(self):
        """Get transaction list."""
        self.client.get(
            "/api/transactions",
            headers={"Authorization": f"Bearer {self.token}"}
        )

    @task(1)
    def create_transaction(self):
        """Create a transaction."""
        self.client.post(
            "/api/transactions",
            headers={"Authorization": f"Bearer {self.token}"},
            json={"amount": 25.50, "description": "Test transaction"}
        )
```

**Run load test:**
```bash
locust -f tests/performance/locustfile.py --host=http://localhost:8000
```

**Targets:**
- Support 100 concurrent users
- Response time < 200ms for 95th percentile
- No errors under normal load

---

## 6. Test Data Management

### Fixtures

```python
# tests/conftest.py
import pytest
from fastapi.testclient import TestClient
from src.api import app

@pytest.fixture
def client():
    """API test client."""
    return TestClient(app)

@pytest.fixture
def auth_token(client):
    """Get authenticated user token."""
    response = client.post("/api/auth/signup", json={
        "email": "test@example.com",
        "password": "SecurePass123"
    })
    return response.json()["access_token"]

@pytest.fixture
def user_with_expenses(client, auth_token):
    """User with predefined expenses."""
    client.post(
        "/api/expenses",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={"name": "Rent", "amount": 1500.0, "is_fixed": True}
    )
    client.post(
        "/api/expenses",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={"name": "Groceries", "amount": 500.0, "is_fixed": False}
    )
    return auth_token

@pytest.fixture(autouse=True)
def reset_database():
    """Reset database before each test."""
    # Clear all tables
    # Recreate schema
    yield
    # Cleanup
```

---

## 7. Continuous Integration

### GitHub Actions Workflow

```yaml
# .github/workflows/test.yml
name: Test

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.13'

      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install -r requirements-dev.txt

      - name: Run linters
        run: |
          ruff check src/ tests/
          mypy src/

      - name: Run unit tests
        run: |
          pytest tests/ -v --cov=src --cov-report=term --cov-report=html

      - name: Check test coverage
        run: |
          coverage report --fail-under=80

      - name: Run security scanner
        run: |
          python agents/security_scanner.py --scan all

      - name: Run skeptical senior dev review
        run: |
          python agents/skeptical_senior_dev.py --review code
```

---

## 8. Test Coverage Goals

### Overall Targets

| Metric | Current | Target |
|--------|---------|--------|
| Line Coverage | ~85% | 90%+ |
| Branch Coverage | ~75% | 85%+ |
| Error Case Tests | ~10% | 30%+ |
| Integration Tests | 0 | 100+ tests |
| E2E Tests | 0 | 20+ scenarios |

### Per-Module Targets

| Module | Current Error % | Target Error % |
|--------|----------------|----------------|
| calculator.py | 3% | 35% |
| database.py | 0% | 30% |
| import_expenses.py | 7% | 30% |
| export_expenses.py | 0% | 30% |
| api.py (new) | 0% | 40% |

---

## 9. Testing Timeline

### Week 1: Foundation
- [ ] Set up FastAPI test client
- [ ] Create test fixtures and utilities
- [ ] Write authentication endpoint tests (happy + error paths)
- [ ] Achieve 30%+ error coverage in auth tests

### Week 2: Core API
- [ ] Write budget endpoint tests
- [ ] Write transaction endpoint tests
- [ ] Write expense endpoint tests
- [ ] Add security tests (SQL injection, XSS, authorization)

### Week 3: Integration & E2E
- [ ] Write integration tests (multi-endpoint flows)
- [ ] Set up Playwright/Cypress
- [ ] Write critical E2E scenarios
- [ ] Add load testing with Locust

### Week 4: Polish
- [ ] Improve error coverage in existing test suites
- [ ] Add missing edge case tests
- [ ] Set up CI/CD pipeline
- [ ] Document testing best practices

---

## 10. Testing Best Practices

### Do's ✅

- **Test error cases:** For every happy path, test 2-3 unhappy paths
- **Test boundaries:** Max/min values, edge of valid range
- **Test security:** Authorization, input validation, SQL injection
- **Use fixtures:** Don't repeat setup code
- **Name tests clearly:** `test_create_expense_with_negative_amount_rejected`
- **Assert specific errors:** Use `pytest.raises` with `match=`
- **Test user isolation:** Verify User A can't access User B's data
- **Mock external dependencies:** Don't hit real APIs in tests

### Don'ts ❌

- **Don't only test happy paths:** This is the #1 AI coding antipattern
- **Don't skip error messages:** Verify the exact error message
- **Don't use bare assertions:** `assert x` → `assert x == expected_value`
- **Don't test implementation:** Test behavior, not internal structure
- **Don't rely on test order:** Each test should be independent
- **Don't commit failing tests:** Fix them or mark as xfail
- **Don't ignore warnings:** They're often bugs waiting to happen

---

## Review Checklist

Before proceeding with API development:
- [ ] Understand why error case testing is critical
- [ ] Commit to 30%+ error coverage goal
- [ ] Have fixtures and test utilities planned
- [ ] Know how to test JWT authentication
- [ ] Know how to test user isolation
- [ ] Understand rate limiting testing approach
- [ ] Have CI/CD pipeline planned

**Status:** Ready for implementation
**Next Step:** Begin API development with TDD approach
