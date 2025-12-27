# Frontend Test Strategy: The Number Web App

**Author:** Test Architect & QA Lead
**Date:** 2025-12-16
**Project:** The Number - Vue 3 + Vuetify Budget Tracking Application
**Framework:** Vitest + Vue Test Utils

---

## Executive Summary

This document provides a comprehensive test strategy for The Number web application's frontend, focusing on the critical onboarding flow and all frontend components. The analysis reveals **significant gaps** in test coverage, particularly around the **Onboarding.vue component (0% coverage)**, edge case handling, integration scenarios, and end-to-end user flows.

### Current State Assessment

**Strengths:**
- Good foundation with Vitest + Vue Test Utils
- Comprehensive unit tests for existing components (NumberDisplay, NavigationRail)
- Solid store and API layer test coverage
- Well-structured test organization

**Critical Gaps:**
- **No tests for Onboarding.vue** - the most critical user-facing component
- Missing validation edge cases (negative numbers, special characters, SQL injection)
- No integration tests for multi-step flows
- Limited error recovery and network failure testing
- Missing accessibility tests
- No E2E tests for complete user journeys

---

## 1. Current Test Coverage Analysis

### 1.1 What's Actually Being Tested

#### Components with Good Coverage

**NumberDisplay.vue (305 lines of tests)**
- ✅ Basic rendering with various props
- ✅ Mode-specific subtitles (paycheck vs fixed pool)
- ✅ Over-budget state styling
- ✅ Today's spending display logic
- ✅ Spending percentage calculations
- ✅ Edge cases: negative numbers, large numbers, zero values
- ✅ Props validation

**NavigationRail.vue (301 lines of tests)**
- ✅ Navigation item rendering
- ✅ Router integration
- ✅ Active route highlighting
- ✅ Icon display
- ✅ Drawer properties

**Budget Store (331 lines of tests)**
- ✅ Initial state
- ✅ Computed properties
- ✅ CRUD operations for expenses and transactions
- ✅ Error handling with detail extraction
- ✅ Loading states

**API Service (297 lines of tests)**
- ✅ All endpoint calls
- ✅ Request parameter formatting
- ✅ Response handling
- ✅ Error scenarios
- ✅ File upload/download for imports/exports

#### Views with Good Coverage

**Dashboard.vue (505 lines)**
- ✅ Loading states
- ✅ Not configured state
- ✅ Error display
- ✅ Record spending form validation
- ✅ Budget summary display
- ✅ Recent transactions list
- ✅ Component lifecycle (data fetching on mount)

**Expenses.vue (502 lines)**
- ✅ Add expense form validation
- ✅ Expenses list display
- ✅ Delete confirmation flow
- ✅ Total calculation
- ✅ Data table formatting
- ✅ Edge cases (large amounts, decimals)

**Settings.vue (641 lines)**
- ✅ Mode selection (paycheck vs fixed pool)
- ✅ Form field visibility based on mode
- ✅ Loading existing configuration
- ✅ Save configuration flow
- ✅ Success/error snackbars
- ✅ Store refresh after save

**Transactions.vue (575 lines)**
- ✅ Summary card calculations (today, all-time)
- ✅ Add transaction dialog
- ✅ Transaction form validation
- ✅ Delete confirmation
- ✅ Date formatting
- ✅ Edge cases (empty list, large amounts)

### 1.2 What's Missing - Critical Gaps

#### 🚨 CRITICAL: Onboarding.vue - 0% Test Coverage

**This is the most critical gap.** The onboarding flow is the first experience for new users and contains complex multi-step logic with validation, API calls, and state management. **529 lines of untested code.**

**Missing Tests:**
- Step navigation (forward/back)
- Mode selection persistence
- Input validation at each step
- Expense addition/removal during onboarding
- "The Number" calculation preview
- API failure recovery
- Form reset on back navigation
- Data persistence across steps
- Complete button state
- Error snackbar display
- Network timeout handling
- Concurrent API call handling

#### Missing Test Categories Across All Components

**1. Security & Input Validation**
- ❌ SQL injection attempts in text fields
- ❌ XSS (cross-site scripting) in description fields
- ❌ Script tag injection
- ❌ Extremely long strings (buffer overflow)
- ❌ Unicode/emoji handling
- ❌ Null byte injection
- ❌ Path traversal attempts in file uploads

**2. Edge Cases**
- ❌ Infinity and NaN values
- ❌ Negative expense amounts
- ❌ Zero days until paycheck
- ❌ Date manipulation (future dates, past dates)
- ❌ Concurrent form submissions
- ❌ Rapid clicking (debouncing)
- ❌ Browser back/forward button behavior

**3. Network & API Integration**
- ❌ Slow network (loading states > 2 seconds)
- ❌ Network timeout scenarios
- ❌ Partial response data
- ❌ API version mismatches
- ❌ CORS errors
- ❌ Rate limiting responses
- ❌ Retry logic on failures

**4. State Management**
- ❌ Race conditions in async operations
- ❌ Stale data after navigation
- ❌ Store state after logout/login
- ❌ Multiple tabs open simultaneously
- ❌ Browser refresh mid-operation
- ❌ Memory leaks in long-running sessions

**5. Accessibility**
- ❌ Keyboard navigation
- ❌ Screen reader compatibility
- ❌ Focus management
- ❌ ARIA labels
- ❌ Color contrast
- ❌ Tab order

**6. Performance**
- ❌ Large data sets (1000+ transactions)
- ❌ Component render time
- ❌ Memory usage
- ❌ Bundle size impact

**7. Browser Compatibility**
- ❌ Different viewport sizes
- ❌ Mobile touch events
- ❌ Browser-specific APIs
- ❌ LocalStorage availability

### 1.3 Test Quality Assessment

**Are Tests Meaningful or Superficial?**

**Meaningful Tests (70%):**
- Most tests verify actual behavior, not just structure
- Good use of mocking for API calls
- Proper async handling with `flushPromises()`
- Tests verify user-facing outcomes
- Edge case coverage in NumberDisplay

**Superficial Areas (30%):**
- Some tests just check that elements exist
- Limited testing of user interaction sequences
- Not enough "unhappy path" scenarios
- Missing integration between components

---

## 2. Onboarding Flow Test Design

### 2.1 Critical Onboarding Scenarios

The onboarding flow is a **5-step wizard** (0-4):
- Step 0: Welcome screen
- Step 1: Mode selection (paycheck vs fixed_pool)
- Step 2: Income/pool configuration
- Step 3: Add expenses
- Step 4: Review "The Number"

### 2.2 Happy Path Test Suite

**Test: Complete Paycheck Mode Onboarding**
```
Given: A new user on the welcome screen
When:
  - User clicks "Get Started"
  - Selects "Paycheck Mode"
  - Enters $5000 monthly income
  - Enters 15 days until paycheck
  - Adds 2 expenses (Rent: $1500, Groceries: $500)
  - Reviews "The Number" ($200/day)
  - Clicks "Complete Setup"
Then:
  - API calls are made in correct order
  - Budget config is saved with correct data
  - All expenses are created
  - 'complete' event is emitted
  - User sees success state
```

**Test: Complete Fixed Pool Mode Onboarding**
```
Given: A new user on the welcome screen
When:
  - User clicks "Get Started"
  - Selects "Fixed Pool Mode"
  - Enters $10,000 total money
  - Adds 1 expense (Rent: $1500)
  - Reviews "The Number"
  - Clicks "Complete Setup"
Then:
  - Budget config saved with mode: 'fixed_pool'
  - Total money: $10,000
  - Expense created
  - Onboarding completes successfully
```

**Test: Complete Onboarding Without Expenses**
```
Given: A new user on step 3
When: User clicks "Next" without adding any expenses
Then:
  - User proceeds to step 4
  - "The Number" is calculated with 0 expenses
  - Configuration saves successfully
  - No expense API calls are made
```

### 2.3 Edge Case Test Suite

#### Input Validation Tests

**Test: Reject Negative Income**
```
Given: User on step 2 (Paycheck Mode)
When: User enters -5000 in monthly income field
Then: Validation error displayed: "Income must be greater than 0"
And: "Next" button is disabled
```

**Test: Reject Zero Days Until Paycheck**
```
Given: User on step 2 (Paycheck Mode)
When: User enters 0 days until paycheck
Then: Validation error: "Days must be greater than 0"
And: Cannot proceed to next step
```

