# Deployment Map

Last verified: 2026-01-28

## FOIL Engineering (company site)

| Layer          | Value                                    |
|----------------|------------------------------------------|
| Local path     | `C:\Users\watso\Dev\foil-industries-v2\` |
| GitHub repo    | `WatsonMulkey/foil-industries`           |
| Vercel project | `foil-industries`                        |
| Production URL | https://www.foil.engineering             |
| Framework      | Astro 5                                  |

**Deploy**: `cd foil-industries-v2 && npx vercel --prod --yes`

### Notes
- `/TheNumber` path is a Vercel rewrite proxying to `thenumber-rust.vercel.app`
- Changes to `vercel.json` rewrites require a Vercel deploy
- Local folder pending rename to `foil-engineering` (requires closing editors first)


## The Number (budget app)

| Layer          | Value                                    |
|----------------|------------------------------------------|
| Repo root      | `C:\Users\watso\Dev\`                    |
| Frontend path  | `C:\Users\watso\Dev\frontend\`           |
| API path       | `C:\Users\watso\Dev\api\`                |
| GitHub repo    | `WatsonMulkey/The_Number`                |
| Vercel project | `thenumber-rust`                         |
| Fly.io app     | `the-number-budget`                      |
| Frontend URL   | https://foil.engineering/TheNumber       |
| API URL        | https://the-number-budget.fly.dev        |
| Framework      | Vue 3 + Vite (frontend), FastAPI (API)   |
| Database       | SQLite on Fly.io persistent volume `/data` |

**Deploy frontend**: `cd frontend && npx vercel --prod --yes`
**Deploy API**: `cd C:\Users\watso\Dev && fly deploy --now`
**Deploy both**: Run both commands above. There is no single deploy command.

### Warnings
- `git push` alone does NOT deploy frontend or API
- API and frontend must be deployed separately
- The Vercel project name `thenumber-rust` is misleading (no Rust) - DO NOT rename it, `thenumber` on Vercel is a different unrelated project (Sokoban game)
- FastAPI needs full restart (not reload) for CORS `.env` changes


## Monomythism Website

| Layer          | Value                                        |
|----------------|----------------------------------------------|
| Local path     | `C:\Users\watso\Dev\monomythism-website\`    |
| GitHub repo    | Not yet set up                               |
| Hosting        | Not yet deployed                             |
| Framework      | Astro 5                                      |
| Dev URL        | http://localhost:4321/                        |
| Password       | `monomyth2024`                               |

**Dev server**: `cd monomythism-website && npm run dev`


## Name Mapping (why things are named differently)

| What you see locally     | What it actually is                        |
|--------------------------|--------------------------------------------|
| `foil-industries-v2/`    | FOIL company site (Astro) - rename pending |
| `frontend/`              | The Number Vue 3 frontend                  |
| `api/`                   | The Number FastAPI backend                 |
| `thenumber-rust`         | Vercel project for The Number (NOT Rust)   |
| `thenumber` (on Vercel)  | UNRELATED Sokoban game - do not touch      |
| `foil-industries`        | Vercel project for foil.engineering        |
| `the-number-budget`      | Fly.io app for The Number API              |


## Vercel Projects (verified 2026-01-28)

| Vercel Project       | Domain                | What it serves              |
|----------------------|-----------------------|-----------------------------|
| `foil-industries`    | www.foil.engineering  | FOIL company site (Astro)   |
| `thenumber-rust`     | thenumber-rust.vercel.app | The Number frontend (Vue) |
| `thenumber`          | thenumber.vercel.app  | UNRELATED Sokoban game      |
