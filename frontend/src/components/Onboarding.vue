<template>
  <v-card class="onboarding-card mx-auto" elevation="4" max-width="900">
    <v-card-title class="text-h4 pa-6 text-center bg-primary">
      <div class="text-white">
        <div class="text-h3 mb-2">The Number</div>
        <div class="text-subtitle-1">Your Simple Daily Budget App</div>
      </div>
    </v-card-title>

    <!-- Progress Indicator -->
    <v-card-text class="text-center py-2" v-if="currentStep > 0">
      <v-chip size="small" color="primary">
        Step {{ currentStep }} of 4
      </v-chip>
    </v-card-text>

    <v-card-text class="pa-8">
      <!-- Step 0: Welcome Screen -->
      <div v-if="currentStep === 0">
        <div class="text-center">
          <v-icon size="80" color="primary" class="mb-4">mdi-currency-usd</v-icon>
          <h2 class="text-h4 mb-4">Welcome to The Number!</h2>
          <p class="text-h6 text-medium-emphasis mb-6">
            Let's set up your daily budget in just 4 quick steps
          </p>

          <v-list class="text-left mb-6 mx-auto" max-width="500">
            <v-list-item>
              <template v-slot:prepend>
                <v-icon color="primary">mdi-numeric-1-circle</v-icon>
              </template>
              <v-list-item-title>Choose your budgeting style</v-list-item-title>
            </v-list-item>
            <v-list-item>
              <template v-slot:prepend>
                <v-icon color="primary">mdi-numeric-2-circle</v-icon>
              </template>
              <v-list-item-title>Enter your income or available money</v-list-item-title>
            </v-list-item>
            <v-list-item>
              <template v-slot:prepend>
                <v-icon color="primary">mdi-numeric-3-circle</v-icon>
              </template>
              <v-list-item-title>Add your monthly expenses</v-list-item-title>
            </v-list-item>
            <v-list-item>
              <template v-slot:prepend>
                <v-icon color="primary">mdi-numeric-4-circle</v-icon>
              </template>
              <v-list-item-title>See your daily spending limit!</v-list-item-title>
            </v-list-item>
          </v-list>

          <p class="text-body-1 mb-4">This will only take about 2 minutes.</p>
        </div>
      </div>

      <!-- Step 1: Choose Budget Mode -->
      <div v-else-if="currentStep === 1">
        <h2 class="text-h5 mb-6 text-center">Choose Your Budgeting Style</h2>
        <p class="text-center text-medium-emphasis mb-6">Which situation describes you best?</p>

        <v-radio-group v-model="budgetMode">
          <v-card
            class="mb-4 pa-4"
            :class="{ 'border-primary': budgetMode === 'paycheck' }"
            @click="budgetMode = 'paycheck'"
            style="cursor: pointer;"
          >
            <v-radio value="paycheck">
              <template v-slot:label>
                <div class="ml-4">
                  <div class="text-h6 mb-2">
                    <v-icon color="primary" class="mr-2">mdi-cash-check</v-icon>
                    Paycheck Mode
                  </div>
                  <div class="text-body-2 text-medium-emphasis">
                    I have regular income (weekly, bi-weekly, or monthly paychecks)
                  </div>
                  <div class="text-caption text-medium-emphasis mt-1">
                    → Calculate your daily budget from income and days until next paycheck
                  </div>
                </div>
              </template>
            </v-radio>
          </v-card>

          <v-card
            class="mb-4 pa-4"
            :class="{ 'border-primary': budgetMode === 'fixed_pool' }"
            @click="budgetMode = 'fixed_pool'"
            style="cursor: pointer;"
          >
            <v-radio value="fixed_pool">
              <template v-slot:label>
                <div class="ml-4">
                  <div class="text-h6 mb-2">
                    <v-icon color="primary" class="mr-2">mdi-piggy-bank</v-icon>
                    Fixed Pool Mode
                  </div>
                  <div class="text-body-2 text-medium-emphasis">
                    I have a fixed amount of money to work with
                  </div>
                  <div class="text-caption text-medium-emphasis mt-1">
                    → See how long your money will last and get a daily spending limit
                  </div>
                </div>
              </template>
            </v-radio>
          </v-card>
        </v-radio-group>
      </div>

      <!-- Step 2: Enter Details -->
      <div v-else-if="currentStep === 2">
        <h2 class="text-h5 mb-6 text-center">
          {{ budgetMode === 'paycheck' ? 'Paycheck Mode Setup' : 'Fixed Pool Setup' }}
        </h2>

        <v-form ref="detailsForm" class="max-w-500 mx-auto">
          <!-- Paycheck Mode Fields -->
          <div v-if="budgetMode === 'paycheck'">
            <v-text-field
              v-model.number="monthlyIncome"
              type="number"
              label="What is your total monthly income?"
              prefix="$"
              variant="outlined"
              :rules="[v => v > 0 || 'Income must be greater than 0']"
              class="mb-4"
              hint="Include all sources of income"
            />
            <v-text-field
              v-model.number="daysUntilPaycheck"
              type="number"
              label="How many days until your next paycheck?"
              variant="outlined"
              :rules="[v => v > 0 || 'Days must be greater than 0']"
              hint="Enter the number of days remaining"
            />
          </div>

          <!-- Fixed Pool Mode Fields -->
          <div v-if="budgetMode === 'fixed_pool'">
            <v-text-field
              v-model.number="totalMoney"
              type="number"
              label="How much total money do you have available?"
              prefix="$"
              variant="outlined"
              :rules="[v => v > 0 || 'Amount must be greater than 0']"
              hint="Enter the total amount you have to work with"
            />
          </div>
        </v-form>
      </div>

      <!-- Step 3: Add Expenses -->
      <div v-else-if="currentStep === 3">
        <h2 class="text-h5 mb-4 text-center">Add Your Monthly Expenses</h2>
        <p class="text-center text-medium-emphasis mb-6">
          Add expenses that you MUST pay each month (rent, utilities, bills, etc.)
        </p>

        <!-- Add Expense Form -->
        <v-card variant="outlined" class="mb-4 pa-4 max-w-600 mx-auto">
          <v-form @submit.prevent="addExpense">
            <v-row>
              <v-col cols="12" sm="5">
                <v-text-field
                  v-model="newExpense.name"
                  label="Expense Name"
                  variant="outlined"
                  density="compact"
                  placeholder="e.g., Rent"
                />
              </v-col>
              <v-col cols="12" sm="4">
                <v-text-field
                  v-model.number="newExpense.amount"
                  type="number"
                  label="Amount"
                  prefix="$"
                  variant="outlined"
                  density="compact"
                />
              </v-col>
              <v-col cols="12" sm="3">
                <v-btn
                  type="submit"
                  color="primary"
                  block
                  :disabled="!newExpense.name || newExpense.amount <= 0"
                >
                  <v-icon>mdi-plus</v-icon>
                  Add
                </v-btn>
              </v-col>
            </v-row>
          </v-form>
        </v-card>

        <!-- Expenses List -->
        <div class="max-w-600 mx-auto">
          <v-alert v-if="expenses.length === 0" type="info" variant="tonal" class="mb-4">
            No expenses added yet. You can skip this step if you have no monthly expenses.
          </v-alert>

          <v-list v-else class="mb-4">
            <v-list-item
              v-for="(expense, index) in expenses"
              :key="index"
              class="border-b"
            >
              <template v-slot:prepend>
                <v-icon>mdi-receipt</v-icon>
              </template>
              <v-list-item-title>{{ expense.name }}</v-list-item-title>
              <v-list-item-subtitle>${{ expense.amount.toFixed(2) }}</v-list-item-subtitle>
              <template v-slot:append>
                <v-btn
                  icon
                  size="small"
                  variant="text"
                  @click="removeExpense(index)"
                >
                  <v-icon>mdi-delete</v-icon>
                </v-btn>
              </template>
            </v-list-item>

            <v-divider class="my-2" />

            <v-list-item class="bg-grey-lighten-4">
              <v-list-item-title class="font-weight-bold">
                Total Monthly Expenses
              </v-list-item-title>
              <v-list-item-subtitle class="text-h6">
                ${{ totalExpenses.toFixed(2) }}
              </v-list-item-subtitle>
            </v-list-item>
          </v-list>
        </div>
      </div>

      <!-- Step 4: Show The Number -->
      <div v-else-if="currentStep === 4">
        <div class="text-center">
          <v-icon size="80" color="success" class="mb-4">mdi-check-circle</v-icon>
          <h2 class="text-h4 mb-6">Here's Your Number!</h2>

          <v-card class="mb-6 pa-6 max-w-600 mx-auto" elevation="2">
            <!-- Mode-specific summary -->
            <div v-if="budgetMode === 'paycheck'" class="mb-4">
              <div class="d-flex justify-space-between mb-2">
                <span>Monthly Income:</span>
                <span class="font-weight-bold">${{ monthlyIncome.toFixed(2) }}</span>
              </div>
              <div class="d-flex justify-space-between mb-2">
                <span>Total Expenses:</span>
                <span class="font-weight-bold">${{ totalExpenses.toFixed(2) }}</span>
              </div>
              <v-divider class="my-3" />
              <div class="d-flex justify-space-between mb-2">
                <span>After Expenses:</span>
                <span class="font-weight-bold">${{ (monthlyIncome - totalExpenses).toFixed(2) }}</span>
              </div>
              <div class="d-flex justify-space-between mb-4">
                <span>Days to Paycheck:</span>
                <span class="font-weight-bold">{{ daysUntilPaycheck }}</span>
              </div>
            </div>

            <div v-if="budgetMode === 'fixed_pool'" class="mb-4">
              <div class="d-flex justify-space-between mb-2">
                <span>Total Money:</span>
                <span class="font-weight-bold">${{ totalMoney.toFixed(2) }}</span>
              </div>
              <div class="d-flex justify-space-between mb-2">
                <span>Monthly Expenses:</span>
                <span class="font-weight-bold">${{ totalExpenses.toFixed(2) }}</span>
              </div>
              <v-divider class="my-3" />
              <div class="d-flex justify-space-between mb-4">
                <span>Will Last:</span>
                <span class="font-weight-bold">
                  {{ totalExpenses > 0 ? (totalMoney / totalExpenses).toFixed(1) : '∞' }} months
                </span>
              </div>
            </div>

            <v-divider class="my-4" />

            <!-- The Number -->
            <div class="text-center py-4 bg-success-lighten rounded">
              <div class="text-h6 mb-2">THE NUMBER</div>
              <div class="text-h2 font-weight-bold text-success">
                ${{ calculatedNumber.toFixed(2) }}<span class="text-h5">/day</span>
              </div>
            </div>
          </v-card>

          <!-- Tips -->
          <v-card class="mb-6 pa-4 max-w-600 mx-auto text-left" variant="outlined">
            <div class="text-h6 mb-3">
              <v-icon color="primary" class="mr-2">mdi-lightbulb-outline</v-icon>
              Tips for Success
            </div>
            <ul class="text-body-2">
              <li>Check "The Number" every morning</li>
              <li>Record your spending throughout the day</li>
              <li>Try to stay under your daily limit</li>
              <li>Update your expenses if anything changes</li>
            </ul>
          </v-card>

          <!-- Warnings -->
          <v-alert
            v-if="calculatedNumber <= 0"
            type="warning"
            variant="tonal"
            class="max-w-600 mx-auto mb-4"
          >
            <strong>Warning:</strong> Your expenses exceed your {{ budgetMode === 'paycheck' ? 'income' : 'money' }}.
            Consider reviewing your expenses or finding ways to increase income.
          </v-alert>

          <v-alert
            v-else-if="calculatedNumber < 20 && budgetMode === 'paycheck'"
            type="info"
            variant="tonal"
            class="max-w-600 mx-auto mb-4"
          >
            Your budget is tight. Track your spending carefully!
          </v-alert>
        </div>
      </div>
    </v-card-text>

    <!-- Navigation Buttons -->
    <v-card-actions class="pa-4">
      <v-btn
        v-if="currentStep > 0"
        variant="text"
        @click="prevStep"
        :disabled="loading"
      >
        Back
      </v-btn>
      <v-spacer />
      <v-btn
        v-if="currentStep < 4"
        color="primary"
        @click="nextStep"
        :disabled="!canProceed || loading"
        :loading="loading"
      >
        {{ currentStep === 0 ? 'Get Started' : 'Next' }}
      </v-btn>
      <v-btn
        v-else
        color="success"
        size="large"
        @click="completeOnboarding"
        :loading="loading"
      >
        Complete Setup
      </v-btn>
    </v-card-actions>

    <!-- Error Snackbar -->
    <v-snackbar
      v-model="showError"
      color="error"
      timeout="5000"
    >
      {{ errorMessage }}
    </v-snackbar>
  </v-card>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { budgetApi } from '@/services/api'

