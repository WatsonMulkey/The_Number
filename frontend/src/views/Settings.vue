<template>
  <div class="settings">
    <h1 class="text-h3 mb-6">Budget Settings</h1>

    <v-card elevation="2" class="mb-6">
      <v-card-title>Configure Budget Mode</v-card-title>
      <v-card-text>
        <v-form @submit.prevent="saveBudgetConfig">
          <!-- Mode Selection -->
          <v-radio-group v-model="config.mode" class="mb-4">
            <v-radio
              value="paycheck"
              label="Paycheck Mode"
            >
              <template v-slot:label>
                <div>
                  <div class="font-weight-bold">Paycheck Mode</div>
                  <div class="text-caption text-medium-emphasis">
                    Calculate daily spending based on income and days until next paycheck
                  </div>
                </div>
              </template>
            </v-radio>
            <v-radio
              value="fixed_pool"
              label="Fixed Pool Mode"
            >
              <template v-slot:label>
                <div>
                  <div class="font-weight-bold">Fixed Pool Mode</div>
                  <div class="text-caption text-medium-emphasis">
                    Calculate how long your current money will last
                  </div>
                </div>
              </template>
            </v-radio>
          </v-radio-group>

          <!-- Paycheck Mode Fields -->
          <div v-if="config.mode === 'paycheck'">
            <v-text-field
              v-model.number="config.monthly_income"
              type="number"
              label="Monthly Income"
              variant="outlined"
              required
              class="mb-4"
            />
            <v-text-field
              v-model.number="config.days_until_paycheck"
              type="number"
              label="Days Until Next Paycheck"
              variant="outlined"
              required
              class="mb-4"
            />
          </div>

          <!-- Fixed Pool Mode Fields -->
          <div v-if="config.mode === 'fixed_pool'">
            <v-text-field
              v-model.number="config.total_money"
              type="number"
              label="Total Money Available"
              variant="outlined"
              required
              class="mb-4"
            />

            <p class="text-subtitle-2 mb-2">Budget Calculation Method:</p>

            <v-radio-group v-model="config.fixed_pool_mode" class="mb-4">
              <v-radio value="target_date">
                <template v-slot:label>
                  <div>
                    <div class="font-weight-medium">Last Until Specific Date</div>
                    <div class="text-caption text-medium-emphasis">
                      Set a target date, we'll calculate your daily budget
                    </div>
                  </div>
                </template>
              </v-radio>
              <v-radio value="daily_limit">
                <template v-slot:label>
                  <div>
                    <div class="font-weight-medium">Set Daily Spending Limit</div>
                    <div class="text-caption text-medium-emphasis">
                      Set how much to spend per day, we'll calculate when it runs out
                    </div>
                  </div>
                </template>
              </v-radio>
            </v-radio-group>

            <!-- Target End Date Field -->
            <v-text-field
              v-if="config.fixed_pool_mode === 'target_date'"
              v-model="config.target_end_date"
              type="date"
              label="Target End Date"
              variant="outlined"
              required
              class="mb-4"
              hint="When do you need this money to last until?"
            />

            <!-- Daily Spending Limit Field -->
            <v-text-field
              v-if="config.fixed_pool_mode === 'daily_limit'"
              v-model.number="config.daily_spending_limit"
              type="number"
              label="Daily Spending Limit"
              variant="outlined"
              required
              class="mb-4"
              hint="How much do you want to limit yourself to per day?"
            />
          </div>

          <v-btn
            type="submit"
            color="primary"
            size="large"
            :loading="loading"
          >
            Save Configuration
          </v-btn>
        </v-form>
      </v-card-text>
    </v-card>

    <!-- Current Config Display -->
    <v-card v-if="currentConfig" elevation="2">
      <v-card-title>Current Configuration</v-card-title>
      <v-card-text>
        <v-list density="compact">
          <v-list-item>
            <v-list-item-title>Mode</v-list-item-title>
            <v-list-item-subtitle>
              {{ currentConfig.mode === 'paycheck' ? 'Paycheck Mode' : 'Fixed Pool Mode' }}
            </v-list-item-subtitle>
          </v-list-item>
          <v-list-item v-if="currentConfig.monthly_income">
            <v-list-item-title>Monthly Income</v-list-item-title>
            <v-list-item-subtitle>
              {{ currentConfig.monthly_income.toFixed(2) }}
            </v-list-item-subtitle>
          </v-list-item>
          <v-list-item v-if="currentConfig.days_until_paycheck">
            <v-list-item-title>Days Until Paycheck</v-list-item-title>
            <v-list-item-subtitle>
              {{ currentConfig.days_until_paycheck }}
            </v-list-item-subtitle>
          </v-list-item>
          <v-list-item v-if="currentConfig.total_money !== undefined">
            <v-list-item-title>Total Money</v-list-item-title>
            <v-list-item-subtitle>
              {{ currentConfig.total_money.toFixed(2) }}
            </v-list-item-subtitle>
          </v-list-item>
          <v-list-item v-if="currentConfig.target_end_date">
            <v-list-item-title>Target End Date</v-list-item-title>
            <v-list-item-subtitle>
              {{ new Date(currentConfig.target_end_date).toLocaleDateString() }}
            </v-list-item-subtitle>
          </v-list-item>
          <v-list-item v-if="currentConfig.daily_spending_limit">
            <v-list-item-title>Daily Spending Limit</v-list-item-title>
            <v-list-item-subtitle>
              {{ currentConfig.daily_spending_limit.toFixed(2) }}
            </v-list-item-subtitle>
          </v-list-item>
        </v-list>
      </v-card-text>
    </v-card>

    <!-- Success Snackbar -->
    <v-snackbar
      v-model="showSuccess"
      color="success"
      timeout="3000"
    >
      Budget configuration saved successfully!
    </v-snackbar>

    <!-- Error Snackbar -->
    <v-snackbar
      v-model="showError"
      color="error"
      timeout="5000"
    >
      {{ errorMessage }}
    </v-snackbar>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { budgetApi } from '@/services/api'
