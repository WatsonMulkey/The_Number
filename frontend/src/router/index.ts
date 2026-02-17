import { createRouter, createWebHistory } from 'vue-router'
import Dashboard from '../views/Dashboard.vue'
import { useAuthStore } from '../stores/auth'

let authChecked = false

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'landing',
      component: () => import('../views/Landing.vue'),
      meta: { public: true }
    },
    {
      path: '/dashboard',
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
    },
    {
      path: '/admin',
      name: 'admin',
      component: () => import('../views/Admin.vue'),
      meta: { requiresAdmin: true }
    },
    {
      path: '/:pathMatch(.*)*',
      redirect: { name: 'dashboard' }
    }
  ]
})

/**
 * Auth guard: ensures auth state is checked before any route.
 * - Authenticated users hitting landing → redirect to dashboard
 * - Unauthenticated users hitting protected routes → redirect to landing
 */
router.beforeEach(async (to, _from, next) => {
  if (!authChecked) {
    const authStore = useAuthStore()
    await authStore.checkAuth()
    authChecked = true
  }

  const authStore = useAuthStore()

  // Authenticated users hitting landing → redirect to dashboard
  if (to.name === 'landing' && authStore.isAuthenticated) {
    return next({ name: 'dashboard' })
  }

  // Unauthenticated users hitting protected routes → redirect to landing
  if (!to.meta?.public && !authStore.isAuthenticated) {
    return next({ name: 'landing' })
  }

  // Non-admin users hitting admin routes → redirect to dashboard
  if (to.meta?.requiresAdmin && !authStore.user?.is_admin) {
    return next({ name: 'dashboard' })
  }

  next()
})

export default router
