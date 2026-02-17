<template>
  <div class="landing">
    <!-- Hero Section -->
    <section class="hero">
      <div class="hero-content">
        <h1 class="hero-headline">Know Your Number</h1>
        <p class="hero-subline">
          The daily budget app that answers one question:
          <strong>how much can I spend today?</strong>
        </p>
        <div class="hero-body">
          <p>
            If you also have no idea how much you're going to spend on entertainment or gas or groceries;
            then The Number could be the budget app you're looking for. The Number just takes your available
            money (paycheck or fixed pool) accounts for your expenses, then tells you how much you can spend
            on a daily basis and not bust your budget.
          </p>
          <p>
            Track your purchases in the app, and see how your budget for tomorrow goes up and down.
          </p>
        </div>
        <v-btn
          size="x-large"
          color="primary"
          class="hero-cta"
          @click="openRegister"
        >
          Join the Beta
        </v-btn>
      </div>
    </section>

    <!-- How It Works -->
    <section class="how-it-works">
      <h2 class="section-title">How It Works</h2>
      <div class="steps">
        <div class="step">
          <div class="step-icon">
            <v-icon size="40" color="primary">mdi-calendar-clock</v-icon>
          </div>
          <h3 class="step-title">1. Set your income and payday</h3>
          <p class="step-desc">
            Tell us how much you make and when you get paid. We handle the math from there.
          </p>
        </div>
        <div class="step">
          <div class="step-icon">
            <v-icon size="40" color="primary">mdi-receipt-text-outline</v-icon>
          </div>
          <h3 class="step-title">2. Log what you spend</h3>
          <p class="step-desc">
            Quick-add purchases as you go. No categories to fuss with, just the amount.
          </p>
        </div>
        <div class="step">
          <div class="step-icon">
            <v-icon size="40" color="primary">mdi-pound</v-icon>
          </div>
          <h3 class="step-title">3. See your number</h3>
          <p class="step-desc">
            One number tells you exactly what you can spend today, and updates in real time.
          </p>
        </div>
      </div>
    </section>

    <!-- Features -->
    <section class="features">
      <h2 class="section-title">Built for Real Life</h2>
      <div class="feature-grid">
        <div class="feature-card">
          <v-icon size="32" color="primary" class="feature-icon">mdi-shield-lock-outline</v-icon>
          <h3 class="feature-title">Privacy First</h3>
          <p class="feature-desc">
            No bank account, no phone number, no location tracking, no app store. Just an optional email address for password resetting.
          </p>
        </div>
        <div class="feature-card">
          <v-icon size="32" color="primary" class="feature-icon">mdi-update</v-icon>
          <h3 class="feature-title">Real-time daily budget</h3>
          <p class="feature-desc">
            Your number recalculates after every purchase, so you always know where you stand.
          </p>
        </div>
        <div class="feature-card">
          <v-icon size="32" color="primary" class="feature-icon">mdi-weather-sunset-up</v-icon>
          <h3 class="feature-title">Tomorrow preview</h3>
          <p class="feature-desc">
            See how today's spending affects tomorrow's budget before you swipe.
          </p>
        </div>
        <div class="feature-card">
          <v-icon size="32" color="primary" class="feature-icon">mdi-piggy-bank-outline</v-icon>
          <h3 class="feature-title">Savings pool</h3>
          <p class="feature-desc">
            Unspent budget carries forward automatically. Underspend today, and have more tomorrow!
          </p>
        </div>
        <div class="feature-card">
          <v-icon size="32" color="primary" class="feature-icon">mdi-cellphone-check</v-icon>
          <h3 class="feature-title">Install from your browser</h3>
          <p class="feature-desc">
            Install it like a native app from your browser. No app store required.
          </p>
        </div>
      </div>
    </section>

    <!-- FAQ -->
    <section class="faq">
      <h2 class="section-title">Frequently Asked Questions</h2>
      <v-expansion-panels variant="accordion" class="faq-panels">
        <v-expansion-panel>
          <v-expansion-panel-title>How do I install The Number?</v-expansion-panel-title>
          <v-expansion-panel-text>
            The Number is a Progressive Web App (PWA). On your phone's browser, tap the share or menu
            button and select "Add to Home Screen." It installs instantly — no app store needed.
          </v-expansion-panel-text>
        </v-expansion-panel>
        <v-expansion-panel>
          <v-expansion-panel-title>I already have a budget in a spreadsheet, can I import it to The Number?</v-expansion-panel-title>
          <v-expansion-panel-text>
            Yes! Go to Settings and use the CSV/Excel import option to bring in your existing budget
            and expenses.
          </v-expansion-panel-text>
        </v-expansion-panel>
        <v-expansion-panel>
          <v-expansion-panel-title>What if I don't want to enter my email address?</v-expansion-panel-title>
          <v-expansion-panel-text>
            Email is completely optional. It's only used for password resets. You can create an account
            with just a username and password.
          </v-expansion-panel-text>
        </v-expansion-panel>
      </v-expansion-panels>
    </section>

    <!-- CTA Footer -->
    <section class="cta-footer">
      <h2 class="cta-headline">Ready to take control?</h2>
      <v-btn
        size="x-large"
        color="primary"
        class="hero-cta"
        @click="openRegister"
      >
        Join the Beta
      </v-btn>
      <p class="cta-login">
        Already have an account?
        <a href="#" class="login-link" @click.prevent="openLogin">Log in</a>
      </p>
    </section>

    <!-- Auth Modal -->
    <AuthModal
      v-model="showAuthModal"
      :initial-mode="authMode"
      @success="handleAuthSuccess"
    />
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import AuthModal from '@/components/AuthModal.vue'

