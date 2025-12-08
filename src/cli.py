"""
Command-line interface for The Number budgeting app.

Provides an interactive CLI for managing budget, expenses, and getting daily spending limits.
"""

import os
import sys
from datetime import datetime
from typing import Optional
from pathlib import Path

from .database import EncryptedDatabase
from .calculator import BudgetCalculator, Expense
from .onboarding import Onboarding


class CLI:
    """Interactive command-line interface for The Number app."""

    def __init__(self, db_path: str = "budget.db"):
        """Initialize CLI with database connection."""
        # Load encryption key from environment
        encryption_key = os.getenv("DB_ENCRYPTION_KEY")

        self.db = EncryptedDatabase(db_path=db_path, encryption_key=encryption_key)
        self.calculator = BudgetCalculator()
        self._load_expenses()
        self._check_onboarding()

    def _load_expenses(self) -> None:
        """Load expenses from database into calculator."""
        expenses = self.db.get_expenses()
        for exp in expenses:
            self.calculator.add_expense(
                name=exp["name"],
                amount=exp["amount"],
                is_fixed=exp["is_fixed"]
            )

    def _check_onboarding(self) -> None:
        """Check if user needs to go through onboarding."""
        if not self.db.get_setting("onboarded"):
            onboarding = Onboarding(self.db)
            success = onboarding.run()

            if success:
                # Reload expenses after onboarding
                self.calculator.expenses = []
                self._load_expenses()
            else:
                # User cancelled onboarding
                self.clear_screen()
                print("
  You can complete setup anytime by running the app again.
")
                sys.exit(0)

    def clear_screen(self) -> None:
        """Clear the terminal screen."""
        os.system('cls' if os.name == 'nt' else 'clear')

    def print_header(self, title: str) -> None:
        """Print a formatted header."""
        print("\n" + "="*60)
        print(f"  {title}")
        print("="*60 + "\n")

    def print_menu(self, options: list) -> None:
        """Print a numbered menu."""
        for i, option in enumerate(options, 1):
            print(f"  {i}. {option}")
        print()

    def get_input(self, prompt: str, input_type: type = str, allow_empty: bool = False) -> any:
        """
        Get validated user input.

        Args:
            prompt: Input prompt to display
            input_type: Type to convert input to (str, int, float)
            allow_empty: Whether to allow empty input

        Returns:
            Validated input of specified type
        """
        while True:
            try:
                value = input(f"  {prompt}: ").strip()

                if not value and allow_empty:
                    return None

                if not value:
                    print("  ❌ Input cannot be empty. Please try again.\n")
                    continue

                if input_type == str:
                    return value
                elif input_type == int:
                    return int(value)
                elif input_type == float:
                    return float(value)
                else:
                    return input_type(value)

            except ValueError:
                print(f"  ❌ Invalid input. Please enter a valid {input_type.__name__}.\n")
            except KeyboardInterrupt:
                print("\n\n  Cancelled.\n")
                return None

    def get_the_number(self) -> None:
        """Main feature: Display 'The Number' - daily spending limit."""
        self.clear_screen()
        self.print_header("GET THE NUMBER")

        # Check if user has set up their budget mode
        budget_mode = self.db.get_setting("budget_mode")

        if not budget_mode:
            print("  You haven't set up your budget mode yet.")
            print("  Please configure your budget first (Setup > Budget Mode).\n")
            input("  Press Enter to continue...")
            return

        if budget_mode == "paycheck":
            monthly_income = self.db.get_setting("monthly_income", 0)
            days_until_paycheck = self.db.get_setting("days_until_paycheck", 30)

            result = self.calculator.calculate_paycheck_mode(
                monthly_income=monthly_income,
                days_until_paycheck=days_until_paycheck
            )

            print(f"  💰 Monthly Income: ${result['total_income']:.2f}")
            print(f"  📊 Total Expenses: ${result['total_expenses']:.2f}")
            print(f"  💵 Remaining: ${result['remaining_money']:.2f}")
            print(f"  📅 Days Until Paycheck: {result['days_remaining']}")
            print("\n" + "-"*60 + "\n")
            print(f"  🎯 THE NUMBER: ${result['daily_limit']:.2f} per day")
            print("\n" + "-"*60 + "\n")

        elif budget_mode == "fixed_pool":
            total_money = self.db.get_setting("total_money", 0)

            result = self.calculator.calculate_fixed_pool_mode(total_money=total_money)

            print(f"  💰 Total Money: ${result['total_money']:.2f}")
            print(f"  📊 Monthly Expenses: ${result['monthly_expenses']:.2f}")
            print(f"  📅 Money Will Last: {result['days_remaining']:.1f} days ({result['months_remaining']:.1f} months)")
            print("\n" + "-"*60 + "\n")
            print(f"  🎯 THE NUMBER: ${result['daily_limit']:.2f} per day")
            print("\n" + "-"*60 + "\n")

        # Show today's spending
        today_spending = self.db.get_total_spending_today()
        remaining_today = result['daily_limit'] - today_spending

        print(f"  Today's Spending: ${today_spending:.2f}")
        print(f"  Remaining Today: ${remaining_today:.2f}")

        if remaining_today < 0:
            print("\n  ⚠️  Warning: You've exceeded your daily limit!")
        elif remaining_today < result['daily_limit'] * 0.2:
            print("\n  ⚠️  Warning: You're close to your daily limit!")

        print()
        input("  Press Enter to continue...")

    def manage_expenses(self) -> None:
        """Manage budget expenses."""
        while True:
            self.clear_screen()
            self.print_header("MANAGE EXPENSES")

            expenses = self.db.get_expenses()
            total = sum(exp["amount"] for exp in expenses)

            if expenses:
                print("  Current Expenses:\n")
                for exp in expenses:
                    expense_type = "Fixed" if exp["is_fixed"] else "Variable"
                    print(f"    [{exp['id']}] {exp['name']:<20} ${exp['amount']:>8.2f}  ({expense_type})")
                print(f"\n  {'Total:':<22} ${total:>8.2f}\n")
            else:
                print("  No expenses added yet.\n")

            options = [
                "Add Expense",
                "Remove Expense",
                "Back to Main Menu"
            ]
            self.print_menu(options)

            choice = self.get_input("Select option", int)

            if choice == 1:
                self._add_expense()
            elif choice == 2:
                self._remove_expense()
            elif choice == 3:
                break

    def _add_expense(self) -> None:
        """Add a new expense."""
        print("\n  Add New Expense\n")

        name = self.get_input("Expense name")
        if not name:
            return

        amount = self.get_input("Amount", float)
        if amount is None or amount < 0:
            print("  ❌ Amount must be a positive number.")
            return

        is_fixed_input = self.get_input("Is this a fixed monthly expense? (y/n)", str)
        is_fixed = is_fixed_input.lower() in ['y', 'yes']

        # Add to database
        self.db.add_expense(name=name, amount=amount, is_fixed=is_fixed)

        # Add to calculator
        self.calculator.add_expense(name=name, amount=amount, is_fixed=is_fixed)

        print(f"\n  ✅ Added expense: {name} - ${amount:.2f}\n")
        input("  Press Enter to continue...")

    def _remove_expense(self) -> None:
        """Remove an expense."""
        expenses = self.db.get_expenses()
        if not expenses:
            print("\n  No expenses to remove.\n")
            input("  Press Enter to continue...")
            return

        print("\n  Remove Expense\n")
        expense_id = self.get_input("Enter expense ID to remove", int)

        if expense_id:
            self.db.delete_expense(expense_id)
            print(f"\n  ✅ Removed expense ID {expense_id}\n")

            # Reload expenses into calculator
            self.calculator.expenses = []
            self._load_expenses()

        input("  Press Enter to continue...")

    def record_spending(self) -> None:
        """Record a spending transaction."""
        self.clear_screen()
        self.print_header("RECORD SPENDING")

        amount = self.get_input("Amount spent", float)
        if amount is None or amount < 0:
            print("  ❌ Amount must be a positive number.")
            input("  Press Enter to continue...")
            return

        description = self.get_input("Description")
        if not description:
            return

        category = self.get_input("Category (optional)", str, allow_empty=True)

        # Add transaction
        self.db.add_transaction(amount=amount, description=description, category=category)
        self.calculator.add_transaction(amount=amount, description=description, category=category)

        print(f"\n  ✅ Recorded: ${amount:.2f} - {description}\n")
        input("  Press Enter to continue...")

    def view_transactions(self) -> None:
        """View recent transactions."""
        self.clear_screen()
        self.print_header("RECENT TRANSACTIONS")

        transactions = self.db.get_transactions(limit=20)

        if transactions:
            print("  Last 20 Transactions:\n")
            for txn in transactions:
                date_str = datetime.fromisoformat(txn["date"]).strftime("%Y-%m-%d %H:%M")
                category = f" [{txn['category']}]" if txn['category'] else ""
                print(f"    {date_str}  ${txn['amount']:>8.2f}  {txn['description']}{category}")
            print()
        else:
            print("  No transactions recorded yet.\n")

        input("  Press Enter to continue...")

    def setup_budget_mode(self) -> None:
        """Configure budget mode and settings."""
        self.clear_screen()
        self.print_header("BUDGET MODE SETUP")

        current_mode = self.db.get_setting("budget_mode", "Not set")
        print(f"  Current Mode: {current_mode}\n")

        options = [
            "Paycheck Mode (Regular income, calculate days until paycheck)",
            "Fixed Pool Mode (Fixed amount of money, calculate how long it lasts)",
            "Back to Main Menu"
        ]
        self.print_menu(options)

        choice = self.get_input("Select budget mode", int)

        if choice == 1:
            self._setup_paycheck_mode()
        elif choice == 2:
            self._setup_fixed_pool_mode()

    def _setup_paycheck_mode(self) -> None:
        """Set up paycheck-based budgeting."""
        print("\n  Paycheck Mode Setup\n")

        monthly_income = self.get_input("Monthly income", float)
        if monthly_income is None or monthly_income < 0:
            return

        days_until_paycheck = self.get_input("Days until next paycheck", int)
        if days_until_paycheck is None or days_until_paycheck <= 0:
            return

        self.db.set_setting("budget_mode", "paycheck")
        self.db.set_setting("monthly_income", monthly_income)
        self.db.set_setting("days_until_paycheck", days_until_paycheck)

        print("\n  ✅ Paycheck mode configured!\n")
        input("  Press Enter to continue...")

    def _setup_fixed_pool_mode(self) -> None:
        """Set up fixed-pool budgeting."""
        print("\n  Fixed Pool Mode Setup\n")

        total_money = self.get_input("Total money available", float)
        if total_money is None or total_money < 0:
            return

        self.db.set_setting("budget_mode", "fixed_pool")
        self.db.set_setting("total_money", total_money)

        print("\n  ✅ Fixed pool mode configured!\n")
        input("  Press Enter to continue...")

    def main_menu(self) -> None:
        """Display main menu and handle navigation."""
        while True:
            self.clear_screen()
            self.print_header("THE NUMBER - Budget App")

            options = [
                "🎯 Get The Number (Daily Budget)",
                "💵 Record Spending",
                "📊 Manage Expenses",
                "📝 View Transactions",
                "⚙️  Setup Budget Mode",
                "❌ Exit"
            ]
            self.print_menu(options)

            choice = self.get_input("Select option", int)

            if choice == 1:
                self.get_the_number()
            elif choice == 2:
                self.record_spending()
            elif choice == 3:
                self.manage_expenses()
            elif choice == 4:
                self.view_transactions()
            elif choice == 5:
                self.setup_budget_mode()
            elif choice == 6:
                self.clear_screen()
                print("\n  Thanks for using The Number! 💰\n")
                sys.exit(0)
            else:
                print("\n  ❌ Invalid option. Please try again.\n")
                input("  Press Enter to continue...")

    def run(self) -> None:
        """Start the CLI application."""
        try:
            self.main_menu()
        except KeyboardInterrupt:
            self.clear_screen()
            print("\n  Goodbye! 👋\n")
            sys.exit(0)
        except Exception as e:
            print(f"\n  ❌ Error: {e}\n")
            sys.exit(1)
