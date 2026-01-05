/**
 * Common validation rules for form inputs.
 * Import and use in any Vue component that needs validation.
 */

export const useValidation = () => {
  const rules = {
    required: (v: any) => !!v || 'This field is required',

    requiredNumber: (v: any) => {
      if (v === null || v === undefined || v === '') return 'This field is required'
      return true
    },

    positive: (v: any) => {
      if (v === null || v === undefined || v === '') return 'Amount is required'
      if (typeof v === 'number' && v <= 0) return 'Must be greater than 0'
      if (typeof v !== 'number') return 'Must be a valid number'
      return true
    },

    maxLength: (max: number) => (v: string) => {
      if (!v) return true
      if (v.length > max) return `Maximum ${max} characters`
      return true
    },

    email: (v: string) => {
      if (!v) return 'Email is required'
      const pattern = /.+@.+\..+/
      if (!pattern.test(v)) return 'Invalid email address'
      return true
    },

    minPassword: (v: string) => {
      if (!v) return 'Password is required'
      if (v.length < 8) return 'Password must be at least 8 characters'
      return true
    },

    minLength: (min: number) => (v: string) => {
      if (!v) return true
      if (v.length < min) return `Minimum ${min} characters`
      return true
    },

    username: (v: string) => {
      if (!v) return 'Username is required'
      if (v.length < 3) return 'Username must be at least 3 characters'
      if (v.length > 50) return 'Username must be less than 50 characters'
      if (!/^[a-zA-Z0-9_-]+$/.test(v)) return 'Username can only contain letters, numbers, underscores, and hyphens'
      return true
    },

    positiveInteger: (v: any) => {
      if (v === null || v === undefined || v === '') return 'This field is required'
      if (typeof v !== 'number' || !Number.isInteger(v)) return 'Must be a whole number'
      if (v <= 0) return 'Must be greater than 0'
      return true
    },

    nonNegative: (v: any) => {
      if (v === null || v === undefined || v === '') return 'This field is required'
      if (typeof v !== 'number') return 'Must be a valid number'
      if (v < 0) return 'Cannot be negative'
      return true
    }
  }

  return { rules }
}
