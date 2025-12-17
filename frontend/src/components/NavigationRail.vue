<template>
  <v-navigation-drawer
    permanent
    rail
    :width="96"
    color="surface"
    elevation="2"
  >
    <v-list density="compact" nav>
      <!-- Avatar at top -->
      <v-list-item class="mb-4 mt-2">
        <v-avatar color="primary" size="56">
          <span class="text-h6 text-white">TN</span>
        </v-avatar>
      </v-list-item>

      <!-- Navigation items -->
      <v-list-item
        :to="{ name: 'dashboard' }"
        :active="$route.name === 'dashboard'"
        prepend-icon="mdi-pound"
        title="The Number"
      />

      <v-list-item
        :to="{ name: 'expenses' }"
        :active="$route.name === 'expenses'"
        prepend-icon="mdi-currency-usd"
        title="Expenses"
      />

      <v-list-item
        :to="{ name: 'transactions' }"
        :active="$route.name === 'transactions'"
        prepend-icon="mdi-receipt"
        title="Spending"
      />

      <v-list-item
        :to="{ name: 'settings' }"
        :active="$route.name === 'settings'"
        prepend-icon="mdi-cog"
        title="Settings"
      />
    </v-list>
  </v-navigation-drawer>
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
}
</style>
