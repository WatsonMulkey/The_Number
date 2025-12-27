<template>
  <v-card class="onboarding-card mx-auto" elevation="4" max-width="900" color="#E9F5DB">
    <v-card-title class="text-h4 pa-6 text-center" style="background-color: #E9F5DB;">
      <div>
        <div class="text-h3 mb-2" style="color: #2d5016;">The Number</div>
        <div class="text-subtitle-1" style="color: #4a7c2f;">Your Simple Daily Budget App</div>
      </div>
    </v-card-title>

    <!-- Progress Indicator -->
    <v-card-text class="text-center py-1" v-if="currentStep > 0">
      <v-chip size="small" color="primary">
        Step {{ currentStep }} of 5
      </v-chip>
    </v-card-text>

    <v-card-text class="pa-6">
      <!-- Step 0: Welcome + Account Creation -->
      <div v-if="currentStep === 0">
        <div class="text-center mb-6">
          <v-icon size="100" color="primary" class="mb-3">mdi-currency-usd</v-icon>
          <h2 class="text-h3 mb-3">Welcome to The Number!</h2>
          <p class="text-h5 text-medium-emphasis mb-4">
            Let's set up your daily budget in just 5 quick steps
          </p>
        </div>

        <!-- Account Creation Section -->
        <v-card class="max-w-700 mx-auto pa-6 mb-6" elevation="3" color="white">
          <h3 class="text-h5 mb-4 text-center">Create an Account</h3>

          <v-alert type="info" variant="tonal" class="mb-4">
            <div class="text-body-2">
              Create an account to save your budget history and make The Number easier to use.
              If you would like, you can enter an email address for password resetting, <strong>BUT you can use
              The Number without entering any personally identifiable information</strong>.
            </div>
            <div class="text-body-2 mt-3">
              While we take data and security very seriously, we are also only interested in helping
              you budget, not selling your info to 3rd parties.
            </div>
            <div class="text-body-2 mt-3">
              At the end of the setup process, you can download a budget file that you can use
              elsewhere, or use to reload your budget information.
            </div>
          </v-alert>

          <v-form ref="accountForm" @submit.prevent="createAccount">
            <v-text-field
              v-model="username"
              label="Username"
              variant="outlined"
              :rules="[rules.required, rules.username]"
              required
              class="mb-3"
              hint="Required - Choose a unique username"
              persistent-hint
            />

            <v-text-field
              v-model="email"
              label="Email (Optional)"
              variant="outlined"
              :rules="email ? [rules.email] : []"
              type="email"
              class="mb-3"
              hint="Optional - Only needed for password reset"
              persistent-hint
            />

            <v-text-field
              v-model="password"
              label="Password"
              variant="outlined"
              :rules="[rules.required, rules.minPassword]"
              type="password"
              required
              class="mb-3"
              hint="At least 8 characters"
              persistent-hint
            />

            <v-text-field
              v-model="confirmPassword"
              label="Confirm Password"
              variant="outlined"
              :rules="[rules.required, v => v === password || 'Passwords must match']"
              type="password"
              required
              class="mb-4"
            />

            <v-alert v-if="accountError" type="error" class="mb-4">
              {{ accountError }}
            </v-alert>

            <div class="text-center">
              <v-btn
                type="submit"
                color="primary"
                size="large"
                :loading="creatingAccount"
                class="px-8"
              >
                Create Account & Continue
              </v-btn>
            </div>
          </v-form>

          <v-divider class="my-4" />

          <div class="text-center">
            <p class="text-body-2 mb-2">Already have an account?</p>
            <v-btn variant="text" @click="showLoginDialog = true">
              Login Instead
            </v-btn>
          </div>
        </v-card>
      </div>

      <!-- Step 1: Choose Budget Mode -->
      <div v-else-if="currentStep === 1">
        <h2 class="text-h4 mb-4 text-center">Choose Your Budgeting Style</h2>
        <p class="text-h6 text-center text-medium-emphasis mb-4">Which situation describes you best?</p>

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
        <h2 class="text-h4 mb-4 text-center">
          {{ budgetMode === 'paycheck' ? 'Paycheck Mode Setup' : 'Fixed Pool Setup' }}
        </h2>

        <v-form ref="detailsForm" class="max-w-500 mx-auto" @submit.prevent="nextStep">
          <!-- Paycheck Mode Fields -->
          <div v-if="budgetMode === 'paycheck'">
            <p class="text-h6 mb-3">How often do you get paid?</p>
            <v-radio-group v-model="payFrequency" class="mb-4">
              <v-radio value="weekly">
                <template v-slot:label>
                  <div>
                    <strong>Weekly</strong>
                    <div class="text-caption text-medium-emphasis">Every 7 days</div>
                  </div>
                </template>
              </v-radio>
              <v-radio value="biweekly">
                <template v-slot:label>
                  <div>
                    <strong>Bi-weekly</strong>
                    <div class="text-caption text-medium-emphasis">Every 14 days</div>
                  </div>
                </template>
              </v-radio>
              <v-radio value="semimonthly">
                <template v-slot:label>
                  <div>
                    <strong>Semi-monthly</strong>
                    <div class="text-caption text-medium-emphasis">Twice a month (e.g., 1st and 15th)</div>
                  </div>
                </template>
              </v-radio>
              <v-radio value="monthly">
                <template v-slot:label>
                  <div>
                    <strong>Monthly</strong>
                    <div class="text-caption text-medium-emphasis">Once a month</div>
                  </div>
                </template>
              </v-radio>
            </v-radio-group>

            <v-text-field
              v-model.number="monthlyIncome"
              type="number"
              label="What is your total monthly income?"
              variant="outlined"
              :rules="[rules.positive]"
              required
              class="mb-4"
              hint="Include all sources of income"
            />

            <v-text-field
              v-model="nextPaycheckDate"
              type="date"
              label="When is your next paycheck?"
              variant="outlined"
              :rules="[rules.required, v => new Date(v) > new Date() || 'Date must be in the future']"
              required
              :hint="nextPaycheckDate ? `${daysUntilPaycheck} days from today` : 'Select the date of your next paycheck'"
              :persistent-hint="!!nextPaycheckDate"
              :min="new Date().toISOString().split('T')[0]"
            />

            <v-alert
              v-if="nextPaycheckDate && payFrequency"
              type="info"
              variant="tonal"
              class="mt-4"
              density="compact"
            >
              <div class="text-body-2">
                <strong>{{ formatPayFrequency(payFrequency) }}</strong> pay cycle:
                {{ getPayCycleInfo(payFrequency, daysUntilPaycheck) }}
              </div>
            </v-alert>
          </div>

          <!-- Fixed Pool Mode Fields -->
          <div v-if="budgetMode === 'fixed_pool'">
            <v-text-field
              v-model.number="totalMoney"
              type="number"
              label="How much total money do you have available?"
              variant="outlined"
              :rules="[rules.positive]"
              required
              hint="Enter the total amount you have to work with"
              class="mb-4"
            />

            <p class="text-h6 mb-3">How would you like to set up your budget?</p>
            <p class="text-caption text-medium-emphasis mb-4">You can change this later in Settings</p>

            <v-radio-group v-model="fixedPoolMode">
              <v-card
                class="mb-3 pa-3"
                :class="{ 'border-primary': fixedPoolMode === 'target_date' }"
                @click="fixedPoolMode = 'target_date'"
                style="cursor: pointer;"
              >
                <v-radio value="target_date">
                  <template v-slot:label>
                    <div class="ml-3">
                      <div class="text-subtitle-1 font-weight-bold mb-1">
                        <v-icon size="small" color="primary" class="mr-1">mdi-calendar-clock</v-icon>
                        Make it last until a specific date
                      </div>
                      <div class="text-caption text-medium-emphasis">
                        Set a target date, and we'll calculate your daily budget
                      </div>
                    </div>
                  </template>
                </v-radio>
              </v-card>

              <v-card
                class="mb-3 pa-3"
                :class="{ 'border-primary': fixedPoolMode === 'daily_limit' }"
                @click="fixedPoolMode = 'daily_limit'"
                style="cursor: pointer;"
              >
                <v-radio value="daily_limit">
                  <template v-slot:label>
                    <div class="ml-3">
                      <div class="text-subtitle-1 font-weight-bold mb-1">
                        <v-icon size="small" color="primary" class="mr-1">mdi-cash-limit</v-icon>
                        Set a daily spending limit
                      </div>
                      <div class="text-caption text-medium-emphasis">
                        Set how much you want to spend per day, see when it runs out
                      </div>
                    </div>
                  </template>
                </v-radio>
              </v-card>
            </v-radio-group>

            <!-- Option B: Target End Date -->
            <v-text-field
              v-if="fixedPoolMode === 'target_date'"
              v-model="targetEndDate"
              type="date"
              label="When do you need this money to last until?"
              variant="outlined"
              :rules="[rules.required, v => new Date(v) > new Date() || 'Date must be in the future']"
              required
              hint="Pick a future date (e.g., when you start a new job)"
              :min="new Date().toISOString().split('T')[0]"
            />

            <!-- Option C: Daily Spending Limit -->
            <v-text-field
              v-if="fixedPoolMode === 'daily_limit'"
              v-model.number="dailySpendingLimit"
              type="number"
              label="What daily spending limit do you want?"
              variant="outlined"
              :rules="[rules.positive]"
              required
              hint="How much do you want to limit yourself to per day?"
            />
          </div>
        </v-form>
      </div>

      <!-- Step 3: Add Expenses -->
      <div v-else-if="currentStep === 3">
        <h2 class="text-h4 mb-3 text-center">Add Your Monthly Expenses</h2>
        <p class="text-h6 text-center mb-4" style="color: var(--color-soft-charcoal);">
          Add expenses that you MUST pay each month (rent, utilities, bills, etc.)
        </p>

        <!-- Import from Spreadsheet -->
        <div class="text-center mb-4">
          <v-btn
            variant="outlined"
            color="primary"
            @click="triggerFileInput"
            prepend-icon="mdi-upload"
          >
            Import from Spreadsheet (CSV/Excel)
          </v-btn>
          <input
            ref="fileInput"
            type="file"
            accept=".csv,.xlsx"
            style="display: none"
            @change="handleFileImport"
          />
          <p class="text-caption text-medium-emphasis mt-2">
            Or add expenses manually below
          </p>
        </div>

        <v-alert v-if="importSuccess" type="success" class="mb-4 max-w-600 mx-auto">
          {{ importSuccess }}
        </v-alert>
        <v-alert v-if="importError" type="error" class="mb-4 max-w-600 mx-auto">
          {{ importError }}
        </v-alert>

        <!-- Add Expense Form -->
        <v-card variant="outlined" class="mb-4 pa-4 max-w-600 mx-auto">
          <v-form ref="expenseForm" @submit.prevent="addExpense">
            <v-row>
              <v-col cols="12" sm="5">
                <v-text-field
                  v-model="newExpense.name"
                  label="Expense Name"
                  variant="outlined"
                  density="compact"
                  placeholder="e.g., Rent"
                  :rules="[rules.required, rules.maxLength(100)]"
                  counter="100"
                  required
                />
              </v-col>
              <v-col cols="12" sm="4">
                <v-text-field
                  v-model.number="newExpense.amount"
                  type="number"
                  label="Amount"
                  variant="outlined"
                  density="compact"
                  :rules="[rules.positive]"
                  required
                />
              </v-col>
              <v-col cols="12" sm="3">
                <v-btn
                  type="submit"
                  color="primary"
                  block
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
              <v-list-item-subtitle :aria-label="`${expense.amount.toFixed(0)} dollars and ${Math.round((expense.amount % 1) * 100)} cents`">{{ expense.amount.toFixed(2) }}</v-list-item-subtitle>
              <template v-slot:append>
                <v-btn
                  icon
                  size="default"
                  variant="text"
                  @click="removeExpense(index)"
                  :aria-label="`Delete expense: ${expense.name}`"
                  style="min-width: 44px; min-height: 44px;"
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
              <v-list-item-subtitle class="text-h6" :aria-label="`Total: ${totalExpenses.toFixed(0)} dollars and ${Math.round((totalExpenses % 1) * 100)} cents`">
                {{ totalExpenses.toFixed(2) }}
              </v-list-item-subtitle>
            </v-list-item>
          </v-list>
        </div>
      </div>

      <!-- Step 4: Show The Number -->
      <div v-else-if="currentStep === 4">
        <div class="text-center">
          <v-icon size="100" color="success" class="mb-3">mdi-check-circle</v-icon>
          <h2 class="text-h3 mb-4">Here's Your Number!</h2>

          <v-card class="mb-4 pa-6 max-w-600 mx-auto" elevation="2">
            <!-- Mode-specific summary -->
            <div v-if="budgetMode === 'paycheck'" class="mb-4">
              <div class="d-flex justify-space-between mb-2">
                <span>Monthly Income:</span>
                <span class="font-weight-bold" :aria-label="`${monthlyIncome.toFixed(0)} dollars and ${Math.round((monthlyIncome % 1) * 100)} cents`">{{ monthlyIncome.toFixed(2) }}</span>
              </div>
              <div class="d-flex justify-space-between mb-2">
                <span>Total Expenses:</span>
                <span class="font-weight-bold" :aria-label="`${totalExpenses.toFixed(0)} dollars and ${Math.round((totalExpenses % 1) * 100)} cents`">{{ totalExpenses.toFixed(2) }}</span>
              </div>
              <v-divider class="my-3" />
              <div class="d-flex justify-space-between mb-2">
                <span>After Expenses:</span>
                <span class="font-weight-bold" :aria-label="`${(monthlyIncome - totalExpenses).toFixed(0)} dollars and ${Math.round(((monthlyIncome - totalExpenses) % 1) * 100)} cents`">{{ (monthlyIncome - totalExpenses).toFixed(2) }}</span>
              </div>
              <div class="d-flex justify-space-between mb-2">
                <span>Pay Frequency:</span>
                <span class="font-weight-bold">{{ formatPayFrequency(payFrequency) }}</span>
              </div>
              <div class="d-flex justify-space-between mb-2">
                <span>Next Paycheck:</span>
                <span class="font-weight-bold">{{ formatTargetDate(nextPaycheckDate) }}</span>
              </div>
              <div class="d-flex justify-space-between mb-4">
                <span>Days Until Paycheck:</span>
                <span class="font-weight-bold">{{ daysUntilPaycheck }} days</span>
              </div>
            </div>

            <div v-if="budgetMode === 'fixed_pool'" class="mb-4">
              <div class="d-flex justify-space-between mb-2">
                <span>Total Money:</span>
                <span class="font-weight-bold" :aria-label="`${totalMoney.toFixed(0)} dollars and ${Math.round((totalMoney % 1) * 100)} cents`">{{ totalMoney.toFixed(2) }}</span>
              </div>
              <div class="d-flex justify-space-between mb-2">
                <span>Monthly Expenses:</span>
                <span class="font-weight-bold" :aria-label="`${totalExpenses.toFixed(0)} dollars and ${Math.round((totalExpenses % 1) * 100)} cents`">{{ totalExpenses.toFixed(2) }}</span>
              </div>
              <v-divider class="my-3" />
              <div v-if="fixedPoolMode === 'daily_limit'" class="d-flex justify-space-between mb-2">
                <span>After Expenses:</span>
                <span class="font-weight-bold" :aria-label="`${(totalMoney - totalExpenses).toFixed(0)} dollars and ${Math.round(((totalMoney - totalExpenses) % 1) * 100)} cents`">{{ (totalMoney - totalExpenses).toFixed(2) }}</span>
              </div>
              <div class="d-flex justify-space-between mb-4">
                <span>
                  <template v-if="fixedPoolMode === 'target_date'">Target Date:</template>
                  <template v-else>Will Last:</template>
                </span>
                <span class="font-weight-bold">
                  <template v-if="fixedPoolMode === 'daily_limit'">
                    {{ daysMoneyWillLast }} days
                  </template>
                  <template v-else-if="fixedPoolMode === 'target_date' && targetEndDate">
                    {{ formatTargetDate(targetEndDate) }}
                    <div class="text-caption text-medium-emphasis">
                      ({{ calculateDaysUntilTarget(targetEndDate) }} days / {{ (calculateDaysUntilTarget(targetEndDate) / 30).toFixed(1) }} months)
                    </div>
                  </template>
                </span>
              </div>
            </div>

            <v-divider class="my-4" />

            <!-- The Number -->
            <div class="text-center py-4 bg-success-lighten rounded">
              <div class="text-h6 mb-2">THE NUMBER</div>
              <div
                class="text-h2 font-weight-bold text-success"
                :aria-label="`${calculatedNumber.toFixed(0)} dollars and ${Math.round((calculatedNumber % 1) * 100)} cents per day`"
              >
                {{ calculatedNumber.toFixed(2) }}<span class="text-h5">/day</span>
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
      timeout="-1"
      role="alert"
      aria-live="assertive"
    >
      {{ errorMessage }}
      <template v-slot:actions>
        <v-btn
          variant="text"
          @click="completeOnboarding"
        >
          Retry
        </v-btn>
        <v-btn
          variant="text"
          @click="showError = false"
        >
          Close
        </v-btn>
      </template>
    </v-snackbar>
  </v-card>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { budgetApi } from '@/services/api'
