<template>
  <v-app>
    <ErrorBoundary>
      <a href="#main-content" class="skip-link">Skip to main content</a>
      <NavigationRail />
      <v-main
        id="main-content"
        tabindex="-1"
        role="main"
        style="background-color: var(--color-warm-white);"
        :class="{ 'landing-layout': isLanding }"
      >
        <v-container fluid>
          <router-view />
        </v-container>
      </v-main>
    </ErrorBoundary>
  </v-app>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import NavigationRail from './components/NavigationRail.vue'
import ErrorBoundary from './components/ErrorBoundary.vue'

const route = useRoute()
const isLanding = computed(() => route.name === 'landing')
</script>

<style>
/* The Number Brand Guidelines - Typography */
@import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;700&display=swap');

/* ================================
   THE NUMBER DESIGN SYSTEM
   Based on FOIL Industries Guidelines
   ================================ */

:root {
  /* Primary Colors - The Number (Rebrand: forest green + warm cream) */
  --color-sage-green: #faf3dd;       /* Warm cream accent (was #E9F5DB) */
  --color-warm-white: #fdfcf0;       /* Warm cream background (was #FAFAF8) */
  --color-soft-charcoal: #2d3436;    /* Dark text base (was #3a3d42) */
  --color-green: #4a7c59;            /* Forest green — primary brand color */

  /* FOIL Accents (5% usage) */
  --color-slate: #4a5f7a;
  --color-mustard: #d4a017;
  --color-terracotta: #c96a5a;

  /* Functional Colors */
  --color-success: #4a7c59;          /* Forest green (was #6b7a52) */
  --color-error: #c96a5a;
  --color-text-primary: #2d3436;     /* (was #2b2e33) */
  --color-text-secondary: #4a4f52;   /* WCAG AA on #fdfcf0 (was #3a3d42) */
  --color-text-muted: #5a5d60;       /* Darkened for WCAG AA on #fdfcf0 (was #6b6e70) */

  /* Typography — Nunito replaces Scope One + Inter */
  --font-display: 'Nunito', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  --font-ui: 'Nunito', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;

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

/* WCAG AA contrast fix: Vuetify's default 0.6 opacity fails on warm cream bg */
.v-application {
  --v-medium-emphasis-opacity: 0.75;
}

/* Typography Hierarchy - Simplified */
* {
  font-family: var(--font-ui);
}

/* Nunito for everything */
h1 {
  font-family: var(--font-display) !important;
  font-weight: 400;
  color: var(--color-green);
}

h2, h3, h4, h5, h6 {
  font-family: var(--font-ui) !important;
  font-weight: 700;
  color: var(--color-green);
}

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

/* Responsive: Desktop layout adjustments */
@media (min-width: 768px) {
  #main-content {
    padding-bottom: 16px !important; /* Desktop: no bottom nav */
    padding-left: 96px !important; /* Account for fixed navigation rail width */
  }

  /* Landing page: no nav rail, so no left padding */
  #main-content.landing-layout {
    padding-left: 0 !important;
  }
}

/* Ensure content doesn't overlap with fixed nav rail */
@media (max-width: 767px) {
  #main-content {
    padding-left: 0 !important; /* Mobile: no left nav, use bottom nav */
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
