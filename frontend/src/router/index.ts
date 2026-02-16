import { createRouter, createWebHistory } from 'vue-router'
import Dashboard from '../views/Dashboard.vue'
import { useAuthStore } from '../stores/auth'

let authChecked = false

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'dashboard',
      component: Dashboard
    },
    {
      path: '/expenses',
      name: 'expenses',
      component: () => import('../views/Expenses.vue')
    },
    {
      path: '/transactions',
      name: 'transactions',
      component: () => import('../views/Transactions.vue')
    },
    {
      path: '/settings',
      name: 'settings',
      component: () => import('../views/Settings.vue')
    }
  ]
})

/**
 * Auth guard: ensures auth state is checked before any protected route.
 * Prevents dashboard from fetching budget data before auth is confirmed.
 */
router.beforeEach(async (_to, _from, next) => {
  if (!authChecked) {
    const authStore = useAuthStore()
    await authStore.checkAuth()
    authChecked = true
  }
  next()
})

export default router