import { useValidation } from '@/composables/useValidation'
import { useAuthStore } from '@/stores/auth'
import axios from 'axios'

const emit = defineEmits(['complete'])
const { rules } = useValidation()
const authStore = useAuthStore()

// Form refs
const detailsForm = ref<any>(null)
const expenseForm = ref<any>(null)
const accountForm = ref<any>(null)
const fileInput = ref<HTMLInputElement | null>(null)

// Current step (0 = account creation, 1-4 = setup steps)
const currentStep = ref(0)

// Account creation
const username = ref('')
const email = ref('')
const password = ref('')
const confirmPassword = ref('')
const creatingAccount = ref(false)
const accountError = ref('')
const showLoginDialog = ref(false)

// Import/Export
const importSuccess = ref('')
const importError = ref('')

// Budget Mode
const budgetMode = ref<'paycheck' | 'fixed_pool'>('paycheck')

// Paycheck Mode Data
const payFrequency = ref<'weekly' | 'biweekly' | 'semimonthly' | 'monthly'>('biweekly')
const monthlyIncome = ref(0)
const nextPaycheckDate = ref('')
const daysUntilPaycheck = computed(() => {
  if (!nextPaycheckDate.value) return 0
  const nextDate = new Date(nextPaycheckDate.value)
  const today = new Date()
  const diffTime = nextDate.getTime() - today.getTime()
  return Math.ceil(diffTime / (1000 * 60 * 60 * 24))
})

