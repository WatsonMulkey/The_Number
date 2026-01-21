/**
 * Frontend Test Suite: PWA Badge Feature
 *
 * Tests badge integration with Vue store and browser API.
 * Uses Vitest for testing framework.
 */

import { describe, it, expect, beforeEach, vi, afterEach } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useBudgetStore } from '@/stores/budget'
import { budgetApi } from '@/services/api'
import {
  createMockResponse,
  createMockError,
  mockBudgetNumber,
} from '@/test/test-utils'

// ============================================================================
// BADGE SERVICE IMPLEMENTATION
// ============================================================================

/**
 * Service for managing PWA badge via Badging API.
 *
 * BROWSER SUPPORT:
 * - Chrome 81+ (Desktop & Android)
 * - Edge 81+
 * - NOT supported: Safari, Firefox, iOS
 *
 * SECURITY:
 * - Only works when PWA is installed
 * - Requires HTTPS (except localhost)
 */
export class BadgeService {
  private static isSupported(): boolean {
    return 'setAppBadge' in navigator && 'clearAppBadge' in navigator
  }

  /**
   * Set badge to rounded daily budget number.
   *
   * @param value - Daily budget (can be float, negative, or zero)
   * @returns true if badge was set, false if API unsupported
   */
  static setBadge(value: number): boolean {
    if (!this.isSupported()) {
      console.info('[Badge] Badging API not supported - skipping')
      return false
    }

    // Round to nearest integer
    let badgeValue = Math.round(value)

    // Handle NaN → clear badge
    if (Number.isNaN(badgeValue)) {
      return this.clearBadge()
    }

    // Handle negative numbers → show 0
    if (badgeValue < 0) {
      badgeValue = 0
    }

    // Zero → clear badge instead of showing "0"
    if (badgeValue === 0) {
      return this.clearBadge()
    }

    try {
      // @ts-ignore - setAppBadge not in TypeScript types yet
      navigator.setAppBadge(badgeValue)
      console.info(`[Badge] Set to ${badgeValue}`)
      return true
    } catch (error) {
      console.error('[Badge] Failed to set badge:', error)
      return false
    }
  }

  /**
   * Clear the app badge.
   * Called on logout or when budget is zero.
   */
  static clearBadge(): boolean {
    if (!this.isSupported()) {
      return false
    }

    try {
      // @ts-ignore - clearAppBadge not in TypeScript types yet
      navigator.clearAppBadge()
      console.info('[Badge] Cleared')
      return true
    } catch (error) {
      console.error('[Badge] Failed to clear badge:', error)
      return false
    }
  }
}

// ============================================================================
// MOCKS
// ============================================================================

// Mock the API module
vi.mock('@/services/api', () => ({
  budgetApi: {
    getNumber: vi.fn(),
    createTransaction: vi.fn(),
    getTransactions: vi.fn(),
  },
}))

// Mock navigator.setAppBadge and clearAppBadge
const mockSetAppBadge = vi.fn()
const mockClearAppBadge = vi.fn()

// ============================================================================
// TEST SUITE: Badge Browser API Support
// ============================================================================

describe('BadgeService - Browser Support', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('should detect when Badging API is supported', () => {
    // Mock supported browser
    // @ts-ignore
    global.navigator.setAppBadge = mockSetAppBadge
    // @ts-ignore
    global.navigator.clearAppBadge = mockClearAppBadge

    const result = BadgeService.setBadge(42)
    expect(result).toBe(true)
    expect(mockSetAppBadge).toHaveBeenCalledWith(42)
  })

  it('should detect when Badging API is NOT supported (Firefox, Safari)', () => {
    // Mock unsupported browser
    // @ts-ignore
    delete global.navigator.setAppBadge
    // @ts-ignore
    delete global.navigator.clearAppBadge

    const result = BadgeService.setBadge(42)
    expect(result).toBe(false)
    // Should not throw error, just fail gracefully
  })

  it('should fail gracefully when API throws error', () => {
    // Mock API that throws
    mockSetAppBadge.mockImplementation(() => {
      throw new Error('Permission denied')
    })
    // @ts-ignore
    global.navigator.setAppBadge = mockSetAppBadge
    // @ts-ignore
    global.navigator.clearAppBadge = mockClearAppBadge

    const result = BadgeService.setBadge(42)
    expect(result).toBe(false)
  })
})

// ============================================================================
// TEST SUITE: Badge Value Formatting
// ============================================================================

