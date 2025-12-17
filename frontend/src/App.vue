<template>
  <v-app>
    <NavigationRail />
    <v-main style="background-color: rgba(135, 152, 106, 0.83);">
      <v-container fluid>
        <router-view />
      </v-container>
    </v-main>
  </v-app>
</template>

<script setup lang="ts">
import NavigationRail from './components/NavigationRail.vue'
</script>

<style>
@import url('https://fonts.googleapis.com/css2?family=Libre+Baskerville:wght@400;700&family=Roboto:wght@300;400;500;700&display=swap');

* {
  font-family: 'Roboto', sans-serif;
}

h1, h2, h3, h4, h5, h6 {
  font-family: 'Libre Baskerville', serif !important;
}
</style>
