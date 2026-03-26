<template>
  <div class="dashboard">
    <!-- Pool Contribution Prompt Dialog -->
    <v-dialog v-model="showPoolPrompt" max-width="400" persistent>
      <v-card>
        <v-card-title class="text-center pa-4" style="background-color: #faf3dd;">
          <v-icon color="success" size="large" class="mr-2">mdi-party-popper</v-icon>
          Congratulations!
        </v-card-title>
        <v-card-text class="pa-6 text-center">
          <p class="text-body-1 mb-4">You have money that carried over from your last pay period!</p>
          <p class="text-h3 font-weight-bold my-4" style="color: #4CAF50;">
            ${{ budgetStore.budgetNumber?.pending_pool_contribution ? Math.ceil(budgetStore.budgetNumber.pending_pool_contribution) : 0 }}
          </p>
          <p class="text-body-2 text-medium-emphasis">Would you like to add it to your savings pool?</p>
        </v-card-text>
        <v-card-actions class="justify-center pb-4">
          <v-btn variant="text" @click="declinePoolContribution">No Thanks</v-btn>
          <v-btn color="primary" variant="elevated" @click="acceptPoolContribution">Add to Pool</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Add to Pool Modal -->
    <AddToPoolModal v-model="showAddToPoolModal" @added="onPoolAdded" />

    <!-- Hero Section removed - Onboarding component has its own branded header -->

    <!-- Error Alert (only show when not in onboarding) -->
    <div aria-live="polite" role="status">
      <v-alert
        v-if="budgetStore.error && budgetStore.budgetNumber"
        type="error"
        class="mb-4"
        closable
        @click:close="budgetStore.error = null"
      >
        {{ budgetStore.error }}
      </v-alert>
    </div>

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
        <!-- Slide: The Number Display -->
        <v-window-item value="number">
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

        <!-- Slide: Savings Pool -->
        <v-window-item v-if="hasPool" value="pool">
          <v-card elevation="2" class="pool-card pa-6 text-center">
            <v-icon size="48" class="mb-2" color="primary">mdi-piggy-bank</v-icon>
            <v-card-title class="text-h5 justify-center mb-2">Savings Pool</v-card-title>
            <v-card-text>
              <div class="text-h3 font-weight-bold my-4" style="color: var(--color-soft-charcoal);">
                ${{ Math.ceil(budgetStore.budgetNumber.pool_balance) }}
              </div>
              <v-chip
                :color="poolEnabled ? 'success' : 'default'"
                size="small"
                class="mb-4"
              >{{ poolEnabled ? 'Active — included in daily budget' : 'Inactive — not included' }}</v-chip>
              <v-switch
                v-model="poolEnabled"
                :label="poolEnabled ? 'Pool funds included' : 'Pool funds excluded'"
                color="primary"
                density="compact"
                hide-details
                class="d-inline-flex justify-center mb-4"
                @update:model-value="togglePoolEnabled"
              />
              <div v-if="budgetStore.budgetNumber.mode === 'paycheck'">
                <v-btn
                  variant="outlined"
                  size="small"
                  color="primary"
                  @click="showAddToPoolModal = true"
                >
                  <v-icon size="small" class="mr-1">mdi-plus</v-icon>
                  Add to Pool
                </v-btn>
              </div>
            </v-card-text>
          </v-card>
        </v-window-item>

        <!-- Slide: Budget Details -->
        <v-window-item value="details">
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

        <!-- Slide: Recent Transactions -->
        <v-window-item value="transactions">
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
      <div class="slide-indicators mb-6">
        <span
          v-for="key in slideKeys"
          :key="key"
          class="slide-dot"
          :class="{ active: currentSlide === key }"
          @click="currentSlide = key"
        />
      </div>

      <!-- Badge Permission Prompt -->
      <v-card
        v-if="showBadgePrompt"
        class="badge-prompt mb-4 pa-4 text-center"
        elevation="1"
      >
        <div class="text-body-2 mb-2">Show your daily budget on the app icon?</div>
        <div class="d-flex justify-center ga-2">
          <v-btn size="small" variant="text" @click="dismissBadgePrompt">No Thanks</v-btn>
          <v-btn size="small" color="primary" variant="elevated" @click="enableBadge">Enable</v-btn>
        </div>
      </v-card>

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
import { ref, onMounted, onUnmounted, computed, watch } from 'vue'
import { useBudgetStore } from '@/stores/budget'
import { useAuthStore } from '@/stores/auth'
import { useValidation } from '@/composables/useValidation'
import NumberDisplay from '@/components/NumberDisplay.vue'
import Onboarding from '@/components/Onboarding.vue'
import AddToPoolModal from '@/components/AddToPoolModal.vue'

const budgetStore = useBudgetStore()
const authStore = useAuthStore()
const { rules } = useValidation()

const transactionForm = ref()
const spendingAmount = ref<number | null>(null)
const spendingDescription = ref('')
const transactionType = ref<'in' | 'out'>('out')
const currentSlide = ref('number')

// Track the last date we fetched data (for day-change detection)
const lastFetchDate = ref<string | null>(null)

// Pool feature state
const showPoolPrompt = ref(false)
const showAddToPoolModal = ref(false)
const poolEnabled = ref(false)
const badgePromptDismissed = ref(localStorage.getItem('badge_prompt_dismissed') === 'true')

const showBadgePrompt = computed(() =>
  !badgePromptDismissed.value &&
  budgetStore.needsBadgePermission() &&
  budgetStore.budgetNumber != null
)

function dismissBadgePrompt() {
  badgePromptDismissed.value = true
  localStorage.setItem('badge_prompt_dismissed', 'true')
}

