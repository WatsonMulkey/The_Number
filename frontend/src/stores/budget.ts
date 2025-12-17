import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { budgetApi, type BudgetNumber, type Expense, type Transaction } from '@/services/api'

export const useBudgetStore = defineStore('budget', () => {
  // State
  const budgetNumber = ref<BudgetNumber | null>(null)
  const expenses = ref<Expense[]>([])
  const transactions = ref<Transaction[]>([])

  // RACE CONDITION FIX: Separate loading states for different operations
  // This prevents UI flickering and incorrect loading indicators when
  // multiple API calls happen concurrently (e.g., fetching number while recording transaction)
  const loadingNumber = ref(false)
  const loadingExpenses = ref(false)
  const loadingTransactions = ref(false)

  // Legacy loading computed property for backward compatibility
  // Returns true if ANY operation is in progress
  const loading = computed(() => loadingNumber.value || loadingExpenses.value || loadingTransactions.value)

  const error = ref<string | null>(null)

  // Computed
  const isConfigured = computed(() => budgetNumber.value !== null)
  const dailyLimit = computed(() => budgetNumber.value?.the_number ?? 0)
  const isOverBudget = computed(() => budgetNumber.value?.is_over_budget ?? false)

  // Actions
  async function fetchNumber() {
    loadingNumber.value = true
    error.value = null
    try {
      const response = await budgetApi.getNumber()
      budgetNumber.value = response.data
    } catch (e: any) {
      error.value = e.response?.data?.detail || 'Failed to fetch budget number'
      throw e
    } finally {
      loadingNumber.value = false
    }
  }

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

  async function addExpense(expense: Omit<Expense, 'id' | 'created_at' | 'updated_at'>) {
    loadingExpenses.value = true
    error.value = null
    try {
      await budgetApi.createExpense(expense)
      await fetchExpenses()
      await fetchNumber() // Refresh "The Number"
    } catch (e: any) {
      error.value = e.response?.data?.detail || 'Failed to add expense'
      throw e
    } finally {
      loadingExpenses.value = false
    }
  }

  async function removeExpense(id: number) {
    loadingExpenses.value = true
    error.value = null
    try {
      await budgetApi.deleteExpense(id)
      await fetchExpenses()
      await fetchNumber() // Refresh "The Number"
    } catch (e: any) {
      error.value = e.response?.data?.detail || 'Failed to delete expense'
      throw e
    } finally {
      loadingExpenses.value = false
    }
  }

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

  async function recordTransaction(transaction: Omit<Transaction, 'id' | 'date' | 'created_at'>) {
    loadingTransactions.value = true
    error.value = null
    try {
      await budgetApi.createTransaction(transaction)
      await fetchTransactions()
      await fetchNumber() // Refresh "The Number" to show updated spending
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
    removeExpense,
    fetchTransactions,
    recordTransaction,
  }
})
