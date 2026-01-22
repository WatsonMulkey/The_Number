<template>
  <div class="dashboard">
    <!-- Hero Section removed - Onboarding component has its own branded header -->

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
      <!-- Swipeable Content Area -->
      <v-window v-model="currentSlide" class="main-carousel mb-8" show-arrows continuous>
        <!-- Slide 1: The Number Display -->
        <v-window-item :value="0">
          <NumberDisplay
            :the-number="budgetStore.budgetNumber.the_number"
            :mode="budgetStore.budgetNumber.mode"
            :today-spending="budgetStore.budgetNumber.today_spending"
            :remaining-today="budgetStore.budgetNumber.remaining_today"
            :is-over-budget="budgetStore.budgetNumber.is_over_budget"
            :days-remaining="budgetStore.budgetNumber.days_remaining"
            :adjusted-daily-budget="budgetStore.budgetNumber.adjusted_daily_budget"
            :original-daily-budget="budgetStore.budgetNumber.original_daily_budget"
            :tomorrow-daily-budget="budgetStore.budgetNumber.tomorrow_daily_budget"
          />
        </v-window-item>

        <!-- Slide 2: Budget Details -->
        <v-window-item :value="1">
          <v-card elevation="2" class="budget-details-card pa-6">
            <v-card-title class="text-h5 mb-4">Budget Details</v-card-title>
            <v-card-text>
              <div class="detail-item mb-4">
                <div class="detail-label">Mode</div>
                <div class="detail-value">{{ budgetStore.budgetNumber.mode === 'paycheck' ? 'Paycheck' : 'Fixed Pool' }}</div>
              </div>

              <!-- Paycheck Mode -->
              <template v-if="budgetStore.budgetNumber.mode === 'paycheck'">
                <div v-if="budgetStore.budgetNumber.total_income" class="detail-item mb-4">
                  <div class="detail-label">Monthly Income</div>
                  <div class="detail-value">${{ budgetStore.budgetNumber.total_income.toFixed(2) }}</div>
                </div>
                <div v-if="budgetStore.budgetNumber.total_expenses" class="detail-item mb-4">
                  <div class="detail-label">Total Expenses</div>
                  <div class="detail-value">${{ budgetStore.budgetNumber.total_expenses.toFixed(2) }}</div>
                </div>
                <div v-if="budgetStore.budgetNumber.remaining_money" class="detail-item mb-4">
                  <div class="detail-label">Remaining</div>
                  <div class="detail-value">${{ budgetStore.budgetNumber.remaining_money.toFixed(2) }}</div>
                </div>
                <div v-if="budgetStore.budgetNumber.days_remaining" class="detail-item">
                  <div class="detail-label">Days Until Paycheck</div>
                  <div class="detail-value">{{ budgetStore.budgetNumber.days_remaining }}</div>
                </div>
              </template>

              <!-- Fixed Pool Mode -->
              <template v-else>
                <div class="detail-item mb-4">
                  <div class="detail-label">Set Daily Budget</div>
                  <div class="detail-value">${{ budgetStore.budgetNumber.the_number.toFixed(2) }}</div>
                </div>
                <div v-if="budgetStore.budgetNumber.days_remaining" class="detail-item mb-4">
                  <div class="detail-label">Will Last</div>
                  <div class="detail-value">
                    {{ Math.floor(budgetStore.budgetNumber.days_remaining) }} days
                    <span class="text-medium-emphasis">({{ (budgetStore.budgetNumber.days_remaining / 30).toFixed(1) }} months)</span>
                  </div>
                </div>
                <div v-if="budgetStore.budgetNumber.total_money" class="detail-item">
                  <div class="detail-label">Total Money Available</div>
                  <div class="detail-value">${{ budgetStore.budgetNumber.total_money.toFixed(2) }}</div>
                </div>
              </template>
            </v-card-text>
          </v-card>
        </v-window-item>

        <!-- Slide 3: Recent Transactions -->
        <v-window-item :value="2">
          <v-card elevation="2" class="transactions-card">
            <v-card-title class="text-h5">Recent Transactions</v-card-title>
            <v-card-text class="transactions-list">
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
        </v-window-item>
      </v-window>

      <!-- Slide Indicators -->
      <div class="slide-indicators mb-6" role="tablist" aria-label="Dashboard sections">
        <v-btn
          v-for="n in 3"
          :key="n"
          :icon="currentSlide === n - 1"
          size="x-small"
          :color="currentSlide === n - 1 ? 'primary' : 'grey'"
          @click="currentSlide = n - 1"
          class="mx-1"
          role="tab"
          :aria-selected="currentSlide === n - 1"
          :aria-label="['The Number Display', 'Budget Details', 'Recent Transactions'][n - 1]"
          :aria-controls="`slide-${n - 1}`"
        >
          <v-icon v-if="currentSlide === n - 1">mdi-circle</v-icon>
          <v-icon v-else>mdi-circle-outline</v-icon>
        </v-btn>
      </div>

      <!-- Record Transaction Card (Always Visible Below) -->
      <v-card elevation="2" class="pa-6 record-transaction-card">
        <v-card-title class="text-h5 mb-4 text-center">Record Transaction</v-card-title>
        <v-card-text>
          <v-form ref="transactionForm" @submit.prevent="recordSpending">
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
              :rules="[rules.positive]"
              required
              class="mb-2"
            />
            <v-text-field
              v-model="spendingDescription"
              :label="transactionType === 'out' ? 'What did you spend on?' : 'Source of income'"
              variant="outlined"
              :rules="[rules.required, rules.maxLength(200)]"
              counter="200"
              required
              class="mb-2"
              :placeholder="transactionType === 'out' ? 'e.g., Groceries' : 'e.g., Freelance work'"
            />
            <v-btn
              type="submit"
              :color="transactionType === 'out' ? 'error' : 'success'"
              block
              size="large"
              :loading="budgetStore.loadingTransactions"
            >
              <v-icon class="mr-1">{{ transactionType === 'out' ? 'mdi-minus' : 'mdi-plus' }}</v-icon>
              {{ transactionType === 'out' ? 'Record Spending' : 'Add Money' }}
            </v-btn>
          </v-form>
        </v-card-text>
      </v-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, watch } from 'vue'
