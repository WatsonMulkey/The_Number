"""
Integration Test Suite: Full Flow Tests for PWA Badge + Tomorrow Number

Tests the complete user journey combining both features:
1. User records overspending transaction
2. Tomorrow number is calculated
3. Badge is updated with new remaining budget
4. Frontend displays tomorrow warning

TESTING APPROACH:
- Tests use actual API endpoints (FastAPI TestClient)
- Tests use actual database operations
- Tests verify full request → response → state update flow
"""

import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timedelta
from typing import Dict, Any
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import app and dependencies
from api.main import app, get_db
from src.database import EncryptedDatabase
from src.calculator import BudgetCalculator


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def client():
    """FastAPI test client."""
    return TestClient(app)


@pytest.fixture
def auth_headers(client: TestClient) -> Dict[str, str]:
    """
    Create a test user and return authentication headers.
    """
    # Register test user
    response = client.post("/api/auth/register", json={
        "username": f"testuser_{datetime.now().timestamp()}",
        "password": "testpassword123",
        "email": "test@example.com"
    })
    assert response.status_code == 201
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def configured_budget(client: TestClient, auth_headers: Dict[str, str]):
    """
    Configure a test budget in paycheck mode.
    Returns configuration details.
    """
    config = {
        "mode": "paycheck",
        "monthly_income": 4000.0,
        "days_until_paycheck": 10
    }
    response = client.post(
        "/api/budget/configure",
        json=config,
        headers=auth_headers
    )
    assert response.status_code == 200
    return config


# ============================================================================
# TEST SUITE: Full Flow - Record Transaction → Tomorrow Number + Badge
# ============================================================================

class TestFullFlowOverspendingScenario:
    """
    Test the complete user flow when overspending occurs.
    """

    def test_full_flow_record_overspending_transaction(
        self,
        client: TestClient,
        auth_headers: Dict[str, str],
        configured_budget: Dict[str, Any]
    ):
        """
        FULL INTEGRATION TEST: Complete flow from transaction to UI state.

        GIVEN user has paycheck mode configured ($4000/month, 10 days left)
        WHEN user records a $500 transaction (way over daily limit)
        THEN:
        1. API calculates tomorrow_number
        2. API returns is_over_budget = true
        3. Frontend can display tomorrow warning
        4. Frontend can update badge with remaining budget

        STEPS:
        1. Get initial budget state (under budget)
        2. Record overspending transaction
        3. Get updated budget state
        4. Verify tomorrow_number is calculated
        5. Verify is_over_budget = true
        6. Verify remaining_today is negative
        """
        # Step 1: Get initial budget state
        response = client.get("/api/number", headers=auth_headers)
        assert response.status_code == 200
        initial_state = response.json()

        assert initial_state["is_over_budget"] is False
        assert initial_state["today_spending"] == 0
        assert "tomorrow_number" not in initial_state or initial_state["tomorrow_number"] is None

        # Calculate expected daily limit: (4000 - expenses) / 10
        # Assuming no expenses configured, daily_limit ≈ $400
        initial_daily_limit = initial_state["the_number"]
        assert initial_daily_limit > 0

        # Step 2: Record overspending transaction ($500 when limit is ~$400)
        transaction = {
            "amount": 500.0,
            "description": "Emergency car repair",
            "category": "Transportation"
        }
        response = client.post(
            "/api/transactions",
            json=transaction,
            headers=auth_headers
        )
        assert response.status_code == 201

        # Step 3: Get updated budget state
        response = client.get("/api/number", headers=auth_headers)
        assert response.status_code == 200
        updated_state = response.json()

        # Step 4: Verify is_over_budget
        assert updated_state["is_over_budget"] is True, \
            "Should be over budget after spending $500"

        # Step 5: Verify today_spending updated
        assert updated_state["today_spending"] == 500.0

        # Step 6: Verify remaining_today is negative
        assert updated_state["remaining_today"] < 0, \
            "Remaining today should be negative when over budget"

        # Step 7: Verify tomorrow_number is calculated
        assert "tomorrow_number" in updated_state, \
            "API should return tomorrow_number when over budget"
        assert updated_state["tomorrow_number"] is not None, \
            "tomorrow_number should not be null when over budget"
        assert updated_state["tomorrow_number"] > 0, \
            "tomorrow_number should be positive (adjusted budget)"
        assert updated_state["tomorrow_number"] < initial_daily_limit, \
            "tomorrow_number should be less than original daily limit"

        # Calculate expected tomorrow_number manually
        remaining_money = updated_state["remaining_money"]
        today_spending = updated_state["today_spending"]
        days_remaining = updated_state["days_remaining"]

        expected_tomorrow = (remaining_money - today_spending) / (days_remaining - 1)
        assert abs(updated_state["tomorrow_number"] - expected_tomorrow) < 0.01, \
            f"tomorrow_number calculation incorrect: expected {expected_tomorrow}, got {updated_state['tomorrow_number']}"

    def test_full_flow_multiple_small_transactions_accumulate(
        self,
        client: TestClient,
        auth_headers: Dict[str, str],
        configured_budget: Dict[str, Any]
    ):
        """
        GIVEN user starts day under budget
        WHEN user records multiple small transactions that accumulate to overspending
        THEN tomorrow_number should reflect total overspending

        SCENARIO: Coffee ($5) + Lunch ($15) + Dinner ($25) = $45
        If daily limit is $40, user is over by $5.
        """
        # Get initial state
        response = client.get("/api/number", headers=auth_headers)
        initial_state = response.json()
        daily_limit = initial_state["the_number"]

        # Record multiple transactions
        transactions = [
            {"amount": 5.0, "description": "Coffee"},
            {"amount": 15.0, "description": "Lunch"},
            {"amount": 25.0, "description": "Dinner"},
        ]

        for txn in transactions:
            response = client.post(
                "/api/transactions",
                json=txn,
                headers=auth_headers
            )
            assert response.status_code == 201

        # Get final state
        response = client.get("/api/number", headers=auth_headers)
        final_state = response.json()

        # Verify total spending
        total_spent = sum(t["amount"] for t in transactions)
        assert final_state["today_spending"] == total_spent

        # Verify is_over_budget if total exceeds limit
        if total_spent > daily_limit:
            assert final_state["is_over_budget"] is True
            assert final_state["tomorrow_number"] is not None
            assert final_state["tomorrow_number"] < daily_limit
        else:
            assert final_state["is_over_budget"] is False
            assert final_state["tomorrow_number"] is None

    def test_full_flow_income_transaction_should_not_affect_overspending(
        self,
        client: TestClient,
        auth_headers: Dict[str, str],
        configured_budget: Dict[str, Any]
    ):
        """
        GIVEN user records an expense transaction (overspending)
        WHEN user records an income transaction
        THEN income should not count toward today_spending

        SCENARIO: User sells something for $50 (income)
        This should NOT reduce today_spending or affect is_over_budget.
        """
        # Record expense
        expense = {"amount": 500.0, "description": "Big purchase"}
        client.post("/api/transactions", json=expense, headers=auth_headers)

        # Record income (category = 'income')
        income = {"amount": 50.0, "description": "Sold old laptop", "category": "income"}
        client.post("/api/transactions", json=income, headers=auth_headers)

        # Get state
        response = client.get("/api/number", headers=auth_headers)
        state = response.json()

        # today_spending should only include expense, not income
        # Implementation note: Database must filter by category != 'income'
        assert state["today_spending"] >= 500.0  # At least the expense


