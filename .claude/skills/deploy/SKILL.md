---
name: deploy
description: Project-aware deployment with pre-flight checks and post-deploy verification. Supports Vercel (foil.engineering, The Number frontend) and Fly.io (The Number backend).
---

# Deploy

Run project-aware deployment with safety checks and verification.

## Instructions

### 1. Detect Current Project

Determine which project to deploy based on the current working directory:

| Directory | Project | Platform |
|-----------|---------|----------|
| `foil-industries-v2/` | Foil Engineering | Vercel |
| `frontend/` or root `Dev/` | The Number (frontend) | Vercel |
| Root `Dev/` with `--backend` | The Number (backend) | Fly.io |
| `resume-tailor/` | Resume Tailor | N/A (local only) |

If ambiguous, ask the user which project to deploy.

### 2. Pre-flight Checks

Run ALL of these before deploying:

```bash
# Check git status - warn about uncommitted changes
git status

# Check current branch
git branch --show-current

# Verify no merge conflicts
git diff --check
```

**Project-specific checks:**

**Foil Engineering (Vercel):**
- Verify in `foil-industries-v2/` directory
- Run `npm run build` to catch build errors
- Check `dist/` output for sitemap.xml and robots.txt
- Verify `vercel.json` exists with security headers

**The Number Frontend (Vercel):**
- MUST be in `C:\Users\watso\Dev` root (NOT `frontend/`)
- Run `npm run build` from `frontend/` to verify build succeeds
- Check bundle size warnings
- Verify `frontend/.vercel/project.json` exists

**The Number Backend (Fly.io):**
- MUST be in `C:\Users\watso\Dev` root
- Run `fly status` to check current deployment
- Verify `fly.toml` exists
- Check `src/database.py` for pending migrations

### 3. Deploy

**Foil Engineering:**
```bash
cd C:\Users\watso\Dev\foil-industries-v2
npx vercel --prod --yes
```

**The Number Frontend:**
```bash
cd C:\Users\watso\Dev
npx vercel --prod --yes
```

**The Number Backend:**
```bash
cd C:\Users\watso\Dev
fly deploy --now
```

### 4. Post-deploy Verification

**Foil Engineering:**
- Fetch `https://foil.engineering` and verify 200 response
- Check security headers are present (HSTS, Referrer-Policy)
- Verify sitemap at `https://foil.engineering/sitemap-index.xml`

**The Number Frontend:**
- Fetch the deployed URL and verify 200 response
- Check that the app loads (no blank page)

**The Number Backend:**
- Run `curl https://the-number-budget.fly.dev/health` and verify response
- Check `fly logs` for any startup errors

### 5. Report

Output a summary:
```
Deploy complete:
- Project: [name]
- Platform: [Vercel/Fly.io]
- URL: [deployed URL]
- Status: [success/warning]
- Checks: [list of passed/failed checks]
```

## Safety Rules

- NEVER deploy with uncommitted changes without user confirmation
- NEVER force-deploy if build fails
- ALWAYS run pre-flight checks before deploying
- If any check fails, report the failure and ask before proceeding
