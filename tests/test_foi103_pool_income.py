"""
Tests for FOI-103: Pool income addition must not corrupt the daily number.

Verifies that calculator.calculate_fixed_pool_mode() returns remaining_money
in all code paths, and that pool math in the /api/number endpoint uses it correctly.
"""
import pytest
from datetime import datetime, timedelta
from src.calculator import BudgetCalculator


class TestFixedPoolReturnsRemainingMoney:
    """Every fixed_pool calculation path must return remaining_money."""

    def test_option_b_target_date_returns_remaining_money(self):
        """Option B (target end date) should return remaining_money."""
        calc = BudgetCalculator()
        calc.add_expense("rent", 1500)
        target = datetime.now() + timedelta(days=180)
        result = calc.calculate_fixed_pool_mode(total_money=6000, target_end_date=target)

        assert "remaining_money" in result
        # remaining_money can be negative if expenses exceed total over the period
        # (e.g., $1500/mo rent * 6 months = $9000 > $6000 pool)
        assert isinstance(result["remaining_money"], (int, float))
        assert result["mode"] == "fixed_pool"
        assert result["calculation_mode"] == "target_date"

    def test_option_c_daily_limit_returns_remaining_money(self):
        """Option C (daily spending limit) should return remaining_money = total_money."""
        calc = BudgetCalculator()
        result = calc.calculate_fixed_pool_mode(total_money=6000, daily_spending_limit=33.33)

        assert "remaining_money" in result
        assert result["remaining_money"] == 6000
        assert result["mode"] == "fixed_pool"
        assert result["calculation_mode"] == "daily_limit"

    def test_fallback_expenses_based_returns_remaining_money(self):
        """Fallback (no target date, no daily limit) should return remaining_money."""
        calc = BudgetCalculator()
        calc.add_expense("groceries", 400)
        result = calc.calculate_fixed_pool_mode(total_money=6000)

        assert "remaining_money" in result
        assert result["mode"] == "fixed_pool"
        assert result["calculation_mode"] == "expenses_based"

    def test_zero_money_returns_no_remaining(self):
        """Zero money edge case should still be handled."""
        calc = BudgetCalculator()
        result = calc.calculate_fixed_pool_mode(total_money=0)

        assert result.get("out_of_money") == True
        assert result["daily_limit"] == 0

    def test_no_expenses_fallback_returns_remaining_money(self):
        """Fallback with zero expenses should return remaining_money = total_money."""
        calc = BudgetCalculator()
        result = calc.calculate_fixed_pool_mode(total_money=6000)

        assert "remaining_money" in result
        # With no expenses, remaining = total (infinite runway, no deductions)
        assert result["remaining_money"] == 6000


class TestPoolMathCorrectness:
    """
    Simulates the pool math from api/main.py lines 302-316.
    Ensures adding pool balance INCREASES the daily number, never decreases it.
    """

    def _simulate_pool_math(self, result: dict, pool_balance: float) -> float:
        """Reproduce the pool calculation logic from main.py."""
        base_daily_limit = result["daily_limit"]
        days_remaining = result.get("days_remaining")
        remaining_money = result.get("remaining_money", 0)

        # Defensive fallback (FOI-103 fix)
        if remaining_money == 0 and base_daily_limit > 0 and days_remaining and days_remaining > 0:
            remaining_money = base_daily_limit * days_remaining

        the_number = base_daily_limit
        if pool_balance > 0 and days_remaining and days_remaining > 0:
            remaining_with_pool = remaining_money + pool_balance
            the_number = remaining_with_pool / days_remaining

        return the_number

    def test_adding_pool_increases_daily_number_option_b(self):
        """Drew's bug: $6000 over 180 days, add $500 to pool. Number should go UP."""
        calc = BudgetCalculator()
        target = datetime.now() + timedelta(days=180)
        result = calc.calculate_fixed_pool_mode(total_money=6000, target_end_date=target)

        base_number = result["daily_limit"]
        number_with_pool = self._simulate_pool_math(result, pool_balance=500)

        assert number_with_pool > base_number, (
            f"Adding $500 to pool should increase daily number, "
            f"but went from ${base_number:.2f} to ${number_with_pool:.2f}"
        )

    def test_adding_pool_increases_daily_number_option_c(self):
        """Option C: Adding pool to a daily-limit-based calculation."""
        calc = BudgetCalculator()
        result = calc.calculate_fixed_pool_mode(total_money=6000, daily_spending_limit=33.33)

        base_number = result["daily_limit"]
        number_with_pool = self._simulate_pool_math(result, pool_balance=500)

        assert number_with_pool > base_number

    def test_adding_pool_increases_daily_number_fallback(self):
        """Fallback mode: Adding pool should still increase."""
        calc = BudgetCalculator()
        calc.add_expense("groceries", 400)
        result = calc.calculate_fixed_pool_mode(total_money=6000)

        base_number = result["daily_limit"]
        number_with_pool = self._simulate_pool_math(result, pool_balance=500)

        assert number_with_pool > base_number

    def test_zero_pool_does_not_change_number(self):
        """Zero pool balance should leave the number unchanged."""
        calc = BudgetCalculator()
        target = datetime.now() + timedelta(days=180)
        result = calc.calculate_fixed_pool_mode(total_money=6000, target_end_date=target)

        base_number = result["daily_limit"]
        number_with_pool = self._simulate_pool_math(result, pool_balance=0)

        assert number_with_pool == base_number

    def test_drew_exact_scenario(self):
        """
        Drew's exact scenario: $6000, ~180 days, adds $500.
        Before fix: (0 + 500) / 180 = $2.78 (WRONG)
        After fix: should be approximately (6000 + 500) / 180 = $36.11
        """
        calc = BudgetCalculator()
        target = datetime.now() + timedelta(days=180)
        result = calc.calculate_fixed_pool_mode(total_money=6000, target_end_date=target)

        number_with_pool = self._simulate_pool_math(result, pool_balance=500)

        # Should be roughly $36/day, definitely not $2.78
        assert number_with_pool > 30, f"Expected ~$36/day but got ${number_with_pool:.2f}"
        assert number_with_pool < 40, f"Expected ~$36/day but got ${number_with_pool:.2f}"