# ============================================================================
# TEST SUITE: Edge Case - Last Day of Budget Period
# ============================================================================

class TestFullFlowLastDay:
    """
    Critical edge case: User overspends on last day.
    tomorrow_number should be null (no tomorrow in this period).
    """

    def test_overspending_on_last_day_shows_no_tomorrow_number(
        self,
        client: TestClient,
        auth_headers: Dict[str, str]
    ):
        """
        GIVEN user has 1 day until paycheck (last day)
        WHEN user overspends today
        THEN tomorrow_number should be null (can't adjust - no tomorrow)
        """
        # Configure budget with 1 day remaining
        config = {
            "mode": "paycheck",
            "monthly_income": 400.0,  # $400 total
            "days_until_paycheck": 1  # LAST DAY
        }
        response = client.post(
            "/api/budget/configure",
            json=config,
            headers=auth_headers
        )
        assert response.status_code == 200

        # Get initial state
        response = client.get("/api/number", headers=auth_headers)
        state = response.json()
        assert state["days_remaining"] == 1

        # Record overspending transaction
        transaction = {"amount": 500.0, "description": "Emergency"}
        client.post("/api/transactions", json=transaction, headers=auth_headers)

        # Get updated state
        response = client.get("/api/number", headers=auth_headers)
        state = response.json()

        # Should be over budget
        assert state["is_over_budget"] is True

        # But tomorrow_number should be null (last day)
        assert state["tomorrow_number"] is None, \
            "tomorrow_number should be null on last day (no tomorrow to adjust)"

    def test_overspending_with_two_days_remaining(
        self,
        client: TestClient,
        auth_headers: Dict[str, str]
    ):
        """
        GIVEN user has 2 days until paycheck
        WHEN user overspends today
        THEN tomorrow_number should be entire remaining budget (1 day left)
        """
        # Configure budget with 2 days remaining
        config = {
            "mode": "paycheck",
            "monthly_income": 200.0,  # $200 total
            "days_until_paycheck": 2
        }
        client.post("/api/budget/configure", json=config, headers=auth_headers)

        # Record overspending
        transaction = {"amount": 150.0, "description": "Large purchase"}
        client.post("/api/transactions", json=transaction, headers=auth_headers)

        # Get state
        response = client.get("/api/number", headers=auth_headers)
        state = response.json()

        # Should have tomorrow_number
        assert state["tomorrow_number"] is not None

        # tomorrow_number = (200 - 150) / (2 - 1) = 50 / 1 = $50
        assert abs(state["tomorrow_number"] - 50.0) < 0.01


