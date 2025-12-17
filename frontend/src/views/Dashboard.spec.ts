import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { createRouter, createMemoryHistory } from 'vue-router'
import Dashboard from './Dashboard.vue'
import { useBudgetStore } from '@/stores/budget'
import { mockBudgetNumber, mockTransactions } from '@/test/test-utils'

// Mock components
vi.mock('@/components/NumberDisplay.vue', () => ({
  default: { template: '<div class="number-display-mock">Number Display</div>' }
}))

describe('Dashboard Component', () => {
  let router: any
  let pinia: any

  beforeEach(async () => {
    pinia = createPinia()
    setActivePinia(pinia)

    router = createRouter({
      history: createMemoryHistory(),
      routes: [
        { path: '/', name: 'dashboard', component: Dashboard },
        { path: '/settings', name: 'settings', component: { template: '<div>Settings</div>' } },
        { path: '/transactions', name: 'transactions', component: { template: '<div>Transactions</div>' } },
      ],
    })

    await router.push('/')
    await router.isReady()
  })

  describe('Loading State', () => {
    it('should show loading spinner when loading and no budget number', async () => {
      const wrapper = mount(Dashboard, {
        global: {
          plugins: [pinia, router],
        },
      })

      const store = useBudgetStore()
      store.loading = true
      store.budgetNumber = null

      await wrapper.vm.$nextTick()

      expect(wrapper.find('.v-progress-circular').exists()).toBe(true)
    })

    it('should not show loading spinner when budget number exists', async () => {
      const wrapper = mount(Dashboard, {
        global: {
          plugins: [pinia, router],
        },
      })

      const store = useBudgetStore()
      store.loading = true
      store.budgetNumber = mockBudgetNumber

      await wrapper.vm.$nextTick()

      expect(wrapper.find('.v-progress-circular').exists()).toBe(false)
    })
  })

  describe('Not Configured State', () => {
    it('should show not configured message when budget number is null', async () => {
      const wrapper = mount(Dashboard, {
        global: {
          plugins: [pinia, router],
        },
      })

      const store = useBudgetStore()
      store.loading = false
      store.budgetNumber = null

      await wrapper.vm.$nextTick()

      expect(wrapper.text()).toContain('Budget Not Configured')
    })

    it('should show configure budget button when not configured', async () => {
      const wrapper = mount(Dashboard, {
        global: {
          plugins: [pinia, router],
        },
      })

      const store = useBudgetStore()
      store.loading = false
      store.budgetNumber = null

      await wrapper.vm.$nextTick()

      expect(wrapper.text()).toContain('Configure Budget')
    })

    it('should link to settings when configure button clicked', async () => {
      const wrapper = mount(Dashboard, {
        global: {
          plugins: [pinia, router],
        },
      })

      const store = useBudgetStore()
      store.loading = false
      store.budgetNumber = null

      await wrapper.vm.$nextTick()

      const button = wrapper.find('.v-btn')
      expect(button.attributes('to')).toBeDefined()
    })
  })

  describe('Error State', () => {
    it('should show error alert when error exists', async () => {
      const wrapper = mount(Dashboard, {
        global: {
          plugins: [pinia, router],
        },
      })

      const store = useBudgetStore()
      store.error = 'Failed to load data'

      await wrapper.vm.$nextTick()

      expect(wrapper.text()).toContain('Failed to load data')
    })

    it('should clear error when alert is closed', async () => {
      const wrapper = mount(Dashboard, {
        global: {
          plugins: [pinia, router],
        },
      })

      const store = useBudgetStore()
      store.error = 'Test error'

      await wrapper.vm.$nextTick()

      const alert = wrapper.find('.v-alert')
      expect(alert.exists()).toBe(true)

      // Simulate closing the alert
      store.error = null
      await wrapper.vm.$nextTick()

      expect(store.error).toBeNull()
    })
  })

  describe('Configured State', () => {
    it('should show NumberDisplay when budget is configured', async () => {
      const wrapper = mount(Dashboard, {
        global: {
          plugins: [pinia, router],
        },
      })

      const store = useBudgetStore()
      store.budgetNumber = mockBudgetNumber
      store.loading = false

      await wrapper.vm.$nextTick()

      expect(wrapper.find('.number-display-mock').exists()).toBe(true)
    })

    it('should show quick actions section when configured', async () => {
      const wrapper = mount(Dashboard, {
        global: {
          plugins: [pinia, router],
        },
      })

      const store = useBudgetStore()
      store.budgetNumber = mockBudgetNumber
      store.loading = false

      await wrapper.vm.$nextTick()

      expect(wrapper.text()).toContain('Record Spending')
      expect(wrapper.text()).toContain('Budget Summary')
      expect(wrapper.text()).toContain('Recent Transactions')
    })
  })

  describe('Record Spending Form', () => {
    it('should render spending form', async () => {
      const wrapper = mount(Dashboard, {
        global: {
          plugins: [pinia, router],
        },
      })

      const store = useBudgetStore()
      store.budgetNumber = mockBudgetNumber
      store.loading = false

      await wrapper.vm.$nextTick()

      expect(wrapper.find('form').exists()).toBe(true)
    })

    it('should have amount input field', async () => {
      const wrapper = mount(Dashboard, {
        global: {
          plugins: [pinia, router],
        },
      })

      const store = useBudgetStore()
      store.budgetNumber = mockBudgetNumber
      store.loading = false

      await wrapper.vm.$nextTick()

      const inputs = wrapper.findAll('input')
      expect(inputs.length).toBeGreaterThan(0)
    })

    it('should record spending with valid data', async () => {
      const wrapper = mount(Dashboard, {
        global: {
          plugins: [pinia, router],
        },
      })

      const store = useBudgetStore()
      store.budgetNumber = mockBudgetNumber
      store.loading = false
      store.recordTransaction = vi.fn().mockResolvedValue(undefined)

      await wrapper.vm.$nextTick()

      // Set form values
      wrapper.vm.spendingAmount = 25.50
      wrapper.vm.spendingDescription = 'Coffee'

      await wrapper.vm.recordSpending()
      await flushPromises()

      expect(store.recordTransaction).toHaveBeenCalledWith({
        amount: 25.50,
        description: 'Coffee',
      })
    })

    it('should not record spending with invalid amount', async () => {
      const wrapper = mount(Dashboard, {
        global: {
          plugins: [pinia, router],
        },
      })

      const store = useBudgetStore()
      store.budgetNumber = mockBudgetNumber
      store.loading = false
      store.recordTransaction = vi.fn()

      await wrapper.vm.$nextTick()

      wrapper.vm.spendingAmount = 0
      wrapper.vm.spendingDescription = 'Test'

      await wrapper.vm.recordSpending()

      expect(store.recordTransaction).not.toHaveBeenCalled()
    })

    it('should not record spending without description', async () => {
      const wrapper = mount(Dashboard, {
        global: {
          plugins: [pinia, router],
        },
      })

      const store = useBudgetStore()
      store.budgetNumber = mockBudgetNumber
      store.loading = false
      store.recordTransaction = vi.fn()

      await wrapper.vm.$nextTick()

      wrapper.vm.spendingAmount = 25.50
      wrapper.vm.spendingDescription = ''

      await wrapper.vm.recordSpending()

      expect(store.recordTransaction).not.toHaveBeenCalled()
    })

    it('should clear form after successful submission', async () => {
      const wrapper = mount(Dashboard, {
        global: {
          plugins: [pinia, router],
        },
      })

      const store = useBudgetStore()
      store.budgetNumber = mockBudgetNumber
      store.loading = false
      store.recordTransaction = vi.fn().mockResolvedValue(undefined)

      await wrapper.vm.$nextTick()

      wrapper.vm.spendingAmount = 25.50
      wrapper.vm.spendingDescription = 'Coffee'

      await wrapper.vm.recordSpending()
      await flushPromises()

      expect(wrapper.vm.spendingAmount).toBe(0)
      expect(wrapper.vm.spendingDescription).toBe('')
    })
  })

  describe('Budget Summary', () => {
    it('should display budget mode', async () => {
      const wrapper = mount(Dashboard, {
        global: {
          plugins: [pinia, router],
        },
      })

      const store = useBudgetStore()
      store.budgetNumber = mockBudgetNumber
      store.loading = false

      await wrapper.vm.$nextTick()

      expect(wrapper.text()).toContain('Mode:')
      expect(wrapper.text()).toContain('Paycheck')
    })

    it('should display monthly income for paycheck mode', async () => {
      const wrapper = mount(Dashboard, {
        global: {
          plugins: [pinia, router],
        },
      })

      const store = useBudgetStore()
      store.budgetNumber = { ...mockBudgetNumber, mode: 'paycheck' }
      store.loading = false

      await wrapper.vm.$nextTick()

      expect(wrapper.text()).toContain('Monthly Income:')
    })

    it('should display total expenses', async () => {
      const wrapper = mount(Dashboard, {
        global: {
          plugins: [pinia, router],
        },
      })

      const store = useBudgetStore()
      store.budgetNumber = mockBudgetNumber
      store.loading = false

      await wrapper.vm.$nextTick()

      expect(wrapper.text()).toContain('Total Expenses:')
    })

    it('should display remaining money when available', async () => {
      const wrapper = mount(Dashboard, {
        global: {
          plugins: [pinia, router],
        },
      })

      const store = useBudgetStore()
      store.budgetNumber = mockBudgetNumber
      store.loading = false

      await wrapper.vm.$nextTick()

      expect(wrapper.text()).toContain('Remaining:')
    })
  })

  describe('Recent Transactions', () => {
    it('should display recent transactions when available', async () => {
      const wrapper = mount(Dashboard, {
        global: {
          plugins: [pinia, router],
        },
      })

      const store = useBudgetStore()
      store.budgetNumber = mockBudgetNumber
      store.transactions = mockTransactions
      store.loading = false

      await wrapper.vm.$nextTick()

      expect(wrapper.text()).toContain('Lunch')
      expect(wrapper.text()).toContain('Gas')
    })

    it('should show empty state when no transactions', async () => {
      const wrapper = mount(Dashboard, {
        global: {
          plugins: [pinia, router],
        },
      })

      const store = useBudgetStore()
      store.budgetNumber = mockBudgetNumber
      store.transactions = []
      store.loading = false

      await wrapper.vm.$nextTick()

      expect(wrapper.text()).toContain('No transactions yet')
    })

    it('should limit to 5 recent transactions', async () => {
      const wrapper = mount(Dashboard, {
        global: {
          plugins: [pinia, router],
        },
      })

      const store = useBudgetStore()
      store.budgetNumber = mockBudgetNumber
      store.transactions = Array(10).fill(null).map((_, i) => ({
        id: i,
        date: '2024-01-15T12:00:00',
        amount: 10,
        description: `Transaction ${i}`,
        created_at: '2024-01-15T12:00:00',
      }))
      store.loading = false

      await wrapper.vm.$nextTick()

      expect(wrapper.vm.recentTransactions.length).toBe(5)
    })

    it('should have view all transactions button', async () => {
      const wrapper = mount(Dashboard, {
        global: {
          plugins: [pinia, router],
        },
      })

      const store = useBudgetStore()
      store.budgetNumber = mockBudgetNumber
      store.loading = false

      await wrapper.vm.$nextTick()

      expect(wrapper.text()).toContain('View All')
    })
  })

  describe('Component Lifecycle', () => {
    it('should load dashboard data on mount', async () => {
      const store = useBudgetStore()
      store.fetchNumber = vi.fn().mockResolvedValue(undefined)
      store.fetchTransactions = vi.fn().mockResolvedValue(undefined)

      mount(Dashboard, {
        global: {
          plugins: [pinia, router],
        },
      })

      await flushPromises()

      expect(store.fetchNumber).toHaveBeenCalled()
      expect(store.fetchTransactions).toHaveBeenCalledWith(5)
    })

    it('should handle loading errors gracefully', async () => {
      const store = useBudgetStore()
      store.fetchNumber = vi.fn().mockRejectedValue(new Error('Network error'))
      store.fetchTransactions = vi.fn().mockResolvedValue(undefined)

      const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {})

      mount(Dashboard, {
        global: {
          plugins: [pinia, router],
        },
      })

      await flushPromises()

      expect(consoleSpy).toHaveBeenCalled()
      consoleSpy.mockRestore()
    })
  })
})
