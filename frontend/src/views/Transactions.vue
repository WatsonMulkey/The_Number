<template>
  <div class="transactions">
    <h1 class="text-h3 mb-6">Spending History</h1>

    <!-- Summary Cards -->
    <v-row class="mb-6">
      <v-col cols="12" md="4">
        <v-card elevation="2" class="pa-4 text-center">
          <div class="text-h4">${{ todayTotal.toFixed(2) }}</div>
          <div class="text-body-2 text-medium-emphasis">Today</div>
        </v-card>
      </v-col>
      <v-col cols="12" md="4">
        <v-card elevation="2" class="pa-4 text-center">
          <div class="text-h4">{{ budgetStore.transactions.length }}</div>
          <div class="text-body-2 text-medium-emphasis">Total Transactions</div>
        </v-card>
      </v-col>
      <v-col cols="12" md="4">
        <v-card elevation="2" class="pa-4 text-center">
          <div class="text-h4">${{ allTimeTotal.toFixed(2) }}</div>
          <div class="text-body-2 text-medium-emphasis">All Time</div>
        </v-card>
      </v-col>
    </v-row>

    <!-- Transactions Table -->
    <v-card elevation="2">
      <v-card-title>
        <div class="d-flex justify-space-between align-center w-100">
          <span>Recent Transactions</span>
          <v-btn
            color="primary"
            @click="showAddDialog = true"
            class="add-transaction-btn"
          >
            <v-icon start>mdi-plus</v-icon>
            <span class="d-none d-sm-inline">Add Transaction</span>
            <span class="d-sm-none">Add</span>
          </v-btn>
        </div>
      </v-card-title>
      <v-card-text>
        <v-data-table
          :headers="headers"
          :items="budgetStore.transactions"
          :loading="budgetStore.loadingTransactions"
          items-per-page="20"
        >
          <template v-slot:item.date="{ item }">
            {{ formatDate(item.date) }}
          </template>
          <template v-slot:item.amount="{ item }">
            <span :class="item.category === 'income' ? 'text-success' : 'text-error'">
              {{ item.category === 'income' ? '+' : '-' }}${{ item.amount.toFixed(2) }}
            </span>
          </template>
          <template v-slot:item.actions="{ item }">
            <v-btn
              icon="mdi-delete"
              size="small"
              variant="text"
              color="error"
              :aria-label="`Delete transaction: ${item.description}`"
              @click="deleteTransaction(item.id)"
            />
          </template>
        </v-data-table>
      </v-card-text>
    </v-card>

    <!-- Add Transaction Dialog -->
    <v-dialog v-model="showAddDialog" max-width="500">
      <v-card>
        <v-card-title>Record Spending</v-card-title>
        <v-card-text>
          <v-form ref="transactionForm" @submit.prevent="addTransaction">
            <v-text-field
              v-model.number="newTransaction.amount"
              type="number"
              label="Amount"
              variant="outlined"
              :rules="[rules.positive]"
              required
              class="mb-4"
            />
            <v-text-field
              v-model="newTransaction.description"
              label="Description"
              variant="outlined"
              :rules="[rules.required, rules.maxLength(200)]"
              counter="200"
              required
              class="mb-4"
            />
            <v-text-field
              v-model="newTransaction.category"
              label="Category (optional)"
              variant="outlined"
              :rules="[rules.maxLength(50)]"
              counter="50"
              class="mb-4"
            />
            <div class="d-flex justify-end gap-2">
              <v-btn @click="closeDialog">Cancel</v-btn>
              <v-btn
                type="submit"
                color="primary"
                :loading="budgetStore.loadingTransactions"
              >
                Add
              </v-btn>
            </div>
          </v-form>
        </v-card-text>
      </v-card>
    </v-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useBudgetStore } from '@/stores/budget'
import { budgetApi, type Transaction } from '@/services/api'
import { useValidation } from '@/composables/useValidation'
import { format } from 'date-fns'

const budgetStore = useBudgetStore()
const { rules } = useValidation()
const showAddDialog = ref(false)
const transactionForm = ref<{ validate: () => Promise<{ valid: boolean }> } | null>(null)

const newTransaction = ref({
  amount: null as number | null,
  description: '',
  category: '',
})

const headers = [
  { title: 'Date', key: 'date', sortable: true },
  { title: 'Description', key: 'description', sortable: true },
  { title: 'Category', key: 'category', sortable: true },
  { title: 'Amount', key: 'amount', sortable: true },
  { title: 'Actions', key: 'actions', sortable: false },
]

const todayTotal = computed(() => {
  const now = new Date()
  const today = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}-${String(now.getDate()).padStart(2, '0')}`
  return budgetStore.transactions
    .filter((txn: Transaction) => {
      // Convert stored UTC timestamp to local date for comparison
      const txnLocal = new Date(txn.date)
      const txnDate = `${txnLocal.getFullYear()}-${String(txnLocal.getMonth() + 1).padStart(2, '0')}-${String(txnLocal.getDate()).padStart(2, '0')}`
      return txnDate === today
    })
    .reduce((sum: number, txn: Transaction) => {
      // Income subtracts from spending, expenses add
      const amount = txn.category === 'income' ? -txn.amount : txn.amount
      return sum + amount
    }, 0)
})

const allTimeTotal = computed(() => {
  return budgetStore.transactions.reduce((sum: number, txn: Transaction) => {
    // Income subtracts from spending, expenses add
    const amount = txn.category === 'income' ? -txn.amount : txn.amount
    return sum + amount
  }, 0)
})

function formatDate(dateString: string) {
  return format(new Date(dateString), 'MMM d, yyyy h:mm a')
}

function closeDialog() {
  showAddDialog.value = false
  newTransaction.value = { amount: null, description: '', category: '' }
  transactionForm.value?.validate() // Reset validation state
}

async function addTransaction() {
  if (!transactionForm.value) return
  const { valid } = await transactionForm.value.validate()
  if (!valid) return

  try {
    const txn: { amount: number; description: string; category?: string } = {
      amount: newTransaction.value.amount!,
      description: newTransaction.value.description,
    }
    if (newTransaction.value.category) {
      txn.category = newTransaction.value.category
    }

    await budgetStore.recordTransaction(txn)
    closeDialog()
  } catch {
    // Error handled by store
  }
}

async function deleteTransaction(id: number) {
  if (!confirm('Are you sure you want to delete this transaction?')) return

  try {
    await budgetApi.deleteTransaction(id)
    budgetStore.transactions = budgetStore.transactions.filter((txn: Transaction) => txn.id !== id)
  } catch {
    // Error handled silently - user can retry
  }
}

onMounted(() => {
  budgetStore.fetchTransactions(50)
})
</script>

<style scoped>
.transactions {
  max-width: 1400px;
  margin: 0 auto;
  padding: 24px;
}

@media (max-width: 600px) {
  .transactions {
    padding: 16px;
  }
}

.gap-2 {
  gap: 8px;
}

/* Ensure button has proper touch target and doesn't shrink */
.add-transaction-btn {
  flex-shrink: 0;
  min-height: 44px;
}
</style>
