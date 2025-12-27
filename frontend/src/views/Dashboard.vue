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
            <v-card-title class="text-h6">Record Transaction</v-card-title>
            <v-card-text>
              <v-form @submit.prevent="recordSpending">
                <!-- Money In/Out Toggle -->
                <div class="mb-4">
                  <v-btn-toggle
                    v-model="transactionType"
                    color="primary"
                    mandatory
                    divided
                    class="w-100"
                  >
                    <v-btn value="out" style="flex: 1;">
                      <v-icon class="mr-1">mdi-minus-circle</v-icon>
                      Money Out
                    </v-btn>
                    <v-btn value="in" style="flex: 1;">
                      <v-icon class="mr-1">mdi-plus-circle</v-icon>
                      Money In
                    </v-btn>
                  </v-btn-toggle>
                </div>

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
                  :label="transactionType === 'out' ? 'What did you spend on?' : 'Source of income'"
                  variant="outlined"
                  class="mb-2"
                  :placeholder="transactionType === 'out' ? 'e.g., Groceries' : 'e.g., Freelance work'"
                />
                <v-btn
                  type="submit"
                  :color="transactionType === 'out' ? 'error' : 'success'"
                  block
                  :loading="budgetStore.loadingTransactions"
                >
                  <v-icon class="mr-1">{{ transactionType === 'out' ? 'mdi-minus' : 'mdi-plus' }}</v-icon>
                  {{ transactionType === 'out' ? 'Record Spending' : 'Add Money' }}
                </v-btn>
              </v-form>
            </v-card-text>
          </v-card>
        </v-col>

        <v-col cols="12" md="4">
          <v-card elevation="2" class="pa-4">
            <v-card-title class="text-h6">Budget Details</v-card-title>
            <v-card-text>
              <div class="mb-3">
                <strong>Mode:</strong> {{ budgetStore.budgetNumber.mode === 'paycheck' ? 'Paycheck' : 'Fixed Pool' }}
              </div>

              <!-- Paycheck Mode -->
              <template v-if="budgetStore.budgetNumber.mode === 'paycheck'">
                <div v-if="budgetStore.budgetNumber.total_income" class="mb-2">
                  <strong>Monthly Income:</strong> {{ budgetStore.budgetNumber.total_income.toFixed(2) }}
                </div>
                <div v-if="budgetStore.budgetNumber.total_expenses" class="mb-2">
                  <strong>Total Expenses:</strong> {{ budgetStore.budgetNumber.total_expenses.toFixed(2) }}
                </div>
                <div v-if="budgetStore.budgetNumber.remaining_money" class="mb-2">
                  <strong>Remaining:</strong> {{ budgetStore.budgetNumber.remaining_money.toFixed(2) }}
                </div>
              </template>

              <!-- Fixed Pool Mode - Show both calculations -->
              <template v-else>
                <v-divider class="my-3"></v-divider>
                <div class="text-caption text-medium-emphasis mb-2">Your Current Plan:</div>

                <div class="mb-2">
                  <strong>Daily Budget:</strong> {{ budgetStore.budgetNumber.the_number.toFixed(2) }}
                </div>
                <div v-if="budgetStore.budgetNumber.days_remaining" class="mb-2">
                  <strong>Lasts For:</strong> {{ Math.floor(budgetStore.budgetNumber.days_remaining) }} days
                  ({{ (budgetStore.budgetNumber.days_remaining / 30).toFixed(1) }} months)
                </div>

                <v-divider class="my-3"></v-divider>
                <div class="text-caption text-medium-emphasis mb-2">Alternative View:</div>

                <div v-if="budgetStore.budgetNumber.total_expenses" class="text-body-2 text-medium-emphasis">
                  If you spent {{ (budgetStore.budgetNumber.total_expenses / 30).toFixed(2) }}/day
                  (monthly expenses), it would last {{ Math.floor((budgetStore.budgetNumber.total_money || 0) / ((budgetStore.budgetNumber.total_expenses || 1) / 30)) }} days
                </div>
              </template>
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
import { ref, onMounted, computed, watch } from 'vue'
import { useBudgetStore } from '@/stores/budget'
import { useAuthStore } from '@/stores/auth'
import NumberDisplay from '@/components/NumberDisplay.vue'
import Onboarding from '@/components/Onboarding.vue'

const budgetStore = useBudgetStore()
const authStore = useAuthStore()

const spendingAmount = ref(0)
const spendingDescription = ref('')
const transactionType = ref<'in' | 'out'>('out')