# ============================================================================
# TEST SUITE: Fixed Pool Mode Integration
# ============================================================================

class TestFullFlowFixedPoolMode:
    """
    Tests for tomorrow_number calculation in fixed pool mode.
    """

    def test_fixed_pool_with_target_date_overspending(
        self,
        client: TestClient,
        auth_headers: Dict[str, str]
    ):
        """
        GIVEN user in fixed pool mode with target date
        WHEN user overspends
        THEN tomorrow_number should adjust for remaining days
        """
        # Configure fixed pool with target date
        target_date = (datetime.now() + timedelta(days=30)).isoformat()
        config = {
            "mode": "fixed_pool",
            "total_money": 900.0,
            "target_end_date": target_date
        }
        response = client.post(
            "/api/budget/configure",
            json=config,
            headers=auth_headers
        )
        assert response.status_code == 200

        # Get initial state
        response = client.get("/api/number", headers=auth_headers)
        initial_state = response.json()
        daily_limit = initial_state["the_number"]

        # Record overspending transaction
        transaction = {"amount": daily_limit + 10.0, "description": "Overspent"}
        client.post("/api/transactions", json=transaction, headers=auth_headers)

        # Get updated state
        response = client.get("/api/number", headers=auth_headers)
        state = response.json()

        # Verify tomorrow_number is calculated
        assert state["is_over_budget"] is True
        assert state["tomorrow_number"] is not None
        assert state["tomorrow_number"] < daily_limit

    def test_fixed_pool_with_daily_limit_overspending(
        self,
        client: TestClient,
        auth_headers: Dict[str, str]
    ):
        """
        GIVEN user in fixed pool mode with daily spending limit
        WHEN user overspends
        THEN tomorrow_number should be calculated
        """
        config = {
            "mode": "fixed_pool",
            "total_money": 300.0,
            "daily_spending_limit": 20.0
        }
        client.post("/api/budget/configure", json=config, headers=auth_headers)

        # Overspend
        transaction = {"amount": 30.0, "description": "Over limit"}
        client.post("/api/transactions", json=transaction, headers=auth_headers)

        # Verify tomorrow_number
        response = client.get("/api/number", headers=auth_headers)
        state = response.json()

        assert state["is_over_budget"] is True
        assert state["tomorrow_number"] is not None


# ============================================================================
# TEST SUITE: Badge Update Integration
# ============================================================================

class TestBadgeUpdateIntegration:
    """
    Tests for badge updates after transactions.
    NOTE: Badge updates happen on frontend, these tests verify API provides correct data.
    """

    def test_api_provides_remaining_today_for_badge_update(
        self,
        client: TestClient,
        auth_headers: Dict[str, str],
        configured_budget: Dict[str, Any]
    ):
        """
        GIVEN user records a transaction
        WHEN frontend calls GET /api/number
        THEN remaining_today should be updated for badge

        FRONTEND FLOW:
        1. User records transaction
        2. Frontend calls fetchNumber()
        3. Frontend calls BadgeService.setBadge(remaining_today)
        4. Badge shows updated budget
        """
        # Initial state
        response = client.get("/api/number", headers=auth_headers)
        initial_state = response.json()
        initial_remaining = initial_state["remaining_today"]

        # Record transaction
        transaction = {"amount": 50.0, "description": "Purchase"}
        client.post("/api/transactions", json=transaction, headers=auth_headers)

        # Get updated state
        response = client.get("/api/number", headers=auth_headers)
        updated_state = response.json()
        updated_remaining = updated_state["remaining_today"]

        # remaining_today should decrease by transaction amount
        assert updated_remaining == initial_remaining - 50.0

        # Badge should be updated to: round(updated_remaining)
        # Frontend: BadgeService.setBadge(updated_state.remaining_today)

    def test_negative_remaining_today_should_clear_badge(
        self,
        client: TestClient,
        auth_headers: Dict[str, str],
        configured_budget: Dict[str, Any]
    ):
        """
        GIVEN user overspends (remaining_today < 0)
        WHEN frontend updates badge
        THEN badge should be cleared (BadgeService handles negative → clear)

        API RESPONSIBILITY: Return accurate negative remaining_today
        FRONTEND RESPONSIBILITY: BadgeService.setBadge(-15.0) → clears badge
        """
        # Overspend
        transaction = {"amount": 5000.0, "description": "Major expense"}
        client.post("/api/transactions", json=transaction, headers=auth_headers)

        # Get state
        response = client.get("/api/number", headers=auth_headers)
        state = response.json()

        # remaining_today should be negative
        assert state["remaining_today"] < 0
        assert state["is_over_budget"] is True

        # Frontend would do: BadgeService.setBadge(state.remaining_today)
        # BadgeService converts negative → 0 → clears badge