const emit = defineEmits(['complete'])

console.log('🎯 Onboarding component loaded')

// Current step (0 = welcome, 1-4 = steps)
const currentStep = ref(0)

// Budget Mode
const budgetMode = ref<'paycheck' | 'fixed_pool'>('paycheck')

// Paycheck Mode Data
const monthlyIncome = ref(0)
const daysUntilPaycheck = ref(14)

// Fixed Pool Mode Data
const totalMoney = ref(0)

// Expenses
const expenses = ref<Array<{ name: string; amount: number; is_fixed: boolean }>>([])
const newExpense = ref({ name: '', amount: 0, is_fixed: true })

// UI State
const loading = ref(false)
const showError = ref(false)
const errorMessage = ref('')

// Computed
const totalExpenses = computed(() =>
  expenses.value.reduce((sum, exp) => sum + exp.amount, 0)
)

const calculatedNumber = computed(() => {
  if (budgetMode.value === 'paycheck') {
    const remaining = monthlyIncome.value - totalExpenses.value
    return daysUntilPaycheck.value > 0 ? Math.max(0, remaining / daysUntilPaycheck.value) : 0
  } else {
    const daysRemaining = totalExpenses.value > 0 ? (totalMoney.value / totalExpenses.value) * 30 : 0
    return daysRemaining > 0 ? totalMoney.value / daysRemaining : 0
  }
})