import { useBudgetStore } from '@/stores/budget'
import { useAuthStore } from '@/stores/auth'
import { useValidation } from '@/composables/useValidation'
import NumberDisplay from '@/components/NumberDisplay.vue'
import Onboarding from '@/components/Onboarding.vue'

const budgetStore = useBudgetStore()
const authStore = useAuthStore()
const { rules } = useValidation()

const transactionForm = ref()
const spendingAmount = ref<number | null>(null)
const spendingDescription = ref('')
const transactionType = ref<'in' | 'out'>('out')
const currentSlide = ref(0)

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
  // Validate form before submitting
  const { valid } = await transactionForm.value.validate()
  if (!valid) return

  try {
    if (transactionType.value === 'out') {
      // Regular spending transaction
      await budgetStore.recordTransaction({
        amount: spendingAmount.value!,
        description: spendingDescription.value,
        category: 'expense'
      })
    } else {
      // Money In - record as positive amount with income category
      await budgetStore.recordTransaction({
        amount: spendingAmount.value!,  // Positive amount
        description: spendingDescription.value,
        category: 'income'
      })
    }

    // Reset form - use null to avoid triggering "must be greater than 0" validation
    spendingAmount.value = null
    spendingDescription.value = ''
    transactionForm.value.resetValidation()
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
/* Phase 2.1: Mobile-first responsive padding */
.dashboard {
  max-width: 1400px;
  margin: 0 auto;
  padding: var(--spacing-sm); /* 16px on mobile */
}

@media (min-width: 768px) {
  .dashboard {
    padding: var(--spacing-md); /* 24px on desktop */
  }
}

.hero-section {
  text-align: center;
  padding: var(--spacing-md) var(--spacing-sm); /* Reduced mobile padding */
  margin-bottom: var(--spacing-lg);
  background: linear-gradient(135deg,
    var(--color-sage-green) 0%,
    rgba(233, 245, 219, 0.7) 100%);
  border-radius: 16px;
  box-shadow: 0 4px 16px rgba(74, 95, 122, 0.08);
}

@media (min-width: 768px) {
  .hero-section {
    padding: var(--spacing-xl) var(--spacing-md) var(--spacing-lg);
  }
}

/* Phase 2.4: Responsive hero title (reduced min from 3rem to 2rem) */
.hero-title {
  font-size: clamp(2rem, 6vw, 4.5rem);
  font-weight: 400;
  color: var(--color-soft-charcoal);
  margin-bottom: var(--spacing-sm);
  letter-spacing: -0.02em;
}

.hero-subtitle {
  font-size: clamp(1.25rem, 3vw, 1.75rem);
  color: var(--color-text-secondary);
  font-style: italic;
  font-weight: 400;
}

/* Phase 2.3: Responsive carousel height */
.main-carousel {
  max-width: 800px;
  margin: 0 auto;
  min-height: 300px; /* Reduced from 500px for mobile */
  max-height: 80vh;  /* Never taller than viewport */
}

@media (min-width: 768px) {
  .main-carousel {
    min-height: 450px;
  }
}

/* Budget Details Card */
.budget-details-card {
  max-width: 800px;
  margin: 0 auto;
  padding: var(--spacing-md) !important; /* Mobile padding */
  background: linear-gradient(135deg,
    var(--color-sage-green) 0%,
    rgba(233, 245, 219, 0.85) 100%);
  border-radius: 24px;
  box-shadow: 0 8px 32px rgba(135, 152, 106, 0.15);
  border: 2px solid rgba(255, 255, 255, 0.3);
  min-height: 450px;
}

@media (min-width: 768px) {
  .budget-details-card {
    padding: var(--spacing-xl) !important; /* Desktop padding */
  }
}

.detail-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--spacing-sm) 0;
  border-bottom: 1px solid rgba(135, 152, 106, 0.1);
}