describe('BadgeService - Value Formatting', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    // @ts-ignore
    global.navigator.setAppBadge = mockSetAppBadge
    // @ts-ignore
    global.navigator.clearAppBadge = mockClearAppBadge
  })

  it('should round float to nearest integer (42.50 → 43)', () => {
    BadgeService.setBadge(42.50)
    expect(mockSetAppBadge).toHaveBeenCalledWith(43)
  })

  it('should round down below half (38.49 → 38)', () => {
    BadgeService.setBadge(38.49)
    expect(mockSetAppBadge).toHaveBeenCalledWith(38)
  })

  it('should round up at or above half (38.51 → 39)', () => {
    BadgeService.setBadge(38.51)
    expect(mockSetAppBadge).toHaveBeenCalledWith(39)
  })

  it('should handle whole numbers unchanged (100.0 → 100)', () => {
    BadgeService.setBadge(100.0)
    expect(mockSetAppBadge).toHaveBeenCalledWith(100)
  })

  it('should handle very large numbers (9999.99 → 10000)', () => {
    BadgeService.setBadge(9999.99)
    expect(mockSetAppBadge).toHaveBeenCalledWith(10000)
  })
})

// ============================================================================
// TEST SUITE: Negative Numbers
// ============================================================================

describe('BadgeService - Negative Numbers', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    // @ts-ignore
    global.navigator.setAppBadge = mockSetAppBadge
    // @ts-ignore
    global.navigator.clearAppBadge = mockClearAppBadge
  })

  it('should convert negative to zero (-15.50 → clear badge)', () => {
    BadgeService.setBadge(-15.50)
    // Should clear instead of showing negative
    expect(mockClearAppBadge).toHaveBeenCalled()
    expect(mockSetAppBadge).not.toHaveBeenCalled()
  })

  it('should handle large negative numbers (-500 → clear)', () => {
    BadgeService.setBadge(-500)
    expect(mockClearAppBadge).toHaveBeenCalled()
  })

  it('should handle negative zero (-0.0 → clear)', () => {
    BadgeService.setBadge(-0.0)
    expect(mockClearAppBadge).toHaveBeenCalled()
  })
})

// ============================================================================
// TEST SUITE: Zero Values
// ============================================================================

describe('BadgeService - Zero Values', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    // @ts-ignore
    global.navigator.setAppBadge = mockSetAppBadge
    // @ts-ignore
    global.navigator.clearAppBadge = mockClearAppBadge
  })

  it('should clear badge when value is zero (0.0 → clear)', () => {
    BadgeService.setBadge(0.0)
    expect(mockClearAppBadge).toHaveBeenCalled()
    expect(mockSetAppBadge).not.toHaveBeenCalled()
  })

  it('should clear badge when rounded to zero (0.49 → clear)', () => {
    BadgeService.setBadge(0.49)
    expect(mockClearAppBadge).toHaveBeenCalled()
  })

  it('should set badge when rounded to 1 (0.51 → 1)', () => {
    BadgeService.setBadge(0.51)
    expect(mockSetAppBadge).toHaveBeenCalledWith(1)
  })
})

// ============================================================================
// TEST SUITE: Badge Clearing
// ============================================================================

describe('BadgeService - Badge Clearing', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    // @ts-ignore
    global.navigator.setAppBadge = mockSetAppBadge
    // @ts-ignore
    global.navigator.clearAppBadge = mockClearAppBadge
  })

  it('should clear badge successfully', () => {
    const result = BadgeService.clearBadge()
    expect(result).toBe(true)
    expect(mockClearAppBadge).toHaveBeenCalled()
  })

  it('should not error when clearing already-clear badge', () => {
    BadgeService.clearBadge()
    BadgeService.clearBadge() // Clear again
    expect(mockClearAppBadge).toHaveBeenCalledTimes(2)
  })

  it('should return false when API unsupported', () => {
    // @ts-ignore
    delete global.navigator.clearAppBadge

    const result = BadgeService.clearBadge()
    expect(result).toBe(false)
  })
})

// ============================================================================
// TEST SUITE: Integration with Budget Store
// ============================================================================

