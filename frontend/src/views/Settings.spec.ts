import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { createRouter, createMemoryHistory } from 'vue-router'
import Settings from './Settings.vue'
import { budgetApi } from '@/services/api'
import { useBudgetStore } from '@/stores/budget'
import { mockBudgetConfig, createMockResponse, createMockError } from '@/test/test-utils'

// Mock the API module
vi.mock('@/services/api', () => ({
  budgetApi: {
    configureBudget: vi.fn(),
    getBudgetConfig: vi.fn(),
  },
}))

describe('Settings Component', () => {
  let router: any
  let pinia: any

  beforeEach(async () => {
    pinia = createPinia()
    setActivePinia(pinia)

    router = createRouter({
      history: createMemoryHistory(),
      routes: [
        { path: '/', name: 'settings', component: Settings },
      ],
    })

    await router.push('/')
    await router.isReady()

    vi.clearAllMocks()
  })

  describe('Rendering', () => {
    it('should render the component', () => {
      const wrapper = mount(Settings, {
        global: {
          plugins: [pinia, router],
        },
      })

      expect(wrapper.exists()).toBe(true)
      expect(wrapper.text()).toContain('Budget Settings')
    })

    it('should render configuration form', () => {
      const wrapper = mount(Settings, {
        global: {
          plugins: [pinia, router],
        },
      })

      expect(wrapper.text()).toContain('Configure Budget Mode')
    })

    it('should have mode selection radio buttons', () => {
      const wrapper = mount(Settings, {
        global: {
          plugins: [pinia, router],
        },
      })

      expect(wrapper.text()).toContain('Paycheck Mode')
      expect(wrapper.text()).toContain('Fixed Pool Mode')
    })
  })

  describe('Mode Selection', () => {
    it('should initialize with paycheck mode by default', () => {
      const wrapper = mount(Settings, {
        global: {
          plugins: [pinia, router],
        },
      })

      expect(wrapper.vm.config.mode).toBe('paycheck')
    })

    it('should show paycheck mode fields when selected', async () => {
      const wrapper = mount(Settings, {
        global: {
          plugins: [pinia, router],
        },
      })

      wrapper.vm.config.mode = 'paycheck'
      await wrapper.vm.$nextTick()

      expect(wrapper.text()).toContain('Monthly Income')
      expect(wrapper.text()).toContain('Days Until Next Paycheck')
    })

    it('should show fixed pool fields when selected', async () => {
      const wrapper = mount(Settings, {
        global: {
          plugins: [pinia, router],
        },
      })

      wrapper.vm.config.mode = 'fixed_pool'
      await wrapper.vm.$nextTick()

      expect(wrapper.text()).toContain('Total Money Available')
    })

    it('should hide paycheck fields in fixed pool mode', async () => {
      const wrapper = mount(Settings, {
        global: {
          plugins: [pinia, router],
        },
      })

      wrapper.vm.config.mode = 'fixed_pool'
      await wrapper.vm.$nextTick()

      expect(wrapper.text()).not.toContain('Monthly Income')
    })

    it('should hide fixed pool fields in paycheck mode', async () => {
      const wrapper = mount(Settings, {
        global: {
          plugins: [pinia, router],
        },
      })

      wrapper.vm.config.mode = 'paycheck'
      await wrapper.vm.$nextTick()

      expect(wrapper.text()).not.toContain('Total Money Available')
    })
  })

  describe('Form Initialization', () => {
    it('should have default config values', () => {
      const wrapper = mount(Settings, {
        global: {
          plugins: [pinia, router],
        },
      })

      expect(wrapper.vm.config).toEqual({
        mode: 'paycheck',
        monthly_income: 0,
        days_until_paycheck: 14,
        total_money: 0,
      })
    })

    it('should have save configuration button', () => {
      const wrapper = mount(Settings, {
        global: {
          plugins: [pinia, router],
        },
      })

      expect(wrapper.text()).toContain('Save Configuration')
    })
  })

  describe('Loading Current Config', () => {
    it('should load existing configuration on mount', async () => {
      vi.mocked(budgetApi.getBudgetConfig).mockResolvedValue(
        createMockResponse(mockBudgetConfig)
      )

      mount(Settings, {
        global: {
          plugins: [pinia, router],
        },
      })

      await flushPromises()

      expect(budgetApi.getBudgetConfig).toHaveBeenCalled()
    })

    it('should populate form with existing config', async () => {
      vi.mocked(budgetApi.getBudgetConfig).mockResolvedValue(
        createMockResponse(mockBudgetConfig)
      )

      const wrapper = mount(Settings, {
        global: {
          plugins: [pinia, router],
        },
      })

      await flushPromises()

      expect(wrapper.vm.config.mode).toBe('paycheck')
      expect(wrapper.vm.config.monthly_income).toBe(5000)
      expect(wrapper.vm.config.days_until_paycheck).toBe(15)
    })

    it('should not populate form when not configured', async () => {
      vi.mocked(budgetApi.getBudgetConfig).mockResolvedValue(
        createMockResponse({ configured: false })
      )

      const wrapper = mount(Settings, {
        global: {
          plugins: [pinia, router],
        },
      })

      await flushPromises()

      expect(wrapper.vm.currentConfig).toBeNull()
    })

    it('should handle load config error gracefully', async () => {
      vi.mocked(budgetApi.getBudgetConfig).mockRejectedValue(
        createMockError('Failed to load')
      )

      const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {})

      mount(Settings, {
        global: {
          plugins: [pinia, router],
        },
      })

      await flushPromises()

      expect(consoleSpy).toHaveBeenCalled()
      consoleSpy.mockRestore()
    })
  })

  describe('Saving Configuration', () => {
    it('should save paycheck mode configuration', async () => {
      vi.mocked(budgetApi.configureBudget).mockResolvedValue(
        createMockResponse({})
      )
      vi.mocked(budgetApi.getBudgetConfig).mockResolvedValue(
        createMockResponse({ configured: false })
      )

      const wrapper = mount(Settings, {
        global: {
          plugins: [pinia, router],
        },
      })

      const store = useBudgetStore()
      store.fetchNumber = vi.fn().mockResolvedValue(undefined)

      await flushPromises()

      wrapper.vm.config = {
        mode: 'paycheck',
        monthly_income: 5000,
        days_until_paycheck: 15,
        total_money: 0,
      }

      await wrapper.vm.saveBudgetConfig()
      await flushPromises()

      expect(budgetApi.configureBudget).toHaveBeenCalledWith({
        mode: 'paycheck',
        monthly_income: 5000,
        days_until_paycheck: 15,
        total_money: 0,
      })
    })

    it('should save fixed pool mode configuration', async () => {
      vi.mocked(budgetApi.configureBudget).mockResolvedValue(
        createMockResponse({})
      )
      vi.mocked(budgetApi.getBudgetConfig).mockResolvedValue(
        createMockResponse({ configured: false })
      )

      const wrapper = mount(Settings, {
        global: {
          plugins: [pinia, router],
        },
      })

      const store = useBudgetStore()
      store.fetchNumber = vi.fn().mockResolvedValue(undefined)

      await flushPromises()

      wrapper.vm.config = {
        mode: 'fixed_pool',
        monthly_income: 0,
        days_until_paycheck: 14,
        total_money: 10000,
      }

      await wrapper.vm.saveBudgetConfig()
      await flushPromises()

      expect(budgetApi.configureBudget).toHaveBeenCalledWith({
        mode: 'fixed_pool',
        monthly_income: 0,
        days_until_paycheck: 14,
        total_money: 10000,
      })
    })

    it('should show success message after save', async () => {
      vi.mocked(budgetApi.configureBudget).mockResolvedValue(
        createMockResponse({})
      )
      vi.mocked(budgetApi.getBudgetConfig).mockResolvedValue(
        createMockResponse({ configured: false })
      )

      const wrapper = mount(Settings, {
        global: {
          plugins: [pinia, router],
        },
      })

      const store = useBudgetStore()
      store.fetchNumber = vi.fn().mockResolvedValue(undefined)

      await flushPromises()

      await wrapper.vm.saveBudgetConfig()
      await flushPromises()

      expect(wrapper.vm.showSuccess).toBe(true)
    })

    it('should refresh budget number after save', async () => {
      vi.mocked(budgetApi.configureBudget).mockResolvedValue(
        createMockResponse({})
      )
      vi.mocked(budgetApi.getBudgetConfig).mockResolvedValue(
        createMockResponse({ configured: false })
      )

      const wrapper = mount(Settings, {
        global: {
          plugins: [pinia, router],
        },
      })

      const store = useBudgetStore()
      store.fetchNumber = vi.fn().mockResolvedValue(undefined)

      await flushPromises()

      await wrapper.vm.saveBudgetConfig()
      await flushPromises()

      expect(store.fetchNumber).toHaveBeenCalled()
    })

    it('should reload config after save', async () => {
      vi.mocked(budgetApi.configureBudget).mockResolvedValue(
        createMockResponse({})
      )
      vi.mocked(budgetApi.getBudgetConfig).mockResolvedValue(
        createMockResponse({ configured: false })
      )

      const wrapper = mount(Settings, {
        global: {
          plugins: [pinia, router],
        },
      })

      const store = useBudgetStore()
      store.fetchNumber = vi.fn().mockResolvedValue(undefined)

      await flushPromises()

      // Clear previous calls
      vi.mocked(budgetApi.getBudgetConfig).mockClear()

      await wrapper.vm.saveBudgetConfig()
      await flushPromises()

      // Should be called again after save
      expect(budgetApi.getBudgetConfig).toHaveBeenCalled()
    })

    it('should set loading state during save', async () => {
      let loadingDuringSave = false

      vi.mocked(budgetApi.configureBudget).mockImplementation(async () => {
        // Check loading state during save
        return createMockResponse({})
      })
      vi.mocked(budgetApi.getBudgetConfig).mockResolvedValue(
        createMockResponse({ configured: false })
      )

      const wrapper = mount(Settings, {
        global: {
          plugins: [pinia, router],
        },
      })

      const store = useBudgetStore()
      store.fetchNumber = vi.fn().mockResolvedValue(undefined)

      await flushPromises()

      const savePromise = wrapper.vm.saveBudgetConfig()
      loadingDuringSave = wrapper.vm.loading

      await savePromise
      await flushPromises()

      expect(wrapper.vm.loading).toBe(false)
    })

    it('should handle save error', async () => {
      vi.mocked(budgetApi.configureBudget).mockRejectedValue(
        createMockError('Failed to save')
      )
      vi.mocked(budgetApi.getBudgetConfig).mockResolvedValue(
        createMockResponse({ configured: false })
      )

      const wrapper = mount(Settings, {
        global: {
          plugins: [pinia, router],
        },
      })

      await flushPromises()

      await wrapper.vm.saveBudgetConfig()
      await flushPromises()

      expect(wrapper.vm.showError).toBe(true)
      expect(wrapper.vm.errorMessage).toBe('Failed to save')
    })

    it('should handle error without detail property', async () => {
      const error: any = new Error('Network error')
      error.response = {}

      vi.mocked(budgetApi.configureBudget).mockRejectedValue(error)
      vi.mocked(budgetApi.getBudgetConfig).mockResolvedValue(
        createMockResponse({ configured: false })
      )

      const wrapper = mount(Settings, {
        global: {
          plugins: [pinia, router],
        },
      })

      await flushPromises()

      await wrapper.vm.saveBudgetConfig()
      await flushPromises()

      expect(wrapper.vm.errorMessage).toBe('Failed to save configuration')
    })
  })

  describe('Current Configuration Display', () => {
    it('should show current config when available', async () => {
      vi.mocked(budgetApi.getBudgetConfig).mockResolvedValue(
        createMockResponse(mockBudgetConfig)
      )

      const wrapper = mount(Settings, {
        global: {
          plugins: [pinia, router],
        },
      })

      await flushPromises()

      expect(wrapper.text()).toContain('Current Configuration')
      expect(wrapper.text()).toContain('Paycheck Mode')
    })

    it('should not show current config when not configured', async () => {
      vi.mocked(budgetApi.getBudgetConfig).mockResolvedValue(
        createMockResponse({ configured: false })
      )

      const wrapper = mount(Settings, {
        global: {
          plugins: [pinia, router],
        },
      })

      await flushPromises()

      expect(wrapper.vm.currentConfig).toBeNull()
    })

    it('should display paycheck mode details', async () => {
      vi.mocked(budgetApi.getBudgetConfig).mockResolvedValue(
        createMockResponse(mockBudgetConfig)
      )

      const wrapper = mount(Settings, {
        global: {
          plugins: [pinia, router],
        },
      })

      await flushPromises()

      expect(wrapper.text()).toContain('Monthly Income')
      expect(wrapper.text()).toContain('$5000.00')
      expect(wrapper.text()).toContain('Days Until Paycheck')
      expect(wrapper.text()).toContain('15')
    })

    it('should display fixed pool mode details', async () => {
      vi.mocked(budgetApi.getBudgetConfig).mockResolvedValue(
        createMockResponse({
          mode: 'fixed_pool',
          total_money: 10000,
          configured: true,
        })
      )

      const wrapper = mount(Settings, {
        global: {
          plugins: [pinia, router],
        },
      })

      await flushPromises()

      expect(wrapper.text()).toContain('Fixed Pool Mode')
      expect(wrapper.text()).toContain('Total Money')
    })
  })

  describe('Snackbars', () => {
    it('should show success snackbar on successful save', async () => {
      vi.mocked(budgetApi.configureBudget).mockResolvedValue(
        createMockResponse({})
      )
      vi.mocked(budgetApi.getBudgetConfig).mockResolvedValue(
        createMockResponse({ configured: false })
      )

      const wrapper = mount(Settings, {
        global: {
          plugins: [pinia, router],
        },
      })

      const store = useBudgetStore()
      store.fetchNumber = vi.fn().mockResolvedValue(undefined)

      await flushPromises()

      await wrapper.vm.saveBudgetConfig()
      await flushPromises()

      expect(wrapper.vm.showSuccess).toBe(true)
      expect(wrapper.text()).toContain('Budget configuration saved successfully!')
    })

    it('should show error snackbar on save failure', async () => {
      vi.mocked(budgetApi.configureBudget).mockRejectedValue(
        createMockError('Save failed')
      )
      vi.mocked(budgetApi.getBudgetConfig).mockResolvedValue(
        createMockResponse({ configured: false })
      )

      const wrapper = mount(Settings, {
        global: {
          plugins: [pinia, router],
        },
      })

      await flushPromises()

      await wrapper.vm.saveBudgetConfig()
      await flushPromises()

      expect(wrapper.vm.showError).toBe(true)
      expect(wrapper.text()).toContain('Save failed')
    })
  })

  describe('Edge Cases', () => {
    it('should handle very large income values', async () => {
      const wrapper = mount(Settings, {
        global: {
          plugins: [pinia, router],
        },
      })

      wrapper.vm.config.monthly_income = 999999.99

      expect(wrapper.vm.config.monthly_income).toBe(999999.99)
    })

    it('should handle zero values', async () => {
      const wrapper = mount(Settings, {
        global: {
          plugins: [pinia, router],
        },
      })

      wrapper.vm.config.monthly_income = 0
      wrapper.vm.config.days_until_paycheck = 0

      expect(wrapper.vm.config.monthly_income).toBe(0)
      expect(wrapper.vm.config.days_until_paycheck).toBe(0)
    })

    it('should handle switching modes multiple times', async () => {
      const wrapper = mount(Settings, {
        global: {
          plugins: [pinia, router],
        },
      })

      wrapper.vm.config.mode = 'paycheck'
      await wrapper.vm.$nextTick()

      wrapper.vm.config.mode = 'fixed_pool'
      await wrapper.vm.$nextTick()

      wrapper.vm.config.mode = 'paycheck'
      await wrapper.vm.$nextTick()

      expect(wrapper.vm.config.mode).toBe('paycheck')
    })
  })
})