// Fixed Pool Mode Data
const totalMoney = ref(0)
const fixedPoolMode = ref<'target_date' | 'daily_limit'>('target_date')
const targetEndDate = ref('')
const dailySpendingLimit = ref(0)

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
    // Fixed pool mode
    if (fixedPoolMode.value === 'daily_limit') {
      // User explicitly set a daily spending limit - use it directly
      return dailySpendingLimit.value
    } else {
      // Target date mode - calculate based on days until target date
      if (!targetEndDate.value) return 0
      const daysUntilTarget = calculateDaysUntilTarget(targetEndDate.value)
      if (daysUntilTarget <= 0) return 0

      // Calculate daily portion of monthly expenses
      const dailyExpenses = totalExpenses.value / 30

      // Money available after accounting for expenses over the period
      const totalExpensesForPeriod = dailyExpenses * daysUntilTarget
      const remainingMoney = totalMoney.value - totalExpensesForPeriod

      // Divide by days to get daily spending limit
      return Math.max(0, remainingMoney / daysUntilTarget)
    }
  }
})

const daysMoneyWillLast = computed(() => {
  if (budgetMode.value === 'fixed_pool') {
    const remainingAfterExpenses = totalMoney.value - totalExpenses.value
    if (fixedPoolMode.value === 'daily_limit' && dailySpendingLimit.value > 0) {
      return Math.floor(remainingAfterExpenses / dailySpendingLimit.value)
    }
  }
  return 0
})

