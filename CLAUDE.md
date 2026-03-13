# Dev Monorepo - Cross-Project Guidelines

## Project Stack
- Primary languages: Python, TypeScript, HTML/CSS, Markdown
- Deployments: Vercel (frontend), Fly.io (backend APIs)
- Key projects: TheNumber (budget PWA - Vue/Vuetify frontend, Python backend), FOIL Engineering site (foil.engineering), Resume Tailor (Python, exe builds), monomythism site
- Always deploy BOTH frontend and backend when changes span the stack.

## Deployment
- Always confirm the correct Vercel project and Fly.io app before deploying. Never assume — verify with `vercel ls` or check project.json first.
- After deploying, verify the live URL returns HTTP 200 and spot-check for visual regressions (e.g., white-on-white text, stale cached assets).

## State Verification
- Never report on project state from memory or prior sessions. Always verify current state by reading files, running the app, or checking git status before summarizing what's done vs. pending.
- When building executables or generating PDFs, verify the output file actually exists at the expected path before reporting success.

## Repository Awareness
- The user's GitHub repos (foil-industries-v2, etc.) are PUBLIC, not private. Never assume they are private.
- Be aware of git repo boundaries: foil-industries-v2 may be a sub-repo gitignored from a parent directory. Always `cd` into the correct repo before git operations.

## Runtime vs. Seed Data
- When renaming, updating, or fixing data: always check BOTH seed/import scripts AND runtime data files (e.g., JSON files loaded at runtime). Never assume fixing the import script is sufficient.
- Resume Tailor has two data sources: `import_career_data.py` (seed) and `~/.resume_tailor/career_data.json` (runtime). Both must be updated.
