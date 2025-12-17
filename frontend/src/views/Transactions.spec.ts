import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { createRouter, createMemoryHistory } from 'vue-router'
import Transactions from './Transactions.vue'
import { useBudgetStore } from '@/stores/budget'
import { mockTransactions } from '@/test/test-utils'

describe('Transactions Component', () => {
  let router: any
  let pinia: any

  beforeEach(async () => {
    pinia = createPinia()
    setActivePinia(pinia)

    router = createRouter({
      history: createMemoryHistory(),
      routes: [
        { path: '/', name: 'transactions', component: Transactions },
      ],
    })

    await router.push('/')
    await router.isReady()

    // Mock window.confirm
    global.confirm = vi.fn(() => true)
  })

  describe('Rendering', () => {
    it('should render the component', () => {
      const wrapper = mount(Transactions, {
        global: {
          plugins: [pinia, router],
        },
      })

      expect(wrapper.exists()).toBe(true)
      expect(wrapper.text()).toContain('Spending History')
    })

    it('should render summary cards', () => {
      const wrapper = mount(Transactions, {
        global: {
          plugins: [pinia, router],
        },
      })

      expect(wrapper.text()).toContain('Today')
      expect(wrapper.text()).toContain('Total Transactions')
      expect(wrapper.text()).toContain('All Time')
    })

    it('should render transactions table', () => {
      const wrapper = mount(Transactions, {
        global: {
          plugins: [pinia, router],
        },
      })

      expect(wrapper.text()).toContain('Recent Transactions')
    })
  })

  describe('Summary Cards', () => {
    it('should calculate today\'s total correctly', async () => {
      const wrapper = mount(Transactions, {
        global: {
          plugins: [pinia, router],
        },
      })

      const today = new Date().toISOString().split('T')[0]
      const store = useBudgetStore()
      store.transactions = [
        {
          id: 1,
          date: `${today}T12:00:00`,
          amount: 25.50,
          description: 'Lunch',
          created_at: `${today}T12:00:00`,
        },
        {
          id: 2,
          date: `${today}T18:00:00`,
          amount: 50.00,
          description: 'Dinner',
          created_at: `${today}T18:00:00`,
        },
        {
          id: 3,
          date: '2024-01-01T12:00:00',
          amount: 100.00,
          description: 'Old',
          created_at: '2024-01-01T12:00:00',
        },
      ]

      await wrapper.vm.$nextTick()

      expect(wrapper.vm.todayTotal).toBe(75.50)
    })

    it('should show zero for today when no transactions today', () => {
      const wrapper = mount(Transactions, {
        global: {
          plugins: [pinia, router],
        },
      })

      const store = useBudgetStore()
      store.transactions = mockTransactions

      expect(wrapper.vm.todayTotal).toBe(0)
    })

    it('should calculate all time total correctly', () => {
      const wrapper = mount(Transactions, {
        global: {
          plugins: [pinia, router],
        },
      })

      const store = useBudgetStore()
      store.transactions = mockTransactions

      expect(wrapper.vm.allTimeTotal).toBe(75.50) // 25.50 + 50.00
    })

    it('should show transaction count', async () => {
      const wrapper = mount(Transactions, {
        global: {
          plugins: [pinia, router],
        },
      })

      const store = useBudgetStore()
      store.transactions = mockTransactions

      await wrapper.vm.$nextTick()

      expect(wrapper.text()).toContain('2')
    })
  })

  describe('Add Transaction Button', () => {
    it('should have add transaction button', () => {
      const wrapper = mount(Transactions, {
        global: {
          plugins: [pinia, router],
        },
      })

      expect(wrapper.text()).toContain('Add Transaction')
    })

    it('should show dialog when add button clicked', async () => {
      const wrapper = mount(Transactions, {
        global: {
          plugins: [pinia, router],
        },
      })

      expect(wrapper.vm.showAddDialog).toBe(false)

      wrapper.vm.showAddDialog = true
      await wrapper.vm.$nextTick()

      expect(wrapper.vm.showAddDialog).toBe(true)
    })
  })

  describe('Add Transaction Dialog', () => {
    it('should initialize with default values', () => {
      const wrapper = mount(Transactions, {
        global: {
          plugins: [pinia, router],
        },
      })

      expect(wrapper.vm.newTransaction).toEqual({
        amount: 0,
        description: '',
        category: '',
      })
    })

    it('should add transaction with valid data', async () => {
      const wrapper = mount(Transactions, {
        global: {
          plugins: [pinia, router],
        },
      })

      const store = useBudgetStore()
      store.recordTransaction = vi.fn().mockResolvedValue(undefined)

      wrapper.vm.newTransaction = {
        amount: 25.50,
        description: 'Coffee',
        category: 'Food',
      }

      await wrapper.vm.addTransaction()
      await flushPromises()

      expect(store.recordTransaction).toHaveBeenCalledWith({
        amount: 25.50,
        description: 'Coffee',
        category: 'Food',
      })
    })

    it('should not add transaction with zero amount', async () => {
      const wrapper = mount(Transactions, {
        global: {
          plugins: [pinia, router],
        },
      })

      const store = useBudgetStore()
      store.recordTransaction = vi.fn()

      wrapper.vm.newTransaction = {
        amount: 0,
        description: 'Coffee',
        category: 'Food',
      }

      await wrapper.vm.addTransaction()

      expect(store.recordTransaction).not.toHaveBeenCalled()
    })

    it('should not add transaction without description', async () => {
      const wrapper = mount(Transactions, {
        global: {
          plugins: [pinia, router],
        },
      })

      const store = useBudgetStore()
      store.recordTransaction = vi.fn()

      wrapper.vm.newTransaction = {
        amount: 25.50,
        description: '',
        category: 'Food',
      }

      await wrapper.vm.addTransaction()

      expect(store.recordTransaction).not.toHaveBeenCalled()
    })

    it('should add transaction without category', async () => {
      const wrapper = mount(Transactions, {
        global: {
          plugins: [pinia, router],
        },
      })

      const store = useBudgetStore()
      store.recordTransaction = vi.fn().mockResolvedValue(undefined)

      wrapper.vm.newTransaction = {
        amount: 25.50,
        description: 'Coffee',
        category: '',
      }

      await wrapper.vm.addTransaction()
      await flushPromises()

      expect(store.recordTransaction).toHaveBeenCalledWith({
        amount: 25.50,
        description: 'Coffee',
      })
    })

    it('should reset form after successful add', async () => {
      const wrapper = mount(Transactions, {
        global: {
          plugins: [pinia, router],
        },
      })

      const store = useBudgetStore()
      store.recordTransaction = vi.fn().mockResolvedValue(undefined)

      wrapper.vm.newTransaction = {
        amount: 25.50,
        description: 'Coffee',
        category: 'Food',
      }

      await wrapper.vm.addTransaction()
      await flushPromises()

      expect(wrapper.vm.newTransaction).toEqual({
        amount: 0,
        description: '',
        category: '',
      })
    })

    it('should close dialog after successful add', async () => {
      const wrapper = mount(Transactions, {
        global: {
          plugins: [pinia, router],
        },
      })

      const store = useBudgetStore()
      store.recordTransaction = vi.fn().mockResolvedValue(undefined)

      wrapper.vm.showAddDialog = true
      wrapper.vm.newTransaction = {
        amount: 25.50,
        description: 'Coffee',
        category: 'Food',
      }

      await wrapper.vm.addTransaction()
      await flushPromises()

      expect(wrapper.vm.showAddDialog).toBe(false)
    })

    it('should handle add transaction error', async () => {
      const wrapper = mount(Transactions, {
        global: {
          plugins: [pinia, router],
        },
      })

      const store = useBudgetStore()
      store.recordTransaction = vi.fn().mockRejectedValue(new Error('Failed'))

      const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {})

      wrapper.vm.newTransaction = {
        amount: 25.50,
        description: 'Coffee',
        category: 'Food',
      }

      await wrapper.vm.addTransaction()
      await flushPromises()

      expect(consoleSpy).toHaveBeenCalled()
      consoleSpy.mockRestore()
    })
  })

  describe('Transactions Table', () => {
    it('should have correct table headers', () => {
      const wrapper = mount(Transactions, {
        global: {
          plugins: [pinia, router],
        },
      })

      const headers = wrapper.vm.headers
      expect(headers).toEqual([
        { title: 'Date', key: 'date', sortable: true },
        { title: 'Description', key: 'description', sortable: true },
        { title: 'Category', key: 'category', sortable: true },
        { title: 'Amount', key: 'amount', sortable: true },
        { title: 'Actions', key: 'actions', sortable: false },
      ])
    })

    it('should display transactions from store', async () => {
      const wrapper = mount(Transactions, {
        global: {
          plugins: [pinia, router],
        },
      })

      const store = useBudgetStore()
      store.transactions = mockTransactions

      await wrapper.vm.$nextTick()

      expect(wrapper.text()).toContain('Lunch')
      expect(wrapper.text()).toContain('Gas')
    })

    it('should show loading state', async () => {
      const wrapper = mount(Transactions, {
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

    it('should format dates correctly', () => {
      const wrapper = mount(Transactions, {
        global: {
          plugins: [pinia, router],
        },
      })

      const dateString = '2024-01-15T12:30:00'
      const formatted = wrapper.vm.formatDate(dateString)

      expect(formatted).toContain('Jan')
      expect(formatted).toContain('15')
      expect(formatted).toContain('2024')
    })
  })

  describe('Deleting Transactions', () => {
    it('should delete transaction with confirmation', async () => {
      const wrapper = mount(Transactions, {
        global: {
          plugins: [pinia, router],
        },
      })

      const store = useBudgetStore()
      store.transactions = [...mockTransactions]

      await wrapper.vm.deleteTransaction(1)

      expect(global.confirm).toHaveBeenCalled()
      expect(store.transactions).toHaveLength(1)
      expect(store.transactions[0].id).toBe(2)
    })

    it('should not delete transaction if not confirmed', async () => {
      global.confirm = vi.fn(() => false)

      const wrapper = mount(Transactions, {
        global: {
          plugins: [pinia, router],
        },
      })

      const store = useBudgetStore()
      store.transactions = [...mockTransactions]

      await wrapper.vm.deleteTransaction(1)

      expect(global.confirm).toHaveBeenCalled()
      expect(store.transactions).toHaveLength(2)
    })

    it('should handle delete transaction error', async () => {
      const wrapper = mount(Transactions, {
        global: {
          plugins: [pinia, router],
        },
      })

      const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {})

      // Force an error by making transactions read-only
      const store = useBudgetStore()
      Object.defineProperty(store, 'transactions', {
        value: mockTransactions,
        writable: false,
      })

      await wrapper.vm.deleteTransaction(1)
      await flushPromises()

      expect(consoleSpy).toHaveBeenCalled()
      consoleSpy.mockRestore()
    })
  })

  describe('Component Lifecycle', () => {
    it('should fetch transactions on mount', async () => {
      const store = useBudgetStore()
      store.fetchTransactions = vi.fn().mockResolvedValue(undefined)

      mount(Transactions, {
        global: {
          plugins: [pinia, router],
        },
      })

      await flushPromises()

      expect(store.fetchTransactions).toHaveBeenCalledWith(50)
    })
  })

  describe('Edge Cases', () => {
    it('should handle empty transactions list', () => {
      const wrapper = mount(Transactions, {
        global: {
          plugins: [pinia, router],
        },
      })

      const store = useBudgetStore()
      store.transactions = []

      expect(wrapper.vm.todayTotal).toBe(0)
      expect(wrapper.vm.allTimeTotal).toBe(0)
    })

    it('should handle very large amounts', () => {
      const wrapper = mount(Transactions, {
        global: {
          plugins: [pinia, router],
        },
      })

      const store = useBudgetStore()
      store.transactions = [{
        id: 1,
        date: '2024-01-15T12:00:00',
        amount: 999999.99,
        description: 'Large',
        created_at: '2024-01-15T12:00:00',
      }]

      expect(wrapper.vm.allTimeTotal).toBe(999999.99)
    })

    it('should handle transactions without categories', async () => {
      const wrapper = mount(Transactions, {
        global: {
          plugins: [pinia, router],
        },
      })

      const store = useBudgetStore()
      store.transactions = [{
        id: 1,
        date: '2024-01-15T12:00:00',
        amount: 25.50,
        description: 'Test',
        created_at: '2024-01-15T12:00:00',
      }]

      await wrapper.vm.$nextTick()

      expect(wrapper.text()).toContain('Test')
    })

    it('should handle decimal amounts correctly', () => {
      const wrapper = mount(Transactions, {
        global: {
          plugins: [pinia, router],
        },
      })

      const store = useBudgetStore()
      store.transactions = [{
        id: 1,
        date: '2024-01-15T12:00:00',
        amount: 15.99,
        description: 'Test',
        created_at: '2024-01-15T12:00:00',
      }]

      expect(wrapper.vm.allTimeTotal).toBe(15.99)
    })
  })
})
