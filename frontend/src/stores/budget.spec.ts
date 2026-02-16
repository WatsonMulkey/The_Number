import { describe, it, expect, beforeEach, vi } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useBudgetStore } from './budget'
import { budgetApi } from '@/services/api'
import {
  createMockResponse,
  createMockError,
  mockBudgetNumber,
  mockBudgetNumberWithPool,
  mockExpenses,
  mockTransactions,
} from '@/test/test-utils'

// Mock the API module
vi.mock('@/services/api', () => ({
  budgetApi: {
    getNumber: vi.fn(),
    getExpenses: vi.fn(),
    createExpense: vi.fn(),
    deleteExpense: vi.fn(),
    updateExpense: vi.fn(),
    getTransactions: vi.fn(),
    createTransaction: vi.fn(),
    acceptPoolContribution: vi.fn(),
    declinePoolContribution: vi.fn(),
    togglePool: vi.fn(),
    addToPool: vi.fn(),
  },
}))

describe('Budget Store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  describe('Initial State', () => {
    it('should initialize with correct default values', () => {
      const store = useBudgetStore()

      expect(store.budgetNumber).toBeNull()
      expect(store.expenses).toEqual([])
      expect(store.transactions).toEqual([])
      expect(store.loading).toBe(false)
      expect(store.error).toBeNull()
    })
  })

  describe('Computed Properties', () => {
    it('should compute isConfigured correctly', () => {
      const store = useBudgetStore()

      expect(store.isConfigured).toBe(false)

      store.budgetNumber = mockBudgetNumber
      expect(store.isConfigured).toBe(true)
    })

    it('should compute dailyLimit correctly', () => {
      const store = useBudgetStore()

      expect(store.dailyLimit).toBe(0)

      store.budgetNumber = mockBudgetNumber
      expect(store.dailyLimit).toBe(100)
    })

    it('should compute isOverBudget correctly', () => {
      const store = useBudgetStore()

      expect(store.isOverBudget).toBe(false)

      store.budgetNumber = { ...mockBudgetNumber, is_over_budget: true }
      expect(store.isOverBudget).toBe(true)
    })
  })

  describe('fetchNumber', () => {
    it('should fetch budget number successfully', async () => {
      const store = useBudgetStore()
      vi.mocked(budgetApi.getNumber).mockResolvedValue(
        createMockResponse(mockBudgetNumber)
      )

      await store.fetchNumber()

      expect(budgetApi.getNumber).toHaveBeenCalledTimes(1)
      expect(store.budgetNumber).toEqual(mockBudgetNumber)
      expect(store.loading).toBe(false)
      expect(store.error).toBeNull()
    })

    it('should handle fetch number error', async () => {
      const store = useBudgetStore()
      const errorMessage = 'Failed to fetch budget number'
      vi.mocked(budgetApi.getNumber).mockRejectedValue(
        createMockError(errorMessage)
      )

      await expect(store.fetchNumber()).rejects.toThrow()

      expect(store.error).toBe(errorMessage)
      expect(store.loading).toBe(false)
    })

    it('should set loading state during fetch', async () => {
      const store = useBudgetStore()
      let loadingDuringFetch = false

      vi.mocked(budgetApi.getNumber).mockImplementation(async () => {
        loadingDuringFetch = store.loading
        return createMockResponse(mockBudgetNumber)
      })

      await store.fetchNumber()

      expect(loadingDuringFetch).toBe(true)
      expect(store.loading).toBe(false)
    })
  })

  describe('fetchExpenses', () => {
    it('should fetch expenses successfully', async () => {
      const store = useBudgetStore()
      vi.mocked(budgetApi.getExpenses).mockResolvedValue(
        createMockResponse(mockExpenses)
      )

      await store.fetchExpenses()

      expect(budgetApi.getExpenses).toHaveBeenCalledTimes(1)
      expect(store.expenses).toEqual(mockExpenses)
      expect(store.loading).toBe(false)
      expect(store.error).toBeNull()
    })

    it('should handle fetch expenses error', async () => {
      const store = useBudgetStore()
      const errorMessage = 'Failed to fetch expenses'
      vi.mocked(budgetApi.getExpenses).mockRejectedValue(
        createMockError(errorMessage)
      )

      await expect(store.fetchExpenses()).rejects.toThrow()

      expect(store.error).toBe(errorMessage)
      expect(store.loading).toBe(false)
    })
  })

  describe('addExpense (optimistic update)', () => {
    it('should add expense optimistically then replace with server data', async () => {
      const store = useBudgetStore()
      const newExpense = { name: 'Netflix', amount: 15, is_fixed: true }
      const createdExpense = { ...newExpense, id: 3, created_at: '2024-01-15', updated_at: '2024-01-15' }

      vi.mocked(budgetApi.createExpense).mockResolvedValue(
        createMockResponse(createdExpense)
      )
      vi.mocked(budgetApi.getNumber).mockResolvedValue(
        createMockResponse(mockBudgetNumber)
      )

      await store.addExpense(newExpense)

      expect(budgetApi.createExpense).toHaveBeenCalledWith(newExpense)
      // Should NOT refetch all expenses - uses optimistic update
      expect(budgetApi.getExpenses).not.toHaveBeenCalled()
      // Should refetch number (server-calculated)
      expect(budgetApi.getNumber).toHaveBeenCalled()
      // Final state should have the server response (with real id)
      expect(store.expenses[0]).toEqual(createdExpense)
    })

    it('should rollback optimistic add on error', async () => {
      const store = useBudgetStore()
      const newExpense = { name: 'Netflix', amount: 15, is_fixed: true }
      const errorMessage = 'Failed to add expense'

      vi.mocked(budgetApi.createExpense).mockRejectedValue(
        createMockError(errorMessage)
      )

      await expect(store.addExpense(newExpense)).rejects.toThrow()

      expect(store.error).toBe(errorMessage)
      // Optimistic entry should be rolled back
      expect(store.expenses.length).toBe(0)
    })
  })

  describe('removeExpense (optimistic update)', () => {
    it('should remove expense optimistically', async () => {
      const store = useBudgetStore()
      // Pre-populate expenses
      store.expenses = [...mockExpenses]
      const expenseId = 1

      vi.mocked(budgetApi.deleteExpense).mockResolvedValue(
        createMockResponse(null)
      )
      vi.mocked(budgetApi.getNumber).mockResolvedValue(
        createMockResponse(mockBudgetNumber)
      )

      await store.removeExpense(expenseId)

      expect(budgetApi.deleteExpense).toHaveBeenCalledWith(expenseId)
      // Should NOT refetch all expenses - removes optimistically
      expect(budgetApi.getExpenses).not.toHaveBeenCalled()
      // Should refetch number (server-calculated)
      expect(budgetApi.getNumber).toHaveBeenCalled()
      // Expense should be removed from local state
      expect(store.expenses.find(e => e.id === expenseId)).toBeUndefined()
      expect(store.expenses.length).toBe(1)
    })

    it('should rollback optimistic remove on error', async () => {
      const store = useBudgetStore()
      // Pre-populate expenses
      store.expenses = [...mockExpenses]
      const errorMessage = 'Failed to delete expense'

      vi.mocked(budgetApi.deleteExpense).mockRejectedValue(
        createMockError(errorMessage)
      )

      await expect(store.removeExpense(1)).rejects.toThrow()

      expect(store.error).toBe(errorMessage)
      // Should rollback - expenses restored
      expect(store.expenses.length).toBe(2)
      expect(store.expenses[0].id).toBe(1)
    })
  })

  describe('updateExpense (optimistic update)', () => {
    it('should update expense optimistically then confirm with server data', async () => {
      const store = useBudgetStore()
      // Pre-populate expenses
      store.expenses = [...mockExpenses]
      const updatedExpense = { ...mockExpenses[0], amount: 1600 }

      vi.mocked(budgetApi.updateExpense).mockResolvedValue(
        createMockResponse(updatedExpense)
      )
      vi.mocked(budgetApi.getNumber).mockResolvedValue(
        createMockResponse(mockBudgetNumber)
      )

      await store.updateExpense(1, { amount: 1600 })

      expect(budgetApi.updateExpense).toHaveBeenCalledWith(1, { amount: 1600 })
      // Should NOT refetch all expenses
      expect(budgetApi.getExpenses).not.toHaveBeenCalled()
      // Local state should be updated with server response
      expect(store.expenses[0].amount).toBe(1600)
    })

    it('should rollback optimistic update on error', async () => {
      const store = useBudgetStore()
      // Pre-populate expenses
      store.expenses = [...mockExpenses]
      const originalAmount = mockExpenses[0].amount
      const errorMessage = 'Failed to update expense'

      vi.mocked(budgetApi.updateExpense).mockRejectedValue(
        createMockError(errorMessage)
      )

      await expect(store.updateExpense(1, { amount: 9999 })).rejects.toThrow()

      expect(store.error).toBe(errorMessage)
      // Should rollback to original amount
      expect(store.expenses[0].amount).toBe(originalAmount)
    })
  })

  describe('recordTransaction (optimistic update)', () => {
    it('should add transaction optimistically then replace with server data', async () => {
      const store = useBudgetStore()
      const newTransaction = { amount: 25.50, description: 'Coffee' }
      const createdTransaction = { ...newTransaction, id: 3, date: '2024-01-16T10:00:00', created_at: '2024-01-16T10:00:00' }

      vi.mocked(budgetApi.createTransaction).mockResolvedValue(
        createMockResponse(createdTransaction)
      )
      vi.mocked(budgetApi.getNumber).mockResolvedValue(
        createMockResponse(mockBudgetNumber)
      )

      await store.recordTransaction(newTransaction)

      expect(budgetApi.createTransaction).toHaveBeenCalledWith(newTransaction)
      // Should NOT refetch all transactions
      expect(budgetApi.getTransactions).not.toHaveBeenCalled()
      // Should refetch number (server-calculated)
      expect(budgetApi.getNumber).toHaveBeenCalled()
      // Final state should have the server response (with real id)
      expect(store.transactions[0]).toEqual(createdTransaction)
    })

    it('should rollback optimistic transaction on error', async () => {
      const store = useBudgetStore()
      const newTransaction = { amount: 25.50, description: 'Coffee' }
      const errorMessage = 'Failed to record transaction'

      vi.mocked(budgetApi.createTransaction).mockRejectedValue(
        createMockError(errorMessage)
      )

      await expect(store.recordTransaction(newTransaction)).rejects.toThrow()

      expect(store.error).toBe(errorMessage)
      // Optimistic entry should be rolled back
      expect(store.transactions.length).toBe(0)
    })
  })

  describe('fetchTransactions', () => {
    it('should fetch transactions with default limit', async () => {
      const store = useBudgetStore()
      vi.mocked(budgetApi.getTransactions).mockResolvedValue(
        createMockResponse(mockTransactions)
      )

      await store.fetchTransactions()

      expect(budgetApi.getTransactions).toHaveBeenCalledWith(20)
      expect(store.transactions).toEqual(mockTransactions)
      expect(store.loading).toBe(false)
      expect(store.error).toBeNull()
    })

    it('should fetch transactions with custom limit', async () => {
      const store = useBudgetStore()
      vi.mocked(budgetApi.getTransactions).mockResolvedValue(
        createMockResponse(mockTransactions)
      )

      await store.fetchTransactions(50)

      expect(budgetApi.getTransactions).toHaveBeenCalledWith(50)
    })
  })

  // =============================================
  // Pool Feature Tests
  // =============================================

  describe('Pool Feature - acceptPoolContribution', () => {
    it('should accept pool contribution and refresh number', async () => {
      const store = useBudgetStore()
      const updatedNumber = { ...mockBudgetNumberWithPool, pending_pool_contribution: null, pool_balance: 195.50 }

      vi.mocked(budgetApi.acceptPoolContribution).mockResolvedValue(
        createMockResponse({ pool_balance: 195.50 })
      )
      vi.mocked(budgetApi.getNumber).mockResolvedValue(
        createMockResponse(updatedNumber)
      )

      await store.acceptPoolContribution()

      expect(budgetApi.acceptPoolContribution).toHaveBeenCalledTimes(1)
      expect(budgetApi.getNumber).toHaveBeenCalledTimes(1)
      expect(store.budgetNumber?.pending_pool_contribution).toBeNull()
      expect(store.budgetNumber?.pool_balance).toBe(195.50)
      expect(store.error).toBeNull()
    })

    it('should handle accept pool contribution error', async () => {
      const store = useBudgetStore()
      const errorMessage = 'Failed to accept pool contribution'

      vi.mocked(budgetApi.acceptPoolContribution).mockRejectedValue(
        createMockError(errorMessage)
      )

      await expect(store.acceptPoolContribution()).rejects.toThrow()

      expect(store.error).toBe(errorMessage)
    })
  })

  describe('Pool Feature - declinePoolContribution', () => {
    it('should decline pool contribution and refresh number', async () => {
      const store = useBudgetStore()
      const updatedNumber = { ...mockBudgetNumberWithPool, pending_pool_contribution: null }

      vi.mocked(budgetApi.declinePoolContribution).mockResolvedValue(
        createMockResponse({ status: 'declined', amount_declined: 45.50 })
      )
      vi.mocked(budgetApi.getNumber).mockResolvedValue(
        createMockResponse(updatedNumber)
      )

      await store.declinePoolContribution()

      expect(budgetApi.declinePoolContribution).toHaveBeenCalledTimes(1)
      expect(budgetApi.getNumber).toHaveBeenCalledTimes(1)
      expect(store.budgetNumber?.pending_pool_contribution).toBeNull()
      expect(store.error).toBeNull()
    })

    it('should handle decline pool contribution error', async () => {
      const store = useBudgetStore()
      const errorMessage = 'Failed to decline pool contribution'

      vi.mocked(budgetApi.declinePoolContribution).mockRejectedValue(
        createMockError(errorMessage)
      )

      await expect(store.declinePoolContribution()).rejects.toThrow()

      expect(store.error).toBe(errorMessage)
    })
  })

  describe('Pool Feature - togglePool', () => {
    it('should enable pool and refresh number', async () => {
      const store = useBudgetStore()
      const updatedNumber = { ...mockBudgetNumber, pool_enabled: true, pool_balance: 150 }

      vi.mocked(budgetApi.togglePool).mockResolvedValue(
        createMockResponse({ pool_balance: 150 })
      )
      vi.mocked(budgetApi.getNumber).mockResolvedValue(
        createMockResponse(updatedNumber)
      )

      await store.togglePool(true)

      expect(budgetApi.togglePool).toHaveBeenCalledWith(true)
      expect(budgetApi.getNumber).toHaveBeenCalledTimes(1)
      expect(store.budgetNumber?.pool_enabled).toBe(true)
      expect(store.error).toBeNull()
    })

    it('should disable pool and refresh number', async () => {
      const store = useBudgetStore()
      const updatedNumber = { ...mockBudgetNumberWithPool, pool_enabled: false }

      vi.mocked(budgetApi.togglePool).mockResolvedValue(
        createMockResponse({ pool_balance: 150 })
      )
      vi.mocked(budgetApi.getNumber).mockResolvedValue(
        createMockResponse(updatedNumber)
      )

      await store.togglePool(false)

      expect(budgetApi.togglePool).toHaveBeenCalledWith(false)
      expect(store.budgetNumber?.pool_enabled).toBe(false)
    })

    it('should handle toggle pool error', async () => {
      const store = useBudgetStore()
      const errorMessage = 'Failed to toggle pool'

      vi.mocked(budgetApi.togglePool).mockRejectedValue(
        createMockError(errorMessage)
      )

      await expect(store.togglePool(true)).rejects.toThrow()

      expect(store.error).toBe(errorMessage)
    })
  })

  describe('Pool Feature - addToPool', () => {
    it('should add money to pool and refresh number', async () => {
      const store = useBudgetStore()
      const updatedNumber = { ...mockBudgetNumberWithPool, pool_balance: 200 }

      vi.mocked(budgetApi.addToPool).mockResolvedValue(
        createMockResponse({ pool_balance: 200 })
      )
      vi.mocked(budgetApi.getNumber).mockResolvedValue(
        createMockResponse(updatedNumber)
      )

      await store.addToPool(50)

      expect(budgetApi.addToPool).toHaveBeenCalledWith(50)
      expect(budgetApi.getNumber).toHaveBeenCalledTimes(1)
      expect(store.budgetNumber?.pool_balance).toBe(200)
      expect(store.error).toBeNull()
    })

    it('should handle add to pool error', async () => {
      const store = useBudgetStore()
      const errorMessage = 'Failed to add to pool'

      vi.mocked(budgetApi.addToPool).mockRejectedValue(
        createMockError(errorMessage)
      )

      await expect(store.addToPool(50)).rejects.toThrow()

      expect(store.error).toBe(errorMessage)
    })
  })

  describe('Pool Feature - pending contribution with budget number', () => {
    it('should show pending contribution in budget number', async () => {
      const store = useBudgetStore()
      vi.mocked(budgetApi.getNumber).mockResolvedValue(
        createMockResponse(mockBudgetNumberWithPool)
      )

      await store.fetchNumber()

      expect(store.budgetNumber?.pending_pool_contribution).toBe(45.50)
      expect(store.budgetNumber?.pool_balance).toBe(150)
      expect(store.budgetNumber?.pool_enabled).toBe(true)
    })

    it('should show no pending contribution when null', async () => {
      const store = useBudgetStore()
      const noPending = { ...mockBudgetNumberWithPool, pending_pool_contribution: null }
      vi.mocked(budgetApi.getNumber).mockResolvedValue(
        createMockResponse(noPending)
      )

      await store.fetchNumber()

      expect(store.budgetNumber?.pending_pool_contribution).toBeNull()
    })
  })

  describe('Error Handling', () => {
    it('should clear previous errors on new fetch', async () => {
      const store = useBudgetStore()
      store.error = 'Previous error'

      vi.mocked(budgetApi.getNumber).mockResolvedValue(
        createMockResponse(mockBudgetNumber)
      )

      await store.fetchNumber()

      expect(store.error).toBeNull()
    })

    it('should handle API errors without detail property', async () => {
      const store = useBudgetStore()
      const error: any = new Error('Network error')
      error.response = {}

      vi.mocked(budgetApi.getNumber).mockRejectedValue(error)

      await expect(store.fetchNumber()).rejects.toThrow()

      expect(store.error).toBe('Failed to fetch budget number')
    })
  })
})
