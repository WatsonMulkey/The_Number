import { describe, it, expect, beforeEach, vi } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useBudgetStore } from './budget'
import { budgetApi } from '@/services/api'
import {
  createMockResponse,
  createMockError,
  mockBudgetNumber,
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
    getTransactions: vi.fn(),
    createTransaction: vi.fn(),
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

  describe('addExpense', () => {
    it('should add expense and refresh data', async () => {
      const store = useBudgetStore()
      const newExpense = { name: 'Netflix', amount: 15, is_fixed: true }

      vi.mocked(budgetApi.createExpense).mockResolvedValue(
        createMockResponse({ ...newExpense, id: 3, created_at: '', updated_at: '' })
      )
      vi.mocked(budgetApi.getExpenses).mockResolvedValue(
        createMockResponse(mockExpenses)
      )
      vi.mocked(budgetApi.getNumber).mockResolvedValue(
        createMockResponse(mockBudgetNumber)
      )

      await store.addExpense(newExpense)

      expect(budgetApi.createExpense).toHaveBeenCalledWith(newExpense)
      expect(budgetApi.getExpenses).toHaveBeenCalled()
      expect(budgetApi.getNumber).toHaveBeenCalled()
      expect(store.loading).toBe(false)
      expect(store.error).toBeNull()
    })

    it('should handle add expense error', async () => {
      const store = useBudgetStore()
      const newExpense = { name: 'Netflix', amount: 15, is_fixed: true }
      const errorMessage = 'Failed to add expense'

      vi.mocked(budgetApi.createExpense).mockRejectedValue(
        createMockError(errorMessage)
      )

      await expect(store.addExpense(newExpense)).rejects.toThrow()

      expect(store.error).toBe(errorMessage)
      expect(store.loading).toBe(false)
    })
  })

  describe('removeExpense', () => {
    it('should remove expense and refresh data', async () => {
      const store = useBudgetStore()
      const expenseId = 1

      vi.mocked(budgetApi.deleteExpense).mockResolvedValue(
        createMockResponse(null)
      )
      vi.mocked(budgetApi.getExpenses).mockResolvedValue(
        createMockResponse(mockExpenses)
      )
      vi.mocked(budgetApi.getNumber).mockResolvedValue(
        createMockResponse(mockBudgetNumber)
      )

      await store.removeExpense(expenseId)

      expect(budgetApi.deleteExpense).toHaveBeenCalledWith(expenseId)
      expect(budgetApi.getExpenses).toHaveBeenCalled()
      expect(budgetApi.getNumber).toHaveBeenCalled()
      expect(store.loading).toBe(false)
      expect(store.error).toBeNull()
    })

    it('should handle remove expense error', async () => {
      const store = useBudgetStore()
      const errorMessage = 'Failed to delete expense'

      vi.mocked(budgetApi.deleteExpense).mockRejectedValue(
        createMockError(errorMessage)
      )

      await expect(store.removeExpense(1)).rejects.toThrow()

      expect(store.error).toBe(errorMessage)
      expect(store.loading).toBe(false)
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

    it('should handle fetch transactions error', async () => {
      const store = useBudgetStore()
      const errorMessage = 'Failed to fetch transactions'
      vi.mocked(budgetApi.getTransactions).mockRejectedValue(
        createMockError(errorMessage)
      )

      await expect(store.fetchTransactions()).rejects.toThrow()

      expect(store.error).toBe(errorMessage)
      expect(store.loading).toBe(false)
    })
  })

  describe('recordTransaction', () => {
    it('should record transaction and refresh data', async () => {
      const store = useBudgetStore()
      const newTransaction = { amount: 25.50, description: 'Coffee' }

      vi.mocked(budgetApi.createTransaction).mockResolvedValue(
        createMockResponse({ ...newTransaction, id: 3, date: '', created_at: '' })
      )
      vi.mocked(budgetApi.getTransactions).mockResolvedValue(
        createMockResponse(mockTransactions)
      )
      vi.mocked(budgetApi.getNumber).mockResolvedValue(
        createMockResponse(mockBudgetNumber)
      )

      await store.recordTransaction(newTransaction)

      expect(budgetApi.createTransaction).toHaveBeenCalledWith(newTransaction)
      expect(budgetApi.getTransactions).toHaveBeenCalled()
      expect(budgetApi.getNumber).toHaveBeenCalled()
      expect(store.loading).toBe(false)
      expect(store.error).toBeNull()
    })

    it('should handle record transaction error', async () => {
      const store = useBudgetStore()
      const newTransaction = { amount: 25.50, description: 'Coffee' }
      const errorMessage = 'Failed to record transaction'

      vi.mocked(budgetApi.createTransaction).mockRejectedValue(
        createMockError(errorMessage)
      )

      await expect(store.recordTransaction(newTransaction)).rejects.toThrow()

      expect(store.error).toBe(errorMessage)
      expect(store.loading).toBe(false)
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