const recentTransactions = computed(() =>
  budgetStore.transactions.slice(0, 5)
)

async function loadDashboard() {
  console.log('📊 loadDashboard called')
  console.log('🔑 Auth state:', {
    isAuthenticated: authStore.isAuthenticated,
    hasToken: !!authStore.token,
    hasUser: !!authStore.user
  })

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
    // Handle authentication errors
    if (e.response?.status === 401) {
      console.error('❌ Authentication failed - token may be invalid or expired')
      console.log('🔑 Checking stored auth...')
      const storedToken = localStorage.getItem('auth_token')
      const storedUser = localStorage.getItem('user')
      console.log('🔑 LocalStorage:', { hasToken: !!storedToken, hasUser: !!storedUser })

      // Try to re-authenticate
      await authStore.checkAuth()

      budgetStore.error = 'Please log in again to continue'
    }
    // If not configured, clear the error so onboarding shows
    else if (e.response?.status === 400 || e.response?.status === 500) {
      budgetStore.error = null
      console.log('⚠️ Cleared error to show onboarding')
    }
    console.error('❌ Failed to load dashboard:', e)
  }
}

async function recordSpending() {
  if (spendingAmount.value <= 0 || !spendingDescription.value) return

  try {
    if (transactionType.value === 'out') {
      // Regular spending transaction
      await budgetStore.recordTransaction({
        amount: spendingAmount.value,
        description: spendingDescription.value,
        category: 'expense'
      })
    } else {
      // Money In - record as positive amount with income category
      await budgetStore.recordTransaction({
        amount: spendingAmount.value,  // Positive amount
        description: spendingDescription.value,
        category: 'income'
      })
    }
    spendingAmount.value = 0
    spendingDescription.value = ''
  } catch (e) {
    console.error('Failed to record transaction:', e)
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

// Watch for authentication changes and reload dashboard when user logs in
watch(() => authStore.isAuthenticated, (isAuthenticated, wasAuthenticated) => {
  console.log('🔐 Auth state changed:', { isAuthenticated, wasAuthenticated })
  // If user just logged in (wasn't authenticated before, is now)
  if (isAuthenticated && !wasAuthenticated) {
    console.log('✅ User just logged in - reloading dashboard')
    loadDashboard()
  }
})
</script>

<style scoped>
.dashboard {
  max-width: 1400px;
  margin: 0 auto;
  padding: var(--spacing-md);
}

.hero-section {
  text-align: center;
  padding: var(--spacing-xl) var(--spacing-md) var(--spacing-lg);
  margin-bottom: var(--spacing-lg);
  background: linear-gradient(135deg,
    var(--color-sage-green) 0%,
    rgba(233, 245, 219, 0.7) 100%);
  border-radius: 16px;
  box-shadow: 0 4px 16px rgba(74, 95, 122, 0.08);
}

.hero-title {
  font-size: clamp(3rem, 6vw, 4.5rem);
  font-weight: 400;
  color: var(--color-soft-charcoal);
  margin-bottom: var(--spacing-sm);
  font-family: var(--font-display);
  letter-spacing: -0.02em;
}

.hero-subtitle {
  font-size: clamp(1.25rem, 3vw, 1.75rem);
  color: var(--color-text-secondary);
  font-family: var(--font-display);
  font-style: italic;
  font-weight: 400;
}

/* Card styling to match brand */
:deep(.v-card) {
  background-color: white;
  border: 1px solid rgba(233, 245, 219, 0.3);
  border-radius: 12px;
  transition: all var(--transition-base) var(--transition-ease);
}

:deep(.v-card:hover) {
  border-color: var(--color-sage-green);
  box-shadow: 0 8px 24px rgba(135, 152, 106, 0.12);
}

:deep(.v-card-title) {
  font-family: var(--font-display);
  color: var(--color-text-primary);
  font-weight: 400;
}

:deep(.v-btn) {
  font-family: var(--font-ui);
  font-weight: 600;
  text-transform: none;
  letter-spacing: 0.01em;
}

/* Primary button styling */
:deep(.v-btn--variant-elevated) {
  background-color: var(--color-sage-green) !important;
  color: var(--color-soft-charcoal) !important;
}

:deep(.v-btn--variant-elevated:hover) {
  background-color: #d4e8c4 !important;
}

/* Error/Success button colors */
:deep(.v-btn.bg-error) {
  background-color: var(--color-terracotta) !important;
  color: white !important;
}

:deep(.v-btn.bg-success) {
  background-color: var(--color-success) !important;
  color: white !important;
}
</style>
