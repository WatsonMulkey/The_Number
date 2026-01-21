import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { budgetApi, type BudgetNumber, type Expense, type ExpenseUpdate, type Transaction } from '@/services/api'

/**
 * Budget store - manages budget number, expenses, and transactions.
 * Provides granular loading states to prevent race conditions.
 */
export const useBudgetStore = defineStore('budget', () => {
  // State
  const budgetNumber = ref<BudgetNumber | null>(null)
  const expenses = ref<Expense[]>([])
  const transactions = ref<Transaction[]>([])

  /**
   * Granular loading states for different operations.
   * Prevents UI flickering when multiple API calls happen concurrently.
   */
  const loadingNumber = ref(false)
  const loadingExpenses = ref(false)
  const loadingTransactions = ref(false)

  /** Returns true if ANY operation is in progress (backward compatible) */
  const loading = computed(() => loadingNumber.value || loadingExpenses.value || loadingTransactions.value)

  const error = ref<string | null>(null)

  // Computed
  /** Whether the budget has been configured (completed onboarding) */
  const isConfigured = computed(() => budgetNumber.value !== null)
  /** The daily spending limit ("The Number") */
  const dailyLimit = computed(() => budgetNumber.value?.the_number ?? 0)
  /** Whether today's spending has exceeded the daily limit */
  const isOverBudget = computed(() => budgetNumber.value?.is_over_budget ?? false)

  // Actions

  /** Update PWA app badge with the current daily budget number */
  async function updateAppBadge() {
    if (!('setAppBadge' in navigator) || !budgetNumber.value) return

    try {
      const rounded = Math.round(budgetNumber.value.the_number)
      if (rounded > 0) {
        await (navigator as any).setAppBadge(rounded)
      } else {
        await (navigator as any).clearAppBadge()
      }
    } catch (e) {
      // Silently fail - not all browsers support this
      console.warn('Badge API failed:', e)
    }
  }

  /** Clear the PWA app badge (call on logout) */
  async function clearAppBadge() {
    if (!('clearAppBadge' in navigator)) return

    try {
      await (navigator as any).clearAppBadge()
    } catch (e) {
      console.warn('Badge API failed:', e)
    }
  }

  /** Fetch the current budget number ("The Number") from the API */
  async function fetchNumber() {
    loadingNumber.value = true
    error.value = null
    try {
      const response = await budgetApi.getNumber()
      budgetNumber.value = response.data
      // Update PWA badge with the new number
      await updateAppBadge()
    } catch (e: any) {
      error.value = e.response?.data?.detail || 'Failed to fetch budget number'
      throw e
    } finally {
      loadingNumber.value = false
    }
  }

  /** Fetch all monthly expenses */
  async function fetchExpenses() {
    loadingExpenses.value = true
    error.value = null
    try {
      const response = await budgetApi.getExpenses()
      expenses.value = response.data
    } catch (e: any) {
      error.value = e.response?.data?.detail || 'Failed to fetch expenses'
      throw e
    } finally {
      loadingExpenses.value = false
    }
  }

  /** Add a new monthly expense and refresh data */
  async function addExpense(expense: Omit<Expense, 'id' | 'created_at' | 'updated_at'>) {
    loadingExpenses.value = true
    error.value = null
    try {
      await budgetApi.createExpense(expense)
      // Fetch expenses and number in parallel since both need updating
      await Promise.all([fetchExpenses(), fetchNumber()])
    } catch (e: any) {
      error.value = e.response?.data?.detail || 'Failed to add expense'
      throw e
    } finally {
      loadingExpenses.value = false
    }
  }

  /** Remove a monthly expense and refresh data */
  async function removeExpense(id: number) {
    loadingExpenses.value = true
    error.value = null
    try {
      await budgetApi.deleteExpense(id)
      // Fetch expenses and number in parallel since both need updating
      await Promise.all([fetchExpenses(), fetchNumber()])
    } catch (e: any) {
      error.value = e.response?.data?.detail || 'Failed to delete expense'
      throw e
    } finally {
      loadingExpenses.value = false
    }
  }

  /** Update an existing expense and refresh data */
  async function updateExpense(id: number, updates: ExpenseUpdate) {
    loadingExpenses.value = true
    error.value = null
    try {
      await budgetApi.updateExpense(id, updates)
      // Fetch expenses and number in parallel since both need updating
      await Promise.all([fetchExpenses(), fetchNumber()])
    } catch (e: any) {
      error.value = e.response?.data?.detail || 'Failed to update expense'
      throw e
    } finally {
      loadingExpenses.value = false
    }
  }

  /** Fetch recent transactions */
  async function fetchTransactions(limit = 20) {
    loadingTransactions.value = true
    error.value = null
    try {
      const response = await budgetApi.getTransactions(limit)
      transactions.value = response.data
    } catch (e: any) {
      error.value = e.response?.data?.detail || 'Failed to fetch transactions'
      throw e
    } finally {
      loadingTransactions.value = false
    }
  }

  /** Record a new spending transaction and refresh data */
  async function recordTransaction(transaction: Omit<Transaction, 'id' | 'date' | 'created_at'>) {
    loadingTransactions.value = true
    error.value = null
    try {
      await budgetApi.createTransaction(transaction)
      // Fetch transactions and number in parallel since both need updating
      await Promise.all([fetchTransactions(), fetchNumber()])
    } catch (e: any) {
      error.value = e.response?.data?.detail || 'Failed to record transaction'
      throw e
    } finally {
      loadingTransactions.value = false
    }
  }

  return {
    // State
    budgetNumber,
    expenses,
    transactions,
    error,

    // Loading states (granular for race condition prevention)
    loadingNumber,
    loadingExpenses,
    loadingTransactions,
    loading, // Computed: true if any operation is loading (backward compatible)

    // Computed
    isConfigured,
    dailyLimit,
    isOverBudget,

    // Actions
    fetchNumber,
    fetchExpenses,
    addExpense,
    updateExpense,
    removeExpense,
    fetchTransactions,
    recordTransaction,
    clearAppBadge,
  }
})
