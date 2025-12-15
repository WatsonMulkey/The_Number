"""
Core budget calculation engine for The Number app.

This module handles two budgeting modes:
1. Paycheck Mode: Calculate daily spending based on income and days until next paycheck
2. Fixed Pool Mode: Calculate how long a fixed amount of money will last
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass

# Security and validation constants
MAX_STRING_LENGTH = 200  # Maximum length for user input strings
MAX_AMOUNT = 10_000_000  # Maximum dollar amount ($10 million)
MAX_DAYS_UNTIL_PAYCHECK = 365  # Maximum days (1 year)


@dataclass
class Expense:
    """Represents a budget expense (fixed or variable)."""
    name: str
    amount: float
    is_fixed: bool  # True for monthly fixed expenses, False for variable

    def __post_init__(self):
        if self.amount < 0:
            raise ValueError(f"Expense amount cannot be negative: {self.amount}")
        if self.amount > MAX_AMOUNT:
            raise ValueError(f"Expense amount exceeds maximum (${MAX_AMOUNT:,}): {self.amount}")


@dataclass
class Transaction:
    """Represents a daily spending transaction."""
    date: datetime
    amount: float
    description: str
    category: Optional[str] = None

    def __post_init__(self):
        if self.amount < 0:
            raise ValueError(f"Transaction amount cannot be negative: {self.amount}")
        if self.amount > MAX_AMOUNT:
            raise ValueError(f"Transaction amount exceeds maximum (${MAX_AMOUNT:,}): {self.amount}")


class BudgetCalculator:
    """Calculates daily spending limits based on income and expenses."""

    def __init__(self):
        self.expenses: List[Expense] = []
        self.transactions: List[Transaction] = []

    def add_expense(self, name: str, amount: float, is_fixed: bool = True) -> None:
        """Add a budget expense."""
        expense = Expense(name=name, amount=amount, is_fixed=is_fixed)
        self.expenses.append(expense)

    def add_transaction(self, amount: float, description: str,
                       date: Optional[datetime] = None, category: Optional[str] = None) -> None:
        """Record a spending transaction."""
        if date is None:
            date = datetime.now()
        transaction = Transaction(date=date, amount=amount, description=description, category=category)
        self.transactions.append(transaction)

    def get_total_expenses(self) -> float:
        """Calculate total monthly expenses."""
        return sum(expense.amount for expense in self.expenses)

    def get_today_spending(self) -> float:
        """Get total spending for today."""
        today = datetime.now().date()
        return sum(
            t.amount for t in self.transactions
            if t.date.date() == today
        )

    def get_period_spending(self, start_date: datetime, end_date: datetime) -> float:
        """Get total spending between two dates."""
        return sum(
            t.amount for t in self.transactions
            if start_date.date() <= t.date.date() <= end_date.date()
        )

    def calculate_paycheck_mode(self, monthly_income: float, days_until_paycheck: int) -> Dict[str, float]:
        """
        Calculate daily spending limit based on monthly income and days until next paycheck.

        Args:
            monthly_income: Total monthly income
            days_until_paycheck: Number of days until next paycheck

        Returns:
            Dictionary with:
                - total_income: Monthly income
                - total_expenses: Sum of all expenses
                - remaining_money: Money left after expenses
                - days_remaining: Days until next paycheck
                - daily_limit: Amount that can be spent per day
        """
        if monthly_income < 0:
            raise ValueError("Monthly income cannot be negative")
        if days_until_paycheck <= 0:
            raise ValueError("Days until paycheck must be positive")
        if days_until_paycheck > MAX_DAYS_UNTIL_PAYCHECK:
            raise ValueError(f"Days until paycheck cannot exceed {MAX_DAYS_UNTIL_PAYCHECK}")

        total_expenses = self.get_total_expenses()
        remaining_money = monthly_income - total_expenses
        is_deficit = remaining_money < 0
        daily_limit = max(0, remaining_money / days_until_paycheck)

        return {
            "total_income": monthly_income,
            "total_expenses": total_expenses,
            "remaining_money": remaining_money,
            "days_remaining": days_until_paycheck,
            "daily_limit": daily_limit,
            "is_deficit": is_deficit,
            "deficit_amount": abs(min(0, remaining_money)),
            "mode": "paycheck"
        }

    def calculate_fixed_pool_mode(self, total_money: float) -> Dict[str, float]:
        """
        Calculate how long a fixed amount of money will last with current expenses.

        Args:
            total_money: Total amount of money available

        Returns:
            Dictionary with:
                - total_money: Total money available
                - monthly_expenses: Sum of monthly expenses
                - months_remaining: How many months the money will last
                - days_remaining: How many days the money will last
                - daily_limit: Recommended daily spending limit
        """
        if total_money < 0:
            raise ValueError("Total money cannot be negative")

        total_expenses = self.get_total_expenses()

        # Handle zero money case
        if total_money <= 0:
            return {
                "total_money": total_money,
                "monthly_expenses": total_expenses,
                "months_remaining": 0,
                "days_remaining": 0,
                "daily_limit": 0,
                "out_of_money": True,
                "mode": "fixed_pool"
            }

        # Calculate how long the money will last
        if total_expenses > 0:
            months_remaining = total_money / total_expenses
            days_remaining = months_remaining * 30  # Approximate
            daily_limit = total_money / days_remaining if days_remaining > 0 else 0
        else:
            # No expenses, money lasts forever (theoretically)
            months_remaining = float('inf')
            days_remaining = float('inf')
            daily_limit = 0

        return {
            "total_money": total_money,
            "monthly_expenses": total_expenses,
            "months_remaining": months_remaining,
            "days_remaining": days_remaining,
            "daily_limit": daily_limit,
            "mode": "fixed_pool"
        }

    def get_number(self, mode: str, **kwargs) -> float:
        """
        Get "The Number" - the daily spending limit.

        Args:
            mode: Either 'paycheck' or 'fixed_pool'
            **kwargs: Arguments for the selected mode
                - For paycheck mode: monthly_income, days_until_paycheck
                - For fixed_pool mode: total_money

        Returns:
            The daily spending limit (The Number)
        """
        if mode == "paycheck":
            result = self.calculate_paycheck_mode(
                monthly_income=kwargs.get('monthly_income', 0),
                days_until_paycheck=kwargs.get('days_until_paycheck', 1)
            )
        elif mode == "fixed_pool":
            result = self.calculate_fixed_pool_mode(
                total_money=kwargs.get('total_money', 0)
            )
        else:
            raise ValueError(f"Invalid mode: {mode}. Must be 'paycheck' or 'fixed_pool'")

        return result['daily_limit']