async function enableBadge() {
  await budgetStore.requestBadgePermission()
  dismissBadgePrompt()
}

const recentTransactions = computed(() =>
  budgetStore.transactions.slice(0, 5)
)

const hasPool = computed(() => (budgetStore.budgetNumber?.pool_balance ?? 0) > 0)

const slideKeys = computed(() => {
  const keys: string[] = ['number']
  if (hasPool.value) keys.push('pool')
  keys.push('details', 'transactions')
  return keys
})

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

    // Track when we last fetched data (for day-change detection)
    lastFetchDate.value = new Date().toDateString()

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

// Pool feature methods
async function acceptPoolContribution() {
  try {
    await budgetStore.acceptPoolContribution()
    showPoolPrompt.value = false
  } catch (e) {
    console.error('Failed to accept pool contribution:', e)
  }
}

async function declinePoolContribution() {
  try {
    await budgetStore.declinePoolContribution()
    showPoolPrompt.value = false
  } catch (e) {
    console.error('Failed to decline pool contribution:', e)
  }
}

async function togglePoolEnabled(enabled: boolean | null) {
  if (enabled === null) return
  try {
    await budgetStore.togglePool(enabled)
  } catch (e) {
    console.error('Failed to toggle pool:', e)
    // Revert local state on error
    poolEnabled.value = !enabled
  }
}

function onPoolAdded() {
  // Modal handles the API call, just close it
  showAddToPoolModal.value = false
}

// Sync pool enabled state with API response
watch(
  () => budgetStore.budgetNumber?.pool_enabled,
  (enabled) => {
    if (enabled !== undefined) {
      poolEnabled.value = enabled
    }
  },
  { immediate: true }
)

// Show pool prompt when there's a pending contribution
watch(
  () => budgetStore.budgetNumber?.pending_pool_contribution,
  (pending) => {
    if (pending && pending > 0) {
      showPoolPrompt.value = true
    }
  },
  { immediate: true }
)

onMounted(() => {
  loadDashboard()
})

// Day-change detection: refresh data when user returns to the app on a new day
// This ensures the budget resets correctly at midnight in the user's timezone
function handleVisibilityChange() {
  if (document.visibilityState === 'visible' && lastFetchDate.value) {
    const today = new Date().toDateString()
    if (lastFetchDate.value !== today) {
      console.log('🌅 Day changed since last fetch - refreshing data')
      console.log(`   Last fetch: ${lastFetchDate.value}, Today: ${today}`)
      loadDashboard()
    }
  }
}

// Set up visibility change listener
document.addEventListener('visibilitychange', handleVisibilityChange)

// Clean up listener on unmount
onUnmounted(() => {
  document.removeEventListener('visibilitychange', handleVisibilityChange)
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
    rgba(250, 243, 221, 0.7) 100%);
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
    rgba(250, 243, 221, 0.85) 100%);
  border-radius: 24px;
  box-shadow: 0 8px 32px rgba(74, 124, 89, 0.15);
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
  border-bottom: 1px solid rgba(74, 124, 89, 0.1);
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
    rgba(250, 243, 221, 0.85) 100%);
  border-radius: 24px;
  box-shadow: 0 8px 32px rgba(74, 124, 89, 0.15);
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

/* Slide Indicators - simple dots */
.slide-indicators {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 8px;
}

.slide-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background-color: var(--color-soft-charcoal, #4A5F7A);
  opacity: 0.25;
  cursor: pointer;
  transition: opacity 0.2s ease;
}

.slide-dot.active {
  opacity: 0.85;
}

/* Record Transaction Card */
.record-transaction-card {
  max-width: 600px;
  margin: 0 auto;
  padding: var(--spacing-md) !important; /* Consistent mobile padding */
  background-color: white;
  border: 1px solid rgba(250, 243, 221, 0.3);
  border-radius: 16px;
  box-shadow: 0 4px 16px rgba(74, 124, 89, 0.12);
}

/* Card styling to match brand */
:deep(.v-card) {
  background-color: white;
  border: 1px solid rgba(250, 243, 221, 0.3);
  border-radius: 12px;
  transition: all var(--transition-base) var(--transition-ease);
}

:deep(.v-card:hover) {
  border-color: var(--color-sage-green);
  box-shadow: 0 8px 24px rgba(74, 124, 89, 0.12);
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

/* Carousel navigation arrows - smaller to avoid text overlap */
:deep(.v-window__controls) {
  background: transparent;
  padding: 0 4px;
}

:deep(.v-window__controls .v-btn) {
  width: 32px !important;
  height: 32px !important;
  min-width: 32px !important;
  background-color: rgba(255, 255, 255, 0.9) !important;
  border: 1px solid var(--color-sage-green);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

:deep(.v-window__controls .v-btn .v-icon) {
  font-size: 18px;
}

/* Pool Card Styles */
.pool-card {
  max-width: 800px;
  margin: 0 auto;
  background: linear-gradient(135deg,
    var(--color-sage-green) 0%,
    rgba(250, 243, 221, 0.85) 100%) !important;
  border-radius: 24px !important;
  box-shadow: 0 8px 32px rgba(74, 124, 89, 0.15);
  border: 2px solid rgba(255, 255, 255, 0.3) !important;
  min-height: 300px;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.pool-card :deep(.v-switch .v-label) {
  color: var(--color-soft-charcoal);
}

/* Badge permission prompt */
.badge-prompt {
  max-width: 600px;
  margin: 0 auto;
  background-color: rgba(250, 243, 221, 0.6) !important;
  border: 1px solid rgba(74, 124, 89, 0.2) !important;
  border-radius: 12px !important;
}
</style>
