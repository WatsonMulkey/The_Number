import { describe, it, expect, vi, beforeEach } from 'vitest'
import type { BudgetConfig, Expense, Transaction } from './api'

// Use vi.hoisted to ensure mock functions are defined before vi.mock runs
const mockFns = vi.hoisted(() => ({
  get: vi.fn(),
  post: vi.fn(),
  put: vi.fn(),
  delete: vi.fn(),
}))

// Mock axios.create to return our mock instance
vi.mock('axios', () => {
  return {
    default: {
      create: () => ({
        get: mockFns.get,
        post: mockFns.post,
        put: mockFns.put,
        delete: mockFns.delete,
        interceptors: {
          request: { use: vi.fn() },
          response: { use: vi.fn() },
        },
      }),
    },
  }
})

// Import after mocking
import { budgetApi } from './api'

describe('API Client', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('Budget Number API', () => {
    it('should get budget number', async () => {
      const mockData = {
        the_number: 100,
        mode: 'paycheck',
        total_income: 5000,
        total_expenses: 2000,
        remaining_money: 3000,
        days_remaining: 15,
        today_spending: 50,
        remaining_today: 50,
        is_over_budget: false,
      }

      mockFns.get.mockResolvedValueOnce({ data: mockData })
      const result = await budgetApi.getNumber()

      expect(mockFns.get).toHaveBeenCalledWith('/api/number')
      expect(result.data).toEqual(mockData)
    })
  })

  describe('Budget Configuration API', () => {
    it('should configure budget', async () => {
      const config: BudgetConfig = {
        mode: 'paycheck',
        monthly_income: 5000,
        days_until_paycheck: 15,
      }

      mockFns.post.mockResolvedValueOnce({ data: config })
      const result = await budgetApi.configureBudget(config)

      expect(mockFns.post).toHaveBeenCalledWith('/api/budget/configure', config)
      expect(result.data).toEqual(config)
    })

    it('should get budget config', async () => {
      const mockConfig = {
        mode: 'paycheck' as const,
        monthly_income: 5000,
        days_until_paycheck: 15,
        configured: true,
      }

      mockFns.get.mockResolvedValueOnce({ data: mockConfig })
      const result = await budgetApi.getBudgetConfig()

      expect(mockFns.get).toHaveBeenCalledWith('/api/budget/config')
      expect(result.data).toEqual(mockConfig)
    })
  })

  describe('Expenses API', () => {
    it('should get expenses', async () => {
      const mockExpenses: Expense[] = [
        {
          id: 1,
          name: 'Rent',
          amount: 1500,
          is_fixed: true,
          created_at: '2024-01-01T00:00:00',
          updated_at: '2024-01-01T00:00:00',
        },
      ]

      mockFns.get.mockResolvedValueOnce({ data: mockExpenses })
      const result = await budgetApi.getExpenses()

      expect(mockFns.get).toHaveBeenCalledWith('/api/expenses')
      expect(result.data).toEqual(mockExpenses)
    })

    it('should create expense', async () => {
      const newExpense = {
        name: 'Netflix',
        amount: 15,
        is_fixed: true,
      }

      const createdExpense: Expense = {
        ...newExpense,
        id: 1,
        created_at: '2024-01-01T00:00:00',
        updated_at: '2024-01-01T00:00:00',
      }

      mockFns.post.mockResolvedValueOnce({ data: createdExpense })
      const result = await budgetApi.createExpense(newExpense)

      expect(mockFns.post).toHaveBeenCalledWith('/api/expenses', newExpense)
      expect(result.data).toEqual(createdExpense)
    })

    it('should delete expense', async () => {
      const expenseId = 1

      mockFns.delete.mockResolvedValueOnce({ data: null })
      await budgetApi.deleteExpense(expenseId)

      expect(mockFns.delete).toHaveBeenCalledWith(`/api/expenses/${expenseId}`)
    })

    it('should import expenses', async () => {
      const file = new File(['content'], 'expenses.csv', { type: 'text/csv' })
      const replace = true

      mockFns.post.mockResolvedValueOnce({ data: { imported: 5 } })
      await budgetApi.importExpenses(file, replace)

      expect(mockFns.post).toHaveBeenCalledWith(
        `/api/expenses/import?replace=${replace}`,
        expect.any(FormData),
        { headers: { 'Content-Type': 'multipart/form-data' } }
      )
    })

    it('should export expenses as CSV', async () => {
      const mockBlob = new Blob(['data'], { type: 'text/csv' })

      mockFns.get.mockResolvedValueOnce({ data: mockBlob })
      const result = await budgetApi.exportExpenses('csv')

      expect(mockFns.get).toHaveBeenCalledWith('/api/expenses/export/csv', {
        responseType: 'blob',
      })
      expect(result.data).toEqual(mockBlob)
    })

    it('should export expenses as Excel', async () => {
      const mockBlob = new Blob(['data'], { type: 'application/vnd.ms-excel' })

      mockFns.get.mockResolvedValueOnce({ data: mockBlob })
      const result = await budgetApi.exportExpenses('excel')

      expect(mockFns.get).toHaveBeenCalledWith('/api/expenses/export/excel', {
        responseType: 'blob',
      })
      expect(result.data).toEqual(mockBlob)
    })
  })

  describe('Transactions API', () => {
    it('should get transactions with default limit', async () => {
      const mockTransactions: Transaction[] = [
        {
          id: 1,
          date: '2024-01-15T12:00:00',
          amount: 25.50,
          description: 'Lunch',
          category: 'Food',
          created_at: '2024-01-15T12:00:00',
        },
      ]

      mockFns.get.mockResolvedValueOnce({ data: mockTransactions })
      const result = await budgetApi.getTransactions()

      expect(mockFns.get).toHaveBeenCalledWith('/api/transactions', {
        params: { limit: undefined },
      })
      expect(result.data).toEqual(mockTransactions)
    })

    it('should get transactions with custom limit', async () => {
      const mockTransactions: Transaction[] = []

      mockFns.get.mockResolvedValueOnce({ data: mockTransactions })
      await budgetApi.getTransactions(50)

      expect(mockFns.get).toHaveBeenCalledWith('/api/transactions', {
        params: { limit: 50 },
      })
    })

    it('should create transaction', async () => {
      const newTransaction = {
        amount: 25.50,
        description: 'Coffee',
        category: 'Food',
      }

      const createdTransaction: Transaction = {
        ...newTransaction,
        id: 1,
        date: '2024-01-15T12:00:00',
        created_at: '2024-01-15T12:00:00',
      }

      mockFns.post.mockResolvedValueOnce({ data: createdTransaction })
      const result = await budgetApi.createTransaction(newTransaction)

      expect(mockFns.post).toHaveBeenCalledWith('/api/transactions', newTransaction)
      expect(result.data).toEqual(createdTransaction)
    })

    it('should delete transaction', async () => {
      const transactionId = 1

      mockFns.delete.mockResolvedValueOnce({ data: null })
      await budgetApi.deleteTransaction(transactionId)

      expect(mockFns.delete).toHaveBeenCalledWith(`/api/transactions/${transactionId}`)
    })
  })

  describe('Error Handling', () => {
    it('should handle network errors', async () => {
      mockFns.get.mockRejectedValueOnce(new Error('Network error'))

      await expect(budgetApi.getNumber()).rejects.toThrow('Network error')
    })

    it('should handle API errors with status codes', async () => {
      const error = {
        response: {
          status: 404,
          data: { detail: 'Not found' },
        },
      }

      mockFns.get.mockRejectedValueOnce(error)

      await expect(budgetApi.getNumber()).rejects.toEqual(error)
    })
  })
})