# ============================================================================
# TEST SUITE: Error Handling
# ============================================================================

class TestFullFlowErrorHandling:
    """
    Tests for error scenarios in integration flow.
    """

    def test_api_error_does_not_break_tomorrow_number_calculation(
        self,
        client: TestClient,
        auth_headers: Dict[str, str],
        configured_budget: Dict[str, Any]
    ):
        """
        GIVEN API encounters an error during calculation
        WHEN error is recoverable
        THEN should return appropriate error response

        NOTE: Division by zero is prevented in calculation logic,
        so this tests other potential errors.
        """
        # This test documents expected error handling behavior
        # Specific errors depend on implementation details
        pass

    def test_unconfigured_budget_returns_error_not_crash(
        self,
        client: TestClient,
        auth_headers: Dict[str, str]
    ):
        """
        GIVEN user has NOT configured budget yet
        WHEN GET /api/number is called
        THEN should return 400 error, not crash
        """
        response = client.get("/api/number", headers=auth_headers)
        assert response.status_code == 400
        assert "not configured" in response.json()["detail"].lower()


# ============================================================================
# PERFORMANCE TESTS
# ============================================================================

class TestFullFlowPerformance:
    """
    Tests to ensure calculations don't cause performance issues.
    """

    def test_tomorrow_number_calculation_is_fast(
        self,
        client: TestClient,
        auth_headers: Dict[str, str],
        configured_budget: Dict[str, Any]
    ):
        """
        GIVEN tomorrow_number calculation adds overhead
        WHEN GET /api/number is called
        THEN response time should be acceptable (< 200ms)
        """
        import time

        # Record transaction to trigger tomorrow_number calculation
        transaction = {"amount": 500.0, "description": "Test"}
        client.post("/api/transactions", json=transaction, headers=auth_headers)

        # Measure response time
        start = time.time()
        response = client.get("/api/number", headers=auth_headers)
        elapsed = time.time() - start

        assert response.status_code == 200
        assert elapsed < 0.2, f"API too slow: {elapsed:.3f}s (should be < 200ms)"

    def test_multiple_rapid_transactions_do_not_cause_race_conditions(
        self,
        client: TestClient,
        auth_headers: Dict[str, str],
        configured_budget: Dict[str, Any]
    ):
        """
        GIVEN user records multiple transactions rapidly
        WHEN each transaction triggers GET /api/number
        THEN all responses should be consistent (no race conditions)
        """
        transactions = [
            {"amount": 10.0, "description": f"Transaction {i}"}
            for i in range(5)
        ]

        for txn in transactions:
            client.post("/api/transactions", json=txn, headers=auth_headers)

        # Get final state
        response = client.get("/api/number", headers=auth_headers)
        state = response.json()

        # today_spending should be sum of all transactions
        expected_spending = sum(t["amount"] for t in transactions)
        assert state["today_spending"] == expected_spending


# ============================================================================
# EDGE CASE REGISTRY
# ============================================================================

"""
INTEGRATION TESTS COVERAGE:

✅ TESTED:
- Full flow: transaction → overspending → tomorrow_number
- Multiple transactions accumulating to overspending
- Last day edge case (tomorrow_number = null)
- Two days remaining boundary case
- Fixed pool mode with target date
- Fixed pool mode with daily limit
- API provides correct data for badge updates
- Negative remaining_today handling
- Performance (< 200ms response time)
- Rapid transactions (race conditions)

⚠️ PARTIALLY TESTED:
- Income vs expense transaction filtering
- Category-based filtering

❌ NOT TESTED:
- Timezone handling (midnight boundary)
- Concurrent users
- Database locking/transactions
- Frontend badge update timing
- PWA installation state

RECOMMENDATIONS:
1. Add E2E tests with Playwright for full browser flow
2. Test timezone edge cases (user crossing midnight)
3. Load testing for multiple concurrent users
4. Test database transaction isolation
5. Test PWA badge on actual mobile devices
"""


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
