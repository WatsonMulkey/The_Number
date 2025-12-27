# The Number Calculation Review

**Date:** 2025-12-26
**Issue:** Numbers not recalculating correctly after transactions
**Priority:** 🔴 CRITICAL - Core functionality

---

## Problem Statement

User reports that after entering a $14 expense and setting up a fixed pool with $25/day limit, The Number shows $25 instead of the expected $11.

---

## Current Architecture

### Two Separate Data Tables

1. **`expenses` table** - Recurring monthly expenses
   - Examples: rent, subscriptions, utilities
   - Used to calculate available money over time
   - NOT today's spending

2. **`transactions` table** - Actual spending events
   - Examples: bought coffee, paid for groceries
   - Records specific date and amount
   - Used to track today's spending

### Calculation Flow

```
Fixed Pool Mode (Daily Limit):
1. User sets daily_spending_limit = $25
2. Calculator returns: result["daily_limit"] = $25
3. API gets today_spending from transactions table
4. API calculates: remaining_today = $25 - today_spending
5. API returns: the_number = remaining_today
```

### Current Formula

```python
# api/main.py:148-149
today_spending = db.get_total_spending_today(user_id)  # SUM of transactions for TODAY
remaining_today = result["daily_limit"] - today_spending
```

---

## Root Cause Analysis

### Hypothesis 1: User Added Expense During Onboarding (Not Transaction)

**If user added $14 as a recurring expense:**
- Goes into `expenses` table
- Does NOT affect `get_total_spending_today()`
- Result: today_spending = $0
- The Number = $25 - $0 = $25 ✓ Matches reported behavior

**Why this is confusing:**
- User expected expense to count as spending
- UX doesn't clearly distinguish expenses vs transactions

### Hypothesis 2: Transaction Created Before Onboarding Completion

**If user recorded transaction before setting budget:**
- Transaction exists in database
- But onboarding creates new session
- Possible cache/state issue

### Hypothesis 3: Frontend Display Issue

**If backend calculates correctly but frontend shows wrong value:**
- Check NumberDisplay.vue component
- Check budgetStore.budgetNumber
- Verify response parsing

---

## Debug Findings

### Server Logs Analysis

```
Line -50: POST /api/transactions - 201 Created  ✓ Transactions being created
Line -47: GET /api/number - 200 OK             ✓ Number endpoint responding
Line -7:  POST /api/transactions - 201 Created  ✓ More transactions
Line -4:  GET /api/number - 200 OK             ✓ Number recalculated
```

**Issue:** No debug output from lines 151-155 in main.py
- Server reloaded but user hasn't made new request since
- Need fresh request to see debug values

---

## Testing Required

### Test Case 1: Fresh Setup
1. Create new account
2. Record transaction of $14 (not expense)
3. Complete onboarding with $25/day limit
4. Check if The Number shows $11

### Test Case 2: Verify Transaction vs Expense
1. Check what "entering an expense" actually creates
2. Verify if it goes to expenses or transactions table
3. Confirm user workflow

### Test Case 3: Debug Output
1. Have user refresh app
2. Check backend terminal for debug output:
   ```
   [DEBUG] Budget calculation for user X:
     - Mode: fixed_pool
     - Daily limit: 25.0
     - Today's spending: ???
     - Remaining today: ???
   ```

---

## Potential Solutions

### Solution 1: Clarify UX (Quick Win)
- Make it crystal clear in UI: "Expenses" vs "Spending"
- Expenses = recurring monthly costs
- Spending = actual money spent today

### Solution 2: Include Recurring Expenses in Daily Calculation
```python
# Option A: Subtract daily portion of expenses
daily_expense_rate = total_expenses / 30
remaining_today = daily_limit - today_spending - daily_expense_rate
```

**Pros:**
- More accurate representation of available money
- Accounts for fixed costs

**Cons:**
- Changes fundamental calculation
- May confuse users who set limit already accounting for expenses

### Solution 3: Separate Display
Show both values clearly:
```
Your Daily Limit: $25.00
Today's Spending: -$14.00
Remaining Today:  $11.00
```

---

## Immediate Actions

1. ✅ Added debug logging to main.py (lines 151-155)
2. ✅ Changed return value to `remaining_today` instead of `daily_limit`
3. ⏳ **NEED USER TO:**
   - Refresh the app
   - Try recording a new transaction
   - Check browser console
   - Check backend terminal for debug output
   - Report what they see

---

## Questions for User

1. When you "entered an expense of 14 dollars" - where did you do this?
   - During onboarding setup? (Recurring Expenses screen)
   - On the main dashboard? (Record Spending section)

2. Can you check the Transactions view and see if the $14 appears there?

3. After refreshing, what does The Number show now?

4. Can you share the debug output from the backend terminal?

---

## Files Modified

- `api/main.py:152` - Changed `the_number=result["daily_limit"]` to `the_number=remaining_today`
- `api/main.py:151-155` - Added debug logging
- `frontend/src/views/Dashboard.vue:203-243` - Added auth state logging

---

## Next Steps

Based on debug output, we'll know:
1. Is `today_spending` actually 0 or 14?
2. Is the calculation correct on backend?
3. Is the issue in frontend display?

Then we can:
- Fix the root cause
- Improve UX to prevent confusion
- Add better error handling
