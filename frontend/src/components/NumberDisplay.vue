<template>
  <v-card
    class="number-display text-center pa-8"
    elevation="0"
    color="transparent"
  >
    <div class="number-container">
      <h2 class="display-text mb-4">Your Number is...</h2>

      <div
        class="the-number"
        :class="{ 'over-budget': isOverBudget }"
      >
        {{ formattedNumber }}
      </div>

      <div class="subtitle-text mt-4">
        {{ subtitle }}
      </div>

      <!-- Today's spending indicator -->
      <v-card
        v-if="todaySpending && todaySpending > 0"
        class="mt-6 pa-4"
        elevation="2"
        color="surface"
      >
        <div class="text-body-1">Today's Spending: {{ todaySpending.toFixed(2) }}</div>
        <div class="text-body-2 text-medium-emphasis">
          Remaining: {{ remainingToday?.toFixed(2) }}
        </div>
        <v-progress-linear
          :model-value="spendingPercentage"
          :color="isOverBudget ? 'error' : 'success'"
          height="8"
          rounded
          class="mt-2"
        />
      </v-card>

      <!-- Overspend impact warning -->
      <v-alert
        v-if="isOverBudget && adjustedDailyBudget"
        type="warning"
        density="comfortable"
        variant="tonal"
        class="mt-4 overspend-alert"
        role="status"
        aria-live="polite"
      >
        <template #prepend>
          <v-icon aria-hidden="true">mdi-alert-circle-outline</v-icon>
        </template>

        <div>
          <div class="font-weight-medium">
            Your new daily budget is ${{ adjustedDailyBudget.toFixed(2) }}
          </div>
          <div class="text-body-2 text-medium-emphasis mt-1">
            (down ${{ budgetDelta.toFixed(2) }} from ${{ originalDailyBudget?.toFixed(2) }})
          </div>
        </div>
      </v-alert>
    </div>
  </v-card>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  theNumber: number
  mode: string
  todaySpending?: number
  remainingToday?: number
  isOverBudget?: boolean
  daysRemaining?: number
  adjustedDailyBudget?: number
  originalDailyBudget?: number
}>()

const formattedNumber = computed(() => {
  return props.theNumber.toFixed(2)
})

const subtitle = computed(() => {
  if (props.mode === 'paycheck') {
    const days = props.daysRemaining || 0
    return `per day for the next ${days.toFixed(0)} days`
  } else {
    return 'per day with current budget'
  }
})

const spendingPercentage = computed(() => {
  if (!props.todaySpending || !props.theNumber) return 0
  return Math.min((props.todaySpending / props.theNumber) * 100, 100)
})

const budgetDelta = computed(() => {
  if (!props.adjustedDailyBudget || !props.originalDailyBudget) return 0
  return props.originalDailyBudget - props.adjustedDailyBudget
})
</script>

<style scoped>
.number-display {
  max-width: 800px;
  margin: 0 auto;
  background: linear-gradient(135deg,
    var(--color-sage-green) 0%,
    rgba(233, 245, 219, 0.85) 100%);
  border-radius: 24px;
  padding: var(--spacing-xl) !important;
  box-shadow: 0 8px 32px rgba(135, 152, 106, 0.15);
  border: 2px solid rgba(255, 255, 255, 0.3);
}

.display-text {
  font-size: clamp(1.75rem, 4vw, 2.5rem);
  color: var(--color-text-secondary);
  font-weight: 600;
  letter-spacing: -0.01em;
}

.the-number {
  font-size: clamp(5rem, 12vw, 9.375rem);
  font-weight: 700;
  color: var(--color-soft-charcoal);
  line-height: 1;
  transition: color var(--transition-base) var(--transition-ease);
  letter-spacing: -0.03em;
}

.the-number.over-budget {
  color: var(--color-terracotta);
}

.subtitle-text {
  font-size: clamp(1rem, 2vw, 1.25rem);
  color: var(--color-text-secondary);
  font-weight: 500;
}

/* Today's spending card styling */
:deep(.v-card) {
  background-color: white;
  border: 1px solid rgba(233, 245, 219, 0.4);
  border-radius: 12px;
}

:deep(.v-progress-linear) {
  border-radius: 4px;
}

:deep(.v-progress-linear.bg-success) {
  background-color: rgba(135, 152, 106, 0.2) !important;
}

:deep(.v-progress-linear__determinate) {
  background-color: var(--color-success) !important;
}

/* Overspend warning alert */
.overspend-alert {
  border-radius: 12px;
  background-color: rgba(255, 193, 7, 0.12) !important;
  border: 2px solid rgba(255, 193, 7, 0.3);
  text-align: left;
}

.overspend-alert :deep(.v-icon) {
  color: #F57C00;
}

@media (max-width: 600px) {
  .overspend-alert .font-weight-medium {
    font-size: 0.875rem;
  }
}
</style>
