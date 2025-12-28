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
  --color-text-secondary: #3a3d42;  /* WCAG fix: Changed from #5a5d62 for 6.8:1 contrast on sage green */
  --color-text-muted: #5a5d62;      /* WCAG fix: Promoted from #8a8d92 */

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

/* Typography Hierarchy - Simplified */
* {
  font-family: var(--font-ui);
}

/* ONLY use display font for h1 - everything else uses Inter */
h1 {
  font-family: var(--font-display) !important;
  font-weight: 400;
  color: var(--color-text-primary);
}

h2, h3, h4, h5, h6 {
  font-family: var(--font-ui) !important;
  font-weight: 600;
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

/* Safe Area Support for Notched Devices (iPhone X+, Android) */
.safe-area-bottom {
  padding-bottom: env(safe-area-inset-bottom, 0) !important;
  height: calc(56px + env(safe-area-inset-bottom, 0)) !important;
}

/* Main content padding to account for bottom nav + safe areas */
#main-content {
  padding-bottom: calc(56px + env(safe-area-inset-bottom, 0) + 16px) !important;
  padding-left: env(safe-area-inset-left, 0) !important;
  padding-right: env(safe-area-inset-right, 0) !important;
}

/* Responsive: Only add bottom padding on mobile */
@media (min-width: 768px) {
  #main-content {
    padding-bottom: 16px !important; /* Desktop: no bottom nav */
  }
}

/* Phase 3.2: High-contrast focus indicators for accessibility */
*:focus-visible {
  outline: 3px solid var(--color-slate);
  outline-offset: 2px;
  border-radius: 4px;
}

.v-btn:focus-visible {
  outline: 2px solid var(--color-slate);
  outline-offset: 2px;
}
</style>
