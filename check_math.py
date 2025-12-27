import sqlite3
from datetime import datetime, date

conn = sqlite3.connect('budget.db')
cursor = conn.cursor()

# Check user ID 2
user_id = 2
cursor.execute('SELECT id, username FROM users WHERE id = ?', (user_id,))
user = cursor.fetchone()

print(f'User: {user[1]} (ID: {user[0]})')
print('=' * 70)

# Get settings from settings table
cursor.execute('SELECT key, value FROM settings WHERE user_id = ?', (user_id,))
settings_rows = cursor.fetchall()
settings = {}
if settings_rows:
    print('\nBudget Configuration (from settings table):')
    for key, value in settings_rows:
        settings[key] = value
        print(f'  {key}: {value}')
else:
    print('\nNo settings found')

# Get expenses
cursor.execute('SELECT name, amount, is_fixed FROM expenses WHERE user_id = ?', (user_id,))
expenses = cursor.fetchall()
total_expenses = 0
if expenses:
    print(f'\nMonthly Expenses:')
    for exp in expenses:
        print(f'  {exp[0]}: ${exp[1]:.2f}')
        total_expenses += exp[1]
    print(f'  ------------------------')
    print(f'  TOTAL: ${total_expenses:.2f}')
else:
    print('\nNo expenses configured')

# Get transactions for today
today_str = date.today().isoformat()
cursor.execute('SELECT date, amount, description, category FROM transactions WHERE user_id = ? AND date = ? ORDER BY created_at', (user_id, today_str))
today_txns = cursor.fetchall()
today_spending = 0
today_income = 0
if today_txns:
    print(f'\nTodays Transactions ({today_str}):')
    for txn in today_txns:
        sign = '+' if txn[3] == 'income' else '-'
        print(f'  {sign}${txn[1]:.2f} - {txn[2]}')
        if txn[3] == 'income':
            today_income += txn[1]
        else:
            today_spending += txn[1]
    print(f'  ------------------------')
    print(f'  Todays Spending: ${today_spending:.2f}')
    if today_income > 0:
        print(f'  Todays Income: ${today_income:.2f}')

# Get all transactions
cursor.execute('SELECT date, amount, description, category FROM transactions WHERE user_id = ? ORDER BY date DESC', (user_id,))
all_txns = cursor.fetchall()
total_spending = 0
total_income = 0
if all_txns and len(all_txns) > len(today_txns):
    print(f'\nAll Transactions ({len(all_txns)} total):')
    for txn in all_txns:
        sign = '+' if txn[3] == 'income' else '-'
        print(f'  {txn[0]}: {sign}${txn[1]:.2f} - {txn[2]}')
        if txn[3] == 'income':
            total_income += txn[1]
        else:
            total_spending += txn[1]

# Now calculate what 'The Number' should be
print('\n' + '=' * 70)
print('CALCULATION VERIFICATION:')
print('=' * 70)

mode = settings.get('mode')
if mode:
    print(f'\nMode: {mode}')

    if mode == 'paycheck':
        monthly_income = float(settings.get('monthly_income', 0))
        days_until_paycheck = int(settings.get('days_until_paycheck', 0))

        print(f'\nInputs:')
        print(f'  Monthly Income: ${monthly_income:.2f}')
        print(f'  Total Monthly Expenses: ${total_expenses:.2f}')
        print(f'  Days Until Paycheck: {days_until_paycheck}')
        print(f'  Todays Spending: ${today_spending:.2f}')

        remaining_money = monthly_income - total_expenses
        print(f'\nStep 1 - Calculate remaining after expenses:')
        print(f'  ${monthly_income:.2f} (income) - ${total_expenses:.2f} (expenses) = ${remaining_money:.2f}')

        if days_until_paycheck > 0:
            the_number = remaining_money / days_until_paycheck
            print(f'\nStep 2 - Divide by days until paycheck:')
            print(f'  ${remaining_money:.2f} / {days_until_paycheck} days = ${the_number:.2f} per day')

            remaining_today = the_number - today_spending
            print(f'\nStep 3 - Subtract todays spending:')
            print(f'  ${the_number:.2f} - ${today_spending:.2f} = ${remaining_today:.2f} remaining today')

            print(f'\n✓ THE NUMBER: ${the_number:.2f} per day')
            print(f'✓ REMAINING TODAY: ${remaining_today:.2f}')

            if today_spending > the_number:
                print(f'⚠ OVER BUDGET by ${today_spending - the_number:.2f}')
        else:
            print(f'\n⚠ Cannot calculate - days until paycheck is {days_until_paycheck}')

    elif mode == 'fixed_pool':
        total_money = float(settings.get('total_money', 0))
        daily_limit = settings.get('daily_spending_limit')
        target_date = settings.get('target_end_date')

        print(f'\nInputs:')
        print(f'  Total Money Available: ${total_money:.2f}')
        if total_spending > 0:
            print(f'  Total Spent So Far: ${total_spending:.2f}')
            print(f'  Money Remaining: ${total_money - total_spending:.2f}')

        if daily_limit:
            daily_limit = float(daily_limit)
            print(f'  Daily Spending Limit: ${daily_limit:.2f}')
            print(f'  Todays Spending: ${today_spending:.2f}')

            remaining_money = total_money - total_spending
            days = remaining_money / daily_limit if daily_limit > 0 else 0
            remaining_today = daily_limit - today_spending

            print(f'\nCalculation:')
            print(f'  ${remaining_money:.2f} (remaining) / ${daily_limit:.2f} per day = {days:.1f} days')
            print(f'  ${daily_limit:.2f} - ${today_spending:.2f} = ${remaining_today:.2f} remaining today')

            print(f'\n✓ THE NUMBER: ${daily_limit:.2f} per day')
            print(f'✓ MONEY WILL LAST: {days:.1f} days')
            print(f'✓ REMAINING TODAY: ${remaining_today:.2f}')

            if today_spending > daily_limit:
                print(f'⚠ OVER BUDGET by ${today_spending - daily_limit:.2f}')

        elif target_date:
            print(f'  Target End Date: {target_date}')
            try:
                end_date = datetime.fromisoformat(target_date.replace('Z', '+00:00'))
                today = datetime.now()
                days_remaining = (end_date - today).days + 1  # Include today
                print(f'  Days Remaining: {days_remaining}')

                remaining_money = total_money - total_spending

                if days_remaining > 0:
                    the_number = remaining_money / days_remaining
                    remaining_today = the_number - today_spending

                    print(f'\nCalculation:')
                    print(f'  ${remaining_money:.2f} (remaining) / {days_remaining} days = ${the_number:.2f} per day')
                    print(f'  ${the_number:.2f} - ${today_spending:.2f} = ${remaining_today:.2f} remaining today')

                    print(f'\n✓ THE NUMBER: ${the_number:.2f} per day')
                    print(f'✓ REMAINING TODAY: ${remaining_today:.2f}')

                    if today_spending > the_number:
                        print(f'⚠ OVER BUDGET by ${today_spending - the_number:.2f}')
                else:
                    print(f'\n⚠ Target date has passed')
            except Exception as e:
                print(f'  Error parsing date: {e}')
else:
    print('\n⚠ No budget mode configured')

conn.close()
