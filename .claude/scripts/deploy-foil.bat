@echo off
REM Deploy foil.engineering frontend to Vercel and verify
cd /d C:\Users\watso\Dev\foil-industries-v2
claude -p "Deploy the frontend to Vercel production for foil.engineering. First verify you're in the foil-industries-v2 directory and that the Vercel project is 'foil-industries'. Run the build, deploy with 'npx vercel --prod --yes', then curl https://www.foil.engineering and confirm HTTP 200. If it fails, report the error." --allowedTools "Bash,Read"
