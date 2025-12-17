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

  <!-- Right Avatar -->
  <div class="avatar-container">
    <v-avatar color="primary" size="56">
      <span class="text-h6 text-white">TN</span>
    </v-avatar>
  </div>
</template>

<script setup lang="ts">
import { useRoute } from 'vue-router'

const $route = useRoute()
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
  margin-bottom: 8px;
}

.floating-item:hover {
  background-color: rgba(255, 255, 255, 0.1) !important;
}

.avatar-container {
  position: fixed;
  top: 20px;
  right: 20px;
  z-index: 1000;
}
</style>