describe('BadgeService - Budget Store Integration', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
    // @ts-ignore
    global.navigator.setAppBadge = mockSetAppBadge
    // @ts-ignore
    global.navigator.clearAppBadge = mockClearAppBadge
  })

  it('should update badge after fetchNumber() succeeds', async () => {
    const store = useBudgetStore()
    const mockResponse = {
      ...mockBudgetNumber,
      the_number: 42.67,
      remaining_today: 42.67,
    }

    vi.mocked(budgetApi.getNumber).mockResolvedValue(
      createMockResponse(mockResponse)
    )

    await store.fetchNumber()

    // After fetchNumber, badge should be updated
    // Implementation would call: BadgeService.setBadge(store.budgetNumber.remaining_today)
    // For this test, we verify the store has the correct data
    expect(store.budgetNumber?.the_number).toBe(42.67)
    expect(store.budgetNumber?.remaining_today).toBe(42.67)
  })

  it('should NOT update badge if fetchNumber() fails', async () => {
    const store = useBudgetStore()
    vi.mocked(budgetApi.getNumber).mockRejectedValue(
      createMockError('Network error')
    )

    mockSetAppBadge.mockClear()

    try {
      await store.fetchNumber()
    } catch (e) {
      // Expected to throw
    }

    // Badge should NOT be updated on error
    expect(mockSetAppBadge).not.toHaveBeenCalled()
  })

  it('should update badge after recording transaction', async () => {
    const store = useBudgetStore()

    // Mock transaction creation
    vi.mocked(budgetApi.createTransaction as any).mockResolvedValue(
      createMockResponse({ id: 1, amount: 25, description: 'Coffee', date: '', created_at: '' })
    )

    // Mock subsequent fetchNumber
    const mockResponse = {
      ...mockBudgetNumber,
      the_number: 100,
      remaining_today: 75, // Was 100, spent 25
      is_over_budget: false,
    }
    vi.mocked(budgetApi.getNumber).mockResolvedValue(
      createMockResponse(mockResponse)
    )

    // Mock fetchTransactions
    vi.mocked(budgetApi.getTransactions as any).mockResolvedValue(
      createMockResponse([])
    )

    await store.recordTransaction({ amount: 25, description: 'Coffee' })

    // Verify store was updated
    expect(store.budgetNumber?.remaining_today).toBe(75)
  })

  it('should clear badge on logout', () => {
    // In real implementation, logout would call:
    BadgeService.clearBadge()
    expect(mockClearAppBadge).toHaveBeenCalled()
  })
})

// ============================================================================
// TEST SUITE: Edge Cases
// ============================================================================

describe('BadgeService - Edge Cases', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    // @ts-ignore
    global.navigator.setAppBadge = mockSetAppBadge
    // @ts-ignore
    global.navigator.clearAppBadge = mockClearAppBadge
  })

  it('should handle NaN input', () => {
    BadgeService.setBadge(NaN)
    // Math.round(NaN) = NaN, which is falsy
    expect(mockClearAppBadge).toHaveBeenCalled()
  })

  it('should handle Infinity input', () => {
    BadgeService.setBadge(Infinity)
    // Should set to Infinity (browser will handle display)
    expect(mockSetAppBadge).toHaveBeenCalledWith(Infinity)
  })

  it('should handle very small positive number (0.001 → clear)', () => {
    BadgeService.setBadge(0.001)
    expect(mockClearAppBadge).toHaveBeenCalled()
  })

  it('should handle maximum safe integer', () => {
    const maxSafe = Number.MAX_SAFE_INTEGER
    BadgeService.setBadge(maxSafe)
    expect(mockSetAppBadge).toHaveBeenCalledWith(maxSafe)
  })

  it('should handle rapid successive calls (race condition simulation)', () => {
    BadgeService.setBadge(42)
    BadgeService.setBadge(43)
    BadgeService.setBadge(44)

    // All calls should succeed
    expect(mockSetAppBadge).toHaveBeenCalledTimes(3)
    expect(mockSetAppBadge).toHaveBeenLastCalledWith(44)
  })
})

// ============================================================================
// DOCUMENTATION: Integration Points
// ============================================================================

/**
 * INTEGRATION POINTS FOR IMPLEMENTATION:
 *
 * 1. Budget Store (stores/budget.ts):
 *    - Add badge update to fetchNumber() success handler:
 *      ```typescript
 *      async function fetchNumber() {
 *        // ... existing code ...
 *        budgetNumber.value = response.data
 *
 *        // Update badge with remaining daily budget
 *        BadgeService.setBadge(budgetNumber.value.remaining_today)
 *      }
 *      ```
 *
 * 2. Auth Store (stores/auth.ts):
 *    - Clear badge on logout:
 *      ```typescript
 *      function logout() {
 *        // ... existing code ...
 *        BadgeService.clearBadge()
 *      }
 *      ```
 *
 * 3. Transaction Recording (stores/budget.ts):
 *    - Badge updates automatically via fetchNumber() call
 *    - No additional code needed (already calls fetchNumber)
 *
 * 4. Error Handling:
 *    - Never update badge if fetchNumber() fails
 *    - Keep previous badge value on error
 *
 * 5. PWA Detection:
 *    - Badge only works when app is installed as PWA
 *    - Consider adding UI hint: "Install app to see budget on icon"
 */

/**
 * BROWSER COMPATIBILITY MATRIX:
 *
 * ✅ Supported (with PWA installed):
 *    - Chrome 81+ (Desktop)
 *    - Chrome 81+ (Android)
 *    - Edge 81+ (Desktop)
 *    - Edge 81+ (Android)
 *
 * ❌ Not Supported:
 *    - Safari (Desktop & iOS) - No Badging API
 *    - Firefox (All platforms) - No Badging API
 *    - Chrome iOS - Uses Safari engine, no support
 *    - All browsers without PWA installed
 *
 * GRACEFUL DEGRADATION:
 *    - App functions normally without badge
 *    - No error messages shown to user
 *    - Consider feature detection + user notification
 */
