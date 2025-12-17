# Changelog

All notable changes to The Number will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.9.0] - 2025-12-16

### Added
- Comprehensive codebase review (CODEBASE_REVIEW.md)
- Comprehensive test plan (TEST_PLAN.md)
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