**Test: Handle Very Large Income Values**
```
Given: User on step 2
When: User enters $999,999,999.99
Then: Value is accepted and displayed correctly
And: "The Number" calculation doesn't overflow
And: API receives correct value
```

**Test: Handle Decimal Precision**
```
Given: User on step 2
When: User enters $1234.567 (3 decimal places)
Then: Value is stored as 1234.567
And: Display shows $1234.57 (rounded)
```

**Test: Reject Special Characters in Expense Name**
```
Given: User on step 3
When: User enters "<script>alert('xss')</script>" as expense name
Then: Input is sanitized or rejected
And: No script execution occurs
```

**Test: Handle Emoji in Expense Name**
```
Given: User on step 3
When: User enters "Coffee ☕" as expense name
Then: Emoji is preserved
And: Expense saves successfully
```

**Test: Extreme Expense Amounts**
```
Given: User on step 3
When: User enters $0.01 expense (minimum)
Then: Expense is added
And: Total calculates correctly

When: User enters $99999.99 expense (maximum realistic)
Then: Expense is added
And: "The Number" may show warning if < $20/day
```

#### Navigation Tests

**Test: Back Button Preserves Data**
```
Given: User on step 3 with expenses added
When: User clicks "Back"
Then: User goes to step 2
And: All previously entered data is preserved
When: User clicks "Next"
Then: Returns to step 3
And: Expenses list is still intact
```

**Test: Cannot Go Back from Step 0**
```
Given: User on welcome screen (step 0)
When: No back button should be visible
Then: currentStep remains 0
```

**Test: Cannot Proceed Without Required Fields**
```
Given: User on step 2 (Paycheck Mode)
When: Monthly income is 0
Then: "Next" button is disabled
And: canProceed computed property is false
```

**Test: Step Counter Displays Correctly**
```
Given: User is navigating through onboarding
When: On step 0: No step counter shown
When: On step 1: "Step 1 of 4"
When: On step 4: "Step 4 of 4"
```

#### Expense Management Tests

**Test: Add Multiple Expenses**
```
Given: User on step 3
When: User adds 10 different expenses
Then: All 10 expenses appear in the list
And: Total updates correctly after each addition
And: Form resets after each add
```

**Test: Remove Expense from List**
```
Given: User has 3 expenses added
When: User clicks delete on expense 2
Then: Expense is removed from array
And: Total recalculates
And: Remaining expenses maintain their data
```

**Test: Add Expense Without Name**
```
Given: User on step 3
When: Amount is 100 but name is empty
Then: "Add" button is disabled
And: Expense is not added
```

**Test: Add Expense With Zero Amount**
```
Given: User on step 3
When: Name is "Test" but amount is 0
Then: "Add" button is disabled
And: Expense is not added
```

**Test: Toggle Fixed Expense Flag**
```
Given: User adding an expense
When: User unchecks "is_fixed" checkbox
Then: Expense is added with is_fixed: false
And: Displayed differently in list (shows "Variable" chip)
```

### 2.4 API Failure Scenarios

**Test: Budget Configuration API Failure**
```
Given: User completes all steps
When: User clicks "Complete Setup"
And: API returns 500 error
Then: Loading spinner stops
And: Error snackbar displays: "Failed to complete onboarding"
And: User remains on step 4
And: Can retry by clicking "Complete Setup" again
```

**Test: Expense Creation Partial Failure**
```
Given: User has 3 expenses to create
When: Expense 1 saves successfully
And: Expense 2 fails with network error
Then: Onboarding stops at failed expense
And: Error message displays
And: Already-saved expenses are not duplicated on retry
```

**Test: Network Timeout During Configuration**
```
Given: User clicks "Complete Setup"
When: API call takes > 30 seconds
Then: Timeout error is shown
And: Loading state clears
And: User can retry
```

**Test: Invalid API Response**
```
Given: User clicks "Complete Setup"
When: API returns 200 but with malformed JSON
Then: Error is caught
And: User-friendly error message shown
And: Application doesn't crash
```

### 2.5 Calculation & Display Tests

**Test: The Number Calculation - Paycheck Mode**
```
Given: User enters:
  - Monthly income: $5000
  - Days until paycheck: 15
  - Total expenses: $2000
When: On step 4
Then: calculatedNumber shows $200/day
Formula: (5000 - 2000) / 15 = 200
```

**Test: The Number Calculation - Fixed Pool Mode**
```
Given: User enters:
  - Total money: $10000
  - Monthly expenses: $2000
When: On step 4
Then: calculatedNumber shows correct daily amount
Formula:
  - Months money will last: 10000 / 2000 = 5 months
  - Days: 5 * 30 = 150 days
  - Daily: 10000 / 150 = $66.67/day
```

**Test: Warning When Expenses Exceed Income**
```
Given: User enters:
  - Monthly income: $2000
  - Total expenses: $3000
When: On step 4
Then: calculatedNumber is 0 or negative
And: Warning alert shows: "Your expenses exceed your income"
```

**Test: Warning for Low Daily Budget**
```
Given: User's calculated number is $15/day
When: On step 4
Then: Info alert shows: "Your budget is tight. Track carefully!"
```

**Test: Mode Summary Display**
```
Given: User on step 4 (Paycheck Mode)
Then: Summary shows:
  - Monthly Income: $5000.00
  - Total Expenses: $2000.00
  - After Expenses: $3000.00
  - Days to Paycheck: 15

Given: User on step 4 (Fixed Pool Mode)
Then: Summary shows:
  - Total Money: $10000.00
  - Monthly Expenses: $2000.00
  - Will Last: 5.0 months
```

### 2.6 Data Persistence Tests

**Test: Mode Selection Persists Across Steps**
```
Given: User selects "Fixed Pool Mode" on step 1
When: User navigates to step 2 and back to step 1
Then: "Fixed Pool Mode" is still selected
```

**Test: Expense Data Persists During Navigation**
```
Given: User adds 3 expenses on step 3
When: User goes back to step 2, then forward to step 3
Then: All 3 expenses are still in the list
And: Total expenses still calculated correctly
```

**Test: Form Reset After Expense Add**
```
Given: User enters expense data
When: User clicks "Add"
Then: newExpense.name is cleared to ''
And: newExpense.amount is reset to 0
And: newExpense.is_fixed remains true (default)
```

---

## 3. Component Test Strategy

### 3.1 Onboarding.vue Critical Test Cases

**Priority: P0 (Must Have)**

| Test ID | Scenario | Given | When | Then | Rationale |
|---------|----------|-------|------|------|-----------|
| ON-001 | Welcome screen renders | New user | Component mounts | Shows welcome screen with 4-step overview | First impression matters |
| ON-002 | Get Started button | On step 0 | Click "Get Started" | Advances to step 1 | Entry point to flow |
| ON-003 | Mode selection | On step 1 | Select paycheck mode | budgetMode updates to 'paycheck' | Core configuration |
| ON-004 | Mode selection | On step 1 | Select fixed pool mode | budgetMode updates to 'fixed_pool' | Core configuration |
| ON-005 | Paycheck fields visible | budgetMode = 'paycheck' | On step 2 | Shows income & days fields | Mode-specific logic |
| ON-006 | Fixed pool fields visible | budgetMode = 'fixed_pool' | On step 2 | Shows total money field | Mode-specific logic |
| ON-007 | Validation - positive income | On step 2 | Enter 5000 | Validation passes | Happy path |
| ON-008 | Validation - zero income | On step 2 | Enter 0 | Error: "must be > 0" | Critical validation |
| ON-009 | Validation - negative income | On step 2 | Enter -100 | Error: "must be > 0" | Prevents invalid data |
| ON-010 | Add expense | On step 3 | Add "Rent" $1500 | Expense appears in list | Core functionality |
| ON-011 | Remove expense | 2 expenses added | Click delete on expense 1 | Expense removed, total updates | Data management |
| ON-012 | Skip expenses | On step 3 | Click Next with 0 expenses | Advances to step 4 | Optional step |
| ON-013 | Calculate The Number | Complete form | On step 4 | Shows correct daily amount | Primary value proposition |
| ON-014 | Complete onboarding | All steps done | Click "Complete Setup" | API calls made, event emitted | End-to-end flow |
| ON-015 | API error handling | Step 4 | API fails | Error snackbar shows | Error recovery |

