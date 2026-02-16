# Deployment Status

**Last Updated:** February 16, 2026

## The Number

| Component | Platform | URL | Status |
|-----------|----------|-----|--------|
| Frontend | Vercel (`thenumber`) | foil.engineering/TheNumber/ | Live |
| Backend | Fly.io (`the-number-budget`) | the-number-budget.fly.dev | Live |

**Deploy from**: `C:\Users\watso\Dev` (not `frontend/`)

```bash
# Frontend
npx vercel --prod --yes

# Backend
fly deploy --now

# Verify
curl https://the-number-budget.fly.dev/health
```

**Current features deployed**: Pool/carry-over, PWA badge, overspend recalculation, TypeScript strict mode.

## Foil Engineering

| Component | Platform | URL | Status |
|-----------|----------|-----|--------|
| Site | Vercel (`foil-industries`) | www.foil.engineering | Live |

**Deploy from**: `C:\Users\watso\Dev\foil-industries-v2` (separate git repo)
**Branch**: `master` (auto-deploys on push)

## Resume Tailor

Local-only application. No cloud deployment.
Build executable: `.\build_executable.bat` in `resume-tailor/`