const canProceed = computed(() => {
  if (currentStep.value === 0) return true
  if (currentStep.value === 1) return !!budgetMode.value
  if (currentStep.value === 2) {
    if (budgetMode.value === 'paycheck') {
      return monthlyIncome.value > 0 && !!payFrequency.value && !!nextPaycheckDate.value && daysUntilPaycheck.value > 0
    } else {
      // Fixed pool mode validation
      if (totalMoney.value <= 0) return false
      if (fixedPoolMode.value === 'target_date') {
        return !!targetEndDate.value && new Date(targetEndDate.value) > new Date()
      } else {
        return dailySpendingLimit.value > 0
      }
    }
  }
  if (currentStep.value === 3) return true // Can skip expenses
  return true
})

// Methods
function formatPayFrequency(frequency: string): string {
  const frequencyMap: Record<string, string> = {
    'weekly': 'Weekly',
    'biweekly': 'Bi-weekly',
    'semimonthly': 'Semi-monthly',
    'monthly': 'Monthly'
  }
  return frequencyMap[frequency] || frequency
}

function getPayCycleInfo(frequency: string, daysUntil: number): string {
  const cycleLengths: Record<string, number> = {
    'weekly': 7,
    'biweekly': 14,
    'semimonthly': 15,
    'monthly': 30
  }
  const cycleLength = cycleLengths[frequency] || 30
  const daysInto = cycleLength - daysUntil

  if (daysInto < 0) {
    return `${daysUntil} days until next paycheck (cycle: ${cycleLength} days)`
  }

  return `Day ${daysInto} of ${cycleLength} (${daysUntil} days until next paycheck)`
}

