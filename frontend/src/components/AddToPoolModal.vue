<template>
  <v-dialog
    v-model="isOpen"
    max-width="400"
    role="dialog"
    aria-labelledby="add-pool-modal-title"
  >
    <v-card>
      <v-card-title
        id="add-pool-modal-title"
        class="text-h5 pa-4 text-center"
        style="background-color: #faf3dd;"
      >
        <v-icon size="32" color="primary" class="mr-2">mdi-piggy-bank</v-icon>
        Add to Pool
      </v-card-title>

      <v-card-text class="pa-6">
        <p class="text-body-2 text-medium-emphasis mb-4">
          Add money to your savings pool. When enabled, pool funds are factored into your daily budget.
        </p>

        <v-form ref="form" @submit.prevent="handleSubmit">
          <v-text-field
            v-model.number="amount"
            type="number"
            label="Amount"
            variant="outlined"
            prefix="$"
            :rules="amountRules"
            autofocus
            class="mb-2"
          />

          <v-alert
            v-if="error"
            type="error"
            variant="tonal"
            class="mb-3"
            closable
            @click:close="error = null"
          >
            {{ error }}
          </v-alert>

          <div class="d-flex gap-2 mt-4">
            <v-btn
              variant="text"
              @click="handleClose"
              :disabled="loading"
            >
              Cancel
            </v-btn>
            <v-spacer />
            <v-btn
              type="submit"
              color="primary"
              variant="elevated"
              :loading="loading"
            >
              Add to Pool
            </v-btn>
          </div>
        </v-form>
      </v-card-text>
    </v-card>
  </v-dialog>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { useBudgetStore } from '@/stores/budget'

const props = defineProps<{
  modelValue: boolean
}>()

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  'added': []
}>()

const budgetStore = useBudgetStore()

const isOpen = ref(props.modelValue)
const amount = ref<number | null>(null)
const loading = ref(false)
const error = ref<string | null>(null)
const form = ref()

const amountRules = [
  (v: number | null) => v !== null || 'Amount is required',
  (v: number | null) => (v !== null && v > 0) || 'Amount must be greater than 0',
  (v: number | null) => (v !== null && v <= 10000000) || 'Amount exceeds maximum',
]

// Sync with parent v-model
watch(() => props.modelValue, (newVal) => {
  isOpen.value = newVal
  if (newVal) {
    // Reset form when opened
    amount.value = null
    error.value = null
    form.value?.resetValidation()
  }
})

watch(isOpen, (newVal) => {
  emit('update:modelValue', newVal)
})

async function handleSubmit() {
  const { valid } = await form.value.validate()
  if (!valid || amount.value === null) return

  loading.value = true
  error.value = null

  try {
    await budgetStore.addToPool(amount.value)
    isOpen.value = false
    emit('added')
  } catch (e: any) {
    error.value = e.response?.data?.detail || 'Failed to add to pool'
  } finally {
    loading.value = false
  }
}

function handleClose() {
  if (!loading.value) {
    isOpen.value = false
  }
}
</script>