**Priority: P1 (Should Have)**

| Test ID | Scenario | Given | When | Then | Rationale |
|---------|----------|-------|------|------|-----------|
| ON-016 | Back navigation | On step 3 | Click "Back" | Returns to step 2, data preserved | User can correct mistakes |
| ON-017 | Step counter | Navigating | Each step | Shows "Step X of 4" | User orientation |
| ON-018 | Disable Next button | Invalid input | On any step | Next button disabled | Prevent bad data |
| ON-019 | Loading state | Saving | Click Complete | Loading spinner shows | Visual feedback |
| ON-020 | Expense form reset | Add expense | After adding | Form clears | Better UX |
| ON-021 | Total expenses display | Multiple expenses | On step 3 | Running total shown | Transparency |
| ON-022 | Warning - expenses exceed income | Income < expenses | On step 4 | Warning alert shown | Financial guidance |
| ON-023 | Tight budget warning | Daily amount < $20 | On step 4 | Info alert shown | User awareness |
| ON-024 | Fixed vs Variable expense | Adding expense | Toggle checkbox | Expense type saved correctly | Data accuracy |
| ON-025 | Decimal amounts | Enter 1234.56 | Any monetary field | Stored and displayed correctly | Precision |

**Priority: P2 (Nice to Have)**

| Test ID | Scenario | Given | When | Then | Rationale |
|---------|----------|-------|------|------|-----------|
| ON-026 | Very large income | Step 2 | Enter $999,999.99 | Accepts and calculates | Edge case |
| ON-027 | Very small income | Step 2 | Enter $0.01 | Accepts (passes validation) | Edge case |
| ON-028 | 100 expenses | Step 3 | Add 100 expenses | All stored, performance OK | Stress test |
| ON-029 | Emoji in expense name | Step 3 | Enter "Coffee ☕" | Saves and displays correctly | Unicode support |
| ON-030 | Long expense name | Step 3 | 255 character name | Truncates or accepts | Boundary test |

### 3.2 Dashboard.vue Enhancements

**Missing Tests:**

- **Refresh Behavior**: What happens when user manually refreshes page?
- **Stale Data**: If budget changes in another tab, does dashboard update?
- **Empty State Variations**: Different messages for different error types
- **Quick Action Buttons**: Do they navigate correctly?
- **Spending Form Edge Cases**: What if user enters spending > daily limit?
- **Transaction List Scrolling**: Performance with 1000+ transactions

### 3.3 Settings.vue Enhancements

**Missing Tests:**

- **Unsaved Changes Warning**: If user navigates away with unsaved data
- **Mode Switch with Data**: Switching modes when data exists
- **Validation Rules**: All numeric fields should reject non-numeric input
- **Config Update**: Does changing config update "The Number" immediately?
- **Concurrent Edits**: Two tabs editing settings simultaneously

### 3.4 Expenses.vue Enhancements

**Missing Tests:**

- **Bulk Delete**: Select and delete multiple expenses
- **Sort and Filter**: Test table sorting functionality
- **Import CSV**: File upload with various formats
- **Export**: Download CSV/Excel and verify contents
- **Duplicate Expense Names**: Allow or prevent?
- **Edit Expense**: If added, test edit functionality

### 3.5 Transactions.vue Enhancements

**Missing Tests:**

- **Date Range Filter**: Filter transactions by date
- **Category Grouping**: Group by category
- **Bulk Operations**: Delete multiple transactions
- **Export Transactions**: CSV/Excel export
- **Search/Filter**: Filter by description
- **Pagination**: Handle 1000+ transactions

---

## 4. Integration Test Plan

Integration tests verify that multiple components, stores, and APIs work together correctly.

### 4.1 API → Store → Component Flow

**Test: Complete Data Flow for Budget Number**
```javascript
// Test: Full stack budget number retrieval
describe('Budget Number Integration', () => {
  it('should flow from API → Store → Dashboard display', async () => {
    // 1. Mock API response
    mockApi.getNumber.resolves({ data: { the_number: 100, ... } })

    // 2. Store fetches data
    const store = useBudgetStore()
    await store.fetchNumber()

    // 3. Component displays it
    const wrapper = mount(Dashboard)
    await flushPromises()

    // 4. Verify entire flow
    expect(mockApi.getNumber).toHaveBeenCalled()
    expect(store.budgetNumber.the_number).toBe(100)
    expect(wrapper.text()).toContain('$100.00')
  })
})
```

**Test: Expense Creation Flow**
```javascript
// Test: Add expense → updates store → updates dashboard
describe('Expense Creation Integration', () => {
  it('should create expense and update budget number', async () => {
    // Setup
    const store = useBudgetStore()
    const expensesView = mount(Expenses)

    // Add expense
    await expensesView.vm.newExpense = { name: 'Netflix', amount: 15, is_fixed: true }
    await expensesView.vm.addExpense()
    await flushPromises()

    // Verify store updated
    expect(store.expenses).toContainEqual(expect.objectContaining({ name: 'Netflix' }))

    // Verify budget number recalculated
    expect(store.budgetNumber.total_expenses).toBeGreaterThan(0)

    // Verify dashboard shows new expense
    const dashboard = mount(Dashboard)
    await flushPromises()
    expect(dashboard.text()).toContain('Netflix')
  })
})
```

**Test: Transaction Recording Flow**
```javascript
// Test: Record transaction → updates spending → changes budget status
describe('Transaction Recording Integration', () => {
  it('should record transaction and update over-budget status', async () => {
    const store = useBudgetStore()
    store.budgetNumber = { the_number: 50, today_spending: 0, ... }

    // Record spending that exceeds daily limit
    await store.recordTransaction({ amount: 75, description: 'Emergency' })
    await flushPromises()

    // Verify over-budget flag
    expect(store.isOverBudget).toBe(true)

    // Verify dashboard shows warning
    const dashboard = mount(Dashboard)
    expect(dashboard.find('.over-budget')).toExist()
  })
})
```

### 4.2 Router Navigation Tests

**Test: Navigation Between Views**
```javascript
describe('Router Navigation Integration', () => {
  it('should navigate from Dashboard → Expenses → Settings', async () => {
    const router = createRouter(...)
    const app = mount(App, { global: { plugins: [router] } })

    // Start on dashboard
    expect(router.currentRoute.value.name).toBe('dashboard')

    // Click expenses link
    await app.find('[title="Expenses"]').trigger('click')
    await flushPromises()
    expect(router.currentRoute.value.name).toBe('expenses')

    // Navigate to settings
    await app.find('[title="Settings"]').trigger('click')
    await flushPromises()
    expect(router.currentRoute.value.name).toBe('settings')
  })

  it('should highlight active navigation item', async () => {
    // Verify NavigationRail shows correct active state
    const nav = app.findComponent(NavigationRail)
    expect(nav.find('[title="Settings"]').classes()).toContain('v-list-item--active')
  })
})
```

### 4.3 State Persistence Tests

**Test: Data Persists Across Navigation**
```javascript
describe('State Persistence', () => {
  it('should maintain store data when navigating between views', async () => {
    const store = useBudgetStore()
    await store.fetchNumber()
    const originalNumber = store.budgetNumber.the_number

    // Navigate to expenses
    await router.push('/expenses')
    await flushPromises()

    // Navigate back to dashboard
    await router.push('/')
    await flushPromises()

    // Data should still be there (no refetch needed)
    expect(store.budgetNumber.the_number).toBe(originalNumber)
    expect(mockApi.getNumber).toHaveBeenCalledTimes(1) // Only once
  })
})
```

### 4.4 Error Boundary Tests

**Test: Global Error Handling**
```javascript
describe('Error Boundaries', () => {
  it('should catch component errors and show fallback UI', async () => {
    // Simulate component error
    const BrokenComponent = {
      setup() { throw new Error('Component crashed') }
    }

    const app = mount(App, {
      global: {
        components: { BrokenComponent },
        errorHandler: (err) => { /* capture */ }
      }
    })

    // Verify error UI
    expect(app.text()).toContain('Something went wrong')
    expect(app.find('.error-fallback')).toExist()
  })
})
```

### 4.5 Real API Integration Tests