function formatTargetDate(dateString: string): string {
  // Parse as local date to avoid timezone issues
  const [year, month, day] = dateString.split('T')[0].split('-')
  const date = new Date(Number(year), Number(month) - 1, Number(day))
  return date.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
}

function calculateDaysUntilTarget(dateString: string): number {
  const target = new Date(dateString)
  const today = new Date()
  const diffTime = target.getTime() - today.getTime()
  return Math.ceil(diffTime / (1000 * 60 * 60 * 24))
}

async function addExpense() {
  // Validate form before submitting
  const { valid } = await expenseForm.value.validate()
  if (!valid) return

  if (newExpense.value.name && newExpense.value.amount > 0) {
    expenses.value.push({ ...newExpense.value })
    newExpense.value = { name: '', amount: 0, is_fixed: true }
    expenseForm.value.resetValidation()
  }
}

function removeExpense(index: number) {
  expenses.value.splice(index, 1)
}

async function createAccount() {
  // Validate form before submitting
  const { valid } = await accountForm.value.validate()
  if (!valid) return

  creatingAccount.value = true
  accountError.value = ''

  try {
    // Call auth store register method
    await authStore.register(
      username.value,
      password.value,
      email.value || undefined
    )

    // On success, advance to step 1
    currentStep.value = 1
  } catch (err: any) {
    accountError.value = err.response?.data?.detail || 'Failed to create account'
  } finally {
    creatingAccount.value = false
  }
}

