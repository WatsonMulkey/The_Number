"""
Unit tests for the budget calculator module.
"""

import pytest
from datetime import datetime
from src.calculator import BudgetCalculator, Expense, Transaction


class TestExpense:
    """Test Expense dataclass."""

    def test_create_expense(self):
        """Test creating a valid expense."""
        expense = Expense(name="Rent", amount=1500.0, is_fixed=True)
        assert expense.name == "Rent"
        assert expense.amount == 1500.0
        assert expense.is_fixed is True

    def test_negative_amount_raises_error(self):
        """Test that negative amounts raise ValueError."""
        with pytest.raises(ValueError, match="cannot be negative"):
            Expense(name="Rent", amount=-100.0, is_fixed=True)


class TestTransaction:
    """Test Transaction dataclass."""

    def test_create_transaction(self):
        """Test creating a valid transaction."""
        date = datetime.now()
        txn = Transaction(date=date, amount=25.50, description="Coffee")
        assert txn.date == date
        assert txn.amount == 25.50
        assert txn.description == "Coffee"
        assert txn.category is None

    def test_transaction_with_category(self):
        """Test creating transaction with category."""
        date = datetime.now()
        txn = Transaction(date=date, amount=50.0, description="Dinner", category="Food")
        assert txn.category == "Food"

    def test_negative_transaction_raises_error(self):
        """Test that negative transaction amounts raise ValueError."""
        with pytest.raises(ValueError, match="cannot be negative"):
            Transaction(date=datetime.now(), amount=-10.0, description="Invalid")


class TestBudgetCalculator:
    """Test BudgetCalculator class."""

    def test_add_expense(self):
        """Test adding expenses."""
        calc = BudgetCalculator()
        calc.add_expense("Rent", 1500.0, is_fixed=True)
        calc.add_expense("Groceries", 300.0, is_fixed=False)

        assert len(calc.expenses) == 2
        assert calc.get_total_expenses() == 1800.0

    def test_add_transaction(self):
        """Test adding transactions."""
        calc = BudgetCalculator()
        calc.add_transaction(25.0, "Coffee")
        calc.add_transaction(50.0, "Lunch", category="Food")

        assert len(calc.transactions) == 2

    def test_get_today_spending(self):
        """Test getting today's spending."""
        calc = BudgetCalculator()
        calc.add_transaction(25.0, "Coffee")
        calc.add_transaction(15.0, "Snack")

        assert calc.get_today_spending() == 40.0

    def test_calculate_paycheck_mode(self):
        """Test paycheck mode calculation."""
        calc = BudgetCalculator()
        calc.add_expense("Rent", 1500.0)
        calc.add_expense("Utilities", 200.0)

        result = calc.calculate_paycheck_mode(
            monthly_income=3000.0,
            days_until_paycheck=15
        )

        assert result["total_income"] == 3000.0
        assert result["total_expenses"] == 1700.0
        assert result["remaining_money"] == 1300.0
        assert result["days_remaining"] == 15
        assert result["daily_limit"] == pytest.approx(86.67, rel=0.01)
        assert result["mode"] == "paycheck"

    def test_paycheck_mode_negative_income_raises_error(self):
        """Test that negative income raises ValueError."""
        calc = BudgetCalculator()
        with pytest.raises(ValueError, match="cannot be negative"):
            calc.calculate_paycheck_mode(monthly_income=-1000.0, days_until_paycheck=15)

    def test_paycheck_mode_zero_days_raises_error(self):
        """Test that zero days raises ValueError."""
        calc = BudgetCalculator()
        with pytest.raises(ValueError, match="must be positive"):
            calc.calculate_paycheck_mode(monthly_income=3000.0, days_until_paycheck=0)

    def test_calculate_fixed_pool_mode(self):
        """Test fixed pool mode calculation."""
        calc = BudgetCalculator()
        calc.add_expense("Rent", 1500.0)
        calc.add_expense("Food", 500.0)

        result = calc.calculate_fixed_pool_mode(total_money=6000.0)

        assert result["total_money"] == 6000.0
        assert result["monthly_expenses"] == 2000.0
        assert result["months_remaining"] == 3.0
        assert result["days_remaining"] == 90.0
        assert result["daily_limit"] == pytest.approx(66.67, rel=0.01)
        assert result["mode"] == "fixed_pool"

    def test_fixed_pool_mode_no_expenses(self):
        """Test fixed pool mode with no expenses."""
        calc = BudgetCalculator()
        result = calc.calculate_fixed_pool_mode(total_money=5000.0)

        assert result["monthly_expenses"] == 0.0
        assert result["months_remaining"] == float('inf')
        assert result["days_remaining"] == float('inf')
        assert result["daily_limit"] == 0.0

    def test_fixed_pool_mode_negative_money_raises_error(self):
        """Test that negative total money raises ValueError."""
        calc = BudgetCalculator()
        with pytest.raises(ValueError, match="cannot be negative"):
            calc.calculate_fixed_pool_mode(total_money=-100.0)

    def test_get_number_paycheck_mode(self):
        """Test get_number method with paycheck mode."""
        calc = BudgetCalculator()
        calc.add_expense("Rent", 1000.0)

        number = calc.get_number(
            mode="paycheck",
            monthly_income=2000.0,
            days_until_paycheck=10
        )

        assert number == 100.0  # (2000 - 1000) / 10

    def test_get_number_fixed_pool_mode(self):
        """Test get_number method with fixed pool mode."""
        calc = BudgetCalculator()
        calc.add_expense("Rent", 1000.0)

        number = calc.get_number(
            mode="fixed_pool",
            total_money=3000.0
        )

        assert number == pytest.approx(33.33, rel=0.01)  # 3000 / 30 days (3000/1000 months * 30)

    def test_get_number_invalid_mode_raises_error(self):
        """Test that invalid mode raises ValueError."""
        calc = BudgetCalculator()
        with pytest.raises(ValueError, match="Invalid mode"):
            calc.get_number(mode="invalid")

    def test_get_period_spending(self):
        """Test getting spending for a date range."""
        calc = BudgetCalculator()
        date1 = datetime(2024, 1, 1)
        date2 = datetime(2024, 1, 15)
        date3 = datetime(2024, 2, 1)

        calc.add_transaction(100.0, "Item 1", date=date1)
        calc.add_transaction(50.0, "Item 2", date=date2)
        calc.add_transaction(75.0, "Item 3", date=date3)

        # Get spending for January only
        total = calc.get_period_spending(
            start_date=datetime(2024, 1, 1),
            end_date=datetime(2024, 1, 31)
        )

        assert total == 150.0  # First two transactions only
