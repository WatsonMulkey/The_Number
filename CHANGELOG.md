# Changelog

All notable changes to The Number will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2026-04-10

### Fixed
- **Daily budget no longer inflates mid-cycle** (FOI-137) — `the_number` now subtracts cycle-to-date spending from the remaining budget before dividing by remaining days. Previously, the full cycle budget was divided by fewer remaining days, overestimating the daily limit by up to 600% late in the cycle.
- **Timezone-correct cycle spending queries** — both the FOI-137 fix and the pre-existing pool auto-roll code now use UTC-aware date boundaries via `date_to_utc()`, preventing midnight-boundary miscounting for non-UTC users.

### Added
- `date_to_utc()` helper in `api/utils/dates.py` for timezone-correct date boundary conversions
- `/api/version` endpoint returning current version
- Version display on Settings page (FOI-138)
- Backfilled CHANGELOG entries from v1.0.0 through v1.1.0

## [1.0.3] - 2026-04-05

### Fixed
- 5 Drew beta bugs (FOI-109 through FOI-113): UTC timestamps, pool button gate, navbar a11y, contrast, test field names
- Mobile bottom nav broken by `tag="nav"` prop — wrapped in plain `<nav>` element
- `v-model` on read-only computed — switched to `:model-value`

## [1.0.2] - 2026-04-04

### Fixed
- Timezone source guard (FOI-104)
- Axios pinned to 1.14.0 (supply chain attack on 1.14.1 / 0.30.4)
- `/api/number` integration tests (4 test cases)

## [1.0.1] - 2026-03-17

### Fixed
- **Critical daily budget 2.17x overstatement** for biweekly pay — added `cycle_ratio` pro-rate factor
- Pool income corruption and timezone bugs (FOI-103, FOI-104)

## [1.0.0] - 2026-03-13

### Added
- Beta launch with invite codes
- Pool / carry-over feature
- PWA badge, expense frequency, CSV/Excel export
- UI rebrand: Nunito + forest green + warm cream

### Fixed
- Pre-launch QA: logout crash, favicon 404, Zod warnings, payday off-by-one

## [0.9.0] - 2025-12-16

### Added
- Comprehensive codebase review (docs/CODEBASE_REVIEW.md)
- Comprehensive test plan (docs/TEST_PLAN.md)
- Semantic versioning system
- Frontend environment variable configuration (.env, .env.example)

### Fixed
- **CRITICAL:** Router history bug - Fixed `import.meta.url` to `import.meta.env.BASE_URL` in router config
  - Impact: Navigation will now work correctly in production builds
  - File: `frontend/src/router/index.ts:5`

- **CRITICAL:** Transaction delete bug - Uncommented API call for transaction deletion
  - Impact: Transaction deletions now persist to database instead of only removing from local state
  - File: `frontend/src/views/Transactions.vue:178`

- **CRITICAL:** Hardcoded API URL - Made API base URL configurable via environment variable
  - Impact: Application can now be deployed to different environments
  - File: `frontend/src/services/api.ts:4`

### Changed
- N/A

### Deprecated
- N/A

### Removed
- N/A

### Security
- N/A

---

## Version Naming Scheme

- **0.x.x** - Pre-release (not production-ready)
- **1.0.0** - First production release (with PWA + Gumroad payment)
- **1.x.x** - Minor features, non-breaking changes
- **2.x.x** - Major features, potential breaking changes

## Roadmap to 1.0.0

- [ ] PWA infrastructure (manifest + service worker)
- [ ] Gumroad payment integration
- [ ] User authentication
- [ ] Multi-user data isolation
- [ ] Deployment to production
- [ ] Public launch

---

[Unreleased]: https://github.com/WatsonMulkey/The_Number/compare/v0.9.0...HEAD
[0.9.0]: https://github.com/WatsonMulkey/The_Number/releases/tag/v0.9.0
