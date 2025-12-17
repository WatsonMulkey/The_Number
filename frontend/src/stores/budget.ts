import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { budgetApi, type BudgetNumber, type Expense, type Transaction } from '@/services/api'

export const useBudgetStore = defineStore('budget', () => {
  // State
  const budgetNumber = ref<BudgetNumber | null>(null)
  const expenses = ref<Expense[]>([])
  const transactions = ref<Transaction[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  // Computed
  const isConfigured = computed(() => budgetNumber.value !== null)
  const dailyLimit = computed(() => budgetNumber.value?.the_number ?? 0)
  const isOverBudget = computed(() => budgetNumber.value?.is_over_budget ?? false)

  // Actions
  async function fetchNumber() {
    loading.value = true
    error.value = null
    try {
      const response = await budgetApi.getNumber()
      budgetNumber.value = response.data
    } catch (e: any) {
      error.value = e.response?.data?.detail || 'Failed to fetch budget number'
      throw e
    } finally {
      loading.value = false
    }
  }

  async function fetchExpenses() {
    loading.value = true
    error.value = null
    try {
      const response = await budgetApi.getExpenses()
      expenses.value = response.data
    } catch (e: any) {
      error.value = e.response?.data?.detail || 'Failed to fetch expenses'
      throw e
    } finally {
      loading.value = false
    }
  }

  async function addExpense(expense: Omit<Expense, 'id' | 'created_at' | 'updated_at'>) {
    loading.value = true
    error.value = null
    try {
      await budgetApi.createExpense(expense)
      await fetchExpenses()
      await fetchNumber() // Refresh "The Number"
    } catch (e: any) {
      error.value = e.response?.data?.detail || 'Failed to add expense'
      throw e
    } finally {
      loading.value = false
    }
  }

  async function removeExpense(id: number) {
    loading.value = true
    error.value = null
    try {
      await budgetApi.deleteExpense(id)
      await fetchExpenses()
      await fetchNumber() // Refresh "The Number"
    } catch (e: any) {
      error.value = e.response?.data?.detail || 'Failed to delete expense'
      throw e
    } finally {
      loading.value = false
    }
  }

  async function fetchTransactions(limit = 20) {
    loading.value = true
    error.value = null
    try {
      const response = await budgetApi.getTransactions(limit)
      transactions.value = response.data
    } catch (e: any) {
      error.value = e.response?.data?.detail || 'Failed to fetch transactions'
      throw e
    } finally {
      loading.value = false
    }
  }

  async function recordTransaction(transaction: Omit<Transaction, 'id' | 'date' | 'created_at'>) {
    loading.value = true
    error.value = null
    try {
      await budgetApi.createTransaction(transaction)
      await fetchTransactions()
      await fetchNumber() // Refresh "The Number" to show updated spending
    } catch (e: any) {
      error.value = e.response?.data?.detail || 'Failed to record transaction'
      throw e
    } finally {
      loading.value = false
    }
  }

  return {
    // State
    budgetNumber,
    expenses,
    transactions,
    loading,
    error,

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
