<template>
  <div v-if="hasError" class="error-boundary">
    <v-container class="d-flex justify-center align-center" style="min-height: 100vh;">
      <v-card max-width="600" class="pa-6">
        <v-card-title class="text-h4 text-center mb-4">
          <v-icon size="64" color="error" class="mb-2">mdi-alert-circle</v-icon>
          <div>Something went wrong</div>
        </v-card-title>
        <v-card-text class="text-center">
          <p class="text-body-1 mb-4">
            We're sorry, but something unexpected happened. Please try refreshing the page.
          </p>
          <p class="text-caption text-medium-emphasis" v-if="errorMessage">
            {{ errorMessage }}
          </p>
        </v-card-text>
        <v-card-actions class="justify-center">
          <v-btn
            color="primary"
            size="large"
            @click="handleReset"
          >
            Refresh Page
          </v-btn>
          <v-btn
            variant="text"
            @click="handleReset"
          >
            Try Again
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-container>
  </div>
  <slot v-else />
</template>

<script setup lang="ts">
import { ref, onErrorCaptured } from 'vue'

const hasError = ref(false)
const errorMessage = ref('')

onErrorCaptured((err, instance, info) => {
  hasError.value = true
  errorMessage.value = err.message || 'An unknown error occurred'

  // Log error to console for debugging
  console.error('Error caught by boundary:', {
    error: err,
    component: instance?.$options.name,
    info
  })

  // Prevent error from propagating further
  return false
})

function handleReset() {
  // Refresh the page to reset the app state
  window.location.reload()
}
</script>

<style scoped>
.error-boundary {
  background-color: rgba(135, 152, 106, 0.83);
  min-height: 100vh;
}
</style>