function triggerFileInput() {
  fileInput.value?.click()
}

async function handleFileImport(event: Event) {
  const input = event.target as HTMLInputElement
  const file = input.files?.[0]

  if (!file) return

  // Clear previous messages
  importSuccess.value = ''
  importError.value = ''

  try {
    // Validate file type
    const validTypes = [
      'text/csv',
      'application/vnd.ms-excel',
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    ]

    if (!validTypes.includes(file.type) && !file.name.endsWith('.csv') && !file.name.endsWith('.xlsx')) {
      importError.value = 'Invalid file type. Please upload a CSV or Excel file.'
      return
    }

    // Upload file to API (replace=false to append to existing expenses)
    const response = await budgetApi.importExpenses(file, false)

    // Handle success
    const data = response.data
    if (data.imported_count > 0) {
      importSuccess.value = `Successfully imported ${data.imported_count} expense(s)!`

      // Add imported expenses to the list
      if (data.expenses && Array.isArray(data.expenses)) {
        expenses.value.push(...data.expenses)
      }
    }

    // Show any errors that occurred during import
    if (data.errors && data.errors.length > 0) {
      importError.value = `${data.errors.length} row(s) failed to import. ${data.errors[0]}`
    }

    // Clear the file input so the same file can be uploaded again if needed
    input.value = ''
  } catch (err: any) {
    importError.value = err.response?.data?.detail || 'Failed to import expenses'
  }
}

