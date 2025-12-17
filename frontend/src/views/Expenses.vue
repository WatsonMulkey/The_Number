<template>
  <div class="expenses">
    <h1 class="text-h3 mb-6">Manage Expenses</h1>

    <!-- Add Expense Card -->
    <v-card class="mb-6" elevation="2">
      <v-card-title>Add New Expense</v-card-title>
      <v-card-text>
        <v-form @submit.prevent="addExpense">
          <v-row>
            <v-col cols="12" md="4">
              <v-text-field
                v-model="newExpense.name"
                label="Expense Name"
                variant="outlined"
                required
              />
            </v-col>
            <v-col cols="12" md="4">
              <v-text-field
                v-model.number="newExpense.amount"
                type="number"
                label="Monthly Amount"
                prefix="$"
                variant="outlined"
                required
              />
            </v-col>
            <v-col cols="12" md="2">
              <v-checkbox
                v-model="newExpense.is_fixed"
                label="Fixed"
                density="comfortable"
              />
            </v-col>
            <v-col cols="12" md="2">
              <v-btn
                type="submit"
                color="primary"
                block
                height="56"
                :loading="budgetStore.loading"
              >
                Add
              </v-btn>
            </v-col>
          </v-row>
        </v-form>
      </v-card-text>
    </v-card>

    <!-- Expenses List -->
    <v-card elevation="2">
      <v-card-title>
        <div class="d-flex justify-space-between align-center">
          <span>Current Expenses</span>
          <div>
            <v-chip color="primary" class="mr-2">
              Total: ${{ totalExpenses.toFixed(2) }}/mo
            </v-chip>
          </div>
        </div>
      </v-card-title>
      <v-card-text>
        <v-data-table
          :headers="headers"
          :items="budgetStore.expenses"
          :loading="budgetStore.loading"
          items-per-page="10"
        >
          <template v-slot:item.amount="{ item }">
            ${{ item.amount.toFixed(2) }}
          </template>
          <template v-slot:item.is_fixed="{ item }">
            <v-chip
              :color="item.is_fixed ? 'success' : 'warning'"
              size="small"
            >
              {{ item.is_fixed ? 'Fixed' : 'Variable' }}
            </v-chip>
          </template>
          <template v-slot:item.actions="{ item }">
            <v-btn
              icon="mdi-delete"
              size="small"
              variant="text"
              color="error"
              @click="deleteExpense(item.id)"
            />
          </template>
        </v-data-table>
      </v-card-text>
    </v-card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useBudgetStore } from '@/stores/budget'

const budgetStore = useBudgetStore()

const newExpense = ref({
  name: '',
  amount: 0,
  is_fixed: true,
})

const headers = [
  { title: 'Name', key: 'name', sortable: true },
  { title: 'Amount', key: 'amount', sortable: true },
  { title: 'Type', key: 'is_fixed', sortable: true },
  { title: 'Actions', key: 'actions', sortable: false },
]

const totalExpenses = computed(() => {
  return budgetStore.expenses.reduce((sum, exp) => sum + exp.amount, 0)
})

async function addExpense() {
  if (!newExpense.value.name || newExpense.value.amount <= 0) return

  try {
    await budgetStore.addExpense({ ...newExpense.value })
    newExpense.value = {
      name: '',
      amount: 0,
      is_fixed: true,
    }
  } catch (e) {
    console.error('Failed to add expense:', e)
  }
}

async function deleteExpense(id: number) {
  if (!confirm('Are you sure you want to delete this expense?')) return

  try {
    await budgetStore.removeExpense(id)
  } catch (e) {
    console.error('Failed to delete expense:', e)
  }
}

onMounted(() => {
  budgetStore.fetchExpenses()
})
</script>

<style scoped>
.expenses {
  max-width: 1400px;
  margin: 0 auto;
  padding: 24px;
}
</style>
