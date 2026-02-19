import axios from 'axios'

/**
 * Get the API base URL from environment variables.
 * In production, VITE_API_URL must be set - localhost fallback is for development only.
 */
function getApiBaseUrl(): string {
  const envUrl = import.meta.env.VITE_API_URL
  if (envUrl) {
    return envUrl
  }
  // Development fallback only - production must have VITE_API_URL configured
  if (import.meta.env.DEV) {
    return 'http://localhost:8000'
  }
  // Production without VITE_API_URL - use relative URL (same origin)
  return ''
}

const api = axios.create({
  baseURL: getApiBaseUrl(),
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
      // Only redirect if there was a token (i.e., user was previously authenticated)
      // This prevents redirect loops for unauthenticated users visiting the app
      const hadToken = localStorage.getItem('auth_token')
      localStorage.removeItem('auth_token')
      localStorage.removeItem('user')
      if (hadToken) {
        window.location.href = '/#/login'
      }
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
  adjusted_daily_budget?: number
  original_daily_budget?: number
  tomorrow_daily_budget?: number
  // Pool feature fields
  pool_balance: number
  pool_enabled: boolean
  pending_pool_contribution?: number | null
}

export interface Expense {
  id: number
  name: string
  amount: number
  is_fixed: boolean
  frequency: 'weekly' | 'monthly'
  created_at: string
  updated_at: string
}

export interface ExpenseUpdate {
  name?: string
  amount?: number
  is_fixed?: boolean
  frequency?: 'weekly' | 'monthly'
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
  days_until_paycheck?: number  // Deprecated - use next_payday_date
  next_payday_date?: string     // Preferred - date of next paycheck
  pay_frequency_days?: number   // 7 = weekly, 14 = biweekly, 30 = monthly
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
  updateExpense: (id: number, expense: ExpenseUpdate) =>
    api.put<Expense>(`/api/expenses/${id}`, expense),
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

  // Pool feature
  getPoolStatus: () => api.get<{ pool_balance: number; pool_enabled: boolean; pending_pool_contribution: number | null }>('/api/pool'),
  acceptPoolContribution: () => api.post<{ pool_balance: number }>('/api/pool/accept'),
  declinePoolContribution: () => api.post<{ status: string; amount_declined: number }>('/api/pool/decline'),
  togglePool: (enabled: boolean) => api.post<{ pool_balance: number }>('/api/pool/toggle', { enabled }),
  addToPool: (amount: number) => api.post<{ pool_balance: number }>('/api/pool/add', { amount }),
  setPoolBalance: (balance: number) => api.post<{ pool_balance: number }>('/api/pool/set', { balance }),
}

// Password reset types
// TODO: Implement password reset UI in AuthModal.vue to use these endpoints
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

/**
 * Password reset API endpoints.
 * Backend endpoints are implemented - UI needs to be added to AuthModal.vue.
 * @see AuthModal.vue - Add "Forgot Password" link and reset flow
 */
export const authApi = {
  /** Request a password reset token (sent to user's email if configured) */
  forgotPassword: (data: ForgotPasswordRequest) =>
    api.post<ForgotPasswordResponse>('/api/auth/forgot-password', data),

  /** Reset password using the token from forgotPassword */
  resetPassword: (data: ResetPasswordRequest) =>
    api.post<ResetPasswordResponse>('/api/auth/reset-password', data),
}

// Admin metrics types
export interface AdminMetrics {
  growth: {
    total_users: number
    signups_this_week: number
    signups_this_month: number
  }
  engagement: {
    dau: number
    wau: number
    mau: number
    avg_sessions_per_day: number
  }
  depth: {
    budget_configured_count: number
    budget_configured_pct: number
    paycheck_mode_count: number
    fixed_pool_mode_count: number
    pool_enabled_count: number
  }
  volume: {
    total_transactions: number
    total_expenses: number
  }
}

export interface AdminHealth {
  database: {
    path: string
    size_bytes: number
    size_mb: number
    row_counts: Record<string, number>
  }
  disk: {
    path: string
    total_bytes: number
    used_bytes: number
    free_bytes: number
    used_pct: number
  }
}

export interface TrendDataPoint {
  date: string
  value: number
}

export interface AdminTrends {
  daily_active_users: TrendDataPoint[]
  daily_signups: TrendDataPoint[]
  daily_transactions: TrendDataPoint[]
  comparisons: {
    dau: number
    signups: number
    transactions: number
  }
}

export const adminApi = {
  getMetrics: () => api.get<AdminMetrics>('/api/admin/metrics'),
  getHealth: () => api.get<AdminHealth>('/api/admin/health'),
  getTrends: () => api.get<AdminTrends>('/api/admin/trends'),
}

export default api
