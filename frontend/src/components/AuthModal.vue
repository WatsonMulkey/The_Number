<template>
  <v-dialog v-model="isOpen" max-width="500" persistent>
    <v-card>
      <v-card-title class="text-h5 pa-6 text-center" style="background-color: #E9F5DB;">
        <div>
          <v-icon size="48" color="primary" class="mb-2">
            {{ mode === 'forgot' || mode === 'reset' ? 'mdi-lock-reset' : 'mdi-account-circle' }}
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
            :append-inner-icon="showPassword ? 'mdi-eye-off' : 'mdi-eye'"
            @click:append-inner="showPassword = !showPassword"
          >
            <template v-slot:append-inner>
              <v-icon
                @click="showPassword = !showPassword"
                style="cursor: pointer;"
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

          <!-- Forgot Password Link (Login only) -->
          <div v-if="mode === 'login'" class="text-center mb-3">
            <v-btn
              variant="text"
              size="small"
              @click="mode = 'forgot'"
            >
              Forgot Password?
            </v-btn>
          </div>

          <v-alert v-if="authStore.error" type="error" variant="tonal" class="mb-3">
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

        <!-- Forgot Password Form -->
        <v-form v-if="mode === 'forgot'" ref="forgotForm" @submit.prevent="handleForgotPassword">
          <p class="text-body-2 text-medium-emphasis mb-4">
            Enter your username to receive a password reset token.
          </p>

          <v-text-field
            v-model="forgotUsername"
            label="Username"
            variant="outlined"
            :rules="usernameRules"
            class="mb-3"
            autofocus
          />

          <v-alert v-if="resetError" type="error" variant="tonal" class="mb-3">
            {{ resetError }}
          </v-alert>

          <v-btn
            type="submit"
            color="primary"
            block
            size="large"
            :loading="resetLoading"
            class="mb-3"
          >
            Request Reset Token
          </v-btn>

          <v-divider class="mb-3" />

          <div class="text-center">
            <v-btn
              variant="text"
              @click="mode = 'login'"
            >
              Back to Login
            </v-btn>
          </div>
        </v-form>

        <!-- Reset Password Form -->
        <v-form v-if="mode === 'reset'" ref="resetForm" @submit.prevent="handleResetPassword">
          <v-alert type="info" variant="tonal" class="mb-4">
            <div class="text-subtitle-2 mb-2">Your reset token:</div>
            <div class="text-mono text-caption" style="word-break: break-all;">
              {{ resetToken }}
            </div>
            <div class="text-caption mt-2">Copy this token - you'll need it to reset your password.</div>
          </v-alert>

          <v-text-field
            v-model="resetTokenInput"
            label="Reset Token"
            variant="outlined"
            class="mb-3"
            hint="Paste the token shown above"
          />

          <v-text-field
            v-model="newPassword"
            label="New Password"
            variant="outlined"
            :type="showPassword ? 'text' : 'password'"
            :rules="registerPasswordRules"
            class="mb-3"
            :append-inner-icon="showPassword ? 'mdi-eye-off' : 'mdi-eye'"
            @click:append-inner="showPassword = !showPassword"
          >
            <template v-slot:append-inner>
              <v-icon
                @click="showPassword = !showPassword"
                style="cursor: pointer;"
              >
                {{ showPassword ? 'mdi-eye-off' : 'mdi-eye' }}
              </v-icon>
            </template>
          </v-text-field>

          <!-- Password Strength Indicator -->
          <div v-if="newPassword" class="mb-3">
            <div class="text-caption mb-1">Password Strength:</div>
            <v-progress-linear
              :model-value="newPasswordStrength"
              :color="newPasswordStrengthColor"
              height="6"
              rounded
            />
            <div class="text-caption text-medium-emphasis mt-1">
              {{ newPasswordStrengthText }}
            </div>
          </div>

          <v-alert v-if="resetError" type="error" variant="tonal" class="mb-3">
            {{ resetError }}
          </v-alert>

          <v-alert v-if="resetSuccess" type="success" variant="tonal" class="mb-3">
            {{ resetSuccess }}
          </v-alert>

          <v-btn
            type="submit"
            color="primary"
            block
            size="large"
            :loading="resetLoading"
            class="mb-3"
          >
            Reset Password
          </v-btn>

          <v-divider class="mb-3" />

          <div class="text-center">
            <v-btn
              variant="text"
              @click="mode = 'login'"
            >
              Back to Login
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
import { authApi } from '@/services/api'

const props = defineProps<{
  modelValue: boolean
}>()

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  'success': []
}>()

