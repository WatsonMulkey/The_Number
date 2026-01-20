<template>
  <div class="expenses">
    <h1 class="text-h3 mb-6">Manage Expenses</h1>

    <!-- Add Expense Card -->
    <v-card class="mb-6" elevation="2">
      <v-card-title>Add New Expense</v-card-title>
      <v-card-text>
        <v-form ref="expenseForm" @submit.prevent="addExpense">
          <v-row>
            <v-col cols="12" md="4">
              <v-text-field
                v-model="newExpense.name"
                label="Expense Name"
                variant="outlined"
                :rules="[rules.required, rules.maxLength(100)]"
                counter="100"
                required
              />
            </v-col>
            <v-col cols="12" md="4">
              <v-text-field
                v-model.number="newExpense.amount"
                type="number"
                label="Monthly Amount"
                variant="outlined"
                :rules="[rules.positive]"
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
                :loading="budgetStore.loadingExpenses"
              >
                Add
              </v-btn>
            </v-col>
          </v-row>
        </v-form>
      </v-card-text>
    </v-card>

    <!-- Expenses List with Inline Editing -->
    <v-card elevation="2">
      <v-card-title>
        <div class="d-flex justify-space-between align-center">
          <span>Current Expenses</span>
          <div>
            <v-chip color="primary" class="mr-2">
              Total: {{ totalExpenses.toFixed(2) }}/mo
            </v-chip>
          </div>
        </div>
      </v-card-title>
      <v-card-text>
        <v-data-table
          :headers="headers"
          :items="budgetStore.expenses"
          :loading="budgetStore.loadingExpenses"
          items-per-page="10"
        >
          <!-- Editable Name Column -->
          <template v-slot:item.name="{ item }">
            <div
              v-if="editingId !== item.id || editingField !== 'name'"
              class="editable-cell"
              @click="startEdit(item.id, 'name', item.name)"
            >
              <span>{{ item.name }}</span>
              <v-icon size="small" class="edit-icon">mdi-pencil</v-icon>
            </div>
            <v-text-field
              v-else
              v-model="editValue"
              variant="outlined"
              density="compact"
              hide-details
              autofocus
              :rules="[rules.required, rules.maxLength(100)]"
              @blur="saveEdit(item.id, 'name')"
              @keyup.enter="saveEdit(item.id, 'name')"
              @keyup.escape="cancelEdit"
              class="inline-edit-field"
            />
          </template>

          <!-- Editable Amount Column -->
          <template v-slot:item.amount="{ item }">
            <div
              v-if="editingId !== item.id || editingField !== 'amount'"
              class="editable-cell"
              @click="startEdit(item.id, 'amount', item.amount)"
            >
              <span>${{ item.amount.toFixed(2) }}</span>
              <v-icon size="small" class="edit-icon">mdi-pencil</v-icon>
            </div>
            <v-text-field
              v-else
              v-model.number="editValue"
              type="number"
              variant="outlined"
              density="compact"
              hide-details
              autofocus
              step="0.01"
              min="0.01"
              @blur="saveEdit(item.id, 'amount')"
              @keyup.enter="saveEdit(item.id, 'amount')"
              @keyup.escape="cancelEdit"
              class="inline-edit-field"
            />
          </template>

          <!-- Editable Type Column (Toggle) -->
          <template v-slot:item.is_fixed="{ item }">
            <v-chip
              :color="item.is_fixed ? 'success' : 'warning'"
              size="small"
              class="editable-chip"
              @click="toggleType(item)"
            >
              {{ item.is_fixed ? 'Fixed' : 'Variable' }}
              <v-icon size="x-small" class="ml-1">mdi-swap-horizontal</v-icon>
            </v-chip>
          </template>

          <!-- Actions Column -->
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

    <!-- Save Indicator Snackbar -->
    <v-snackbar v-model="showSaveIndicator" :timeout="1500" color="success">
      Expense updated
    </v-snackbar>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useBudgetStore } from '@/stores/budget'
import { useValidation } from '@/composables/useValidation'

const budgetStore = useBudgetStore()
const { rules } = useValidation()

const expenseForm = ref()
const newExpense = ref({
  name: '',
  amount: 0,
  is_fixed: true,
})

// Inline editing state
const editingId = ref<number | null>(null)
const editingField = ref<'name' | 'amount' | null>(null)
const editValue = ref<string | number>('')
const originalValue = ref<string | number>('')
const showSaveIndicator = ref(false)

const headers = [
  { title: 'Name', key: 'name', sortable: true },
  { title: 'Amount', key: 'amount', sortable: true },
  { title: 'Type', key: 'is_fixed', sortable: true },
  { title: 'Actions', key: 'actions', sortable: false },
]

const totalExpenses = computed(() => {
  return budgetStore.expenses.reduce((sum, exp) => sum + exp.amount, 0)
})

function startEdit(id: number, field: 'name' | 'amount', value: string | number) {
  editingId.value = id
  editingField.value = field
  editValue.value = value
  originalValue.value = value
}

function cancelEdit() {
  editingId.value = null
  editingField.value = null
  editValue.value = ''
}

async function saveEdit(id: number, field: 'name' | 'amount') {
  // Skip if value unchanged
  if (editValue.value === originalValue.value) {
    cancelEdit()
    return
  }

  // Validate
  if (field === 'name' && (!editValue.value || String(editValue.value).trim() === '')) {
    cancelEdit()
    return
  }
  if (field === 'amount' && (typeof editValue.value !== 'number' || editValue.value <= 0)) {
    cancelEdit()
    return
  }

  try {
    const updates = { [field]: editValue.value }
    await budgetStore.updateExpense(id, updates)
    showSaveIndicator.value = true
  } catch (e) {
    console.error('Failed to update expense:', e)
  } finally {
    cancelEdit()
  }
}

async function toggleType(item: { id: number; is_fixed: boolean }) {
  try {
    await budgetStore.updateExpense(item.id, { is_fixed: !item.is_fixed })
    showSaveIndicator.value = true
  } catch (e) {
    console.error('Failed to toggle expense type:', e)
  }
}

async function addExpense() {
  // Validate form before submitting
  const { valid } = await expenseForm.value.validate()
  if (!valid) return

  try {
    await budgetStore.addExpense({ ...newExpense.value })

    // Reset form and clear validation
    newExpense.value = {
      name: '',
      amount: 0,
      is_fixed: true,
    }
    expenseForm.value.resetValidation()
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

/* Inline editing styles */
.editable-cell {
  cursor: pointer;
  padding: 8px 4px;
  border-radius: 4px;
  display: flex;
  align-items: center;
  min-height: 44px; /* PWA touch target */
  transition: background-color 0.2s;
}

.editable-cell:hover {
  background-color: rgba(var(--v-theme-primary), 0.08);
}

.editable-cell .edit-icon {
  opacity: 0;
  margin-left: 8px;
  transition: opacity 0.2s;
}

.editable-cell:hover .edit-icon {
  opacity: 0.6;
}

.inline-edit-field {
  max-width: 200px;
}

.editable-chip {
  cursor: pointer;
  min-height: 32px;
}

.editable-chip:hover {
  opacity: 0.85;
}

/* Mobile optimizations */
@media (max-width: 600px) {
  .expenses {
    padding: 16px;
  }

  .inline-edit-field {
    max-width: 100%;
  }

  .editable-cell .edit-icon {
    opacity: 0.4; /* Always visible on mobile */
  }
}
</style>
