---
name: switch-project
description: Switch context between projects in the mono-repo. Loads project-specific CLAUDE.md, shows git status, and sets up the right mental model.
---

# Switch Project

Switch context when working across multiple projects in the Dev mono-repo. Prevents cross-project mistakes and loads the right context.

## Instructions

### 1. Determine Target Project

Parse the argument to identify the project:

| Argument | Project | Root Directory |
|----------|---------|----------------|
| `foil`, `foil.engineering` | Foil Engineering | `foil-industries-v2/` |
| `number`, `the-number`, `budget` | The Number | `frontend/` (frontend) + root (backend) |
| `resume`, `resume-tailor` | Resume Tailor | `resume-tailor/` |

If no argument provided, list available projects and ask which one.

### 2. Load Project Context

1. Read the project's `CLAUDE.md` file:
   - `foil-industries-v2/CLAUDE.md`
   - `frontend/CLAUDE.md`
   - `resume-tailor/CLAUDE.md`

2. Display a brief summary:
   ```
   Switched to: [Project Name]
   Tech: [stack summary]
   Status: [current status from CLAUDE.md]
   Deploy: [deployment target]
   ```

### 3. Show Project Git Status

Run `git status` filtered to the project's directory:
- Show modified files in the project directory only
- Highlight any uncommitted changes
- Show current branch

### 4. Set Guardrails

Remind about project-specific constraints:

**Foil Engineering:**
- Deploy from `foil-industries-v2/` directory
- Astro SSG -- no client-side JS unless in `<script>` islands
- SEO matters: check meta tags, sitemap, robots.txt

**The Number:**
- Frontend deploys from Dev root (NOT `frontend/`)
- Backend deploys from Dev root with `fly deploy`
- Don't remove debug logs during QA phase
- Use `getApiBaseUrl()` for API URLs

**Resume Tailor:**
- Per-job isolation is critical -- never show multiple jobs to LLM at once
- Provenance tracing is on by default
- Test with `pytest` before committing

### 5. Check for Stale State

- If switching FROM another project, warn about any uncommitted changes in that project
- If the new project has pending tasks in the todo list, surface them

## When to Use

- Starting work on a different project mid-session
- After a `/session-start` when the project isn't clear
- When you notice cross-project confusion (e.g., deploying from wrong directory)
- Before running `/deploy` or `/qa` to confirm the right project is active
