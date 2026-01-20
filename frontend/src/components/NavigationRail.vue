<template>
  <!-- Desktop: Left Rail (≥768px) - Hidden during onboarding -->
  <v-navigation-drawer
    v-if="!isMobile && !isOnboarding"
    permanent
    rail
    :width="96"
    color="transparent"
    elevation="0"
    class="desktop-nav"
  >
    <v-list density="compact" nav class="transparent-nav">
      <!-- Back to FOIL Engineering link -->
      <v-list-item
        href="https://foil.engineering"
        prepend-icon="mdi-arrow-left"
        title="FOIL Engineering"
        class="floating-item foil-link"
        target="_self"
      />

      <v-divider class="my-2" />

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

  <!-- Mobile: Bottom Navigation (<768px) - Hidden during onboarding -->
  <v-bottom-navigation
    v-else-if="!isOnboarding"
    v-model="activeNav"
    grow
    class="mobile-nav safe-area-bottom"
    color="primary"
  >
    <v-btn
      value="dashboard"
      :to="{ name: 'dashboard' }"
      :aria-label="'Navigate to The Number dashboard'"
    >
      <v-icon>mdi-pound</v-icon>
      <span>The Number</span>
    </v-btn>

    <v-btn
      value="expenses"
      :to="{ name: 'expenses' }"
      :aria-label="'Navigate to Expenses'"
    >
      <v-icon>mdi-home</v-icon>
      <span>Expenses</span>
    </v-btn>

    <v-btn
      value="transactions"
      :to="{ name: 'transactions' }"
      :aria-label="'Navigate to Spending'"
    >
      <v-icon>mdi-currency-usd</v-icon>
      <span>Spending</span>
    </v-btn>

    <v-btn
      value="settings"
      :to="{ name: 'settings' }"
      :aria-label="'Navigate to Settings'"
    >
      <v-icon>mdi-cog</v-icon>
      <span>Settings</span>
    </v-btn>
  </v-bottom-navigation>

  <!-- Avatar Menu (all screen sizes, repositioned for mobile) -->
  <div :class="['avatar-container', { 'avatar-mobile': isMobile }]">
    <v-menu>
      <template v-slot:activator="{ props }">
        <v-btn
          icon
          v-bind="props"
          :aria-label="authStore.isAuthenticated ? `User menu for ${authStore.user?.username}` : 'Login menu'"
          class="avatar-button"
        >
          <v-avatar :size="isMobile ? 40 : 56" class="user-avatar">
            <span :class="isMobile ? 'text-body-2' : 'text-h6'">{{ authStore.userInitials }}</span>
          </v-avatar>
        </v-btn>
      </template>

      <v-list>
        <!-- Back to FOIL Engineering (mobile only) -->
        <v-list-item v-if="isMobile" href="https://foil.engineering" target="_self">
          <template v-slot:prepend>
            <v-icon>mdi-open-in-new</v-icon>
          </template>
          <v-list-item-title>FOIL Engineering</v-list-item-title>
        </v-list-item>
        <v-divider v-if="isMobile" />

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
import { ref, onMounted, onUnmounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useBudgetStore } from '@/stores/budget'
import AuthModal from './AuthModal.vue'

const $route = useRoute()
const $router = useRouter()
const authStore = useAuthStore()
const budgetStore = useBudgetStore()
const showAuthModal = ref(false)
const isMobile = ref(false)

// Hide navigation during onboarding (when budget not configured but user is authenticated)
const isOnboarding = computed(() => {
  return authStore.isAuthenticated && !budgetStore.budgetNumber && !budgetStore.loadingNumber
})

// Active nav value for mobile bottom nav
const activeNav = computed({
  get: () => $route.name as string,
  set: () => {
    // Navigation handled by :to prop on buttons
  }
})

function checkMobile() {
  isMobile.value = window.innerWidth < 768
}

onMounted(async () => {
  // Check for existing auth session
  await authStore.checkAuth()

  // Check screen size
  checkMobile()
  window.addEventListener('resize', checkMobile)
})

onUnmounted(() => {
  window.removeEventListener('resize', checkMobile)
})

async function handleLogout() {
  await authStore.logout()

  // Clear budget store data
  budgetStore.$reset()

  // Reload the page to ensure all cached data is cleared
  window.location.reload()
}

async function handleAuthSuccess() {
  // Navigate to dashboard to show onboarding for new users
  // or refresh the number for existing users
  await $router.push({ name: 'dashboard' })

  // Try to fetch the budget number for existing users
  // For new users, this will fail gracefully and show onboarding
  if (authStore.isAuthenticated) {
    try {
      await budgetStore.fetchNumber()
    } catch (e) {
      // Ignore error - this is expected for new users
      // The dashboard will show onboarding flow automatically
    }
  }
}
</script>

<style scoped>
/* Desktop Navigation Rail */
.desktop-nav {
  position: fixed !important;
  left: 0;
  top: 0;
  height: 100vh;
  background-color: transparent !important;
}

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
  font-weight: 600;
}

/* FOIL Engineering link styling */
.foil-link {
  opacity: 0.7;
  font-size: 0.875rem;
}

.foil-link:hover {
  opacity: 1;
}

/* Mobile Bottom Navigation */
.mobile-nav {
  position: fixed !important;
  bottom: 0;
  left: 0;
  right: 0;
  z-index: 1000;
  background-color: white !important;
  border-top: 1px solid var(--color-sage-green);
  box-shadow: 0 -2px 8px rgba(135, 152, 106, 0.1);
  height: 56px; /* Base height, will be adjusted with safe-area */
}

.mobile-nav :deep(.v-btn) {
  flex-direction: column;
  font-size: 0.75rem;
  color: var(--color-text-secondary);
  min-height: 48px; /* Touch target minimum */
  padding: 4px 12px;
}

.mobile-nav :deep(.v-btn--active) {
  color: var(--color-success) !important;
  background-color: rgba(233, 245, 219, 0.3) !important;
  font-weight: 600;
}

.mobile-nav :deep(.v-icon) {
  margin-bottom: 2px;
}

/* Avatar Container */
.avatar-container {
  position: fixed;
  top: 20px;
  right: 20px;
  z-index: 1000;
}

.avatar-mobile {
  top: 12px;
  right: 12px;
}

.avatar-button {
  background-color: white !important;
  border: 3px solid var(--color-sage-green) !important;
  box-shadow: 0 4px 12px rgba(135, 152, 106, 0.15);
  transition: all var(--transition-base) var(--transition-ease);
}

.avatar-mobile .avatar-button {
  width: 48px !important;
  height: 48px !important;
  border-width: 2px !important;
}

.avatar-button:hover {
  border-color: var(--color-success) !important;
  box-shadow: 0 6px 16px rgba(135, 152, 106, 0.25);
}

.user-avatar {
  background-color: var(--color-sage-green) !important;
  color: var(--color-soft-charcoal) !important;
  font-weight: 600;
}
</style>