const authStore = useAuthStore()

// Modal state
const isOpen = ref(props.modelValue)
const mode = ref<'login' | 'register' | 'forgot' | 'reset'>('login')

// Login/Register form
const username = ref('')
const email = ref('')
const password = ref('')
const showPassword = ref(false)
const form = ref<any>(null)

// Password reset form
const forgotUsername = ref('')
const forgotForm = ref<any>(null)
const resetToken = ref('')
const resetTokenInput = ref('')
const newPassword = ref('')
const resetForm = ref<any>(null)
const resetLoading = ref(false)
const resetError = ref('')
const resetSuccess = ref('')

// Validation rules
const usernameRules = [
  (v: string) => !!v || 'Username is required',
  (v: string) => v.length >= 3 || 'Username must be at least 3 characters',
  (v: string) => /^[a-zA-Z0-9_-]+$/.test(v) || 'Username can only contain letters, numbers, hyphens, and underscores'
]

const emailRules = [
  (v: string) => !v || /.+@.+\..+/.test(v) || 'Email must be valid'
]

const loginPasswordRules = [
  (v: string) => !!v || 'Password is required'
]

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

// New password strength (for reset password form)
const newPasswordStrength = computed(() => {
  if (!newPassword.value) return 0

  let strength = 0
  const pwd = newPassword.value

  if (pwd.length >= 8) strength += 20
  if (pwd.length >= 12) strength += 10
  if (pwd.length >= 16) strength += 10

  if (/[a-z]/.test(pwd)) strength += 15
  if (/[A-Z]/.test(pwd)) strength += 15
  if (/[0-9]/.test(pwd)) strength += 15
  if (/[^a-zA-Z0-9]/.test(pwd)) strength += 20

  return Math.min(strength, 100)
})

const newPasswordStrengthColor = computed(() => {
  const strength = newPasswordStrength.value
  if (strength < 40) return 'error'
  if (strength < 70) return 'warning'
  return 'success'
})

const newPasswordStrengthText = computed(() => {
  const strength = newPasswordStrength.value
  if (strength < 40) return 'Weak - Add more characters and variety'
  if (strength < 70) return 'Fair - Consider adding special characters'
  return 'Strong'
})

// Modal title based on mode
const modalTitle = computed(() => {
  switch (mode.value) {
    case 'login':
      return 'Welcome Back!'
    case 'register':
      return 'Create Account'
    case 'forgot':
      return 'Forgot Password'
    case 'reset':
      return 'Reset Password'
    default:
      return 'Welcome Back!'
  }
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
    forgotUsername.value = ''
    resetToken.value = ''
    resetTokenInput.value = ''
    newPassword.value = ''
    resetError.value = ''
    resetSuccess.value = ''
    authStore.clearError()
  }
})

watch(isOpen, (newVal) => {
  emit('update:modelValue', newVal)
})

function toggleMode() {
  mode.value = mode.value === 'login' ? 'register' : 'login'
  authStore.clearError()
  resetError.value = ''
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

async function handleForgotPassword() {
  const { valid } = await forgotForm.value.validate()
  if (!valid) return

  resetLoading.value = true
  resetError.value = ''

  try {
    const response = await authApi.forgotPassword({
      username: forgotUsername.value
    })

    // Store the reset token and show it to the user
    resetToken.value = response.data.reset_token
    resetTokenInput.value = response.data.reset_token // Pre-fill for convenience

    // Switch to reset password mode
    mode.value = 'reset'
  } catch (err: any) {
    resetError.value = err.response?.data?.detail || 'Failed to generate reset token'
  } finally {
    resetLoading.value = false
  }
}

async function handleResetPassword() {
  const { valid } = await resetForm.value.validate()
  if (!valid) return

  resetLoading.value = true
  resetError.value = ''
  resetSuccess.value = ''

  try {
    const response = await authApi.resetPassword({
      reset_token: resetTokenInput.value,
      new_password: newPassword.value
    })

    resetSuccess.value = response.data.message

    // Auto-redirect to login after 2 seconds
    setTimeout(() => {
      mode.value = 'login'
      resetSuccess.value = ''
    }, 2000)
  } catch (err: any) {
    resetError.value = err.response?.data?.detail || 'Failed to reset password'
  } finally {
    resetLoading.value = false
  }
}

function handleClose() {
  if (!authStore.loading && !resetLoading.value) {
    isOpen.value = false
  }
}
</script>

<style scoped>
/* No additional styles needed - using Vuetify defaults */
</style>