**Test: Live API Calls (Optional - E2E Category)**
```javascript
describe('Real API Integration', () => {
  // These run against actual backend (use test database)
  it('should complete full onboarding flow with real API', async () => {
    // Requires test backend running on localhost:8000
    const onboarding = mount(Onboarding)

    // Complete flow
    await onboarding.vm.nextStep() // Welcome
    onboarding.vm.budgetMode = 'paycheck'
    await onboarding.vm.nextStep()

    onboarding.vm.monthlyIncome = 5000
    onboarding.vm.daysUntilPaycheck = 15
    await onboarding.vm.nextStep()

    await onboarding.vm.completeOnboarding()
    await flushPromises()

    // Verify data persisted to real database
    const response = await fetch('http://localhost:8000/api/budget/config')
    const data = await response.json()
    expect(data.configured).toBe(true)
  })
})
```

---

## 5. End-to-End Test Scenarios

E2E tests verify complete user journeys from start to finish, simulating real user behavior.

### 5.1 New User Onboarding Journey

**Scenario: Complete Onboarding → First Expense → View Dashboard**

```gherkin
Feature: New User First Experience

Scenario: User sets up budget and tracks first expense
  Given: User visits the app for the first time
  When: User completes onboarding with:
    | mode              | paycheck |
    | monthly_income    | 5000     |
    | days_to_paycheck  | 15       |
    | expense_1         | Rent, 1500 |
    | expense_2         | Utils, 200 |
  Then: User sees "The Number": $220/day

  When: User clicks "Complete Setup"
  Then: User is redirected to Dashboard
  And: Dashboard shows The Number: $220/day

  When: User records spending: $45, "Groceries"
  Then: Today's spending shows $45
  And: Remaining today shows $175
  And: Transaction appears in recent list

  When: User navigates to Transactions view
  Then: User sees 1 transaction
  And: Summary shows Today: $45
```

**Implementation Strategy:**
- Use Playwright or Cypress for browser automation
- Test on Chrome, Firefox, Safari
- Test mobile viewport (375px width)
- Test with slow 3G network throttling

### 5.2 Budget Reconfiguration Journey

**Scenario: User Changes Budget Mode**

```gherkin
Feature: Budget Reconfiguration

Scenario: Switch from Paycheck to Fixed Pool mode
  Given: User has configured Paycheck mode with:
    | monthly_income    | 5000 |
    | days_to_paycheck  | 15   |
  And: User has 3 expenses totaling $2000

  When: User navigates to Settings
  And: User switches to "Fixed Pool Mode"
  And: User enters total money: $10,000
  And: User clicks "Save Configuration"

  Then: Success message appears
  And: User navigates to Dashboard
  And: The Number is recalculated for fixed pool mode
  And: Mode summary shows "Fixed Pool Mode"
  And: Expenses are preserved
```

### 5.3 Expense Management Journey

**Scenario: Add, Edit, Delete Expenses Over Time**

```gherkin
Feature: Expense Lifecycle

Scenario: User manages monthly expenses
  Given: User has configured budget
  When: User adds expense "Gym Membership", $50
  Then: Total expenses increases by $50
  And: The Number decreases accordingly

  When: User adds expense "Car Payment", $350
  Then: Total expenses includes both new expenses
  And: Dashboard reflects updated daily limit

  When: User deletes "Gym Membership"
  And: User confirms deletion
  Then: Expense is removed from list
  And: The Number increases
  And: Dashboard shows updated calculation

  When: User refreshes browser
  Then: Changes persist
  And: Deleted expense doesn't reappear
```

### 5.4 Spending Tracking Journey

**Scenario: Daily Spending Tracking**

```gherkin
Feature: Daily Expense Tracking

Scenario: User tracks spending throughout the day
  Given: User's daily limit is $100
  And: No spending recorded today

  When: User records transaction: $15, "Breakfast"
  Then: Today's spending: $15
  And: Remaining today: $85
  And: Progress bar shows 15% used

  When: User records transaction: $30, "Lunch"
  Then: Today's spending: $45
  And: Remaining today: $55
  And: Progress bar shows 45% used

  When: User records transaction: $70, "Emergency Car Repair"
  Then: Today's spending: $115
  And: Remaining today: -$15
  And: Over budget warning appears
  And: Number display shows red

  When: User views Transactions page
  Then: All 3 transactions listed
  And: Total for today: $115
```

### 5.5 Data Import/Export Journey

**Scenario: User Imports Expenses from CSV**

```gherkin
Feature: Data Import/Export

Scenario: User imports expenses from spreadsheet
  Given: User has expenses in Excel
  And: User exports to CSV format

  When: User navigates to Expenses
  And: User clicks "Import Expenses"
  And: User uploads CSV file with 10 expenses
  And: User chooses "Add to existing expenses"
  And: User confirms import

  Then: Success message appears
  And: 10 new expenses appear in list
  And: Total expenses updated
  And: The Number recalculated

  When: User clicks "Export Expenses"
  And: User selects Excel format
  Then: File downloads successfully
  And: File contains all expenses with correct data
```

### 5.6 Multi-Device Journey

**Scenario: User Switches Between Devices**

```gherkin
Feature: Cross-Device Usage

Scenario: User accesses app from phone and desktop
  Given: User sets up budget on desktop
  And: User has 5 expenses configured

  When: User opens app on mobile device
  Then: Budget configuration is synced
  And: All 5 expenses appear
  And: The Number displays correctly

  When: User records spending on mobile: $25
  Then: Transaction saved to backend

  When: User switches back to desktop
  And: User refreshes dashboard
  Then: Mobile transaction appears
  And: Spending totals updated
```

### 5.7 Error Recovery Journey

**Scenario: User Recovers from Network Error**

```gherkin
Feature: Network Error Handling

Scenario: User loses connection during onboarding
  Given: User is on onboarding step 3
  And: User has entered 3 expenses

  When: User's network disconnects
  And: User clicks "Next"
  Then: Error message appears
  And: User remains on step 3
  And: Entered data is preserved

  When: Network reconnects
  And: User clicks "Next" again
  Then: Request succeeds
  And: User advances to step 4
  And: All data intact
```

---

## 6. Testing Tools & Framework Recommendations

### 6.1 Current Stack (Keep)

**Vitest + Vue Test Utils**
- ✅ Fast, modern, Vite-native
- ✅ Great Vue 3 support
- ✅ Good developer experience
- Continue using for unit and integration tests

**Happy-DOM**
- ✅ Lightweight DOM environment
- ✅ Faster than jsdom
- Suitable for component tests

### 6.2 Recommended Additions

#### For E2E Testing

**Option 1: Playwright (Recommended)**
```bash
npm install -D @playwright/test
```

**Why Playwright:**
- Modern, maintained by Microsoft
- Cross-browser (Chrome, Firefox, Safari, Edge)
- Built-in auto-wait (less flaky tests)
- Great debugging tools
- Network interception
- Mobile device emulation
- Video recording of test runs

**Sample Playwright Test:**
```javascript
// e2e/onboarding.spec.ts
import { test, expect } from '@playwright/test'

test('complete onboarding flow', async ({ page }) => {
  await page.goto('http://localhost:5173')

  // Step 0: Welcome
  await expect(page.locator('h2')).toContainText('Welcome to The Number')
  await page.click('text=Get Started')

  // Step 1: Mode selection
  await page.click('text=Paycheck Mode')
  await page.click('text=Next')

  // Step 2: Income details
  await page.fill('input[label="Monthly Income"]', '5000')
  await page.fill('input[label="Days Until Paycheck"]', '15')
  await page.click('text=Next')

  // Step 3: Add expenses
  await page.fill('input[placeholder="Expense Name"]', 'Rent')
  await page.fill('input[type="number"]', '1500')
  await page.click('text=Add')

  await expect(page.locator('text=Rent')).toBeVisible()
  await expect(page.locator('text=$1500.00')).toBeVisible()
  await page.click('text=Next')

  // Step 4: Review
  await expect(page.locator('.the-number')).toContainText('$233.33')
  await page.click('text=Complete Setup')

  // Verify dashboard
  await expect(page).toHaveURL('/dashboard')
  await expect(page.locator('text=$233.33')).toBeVisible()
})
```

**Option 2: Cypress**
- Good alternative
- Easier for beginners
- Great component testing mode
- Strong community

#### For Visual Regression Testing

**Chromatic or Percy**
```bash
npm install -D @chromatic-com/storybook
```

**Why Visual Testing:**
- Catch UI regressions
- Verify responsive layouts
- Compare before/after UI changes
- Detect unintended style changes

