# Onboarding Flow

This document describes the step-by-step onboarding process that guides new users through setting up The Number app.

## Overview

The onboarding process automatically runs when a user launches the app for the first time (when `onboarded` setting is not set in the database). It takes approximately 2 minutes to complete.

## Flow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│  User runs: python main.py                                 │
│                                                             │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  Step 0: Welcome Screen                                     │
│                                                             │
│  🎯 Welcome to The Number!                                  │
│  Your Simple Daily Budget App                               │
│                                                             │
│  - Explains what the app does                               │
│  - Lists the 4 setup steps                                  │
│  - Asks user if ready to start                              │
│                                                             │
│  Options: [Yes] [No]                                        │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ├─ No ──► Exit (user can restart later)
                     │
                     ▼ Yes
┌─────────────────────────────────────────────────────────────┐
│  Step 1/4: Choose Your Budgeting Style                      │
│                                                             │
│  Which situation describes you best?                        │
│                                                             │
│  1️⃣  PAYCHECK MODE                                          │
│     I have regular income                                   │
│     → Calculate daily budget from income                    │
│                                                             │
│  2️⃣  FIXED POOL MODE                                        │
│     I have a fixed amount of money                          │
│     → Show how long money will last                         │
│                                                             │
│  Options: [1] [2]                                           │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ├─ 1 (Paycheck Mode) ──┐
                     │                       │
                     ├─ 2 (Fixed Pool) ──────┤
                     │                       │
                     ▼                       ▼
┌──────────────────────────────┐  ┌──────────────────────────┐
│  Step 2a/4:                  │  │  Step 2b/4:              │
│  Paycheck Mode Setup         │  │  Fixed Pool Setup        │
│                              │  │                          │
│  Questions:                  │  │  Questions:              │
│  • Monthly income? $____     │  │  • Total money? $____    │
│  • Days until paycheck? __   │  │                          │
│                              │  │                          │
│  Validates:                  │  │  Validates:              │
│  - Income > 0                │  │  - Money > 0             │
│  - Days > 0                  │  │                          │
└────────────┬─────────────────┘  └───────────┬──────────────┘
             │                                │
             └────────────────┬───────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  Step 3/4: Add Your Monthly Expenses                        │
│                                                             │
│  Add expenses that you MUST pay each month                  │
│  (Rent, utilities, bills, etc.)                             │
│                                                             │
│  For each expense:                                          │
│  • Name: ________                                           │
│  • Amount: $____                                            │
│  • Fixed or Variable? [y/n]                                 │
│                                                             │
│  Shows running total                                        │
│  Allows adding multiple expenses                            │
│  Option to skip (no expenses)                               │
│                                                             │
│  Options: [Add Expense] [Done]                              │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  Step 4/4: Here's Your Number!                              │
│                                                             │
│  [PAYCHECK MODE]              [FIXED POOL MODE]             │
│                                                             │
│  💰 Monthly Income: $3,000    💰 Total Money: $6,000        │
│  📊 Total Expenses: $2,000    📊 Monthly Expenses: $2,000   │
│  ───────────────────────────  ─────────────────────────────│
│  💵 After Expenses: $1,000    📅 Will Last: 3.0 months      │
│  📅 Days to Paycheck: 15                  (90 days)         │
│                                                             │
│  ═══════════════════════════  ═══════════════════════════  │
│  🎯 THE NUMBER: $66.67/day    🎯 THE NUMBER: $66.67/day     │
│  ═══════════════════════════  ═══════════════════════════  │
│                                                             │
│  Today's Spending: $0.00                                    │
│  Remaining Today: $66.67                                    │
│                                                             │
│  💡 Tips for Success:                                       │
│  • Check 'The Number' every morning                         │
│  • Record spending throughout the day                       │
│  • Stay under your daily limit                              │
│  • Update expenses if anything changes                      │
│                                                             │
│  [Press Enter to go to main menu]                           │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  Main Menu (Regular App Interface)                          │
│                                                             │
│  1. 🎯 Get The Number (Daily Budget)                        │
│  2. 💵 Record Spending                                      │
│  3. 📊 Manage Expenses                                      │
│  4. 📝 View Transactions                                    │
│  5. ⚙️  Setup Budget Mode                                   │
│  6. ❌ Exit                                                  │
└─────────────────────────────────────────────────────────────┘
```

## Data Saved During Onboarding

### Settings Table
- `onboarded`: `true` (marks user as onboarded)
- `budget_mode`: `"paycheck"` or `"fixed_pool"`

#### For Paycheck Mode:
- `monthly_income`: Float (e.g., 3000.0)
- `days_until_paycheck`: Integer (e.g., 15)

#### For Fixed Pool Mode:
- `total_money`: Float (e.g., 5000.0)

### Expenses Table
For each expense added:
- `name`: String (e.g., "Rent")
- `amount`: Float (e.g., 1500.0)
- `is_fixed`: Boolean (1 for fixed, 0 for variable)
- `created_at`: ISO timestamp
- `updated_at`: ISO timestamp

## Key Features

### Input Validation
- All numeric inputs must be positive (> 0)
- Empty inputs are rejected (except for optional fields)
- Type checking (int, float, string)
- Custom validation functions per field

### User Experience
- Clear progress indicators (Step X of 4)
- Running totals for expenses
- Helpful explanations at each step
- Examples of common expenses
- Tips and warnings based on calculated budget
- Can cancel at any time (Ctrl+C)

### Error Handling
- Graceful handling of invalid inputs
- Clear error messages
- Allows retry on errors
- Preserves user's place in flow

### Smart Feedback

The app provides context-aware feedback based on the calculated budget:

**Paycheck Mode Warnings:**
- Daily limit ≤ $0: Expenses exceed income
- Daily limit < $20: Budget is very tight
- Daily limit ≥ $20: Budget looks good

**Fixed Pool Mode Warnings:**
- Daily limit ≤ $0: No money left after expenses
- Money lasts < 30 days: Critical - less than a month
- Money lasts 30-90 days: Warning - 1-3 months
- Money lasts > 90 days: Healthy buffer

## Code Structure

### Files
- `src/onboarding.py`: Main onboarding logic
- `src/cli.py`: Integrates onboarding check
- `main.py`: Entry point (triggers onboarding if needed)

### Key Classes
- `Onboarding`: Handles the entire onboarding flow
  - `welcome_screen()`: Step 0
  - `choose_budget_mode()`: Step 1
  - `setup_paycheck_mode()`: Step 2a
  - `setup_fixed_pool_mode()`: Step 2b
  - `add_expenses()`: Step 3
  - `show_first_number()`: Step 4

### Integration
```python
# In CLI.__init__()
def _check_onboarding(self) -> None:
    if not self.db.get_setting("onboarded"):
        onboarding = Onboarding(self.db)
        success = onboarding.run()

        if success:
            # Reload expenses
            self.calculator.expenses = []
            self._load_expenses()
        else:
            # User cancelled
            sys.exit(0)
```

## Testing

To test onboarding:
1. Delete `budget.db` file (if exists)
2. Run `python main.py`
3. Follow the prompts
4. Verify data is saved correctly in database

## Skipping Onboarding (For Development)

To bypass onboarding during testing:
```python
from src.database import EncryptedDatabase
db = EncryptedDatabase()
db.set_setting("onboarded", True)
```

## Future Enhancements

Potential improvements to onboarding:
- Save progress if user exits mid-flow
- Add "back" button to previous steps
- Pre-fill with common expense templates
- Import expenses from CSV
- Connect bank account during onboarding
- Video tutorial or demo mode
- Accessibility improvements (screen reader support)
- Multi-language support
