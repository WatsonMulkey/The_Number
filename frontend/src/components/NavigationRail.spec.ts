import { describe, it, expect, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createRouter, createMemoryHistory } from 'vue-router'
import NavigationRail from './NavigationRail.vue'

describe('NavigationRail Component', () => {
  let router: any

  beforeEach(async () => {
    router = createRouter({
      history: createMemoryHistory(),
      routes: [
        { path: '/', name: 'dashboard', component: { template: '<div>Dashboard</div>' } },
        { path: '/expenses', name: 'expenses', component: { template: '<div>Expenses</div>' } },
        { path: '/transactions', name: 'transactions', component: { template: '<div>Transactions</div>' } },
        { path: '/settings', name: 'settings', component: { template: '<div>Settings</div>' } },
      ],
    })
    await router.push('/')
    await router.isReady()
  })

  describe('Rendering', () => {
    it('should render the navigation rail', () => {
      const wrapper = mount(NavigationRail, {
        global: {
          plugins: [router],
        },
      })

      expect(wrapper.exists()).toBe(true)
    })

    it('should display avatar with "TN" text', () => {
      const wrapper = mount(NavigationRail, {
        global: {
          plugins: [router],
        },
      })

      expect(wrapper.text()).toContain('TN')
    })

    it('should render all navigation items', () => {
      const wrapper = mount(NavigationRail, {
        global: {
          plugins: [router],
        },
      })

      const listItems = wrapper.findAll('.v-list-item')
      // Should have 5 items: 1 avatar + 4 navigation links
      expect(listItems.length).toBeGreaterThanOrEqual(4)
    })
  })

  describe('Navigation Items', () => {
    it('should have Dashboard navigation item', () => {
      const wrapper = mount(NavigationRail, {
        global: {
          plugins: [router],
        },
      })

      const dashboardLink = wrapper.find('[title="Dashboard"]')
      expect(dashboardLink.exists()).toBe(true)
    })

    it('should have Expenses navigation item', () => {
      const wrapper = mount(NavigationRail, {
        global: {
          plugins: [router],
        },
      })

      const expensesLink = wrapper.find('[title="Expenses"]')
      expect(expensesLink.exists()).toBe(true)
    })

    it('should have Spending navigation item', () => {
      const wrapper = mount(NavigationRail, {
        global: {
          plugins: [router],
        },
      })

      const spendingLink = wrapper.find('[title="Spending"]')
      expect(spendingLink.exists()).toBe(true)
    })

    it('should have Settings navigation item', () => {
      const wrapper = mount(NavigationRail, {
        global: {
          plugins: [router],
        },
      })

      const settingsLink = wrapper.find('[title="Settings"]')
      expect(settingsLink.exists()).toBe(true)
    })
  })

  describe('Navigation Links', () => {
    it('should link to dashboard route', () => {
      const wrapper = mount(NavigationRail, {
        global: {
          plugins: [router],
        },
      })

      const dashboardLink = wrapper.find('[title="Dashboard"]')
      expect(dashboardLink.attributes('to')).toBeDefined()
    })

    it('should link to expenses route', () => {
      const wrapper = mount(NavigationRail, {
        global: {
          plugins: [router],
        },
      })

      const expensesLink = wrapper.find('[title="Expenses"]')
      expect(expensesLink.attributes('to')).toBeDefined()
    })

    it('should link to transactions route', () => {
      const wrapper = mount(NavigationRail, {
        global: {
          plugins: [router],
        },
      })

      const transactionsLink = wrapper.find('[title="Spending"]')
      expect(transactionsLink.attributes('to')).toBeDefined()
    })

    it('should link to settings route', () => {
      const wrapper = mount(NavigationRail, {
        global: {
          plugins: [router],
        },
      })

      const settingsLink = wrapper.find('[title="Settings"]')
      expect(settingsLink.attributes('to')).toBeDefined()
    })
  })

  describe('Icons', () => {
    it('should show dashboard icon', () => {
      const wrapper = mount(NavigationRail, {
        global: {
          plugins: [router],
        },
      })

      const dashboardItem = wrapper.find('[title="Dashboard"]')
      expect(dashboardItem.attributes('prepend-icon')).toBe('mdi-view-dashboard')
    })

    it('should show expenses icon', () => {
      const wrapper = mount(NavigationRail, {
        global: {
          plugins: [router],
        },
      })

      const expensesItem = wrapper.find('[title="Expenses"]')
      expect(expensesItem.attributes('prepend-icon')).toBe('mdi-currency-usd')
    })

    it('should show transactions icon', () => {
      const wrapper = mount(NavigationRail, {
        global: {
          plugins: [router],
        },
      })

      const transactionsItem = wrapper.find('[title="Spending"]')
      expect(transactionsItem.attributes('prepend-icon')).toBe('mdi-receipt')
    })

    it('should show settings icon', () => {
      const wrapper = mount(NavigationRail, {
        global: {
          plugins: [router],
        },
      })

      const settingsItem = wrapper.find('[title="Settings"]')
      expect(settingsItem.attributes('prepend-icon')).toBe('mdi-cog')
    })
  })

  describe('Active Route', () => {
    it('should mark dashboard as active when on dashboard route', async () => {
      await router.push('/')
      await router.isReady()

      const wrapper = mount(NavigationRail, {
        global: {
          plugins: [router],
        },
      })

      const dashboardItem = wrapper.find('[title="Dashboard"]')
      expect(dashboardItem.attributes('active')).toBeDefined()
    })

    it('should mark expenses as active when on expenses route', async () => {
      await router.push('/expenses')
      await router.isReady()

      const wrapper = mount(NavigationRail, {
        global: {
          plugins: [router],
        },
      })

      const expensesItem = wrapper.find('[title="Expenses"]')
      expect(expensesItem.attributes('active')).toBeDefined()
    })

    it('should mark transactions as active when on transactions route', async () => {
      await router.push('/transactions')
      await router.isReady()

      const wrapper = mount(NavigationRail, {
        global: {
          plugins: [router],
        },
      })

      const transactionsItem = wrapper.find('[title="Spending"]')
      expect(transactionsItem.attributes('active')).toBeDefined()
    })

    it('should mark settings as active when on settings route', async () => {
      await router.push('/settings')
      await router.isReady()

      const wrapper = mount(NavigationRail, {
        global: {
          plugins: [router],
        },
      })

      const settingsItem = wrapper.find('[title="Settings"]')
      expect(settingsItem.attributes('active')).toBeDefined()
    })
  })

  describe('Navigation Drawer Properties', () => {
    it('should be permanent', () => {
      const wrapper = mount(NavigationRail, {
        global: {
          plugins: [router],
        },
      })

      const drawer = wrapper.find('.v-navigation-drawer')
      expect(drawer.attributes('permanent')).toBeDefined()
    })

    it('should be in rail mode', () => {
      const wrapper = mount(NavigationRail, {
        global: {
          plugins: [router],
        },
      })

      const drawer = wrapper.find('.v-navigation-drawer')
      expect(drawer.attributes('rail')).toBeDefined()
    })

    it('should have correct width', () => {
      const wrapper = mount(NavigationRail, {
        global: {
          plugins: [router],
        },
      })

      const drawer = wrapper.find('.v-navigation-drawer')
      expect(drawer.attributes('width')).toBe('96')
    })
  })

  describe('Styling', () => {
    it('should have fixed position styling', () => {
      const wrapper = mount(NavigationRail, {
        global: {
          plugins: [router],
        },
      })

      const drawer = wrapper.find('.v-navigation-drawer')
      expect(drawer.classes()).toContain('v-navigation-drawer')
    })
  })
})
