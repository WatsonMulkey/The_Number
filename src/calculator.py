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
        """
        Get total spending for today.
        Excludes income transactions (category='income').
        """
        today = datetime.now().date()
        return sum(
            t.amount for t in self.transactions
            if t.date.date() == today and t.category != 'income'
        )

    def get_period_spending(self, start_date: datetime, end_date: datetime) -> float:
        """
        Get total spending between two dates.
        Excludes income transactions (category='income').
        """
        return sum(
            t.amount for t in self.transactions
            if start_date.date() <= t.date.date() <= end_date.date()
               and t.category != 'income'
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

    def calculate_fixed_pool_mode(self, total_money: float,
                                  target_end_date: Optional[datetime] = None,
                                  daily_spending_limit: Optional[float] = None) -> Dict:
        """
        Calculate fixed pool budget with two options:
        - Option B: Last until a specific date (provide target_end_date)
        - Option C: Spend X per day (provide daily_spending_limit)

        Args:
            total_money: Total amount of money available
            target_end_date: Optional target date to make money last until (Option B)
            daily_spending_limit: Optional daily spending limit to enforce (Option C)

        Returns:
            Dictionary with budget calculations for both options
        """
        if total_money < 0:
            raise ValueError("Total money cannot be negative")

        total_expenses = self.get_total_expenses()
        today = datetime.now().date()  # Use date() to strip time and timezone

        # Handle zero money case
        if total_money <= 0:
            return {
                "total_money": total_money,
                "total_expenses": total_expenses,
                "months_remaining": 0,
                "days_remaining": 0,
                "daily_limit": 0,
                "out_of_money": True,
                "mode": "fixed_pool"
            }

        # Option B: Calculate daily budget to last until target date
        if target_end_date:
            # Convert target_end_date to date object to handle timezone-aware datetimes
            target_date = target_end_date.date() if hasattr(target_end_date, 'date') else target_end_date
            days_until_target = (target_date - today).days
            if days_until_target <= 0:
                raise ValueError("Target end date must be in the future")

            # Calculate daily portion of monthly expenses
            daily_expense_rate = total_expenses / 30

            # Money available after accounting for expenses over the period
            total_expenses_for_period = daily_expense_rate * days_until_target
            remaining_money = total_money - total_expenses_for_period

            # Divide by days to get daily spending limit
            daily_limit_option_b = max(0, remaining_money / days_until_target)
            months_remaining_b = days_until_target / 30

            # Also calculate Option C alternative (if they spent monthly expenses instead)
            if total_expenses > 0:
                daily_expense_rate = total_expenses / 30
                days_if_spending_expenses = total_money / daily_expense_rate
                end_date_option_c = today + timedelta(days=days_if_spending_expenses)
            else:
                days_if_spending_expenses = float('inf')
                end_date_option_c = None

            return {
                "total_money": total_money,
                "total_expenses": total_expenses,
                "daily_limit": daily_limit_option_b,
                "target_end_date": target_end_date.isoformat(),
                "days_remaining": days_until_target,
                "months_remaining": months_remaining_b,
                "alt_daily_expenses": total_expenses / 30 if total_expenses > 0 else 0,
                "alt_end_date": end_date_option_c.isoformat() if end_date_option_c else None,
                "alt_days_remaining": days_if_spending_expenses,
                "mode": "fixed_pool",
                "calculation_mode": "target_date"
            }

        # Option C: Calculate how long it will last at a specific daily limit
        elif daily_spending_limit is not None:
            if daily_spending_limit <= 0:
                raise ValueError("Daily spending limit must be positive")

            days_it_will_last = total_money / daily_spending_limit
            end_date = today + timedelta(days=days_it_will_last)
            months_remaining = days_it_will_last / 30

            # Also calculate Option B alternative
            if total_expenses > 0:
                daily_expense_rate = total_expenses / 30
                days_based_on_expenses = total_money / daily_expense_rate
                alt_daily_limit = total_money / days_based_on_expenses if days_based_on_expenses > 0 else 0
            else:
                days_based_on_expenses = float('inf')
                alt_daily_limit = 0

            return {
                "total_money": total_money,
                "total_expenses": total_expenses,
                "daily_limit": daily_spending_limit,
                "end_date": end_date.isoformat(),
                "days_remaining": days_it_will_last,
                "months_remaining": months_remaining,
                "alt_daily_limit": alt_daily_limit,
                "alt_days_remaining": days_based_on_expenses,
                "mode": "fixed_pool",
                "calculation_mode": "daily_limit"
            }

        # Fallback: No option specified, calculate based on monthly expenses
        else:
            if total_expenses > 0:
                months_remaining = total_money / total_expenses
                days_remaining = months_remaining * 30
                daily_limit = total_money / days_remaining if days_remaining > 0 else 0
                end_date = today + timedelta(days=days_remaining)
            else:
                months_remaining = float('inf')
                days_remaining = float('inf')
                daily_limit = 0
                end_date = None

            return {
                "total_money": total_money,
                "total_expenses": total_expenses,
                "months_remaining": months_remaining,
                "days_remaining": days_remaining,
                "daily_limit": daily_limit,
                "end_date": end_date.isoformat() if end_date else None,
                "mode": "fixed_pool",
                "calculation_mode": "expenses_based"
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