const canProceed = computed(() => {
  if (currentStep.value === 0) return true
  if (currentStep.value === 1) return !!budgetMode.value
  if (currentStep.value === 2) {
    if (budgetMode.value === 'paycheck') {
      return monthlyIncome.value > 0 && daysUntilPaycheck.value > 0
    } else {
      return totalMoney.value > 0
    }
  }
  if (currentStep.value === 3) return true // Can skip expenses
  return true
})

// Methods
function addExpense() {
  console.log('Adding expense:', newExpense.value)
  if (newExpense.value.name && newExpense.value.amount > 0) {
    expenses.value.push({ ...newExpense.value })
    newExpense.value = { name: '', amount: 0, is_fixed: true }
  }
}

function removeExpense(index: number) {
  console.log('Removing expense at index:', index)
  expenses.value.splice(index, 1)
}

function prevStep() {
  if (currentStep.value > 0) {
    currentStep.value--
    console.log('Previous step:', currentStep.value)
  }
}

function nextStep() {
  if (canProceed.value && currentStep.value < 4) {
    currentStep.value++
    console.log('Next step:', currentStep.value)
  }
}

async function completeOnboarding() {
  console.log('🎉 Completing onboarding...')
  loading.value = true
  showError.value = false

  try {
    // 1. Save budget configuration
    const budgetConfig: any = { mode: budgetMode.value }
    if (budgetMode.value === 'paycheck') {
      budgetConfig.monthly_income = monthlyIncome.value
      budgetConfig.days_until_paycheck = daysUntilPaycheck.value
    } else {
      budgetConfig.total_money = totalMoney.value
    }

    console.log('Saving budget config:', budgetConfig)
    await budgetApi.configureBudget(budgetConfig)
    console.log('✅ Budget config saved')

    // 2. Save all expenses
    for (const expense of expenses.value) {
      console.log('Saving expense:', expense)
      await budgetApi.createExpense(expense)
    }
    console.log('✅ All expenses saved')

    // 3. Emit completion event
    console.log('✅ Onboarding complete!')
    emit('complete')
  } catch (e: any) {
    console.error('❌ Onboarding error:', e)
    showError.value = true
    errorMessage.value = e.response?.data?.detail || 'Failed to complete onboarding'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.onboarding-card {
  margin: 20px auto;
}

.border-primary {
  border: 2px solid rgb(var(--v-theme-primary)) !important;
}

.max-w-500 {
  max-width: 500px;
}

.max-w-600 {
  max-width: 600px;
}

.bg-success-lighten {
  background-color: rgba(76, 175, 80, 0.1);
}
</style>
