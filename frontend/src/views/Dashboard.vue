<template>
  <div class="dashboard">
    <!-- Hero Section (only show during onboarding) -->
    <div v-if="!budgetStore.budgetNumber && !budgetStore.loadingNumber" class="hero-section">
      <h1 class="hero-title">The Number</h1>
      <p class="hero-subtitle">A different way to budget</p>
    </div>

    <!-- Error Alert (only show when not in onboarding) -->
    <v-alert
      v-if="budgetStore.error && budgetStore.budgetNumber"
      type="error"
      class="mb-4"
      closable
      @click:close="budgetStore.error = null"
    >
      {{ budgetStore.error }}
    </v-alert>

    <!-- Loading State -->
    <v-progress-circular
      v-if="budgetStore.loadingNumber && !budgetStore.budgetNumber"
      indeterminate
      color="primary"
      size="64"
      class="mx-auto d-block mt-16"
    />

    <!-- Not Configured State - Show Onboarding -->
    <Onboarding
      v-else-if="!budgetStore.budgetNumber"
      @complete="onOnboardingComplete"
    />

    <!-- Main Dashboard -->
    <div v-else>
      <!-- The Number Display -->
      <NumberDisplay
        :the-number="budgetStore.budgetNumber.the_number"
        :mode="budgetStore.budgetNumber.mode"
        :today-spending="budgetStore.budgetNumber.today_spending"
        :remaining-today="budgetStore.budgetNumber.remaining_today"
        :is-over-budget="budgetStore.budgetNumber.is_over_budget"
        :days-remaining="budgetStore.budgetNumber.days_remaining"
      />

      <!-- Quick Actions -->
      <v-row class="mt-8">
        <v-col cols="12" md="4">
          <v-card elevation="2" class="pa-4">
            <v-card-title class="text-h6">Record Spending</v-card-title>
            <v-card-text>
              <v-form @submit.prevent="recordSpending">
                <v-text-field
                  v-model.number="spendingAmount"
                  type="number"
                  label="Amount"
                  variant="outlined"
                  :rules="[v => v > 0 || 'Amount must be positive']"
                  class="mb-2"
                />
                <v-text-field
                  v-model="spendingDescription"
                  label="Description"
                  variant="outlined"
                  class="mb-2"
                />
                <v-btn
                  type="submit"
                  color="primary"
                  block
                  :loading="budgetStore.loadingTransactions"
                >
                  Record
                </v-btn>
              </v-form>
            </v-card-text>
          </v-card>
        </v-col>

        <v-col cols="12" md="4">
          <v-card elevation="2" class="pa-4">
            <v-card-title class="text-h6">Budget Summary</v-card-title>
            <v-card-text>
              <div class="mb-2">
                <strong>Mode:</strong> {{ budgetStore.budgetNumber.mode === 'paycheck' ? 'Paycheck' : 'Fixed Pool' }}
              </div>
              <div v-if="budgetStore.budgetNumber.total_income" class="mb-2">
                <strong>Monthly Income:</strong> {{ budgetStore.budgetNumber.total_income.toFixed(2) }}
              </div>
              <div class="mb-2">
                <strong>Total Expenses:</strong> {{ budgetStore.budgetNumber.total_expenses.toFixed(2) }}
              </div>
              <div v-if="budgetStore.budgetNumber.remaining_money" class="mb-2">
                <strong>Remaining:</strong> {{ budgetStore.budgetNumber.remaining_money.toFixed(2) }}
              </div>
            </v-card-text>
          </v-card>
        </v-col>

        <v-col cols="12" md="4">
          <v-card elevation="2" class="pa-4">
            <v-card-title class="text-h6">Recent Transactions</v-card-title>
            <v-card-text>
              <v-list density="compact">
                <v-list-item
                  v-for="txn in recentTransactions"
                  :key="txn.id"
                  :title="txn.description"
                  :subtitle="`$${txn.amount.toFixed(2)}`"
                >
                  <template v-slot:prepend>
                    <v-icon>mdi-receipt</v-icon>
                  </template>
                </v-list-item>
                <v-list-item v-if="recentTransactions.length === 0">
                  <v-list-item-title class="text-medium-emphasis">
                    No transactions yet
                  </v-list-item-title>
                </v-list-item>
              </v-list>
              <v-btn
                :to="{ name: 'transactions' }"
                variant="text"
                block
                class="mt-2"
              >
                View All
              </v-btn>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useBudgetStore } from '@/stores/budget'
import NumberDisplay from '@/components/NumberDisplay.vue'
import Onboarding from '@/components/Onboarding.vue'

const budgetStore = useBudgetStore()

const spendingAmount = ref(0)
const spendingDescription = ref('')

const recentTransactions = computed(() =>
  budgetStore.transactions.slice(0, 5)
)

async function loadDashboard() {
  console.log('📊 loadDashboard called')
  try {
    // Try to fetch the budget number
    console.log('📊 Fetching budget number...')
    await budgetStore.fetchNumber()
    console.log('📊 Budget number fetched:', budgetStore.budgetNumber)
    // Only fetch transactions if we have a configured budget
    if (budgetStore.budgetNumber) {
      console.log('📊 Fetching transactions...')
      await budgetStore.fetchTransactions(5)
      console.log('📊 Transactions fetched')
    } else {
      console.log('⚠️ No budget number - onboarding should show')
    }
  } catch (e: any) {
    // If not configured, clear the error so onboarding shows
    if (e.response?.status === 400 || e.response?.status === 500) {
      budgetStore.error = null
      console.log('⚠️ Cleared error to show onboarding')
    }
    console.error('❌ Failed to load dashboard:', e)
  }
}

async function recordSpending() {
  if (spendingAmount.value <= 0 || !spendingDescription.value) return

  try {
    await budgetStore.recordTransaction({
      amount: spendingAmount.value,
      description: spendingDescription.value,
    })
    spendingAmount.value = 0
    spendingDescription.value = ''
  } catch (e) {
    console.error('Failed to record spending:', e)
  }
}

async function onOnboardingComplete() {
  console.log('🎉 onOnboardingComplete called - reloading dashboard...')
  // Reload dashboard data after onboarding
  await loadDashboard()
  console.log('🎉 Dashboard reloaded after onboarding')
}

onMounted(() => {
  loadDashboard()
})
</script>

<style scoped>
.dashboard {
  max-width: 1400px;
  margin: 0 auto;
  padding: 24px;
}

.hero-section {
  text-align: center;
  padding: 60px 20px 40px;
  margin-bottom: 40px;
}

.hero-title {
  font-size: 4rem;
  font-weight: bold;
  color: white;
  text-shadow: 3px 3px 6px rgba(0, 0, 0, 0.4);
  margin-bottom: 16px;
  font-family: 'Scope One', serif;
}

.hero-subtitle {
  font-size: 2rem;
  color: rgba(255, 255, 255, 0.9);
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
  font-family: 'Scope One', serif;
  font-style: italic;
}
</style>
