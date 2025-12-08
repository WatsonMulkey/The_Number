"""
Onboarding module for The Number app.

Provides a step-by-step guided setup process for new users to configure
their budget and get their first daily spending number.
"""

import os
from typing import Optional, Dict, Any
from .database import EncryptedDatabase


class Onboarding:
    """Handles first-time user onboarding and setup."""

    def __init__(self, db: EncryptedDatabase):
        """Initialize onboarding with database connection."""
        self.db = db

    def clear_screen(self) -> None:
        """Clear the terminal screen."""
        os.system('cls' if os.name == 'nt' else 'clear')

    def print_header(self, title: str, subtitle: str = "") -> None:
        """Print a formatted header."""
        self.clear_screen()
        print("\n" + "="*70)
        print(f"  {title}")
        if subtitle:
            print(f"  {subtitle}")
        print("="*70 + "\n")

    def print_step(self, step_num: int, total_steps: int, title: str) -> None:
        """Print step progress."""
        print(f"\n  📍 Step {step_num} of {total_steps}: {title}\n")
        print("-"*70 + "\n")

    def get_input(self, prompt: str, input_type: type = str,
                  allow_empty: bool = False, validate=None) -> any:
        """
        Get validated user input with optional custom validation.

        Args:
            prompt: Input prompt to display
            input_type: Type to convert input to (str, int, float)
            allow_empty: Whether to allow empty input
            validate: Optional validation function that returns (bool, error_message)

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

                # Convert to type
                if input_type == str:
                    converted = value
                elif input_type == int:
                    converted = int(value)
                elif input_type == float:
                    converted = float(value)
                else:
                    converted = input_type(value)

                # Custom validation
                if validate:
                    is_valid, error_msg = validate(converted)
                    if not is_valid:
                        print(f"  ❌ {error_msg}\n")
                        continue

                return converted

            except ValueError:
                print(f"  ❌ Invalid input. Please enter a valid {input_type.__name__}.\n")
            except KeyboardInterrupt:
                print("\n\n  Setup cancelled. You can restart anytime.\n")
                return None

    def get_yes_no(self, prompt: str) -> bool:
        """Get yes/no input from user."""
        while True:
            response = input(f"  {prompt} (y/n): ").strip().lower()
            if response in ['y', 'yes']:
                return True
            elif response in ['n', 'no']:
                return False
            else:
                print("  ❌ Please enter 'y' or 'n'.\n")

    def welcome_screen(self) -> bool:
        """Display welcome screen and confirm user wants to continue."""
        self.print_header("🎯 Welcome to The Number!", "Your Simple Daily Budget App")

        print("  The Number helps you answer one simple question:\n")
        print("  💰 \"How much can I spend today?\"\n")
        print("-"*70 + "\n")
        print("  This quick setup will take about 2 minutes.\n")
        print("  We'll help you:\n")
        print("    1️⃣  Choose your budgeting style")
        print("    2️⃣  Add your income or available money")
        print("    3️⃣  List your monthly expenses")
        print("    4️⃣  Get your first daily budget number!\n")
        print("-"*70 + "\n")

        return self.get_yes_no("Ready to get started?")

    def choose_budget_mode(self) -> Optional[str]:
        """Step 1: Choose budget mode."""
        self.print_header("🎯 The Number - Setup")
        self.print_step(1, 4, "Choose Your Budgeting Style")

        print("  Which situation describes you best?\n")
        print("  1️⃣  I have regular income (job, salary, consistent paychecks)")
        print("     → Choose PAYCHECK MODE")
        print("     → We'll calculate your daily budget based on your income\n")
        print("  2️⃣  I have a fixed amount of money that needs to last")
        print("     → Choose FIXED POOL MODE")
        print("     → We'll show you how long your money will last\n")
        print("-"*70 + "\n")

        choice = self.get_input(
            "Select your mode (1 or 2)",
            int,
            validate=lambda x: (x in [1, 2], "Please enter 1 or 2")
        )

        if choice is None:
            return None

        return "paycheck" if choice == 1 else "fixed_pool"

    def setup_paycheck_mode(self) -> Optional[Dict[str, Any]]:
        """Step 2a: Configure paycheck mode."""
        self.print_header("🎯 The Number - Setup")
        self.print_step(2, 4, "Paycheck Mode Setup")

        print("  Let's set up your income and paycheck schedule.\n")
        print("-"*70 + "\n")

        # Get monthly income
        monthly_income = self.get_input(
            "What is your total monthly income? $",
            float,
            validate=lambda x: (x > 0, "Income must be greater than $0")
        )

        if monthly_income is None:
            return None

        print(f"\n  ✅ Monthly income: ${monthly_income:,.2f}\n")

        # Get days until paycheck
        print("  When is your next paycheck?\n")
        days_until_paycheck = self.get_input(
            "Days until next paycheck",
            int,
            validate=lambda x: (x > 0, "Must be at least 1 day")
        )

        if days_until_paycheck is None:
            return None

        print(f"\n  ✅ Next paycheck in: {days_until_paycheck} days\n")

        return {
            "mode": "paycheck",
            "monthly_income": monthly_income,
            "days_until_paycheck": days_until_paycheck
        }

    def setup_fixed_pool_mode(self) -> Optional[Dict[str, Any]]:
        """Step 2b: Configure fixed pool mode."""
        self.print_header("🎯 The Number - Setup")
        self.print_step(2, 4, "Fixed Pool Mode Setup")

        print("  Let's set up your available money.\n")
        print("-"*70 + "\n")

        total_money = self.get_input(
            "How much money do you have available? $",
            float,
            validate=lambda x: (x > 0, "Amount must be greater than $0")
        )

        if total_money is None:
            return None

        print(f"\n  ✅ Total money available: ${total_money:,.2f}\n")

        return {
            "mode": "fixed_pool",
            "total_money": total_money
        }

    def add_expenses(self) -> Optional[list]:
        """Step 3: Add monthly expenses."""
        self.print_header("🎯 The Number - Setup")
        self.print_step(3, 4, "Add Your Monthly Expenses")

        print("  Now let's add your monthly expenses (rent, bills, etc.).\n")
        print("  These are costs you MUST pay each month.\n")
        print("  Your daily budget will be what's LEFT OVER after these.\n")
        print("-"*70 + "\n")

        expenses = []
        total = 0.0

        # Ask if they have expenses
        has_expenses = self.get_yes_no("Do you have monthly expenses to add?")

        if not has_expenses:
            print("\n  ℹ️  No expenses added. You can add them later in the main menu.\n")
            input("  Press Enter to continue...")
            return expenses

        print("\n  Common expenses: Rent, Utilities, Phone, Internet, Insurance,")
        print("                   Groceries, Transportation, Subscriptions\n")
        print("-"*70 + "\n")

        while True:
            print(f"\n  Current total expenses: ${total:,.2f}\n")

            # Get expense name
            name = self.get_input(
                "Expense name (or press Enter when done)",
                str,
                allow_empty=True
            )

            if name is None:
                break

            # Get expense amount
            amount = self.get_input(
                f"Monthly amount for {name} $",
                float,
                validate=lambda x: (x >= 0, "Amount cannot be negative")
            )

            if amount is None:
                continue

            # Ask if fixed or variable
            print(f"\n  Is this a FIXED or VARIABLE expense?")
            print(f"    Fixed: Same amount every month (e.g., rent)")
            print(f"    Variable: Amount changes (e.g., groceries)\n")

            is_fixed = self.get_yes_no(f"  Is '{name}' a fixed expense?")

            expenses.append({
                "name": name,
                "amount": amount,
                "is_fixed": is_fixed
            })

            total += amount
            expense_type = "Fixed" if is_fixed else "Variable"
            print(f"\n  ✅ Added: {name} - ${amount:,.2f} ({expense_type})\n")

            # Ask to continue
            add_more = self.get_yes_no("Add another expense?")
            if not add_more:
                break

        if expenses:
            print("\n" + "-"*70)
            print(f"\n  📊 Total Monthly Expenses: ${total:,.2f}\n")
            print("  Breakdown:")
            for exp in expenses:
                exp_type = "Fixed" if exp["is_fixed"] else "Variable"
                print(f"    • {exp['name']:<20} ${exp['amount']:>8,.2f}  ({exp_type})")
            print()

        input("\n  Press Enter to continue...")
        return expenses

    def show_first_number(self, config: Dict[str, Any], expenses: list) -> None:
        """Step 4: Calculate and show the user's first number."""
        from .calculator import BudgetCalculator

        self.print_header("🎯 The Number - Your Daily Budget", "Setup Complete!")
        self.print_step(4, 4, "Here's Your Number!")

        # Calculate the number
        calc = BudgetCalculator()

        # Add expenses to calculator
        for exp in expenses:
            calc.add_expense(exp["name"], exp["amount"], exp["is_fixed"])

        # Calculate based on mode
        if config["mode"] == "paycheck":
            result = calc.calculate_paycheck_mode(
                monthly_income=config["monthly_income"],
                days_until_paycheck=config["days_until_paycheck"]
            )

            print("  💰 Your Budget Summary:\n")
            print(f"    Monthly Income:        ${result['total_income']:>10,.2f}")
            print(f"    Total Expenses:        ${result['total_expenses']:>10,.2f}")
            print(f"    ─────────────────────────────────────────")
            print(f"    Money After Expenses:  ${result['remaining_money']:>10,.2f}")
            print(f"    Days Until Paycheck:   {result['days_remaining']:>10}")
            print()
            print("="*70)
            print()
            print(f"         🎯 THE NUMBER: ${result['daily_limit']:>10,.2f} per day")
            print()
            print("="*70)
            print()

            if result['daily_limit'] <= 0:
                print("  ⚠️  Warning: Your expenses exceed your income!")
                print("     Consider reducing expenses or increasing income.\n")
            elif result['daily_limit'] < 20:
                print("  ⚠️  Your daily budget is quite tight.")
                print("     Track your spending carefully!\n")
            else:
                print("  ✅ Your budget looks good!")
                print("     Stick to your daily limit and you'll stay on track.\n")

        else:  # fixed_pool mode
            result = calc.calculate_fixed_pool_mode(
                total_money=config["total_money"]
            )

            months = result['months_remaining']
            days = result['days_remaining']

            print("  💰 Your Budget Summary:\n")
            print(f"    Total Money:           ${result['total_money']:>10,.2f}")
            print(f"    Monthly Expenses:      ${result['monthly_expenses']:>10,.2f}")
            print(f"    ─────────────────────────────────────────")
            if months == float('inf'):
                print(f"    Money Will Last:       Indefinitely!")
            else:
                print(f"    Money Will Last:       {months:>10,.1f} months")
                print(f"                           ({days:>10,.0f} days)")
            print()
            print("="*70)
            print()
            print(f"         🎯 THE NUMBER: ${result['daily_limit']:>10,.2f} per day")
            print()
            print("="*70)
            print()

            if result['daily_limit'] <= 0:
                print("  ⚠️  Warning: You have no money left after expenses!")
                print("     You need to reduce expenses or find additional funds.\n")
            elif days < 30:
                print("  ⚠️  Your money will run out in less than a month!")
                print("     Consider reducing expenses or finding income.\n")
            elif days < 90:
                print("  ⚠️  Your money will last about 1-3 months.")
                print("     Start planning for additional income.\n")
            else:
                print("  ✅ Your money will last for a while!")
                print("     Stick to your daily limit to stay on track.\n")

        print("-"*70 + "\n")
        print("  💡 Tips for Success:\n")
        print("    • Check 'The Number' every morning")
        print("    • Record your spending throughout the day")
        print("    • Stay under your daily limit to stay on budget")
        print("    • Update your expenses if anything changes\n")
        print("-"*70 + "\n")

        input("  Press Enter to go to the main menu...")

    def run(self) -> bool:
        """
        Run the complete onboarding process.

        Returns:
            True if onboarding completed successfully, False if cancelled
        """
        try:
            # Check if already onboarded
            if self.db.get_setting("onboarded"):
                return True

            # Step 0: Welcome
            if not self.welcome_screen():
                self.clear_screen()
                print("\n  Setup cancelled. Run the app again when you're ready!\n")
                return False

            # Step 1: Choose budget mode
            mode = self.choose_budget_mode()
            if mode is None:
                return False

            # Step 2: Configure mode-specific settings
            if mode == "paycheck":
                config = self.setup_paycheck_mode()
            else:
                config = self.setup_fixed_pool_mode()

            if config is None:
                return False

            # Step 3: Add expenses
            expenses = self.add_expenses()
            if expenses is None:
                return False

            # Save everything to database
            self.db.set_setting("budget_mode", config["mode"])

            if config["mode"] == "paycheck":
                self.db.set_setting("monthly_income", config["monthly_income"])
                self.db.set_setting("days_until_paycheck", config["days_until_paycheck"])
            else:
                self.db.set_setting("total_money", config["total_money"])

            for exp in expenses:
                self.db.add_expense(exp["name"], exp["amount"], exp["is_fixed"])

            # Mark as onboarded
            self.db.set_setting("onboarded", True)

            # Step 4: Show first number
            self.show_first_number(config, expenses)

            return True

        except KeyboardInterrupt:
            self.clear_screen()
            print("\n  Setup cancelled. You can restart anytime.\n")
            return False
        except Exception as e:
            print(f"\n  ❌ Error during setup: {e}\n")
            return False