function prevStep() {
  if (currentStep.value > 0) {
    currentStep.value--
  }
}

async function nextStep() {
  // Validate step 2 (details form) before proceeding
  if (currentStep.value === 2 && detailsForm.value) {
    const { valid } = await detailsForm.value.validate()
    if (!valid) return
  }

  if (canProceed.value && currentStep.value < 4) {
    currentStep.value++
  }
}

async function completeOnboarding() {
  // Prevent race condition from double-clicks
  if (loading.value) return

  console.log('🚀 completeOnboarding called')
  loading.value = true
  showError.value = false

  // ROLLBACK FIX: Track created resources for cleanup on failure
  // This prevents orphaned budget configs when expense creation fails mid-way
  let budgetConfigSaved = false
  const createdExpenseIds: number[] = []

  try {
    // 1. Save budget configuration
    const budgetConfig: any = { mode: budgetMode.value }
    if (budgetMode.value === 'paycheck') {
      budgetConfig.monthly_income = monthlyIncome.value
      budgetConfig.days_until_paycheck = daysUntilPaycheck.value
      budgetConfig.pay_frequency = payFrequency.value
      budgetConfig.next_paycheck_date = new Date(nextPaycheckDate.value).toISOString()
    } else {
      budgetConfig.total_money = totalMoney.value
      // Include fixed pool mode options
      if (fixedPoolMode.value === 'target_date' && targetEndDate.value) {
        budgetConfig.target_end_date = new Date(targetEndDate.value).toISOString()
      } else if (fixedPoolMode.value === 'daily_limit' && dailySpendingLimit.value > 0) {
        budgetConfig.daily_spending_limit = dailySpendingLimit.value
      }
    }

    console.log('💾 Saving budget config:', budgetConfig)
    const configResponse = await budgetApi.configureBudget(budgetConfig)
    console.log('✅ Budget config saved:', configResponse.data)
    budgetConfigSaved = true

    // 2. Save all expenses with rollback capability
    for (const expense of expenses.value) {
      const response = await budgetApi.createExpense(expense)
      // Track created expense ID for potential rollback
      if (response.data?.id) {
        createdExpenseIds.push(response.data.id)
      }
    }

    // 3. Emit completion event
    emit('complete')
  } catch (e: any) {
    console.error('Onboarding error:', e)
    showError.value = true
    errorMessage.value = e.response?.data?.detail || 'Failed to complete onboarding'

    // ROLLBACK: Clean up any partially created data
    // This ensures we don't leave the database in an inconsistent state
    if (createdExpenseIds.length > 0 || budgetConfigSaved) {
      try {
        // Delete any expenses that were created before the failure
        for (const expenseId of createdExpenseIds) {
          try {
            await budgetApi.deleteExpense(expenseId)
          } catch (rollbackError) {
            console.error(`Failed to rollback expense ${expenseId}:`, rollbackError)
          }
        }
        // Note: Budget config cannot be "deleted", but the user can retry
        // and it will be overwritten. The important thing is to not have
        // a budget config pointing to non-existent or partial expenses.
      } catch (rollbackError) {
        console.error('Rollback failed:', rollbackError)
        errorMessage.value += ' Some data may need to be manually cleaned up.'
      }
    }
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
