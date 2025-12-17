import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { createRouter, createMemoryHistory } from 'vue-router'
import Expenses from './Expenses.vue'
import { useBudgetStore } from '@/stores/budget'
import { mockExpenses } from '@/test/test-utils'

describe('Expenses Component', () => {
  let router: any
  let pinia: any

  beforeEach(async () => {
    pinia = createPinia()
    setActivePinia(pinia)

    router = createRouter({
      history: createMemoryHistory(),
      routes: [
        { path: '/', name: 'expenses', component: Expenses },
      ],
    })

    await router.push('/')
    await router.isReady()

    // Mock window.confirm
    global.confirm = vi.fn(() => true)
  })

  describe('Rendering', () => {
    it('should render the component', () => {
      const wrapper = mount(Expenses, {
        global: {
          plugins: [pinia, router],
        },
      })

      expect(wrapper.exists()).toBe(true)
      expect(wrapper.text()).toContain('Manage Expenses')
    })

    it('should render add expense form', () => {
      const wrapper = mount(Expenses, {
        global: {
          plugins: [pinia, router],
        },
      })

      expect(wrapper.text()).toContain('Add New Expense')
    })

    it('should render expenses list', () => {
      const wrapper = mount(Expenses, {
        global: {
          plugins: [pinia, router],
        },
      })

      expect(wrapper.text()).toContain('Current Expenses')
    })
  })

  describe('Add Expense Form', () => {
    it('should have expense name input', () => {
      const wrapper = mount(Expenses, {
        global: {
          plugins: [pinia, router],
        },
      })

      const inputs = wrapper.findAll('input')
      expect(inputs.length).toBeGreaterThan(0)
    })

    it('should have amount input with dollar prefix', () => {
      const wrapper = mount(Expenses, {
        global: {
          plugins: [pinia, router],
        },
      })

      expect(wrapper.html()).toContain('Monthly Amount')
    })

    it('should have fixed checkbox', () => {
      const wrapper = mount(Expenses, {
        global: {
          plugins: [pinia, router],
        },
      })

      const checkboxes = wrapper.findAll('input[type="checkbox"]')
      expect(checkboxes.length).toBeGreaterThan(0)
    })

    it('should have add button', () => {
      const wrapper = mount(Expenses, {
        global: {
          plugins: [pinia, router],
        },
      })

      expect(wrapper.text()).toContain('Add')
    })

    it('should initialize form with default values', () => {
      const wrapper = mount(Expenses, {
        global: {
          plugins: [pinia, router],
        },
      })

      expect(wrapper.vm.newExpense).toEqual({
        name: '',
        amount: 0,
        is_fixed: true,
      })
    })
  })

  describe('Adding Expenses', () => {
    it('should add expense with valid data', async () => {
      const wrapper = mount(Expenses, {
        global: {
          plugins: [pinia, router],
        },
      })

      const store = useBudgetStore()
      store.addExpense = vi.fn().mockResolvedValue(undefined)

      wrapper.vm.newExpense = {
        name: 'Netflix',
        amount: 15,
        is_fixed: true,
      }

      await wrapper.vm.addExpense()
      await flushPromises()

      expect(store.addExpense).toHaveBeenCalledWith({
        name: 'Netflix',
        amount: 15,
        is_fixed: true,
      })
    })

    it('should not add expense with empty name', async () => {
      const wrapper = mount(Expenses, {
        global: {
          plugins: [pinia, router],
        },
      })

      const store = useBudgetStore()
      store.addExpense = vi.fn()

      wrapper.vm.newExpense = {
        name: '',
        amount: 15,
        is_fixed: true,
      }

      await wrapper.vm.addExpense()

      expect(store.addExpense).not.toHaveBeenCalled()
    })

    it('should not add expense with zero or negative amount', async () => {
      const wrapper = mount(Expenses, {
        global: {
          plugins: [pinia, router],
        },
      })

      const store = useBudgetStore()
      store.addExpense = vi.fn()

      wrapper.vm.newExpense = {
        name: 'Netflix',
        amount: 0,
        is_fixed: true,
      }

      await wrapper.vm.addExpense()

      expect(store.addExpense).not.toHaveBeenCalled()
    })

    it('should reset form after successful add', async () => {
      const wrapper = mount(Expenses, {
        global: {
          plugins: [pinia, router],
        },
      })

      const store = useBudgetStore()
      store.addExpense = vi.fn().mockResolvedValue(undefined)

      wrapper.vm.newExpense = {
        name: 'Netflix',
        amount: 15,
        is_fixed: true,
      }

      await wrapper.vm.addExpense()
      await flushPromises()

      expect(wrapper.vm.newExpense).toEqual({
        name: '',
        amount: 0,
        is_fixed: true,
      })
    })

    it('should handle add expense error', async () => {
      const wrapper = mount(Expenses, {
        global: {
          plugins: [pinia, router],
        },
      })

      const store = useBudgetStore()
      store.addExpense = vi.fn().mockRejectedValue(new Error('Failed'))

      const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {})

      wrapper.vm.newExpense = {
        name: 'Netflix',
        amount: 15,
        is_fixed: true,
      }

      await wrapper.vm.addExpense()
      await flushPromises()

      expect(consoleSpy).toHaveBeenCalled()
      consoleSpy.mockRestore()
    })
  })

  describe('Expenses List', () => {
    it('should display expenses from store', async () => {
      const wrapper = mount(Expenses, {
        global: {
          plugins: [pinia, router],
        },
      })

      const store = useBudgetStore()
      store.expenses = mockExpenses

      await wrapper.vm.$nextTick()

      expect(wrapper.text()).toContain('Rent')
      expect(wrapper.text()).toContain('Groceries')
    })

    it('should show loading state', async () => {
      const wrapper = mount(Expenses, {
        global: {
          plugins: [pinia, router],
        },
      })

      const store = useBudgetStore()
      store.loading = true

      await wrapper.vm.$nextTick()

      const table = wrapper.find('.v-data-table')
      expect(table.attributes('loading')).toBeDefined()
    })

    it('should calculate total expenses', async () => {
      const wrapper = mount(Expenses, {
        global: {
          plugins: [pinia, router],
        },
      })

      const store = useBudgetStore()
      store.expenses = mockExpenses

      await wrapper.vm.$nextTick()

      expect(wrapper.vm.totalExpenses).toBe(2000) // 1500 + 500
    })

    it('should display total expenses in header', async () => {
      const wrapper = mount(Expenses, {
        global: {
          plugins: [pinia, router],
        },
      })

      const store = useBudgetStore()
      store.expenses = mockExpenses

      await wrapper.vm.$nextTick()

      expect(wrapper.text()).toContain('Total: $2000.00/mo')
    })

    it('should handle empty expenses list', () => {
      const wrapper = mount(Expenses, {
        global: {
          plugins: [pinia, router],
        },
      })

      const store = useBudgetStore()
      store.expenses = []

      expect(wrapper.vm.totalExpenses).toBe(0)
    })
  })

  describe('Deleting Expenses', () => {
    it('should delete expense with confirmation', async () => {
      const wrapper = mount(Expenses, {
        global: {
          plugins: [pinia, router],
        },
      })

      const store = useBudgetStore()
      store.removeExpense = vi.fn().mockResolvedValue(undefined)

      await wrapper.vm.deleteExpense(1)
      await flushPromises()

      expect(global.confirm).toHaveBeenCalled()
      expect(store.removeExpense).toHaveBeenCalledWith(1)
    })

    it('should not delete expense if not confirmed', async () => {
      global.confirm = vi.fn(() => false)

      const wrapper = mount(Expenses, {
        global: {
          plugins: [pinia, router],
        },
      })

      const store = useBudgetStore()
      store.removeExpense = vi.fn()

      await wrapper.vm.deleteExpense(1)

      expect(global.confirm).toHaveBeenCalled()
      expect(store.removeExpense).not.toHaveBeenCalled()
    })

    it('should handle delete expense error', async () => {
      const wrapper = mount(Expenses, {
        global: {
          plugins: [pinia, router],
        },
      })

      const store = useBudgetStore()
      store.removeExpense = vi.fn().mockRejectedValue(new Error('Failed'))

      const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {})

      await wrapper.vm.deleteExpense(1)
      await flushPromises()

      expect(consoleSpy).toHaveBeenCalled()
      consoleSpy.mockRestore()
    })
  })

  describe('Data Table', () => {
    it('should have correct table headers', () => {
      const wrapper = mount(Expenses, {
        global: {
          plugins: [pinia, router],
        },
      })

      const headers = wrapper.vm.headers
      expect(headers).toEqual([
        { title: 'Name', key: 'name', sortable: true },
        { title: 'Amount', key: 'amount', sortable: true },
        { title: 'Type', key: 'is_fixed', sortable: true },
        { title: 'Actions', key: 'actions', sortable: false },
      ])
    })

    it('should format amounts with dollar sign', async () => {
      const wrapper = mount(Expenses, {
        global: {
          plugins: [pinia, router],
        },
      })

      const store = useBudgetStore()
      store.expenses = mockExpenses

      await wrapper.vm.$nextTick()

      // Check if amounts are formatted
      expect(wrapper.text()).toContain('$1500.00')
      expect(wrapper.text()).toContain('$500.00')
    })

    it('should show fixed/variable chips', async () => {
      const wrapper = mount(Expenses, {
        global: {
          plugins: [pinia, router],
        },
      })

      const store = useBudgetStore()
      store.expenses = mockExpenses

      await wrapper.vm.$nextTick()

      expect(wrapper.text()).toContain('Fixed')
      expect(wrapper.text()).toContain('Variable')
    })

    it('should have delete button for each expense', async () => {
      const wrapper = mount(Expenses, {
        global: {
          plugins: [pinia, router],
        },
      })

      const store = useBudgetStore()
      store.expenses = mockExpenses

      await wrapper.vm.$nextTick()

      const deleteButtons = wrapper.findAll('.v-btn')
      expect(deleteButtons.length).toBeGreaterThan(0)
    })
  })

  describe('Component Lifecycle', () => {
    it('should fetch expenses on mount', async () => {
      const store = useBudgetStore()
      store.fetchExpenses = vi.fn().mockResolvedValue(undefined)

      mount(Expenses, {
        global: {
          plugins: [pinia, router],
        },
      })

      await flushPromises()

      expect(store.fetchExpenses).toHaveBeenCalled()
    })
  })

  describe('Edge Cases', () => {
    it('should handle very large expense amounts', () => {
      const wrapper = mount(Expenses, {
        global: {
          plugins: [pinia, router],
        },
      })

      const store = useBudgetStore()
      store.expenses = [{
        id: 1,
        name: 'Large',
        amount: 999999.99,
        is_fixed: true,
        created_at: '',
        updated_at: '',
      }]

      expect(wrapper.vm.totalExpenses).toBe(999999.99)
    })

    it('should handle decimal amounts correctly', () => {
      const wrapper = mount(Expenses, {
        global: {
          plugins: [pinia, router],
        },
      })

      const store = useBudgetStore()
      store.expenses = [{
        id: 1,
        name: 'Test',
        amount: 15.99,
        is_fixed: true,
        created_at: '',
        updated_at: '',
      }]

      expect(wrapper.vm.totalExpenses).toBe(15.99)
    })
  })
})