const router = useRouter()
const showAuthModal = ref(false)
const authMode = ref<'login' | 'register'>('register')

function openRegister() {
  authMode.value = 'register'
  showAuthModal.value = true
}

function openLogin() {
  authMode.value = 'login'
  showAuthModal.value = true
}

async function handleAuthSuccess() {
  await router.push({ name: 'dashboard' })
}
</script>

<style scoped>
.landing {
  max-width: 960px;
  margin: 0 auto;
  padding: 0 var(--spacing-sm);
}

/* Hero */
.hero {
  text-align: center;
  padding: var(--spacing-xl) 0;
  min-height: 50vh;
  display: flex;
  align-items: center;
  justify-content: center;
}

.hero-headline {
  font-family: var(--font-display) !important;
  font-size: 3.5rem;
  font-weight: 400;
  color: var(--color-text-primary);
  margin-bottom: var(--spacing-sm);
  line-height: 1.1;
}

.hero-subline {
  font-size: 1.25rem;
  color: var(--color-text-secondary);
  max-width: 520px;
  margin: 0 auto var(--spacing-lg);
  line-height: 1.6;
}

.hero-body {
  max-width: 580px;
  margin: 0 auto var(--spacing-lg);
  text-align: center;
}

.hero-body p {
  font-size: 1.05rem;
  color: var(--color-text-secondary);
  line-height: 1.7;
  margin-bottom: var(--spacing-sm);
}

.hero-cta {
  background-color: var(--color-success) !important;
  color: white !important;
  font-weight: 600;
  letter-spacing: 0.5px;
  padding: 12px 40px !important;
  border-radius: 12px !important;
  text-transform: none !important;
  font-size: 1.1rem !important;
}

.hero-cta:hover {
  background-color: var(--color-soft-charcoal) !important;
}

/* How It Works */
.how-it-works {
  padding: var(--spacing-xl) 0;
}

.section-title {
  font-family: var(--font-ui) !important;
  font-size: 1.75rem;
  font-weight: 600;
  text-align: center;
  color: var(--color-text-primary);
  margin-bottom: var(--spacing-lg);
}

.steps {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: var(--spacing-md);
}

.step {
  text-align: center;
  padding: var(--spacing-md);
}

.step-icon {
  width: 72px;
  height: 72px;
  border-radius: 50%;
  background-color: var(--color-sage-green);
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto var(--spacing-sm);
}

.step-title {
  font-size: 1rem;
  font-weight: 600;
  color: var(--color-text-primary);
  margin-bottom: var(--spacing-xs);
}

.step-desc {
  font-size: 0.938rem;
  color: var(--color-text-secondary);
  line-height: 1.5;
}

/* Features */
.features {
  padding: var(--spacing-xl) 0;
}

.feature-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: var(--spacing-md);
}

.feature-card {
  background: var(--color-warm-white);
  border: 1px solid var(--color-sage-green);
  border-radius: 16px;
  padding: var(--spacing-md);
  transition: box-shadow var(--transition-base) var(--transition-ease);
}

.feature-card:hover {
  box-shadow: 0 4px 16px rgba(135, 152, 106, 0.15);
}

.feature-icon {
  margin-bottom: var(--spacing-xs);
}

.feature-title {
  font-size: 1rem;
  font-weight: 600;
  color: var(--color-text-primary);
  margin-bottom: var(--spacing-xs);
}

.feature-desc {
  font-size: 0.938rem;
  color: var(--color-text-secondary);
  line-height: 1.5;
}

/* CTA Footer */
.cta-footer {
  text-align: center;
  padding: var(--spacing-xl) 0;
  margin-bottom: var(--spacing-lg);
}

.cta-headline {
  font-family: var(--font-display) !important;
  font-size: 2rem;
  font-weight: 400;
  color: var(--color-text-primary);
  margin-bottom: var(--spacing-md);
}

.cta-login {
  margin-top: var(--spacing-sm);
  font-size: 0.938rem;
  color: var(--color-text-secondary);
}

.login-link {
  color: var(--color-success);
  font-weight: 600;
  text-decoration: none;
}

.login-link:hover {
  text-decoration: underline;
}

/* FAQ */
.faq {
  padding: var(--spacing-xl) 0;
}

.faq-panels {
  max-width: 720px;
  margin: 0 auto;
}

.faq-panels .v-expansion-panel {
  background: var(--color-warm-white);
  border: 1px solid var(--color-sage-green);
  margin-bottom: var(--spacing-xs);
  border-radius: 12px !important;
}

.faq-panels .v-expansion-panel-title {
  font-weight: 600;
  font-size: 1rem;
  color: var(--color-text-primary);
}

.faq-panels .v-expansion-panel-text {
  font-size: 0.938rem;
  color: var(--color-text-secondary);
  line-height: 1.6;
}

/* Responsive */
@media (max-width: 767px) {
  .hero-headline {
    font-size: 2.5rem;
  }

  .hero-subline {
    font-size: 1.1rem;
  }

  .steps {
    grid-template-columns: 1fr;
    gap: var(--spacing-sm);
  }

  .feature-grid {
    grid-template-columns: 1fr;
  }
}
</style>
