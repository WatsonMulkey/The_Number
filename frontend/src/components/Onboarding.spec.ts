import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import Onboarding from './Onboarding.vue'
import { budgetApi } from '@/services/api'

// Mock the API
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

  /**
   * ========================================
   * COMPONENT SETUP TESTS (5 tests)
   * ========================================
   */
  describe('Component Setup', () => {
    it('should mount successfully', () => {
      const wrapper = mount(Onboarding, {
        global: { plugins: [pinia] },
      })

      expect(wrapper.exists()).toBe(true)
      expect(wrapper.find('.onboarding-card').exists()).toBe(true)
    })

    it('should initialize with currentStep = 0', () => {
      const wrapper = mount(Onboarding, {
        global: { plugins: [pinia] },
      })

      expect(wrapper.vm.currentStep).toBe(0)
    })

    it('should initialize all data refs properly', () => {
      const wrapper = mount(Onboarding, {
        global: { plugins: [pinia] },
      })

      // Check initial state
      expect(wrapper.vm.budgetMode).toBe('paycheck')
      expect(wrapper.vm.monthlyIncome).toBe(0)
      expect(wrapper.vm.daysUntilPaycheck).toBe(14)
      expect(wrapper.vm.totalMoney).toBe(0)
      expect(wrapper.vm.expenses).toEqual([])
      expect(wrapper.vm.newExpense).toEqual({ name: '', amount: 0, is_fixed: true })
      expect(wrapper.vm.loading).toBe(false)
      expect(wrapper.vm.showError).toBe(false)
      expect(wrapper.vm.errorMessage).toBe('')
    })

    it('should register complete emit', () => {
      const wrapper = mount(Onboarding, {
        global: { plugins: [pinia] },
      })

      // Emits should be registered (we'll test actual emission later)
      expect(wrapper.vm.$options?.emits).toBeDefined()
    })

    it('should log component loaded to console', () => {
      const consoleSpy = vi.spyOn(console, 'log')

      mount(Onboarding, {
        global: { plugins: [pinia] },
      })

      expect(consoleSpy).toHaveBeenCalledWith('🎯 Onboarding component loaded')
      consoleSpy.mockRestore()
    })
  })

  /**
   * ========================================
   * STEP 0 - WELCOME SCREEN (3 tests)
   * ========================================
   */
  describe('Step 0 - Welcome Screen', () => {
    it('should render welcome content', () => {
      const wrapper = mount(Onboarding, {
        global: { plugins: [pinia] },
      })

      expect(wrapper.text()).toContain('Welcome to The Number!')
      expect(wrapper.text()).toContain('4 quick steps')
      expect(wrapper.text()).toContain('Choose your budgeting style')
      expect(wrapper.text()).toContain('Enter your income')
      expect(wrapper.text()).toContain('Add your monthly expenses')
      expect(wrapper.text()).toContain('See your daily spending limit')
    })

    it('should show Get Started button', () => {
      const wrapper = mount(Onboarding, {
        global: { plugins: [pinia] },
      })

      const buttons = wrapper.findAll('button')
      const getStartedButton = buttons.find(btn => btn.text().includes('Get Started'))

      expect(getStartedButton).toBeDefined()
      expect(getStartedButton?.attributes('disabled')).toBeUndefined()
    })

    it('should move to step 1 when Get Started is clicked', async () => {
      const wrapper = mount(Onboarding, {
        global: { plugins: [pinia] },
      })

      expect(wrapper.vm.currentStep).toBe(0)

      await wrapper.vm.nextStep()
      await wrapper.vm.$nextTick()

      expect(wrapper.vm.currentStep).toBe(1)
    })
  })

  /**
   * ========================================
   * STEP 1 - BUDGET MODE SELECTION (8 tests)
   * ========================================
   */
  describe('Step 1 - Budget Mode Selection', () => {
    it('should render both mode options', async () => {
      const wrapper = mount(Onboarding, {
        global: { plugins: [pinia] },
      })

      wrapper.vm.currentStep = 1
      await wrapper.vm.$nextTick()

      expect(wrapper.text()).toContain('Paycheck Mode')
      expect(wrapper.text()).toContain('Fixed Pool Mode')
      expect(wrapper.text()).toContain('regular income')
      expect(wrapper.text()).toContain('fixed amount of money')
    })

    it('should allow paycheck mode selection', async () => {
      const wrapper = mount(Onboarding, {
        global: { plugins: [pinia] },
      })

      wrapper.vm.currentStep = 1
      wrapper.vm.budgetMode = 'paycheck'
      await wrapper.vm.$nextTick()

      expect(wrapper.vm.budgetMode).toBe('paycheck')
    })

    it('should allow fixed pool mode selection', async () => {
      const wrapper = mount(Onboarding, {
        global: { plugins: [pinia] },
      })

      wrapper.vm.currentStep = 1
      wrapper.vm.budgetMode = 'fixed_pool'
      await wrapper.vm.$nextTick()

      expect(wrapper.vm.budgetMode).toBe('fixed_pool')
    })

    it('should persist mode when selected', async () => {
      const wrapper = mount(Onboarding, {
        global: { plugins: [pinia] },
      })

      wrapper.vm.currentStep = 1
      wrapper.vm.budgetMode = 'fixed_pool'
      await wrapper.vm.$nextTick()

      // Navigate away and back
      wrapper.vm.currentStep = 2
      await wrapper.vm.$nextTick()
      wrapper.vm.currentStep = 1
      await wrapper.vm.$nextTick()

      expect(wrapper.vm.budgetMode).toBe('fixed_pool')
    })

    it('should enable Next button when mode is selected', () => {
      const wrapper = mount(Onboarding, {
        global: { plugins: [pinia] },
      })

      wrapper.vm.currentStep = 1
      wrapper.vm.budgetMode = 'paycheck'

      expect(wrapper.vm.canProceed).toBe(true)
    })

    it('should have Next button enabled by default (paycheck mode is default)', () => {
      const wrapper = mount(Onboarding, {
        global: { plugins: [pinia] },
      })

      wrapper.vm.currentStep = 1

      // budgetMode defaults to 'paycheck'
      expect(wrapper.vm.budgetMode).toBe('paycheck')
      expect(wrapper.vm.canProceed).toBe(true)
    })

    it('should apply border-primary class to selected mode card', async () => {
      const wrapper = mount(Onboarding, {
        global: { plugins: [pinia] },
      })

      wrapper.vm.currentStep = 1
      wrapper.vm.budgetMode = 'paycheck'
      await wrapper.vm.$nextTick()

      const cards = wrapper.findAll('.v-card')
      const paycheckCard = cards.find(card => card.text().includes('Paycheck Mode'))

      expect(paycheckCard?.classes()).toContain('border-primary')
    })

    it('should proceed to step 2 when Next is clicked with mode selected', async () => {
      const wrapper = mount(Onboarding, {
        global: { plugins: [pinia] },
      })

      wrapper.vm.currentStep = 1
      wrapper.vm.budgetMode = 'paycheck'

      await wrapper.vm.nextStep()
      await wrapper.vm.$nextTick()

      expect(wrapper.vm.currentStep).toBe(2)
    })
  })

  /**
   * ========================================
   * STEP 2 - INCOME/MONEY INPUT (12 tests)
   * ========================================
   */
  describe('Step 2 - Income/Money Input', () => {
    describe('Paycheck Mode Fields', () => {
      it('should show correct fields for paycheck mode', async () => {
        const wrapper = mount(Onboarding, {
          global: { plugins: [pinia] },
        })

        wrapper.vm.currentStep = 2
        wrapper.vm.budgetMode = 'paycheck'
        await wrapper.vm.$nextTick()

        expect(wrapper.text()).toContain('total monthly income')
        expect(wrapper.text()).toContain('days until your next paycheck')
      })

      it('should reject negative income', () => {
        const wrapper = mount(Onboarding, {
          global: { plugins: [pinia] },
        })

        wrapper.vm.currentStep = 2
        wrapper.vm.budgetMode = 'paycheck'
        wrapper.vm.monthlyIncome = -100
        wrapper.vm.daysUntilPaycheck = 15

        expect(wrapper.vm.canProceed).toBe(false)
      })

      it('should reject zero income', () => {
        const wrapper = mount(Onboarding, {
          global: { plugins: [pinia] },
        })

        wrapper.vm.currentStep = 2
        wrapper.vm.budgetMode = 'paycheck'
        wrapper.vm.monthlyIncome = 0
        wrapper.vm.daysUntilPaycheck = 15

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

      it('should reject zero days', () => {
        const wrapper = mount(Onboarding, {
          global: { plugins: [pinia] },
        })

        wrapper.vm.currentStep = 2
        wrapper.vm.budgetMode = 'paycheck'
        wrapper.vm.monthlyIncome = 5000
        wrapper.vm.daysUntilPaycheck = 0

        expect(wrapper.vm.canProceed).toBe(false)
      })

      it('should accept large numbers (999,999.99)', () => {
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
    })

    describe('Fixed Pool Mode Fields', () => {
      it('should show correct fields for fixed pool mode', async () => {
        const wrapper = mount(Onboarding, {
          global: { plugins: [pinia] },
        })

        wrapper.vm.currentStep = 2
        wrapper.vm.budgetMode = 'fixed_pool'
        await wrapper.vm.$nextTick()

        expect(wrapper.text()).toContain('total money')
        expect(wrapper.text()).not.toContain('monthly income')
      })

      it('should reject negative total money', () => {
        const wrapper = mount(Onboarding, {
          global: { plugins: [pinia] },
        })

        wrapper.vm.currentStep = 2
        wrapper.vm.budgetMode = 'fixed_pool'
        wrapper.vm.totalMoney = -1000

        expect(wrapper.vm.canProceed).toBe(false)
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
    })

    it('should update Next button state based on validation', async () => {
      const wrapper = mount(Onboarding, {
        global: { plugins: [pinia] },
      })

      wrapper.vm.currentStep = 2
      wrapper.vm.budgetMode = 'paycheck'

      // Invalid state
      wrapper.vm.monthlyIncome = 0
      expect(wrapper.vm.canProceed).toBe(false)

      // Valid state
      wrapper.vm.monthlyIncome = 5000
      wrapper.vm.daysUntilPaycheck = 15
      expect(wrapper.vm.canProceed).toBe(true)
    })

    it('should update fields when mode is switched', async () => {
      const wrapper = mount(Onboarding, {
        global: { plugins: [pinia] },
      })

      wrapper.vm.currentStep = 2
      wrapper.vm.budgetMode = 'paycheck'
      await wrapper.vm.$nextTick()

      expect(wrapper.text()).toContain('monthly income')

      wrapper.vm.budgetMode = 'fixed_pool'
      await wrapper.vm.$nextTick()

      expect(wrapper.text()).toContain('total money')
      expect(wrapper.text()).not.toContain('days until')
    })

    it('should proceed to step 3 when validation passes', async () => {
      const wrapper = mount(Onboarding, {
        global: { plugins: [pinia] },
      })

      wrapper.vm.currentStep = 2
      wrapper.vm.budgetMode = 'paycheck'
      wrapper.vm.monthlyIncome = 5000
      wrapper.vm.daysUntilPaycheck = 15

      await wrapper.vm.nextStep()
      await wrapper.vm.$nextTick()

      expect(wrapper.vm.currentStep).toBe(3)
    })
  })

  /**
   * ========================================
   * STEP 3 - EXPENSES (15 tests)
   * ========================================
   */
  describe('Step 3 - Expenses', () => {
    it('should render add expense form', async () => {
      const wrapper = mount(Onboarding, {
        global: { plugins: [pinia] },
      })

      wrapper.vm.currentStep = 3
      await wrapper.vm.$nextTick()

      expect(wrapper.text()).toContain('Add Your Monthly Expenses')
      expect(wrapper.find('input[placeholder*="Expense Name"]').exists()).toBe(true)
    })

    it('should add valid expense', async () => {
      const wrapper = mount(Onboarding, {
        global: { plugins: [pinia] },
      })

      wrapper.vm.currentStep = 3
      wrapper.vm.newExpense = { name: 'Rent', amount: 1500, is_fixed: true }

      wrapper.vm.addExpense()

      expect(wrapper.vm.expenses).toHaveLength(1)
      expect(wrapper.vm.expenses[0].name).toBe('Rent')
      expect(wrapper.vm.expenses[0].amount).toBe(1500)
      expect(wrapper.vm.expenses[0].is_fixed).toBe(true)
    })

    it('should not add expense with empty name', () => {
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

    it('should not add expense with negative amount', () => {
      const wrapper = mount(Onboarding, {
        global: { plugins: [pinia] },
      })

      wrapper.vm.currentStep = 3
      wrapper.vm.newExpense = { name: 'Test', amount: -50, is_fixed: true }

      wrapper.vm.addExpense()

      expect(wrapper.vm.expenses).toHaveLength(0)
    })

    it('should show expense in list after adding', async () => {
      const wrapper = mount(Onboarding, {
        global: { plugins: [pinia] },
      })

      wrapper.vm.currentStep = 3
      wrapper.vm.newExpense = { name: 'Utilities', amount: 200, is_fixed: true }
      wrapper.vm.addExpense()
      await wrapper.vm.$nextTick()

      expect(wrapper.text()).toContain('Utilities')
      expect(wrapper.text()).toContain('$200.00')
    })

    it('should delete expense when delete button is clicked', () => {
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

    it('should update total when adding expense', () => {
      const wrapper = mount(Onboarding, {
        global: { plugins: [pinia] },
      })

      wrapper.vm.currentStep = 3
      expect(wrapper.vm.totalExpenses).toBe(0)

      wrapper.vm.newExpense = { name: 'Rent', amount: 1500, is_fixed: true }
      wrapper.vm.addExpense()

      expect(wrapper.vm.totalExpenses).toBe(1500)

      wrapper.vm.newExpense = { name: 'Utils', amount: 200, is_fixed: true }
      wrapper.vm.addExpense()

      expect(wrapper.vm.totalExpenses).toBe(1700)
    })

    it('should update total when removing expense', () => {
      const wrapper = mount(Onboarding, {
        global: { plugins: [pinia] },
      })

      wrapper.vm.currentStep = 3
      wrapper.vm.expenses = [
        { name: 'Rent', amount: 1500, is_fixed: true },
        { name: 'Utils', amount: 200, is_fixed: true },
      ]

      expect(wrapper.vm.totalExpenses).toBe(1700)

      wrapper.vm.removeExpense(0)

      expect(wrapper.vm.totalExpenses).toBe(200)
    })

    it('should allow skipping with zero expenses', () => {
      const wrapper = mount(Onboarding, {
        global: { plugins: [pinia] },
      })

      wrapper.vm.currentStep = 3
      wrapper.vm.expenses = []

      expect(wrapper.vm.canProceed).toBe(true)
    })

    it('should add multiple expenses', () => {
      const wrapper = mount(Onboarding, {
        global: { plugins: [pinia] },
      })

      wrapper.vm.currentStep = 3

      wrapper.vm.newExpense = { name: 'Rent', amount: 1500, is_fixed: true }
      wrapper.vm.addExpense()

      wrapper.vm.newExpense = { name: 'Utils', amount: 200, is_fixed: true }
      wrapper.vm.addExpense()

      wrapper.vm.newExpense = { name: 'Food', amount: 400, is_fixed: false }
      wrapper.vm.addExpense()

      expect(wrapper.vm.expenses).toHaveLength(3)
      expect(wrapper.vm.totalExpenses).toBe(2100)
    })

    it('should clear expense form after adding', () => {
      const wrapper = mount(Onboarding, {
        global: { plugins: [pinia] },
      })

      wrapper.vm.currentStep = 3
      wrapper.vm.newExpense = { name: 'Rent', amount: 1500, is_fixed: true }
      wrapper.vm.addExpense()

      expect(wrapper.vm.newExpense.name).toBe('')
      expect(wrapper.vm.newExpense.amount).toBe(0)
      expect(wrapper.vm.newExpense.is_fixed).toBe(true)
    })

    it('should go back to step 2', async () => {
      const wrapper = mount(Onboarding, {
        global: { plugins: [pinia] },
      })

      wrapper.vm.currentStep = 3
      await wrapper.vm.prevStep()

      expect(wrapper.vm.currentStep).toBe(2)
    })

    it('should proceed to step 4', async () => {
      const wrapper = mount(Onboarding, {
        global: { plugins: [pinia] },
      })

      wrapper.vm.currentStep = 3
      wrapper.vm.expenses = [{ name: 'Rent', amount: 1500, is_fixed: true }]

      await wrapper.vm.nextStep()

      expect(wrapper.vm.currentStep).toBe(4)
    })

    it('should show empty state when no expenses added', async () => {
      const wrapper = mount(Onboarding, {
        global: { plugins: [pinia] },
      })

      wrapper.vm.currentStep = 3
      await wrapper.vm.$nextTick()

      expect(wrapper.text()).toContain('No expenses added yet')
      expect(wrapper.text()).toContain('skip this step')
    })
  })

  /**
   * ========================================
   * STEP 4 - SHOW THE NUMBER (10 tests)
   * ========================================
   */
  describe('Step 4 - Show The Number', () => {
    it('should display summary correctly for paycheck mode', async () => {
      const wrapper = mount(Onboarding, {
        global: { plugins: [pinia] },
      })

      wrapper.vm.currentStep = 4
      wrapper.vm.budgetMode = 'paycheck'
      wrapper.vm.monthlyIncome = 5000
      wrapper.vm.daysUntilPaycheck = 15
      wrapper.vm.expenses = [{ name: 'Rent', amount: 1500, is_fixed: true }]
      await wrapper.vm.$nextTick()

      expect(wrapper.text()).toContain('Monthly Income: $5000.00')
      expect(wrapper.text()).toContain('Total Expenses: $1500.00')
      expect(wrapper.text()).toContain('After Expenses: $3500.00')
      expect(wrapper.text()).toContain('Days to Paycheck: 15')
    })

    it('should display summary correctly for fixed pool mode', async () => {
      const wrapper = mount(Onboarding, {
        global: { plugins: [pinia] },
      })

      wrapper.vm.currentStep = 4
      wrapper.vm.budgetMode = 'fixed_pool'
      wrapper.vm.totalMoney = 10000
      wrapper.vm.expenses = [{ name: 'Rent', amount: 2000, is_fixed: true }]
      await wrapper.vm.$nextTick()

      expect(wrapper.text()).toContain('Total Money: $10000.00')
      expect(wrapper.text()).toContain('Monthly Expenses: $2000.00')
      expect(wrapper.text()).toContain('Will Last: 5.0 months')
    })

    it('should calculate The Number correctly for paycheck mode', () => {
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

    it('should calculate The Number correctly for fixed pool mode', () => {
      const wrapper = mount(Onboarding, {
        global: { plugins: [pinia] },
      })

      wrapper.vm.budgetMode = 'fixed_pool'
      wrapper.vm.totalMoney = 10000
      wrapper.vm.expenses = [{ name: 'Rent', amount: 2000, is_fixed: true }]

      // Money lasts: 10000 / 2000 = 5 months = 150 days
      // Daily: 10000 / 150 = 66.67
      const expected = 10000 / 150
      expect(wrapper.vm.calculatedNumber).toBeCloseTo(expected, 2)
    })

    it('should show warning when expenses exceed income', async () => {
      const wrapper = mount(Onboarding, {
        global: { plugins: [pinia] },
      })

      wrapper.vm.currentStep = 4
      wrapper.vm.budgetMode = 'paycheck'
      wrapper.vm.monthlyIncome = 2000
      wrapper.vm.daysUntilPaycheck = 15
      wrapper.vm.expenses = [{ name: 'Rent', amount: 3000, is_fixed: true }]
      await wrapper.vm.$nextTick()

      expect(wrapper.text()).toContain('Your expenses exceed')
    })

    it('should show warning when daily limit is less than $20', async () => {
      const wrapper = mount(Onboarding, {
        global: { plugins: [pinia] },
      })

      wrapper.vm.currentStep = 4
      wrapper.vm.budgetMode = 'paycheck'
      wrapper.vm.monthlyIncome = 500
      wrapper.vm.daysUntilPaycheck = 30
      wrapper.vm.expenses = []
      await wrapper.vm.$nextTick()

      // 500 / 30 = 16.67 < 20
      expect(wrapper.text()).toContain('Your budget is tight')
    })

    it('should render tips section', async () => {
      const wrapper = mount(Onboarding, {
        global: { plugins: [pinia] },
      })

      wrapper.vm.currentStep = 4
      await wrapper.vm.$nextTick()

      expect(wrapper.text()).toContain('Tips for Success')
      expect(wrapper.text()).toContain('Check "The Number" every morning')
      expect(wrapper.text()).toContain('Record your spending')
    })

    it('should show Complete Setup button', async () => {
      const wrapper = mount(Onboarding, {
        global: { plugins: [pinia] },
      })

      wrapper.vm.currentStep = 4
      await wrapper.vm.$nextTick()

      expect(wrapper.text()).toContain('Complete Setup')
    })

    it('should go back to step 3', async () => {
      const wrapper = mount(Onboarding, {
        global: { plugins: [pinia] },
      })

      wrapper.vm.currentStep = 4
      await wrapper.vm.prevStep()

      expect(wrapper.vm.currentStep).toBe(3)
    })

    it('should return 0 when expenses exceed income in paycheck mode', () => {
      const wrapper = mount(Onboarding, {
        global: { plugins: [pinia] },
      })

      wrapper.vm.budgetMode = 'paycheck'
      wrapper.vm.monthlyIncome = 2000
      wrapper.vm.daysUntilPaycheck = 15
      wrapper.vm.expenses = [{ name: 'Rent', amount: 3000, is_fixed: true }]

      expect(wrapper.vm.calculatedNumber).toBe(0)
    })
  })

  /**
   * ========================================
   * API INTEGRATION TESTS (15 tests)
   * ========================================
   */
  describe('API Integration', () => {
    it('should save budget configuration on successful onboarding', async () => {
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

    it('should save all expenses on successful onboarding', async () => {
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
      expect(budgetApi.createExpense).toHaveBeenCalledWith({ name: 'Rent', amount: 1500, is_fixed: true })
      expect(budgetApi.createExpense).toHaveBeenCalledWith({ name: 'Utils', amount: 200, is_fixed: true })
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
      expect(wrapper.emitted('complete')).toHaveLength(1)
    })

    it('should show error on config save failure', async () => {
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
      expect(wrapper.emitted('complete')).toBeFalsy()
    })

    it('should show error on expense save failure', async () => {
      vi.mocked(budgetApi.configureBudget).mockResolvedValue({ data: {} } as any)
      vi.mocked(budgetApi.createExpense).mockRejectedValue({
        response: { data: { detail: 'Expense creation failed' } }
      })

      const wrapper = mount(Onboarding, {
        global: { plugins: [pinia] },
      })

      wrapper.vm.budgetMode = 'paycheck'
      wrapper.vm.monthlyIncome = 5000
      wrapper.vm.daysUntilPaycheck = 15
      wrapper.vm.expenses = [{ name: 'Rent', amount: 1500, is_fixed: true }]

      await wrapper.vm.completeOnboarding()
      await flushPromises()

      expect(wrapper.vm.showError).toBe(true)
      expect(wrapper.vm.errorMessage).toBe('Expense creation failed')
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

      expect(wrapper.vm.loading).toBe(false)

      await wrapper.vm.completeOnboarding()
      await flushPromises()

      expect(loadingDuringSave).toBe(true)
      expect(wrapper.vm.loading).toBe(false)
    })

    it('should disable buttons during save', async () => {
      vi.mocked(budgetApi.configureBudget).mockImplementation(async () => {
        // Simulate slow network
        await new Promise(resolve => setTimeout(resolve, 100))
        return { data: {} } as any
      })

      const wrapper = mount(Onboarding, {
        global: { plugins: [pinia] },
      })

      wrapper.vm.currentStep = 4
      wrapper.vm.budgetMode = 'paycheck'
      wrapper.vm.monthlyIncome = 5000
      wrapper.vm.daysUntilPaycheck = 15
      wrapper.vm.loading = true
      await wrapper.vm.$nextTick()

      const backButton = wrapper.findAll('button').find(btn => btn.text().includes('Back'))
      expect(backButton?.attributes('disabled')).toBeDefined()
    })

    it('should handle network timeout', async () => {
      vi.mocked(budgetApi.configureBudget).mockRejectedValue(
        new Error('Network timeout')
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
      expect(wrapper.vm.errorMessage).toBe('Failed to complete onboarding')
    })

    it('should handle 400 error', async () => {
      vi.mocked(budgetApi.configureBudget).mockRejectedValue({
        response: {
          status: 400,
          data: { detail: 'Invalid budget configuration' }
        }
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
      expect(wrapper.vm.errorMessage).toBe('Invalid budget configuration')
    })

    it('should handle 500 error', async () => {
      vi.mocked(budgetApi.configureBudget).mockRejectedValue({
        response: {
          status: 500,
          data: { detail: 'Internal server error' }
        }
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
      expect(wrapper.vm.errorMessage).toBe('Internal server error')
    })

    it('should save multiple expenses sequentially', async () => {
      const callOrder: string[] = []

      vi.mocked(budgetApi.configureBudget).mockImplementation(async () => {
        callOrder.push('config')
        return { data: {} } as any
      })

      vi.mocked(budgetApi.createExpense).mockImplementation(async (expense: any) => {
        callOrder.push(expense.name)
        return { data: {} } as any
      })

      const wrapper = mount(Onboarding, {
        global: { plugins: [pinia] },
      })

      wrapper.vm.budgetMode = 'paycheck'
      wrapper.vm.monthlyIncome = 5000
      wrapper.vm.daysUntilPaycheck = 15
      wrapper.vm.expenses = [
        { name: 'Rent', amount: 1500, is_fixed: true },
        { name: 'Utils', amount: 200, is_fixed: true },
        { name: 'Food', amount: 400, is_fixed: false },
      ]

      await wrapper.vm.completeOnboarding()
      await flushPromises()

      expect(callOrder).toEqual(['config', 'Rent', 'Utils', 'Food'])
    })

    it('should clear error on retry', async () => {
      // First call fails
      vi.mocked(budgetApi.configureBudget).mockRejectedValueOnce({
        response: { data: { detail: 'Network error' } }
      })
      // Second call succeeds
      vi.mocked(budgetApi.configureBudget).mockResolvedValueOnce({ data: {} } as any)

      const wrapper = mount(Onboarding, {
        global: { plugins: [pinia] },
      })

      wrapper.vm.budgetMode = 'paycheck'
      wrapper.vm.monthlyIncome = 5000
      wrapper.vm.daysUntilPaycheck = 15

      // First attempt - fails
      await wrapper.vm.completeOnboarding()
      await flushPromises()

      expect(wrapper.vm.showError).toBe(true)

      // Retry - succeeds
      await wrapper.vm.completeOnboarding()
      await flushPromises()

      expect(wrapper.vm.showError).toBe(false)
      expect(wrapper.emitted('complete')).toBeTruthy()
    })

    it('should save fixed pool mode configuration correctly', async () => {
      vi.mocked(budgetApi.configureBudget).mockResolvedValue({ data: {} } as any)

      const wrapper = mount(Onboarding, {
        global: { plugins: [pinia] },
      })

      wrapper.vm.budgetMode = 'fixed_pool'
      wrapper.vm.totalMoney = 10000
      wrapper.vm.expenses = []

      await wrapper.vm.completeOnboarding()
      await flushPromises()

      expect(budgetApi.configureBudget).toHaveBeenCalledWith({
        mode: 'fixed_pool',
        total_money: 10000,
      })
    })

    it('should not save expenses if none were added', async () => {
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

      expect(budgetApi.createExpense).not.toHaveBeenCalled()
      expect(wrapper.emitted('complete')).toBeTruthy()
    })
  })

  /**
   * ========================================
   * EDGE CASES (12 tests)
   * ========================================
   */
  describe('Edge Cases', () => {
    it('should handle very large income (999,999.99)', async () => {
      const wrapper = mount(Onboarding, {
        global: { plugins: [pinia] },
      })

      wrapper.vm.budgetMode = 'paycheck'
      wrapper.vm.monthlyIncome = 999999.99
      wrapper.vm.daysUntilPaycheck = 30
      wrapper.vm.expenses = []

      const calculatedNumber = wrapper.vm.calculatedNumber
      expect(calculatedNumber).toBeCloseTo(33333.33, 2)
      expect(isNaN(calculatedNumber)).toBe(false)
      expect(isFinite(calculatedNumber)).toBe(true)
    })

    it('should handle special characters in expense name', () => {
      const wrapper = mount(Onboarding, {
        global: { plugins: [pinia] },
      })

      wrapper.vm.currentStep = 3
      wrapper.vm.newExpense = { name: 'Coffee ☕ & Drinks 🍺', amount: 100, is_fixed: true }
      wrapper.vm.addExpense()

      expect(wrapper.vm.expenses).toHaveLength(1)
      expect(wrapper.vm.expenses[0].name).toBe('Coffee ☕ & Drinks 🍺')
    })

    it('should handle decimal amounts correctly', () => {
      const wrapper = mount(Onboarding, {
        global: { plugins: [pinia] },
      })

      wrapper.vm.currentStep = 3
      wrapper.vm.newExpense = { name: 'Subscription', amount: 12.99, is_fixed: true }
      wrapper.vm.addExpense()

      expect(wrapper.vm.expenses[0].amount).toBe(12.99)
      expect(wrapper.vm.totalExpenses).toBe(12.99)
    })

    it('should prevent division by zero in paycheck mode', () => {
      const wrapper = mount(Onboarding, {
        global: { plugins: [pinia] },
      })

      wrapper.vm.budgetMode = 'paycheck'
      wrapper.vm.monthlyIncome = 5000
      wrapper.vm.daysUntilPaycheck = 0
      wrapper.vm.expenses = []

      expect(wrapper.vm.calculatedNumber).toBe(0)
      expect(isNaN(wrapper.vm.calculatedNumber)).toBe(false)
    })

    it('should prevent division by zero in fixed pool mode', () => {
      const wrapper = mount(Onboarding, {
        global: { plugins: [pinia] },
      })

      wrapper.vm.budgetMode = 'fixed_pool'
      wrapper.vm.totalMoney = 10000
      wrapper.vm.expenses = []

      // With 0 expenses, daysRemaining should be 0
      expect(wrapper.vm.calculatedNumber).toBe(0)
      expect(isNaN(wrapper.vm.calculatedNumber)).toBe(false)
    })

    it('should maintain state when using back button', async () => {
      const wrapper = mount(Onboarding, {
        global: { plugins: [pinia] },
      })

      // Set up data on step 1
      wrapper.vm.currentStep = 1
      wrapper.vm.budgetMode = 'fixed_pool'

      // Move to step 2 and add data
      wrapper.vm.currentStep = 2
      wrapper.vm.totalMoney = 10000

      // Move to step 3 and add expense
      wrapper.vm.currentStep = 3
      wrapper.vm.newExpense = { name: 'Rent', amount: 1500, is_fixed: true }
      wrapper.vm.addExpense()

      // Go back to step 2
      await wrapper.vm.prevStep()
      expect(wrapper.vm.currentStep).toBe(2)
      expect(wrapper.vm.totalMoney).toBe(10000)

      // Go back to step 1
      await wrapper.vm.prevStep()
      expect(wrapper.vm.currentStep).toBe(1)
      expect(wrapper.vm.budgetMode).toBe('fixed_pool')

      // Go forward to step 2
      await wrapper.vm.nextStep()
      expect(wrapper.vm.currentStep).toBe(2)
      expect(wrapper.vm.totalMoney).toBe(10000)

      // Go forward to step 3
      await wrapper.vm.nextStep()
      expect(wrapper.vm.currentStep).toBe(3)
      expect(wrapper.vm.expenses).toHaveLength(1)
      expect(wrapper.vm.expenses[0].name).toBe('Rent')
    })

    it('should handle rapid clicking of Next button gracefully', async () => {
      const wrapper = mount(Onboarding, {
        global: { plugins: [pinia] },
      })

      wrapper.vm.currentStep = 0

      // Rapid clicks
      wrapper.vm.nextStep()
      wrapper.vm.nextStep()
      wrapper.vm.nextStep()
      await wrapper.vm.$nextTick()

      // Should only advance one step at a time
      expect(wrapper.vm.currentStep).toBe(1)
    })

    it('should handle rapid clicking of Back button gracefully', async () => {
      const wrapper = mount(Onboarding, {
        global: { plugins: [pinia] },
      })

      wrapper.vm.currentStep = 3

      // Rapid clicks
      wrapper.vm.prevStep()
      wrapper.vm.prevStep()
      wrapper.vm.prevStep()
      wrapper.vm.prevStep()
      wrapper.vm.prevStep()
      await wrapper.vm.$nextTick()

      // Should not go below 0
      expect(wrapper.vm.currentStep).toBe(0)
    })

    it('should not show step counter on step 0', async () => {
      const wrapper = mount(Onboarding, {
        global: { plugins: [pinia] },
      })

      wrapper.vm.currentStep = 0
      await wrapper.vm.$nextTick()

      expect(wrapper.text()).not.toContain('Step')
    })

    it('should show step counter on steps 1-4', async () => {
      const wrapper = mount(Onboarding, {
        global: { plugins: [pinia] },
      })

      wrapper.vm.currentStep = 1
      await wrapper.vm.$nextTick()
      expect(wrapper.text()).toContain('Step 1 of 4')

      wrapper.vm.currentStep = 2
      await wrapper.vm.$nextTick()
      expect(wrapper.text()).toContain('Step 2 of 4')

      wrapper.vm.currentStep = 3
      await wrapper.vm.$nextTick()
      expect(wrapper.text()).toContain('Step 3 of 4')

      wrapper.vm.currentStep = 4
      await wrapper.vm.$nextTick()
      expect(wrapper.text()).toContain('Step 4 of 4')
    })

    it('should not show Back button on step 0', async () => {
      const wrapper = mount(Onboarding, {
        global: { plugins: [pinia] },
      })

      wrapper.vm.currentStep = 0
      await wrapper.vm.$nextTick()

      const buttons = wrapper.findAll('button')
      const backButton = buttons.find(btn => btn.text().includes('Back'))

      expect(backButton).toBeUndefined()
    })

    it('should handle expense with very long name', () => {
      const wrapper = mount(Onboarding, {
        global: { plugins: [pinia] },
      })

      wrapper.vm.currentStep = 3
      const longName = 'A'.repeat(255)
      wrapper.vm.newExpense = { name: longName, amount: 100, is_fixed: true }
      wrapper.vm.addExpense()

      expect(wrapper.vm.expenses).toHaveLength(1)
      expect(wrapper.vm.expenses[0].name).toBe(longName)
    })
  })

  /**
   * ========================================
   * ADDITIONAL NAVIGATION TESTS
   * ========================================
   */
  describe('Additional Navigation Tests', () => {
    it('should not allow proceeding from step 1 without mode selection (edge case)', () => {
      const wrapper = mount(Onboarding, {
        global: { plugins: [pinia] },
      })

      wrapper.vm.currentStep = 1
      wrapper.vm.budgetMode = '' as any // Force invalid state

      expect(wrapper.vm.canProceed).toBe(false)
    })

    it('should not proceed from step 2 if validation fails', async () => {
      const wrapper = mount(Onboarding, {
        global: { plugins: [pinia] },
      })

      wrapper.vm.currentStep = 2
      wrapper.vm.budgetMode = 'paycheck'
      wrapper.vm.monthlyIncome = 0
      wrapper.vm.daysUntilPaycheck = 0

      const initialStep = wrapper.vm.currentStep
      await wrapper.vm.nextStep()

      // Should not advance
      expect(wrapper.vm.currentStep).toBe(initialStep)
    })

    it('should not proceed past step 4', async () => {
      const wrapper = mount(Onboarding, {
        global: { plugins: [pinia] },
      })

      wrapper.vm.currentStep = 4
      await wrapper.vm.nextStep()

      // Should stay at step 4
      expect(wrapper.vm.currentStep).toBe(4)
    })
  })

  /**
   * ========================================
   * CALCULATION EDGE CASES
   * ========================================
   */
  describe('Calculation Edge Cases', () => {
    it('should calculate correctly with zero expenses in paycheck mode', () => {
      const wrapper = mount(Onboarding, {
        global: { plugins: [pinia] },
      })

      wrapper.vm.budgetMode = 'paycheck'
      wrapper.vm.monthlyIncome = 3000
      wrapper.vm.daysUntilPaycheck = 15
      wrapper.vm.expenses = []

      // 3000 / 15 = 200
      expect(wrapper.vm.calculatedNumber).toBe(200)
    })

    it('should handle decimal precision in calculations', () => {
      const wrapper = mount(Onboarding, {
        global: { plugins: [pinia] },
      })

      wrapper.vm.budgetMode = 'paycheck'
      wrapper.vm.monthlyIncome = 1000
      wrapper.vm.daysUntilPaycheck = 3
      wrapper.vm.expenses = [{ name: 'Test', amount: 333.33, is_fixed: true }]

      // (1000 - 333.33) / 3 = 222.22333...
      expect(wrapper.vm.calculatedNumber).toBeCloseTo(222.22, 2)
    })

    it('should show infinity symbol when fixed pool has no expenses', async () => {
      const wrapper = mount(Onboarding, {
        global: { plugins: [pinia] },
      })

      wrapper.vm.currentStep = 4
      wrapper.vm.budgetMode = 'fixed_pool'
      wrapper.vm.totalMoney = 10000
      wrapper.vm.expenses = []
      await wrapper.vm.$nextTick()

      expect(wrapper.text()).toContain('∞')
    })
  })

  /**
   * ========================================
   * CONSOLE LOGGING TESTS
   * ========================================
   */
  describe('Console Logging', () => {
    it('should log when adding expense', () => {
      const consoleSpy = vi.spyOn(console, 'log')
      const wrapper = mount(Onboarding, {
        global: { plugins: [pinia] },
      })

      wrapper.vm.newExpense = { name: 'Test', amount: 100, is_fixed: true }
      wrapper.vm.addExpense()

      expect(consoleSpy).toHaveBeenCalledWith('Adding expense:', expect.any(Object))
      consoleSpy.mockRestore()
    })

    it('should log when removing expense', () => {
      const consoleSpy = vi.spyOn(console, 'log')
      const wrapper = mount(Onboarding, {
        global: { plugins: [pinia] },
      })

      wrapper.vm.expenses = [{ name: 'Test', amount: 100, is_fixed: true }]
      wrapper.vm.removeExpense(0)

      expect(consoleSpy).toHaveBeenCalledWith('Removing expense at index:', 0)
      consoleSpy.mockRestore()
    })

    it('should log when navigating steps', () => {
      const consoleSpy = vi.spyOn(console, 'log')
      const wrapper = mount(Onboarding, {
        global: { plugins: [pinia] },
      })

      wrapper.vm.nextStep()
      expect(consoleSpy).toHaveBeenCalledWith('Next step:', 1)

      wrapper.vm.prevStep()
      expect(consoleSpy).toHaveBeenCalledWith('Previous step:', 0)

      consoleSpy.mockRestore()
    })

    it('should log when completing onboarding', async () => {
      const consoleSpy = vi.spyOn(console, 'log')
      vi.mocked(budgetApi.configureBudget).mockResolvedValue({ data: {} } as any)

      const wrapper = mount(Onboarding, {
        global: { plugins: [pinia] },
      })

      wrapper.vm.budgetMode = 'paycheck'
      wrapper.vm.monthlyIncome = 5000
      wrapper.vm.daysUntilPaycheck = 15

      await wrapper.vm.completeOnboarding()
      await flushPromises()

      expect(consoleSpy).toHaveBeenCalledWith('🎉 Completing onboarding...')
      expect(consoleSpy).toHaveBeenCalledWith('✅ Onboarding complete!')

      consoleSpy.mockRestore()
    })
  })
})
