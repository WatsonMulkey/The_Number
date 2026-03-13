import { z } from 'zod'

/** Schema for the daily budget number response */
export const BudgetNumberSchema = z.object({
  the_number: z.number(),
  mode: z.string(),
  total_income: z.number().optional(),
  total_expenses: z.number(),
  remaining_money: z.number().optional(),
  days_remaining: z.number().optional(),
  total_money: z.number().nullable().optional(),
  today_spending: z.number(),
  remaining_today: z.number(),
  is_over_budget: z.boolean(),
  adjusted_daily_budget: z.number().nullable().optional(),
  original_daily_budget: z.number().nullable().optional(),
  tomorrow_daily_budget: z.number().optional(),
  pool_balance: z.number(),
  pool_enabled: z.boolean(),
  pending_pool_contribution: z.number().nullable().optional(),
})

/** Schema for a monthly expense */
export const ExpenseSchema = z.object({
  id: z.number(),
  name: z.string(),
  amount: z.number(),
  is_fixed: z.boolean(),
  frequency: z.enum(['weekly', 'monthly']),
  created_at: z.string(),
  updated_at: z.string(),
})

/** Schema for a spending transaction */
export const TransactionSchema = z.object({
  id: z.number(),
  date: z.string(),
  amount: z.number(),
  description: z.string(),
  category: z.string().optional(),
  created_at: z.string(),
})

/** Schema for budget config */
export const BudgetConfigSchema = z.object({
  mode: z.enum(['paycheck', 'fixed_pool']),
  monthly_income: z.number().optional(),
  days_until_paycheck: z.number().optional(),
  next_payday_date: z.string().optional(),
  pay_frequency_days: z.number().optional(),
  total_money: z.number().optional(),
  target_end_date: z.string().optional(),
  daily_spending_limit: z.number().optional(),
  configured: z.boolean().optional(),
})

/**
 * Validate API response data against a zod schema.
 * Logs a warning on validation failure but returns the data
 * regardless to avoid breaking the app on unexpected fields.
 */
export function validateResponse<T>(schema: z.ZodSchema<T>, data: unknown, label: string): T {
  const result = schema.safeParse(data)
  if (!result.success) {
    console.warn(`[API Validation] ${label} response shape mismatch:`, result.error.issues)
    // Return data as-is to avoid breaking the app -- this is a warning, not a blocker
    return data as T
  }
  return result.data
}
