import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import NumberDisplay from './NumberDisplay.vue'

describe('NumberDisplay Component', () => {
  describe('Rendering', () => {
    it('should render the number correctly', () => {
      const wrapper = mount(NumberDisplay, {
        props: {
          theNumber: 100.50,
          mode: 'paycheck',
        },
      })

      expect(wrapper.text()).toContain('$100.50')
    })

    it('should display "Your Number is..." heading', () => {
      const wrapper = mount(NumberDisplay, {
        props: {
          theNumber: 100,
          mode: 'paycheck',
        },
      })

      expect(wrapper.text()).toContain('Your Number is...')
    })

    it('should format number with 2 decimal places', () => {
      const wrapper = mount(NumberDisplay, {
        props: {
          theNumber: 100,
          mode: 'paycheck',
        },
      })

      expect(wrapper.text()).toContain('$100.00')
    })
  })

  describe('Mode-specific Subtitle', () => {
    it('should show paycheck mode subtitle with day name', () => {
      const wrapper = mount(NumberDisplay, {
        props: {
          theNumber: 100,
          mode: 'paycheck',
          daysRemaining: 5,
        },
      })

      // Should show "per day through [DayName]"
      expect(wrapper.text()).toContain('per day through')
    })

    it('should show fixed pool mode subtitle', () => {
      const wrapper = mount(NumberDisplay, {
        props: {
          theNumber: 100,
          mode: 'fixed_pool',
        },
      })

      expect(wrapper.text()).toContain('per day with current budget')
    })

    it('should show payday message when days remaining is 0', () => {
      const wrapper = mount(NumberDisplay, {
        props: {
          theNumber: 100,
          mode: 'paycheck',
          daysRemaining: 0,
        },
      })

      expect(wrapper.text()).toContain('payday!')
    })
  })

  describe('Over Budget State', () => {
    it('should apply over-budget class when isOverBudget is true', () => {
      const wrapper = mount(NumberDisplay, {
        props: {
          theNumber: 100,
          mode: 'paycheck',
          isOverBudget: true,
        },
      })

      const numberElement = wrapper.find('.the-number')
      expect(numberElement.classes()).toContain('over-budget')
    })

    it('should not apply over-budget class when isOverBudget is false', () => {
      const wrapper = mount(NumberDisplay, {
        props: {
          theNumber: 100,
          mode: 'paycheck',
          isOverBudget: false,
        },
      })

      const numberElement = wrapper.find('.the-number')
      expect(numberElement.classes()).not.toContain('over-budget')
    })

    it('should not apply over-budget class by default', () => {
      const wrapper = mount(NumberDisplay, {
        props: {
          theNumber: 100,
          mode: 'paycheck',
        },
      })

      const numberElement = wrapper.find('.the-number')
      expect(numberElement.classes()).not.toContain('over-budget')
    })
  })

  describe('Today\'s Spending Display', () => {
    it('should show spending card when todaySpending is greater than 0', () => {
      const wrapper = mount(NumberDisplay, {
        props: {
          theNumber: 100,
          mode: 'paycheck',
          todaySpending: 50,
          remainingToday: 50,
        },
      })

      expect(wrapper.text()).toContain('Today\'s Spending: $50.00')
      expect(wrapper.text()).toContain('Remaining: $50.00')
    })

    it('should not show spending card when todaySpending is 0', () => {
      const wrapper = mount(NumberDisplay, {
        props: {
          theNumber: 100,
          mode: 'paycheck',
          todaySpending: 0,
        },
      })

      expect(wrapper.text()).not.toContain('Today\'s Spending')
    })

    it('should not show spending card when todaySpending is undefined', () => {
      const wrapper = mount(NumberDisplay, {
        props: {
          theNumber: 100,
          mode: 'paycheck',
        },
      })

      expect(wrapper.text()).not.toContain('Today\'s Spending')
    })

    it('should format spending amounts with 2 decimal places', () => {
      const wrapper = mount(NumberDisplay, {
        props: {
          theNumber: 100,
          mode: 'paycheck',
          todaySpending: 25.5,
          remainingToday: 74.5,
        },
      })

      expect(wrapper.text()).toContain('Today\'s Spending: $25.50')
      expect(wrapper.text()).toContain('Remaining: $74.50')
    })
  })

  describe('Spending Percentage', () => {
    it('should calculate spending percentage correctly', () => {
      const wrapper = mount(NumberDisplay, {
        props: {
          theNumber: 100,
          mode: 'paycheck',
          todaySpending: 50,
          remainingToday: 50,
        },
      })

      const progressBar = wrapper.find('.v-progress-linear')
      expect(progressBar.exists()).toBe(true)
    })

    it('should cap spending percentage at 100', () => {
      const wrapper = mount(NumberDisplay, {
        props: {
          theNumber: 100,
          mode: 'paycheck',
          todaySpending: 150,
          remainingToday: -50,
          isOverBudget: true,
        },
      })

      // The computed property should cap at 100
      expect(wrapper.vm.spendingPercentage).toBe(100)
    })

    it('should return 0 percentage when no spending data', () => {
      const wrapper = mount(NumberDisplay, {
        props: {
          theNumber: 100,
          mode: 'paycheck',
        },
      })

      expect(wrapper.vm.spendingPercentage).toBe(0)
    })

    it('should handle zero theNumber gracefully', () => {
      const wrapper = mount(NumberDisplay, {
        props: {
          theNumber: 0,
          mode: 'paycheck',
          todaySpending: 50,
          remainingToday: -50,
        },
      })

      expect(wrapper.vm.spendingPercentage).toBe(0)
    })
  })

  describe('Edge Cases', () => {
    it('should handle negative numbers', () => {
      const wrapper = mount(NumberDisplay, {
        props: {
          theNumber: -50,
          mode: 'paycheck',
        },
      })

      expect(wrapper.text()).toContain('$-50.00')
    })

    it('should handle very large numbers', () => {
      const wrapper = mount(NumberDisplay, {
        props: {
          theNumber: 999999.99,
          mode: 'paycheck',
        },
      })

      expect(wrapper.text()).toContain('$999999.99')
    })

    it('should handle very small decimal numbers', () => {
      const wrapper = mount(NumberDisplay, {
        props: {
          theNumber: 0.01,
          mode: 'paycheck',
        },
      })

      expect(wrapper.text()).toContain('$0.01')
    })

    it('should handle negative remaining today', () => {
      const wrapper = mount(NumberDisplay, {
        props: {
          theNumber: 100,
          mode: 'paycheck',
          todaySpending: 150,
          remainingToday: -50,
        },
      })

      expect(wrapper.text()).toContain('Remaining: $-50.00')
    })
  })

  describe('Props Validation', () => {
    it('should accept all valid props', () => {
      const wrapper = mount(NumberDisplay, {
        props: {
          theNumber: 100,
          mode: 'paycheck',
          todaySpending: 50,
          remainingToday: 50,
          isOverBudget: false,
          daysRemaining: 15,
        },
      })

      expect(wrapper.vm.theNumber).toBe(100)
      expect(wrapper.vm.mode).toBe('paycheck')
      expect(wrapper.vm.todaySpending).toBe(50)
      expect(wrapper.vm.remainingToday).toBe(50)
      expect(wrapper.vm.isOverBudget).toBe(false)
      expect(wrapper.vm.daysRemaining).toBe(15)
    })

    it('should work with minimal required props', () => {
      const wrapper = mount(NumberDisplay, {
        props: {
          theNumber: 100,
          mode: 'fixed_pool',
        },
      })

      expect(wrapper.exists()).toBe(true)
    })
  })
})