#### For Accessibility Testing

**axe-core + vitest-axe**
```bash
npm install -D axe-core vitest-axe
```

**Sample Accessibility Test:**
```javascript
import { axe, toHaveNoViolations } from 'vitest-axe'

expect.extend(toHaveNoViolations)

it('should have no accessibility violations', async () => {
  const wrapper = mount(Onboarding)
  const results = await axe(wrapper.element)
  expect(results).toHaveNoViolations()
})
```

#### For Performance Testing

**Lighthouse CI**
```bash
npm install -D @lhci/cli
```

**Performance Budgets:**
- First Contentful Paint < 1.8s
- Time to Interactive < 3.8s
- Largest Contentful Paint < 2.5s

### 6.3 Test Organization Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── Onboarding.vue
│   │   ├── Onboarding.spec.ts          # Unit tests
│   │   └── NumberDisplay.vue
│   ├── views/
│   │   ├── Dashboard.vue
│   │   └── Dashboard.spec.ts
│   ├── stores/
│   │   ├── budget.ts
│   │   └── budget.spec.ts
│   └── test/
│       ├── setup.ts
│       ├── test-utils.ts               # Mock helpers
│       └── fixtures/                    # Test data
│           ├── budget.fixtures.ts
│           └── expenses.fixtures.ts
├── tests/
│   ├── integration/                     # Integration tests
│   │   ├── onboarding-flow.test.ts
│   │   ├── expense-management.test.ts
│   │   └── api-integration.test.ts
│   └── e2e/                            # E2E tests
│       ├── onboarding.spec.ts
│       ├── budget-reconfiguration.spec.ts
│       └── spending-tracking.spec.ts
└── playwright.config.ts
```

---

## 7. Implementation Roadmap

### Phase 1: Critical Coverage (Week 1-2)

**Priority: Onboarding Component**

**Tasks:**
1. Create `Onboarding.spec.ts` with 30+ tests
2. Cover all happy path scenarios
3. Test all validation rules
4. Test back/next navigation
5. Test expense add/remove
6. Test API error scenarios
7. Test calculation logic

**Acceptance Criteria:**
- Onboarding.spec.ts exists with 100% line coverage
- All P0 tests from section 3.1 implemented
- CI passes all tests

**Deliverable:**
```
frontend/src/components/Onboarding.spec.ts (500+ lines)
- 15 happy path tests
- 10 edge case tests
- 8 API failure tests
- 5 calculation tests
```

### Phase 2: Integration Tests (Week 3)

**Tasks:**
1. Create integration test suite
2. Test API → Store → Component flows
3. Test router navigation
4. Test state persistence
5. Add mock server for API tests

**Acceptance Criteria:**
- `tests/integration/` folder with 5+ test files
- All major user flows tested end-to-end
- Mock API server configured

**Deliverable:**
```
tests/integration/
├── onboarding-flow.test.ts
├── expense-crud.test.ts
├── transaction-recording.test.ts
├── budget-calculation.test.ts
└── navigation.test.ts
```

### Phase 3: E2E Setup (Week 4)

**Tasks:**
1. Install Playwright
2. Configure test environments
3. Create 5 critical E2E scenarios
4. Set up CI pipeline for E2E tests
5. Add visual regression tests

**Acceptance Criteria:**
- Playwright configured and running
- 5 E2E tests passing
- Tests run in CI on every PR
- Screenshots on failure

**Deliverable:**
```
tests/e2e/
├── onboarding-journey.spec.ts
├── expense-management.spec.ts
├── spending-tracking.spec.ts
└── budget-reconfiguration.spec.ts

playwright.config.ts
.github/workflows/e2e-tests.yml
```

### Phase 4: Edge Cases & Polish (Week 5-6)

**Tasks:**
1. Add P1 and P2 tests from section 3.1
2. Add accessibility tests
3. Add performance tests
4. Add security tests (XSS, injection)
5. Add browser compatibility tests

**Acceptance Criteria:**
- 95%+ code coverage across frontend
- All components have accessibility tests
- Security tests for all text inputs
- Performance budgets defined

**Deliverable:**
```
tests/
├── accessibility/
│   ├── onboarding.a11y.test.ts
│   └── dashboard.a11y.test.ts
├── security/
│   ├── xss-prevention.test.ts
│   └── input-sanitization.test.ts
└── performance/
    ├── lighthouse.config.js
    └── performance-budgets.json
```

### Phase 5: Maintenance & Documentation (Ongoing)

**Tasks:**
1. Document testing practices
2. Create test writing guide
3. Add test coverage badges
4. Set up test result dashboards
5. Train team on testing

**Deliverable:**
```
docs/
├── TESTING.md
├── TEST_WRITING_GUIDE.md
└── COVERAGE_REPORT.md

README.md (updated with test instructions)
```

---

## 8. Test Coverage Goals

### Coverage Metrics

| Category | Current | Target | Priority |
|----------|---------|--------|----------|
| Onboarding.vue | 0% | 95% | P0 |
| Other Components | 85% | 95% | P1 |
| Stores | 90% | 98% | P1 |
| API Service | 85% | 95% | P1 |
| Views | 80% | 90% | P2 |
| Overall Frontend | 70% | 92% | - |

### Quality Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Test Execution Time | < 30s for unit tests | `npm run test` |
| E2E Execution Time | < 5min for all scenarios | Playwright dashboard |
| Flaky Test Rate | < 2% | CI failure analysis |
| Test Maintenance Time | < 10% of dev time | Team retrospectives |
| Bug Escape Rate | < 5 per release | Production monitoring |

### Definition of Done for Tests

A feature is considered "tested" when:

1. ✅ Unit tests cover all functions and branches
2. ✅ Integration tests cover interaction with other modules
3. ✅ E2E test covers primary user journey
4. ✅ Edge cases documented and tested
5. ✅ Error scenarios tested
6. ✅ Accessibility verified
7. ✅ Performance benchmarked
8. ✅ Tests pass in CI
9. ✅ Test coverage > 90% for new code
10. ✅ No flaky tests

---

## 9. Risk Assessment

### High-Risk Areas

**1. Onboarding Flow (Current Risk: HIGH)**
- **Why:** 0% test coverage, complex multi-step logic
- **Impact:** Broken onboarding = no new users
- **Mitigation:** Implement Phase 1 immediately

**2. Budget Calculations (Current Risk: MEDIUM)**
- **Why:** Complex math, edge cases possible
- **Impact:** Incorrect daily limits = bad financial advice
- **Mitigation:** Add calculation tests with extreme values

**3. API Failures (Current Risk: MEDIUM)**
- **Why:** Limited network error testing
- **Impact:** User data loss, frustrated users
- **Mitigation:** Add retry logic, offline support tests

**4. Data Persistence (Current Risk: MEDIUM)**
- **Why:** No multi-tab or refresh tests
- **Impact:** User loses work
- **Mitigation:** Add state persistence tests

### Low-Risk Areas

- Navigation (well tested)
- Basic rendering (covered)
- Store CRUD operations (good coverage)

---

## 10. Success Criteria

This test strategy is successful when:

1. **Coverage**: 92%+ line coverage across frontend
2. **Confidence**: Team deploys without fear
3. **Speed**: Test suite runs in < 30s (unit), < 5min (E2E)
4. **Quality**: < 5 production bugs per month
5. **Maintainability**: Tests are easy to understand and update
6. **Documentation**: New developers can write tests in first week
7. **Automation**: All tests run in CI, no manual testing needed
8. **User Impact**: Zero critical user-facing bugs escape to production

---

## Appendix A: Sample Test Implementation

### Complete Onboarding Test Suite (Excerpt)

```typescript
// frontend/src/components/Onboarding.spec.ts

import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import Onboarding from './Onboarding.vue'
import { budgetApi } from '@/services/api'

vi.mock('@/services/api', () => ({
  budgetApi: {
    configureBudget: vi.fn(),
    createExpense: vi.fn(),
  },
}))