import { useBudgetStore } from '@/stores/budget'

const budgetStore = useBudgetStore()

const config = ref({
  mode: 'paycheck' as 'paycheck' | 'fixed_pool',
  monthly_income: 0,
  days_until_paycheck: 14,
  total_money: 0,
  fixed_pool_mode: 'target_date' as 'target_date' | 'daily_limit',
  target_end_date: '',
  daily_spending_limit: 0,
})

const currentConfig = ref<any>(null)
const loading = ref(false)
const showSuccess = ref(false)
const showError = ref(false)
const errorMessage = ref('')

async function loadCurrentConfig() {
  try {
    const response = await budgetApi.getBudgetConfig()
    if (response.data.configured) {
      currentConfig.value = response.data
      config.value = {
        mode: response.data.mode,
        monthly_income: response.data.monthly_income || 0,
        days_until_paycheck: response.data.days_until_paycheck || 14,
        total_money: response.data.total_money || 0,
        fixed_pool_mode: (response.data.target_end_date ? 'target_date' : 'daily_limit') as 'target_date' | 'daily_limit',
        target_end_date: response.data.target_end_date ? response.data.target_end_date.split('T')[0] : '',
        daily_spending_limit: response.data.daily_spending_limit || 0,
      }
    }
  } catch (e: any) {
    console.error('Failed to load config:', e)
  }
}

async function saveBudgetConfig() {
  loading.value = true
  showError.value = false

  try {
    // Only send fields relevant to the current mode
    const payload: any = { mode: config.value.mode }

    if (config.value.mode === 'paycheck') {
      payload.monthly_income = config.value.monthly_income
      payload.days_until_paycheck = config.value.days_until_paycheck
    } else {
      payload.total_money = config.value.total_money
      // Include fixed pool mode options
      if (config.value.fixed_pool_mode === 'target_date' && config.value.target_end_date) {
        payload.target_end_date = new Date(config.value.target_end_date).toISOString()
      } else if (config.value.fixed_pool_mode === 'daily_limit' && config.value.daily_spending_limit > 0) {
        payload.daily_spending_limit = config.value.daily_spending_limit
      }
    }

    await budgetApi.configureBudget(payload)
    showSuccess.value = true
    await loadCurrentConfig()
    // Refresh "The Number" on the dashboard
    await budgetStore.fetchNumber()
  } catch (e: any) {
    showError.value = true
    errorMessage.value = e.response?.data?.detail || 'Failed to save configuration'
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadCurrentConfig()
})
</script>

<style scoped>
.settings {
  max-width: 800px;
  margin: 0 auto;
  padding: var(--spacing-md);
}

/* Page title styling */
h1 {
  font-family: var(--font-display);
  color: var(--color-text-primary);
  font-weight: 400;
}

/* Card styling */
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
  font-size: 1.5rem;
}

/* Button styling */
:deep(.v-btn) {
  font-family: var(--font-ui);
  font-weight: 600;
  text-transform: none;
}

:deep(.v-btn.bg-primary) {
  background-color: var(--color-sage-green) !important;
  color: var(--color-soft-charcoal) !important;
}

/* Form elements */
:deep(.v-text-field) {
  font-family: var(--font-ui);
}

:deep(.v-radio) {
  font-family: var(--font-ui);
}

:deep(.v-label) {
  font-family: var(--font-ui);
}

/* Active radio button */
:deep(.v-selection-control--dirty .v-selection-control__input) {
  color: var(--color-sage-green) !important;
}
</style>
