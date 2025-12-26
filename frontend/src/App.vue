<template>
  <v-app>
    <ErrorBoundary>
      <a href="#main-content" class="skip-link">Skip to main content</a>
      <NavigationRail />
      <v-main id="main-content" tabindex="-1" style="background-color: var(--color-warm-white);">
        <v-container fluid>
          <router-view />
        </v-container>
      </v-main>
    </ErrorBoundary>
  </v-app>
</template>

<script setup lang="ts">
import NavigationRail from './components/NavigationRail.vue'
import ErrorBoundary from './components/ErrorBoundary.vue'
</script>

<style>
/* The Number Brand Guidelines - Typography */
@import url('https://fonts.googleapis.com/css2?family=Scope+One&display=swap');
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

/* ================================
   THE NUMBER DESIGN SYSTEM
   Based on FOIL Industries Guidelines
   ================================ */

:root {
  /* Primary Colors - The Number */
  --color-sage-green: #E9F5DB;
  --color-warm-white: #FAFAF8;
  --color-soft-charcoal: #3a3d42;

  /* FOIL Accents (5% usage) */
  --color-slate: #4a5f7a;
  --color-mustard: #d4a017;
  --color-terracotta: #c96a5a;

  /* Functional Colors */
  --color-success: #87986a;
  --color-error: #c96a5a;
  --color-text-primary: #2b2e33;
  --color-text-secondary: #5a5d62;
  --color-text-muted: #8a8d92;

  /* Typography */
  --font-display: 'Scope One', Georgia, serif;
  --font-ui: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;

  /* Spacing */
  --spacing-xs: 8px;
  --spacing-sm: 16px;
  --spacing-md: 24px;
  --spacing-lg: 36px;
  --spacing-xl: 48px;

  /* Transitions */
  --transition-fast: 150ms;
  --transition-base: 250ms;
  --transition-slow: 370ms;
  --transition-ease: cubic-bezier(0.4, 0, 0.2, 1);
}

/* Typography Hierarchy */
* {
  font-family: var(--font-ui);
}

h1, h2, h3, h4, h5, h6 {
  font-family: var(--font-display) !important;
  font-weight: 400;
  color: var(--color-text-primary);
}

/* Body text uses Inter for clarity */
body, p, span, div, button, input, textarea, select {
  font-family: var(--font-ui);
}

/* Skip link for accessibility */
.skip-link {
  position: absolute;
  top: -40px;
  left: 0;
  background: var(--color-slate);
  color: var(--color-warm-white);
  padding: 8px 16px;
  text-decoration: none;
  z-index: 9999;
  border-radius: 0 0 4px 0;
  font-family: var(--font-ui);
  font-weight: 600;
}

.skip-link:focus {
  top: 0;
}

/* Override Vuetify defaults to match brand */
.v-application {
  font-family: var(--font-ui) !important;
}

.v-card {
  font-family: var(--font-ui) !important;
}
</style>
