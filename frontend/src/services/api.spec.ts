import { describe, it, expect, beforeEach, vi, afterEach } from 'vitest'
import axios from 'axios'
import { budgetApi } from './api'
import type { BudgetConfig, Expense, Transaction } from './api'

// Mock axios
vi.mock('axios')

describe('API Client', () => {
  const mockedAxios = axios as any

  beforeEach(() => {
    mockedAxios.create.mockReturnValue({
      get: vi.fn(),
      post: vi.fn(),
      delete: vi.fn(),
    })
  })

  afterEach(() => {
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

      const mockGet = vi.fn().mockResolvedValue({ data: mockData })
      mockedAxios.create.mockReturnValue({ get: mockGet })

      // Re-import to get fresh instance
      const { budgetApi: freshApi } = await import('./api')
      const result = await freshApi.getNumber()

      expect(mockGet).toHaveBeenCalledWith('/api/number')
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

      const mockPost = vi.fn().mockResolvedValue({ data: config })
      mockedAxios.create.mockReturnValue({ post: mockPost })

      const { budgetApi: freshApi } = await import('./api')
      const result = await freshApi.configureBudget(config)

      expect(mockPost).toHaveBeenCalledWith('/api/budget/configure', config)
      expect(result.data).toEqual(config)
    })

    it('should get budget config', async () => {
      const mockConfig = {
        mode: 'paycheck' as const,
        monthly_income: 5000,
        days_until_paycheck: 15,
        configured: true,
      }

      const mockGet = vi.fn().mockResolvedValue({ data: mockConfig })
      mockedAxios.create.mockReturnValue({ get: mockGet })

      const { budgetApi: freshApi } = await import('./api')
      const result = await freshApi.getBudgetConfig()

      expect(mockGet).toHaveBeenCalledWith('/api/budget/config')
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

      const mockGet = vi.fn().mockResolvedValue({ data: mockExpenses })
      mockedAxios.create.mockReturnValue({ get: mockGet })

      const { budgetApi: freshApi } = await import('./api')
      const result = await freshApi.getExpenses()

      expect(mockGet).toHaveBeenCalledWith('/api/expenses')
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

      const mockPost = vi.fn().mockResolvedValue({ data: createdExpense })
      mockedAxios.create.mockReturnValue({ post: mockPost })

      const { budgetApi: freshApi } = await import('./api')
      const result = await freshApi.createExpense(newExpense)

      expect(mockPost).toHaveBeenCalledWith('/api/expenses', newExpense)
      expect(result.data).toEqual(createdExpense)
    })

    it('should delete expense', async () => {
      const expenseId = 1

      const mockDelete = vi.fn().mockResolvedValue({ data: null })
      mockedAxios.create.mockReturnValue({ delete: mockDelete })

      const { budgetApi: freshApi } = await import('./api')
      await freshApi.deleteExpense(expenseId)

      expect(mockDelete).toHaveBeenCalledWith(`/api/expenses/${expenseId}`)
    })

    it('should import expenses', async () => {
      const file = new File(['content'], 'expenses.csv', { type: 'text/csv' })
      const replace = true

      const mockPost = vi.fn().mockResolvedValue({ data: { imported: 5 } })
      mockedAxios.create.mockReturnValue({ post: mockPost })

      const { budgetApi: freshApi } = await import('./api')
      await freshApi.importExpenses(file, replace)

      expect(mockPost).toHaveBeenCalledWith(
        `/api/expenses/import?replace=${replace}`,
        expect.any(FormData),
        { headers: { 'Content-Type': 'multipart/form-data' } }
      )
    })

    it('should export expenses as CSV', async () => {
      const mockBlob = new Blob(['data'], { type: 'text/csv' })

      const mockGet = vi.fn().mockResolvedValue({ data: mockBlob })
      mockedAxios.create.mockReturnValue({ get: mockGet })

      const { budgetApi: freshApi } = await import('./api')
      const result = await freshApi.exportExpenses('csv')

      expect(mockGet).toHaveBeenCalledWith('/api/expenses/export/csv', {
        responseType: 'blob',
      })
      expect(result.data).toEqual(mockBlob)
    })

    it('should export expenses as Excel', async () => {
      const mockBlob = new Blob(['data'], { type: 'application/vnd.ms-excel' })

      const mockGet = vi.fn().mockResolvedValue({ data: mockBlob })
      mockedAxios.create.mockReturnValue({ get: mockGet })

      const { budgetApi: freshApi } = await import('./api')
      const result = await freshApi.exportExpenses('excel')

      expect(mockGet).toHaveBeenCalledWith('/api/expenses/export/excel', {
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

      const mockGet = vi.fn().mockResolvedValue({ data: mockTransactions })
      mockedAxios.create.mockReturnValue({ get: mockGet })

      const { budgetApi: freshApi } = await import('./api')
      const result = await freshApi.getTransactions()

      expect(mockGet).toHaveBeenCalledWith('/api/transactions', {
        params: { limit: undefined },
      })
      expect(result.data).toEqual(mockTransactions)
    })

    it('should get transactions with custom limit', async () => {
      const mockTransactions: Transaction[] = []

      const mockGet = vi.fn().mockResolvedValue({ data: mockTransactions })
      mockedAxios.create.mockReturnValue({ get: mockGet })

      const { budgetApi: freshApi } = await import('./api')
      await freshApi.getTransactions(50)

      expect(mockGet).toHaveBeenCalledWith('/api/transactions', {
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

      const mockPost = vi.fn().mockResolvedValue({ data: createdTransaction })
      mockedAxios.create.mockReturnValue({ post: mockPost })

      const { budgetApi: freshApi } = await import('./api')
      const result = await freshApi.createTransaction(newTransaction)

      expect(mockPost).toHaveBeenCalledWith('/api/transactions', newTransaction)
      expect(result.data).toEqual(createdTransaction)
    })

    it('should delete transaction', async () => {
      const transactionId = 1

      const mockDelete = vi.fn().mockResolvedValue({ data: null })
      mockedAxios.create.mockReturnValue({ delete: mockDelete })

      const { budgetApi: freshApi } = await import('./api')
      await freshApi.deleteTransaction(transactionId)

      expect(mockDelete).toHaveBeenCalledWith(`/api/transactions/${transactionId}`)
    })
  })

  describe('Error Handling', () => {
    it('should handle network errors', async () => {
      const mockGet = vi.fn().mockRejectedValue(new Error('Network error'))
      mockedAxios.create.mockReturnValue({ get: mockGet })

      const { budgetApi: freshApi } = await import('./api')

      await expect(freshApi.getNumber()).rejects.toThrow('Network error')
    })

    it('should handle API errors with status codes', async () => {
      const error = {
        response: {
          status: 404,
          data: { detail: 'Not found' },
        },
      }

      const mockGet = vi.fn().mockRejectedValue(error)
      mockedAxios.create.mockReturnValue({ get: mockGet })

      const { budgetApi: freshApi } = await import('./api')

      await expect(freshApi.getNumber()).rejects.toEqual(error)
    })
  })
})
