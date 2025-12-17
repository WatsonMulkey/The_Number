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
        v-if="todaySpending > 0"
        class="mt-6 pa-4"
        elevation="2"
        color="surface"
      >
        <div class="text-body-1">Today's Spending: {{ todaySpending.toFixed(2) }}</div>
        <div class="text-body-2 text-medium-emphasis">
          Remaining: {{ remainingToday.toFixed(2) }}
        </div>
        <v-progress-linear
          :model-value="spendingPercentage"
          :color="isOverBudget ? 'error' : 'success'"
          height="8"
          rounded
          class="mt-2"
        />
      </v-card>
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
</script>

<style scoped>
.number-display {
  max-width: 800px;
  margin: 0 auto;
}

.display-text {
  font-family: 'Scope One', serif;
  font-size: 2.5rem;
  color: white;
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
}

.the-number {
  font-family: 'Scope One', serif;
  font-size: 150px;
  font-weight: bold;
  color: white;
  text-shadow: 4px 4px 8px rgba(0, 0, 0, 0.5);
  line-height: 1;
  transition: color 0.3s ease;
}

.the-number.over-budget {
  color: #ff5252;
}

.subtitle-text {
  font-family: 'Scope One', serif;
  font-size: 1.5rem;
  color: white;
  text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.3);
}

@media (max-width: 960px) {
  .the-number {
    font-size: 100px;
  }

  .display-text {
    font-size: 2rem;
  }

  .subtitle-text {
    font-size: 1.2rem;
  }
}

@media (max-width: 600px) {
  .the-number {
    font-size: 80px;
  }

  .display-text {
    font-size: 1.5rem;
  }

  .subtitle-text {
    font-size: 1rem;
  }
}
</style>
