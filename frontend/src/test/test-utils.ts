import { mount, VueWrapper } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { createRouter, createMemoryHistory, Router } from 'vue-router'
import { vi } from 'vitest'
import type { ComponentPublicInstance } from 'vue'

// Create a test router
export function createTestRouter(routes: any[] = []): Router {
  return createRouter({
    history: createMemoryHistory(),
    routes: routes.length ? routes : [
      { path: '/', name: 'dashboard', component: { template: '<div>Dashboard</div>' } },
      { path: '/expenses', name: 'expenses', component: { template: '<div>Expenses</div>' } },
      { path: '/transactions', name: 'transactions', component: { template: '<div>Transactions</div>' } },
      { path: '/settings', name: 'settings', component: { template: '<div>Settings</div>' } },
    ],
  })
}

// Create a fresh pinia instance for each test
export function createTestPinia() {
  const pinia = createPinia()
  setActivePinia(pinia)
  return pinia
}

// Mount helper with common setup
export function mountWithPlugins(
  component: any,
  options: any = {}
) {
  const pinia = createTestPinia()
  const router = createTestRouter()

  return mount(component, {
    global: {
      plugins: [pinia, router],
      ...options.global,
    },
    ...options,
  })
}

// Mock API response helper
export function createMockResponse<T>(data: T, status = 200) {
  return {
    data,
    status,
    statusText: 'OK',
    headers: {},
    config: {} as any,
  }
}

// Mock API error helper
export function createMockError(message: string, status = 500) {
  const error: any = new Error(message)
  error.response = {
    data: { detail: message },
    status,
    statusText: 'Error',
    headers: {},
    config: {} as any,
  }
  return error
}

// Wait for async updates
export async function flushPromises() {
  return new Promise((resolve) => setTimeout(resolve, 0))
}

// Mock budget number data
export const mockBudgetNumber = {
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

// Mock expense data
export const mockExpenses = [
  {
    id: 1,
    name: 'Rent',
    amount: 1500,
    is_fixed: true,
    created_at: '2024-01-01T00:00:00',
    updated_at: '2024-01-01T00:00:00',
  },
  {
    id: 2,
    name: 'Groceries',
    amount: 500,
    is_fixed: false,
    created_at: '2024-01-01T00:00:00',
    updated_at: '2024-01-01T00:00:00',
  },
]

// Mock transaction data
export const mockTransactions = [
  {
    id: 1,
    date: '2024-01-15T12:00:00',
    amount: 25.50,
    description: 'Lunch',
    category: 'Food',
    created_at: '2024-01-15T12:00:00',
  },
  {
    id: 2,
    date: '2024-01-15T18:00:00',
    amount: 50.00,
    description: 'Gas',
    category: 'Transportation',
    created_at: '2024-01-15T18:00:00',
  },
]

// Mock budget config
export const mockBudgetConfig = {
  mode: 'paycheck' as const,
  monthly_income: 5000,
  days_until_paycheck: 15,
  configured: true,
}
