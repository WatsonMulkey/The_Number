# Get user input for total monthly income
total_income = float(input("Enter your total monthly income: $"))

# List of monthly expenses
expenses = {
    "rent": 1500,
    "utilities": 200,
    "groceries": 300,
    "transportation": 200,
    "insurance": 0,  # Add more as needed
    "entertainment": 0,
    "other_expenses": 0
}

# Calculate total expenses
total_expenses = sum(expenses.values())

# Calculate remaining money after obligations
remaining_money = total_income - total_expenses

# Ask for the number of days until next paycheck
days_until_paycheck = int(input("How many days until your next paycheck? "))

# Calculate daily spending limit based on remaining money and days left
daily_limit = remaining_money / days_until_paycheck if days_until_paycheck != 0 else 0

print(f"After paying all monthly obligations, you have ${remaining_money:.2f} left.")
print(f"You can spend up to ${daily_limit:.2f} per day until your next paycheck.")
