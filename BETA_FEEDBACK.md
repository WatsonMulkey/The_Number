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
**Status**: Open

CSV/Excel export fails on both mobile (iOS 26.3.1) and desktop browser (Chrome 146.0.7680.76). "Failed to export" error.

**Resolution**: TBD

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

**Resolution**: TBD

---

## Summary Stats

| Category | Count |
|----------|-------|
| Bugs | 1 |
| UX Issues | 2 |
| Feature Requests | 0 |
| General Feedback | 0 |

---

## Known Issues (Pre-Beta)

- `npm audit`: 25 vulns (1 critical) — not user-facing
- EncryptedDatabase only encrypts settings values — expenses/transactions are plaintext
- No password reset flow (manual admin reset only — see ADMIN_PASSWORD_RESET_GUIDE.md)
- No user-delete endpoint
- Test account `testbetacode` exists from invite code verification (user ID 12)
