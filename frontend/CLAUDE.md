# The Number - Budget PWA

## Status: Active — QA phase, beta feedback

## Tech Stack
- **Frontend**: Vue 3 + TypeScript + Vuetify 3
- **State**: Pinia stores
- **Build**: Vite + vite-plugin-pwa
- **Backend**: FastAPI (Python) on Fly.io
- **Database**: Encrypted SQLite on Fly.io persistent volume
- **Auth**: JWT with 30-day tokens

## Architecture
- SPA with Vue Router (no SSR)
- PWA with service worker for offline support
- Pinia stores: `auth.ts` (authentication), `budget.ts` (budget/expenses/pool)
- API calls go to `https://the-number-budget.fly.dev`
- Frontend deployed to Vercel, proxied via `foil.engineering/TheNumber/`

## Key Files
- `src/views/Dashboard.vue` - Main budget dashboard with pool section
- `src/views/Transactions.vue` - Transaction history
- `src/stores/budget.ts` - Budget state management (expenses, pool, daily number)
- `src/stores/auth.ts` - Authentication state
- `src/router/index.ts` - Route definitions
- `src/components/` - Reusable components (AuthModal, NumberDisplay, AddToPoolModal, etc.)
- `vite.config.ts` - Vite + PWA + Vuetify config

## Deployment
- **Frontend**: Vercel project `thenumber` (Root Directory = `frontend`)
- **IMPORTANT**: Deploy from `C:\Users\watso\Dev` (NOT from `frontend/`)
- **Backend**: Fly.io app `the-number-budget` (deploy from `C:\Users\watso\Dev`)

```bash
# Frontend deploy (from Dev root!)
cd C:/Users/watso/Dev
npx vercel --prod --yes

# Backend deploy (from Dev root!)
fly deploy --now

# Verify
curl https://the-number-budget.fly.dev/health
```

## Dev Commands
```bash
npm run dev         # Dev server (localhost:5173)
npm run build       # Production build
npm run preview     # Preview production build
npm run test        # Run tests
npm run type-check  # TypeScript check
```

## Current Status
- Pool/carry-over feature deployed and tested
- PWA Badge feature working
- QA phase active, debug logging enabled
- TypeScript strict mode enabled

## Security
- **Axios pinned to 1.14.0** (2026-03-31): Supply chain attack hit axios npm — versions 1.14.1 and 0.30.4 contained a RAT via malicious `plain-crypto-js` dependency. Do NOT upgrade axios without verifying the version is safe. Avoid `^` range — use exact pin.

## Do NOT
- Deploy from `frontend/` directory (Vercel root is configured as `frontend`)
- Hardcode API URLs (use `getApiBaseUrl()`)
- Remove debug console.logs during QA phase
- Upgrade axios without checking for supply chain compromise (see Security section)
