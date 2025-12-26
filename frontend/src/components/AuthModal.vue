<template>
  <v-dialog v-model="isOpen" max-width="500" persistent>
    <v-card>
      <v-card-title class="text-h5 pa-6 text-center" style="background-color: #E9F5DB;">
        <div>
          <v-icon size="48" color="primary" class="mb-2">mdi-account-circle</v-icon>
          <div style="color: #2d5016;">{{ isLoginMode ? 'Welcome Back!' : 'Create Account' }}</div>
        </div>
      </v-card-title>

      <v-card-text class="pa-6">
        <v-form ref="form" @submit.prevent="handleSubmit">
          <v-text-field
            v-model="username"
            label="Username"
            variant="outlined"
            :rules="[v => !!v || 'Username is required', v => v.length >= 3 || 'Username must be at least 3 characters']"
            class="mb-3"
            autofocus
          />

          <v-text-field
            v-if="!isLoginMode"
            v-model="email"
            label="Email (optional)"
            variant="outlined"
            type="email"
            class="mb-3"
          />

          <v-text-field
            v-model="password"
            label="Password"
            variant="outlined"
            :type="showPassword ? 'text' : 'password'"
            :rules="[v => !!v || 'Password is required', v => v.length >= 6 || 'Password must be at least 6 characters']"
            class="mb-3"
            :append-inner-icon="showPassword ? 'mdi-eye-off' : 'mdi-eye'"
            @click:append-inner="showPassword = !showPassword"
          />

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
            {{ isLoginMode ? 'Login' : 'Register' }}
          </v-btn>

          <v-divider class="mb-3" />

          <div class="text-center">
            <v-btn
              variant="text"
              @click="toggleMode"
            >
              {{ isLoginMode ? "Don't have an account? Register" : 'Already have an account? Login' }}
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
import { ref, watch } from 'vue'
import { useAuthStore } from '@/stores/auth'

const props = defineProps<{
  modelValue: boolean
}>()

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  'success': []
}>()

const authStore = useAuthStore()

const isOpen = ref(props.modelValue)
const isLoginMode = ref(true)
const username = ref('')
const email = ref('')
const password = ref('')
const showPassword = ref(false)
const form = ref<any>(null)

watch(() => props.modelValue, (newVal) => {
  isOpen.value = newVal
  if (newVal) {
    // Reset form when opened
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
  isLoginMode.value = !isLoginMode.value
  authStore.clearError()
}

async function handleSubmit() {
  const { valid } = await form.value.validate()
  if (!valid) return

  try {
    if (isLoginMode.value) {
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
