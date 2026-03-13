@echo off
REM Deploy The Number frontend + backend and verify
cd /d C:\Users\watso\Dev
claude -p "Deploy The Number app - BOTH frontend and backend. Backend: run 'fly deploy --now' from C:\Users\watso\Dev, then verify https://the-number-budget.fly.dev/health returns healthy. Frontend: verify .vercel/project.json shows project 'thenumber', then run 'npx vercel --prod --yes' from C:\Users\watso\Dev (NOT frontend/). Verify the live URL returns HTTP 200. Report results for both." --allowedTools "Bash,Read"
