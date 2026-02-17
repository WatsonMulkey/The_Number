import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { budgetApi, type BudgetNumber, type Expense, type ExpenseUpdate, type Transaction } from '@/services/api'
import { BudgetNumberSchema, ExpenseSchema, TransactionSchema, validateResponse } from '@/services/schemas'
import { z } from 'zod'

/**
 * Budget store - manages budget number, expenses, and transactions.
 * Uses optimistic updates for instant UI feedback with rollback on error.
 * Validates API responses with zod schemas.
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

  /** Check if badge API is available */
  function isBadgeSupported() {
    return 'setAppBadge' in navigator
  }

  /** Check if notification permission is needed for badges */
  function needsBadgePermission() {
    return isBadgeSupported() && 'Notification' in window && Notification.permission === 'default'
  }

  /** Request notification permission (required for iOS badges). Must be called from user gesture. */
  async function requestBadgePermission(): Promise<boolean> {
    if (!('Notification' in window)) return false
    try {
      const result = await Notification.requestPermission()
      if (result === 'granted') {
        await updateAppBadge()
        return true
      }
      return false
    } catch (e) {
      console.warn('Notification permission request failed:', e)
      return false
    }
  }

  /** Update PWA app badge with the current daily budget number */
  async function updateAppBadge() {
    if (!('setAppBadge' in navigator) || !budgetNumber.value) return
    if (localStorage.getItem('badge_enabled') === 'false') return

    try {
      const rounded = Math.round(budgetNumber.value.remaining_today ?? budgetNumber.value.the_number)
      if (rounded > 0) {
        await (navigator as any).setAppBadge(rounded)
      } else {
        await (navigator as any).clearAppBadge()
      }
    } catch (e) {
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
      budgetNumber.value = validateResponse(BudgetNumberSchema, response.data, 'BudgetNumber')
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
      expenses.value = validateResponse(z.array(ExpenseSchema), response.data, 'Expenses')
    } catch (e: any) {
      error.value = e.response?.data?.detail || 'Failed to fetch expenses'
      throw e
    } finally {
      loadingExpenses.value = false
    }
  }

  /** Add a new monthly expense with optimistic update */
  async function addExpense(expense: Omit<Expense, 'id' | 'created_at' | 'updated_at'>) {
    error.value = null

    // Optimistic: add a placeholder immediately
    const optimisticId = -(Date.now())
    const now = new Date().toISOString()
    const optimistic: Expense = {
      ...expense,
      id: optimisticId,
      created_at: now,
      updated_at: now,
    }
    expenses.value.unshift(optimistic)

    try {
      const response = await budgetApi.createExpense(expense)
      const validated = validateResponse(ExpenseSchema, response.data, 'Expense')
      // Replace optimistic entry with real server response
      const idx = expenses.value.findIndex(e => e.id === optimisticId)
      if (idx !== -1) {
        expenses.value[idx] = validated
      }
      // Still need to refetch number since it's server-calculated
      await fetchNumber()
    } catch (e: any) {
      // Rollback: remove the optimistic entry
      expenses.value = expenses.value.filter(e => e.id !== optimisticId)
      error.value = e.response?.data?.detail || 'Failed to add expense'
      throw e
    }
  }

  /** Remove a monthly expense with optimistic update */
  async function removeExpense(id: number) {
    error.value = null

    // Optimistic: remove immediately, save snapshot for rollback
    const snapshot = [...expenses.value]
    expenses.value = expenses.value.filter(e => e.id !== id)

    try {
      await budgetApi.deleteExpense(id)
      // Still need to refetch number since it's server-calculated
      await fetchNumber()
    } catch (e: any) {
      // Rollback
      expenses.value = snapshot
      error.value = e.response?.data?.detail || 'Failed to delete expense'
      throw e
    }
  }

  /** Update an existing expense with optimistic update */
  async function updateExpense(id: number, updates: ExpenseUpdate) {
    error.value = null

    // Optimistic: apply updates immediately, save snapshot for rollback
    const snapshot = [...expenses.value]
    const index = expenses.value.findIndex(e => e.id === id)
    if (index !== -1) {
      expenses.value[index] = { ...expenses.value[index], ...updates }
    }

    try {
      const response = await budgetApi.updateExpense(id, updates)
      const validated = validateResponse(ExpenseSchema, response.data, 'Expense')
      // Replace with actual server response
      const idx = expenses.value.findIndex(e => e.id === id)
      if (idx !== -1) {
        expenses.value[idx] = validated
      }
      // Still need to refetch number since it's server-calculated
      await fetchNumber()
    } catch (e: any) {
      // Rollback
      expenses.value = snapshot
      error.value = e.response?.data?.detail || 'Failed to update expense'
      throw e
    }
  }

  /** Fetch recent transactions */
  async function fetchTransactions(limit = 20) {
    loadingTransactions.value = true
    error.value = null
    try {
      const response = await budgetApi.getTransactions(limit)
      transactions.value = validateResponse(z.array(TransactionSchema), response.data, 'Transactions')
    } catch (e: any) {
      error.value = e.response?.data?.detail || 'Failed to fetch transactions'
      throw e
    } finally {
      loadingTransactions.value = false
    }
  }

  /** Record a new spending transaction with optimistic update */
  async function recordTransaction(transaction: Omit<Transaction, 'id' | 'date' | 'created_at'>) {
    error.value = null

    // Optimistic: add placeholder immediately
    const optimisticId = -(Date.now())
    const now = new Date().toISOString()
    const optimistic: Transaction = {
      ...transaction,
      id: optimisticId,
      date: now,
      created_at: now,
    }
    transactions.value.unshift(optimistic)

    try {
      const response = await budgetApi.createTransaction(transaction)
      const validated = validateResponse(TransactionSchema, response.data, 'Transaction')
      // Replace optimistic entry with real server response
      const idx = transactions.value.findIndex(t => t.id === optimisticId)
      if (idx !== -1) {
        transactions.value[idx] = validated
      }
      // Still need to refetch number since it's server-calculated
      await fetchNumber()
    } catch (e: any) {
      // Rollback: remove the optimistic entry
      transactions.value = transactions.value.filter(t => t.id !== optimisticId)
      error.value = e.response?.data?.detail || 'Failed to record transaction'
      throw e
    }
  }

  // Pool feature actions

  /** Accept pending pool contribution from payday rollover */
  async function acceptPoolContribution() {
    error.value = null
    try {
      await budgetApi.acceptPoolContribution()
      await fetchNumber()
    } catch (e: any) {
      error.value = e.response?.data?.detail || 'Failed to accept pool contribution'
      throw e
    }
  }

  /** Decline pending pool contribution */
  async function declinePoolContribution() {
    error.value = null
    try {
      await budgetApi.declinePoolContribution()
      await fetchNumber()
    } catch (e: any) {
      error.value = e.response?.data?.detail || 'Failed to decline pool contribution'
      throw e
    }
  }

  /** Toggle pool enabled/disabled for daily budget calculation */
  async function togglePool(enabled: boolean) {
    error.value = null
    try {
      await budgetApi.togglePool(enabled)
      await fetchNumber()
    } catch (e: any) {
      error.value = e.response?.data?.detail || 'Failed to toggle pool'
      throw e
    }
  }

  /** Manually add money to the pool */
  async function addToPool(amount: number) {
    error.value = null
    try {
      await budgetApi.addToPool(amount)
      await fetchNumber()
    } catch (e: any) {
      error.value = e.response?.data?.detail || 'Failed to add to pool'
      throw e
    }
  }

  /** Set pool balance to an exact value */
  async function setPoolBalance(balance: number) {
    error.value = null
    try {
      await budgetApi.setPoolBalance(balance)
      await fetchNumber()
    } catch (e: any) {
      error.value = e.response?.data?.detail || 'Failed to set pool balance'
      throw e
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
    isBadgeSupported,
    needsBadgePermission,
    requestBadgePermission,

    // Pool feature actions
    acceptPoolContribution,
    declinePoolContribution,
    togglePool,
    addToPool,
    setPoolBalance,
  }
})
