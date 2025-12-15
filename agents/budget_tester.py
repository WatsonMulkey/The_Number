#!/usr/bin/env python3
"""
Budget Tester Agent for The Number App

This agent performs comprehensive testing of budget calculations with edge cases,
boundary conditions, and real-world scenarios to ensure accuracy and reliability.

Usage:
    python agents/budget_tester.py [--mode all|paycheck|fixed_pool] [--verbose]
"""

import sys
import os
from pathlib import Path
from typing import Dict, List, Tuple
from decimal import Decimal

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from calculator import BudgetCalculator, Expense


class BudgetTesterAgent:
    """Agent that tests budget calculations with comprehensive edge cases."""

    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.test_results: List[Dict] = []
        self.failures: List[Dict] = []

    def log(self, message: str, level: str = "INFO"):
        """Log message if verbose mode is enabled."""
        if self.verbose or level == "ERROR":
            prefix = {
                "INFO": "[*]",
                "PASS": "[+]",
                "FAIL": "[-]",
                "ERROR": "[!]"
            }.get(level, "[?]")
            print(f"{prefix} {message}")

    def run_test(self, test_name: str, test_func) -> bool:
        """Run a single test and record results."""
        try:
            test_func()
            self.log(f"PASS: {test_name}", "PASS")
            self.test_results.append({
                "name": test_name,
                "status": "PASS",
                "error": None
            })
            return True
        except AssertionError as e:
            self.log(f"FAIL: {test_name} - {str(e)}", "FAIL")
            self.failures.append({
                "name": test_name,
                "error": str(e)
            })
            self.test_results.append({
                "name": test_name,
                "status": "FAIL",
                "error": str(e)
            })
            return False
        except Exception as e:
            self.log(f"ERROR: {test_name} - {str(e)}", "ERROR")
            self.failures.append({
                "name": test_name,
                "error": f"Unexpected error: {str(e)}"
            })
            self.test_results.append({
                "name": test_name,
                "status": "ERROR",
                "error": str(e)
            })
            return False

    # ===== PAYCHECK MODE TESTS =====

    def test_paycheck_basic_calculation(self):
        """Test basic paycheck mode calculation."""
        calc = BudgetCalculator()
        calc.add_expense("Rent", 1500.0, True)
        calc.add_expense("Groceries", 500.0, False)

        result = calc.calculate_paycheck_mode(monthly_income=3000.0, days_until_paycheck=15)

        # Total expenses: $2000
        # Remaining: $1000
        # Daily limit: $1000 / 15 = $66.67
        assert abs(result['daily_limit'] - 66.67) < 0.01, \
            f"Expected daily limit ~66.67, got {result['daily_limit']}"
        assert result['remaining_money'] == 1000.0

    def test_paycheck_deficit_scenario(self):
        """Test paycheck mode when expenses exceed income."""
        calc = BudgetCalculator()
        calc.add_expense("Rent", 2000.0, True)
        calc.add_expense("Utilities", 1500.0, False)

        result = calc.calculate_paycheck_mode(monthly_income=2000.0, days_until_paycheck=14)

        # Expenses ($3500) > Income ($2000)
        # Deficit: -$1500
        assert result['is_deficit'] is True, "Should detect deficit"
        assert result['daily_limit'] == 0, "Daily limit should be 0 in deficit"
        assert result['remaining_money'] == -1500.0
        assert result['deficit_amount'] == 1500.0

    def test_paycheck_zero_expenses(self):
        """Test paycheck mode with no expenses."""
        calc = BudgetCalculator()

        result = calc.calculate_paycheck_mode(monthly_income=3000.0, days_until_paycheck=30)

        # All income available
        assert result['daily_limit'] == 100.0, \
            f"Expected daily limit 100.0, got {result['daily_limit']}"
        assert result['remaining_money'] == 3000.0

    def test_paycheck_one_day_remaining(self):
        """Test paycheck mode with only 1 day until paycheck."""
        calc = BudgetCalculator()
        calc.add_expense("Rent", 1000.0, True)

        result = calc.calculate_paycheck_mode(monthly_income=2000.0, days_until_paycheck=1)

        # Remaining: $1000, Days: 1
        assert result['daily_limit'] == 1000.0

    def test_paycheck_max_days(self):
        """Test paycheck mode with maximum allowed days."""
        calc = BudgetCalculator()

        try:
            # Should accept 365 days
            result = calc.calculate_paycheck_mode(monthly_income=3000.0, days_until_paycheck=365)
            assert result['days_remaining'] == 365
        except ValueError:
            raise AssertionError("Should accept 365 days")

    def test_paycheck_invalid_days(self):
        """Test paycheck mode rejects invalid days."""
        calc = BudgetCalculator()

        # Test zero days
        try:
            calc.calculate_paycheck_mode(monthly_income=3000.0, days_until_paycheck=0)
            raise AssertionError("Should reject 0 days")
        except ValueError:
            pass  # Expected

        # Test negative days
        try:
            calc.calculate_paycheck_mode(monthly_income=3000.0, days_until_paycheck=-5)
            raise AssertionError("Should reject negative days")
        except ValueError:
            pass  # Expected

        # Test days > 365
        try:
            calc.calculate_paycheck_mode(monthly_income=3000.0, days_until_paycheck=366)
            raise AssertionError("Should reject days > 365")
        except ValueError:
            pass  # Expected

    def test_paycheck_floating_point_precision(self):
        """Test paycheck mode handles floating point precision correctly."""
        calc = BudgetCalculator()
        calc.add_expense("Rent", 1234.56, True)

        result = calc.calculate_paycheck_mode(monthly_income=2345.67, days_until_paycheck=17)

        # Remaining: 2345.67 - 1234.56 = 1111.11
        # Daily: 1111.11 / 17 = 65.359...
        expected_remaining = 1111.11
        assert abs(result['remaining_money'] - expected_remaining) < 0.01

    # ===== FIXED POOL MODE TESTS =====

    def test_fixed_pool_basic_calculation(self):
        """Test basic fixed pool mode calculation."""
        calc = BudgetCalculator()
        calc.add_expense("Rent", 1500.0, True)

        result = calc.calculate_fixed_pool_mode(total_money=10000.0)

        # Monthly expenses: $1500
        # Months remaining: 10000 / 1500 = 6.67 months
        # Days: 6.67 * 30 = 200 days
        # Daily: 10000 / 200 = 50
        assert abs(result['months_remaining'] - 6.67) < 0.01
        assert abs(result['days_remaining'] - 200) < 1

    def test_fixed_pool_zero_money(self):
        """Test fixed pool mode with $0."""
        calc = BudgetCalculator()
        calc.add_expense("Rent", 1000.0, True)

        result = calc.calculate_fixed_pool_mode(total_money=0.0)

        assert result['out_of_money'] is True, "Should flag out of money"
        assert result['daily_limit'] == 0
        assert result['months_remaining'] == 0
        assert result['days_remaining'] == 0

    def test_fixed_pool_no_expenses(self):
        """Test fixed pool mode with no expenses."""
        calc = BudgetCalculator()

        result = calc.calculate_fixed_pool_mode(total_money=5000.0)

        # Money lasts forever with no expenses
        assert result['months_remaining'] == float('inf')
        assert result['days_remaining'] == float('inf')
        assert result['daily_limit'] == 0  # No budget needed

    def test_fixed_pool_exact_one_month(self):
        """Test fixed pool mode when money lasts exactly one month."""
        calc = BudgetCalculator()
        calc.add_expense("Total", 3000.0, True)

        result = calc.calculate_fixed_pool_mode(total_money=3000.0)

        # Exactly 1 month
        assert abs(result['months_remaining'] - 1.0) < 0.01
        assert abs(result['days_remaining'] - 30) < 1

    def test_fixed_pool_small_amount(self):
        """Test fixed pool mode with very small amount."""
        calc = BudgetCalculator()
        calc.add_expense("Expenses", 1000.0, True)

        result = calc.calculate_fixed_pool_mode(total_money=50.0)

        # 50 / 1000 = 0.05 months = 1.5 days
        assert result['months_remaining'] < 1
        assert result['days_remaining'] < 30

    # ===== EXPENSE VALIDATION TESTS =====

    def test_expense_max_amount(self):
        """Test expense validation with maximum amount."""
        calc = BudgetCalculator()

        # Should accept $10M
        try:
            calc.add_expense("Big Expense", 10_000_000.0, True)
        except ValueError:
            raise AssertionError("Should accept $10M expense")

        # Should reject > $10M
        try:
            calc.add_expense("Too Big", 10_000_001.0, True)
            raise AssertionError("Should reject expense > $10M")
        except ValueError:
            pass  # Expected

    def test_expense_negative_amount(self):
        """Test expense validation rejects negative amounts."""
        calc = BudgetCalculator()

        try:
            calc.add_expense("Invalid", -100.0, True)
            raise AssertionError("Should reject negative expense")
        except ValueError:
            pass  # Expected

    # ===== REAL-WORLD SCENARIOS =====

    def test_scenario_college_student(self):
        """Test realistic college student budget scenario."""
        calc = BudgetCalculator()
        calc.add_expense("Rent", 600.0, True)
        calc.add_expense("Utilities", 80.0, True)
        calc.add_expense("Groceries", 250.0, False)
        calc.add_expense("Gas", 100.0, False)

        # Part-time job: $1200/month, biweekly pay
        result = calc.calculate_paycheck_mode(monthly_income=1200.0, days_until_paycheck=14)

        # Total expenses: $1030
        # Remaining: $170
        # Daily: $170 / 14 = ~$12.14
        assert result['remaining_money'] == 170.0
        assert abs(result['daily_limit'] - 12.14) < 0.01

    def test_scenario_emergency_fund(self):
        """Test emergency fund depletion scenario."""
        calc = BudgetCalculator()
        calc.add_expense("Living Expenses", 2500.0, True)

        # $15,000 emergency fund
        result = calc.calculate_fixed_pool_mode(total_money=15000.0)

        # Should last 6 months
        assert abs(result['months_remaining'] - 6.0) < 0.1

    def test_scenario_overspending(self):
        """Test scenario where user is overspending."""
        calc = BudgetCalculator()
        calc.add_expense("Rent", 1800.0, True)
        calc.add_expense("Car Payment", 450.0, True)
        calc.add_expense("Insurance", 200.0, True)
        calc.add_expense("Subscriptions", 100.0, True)
        calc.add_expense("Dining Out", 400.0, False)
        calc.add_expense("Shopping", 300.0, False)

        # Income: $2500/month
        result = calc.calculate_paycheck_mode(monthly_income=2500.0, days_until_paycheck=15)

        # Total expenses: $3250
        # Deficit: -$750
        assert result['is_deficit'] is True
        assert result['deficit_amount'] == 750.0
        assert result['daily_limit'] == 0

    def run_all_tests(self, mode: str = "all") -> Tuple[int, int]:
        """Run all tests and return (passed, failed) counts."""
        print("\n" + "="*60)
        print("BUDGET TESTER AGENT - Running Tests")
        print("="*60 + "\n")

        if mode in ["all", "paycheck"]:
            print("[*] Testing Paycheck Mode...")
            self.run_test("Paycheck: Basic Calculation", self.test_paycheck_basic_calculation)
            self.run_test("Paycheck: Deficit Scenario", self.test_paycheck_deficit_scenario)
            self.run_test("Paycheck: Zero Expenses", self.test_paycheck_zero_expenses)
            self.run_test("Paycheck: One Day Remaining", self.test_paycheck_one_day_remaining)
            self.run_test("Paycheck: Max Days (365)", self.test_paycheck_max_days)
            self.run_test("Paycheck: Invalid Days", self.test_paycheck_invalid_days)
            self.run_test("Paycheck: Floating Point Precision", self.test_paycheck_floating_point_precision)

        if mode in ["all", "fixed_pool"]:
            print("\n[*] Testing Fixed Pool Mode...")
            self.run_test("Fixed Pool: Basic Calculation", self.test_fixed_pool_basic_calculation)
            self.run_test("Fixed Pool: Zero Money", self.test_fixed_pool_zero_money)
            self.run_test("Fixed Pool: No Expenses", self.test_fixed_pool_no_expenses)
            self.run_test("Fixed Pool: Exact One Month", self.test_fixed_pool_exact_one_month)
            self.run_test("Fixed Pool: Small Amount", self.test_fixed_pool_small_amount)

        if mode == "all":
            print("\n[*] Testing Expense Validation...")
            self.run_test("Expense: Max Amount Validation", self.test_expense_max_amount)
            self.run_test("Expense: Negative Amount Rejection", self.test_expense_negative_amount)

            print("\n[*] Testing Real-World Scenarios...")
            self.run_test("Scenario: College Student Budget", self.test_scenario_college_student)
            self.run_test("Scenario: Emergency Fund", self.test_scenario_emergency_fund)
            self.run_test("Scenario: Overspending Detection", self.test_scenario_overspending)

        passed = sum(1 for r in self.test_results if r['status'] == 'PASS')
        failed = len(self.failures)

        print("\n" + "="*60)
        print(f"RESULTS: {passed} passed, {failed} failed")
        print("="*60 + "\n")

        if self.failures:
            print("FAILURES:")
            for failure in self.failures:
                print(f"  [-] {failure['name']}")
                print(f"      {failure['error']}")
            print()

        return passed, failed


def main():
    """Main entry point for the budget tester agent."""
    import argparse

    parser = argparse.ArgumentParser(description="Budget Tester Agent for The Number App")
    parser.add_argument('--mode', choices=['all', 'paycheck', 'fixed_pool'],
                       default='all', help='Test mode to run')
    parser.add_argument('--verbose', action='store_true', help='Enable verbose output')

    args = parser.parse_args()

    agent = BudgetTesterAgent(verbose=args.verbose)
    passed, failed = agent.run_all_tests(mode=args.mode)

    # Exit with error code if tests failed
    sys.exit(0 if failed == 0 else 1)


if __name__ == "__main__":
    main()
