<template>
  <!-- Left Navigation - Transparent -->
  <v-navigation-drawer
    permanent
    rail
    :width="96"
    color="transparent"
    elevation="0"
  >
    <v-list density="compact" nav class="transparent-nav">
      <!-- Navigation items -->
      <v-list-item
        :to="{ name: 'dashboard' }"
        :active="$route.name === 'dashboard'"
        prepend-icon="mdi-pound"
        title="The Number"
        class="floating-item"
      />

      <v-list-item
        :to="{ name: 'expenses' }"
        :active="$route.name === 'expenses'"
        prepend-icon="mdi-home"
        title="Expenses"
        class="floating-item"
      />

      <v-list-item
        :to="{ name: 'transactions' }"
        :active="$route.name === 'transactions'"
        prepend-icon="mdi-currency-usd"
        title="Spending"
        class="floating-item"
      />

      <v-list-item
        :to="{ name: 'settings' }"
        :active="$route.name === 'settings'"
        prepend-icon="mdi-cog"
        title="Settings"
        class="floating-item"
      />
    </v-list>
  </v-navigation-drawer>

  <!-- Right Avatar with Menu -->
  <div class="avatar-container">
    <v-menu>
      <template v-slot:activator="{ props }">
        <v-btn
          icon
          v-bind="props"
          :aria-label="authStore.isAuthenticated ? `User menu for ${authStore.user?.username}` : 'Login menu'"
          class="avatar-button"
        >
          <v-avatar size="56" class="user-avatar">
            <span class="text-h6">{{ authStore.userInitials }}</span>
          </v-avatar>
        </v-btn>
      </template>

      <v-list>
        <template v-if="authStore.isAuthenticated">
          <v-list-item>
            <v-list-item-title class="font-weight-bold">{{ authStore.user?.username }}</v-list-item-title>
            <v-list-item-subtitle v-if="authStore.user?.email">{{ authStore.user.email }}</v-list-item-subtitle>
          </v-list-item>
          <v-divider />
          <v-list-item @click="handleLogout">
            <template v-slot:prepend>
              <v-icon>mdi-logout</v-icon>
            </template>
            <v-list-item-title>Logout</v-list-item-title>
          </v-list-item>
        </template>
        <template v-else>
          <v-list-item @click="showAuthModal = true">
            <template v-slot:prepend>
              <v-icon>mdi-login</v-icon>
            </template>
            <v-list-item-title>Login / Register</v-list-item-title>
          </v-list-item>
        </template>
      </v-list>
    </v-menu>
  </div>

  <!-- Auth Modal -->
  <AuthModal v-model="showAuthModal" @success="handleAuthSuccess" />
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useBudgetStore } from '@/stores/budget'
import AuthModal from './AuthModal.vue'

const $route = useRoute()
const $router = useRouter()
const authStore = useAuthStore()
const budgetStore = useBudgetStore()
const showAuthModal = ref(false)

onMounted(async () => {
  // Check for existing auth session
  await authStore.checkAuth()
})

async function handleLogout() {
  await authStore.logout()

  // Clear budget store data
  budgetStore.$reset()

  // Reload the page to ensure all cached data is cleared
  window.location.reload()
}

function handleAuthSuccess() {
  // Modal will close automatically
  // You could add a success message here if desired
}
</script>

<style scoped>
.v-navigation-drawer {
  position: fixed !important;
  left: 0;
  top: 0;
  height: 100vh;
  background-color: transparent !important;
}

.transparent-nav {
  background-color: transparent !important;
}

.floating-item {
  background-color: transparent !important;
  margin-bottom: var(--spacing-xs);
  border-radius: 12px;
  color: var(--color-text-secondary);
  transition: all var(--transition-base) var(--transition-ease);
}

.floating-item:hover {
  background-color: rgba(233, 245, 219, 0.2) !important;
  color: var(--color-soft-charcoal) !important;
}

/* Active navigation item - subtle sage green accent */
.floating-item.v-list-item--active {
  background-color: var(--color-sage-green) !important;
  color: var(--color-soft-charcoal) !important;
}

.avatar-container {
  position: fixed;
  top: 20px;
  right: 20px;
  z-index: 1000;
}

.avatar-button {
  background-color: white !important;
  border: 3px solid var(--color-sage-green) !important;
  box-shadow: 0 4px 12px rgba(135, 152, 106, 0.15);
  transition: all var(--transition-base) var(--transition-ease);
}

.avatar-button:hover {
  border-color: var(--color-success) !important;
  box-shadow: 0 6px 16px rgba(135, 152, 106, 0.25);
}

.user-avatar {
  background-color: var(--color-sage-green) !important;
  color: var(--color-soft-charcoal) !important;
  font-family: var(--font-display);
  font-weight: 400;
}
</style>
