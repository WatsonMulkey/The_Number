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
        <div class="d-flex justify-space-between align-center">
          <span>Recent Transactions</span>
          <v-btn
            color="primary"
            @click="showAddDialog = true"
          >
            <v-icon start>mdi-plus</v-icon>
            Add Transaction
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
            {{ item.amount.toFixed(2) }}
          </template>
          <template v-slot:item.actions="{ item }">
            <v-btn
              icon="mdi-delete"
              size="small"
              variant="text"
              color="error"
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
          <v-form @submit.prevent="addTransaction">
            <v-text-field
              v-model.number="newTransaction.amount"
              type="number"
              label="Amount"
              variant="outlined"
              required
              class="mb-4"
            />
            <v-text-field
              v-model="newTransaction.description"
              label="Description"
              variant="outlined"
              required
              class="mb-4"
            />
            <v-text-field
              v-model="newTransaction.category"
              label="Category (optional)"
              variant="outlined"
              class="mb-4"
            />
            <div class="d-flex justify-end gap-2">
              <v-btn @click="showAddDialog = false">Cancel</v-btn>
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
import { budgetApi } from '@/services/api'
import { format } from 'date-fns'

const budgetStore = useBudgetStore()
const showAddDialog = ref(false)

const newTransaction = ref({
  amount: 0,
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
  const today = new Date().toISOString().split('T')[0]
  return budgetStore.transactions
    .filter(txn => txn.date.startsWith(today))
    .reduce((sum, txn) => sum + txn.amount, 0)
})

const allTimeTotal = computed(() => {
  return budgetStore.transactions.reduce((sum, txn) => sum + txn.amount, 0)
})

function formatDate(dateString: string) {
  return format(new Date(dateString), 'MMM d, yyyy h:mm a')
}

async function addTransaction() {
  if (newTransaction.value.amount <= 0 || !newTransaction.value.description) return

  try {
    const txn: any = {
      amount: newTransaction.value.amount,
      description: newTransaction.value.description,
    }
    if (newTransaction.value.category) {
      txn.category = newTransaction.value.category
    }

    await budgetStore.recordTransaction(txn)

    newTransaction.value = {
      amount: 0,
      description: '',
      category: '',
    }
    showAddDialog.value = false
  } catch (e) {
    console.error('Failed to add transaction:', e)
  }
}

async function deleteTransaction(id: number) {
  if (!confirm('Are you sure you want to delete this transaction?')) return

  try {
    await budgetApi.deleteTransaction(id)
    budgetStore.transactions = budgetStore.transactions.filter(txn => txn.id !== id)
  } catch (e) {
    console.error('Failed to delete transaction:', e)
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

.gap-2 {
  gap: 8px;
}
</style>
