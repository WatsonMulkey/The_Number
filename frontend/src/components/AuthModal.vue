<template>
  <v-dialog
    v-model="isOpen"
    max-width="500"
    persistent
    role="dialog"
    :aria-labelledby="'auth-modal-title'"
  >
    <v-card>
      <v-card-title
        id="auth-modal-title"
        class="text-h5 pa-6 text-center"
        style="background-color: #E9F5DB;"
      >
        <div>
          <v-icon size="48" color="primary" class="mb-2" aria-hidden="true">
            mdi-account-circle
          </v-icon>
          <div style="color: #2d5016;">{{ modalTitle }}</div>
        </div>
      </v-card-title>

      <v-card-text class="pa-6">
        <!-- Login/Register Form -->
        <v-form v-if="mode === 'login' || mode === 'register'" ref="form" @submit.prevent="handleSubmit">
          <v-text-field
            v-model="username"
            label="Username"
            variant="outlined"
            :rules="usernameRules"
            class="mb-3"
            autofocus
          />

          <v-text-field
            v-if="mode === 'register'"
            v-model="email"
            label="Email (optional)"
            variant="outlined"
            type="email"
            :rules="emailRules"
            class="mb-3"
          />

          <v-text-field
            v-model="password"
            label="Password"
            variant="outlined"
            :type="showPassword ? 'text' : 'password'"
            :rules="mode === 'login' ? loginPasswordRules : registerPasswordRules"
            class="mb-3"
          >
            <template v-slot:append-inner>
              <v-icon
                @click="showPassword = !showPassword"
                @keydown.enter="showPassword = !showPassword"
                @keydown.space.prevent="showPassword = !showPassword"
                style="cursor: pointer;"
                role="button"
                tabindex="0"
                :aria-label="showPassword ? 'Hide password' : 'Show password'"
              >
                {{ showPassword ? 'mdi-eye-off' : 'mdi-eye' }}
              </v-icon>
            </template>
          </v-text-field>

          <!-- Password Strength Indicator (Registration only) -->
          <div v-if="mode === 'register' && password" class="mb-3">
            <div class="text-caption mb-1">Password Strength:</div>
            <v-progress-linear
              :model-value="passwordStrength"
              :color="passwordStrengthColor"
              height="6"
              rounded
            />
            <div class="text-caption text-medium-emphasis mt-1">
              {{ passwordStrengthText }}
            </div>
          </div>

          <v-alert
            v-if="authStore.error"
            type="error"
            variant="tonal"
            class="mb-3"
            role="alert"
            aria-live="assertive"
          >
            {{ authStore.error }}
          </v-alert>

          <v-btn
            type="submit"
            color="primary"
            block
            size="large"
            :loading="authStore.loading"
            class="mb-3"
          >
            {{ mode === 'login' ? 'Login' : 'Register' }}
          </v-btn>

          <v-divider class="mb-3" />

          <div class="text-center">
            <v-btn
              variant="text"
              @click="toggleMode"
            >
              {{ mode === 'login' ? "Don't have an account? Register" : 'Already have an account? Login' }}
            </v-btn>
          </div>
        </v-form>
      </v-card-text>

      <v-card-actions class="pa-4">
        <v-spacer />
        <v-btn
          variant="text"
          @click="handleClose"
          :disabled="authStore.loading"
        >
          Cancel
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script setup lang="ts">
import { ref, watch, computed } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useValidation } from '@/composables/useValidation'

const props = defineProps<{
  modelValue: boolean
}>()

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  'success': []
}>()

const authStore = useAuthStore()
const { rules } = useValidation()

// Modal state
const isOpen = ref(props.modelValue)
const mode = ref<'login' | 'register'>('login')

// Login/Register form
const username = ref('')
const email = ref('')
const password = ref('')
const showPassword = ref(false)
const form = ref<any>(null)

// Validation rules - using common validation composable
const usernameRules = [rules.username]

const emailRules = [
  (v: string) => !v || /.+@.+\..+/.test(v) || 'Email must be valid'
]

const loginPasswordRules = [rules.required]

// Strong password requirements for registration and reset
const registerPasswordRules = [
  (v: string) => !!v || 'Password is required',
  (v: string) => v.length >= 8 || 'Password must be at least 8 characters',
  (v: string) => /[A-Z]/.test(v) || 'Password must contain at least one uppercase letter',
  (v: string) => /[a-z]/.test(v) || 'Password must contain at least one lowercase letter',
  (v: string) => /[0-9]/.test(v) || 'Password must contain at least one number'
]

// Password strength calculation
const passwordStrength = computed(() => {
  if (!password.value) return 0

  let strength = 0
  const pwd = password.value

  // Length contribution (max 40 points)
  if (pwd.length >= 8) strength += 20
  if (pwd.length >= 12) strength += 10
  if (pwd.length >= 16) strength += 10

  // Character type contributions (15 points each)
  if (/[a-z]/.test(pwd)) strength += 15
  if (/[A-Z]/.test(pwd)) strength += 15
  if (/[0-9]/.test(pwd)) strength += 15
  if (/[^a-zA-Z0-9]/.test(pwd)) strength += 20 // Special characters

  return Math.min(strength, 100)
})

const passwordStrengthColor = computed(() => {
  const strength = passwordStrength.value
  if (strength < 40) return 'error'
  if (strength < 70) return 'warning'
  return 'success'
})

const passwordStrengthText = computed(() => {
  const strength = passwordStrength.value
  if (strength < 40) return 'Weak - Add more characters and variety'
  if (strength < 70) return 'Fair - Consider adding special characters'
  return 'Strong'
})

// Modal title based on mode
const modalTitle = computed(() => {
  return mode.value === 'login' ? 'Welcome Back!' : 'Create Account'
})

watch(() => props.modelValue, (newVal) => {
  isOpen.value = newVal
  if (newVal) {
    // Reset all form fields when opened
    mode.value = 'login'
    username.value = ''
    email.value = ''
    password.value = ''
    showPassword.value = false
    authStore.clearError()
  }
})

watch(isOpen, (newVal) => {
  emit('update:modelValue', newVal)
})

function toggleMode() {
  mode.value = mode.value === 'login' ? 'register' : 'login'
  // Clear password for security when switching modes
  password.value = ''
  showPassword.value = false
  authStore.clearError()
}

async function handleSubmit() {
  const { valid } = await form.value.validate()
  if (!valid) return

  try {
    if (mode.value === 'login') {
      await authStore.login(username.value, password.value)
    } else {
      await authStore.register(username.value, password.value, email.value || undefined)
    }

    // Success - close modal and emit success event
    isOpen.value = false
    emit('success')
  } catch (err) {
    // Error is handled in the store and displayed via v-alert
  }
}

function handleClose() {
  if (!authStore.loading) {
    isOpen.value = false
  }
}
</script>

<style scoped>
/* No additional styles needed - using Vuetify defaults */
</style>
