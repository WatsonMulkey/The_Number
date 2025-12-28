# Vue 3 in The Number App - A Complete Guide

This lesson explains how Vue 3 works and how it's being used in The Number budgeting app.

## Table of Contents
1. [What is Vue?](#what-is-vue)
2. [Vue Components](#vue-components)
3. [The Composition API](#the-composition-api)
4. [Reactivity System](#reactivity-system)
5. [Component Structure](#component-structure)
6. [Real Examples from The Number App](#real-examples)
7. [State Management with Pinia](#state-management)
8. [Vue Router](#vue-router)
9. [Common Patterns](#common-patterns)

---

## What is Vue?

Vue is a **progressive JavaScript framework** for building user interfaces. Think of it as a system that:
- Automatically updates the webpage when your data changes
- Organizes your UI into reusable components
- Makes it easy to handle user interactions

**Why Vue for The Number app?**
- Simple syntax that's easy to read and maintain
- Excellent reactivity system (perfect for updating "The Number" in real-time)
- Great mobile support (important for PWA functionality)
- Vuetify provides beautiful Material Design components out of the box

---

## Vue Components

Every `.vue` file is a **Single File Component (SFC)** with three sections:

```vue
<template>
  <!-- HTML structure goes here -->
</template>

<script setup lang="ts">
  // JavaScript/TypeScript logic goes here
</script>

<style scoped>
  /* CSS styling goes here */
</style>
```

### Example: NumberDisplay.vue

```vue
<template>
  <v-card class="number-display">
    <div class="the-number">{{ budgetStore.budgetNumber.the_number.toFixed(2) }}</div>
    <div class="label">/day</div>
  </v-card>
</template>

<script setup lang="ts">
import { useBudgetStore } from '@/stores/budget'

const budgetStore = useBudgetStore()
</script>

<style scoped>
.the-number {
  font-size: 72px;
  font-weight: bold;
}
</style>
```

**What's happening here:**
1. `<template>` - Defines what the user sees
2. `{{ budgetStore.budgetNumber.the_number.toFixed(2) }}` - Vue's **interpolation** syntax - automatically displays data
3. `<script setup>` - Composition API syntax (more on this below)
4. `<style scoped>` - Styles only apply to this component

---

## The Composition API

The Number app uses Vue 3's **Composition API** with `<script setup>` syntax. This is the modern way to write Vue.

### Old Way (Options API):
```javascript
export default {
  data() {
    return {
      count: 0
    }
  },
  methods: {
    increment() {
      this.count++
    }
  }
}
```

### New Way (Composition API):
```javascript
import { ref } from 'vue'

const count = ref(0)

function increment() {
  count.value++
}
```

**Why Composition API is better:**
- More logical code organization
- Better TypeScript support
- Easier to reuse logic
- No need for `this` keyword
- More flexible and composable

---

## Reactivity System

Vue's **reactivity** means the UI automatically updates when data changes.

### `ref()` - Reactive Primitives

For simple values (numbers, strings, booleans):

```typescript
import { ref } from 'vue'

// Create a reactive number
const currentStep = ref(0)

// Read the value (in JavaScript)
console.log(currentStep.value) // 0

// Update the value (UI updates automatically!)
currentStep.value = 1
```

**In template, no `.value` needed:**
```vue
<template>
  <div>Current Step: {{ currentStep }}</div>
  <button @click="currentStep++">Next</button>
</template>
```

### Example from Onboarding.vue:

```typescript
// State for account creation
const username = ref('')
const email = ref('')
const password = ref('')
const creatingAccount = ref(false)

// When user types in form, these update automatically
// When we set creatingAccount to true, loading spinner shows
async function createAccount() {
  creatingAccount.value = true  // Shows loading spinner
  await authStore.register(username.value, password.value)
  creatingAccount.value = false // Hides loading spinner
}
```

### `computed()` - Calculated Values

For values that depend on other data:

```typescript
import { ref, computed } from 'vue'

const monthlyIncome = ref(3000)
const totalExpenses = ref(2000)

// Automatically recalculates when dependencies change
const remainingMoney = computed(() => {
  return monthlyIncome.value - totalExpenses.value
})

// remainingMoney is now 1000
// If monthlyIncome changes to 3500, remainingMoney becomes 1500 automatically!
```

### Real Example from Dashboard.vue:

```typescript
const totalExpenses = computed(() =>
  expenses.value.reduce((sum, exp) => sum + exp.amount, 0)
)

const daysUntilPaycheck = computed(() => {
  if (!nextPaycheckDate.value) return 0
  const nextDate = new Date(nextPaycheckDate.value)
  const today = new Date()
  const diffTime = nextDate.getTime() - today.getTime()
  return Math.ceil(diffTime / (1000 * 60 * 60 * 24))
})
```

**Why use `computed()` instead of a function?**
- Vue caches the result
- Only recalculates when dependencies change
- More efficient for expensive calculations

---

## Component Structure

### Template Syntax

#### 1. **Interpolation** - Display data
```vue
<div>{{ message }}</div>
<div>${{ amount.toFixed(2) }}</div>
```

#### 2. **Directives** - Special Vue attributes

**v-model** - Two-way data binding (form inputs):
```vue
<template>
  <input v-model="username" />
  <p>Hello, {{ username }}!</p>
</template>

<script setup lang="ts">
import { ref } from 'vue'
const username = ref('')
// When user types, username updates. When username changes, input updates.
</script>
```

**v-if / v-else** - Conditional rendering:
```vue
<div v-if="currentStep === 0">
  <!-- Account creation -->
</div>
<div v-else-if="currentStep === 1">
  <!-- Budget mode selection -->
</div>
<div v-else>
  <!-- Other steps -->
</div>
```

**v-for** - Loop through arrays:
```vue
<v-list-item
  v-for="(expense, index) in expenses"
  :key="index"
>
  <v-list-item-title>{{ expense.name }}</v-list-item-title>
  <v-list-item-subtitle>{{ expense.amount.toFixed(2) }}</v-list-item-subtitle>
</v-list-item>
```

**v-show** - Toggle visibility (element stays in DOM):
```vue
<v-alert v-show="showError" type="error">
  {{ errorMessage }}
</v-alert>
```

**@click / @submit** - Event handlers:
```vue
<v-btn @click="nextStep">Next</v-btn>
<v-form @submit.prevent="addExpense">
  <!-- .prevent is like e.preventDefault() -->
</v-form>
```

**:disabled / :loading** - Bind attributes dynamically:
```vue
<v-btn
  :disabled="!canProceed"
  :loading="loading"
  @click="submit"
>
  Submit
</v-btn>
```

### Props and Emits

**Passing data to child components:**

Parent (Dashboard.vue):
```vue
<template>
  <NumberDisplay :budget-number="budgetStore.budgetNumber" />
</template>
```

Child (NumberDisplay.vue):
```vue
<script setup lang="ts">
interface Props {
  budgetNumber: BudgetNumber
}

const props = defineProps<Props>()
// Now can use props.budgetNumber
</script>
```

**Sending data from child to parent:**

Child (Onboarding.vue):
```vue
<script setup lang="ts">
const emit = defineEmits(['complete'])

function finish() {
  emit('complete')  // Tell parent we're done
}
</script>
```

Parent (App.vue):
```vue
<template>
  <Onboarding @complete="handleComplete" />
</template>

<script setup lang="ts">
function handleComplete() {
  console.log('Onboarding complete!')
}
</script>
```

---

## Real Examples from The Number App

### Example 1: Dashboard Carousel (Dashboard.vue)

```vue
<template>
  <!-- v-model binds currentSlide - when slide changes, this updates -->
  <v-window v-model="currentSlide" class="main-carousel mb-8" show-arrows>

    <!-- Slide 1: The Number Display -->
    <v-window-item :value="0">
      <NumberDisplay
        :budget-number="budgetStore.budgetNumber"
        :loading="budgetStore.loading"
      />
    </v-window-item>

    <!-- Slide 2: Budget Details -->
    <v-window-item :value="1">
      <v-card>
        <div class="detail-item">
          <div class="detail-label">Mode</div>
          <!-- Conditional rendering with ternary operator -->
          <div class="detail-value">
            {{ budgetStore.budgetNumber.mode === 'paycheck' ? 'Paycheck' : 'Fixed Pool' }}
          </div>
        </div>
      </v-card>
    </v-window-item>

    <!-- Slide 3: Recent Transactions -->
    <v-window-item :value="2">
      <v-list>
        <!-- Loop through transactions -->
        <v-list-item
          v-for="txn in budgetStore.transactions.slice(0, 5)"
          :key="txn.id"
        >
          <v-list-item-title>{{ txn.description }}</v-list-item-title>
          <v-list-item-subtitle>${{ txn.amount.toFixed(2) }}</v-list-item-subtitle>
        </v-list-item>
      </v-list>
    </v-window-item>
  </v-window>

  <!-- Slide indicators -->
  <div class="slide-indicators">
    <v-btn
      v-for="n in 3"
      :key="n"
      @click="currentSlide = n - 1"
      :color="currentSlide === n - 1 ? 'primary' : 'grey'"
    >
      <v-icon>{{ currentSlide === n - 1 ? 'mdi-circle' : 'mdi-circle-outline' }}</v-icon>
    </v-btn>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useBudgetStore } from '@/stores/budget'

const budgetStore = useBudgetStore()
const currentSlide = ref(0)

// Run when component is added to the page
onMounted(() => {
  budgetStore.fetchBudgetNumber()
})
</script>
```

**What's happening:**
1. `currentSlide` is a reactive variable (starts at 0)
2. `v-model="currentSlide"` makes the carousel sync with currentSlide
3. When user swipes, currentSlide updates automatically
4. Indicators use `currentSlide` to show which slide is active
5. When you click an indicator, it sets `currentSlide` and carousel moves

### Example 2: Form Validation (Onboarding.vue)

```vue
<template>
  <v-form ref="accountForm" @submit.prevent="createAccount">
    <v-text-field
      v-model="username"
      label="Username"
      variant="outlined"
      :rules="[rules.required, rules.username]"
      required
    />

    <v-text-field
      v-model="password"
      label="Password"
      variant="outlined"
      :rules="[rules.required, rules.minPassword]"
      type="password"
      required
    />

    <v-btn type="submit" :loading="creatingAccount">
      Create Account
    </v-btn>
  </v-form>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useValidation } from '@/composables/useValidation'

const { rules } = useValidation()
const accountForm = ref<any>(null)

const username = ref('')
const password = ref('')
const creatingAccount = ref(false)

async function createAccount() {
  // Validate form before submitting
  const { valid } = await accountForm.value.validate()
  if (!valid) return

  creatingAccount.value = true
  // Make API call...
  creatingAccount.value = false
}
</script>
```

**What's happening:**
1. `v-model="username"` - Input value binds to username variable
2. `:rules="[...]"` - Array of validation functions
3. `@submit.prevent` - Prevent page reload, call createAccount instead
4. `:loading="creatingAccount"` - Shows spinner when true
5. `accountForm.value.validate()` - Checks all rules before submitting

### Example 3: Computed Properties (Onboarding.vue)

```typescript
const budgetMode = ref<'paycheck' | 'fixed_pool'>('paycheck')
const monthlyIncome = ref(0)
const totalExpenses = ref(0)
const expenses = ref([])
const daysUntilPaycheck = ref(0)

// Automatically calculates total expenses
const totalExpenses = computed(() =>
  expenses.value.reduce((sum, exp) => sum + exp.amount, 0)
)

// Automatically calculates "The Number"
const calculatedNumber = computed(() => {
  if (budgetMode.value === 'paycheck') {
    const remaining = monthlyIncome.value - totalExpenses.value
    return daysUntilPaycheck.value > 0
      ? Math.max(0, remaining / daysUntilPaycheck.value)
      : 0
  } else {
    // Fixed pool calculation...
  }
})

// Determines if user can proceed to next step
const canProceed = computed(() => {
  if (currentStep.value === 1) return !!budgetMode.value
  if (currentStep.value === 2) {
    return monthlyIncome.value > 0 && daysUntilPaycheck.value > 0
  }
  return true
})
```

**What's happening:**
1. When user adds/removes expenses, `totalExpenses` recalculates
2. When any input changes, `calculatedNumber` recalculates
3. `canProceed` determines if "Next" button is enabled
4. All this happens **automatically** - no manual updates needed!

---

## State Management with Pinia

Pinia is Vue's official state management library. Think of it as a **shared data store** that multiple components can access.

### Example: Budget Store (stores/budget.ts)

```typescript
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useBudgetStore = defineStore('budget', () => {
  // State (like component's ref)
  const budgetNumber = ref<BudgetNumber | null>(null)
  const transactions = ref<Transaction[]>([])
  const loading = ref(false)

  // Computed (like component's computed)
  const isConfigured = computed(() => !!budgetNumber.value)

  // Actions (like component's functions)
  async function fetchBudgetNumber() {
    loading.value = true
    try {
      const response = await budgetApi.getNumber()
      budgetNumber.value = response.data
    } catch (e) {
      console.error(e)
    } finally {
      loading.value = false
    }
  }

  async function recordTransaction(transaction: any) {
    await budgetApi.createTransaction(transaction)
    await fetchBudgetNumber() // Refresh the number
    await fetchTransactions(10)
  }

  // Return everything that components can use
  return {
    budgetNumber,
    transactions,
    loading,
    isConfigured,
    fetchBudgetNumber,
    recordTransaction
  }
})
```

### Using the Store in Components:

```vue
<script setup lang="ts">
import { useBudgetStore } from '@/stores/budget'

const budgetStore = useBudgetStore()

// Access state
console.log(budgetStore.budgetNumber)
console.log(budgetStore.transactions)

// Call actions
budgetStore.fetchBudgetNumber()
budgetStore.recordTransaction({ amount: 50, description: 'Lunch' })
</script>

<template>
  <!-- Use in template -->
  <div>{{ budgetStore.budgetNumber.the_number }}</div>
</template>
```

**Why use Pinia?**
- Share data between components without props drilling
- Centralized business logic
- Persist data across route changes
- DevTools support for debugging

---

## Vue Router

Handles navigation between different "pages" (views) in a Single Page Application.

### Routes Configuration (router/index.ts):

```typescript
const routes = [
  {
    path: '/',
    name: 'dashboard',
    component: () => import('@/views/Dashboard.vue')
  },
  {
    path: '/transactions',
    name: 'transactions',
    component: () => import('@/views/Transactions.vue')
  },
  {
    path: '/settings',
    name: 'settings',
    component: () => import('@/views/Settings.vue')
  }
]
```

### Navigation:

**Using router-link (like `<a>` tags):**
```vue
<router-link to="/">Dashboard</router-link>
<router-link to="/transactions">Transactions</router-link>
```

**Programmatic navigation:**
```typescript
import { useRouter } from 'vue-router'

const router = useRouter()

function goToSettings() {
  router.push('/settings')
}
```

**The Number app uses NavigationRail.vue:**
```vue
<v-list-item
  v-for="item in navItems"
  :key="item.path"
  :to="item.path"
  router
>
  <v-icon>{{ item.icon }}</v-icon>
  <v-list-item-title>{{ item.title }}</v-list-item-title>
</v-list-item>
```

---

## Common Patterns

### 1. Lifecycle Hooks

Run code at specific times in a component's life:

```typescript
import { onMounted, onUnmounted, watch } from 'vue'

// Run once when component is added to page
onMounted(() => {
  console.log('Component mounted!')
  budgetStore.fetchBudgetNumber()
})

// Run when component is removed
onUnmounted(() => {
  console.log('Component unmounted!')
  // Clean up timers, listeners, etc.
})

// Watch for changes to a value
watch(currentSlide, (newValue, oldValue) => {
  console.log(`Slide changed from ${oldValue} to ${newValue}`)
})
```

### 2. Template Refs

Access DOM elements or child components:

```vue
<template>
  <v-form ref="accountForm">
    <!-- form fields -->
  </v-form>
  <input ref="fileInput" type="file" style="display: none" />
</template>

<script setup lang="ts">
import { ref } from 'vue'

const accountForm = ref<any>(null)
const fileInput = ref<HTMLInputElement | null>(null)

function triggerFileInput() {
  fileInput.value?.click() // Access the DOM element
}

async function submit() {
  const { valid } = await accountForm.value.validate() // Call component method
}
</script>
```

### 3. Async Operations with Loading States

```typescript
const loading = ref(false)
const error = ref('')

async function saveData() {
  loading.value = true
  error.value = ''

  try {
    await api.save(data)
  } catch (e: any) {
    error.value = e.message
  } finally {
    loading.value = false // Always runs, even if error
  }
}
```

```vue
<template>
  <v-btn :loading="loading" @click="saveData">Save</v-btn>
  <v-alert v-if="error" type="error">{{ error }}</v-alert>
</template>
```

### 4. Conditional Classes and Styles

```vue
<template>
  <!-- Bind classes dynamically -->
  <div :class="{ 'active': isActive, 'disabled': isDisabled }">

  <!-- Bind inline styles -->
  <div :style="{ color: textColor, fontSize: fontSize + 'px' }">

  <!-- Array of classes -->
  <div :class="['base-class', { 'highlight': isHighlighted }]">
</template>

<script setup lang="ts">
const isActive = ref(true)
const isDisabled = ref(false)
const textColor = ref('blue')
const fontSize = ref(16)
</script>
```

---

## How It All Works Together in The Number App

```
User Types in Form
       ↓
v-model Updates Reactive Variable (ref)
       ↓
Computed Properties Recalculate Automatically
       ↓
Template Re-renders with New Values
       ↓
User Sees Updated UI Instantly
```

### Example Flow: Recording a Transaction

1. **User enters amount in form** → `newTransaction.amount` updates via `v-model`
2. **User clicks "Add"** → `@click="recordTransaction"` fires
3. **recordTransaction() runs:**
   ```typescript
   async function recordTransaction() {
     await budgetStore.recordTransaction(newTransaction.value)
     newTransaction.value = { amount: 0, description: '' } // Clear form
   }
   ```
4. **Store action makes API call** → Backend saves transaction
5. **Store refreshes data:**
   ```typescript
   await fetchBudgetNumber() // Get new "The Number"
   await fetchTransactions() // Get updated transaction list
   ```
6. **Reactive data updates** → All components using the store re-render
7. **Dashboard shows new number** → `budgetStore.budgetNumber.the_number` changed
8. **Transaction list updates** → New transaction appears in list

All of this happens **automatically** thanks to Vue's reactivity system!

---

## Key Takeaways

1. **Everything is Reactive** - When data changes, UI updates automatically
2. **Components are Modular** - Each `.vue` file is self-contained
3. **Composition API is Powerful** - `ref()`, `computed()`, and functions organize logic clearly
4. **Pinia Shares State** - Multiple components can access the same data
5. **Template Syntax is Declarative** - Describe what you want, Vue handles the how
6. **TypeScript Adds Safety** - Catch errors before runtime

## Next Steps

- Experiment with the Dashboard carousel - add a 4th slide
- Create a new component in `frontend/src/components/`
- Add a new computed property to calculate weekly spending
- Try modifying the NumberDisplay component styling
- Add a new route to the router

**Remember:** Vue's reactivity means you describe *what* the UI should look like based on data, and Vue figures out *how* to update it. This is the core concept that makes Vue powerful!