.detail-item:last-child {
  border-bottom: none;
}

.detail-label {
  font-size: 1rem;
  color: var(--color-text-secondary);
  font-weight: 500;
}

.detail-value {
  font-size: 1.25rem;
  color: var(--color-soft-charcoal);
  font-weight: 600;
  text-align: right;
}

/* Transactions Card */
.transactions-card {
  max-width: 800px;
  margin: 0 auto;
  padding: var(--spacing-md) !important; /* Mobile padding */
  background: linear-gradient(135deg,
    var(--color-sage-green) 0%,
    rgba(233, 245, 219, 0.85) 100%);
  border-radius: 24px;
  box-shadow: 0 8px 32px rgba(135, 152, 106, 0.15);
  border: 2px solid rgba(255, 255, 255, 0.3);
  min-height: 450px;
}

@media (min-width: 768px) {
  .transactions-card {
    padding: var(--spacing-xl) !important; /* Desktop padding */
  }
}

.transactions-list {
  max-height: 350px;
  overflow-y: auto;
}

/* Phase 3.1: Touch Target Enlargement */
/* Slide Indicators */
.slide-indicators {
  display: flex;
  justify-content: center;
  align-items: center;
}

.slide-indicators .v-btn {
  min-width: 44px !important;
  min-height: 44px !important;
}

/* Record Transaction Card */
.record-transaction-card {
  max-width: 600px;
  margin: 0 auto;
  padding: var(--spacing-md) !important; /* Consistent mobile padding */
  background-color: white;
  border: 1px solid rgba(233, 245, 219, 0.3);
  border-radius: 16px;
  box-shadow: 0 4px 16px rgba(135, 152, 106, 0.12);
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
  color: var(--color-text-primary);
  font-weight: 600;
}

:deep(.v-btn) {
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

/* Carousel navigation arrows */
:deep(.v-window__controls) {
  background: transparent;
}

:deep(.v-btn--icon.v-btn--density-default) {
  width: 48px !important;
  height: 48px !important;
  min-width: 48px !important;
  background-color: rgba(255, 255, 255, 0.8) !important;
  border: 1px solid var(--color-sage-green);
}
</style>