describe('Onboarding Component', () => {
  let pinia: any

  beforeEach(() => {
    pinia = createPinia()
    setActivePinia(pinia)
    vi.clearAllMocks()
  })

  describe('Initial Rendering', () => {
    it('should render welcome screen on mount', () => {
      const wrapper = mount(Onboarding, {
        global: { plugins: [pinia] },
      })

      expect(wrapper.text()).toContain('Welcome to The Number!')
      expect(wrapper.text()).toContain('4 quick steps')
      expect(wrapper.vm.currentStep).toBe(0)
    })

    it('should show step overview on welcome screen', () => {
      const wrapper = mount(Onboarding, {
        global: { plugins: [pinia] },
      })

      expect(wrapper.text()).toContain('Choose your budgeting style')
      expect(wrapper.text()).toContain('Enter your income')
      expect(wrapper.text()).toContain('Add your monthly expenses')
      expect(wrapper.text()).toContain('See your daily spending limit')
    })

    it('should show Get Started button on welcome screen', () => {
      const wrapper = mount(Onboarding, {
        global: { plugins: [pinia] },
      })

      const button = wrapper.find('button:contains("Get Started")')
      expect(button.exists()).toBe(true)
    })

    it('should not show back button on welcome screen', () => {
      const wrapper = mount(Onboarding, {
        global: { plugins: [pinia] },
      })

      const backButton = wrapper.find('button:contains("Back")')
      expect(backButton.exists()).toBe(false)
    })

    it('should not show step counter on welcome screen', () => {
      const wrapper = mount(Onboarding, {
        global: { plugins: [pinia] },
      })

      expect(wrapper.text()).not.toContain('Step')
    })
  })

  describe('Step Navigation', () => {
    it('should advance from step 0 to step 1 when Get Started clicked', async () => {
      const wrapper = mount(Onboarding, {
        global: { plugins: [pinia] },
      })

      await wrapper.vm.nextStep()

      expect(wrapper.vm.currentStep).toBe(1)
      expect(wrapper.text()).toContain('Choose Your Budgeting Style')
    })

    it('should show step counter on step 1', async () => {
      const wrapper = mount(Onboarding, {
        global: { plugins: [pinia] },
      })

      wrapper.vm.currentStep = 1
      await wrapper.vm.$nextTick()

      expect(wrapper.text()).toContain('Step 1 of 4')
    })

    it('should navigate forward through all steps', async () => {
      const wrapper = mount(Onboarding, {
        global: { plugins: [pinia] },
      })

      // Step 0 → 1
      await wrapper.vm.nextStep()
      expect(wrapper.vm.currentStep).toBe(1)

      // Step 1 → 2 (need mode selected)
      wrapper.vm.budgetMode = 'paycheck'
      await wrapper.vm.nextStep()
      expect(wrapper.vm.currentStep).toBe(2)

      // Step 2 → 3 (need valid income)
      wrapper.vm.monthlyIncome = 5000
      wrapper.vm.daysUntilPaycheck = 15
      await wrapper.vm.nextStep()
      expect(wrapper.vm.currentStep).toBe(3)

      // Step 3 → 4
      await wrapper.vm.nextStep()
      expect(wrapper.vm.currentStep).toBe(4)
    })

    it('should navigate backward through steps', async () => {
      const wrapper = mount(Onboarding, {
        global: { plugins: [pinia] },
      })

      wrapper.vm.currentStep = 3

      await wrapper.vm.prevStep()
      expect(wrapper.vm.currentStep).toBe(2)

      await wrapper.vm.prevStep()
      expect(wrapper.vm.currentStep).toBe(1)

      await wrapper.vm.prevStep()
      expect(wrapper.vm.currentStep).toBe(0)
    })

    it('should not go below step 0 when clicking back', async () => {
      const wrapper = mount(Onboarding, {
        global: { plugins: [pinia] },
      })

      wrapper.vm.currentStep = 0
      await wrapper.vm.prevStep()

      expect(wrapper.vm.currentStep).toBe(0)
    })

    it('should preserve data when navigating back and forward', async () => {
      const wrapper = mount(Onboarding, {
        global: { plugins: [pinia] },
      })

      // Set data on step 1
      wrapper.vm.currentStep = 1
      wrapper.vm.budgetMode = 'paycheck'

      // Go forward
      wrapper.vm.currentStep = 2
      wrapper.vm.monthlyIncome = 5000

      // Go back to step 1
      wrapper.vm.prevStep()
      expect(wrapper.vm.budgetMode).toBe('paycheck')

      // Go forward to step 2
      wrapper.vm.nextStep()
      expect(wrapper.vm.monthlyIncome).toBe(5000)
    })
  })

  describe('Mode Selection (Step 1)', () => {
    it('should render both mode options', () => {
      const wrapper = mount(Onboarding, {
        global: { plugins: [pinia] },
      })
      wrapper.vm.currentStep = 1

      expect(wrapper.text()).toContain('Paycheck Mode')
      expect(wrapper.text()).toContain('Fixed Pool Mode')
    })

    it('should select paycheck mode when clicked', async () => {
      const wrapper = mount(Onboarding, {
        global: { plugins: [pinia] },
      })
      wrapper.vm.currentStep = 1

      wrapper.vm.budgetMode = 'paycheck'
      await wrapper.vm.$nextTick()

      expect(wrapper.vm.budgetMode).toBe('paycheck')
    })

    it('should select fixed pool mode when clicked', async () => {
      const wrapper = mount(Onboarding, {
        global: { plugins: [pinia] },
      })
      wrapper.vm.currentStep = 1

      wrapper.vm.budgetMode = 'fixed_pool'
      await wrapper.vm.$nextTick()

      expect(wrapper.vm.budgetMode).toBe('fixed_pool')
    })

    it('should enable Next button when mode selected', () => {
      const wrapper = mount(Onboarding, {
        global: { plugins: [pinia] },
      })
      wrapper.vm.currentStep = 1
      wrapper.vm.budgetMode = 'paycheck'

      expect(wrapper.vm.canProceed).toBe(true)
    })

    it('should highlight selected mode with border', async () => {
      const wrapper = mount(Onboarding, {
        global: { plugins: [pinia] },
      })
      wrapper.vm.currentStep = 1
      wrapper.vm.budgetMode = 'paycheck'
      await wrapper.vm.$nextTick()

      const paycheckCard = wrapper.find('v-card:contains("Paycheck Mode")')
      expect(paycheckCard.classes()).toContain('border-primary')
    })
  })

  describe('Input Validation (Step 2)', () => {
    describe('Paycheck Mode', () => {
      it('should show monthly income field', async () => {
        const wrapper = mount(Onboarding, {
          global: { plugins: [pinia] },
        })
        wrapper.vm.currentStep = 2
        wrapper.vm.budgetMode = 'paycheck'
        await wrapper.vm.$nextTick()

        expect(wrapper.text()).toContain('total monthly income')
      })

      it('should reject zero income', async () => {
        const wrapper = mount(Onboarding, {
          global: { plugins: [pinia] },
        })
        wrapper.vm.currentStep = 2
        wrapper.vm.budgetMode = 'paycheck'
        wrapper.vm.monthlyIncome = 0
        wrapper.vm.daysUntilPaycheck = 15

        expect(wrapper.vm.canProceed).toBe(false)
      })

      it('should reject negative income', async () => {
        const wrapper = mount(Onboarding, {
          global: { plugins: [pinia] },
        })
        wrapper.vm.currentStep = 2
        wrapper.vm.budgetMode = 'paycheck'
        wrapper.vm.monthlyIncome = -100
        wrapper.vm.daysUntilPaycheck = 15

        expect(wrapper.vm.canProceed).toBe(false)
      })

      it('should accept positive income', () => {
        const wrapper = mount(Onboarding, {
          global: { plugins: [pinia] },
        })
        wrapper.vm.currentStep = 2
        wrapper.vm.budgetMode = 'paycheck'
        wrapper.vm.monthlyIncome = 5000
        wrapper.vm.daysUntilPaycheck = 15

        expect(wrapper.vm.canProceed).toBe(true)
      })

      it('should reject zero days until paycheck', () => {
        const wrapper = mount(Onboarding, {
          global: { plugins: [pinia] },
        })
        wrapper.vm.currentStep = 2
        wrapper.vm.budgetMode = 'paycheck'
        wrapper.vm.monthlyIncome = 5000
        wrapper.vm.daysUntilPaycheck = 0

        expect(wrapper.vm.canProceed).toBe(false)
      })

      it('should reject negative days', () => {
        const wrapper = mount(Onboarding, {
          global: { plugins: [pinia] },
        })
        wrapper.vm.currentStep = 2
        wrapper.vm.budgetMode = 'paycheck'
        wrapper.vm.monthlyIncome = 5000
        wrapper.vm.daysUntilPaycheck = -5

        expect(wrapper.vm.canProceed).toBe(false)
      })

      it('should accept very large income values', () => {
        const wrapper = mount(Onboarding, {
          global: { plugins: [pinia] },
        })
        wrapper.vm.currentStep = 2
        wrapper.vm.budgetMode = 'paycheck'
        wrapper.vm.monthlyIncome = 999999.99
        wrapper.vm.daysUntilPaycheck = 15

        expect(wrapper.vm.canProceed).toBe(true)
        expect(wrapper.vm.monthlyIncome).toBe(999999.99)
      })

      it('should handle decimal income values', () => {
        const wrapper = mount(Onboarding, {
          global: { plugins: [pinia] },
        })
        wrapper.vm.currentStep = 2
        wrapper.vm.budgetMode = 'paycheck'
        wrapper.vm.monthlyIncome = 5432.67
        wrapper.vm.daysUntilPaycheck = 15

        expect(wrapper.vm.monthlyIncome).toBe(5432.67)
      })
    })

    describe('Fixed Pool Mode', () => {
      it('should show total money field', async () => {
        const wrapper = mount(Onboarding, {
          global: { plugins: [pinia] },
        })
        wrapper.vm.currentStep = 2
        wrapper.vm.budgetMode = 'fixed_pool'
        await wrapper.vm.$nextTick()

        expect(wrapper.text()).toContain('total money')
      })

      it('should reject zero total money', () => {
        const wrapper = mount(Onboarding, {
          global: { plugins: [pinia] },
        })
        wrapper.vm.currentStep = 2
        wrapper.vm.budgetMode = 'fixed_pool'
        wrapper.vm.totalMoney = 0

        expect(wrapper.vm.canProceed).toBe(false)
      })

      it('should accept positive total money', () => {
        const wrapper = mount(Onboarding, {
          global: { plugins: [pinia] },
        })
        wrapper.vm.currentStep = 2
        wrapper.vm.budgetMode = 'fixed_pool'
        wrapper.vm.totalMoney = 10000

        expect(wrapper.vm.canProceed).toBe(true)
      })
    })
  })

  describe('Expense Management (Step 3)', () => {
    it('should render expense form', () => {
      const wrapper = mount(Onboarding, {
        global: { plugins: [pinia] },
      })
      wrapper.vm.currentStep = 3

      expect(wrapper.text()).toContain('Add Your Monthly Expenses')
    })

    it('should add expense when valid data provided', async () => {
      const wrapper = mount(Onboarding, {
        global: { plugins: [pinia] },
      })
      wrapper.vm.currentStep = 3

      wrapper.vm.newExpense = { name: 'Rent', amount: 1500, is_fixed: true }
      wrapper.vm.addExpense()

      expect(wrapper.vm.expenses).toHaveLength(1)
      expect(wrapper.vm.expenses[0].name).toBe('Rent')
      expect(wrapper.vm.expenses[0].amount).toBe(1500)
    })

    it('should clear form after adding expense', () => {
      const wrapper = mount(Onboarding, {
        global: { plugins: [pinia] },
      })
      wrapper.vm.currentStep = 3

      wrapper.vm.newExpense = { name: 'Rent', amount: 1500, is_fixed: true }
      wrapper.vm.addExpense()

      expect(wrapper.vm.newExpense.name).toBe('')
      expect(wrapper.vm.newExpense.amount).toBe(0)
    })

    it('should calculate total expenses', () => {
      const wrapper = mount(Onboarding, {
        global: { plugins: [pinia] },
      })
      wrapper.vm.currentStep = 3

      wrapper.vm.expenses = [
        { name: 'Rent', amount: 1500, is_fixed: true },
        { name: 'Utils', amount: 200, is_fixed: true },
        { name: 'Food', amount: 400, is_fixed: false },
      ]

      expect(wrapper.vm.totalExpenses).toBe(2100)
    })

    it('should remove expense when delete clicked', () => {
      const wrapper = mount(Onboarding, {
        global: { plugins: [pinia] },
      })
      wrapper.vm.currentStep = 3

      wrapper.vm.expenses = [
        { name: 'Rent', amount: 1500, is_fixed: true },
        { name: 'Utils', amount: 200, is_fixed: true },
      ]

      wrapper.vm.removeExpense(0)

      expect(wrapper.vm.expenses).toHaveLength(1)
      expect(wrapper.vm.expenses[0].name).toBe('Utils')
    })

    it('should not add expense without name', () => {
      const wrapper = mount(Onboarding, {
        global: { plugins: [pinia] },
      })
      wrapper.vm.currentStep = 3

      wrapper.vm.newExpense = { name: '', amount: 100, is_fixed: true }
      wrapper.vm.addExpense()

      expect(wrapper.vm.expenses).toHaveLength(0)
    })

    it('should not add expense with zero amount', () => {
      const wrapper = mount(Onboarding, {
        global: { plugins: [pinia] },
      })
      wrapper.vm.currentStep = 3

      wrapper.vm.newExpense = { name: 'Test', amount: 0, is_fixed: true }
      wrapper.vm.addExpense()

      expect(wrapper.vm.expenses).toHaveLength(0)
    })

    it('should show empty state when no expenses', async () => {
      const wrapper = mount(Onboarding, {
        global: { plugins: [pinia] },
      })
      wrapper.vm.currentStep = 3
      await wrapper.vm.$nextTick()

      expect(wrapper.text()).toContain('No expenses added yet')
      expect(wrapper.text()).toContain('You can skip this step')
    })

    it('should allow proceeding without adding expenses', () => {
      const wrapper = mount(Onboarding, {
        global: { plugins: [pinia] },
      })
      wrapper.vm.currentStep = 3

      expect(wrapper.vm.canProceed).toBe(true)
    })
  })

  describe('The Number Calculation (Step 4)', () => {
    describe('Paycheck Mode', () => {
      it('should calculate The Number correctly', () => {
        const wrapper = mount(Onboarding, {
          global: { plugins: [pinia] },
        })

        wrapper.vm.budgetMode = 'paycheck'
        wrapper.vm.monthlyIncome = 5000
        wrapper.vm.daysUntilPaycheck = 15
        wrapper.vm.expenses = [
          { name: 'Rent', amount: 1500, is_fixed: true },
          { name: 'Utils', amount: 500, is_fixed: true },
        ]

        // (5000 - 2000) / 15 = 200
        expect(wrapper.vm.calculatedNumber).toBe(200)
      })

      it('should return 0 when expenses exceed income', () => {
        const wrapper = mount(Onboarding, {
          global: { plugins: [pinia] },
        })

        wrapper.vm.budgetMode = 'paycheck'
        wrapper.vm.monthlyIncome = 2000
        wrapper.vm.daysUntilPaycheck = 15
        wrapper.vm.expenses = [
          { name: 'Rent', amount: 3000, is_fixed: true },
        ]

        expect(wrapper.vm.calculatedNumber).toBe(0)
      })

      it('should handle zero days remaining', () => {
        const wrapper = mount(Onboarding, {
          global: { plugins: [pinia] },
        })

        wrapper.vm.budgetMode = 'paycheck'
        wrapper.vm.monthlyIncome = 5000
        wrapper.vm.daysUntilPaycheck = 0
        wrapper.vm.expenses = []

        expect(wrapper.vm.calculatedNumber).toBe(0)
      })
    })

    describe('Fixed Pool Mode', () => {
      it('should calculate The Number correctly', () => {
        const wrapper = mount(Onboarding, {
          global: { plugins: [pinia] },
        })

        wrapper.vm.budgetMode = 'fixed_pool'
        wrapper.vm.totalMoney = 10000
        wrapper.vm.expenses = [
          { name: 'Rent', amount: 2000, is_fixed: true },
        ]

        // Money will last: 10000 / 2000 = 5 months
        // Days: 5 * 30 = 150
        // Daily: 10000 / 150 = 66.67
        const expected = 10000 / 150
        expect(wrapper.vm.calculatedNumber).toBeCloseTo(expected, 2)
      })

      it('should handle zero expenses', () => {
        const wrapper = mount(Onboarding, {
          global: { plugins: [pinia] },
        })

        wrapper.vm.budgetMode = 'fixed_pool'
        wrapper.vm.totalMoney = 10000
        wrapper.vm.expenses = []

        // With 0 expenses, should return 0 (no ongoing costs)
        expect(wrapper.vm.calculatedNumber).toBe(0)
      })
    })

    it('should display summary on step 4', async () => {
      const wrapper = mount(Onboarding, {
        global: { plugins: [pinia] },
      })

      wrapper.vm.currentStep = 4
      wrapper.vm.budgetMode = 'paycheck'
      wrapper.vm.monthlyIncome = 5000
      wrapper.vm.daysUntilPaycheck = 15
      wrapper.vm.expenses = [{ name: 'Rent', amount: 1500, is_fixed: true }]

      await wrapper.vm.$nextTick()

      expect(wrapper.text()).toContain('Here\'s Your Number!')
      expect(wrapper.text()).toContain('Monthly Income: $5000.00')
      expect(wrapper.text()).toContain('Total Expenses: $1500.00')
    })

    it('should show warning when expenses exceed income', async () => {
      const wrapper = mount(Onboarding, {
        global: { plugins: [pinia] },
      })

      wrapper.vm.currentStep = 4
      wrapper.vm.budgetMode = 'paycheck'
      wrapper.vm.monthlyIncome = 2000
      wrapper.vm.expenses = [{ name: 'Rent', amount: 3000, is_fixed: true }]

      await wrapper.vm.$nextTick()

      expect(wrapper.text()).toContain('Your expenses exceed')
    })

    it('should show tight budget warning', async () => {
      const wrapper = mount(Onboarding, {
        global: { plugins: [pinia] },
      })

      wrapper.vm.currentStep = 4
      wrapper.vm.budgetMode = 'paycheck'
      wrapper.vm.monthlyIncome = 500
      wrapper.vm.daysUntilPaycheck = 30
      wrapper.vm.expenses = []

      // 500 / 30 = 16.67 < 20
      await wrapper.vm.$nextTick()

      expect(wrapper.text()).toContain('Your budget is tight')
    })
  })

  describe('Completion Flow', () => {
    it('should show Complete Setup button on step 4', async () => {
      const wrapper = mount(Onboarding, {
        global: { plugins: [pinia] },
      })

      wrapper.vm.currentStep = 4
      await wrapper.vm.$nextTick()

      expect(wrapper.text()).toContain('Complete Setup')
    })

    it('should call API to save budget config', async () => {
      vi.mocked(budgetApi.configureBudget).mockResolvedValue({ data: {} } as any)
      vi.mocked(budgetApi.createExpense).mockResolvedValue({ data: {} } as any)

      const wrapper = mount(Onboarding, {
        global: { plugins: [pinia] },
      })

      wrapper.vm.budgetMode = 'paycheck'
      wrapper.vm.monthlyIncome = 5000
      wrapper.vm.daysUntilPaycheck = 15
      wrapper.vm.expenses = []

      await wrapper.vm.completeOnboarding()
      await flushPromises()

      expect(budgetApi.configureBudget).toHaveBeenCalledWith({
        mode: 'paycheck',
        monthly_income: 5000,
        days_until_paycheck: 15,
      })
    })

    it('should create all expenses', async () => {
      vi.mocked(budgetApi.configureBudget).mockResolvedValue({ data: {} } as any)
      vi.mocked(budgetApi.createExpense).mockResolvedValue({ data: {} } as any)

      const wrapper = mount(Onboarding, {
        global: { plugins: [pinia] },
      })

      wrapper.vm.budgetMode = 'paycheck'
      wrapper.vm.monthlyIncome = 5000
      wrapper.vm.daysUntilPaycheck = 15
      wrapper.vm.expenses = [
        { name: 'Rent', amount: 1500, is_fixed: true },
        { name: 'Utils', amount: 200, is_fixed: true },
      ]

      await wrapper.vm.completeOnboarding()
      await flushPromises()

      expect(budgetApi.createExpense).toHaveBeenCalledTimes(2)
    })

    it('should emit complete event on success', async () => {
      vi.mocked(budgetApi.configureBudget).mockResolvedValue({ data: {} } as any)

      const wrapper = mount(Onboarding, {
        global: { plugins: [pinia] },
      })

      wrapper.vm.budgetMode = 'paycheck'
      wrapper.vm.monthlyIncome = 5000
      wrapper.vm.daysUntilPaycheck = 15
      wrapper.vm.expenses = []

      await wrapper.vm.completeOnboarding()
      await flushPromises()

      expect(wrapper.emitted('complete')).toBeTruthy()
    })

    it('should show error snackbar on API failure', async () => {
      vi.mocked(budgetApi.configureBudget).mockRejectedValue({
        response: { data: { detail: 'Server error' } }
      })

      const wrapper = mount(Onboarding, {
        global: { plugins: [pinia] },
      })

      wrapper.vm.budgetMode = 'paycheck'
      wrapper.vm.monthlyIncome = 5000
      wrapper.vm.daysUntilPaycheck = 15

      await wrapper.vm.completeOnboarding()
      await flushPromises()

      expect(wrapper.vm.showError).toBe(true)
      expect(wrapper.vm.errorMessage).toBe('Server error')
    })

    it('should set loading state during save', async () => {
      let loadingDuringSave = false

      vi.mocked(budgetApi.configureBudget).mockImplementation(async () => {
        loadingDuringSave = wrapper.vm.loading
        return { data: {} } as any
      })

      const wrapper = mount(Onboarding, {
        global: { plugins: [pinia] },
      })

      wrapper.vm.budgetMode = 'paycheck'
      wrapper.vm.monthlyIncome = 5000
      wrapper.vm.daysUntilPaycheck = 15
      wrapper.vm.expenses = []

      await wrapper.vm.completeOnboarding()
      await flushPromises()

      expect(loadingDuringSave).toBe(true)
      expect(wrapper.vm.loading).toBe(false)
    })

    it('should handle network timeout', async () => {
      vi.mocked(budgetApi.configureBudget).mockImplementation(() =>
        new Promise((_, reject) =>
          setTimeout(() => reject(new Error('Timeout')), 100)
        )
      )

      const wrapper = mount(Onboarding, {
        global: { plugins: [pinia] },
      })

      wrapper.vm.budgetMode = 'paycheck'
      wrapper.vm.monthlyIncome = 5000
      wrapper.vm.daysUntilPaycheck = 15

      await wrapper.vm.completeOnboarding()
      await flushPromises()

      expect(wrapper.vm.showError).toBe(true)
    })
  })
})
```

---

## Appendix B: Quick Reference

### Running Tests

```bash
# Unit tests (fast)
npm run test

