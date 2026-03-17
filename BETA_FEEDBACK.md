# The Number - Beta Feedback Log

**Beta Start**: 2026-03-13
**Testers**: 10 invited
**Invite Code**: FOIL2026
**App URL**: https://foil.engineering/TheNumber

---

## Feedback

### [2026-03-13] - Beta Tester #1
**Type**: Bug
**Severity**: High
**Status**: Fixed

CSV/Excel export fails on both mobile (iOS 26.3.1) and desktop browser (Chrome 146.0.7680.76). "Failed to export" error.

**Resolution**: Fixed — export endpoint was calling `db.execute()` which doesn't exist on EncryptedDatabase. Rewrote to use `db.get_setting()`, `db.get_expenses()`, `db.get_transactions()`. Deployed 2026-03-13.

---

### [2026-03-13] - Beta Tester #1
**Type**: UX
**Severity**: Low
**Status**: Open

App is USD-only ($ symbol throughout). Not broken for dollar users, but could cause issues if exported data with `$` is imported into software that auto-converts currencies for non-USD users.

**Resolution**: TBD

---

### [2026-03-13] - Beta Tester #1
**Type**: UX
**Severity**: Low
**Status**: Open

Landing page: no "Already have an account? Log in" link visible until you click "Join the Beta". There is one at the bottom of the page but not near the top CTA. Inconsistent — brain itch.

**Resolution**: Fixed — added "Already have an account? Log in" link under hero CTA. Deployed 2026-03-13.

---

### [2026-03-16] - Beta Tester #2 (Jay)
**Type**: General Feedback
**Severity**: N/A
**Status**: N/A

Positive reception: loved how easy setup was, appreciates the "chill" approach to budgeting. Says it gets them thinking about the big picture and getting more detailed with expenses over time.

---

### [2026-03-16] - Beta Tester #2 (Jay)
**Type**: Bug
**Severity**: High
**Status**: Open

Number appears way too high. Setup: $2,000 every 2 weeks ($4,000/mo), ~$2,300/mo in expenses. Number shows $386/day, which implies ~$12k/mo income with no expenses deducted. Expected: ~$1,700/mo discretionary → ~$56/day.

**Root Cause**: `calculate_paycheck_mode()` divided full monthly surplus ($1,700) by days until next paycheck (~4 days) instead of pro-rating to the pay cycle. For biweekly pay, this overstated The Number by 2.17x (30.44/14). The same bug existed in the pool/leftover calculation, inflating pool contributions by ~$900 per pay period.

**Resolution**: Fixed 2026-03-16. Pro-rated monthly income and expenses to pay cycle length in both `src/calculator.py` and `api/main.py`. Added one-time pool balance reset for all users (flag: `pool_formula_fixed`). Deployed same day.

---

### [2026-03-16] - Beta Tester #2 (Jay)
**Type**: Feature Request
**Severity**: Medium
**Status**: Open

Wants ability to manually adjust The Number downward to save toward goals. Example: rent is $1,500/mo (~$50/day), but wants to budget for $1,800/mo rent (~$60/day) by voluntarily lowering daily spend by $10. Essentially a "savings goal" or "manual override" that reduces The Number to help save for a specific target.

**Resolution**: TBD

---

## Summary Stats

| Category | Count |
|----------|-------|
| Bugs | 2 |
| UX Issues | 2 |
| Feature Requests | 1 |
| General Feedback | 1 |

---

## Known Issues (Pre-Beta)

- `npm audit`: 25 vulns (1 critical) — not user-facing
- EncryptedDatabase only encrypts settings values — expenses/transactions are plaintext
- No password reset flow (manual admin reset only — see ADMIN_PASSWORD_RESET_GUIDE.md)
- No user-delete endpoint
- Test account `testbetacode` exists from invite code verification (user ID 12)
