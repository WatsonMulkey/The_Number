/**
 * Input sanitization utilities
 *
 * Provides functions to sanitize user input and prevent XSS attacks.
 */

/**
 * Sanitize a string by removing HTML tags and dangerous characters.
 * This prevents XSS attacks by stripping all HTML/script content.
 *
 * @param input - The string to sanitize
 * @returns Sanitized string safe for display
 */
export function sanitizeText(input: string): string {
  if (!input) return ''

  // Remove HTML tags
  let sanitized = input.replace(/<[^>]*>/g, '')

  // Remove script-like patterns
  sanitized = sanitized.replace(/javascript:/gi, '')
  sanitized = sanitized.replace(/on\w+\s*=/gi, '')

  // Trim and normalize whitespace
  sanitized = sanitized.trim()

  return sanitized
}

/**
 * Sanitize a number input to ensure it's a valid number.
 *
 * @param input - The input to sanitize
 * @param min - Minimum allowed value (optional)
 * @param max - Maximum allowed value (optional)
 * @returns Sanitized number or null if invalid
 */
export function sanitizeNumber(
  input: string | number,
  min?: number,
  max?: number
): number | null {
  const num = typeof input === 'string' ? parseFloat(input) : input

  if (isNaN(num) || !isFinite(num)) {
    return null
  }

  if (min !== undefined && num < min) {
    return min
  }

  if (max !== undefined && num > max) {
    return max
  }

  return num
}

/**
 * Validate and sanitize email address.
 *
 * @param email - Email address to validate
 * @returns Sanitized email or null if invalid
 */
export function sanitizeEmail(email: string): string | null {
  if (!email) return null

  const sanitized = email.trim().toLowerCase()

  // Basic email validation regex
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/

  if (!emailRegex.test(sanitized)) {
    return null
  }

  return sanitized
}

/**
 * Sanitize username to only allow alphanumeric and underscores.
 *
 * @param username - Username to sanitize
 * @returns Sanitized username
 */
export function sanitizeUsername(username: string): string {
  if (!username) return ''

  // Only allow alphanumeric, underscores, and hyphens
  return username.replace(/[^a-zA-Z0-9_-]/g, '').trim()
}