# Unit tests with coverage
npm run test:coverage

# Watch mode (for development)
npm run test:watch

# E2E tests (requires app running)
npm run test:e2e

# E2E in headed mode (see browser)
npm run test:e2e:headed

# All tests
npm run test:all
```

### Writing a New Test

```typescript
// 1. Import test utilities
import { describe, it, expect, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'

// 2. Import component
import MyComponent from './MyComponent.vue'

// 3. Describe test suite
describe('MyComponent', () => {
  let pinia: any

  // 4. Setup
  beforeEach(() => {
    pinia = createPinia()
    setActivePinia(pinia)
  })

  // 5. Write test
  it('should render correctly', () => {
    const wrapper = mount(MyComponent, {
      global: { plugins: [pinia] },
      props: { title: 'Test' }
    })

    expect(wrapper.text()).toContain('Test')
  })
})
```

### Test Naming Conventions

- **File names**: `ComponentName.spec.ts`
- **Describe blocks**: Feature or component name
- **Test names**: Start with "should" + describe behavior
- **Good**: `should disable button when form is invalid`
- **Bad**: `test button disabled`

---

## Conclusion

This comprehensive test strategy provides a clear roadmap to achieve 92%+ test coverage and ensure the reliability of The Number web application. The **critical priority is implementing tests for Onboarding.vue**, as this represents the largest coverage gap and highest risk area.

By following the phased implementation plan and adhering to TDD principles, the team will build confidence in the codebase, reduce production bugs, and enable rapid, safe iteration on features.

**Next Steps:**
1. Review and approve this strategy
2. Allocate resources for Phase 1 (Onboarding tests)
3. Begin implementation using provided test templates
4. Track coverage metrics weekly
5. Adjust timeline based on team velocity

---

**Questions or feedback?** Contact the Test Architect or open a discussion in the team channel.
