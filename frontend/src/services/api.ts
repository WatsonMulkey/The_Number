import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json',
  },
})

// Add request interceptor to include auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('auth_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Add response interceptor to handle auth errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token is invalid or expired, redirect to login
      localStorage.removeItem('auth_token')
      localStorage.removeItem('user')
      window.location.href = '/#/login' // Or use router if available
    }
    return Promise.reject(error)
  }
)

// Types
export interface BudgetNumber {
  the_number: number
  mode: string
  total_income?: number
  total_expenses: number
  remaining_money?: number
  days_remaining?: number
  total_money?: number
  today_spending: number
  remaining_today: number
  is_over_budget: boolean
}

export interface Expense {
  id: number
  name: string
  amount: number
  is_fixed: boolean
  created_at: string
  updated_at: string
}

export interface Transaction {
  id: number
  date: string
  amount: number
  description: string
  category?: string
  created_at: string
}

export interface BudgetConfig {
  mode: 'paycheck' | 'fixed_pool'
  monthly_income?: number
  days_until_paycheck?: number
  total_money?: number
  target_end_date?: string
  daily_spending_limit?: number
}

// API endpoints
export const budgetApi = {
  // Get "The Number"
  getNumber: () => api.get<BudgetNumber>('/api/number'),

  // Configure budget
  configureBudget: (config: BudgetConfig) => api.post('/api/budget/configure', config),
  getBudgetConfig: () => api.get<BudgetConfig & { configured: boolean }>('/api/budget/config'),

  // Expenses
  getExpenses: () => api.get<Expense[]>('/api/expenses'),
  createExpense: (expense: Omit<Expense, 'id' | 'created_at' | 'updated_at'>) =>
    api.post<Expense>('/api/expenses', expense),
  deleteExpense: (id: number) => api.delete(`/api/expenses/${id}`),
  importExpenses: (file: File, replace: boolean) => {
    const formData = new FormData()
    formData.append('file', file)
    return api.post(`/api/expenses/import?replace=${replace}`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
  },
  exportExpenses: (format: 'csv' | 'excel') =>
    api.get(`/api/expenses/export/${format}`, { responseType: 'blob' }),

  // Transactions
  getTransactions: (limit?: number) =>
    api.get<Transaction[]>('/api/transactions', { params: { limit } }),
  createTransaction: (transaction: Omit<Transaction, 'id' | 'date' | 'created_at'>) =>
    api.post<Transaction>('/api/transactions', transaction),
  deleteTransaction: (id: number) => api.delete(`/api/transactions/${id}`),
}

// Password reset types
export interface ForgotPasswordRequest {
  username: string
}

export interface ForgotPasswordResponse {
  reset_token: string
  message: string
  expires_in: number
}

export interface ResetPasswordRequest {
  reset_token: string
  new_password: string
}

export interface ResetPasswordResponse {
  message: string
}

// Password reset API
export const authApi = {
  forgotPassword: (data: ForgotPasswordRequest) =>
    api.post<ForgotPasswordResponse>('/api/auth/forgot-password', data),

  resetPassword: (data: ResetPasswordRequest) =>
    api.post<ResetPasswordResponse>('/api/auth/reset-password', data),
}

export default api
