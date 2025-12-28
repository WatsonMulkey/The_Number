# Session Start Checklist

**This file is automatically displayed at the start of each session via `.claude/hooks/session-start.sh`**

---

## ✅ Pre-Session Verification

Before starting ANY work, verify you understand:

###  1. What's Actually Deployed?

Read: `docs/DEPLOYMENT_STATUS.md` - Sections to focus on:
- [ ] **Quick Status** table - What version is live?
- [ ] **Local Changes (Not Deployed)** - What's built but not uploaded?
- [ ] **Known Issues** - What's broken in production?

**Key Question:** _"If I make a change, am I editing production code or local-only code?"_

### 2. What Phase Are We In?

Read: `docs/PROJECT_PHASE.md` - Sections to focus on:
- [ ] **Current Phase Focus** - What matters most right now?
- [ ] **Success Criteria** - What needs to be true to move forward?
- [ ] **Next Session Priorities** - What should I work on?

**Key Question:** _"Am I working on the right things for this phase?"_

### 3. What Did Last Session Accomplish?

Check:
- [ ] Git log: `git log -3 --oneline`
- [ ] Git status: `git status --short`
- [ ] PROJECT_PHASE.md → "Context Handoff Notes"

**Key Question:** _"What context do I need from the previous session?"_

---

## 📋 Session Start Actions

### Every Session (Required)

1. **Run `/skill retro`** - Load retrospective learnings
   - Searches supermemory for past mistakes
   - Reviews what worked/didn't work
   - Applied learnings to current task

2. **Verify deployment state** (done automatically by hook)
   - Backend health check
   - Git commits ahead of origin
   - Uncommitted changes count

3. **Update TodoWrite with session plan**
   - Break down user's request into tasks
   - Mark current task as in_progress
   - Complete tasks as you finish them

### Before Major Operations

**Before Deploying:**
- [ ] Read DEPLOYMENT_STATUS.md → "Deployment Procedures"
- [ ] Run deployment testing checklist
- [ ] Commit all changes to git first
- [ ] Update DEPLOYMENT_STATUS.md after deployment

**Before Creating/Changing Architecture:**
- [ ] Run `/skill best-practices-review`
- [ ] Check PROJECT_PHASE.md → "What We're NOT Focusing On"
- [ ] Confirm with user if unsure about scope

**Before Committing:**
- [ ] Review changes: `git diff`
- [ ] Run tests if applicable
- [ ] Write descriptive commit message
- [ ] Include Claude Code attribution

---

## 🎯 Context Management Strategy

### How to Stay Oriented

**If you're confused about deployment state:**
1. Read DEPLOYMENT_STATUS.md completely
2. Check production URLs manually
3. Compare local `frontend/dist/` files to what's described as deployed
4. Ask user for clarification before proceeding

**If you're unsure what to work on:**
1. Read PROJECT_PHASE.md → "Next Session Priorities"
2. Check for blocking issues in DEPLOYMENT_STATUS.md
3. Ask user what's most important right now

**If you make a mistake:**
1. Run `/skill error-lessons` immediately
2. Document in retrospective
3. Update DEPLOYMENT_STATUS.md if it affects production
4. Update BEST_PRACTICES.md if it reveals a pattern

---

## 🔄 Continuous Context Tracking

### During Work

- **Use TodoWrite frequently** - Track progress in real-time
- **Mark todos complete immediately** - Don't batch completions
- **Update DEPLOYMENT_STATUS.md** - After every deployment
- **Update PROJECT_PHASE.md** - When priorities shift

### At Natural Breaks

- **Commit to git** - Don't let uncommitted work pile up
- **Update documentation** - If you learned something important
- **Check production** - If you deployed something

### Before Ending Session

Session end hook (Ralph Wiggum stop-hook) will:
- Prompt for session summary
- Update DEPLOYMENT_STATUS.md
- Update PROJECT_PHASE.md handoff notes
- Save summary to `.claude/last-session-summary.txt`

---

## 📚 Quick Reference

### Key Files to Know

| File | When to Read | Purpose |
|------|--------------|---------|
| `DEPLOYMENT_STATUS.md` | Every session start, before/after deploy | Single source of truth for what's live |
| `PROJECT_PHASE.md` | Session start, when priorities unclear | Understand current phase and priorities |
| `SESSION_START.md` | Auto-displayed at start | This file - session checklist |
| `UX_OVERHAUL_PLAN.md` | Before UX work, reference during implementation | Complete UX audit findings and 3-phase implementation plan |
| `PWA_DEPLOYMENT_HANDOFF.md` | When confused about PWA | Original PWA deployment context |
| `BEST_PRACTICES.md` | Before major decisions | Project-specific best practices |
| `ROADMAP.md` | Planning features | Long-term feature backlog |

### Important Commands

```bash
# Context Loading
/skill retro                          # Load retrospective learnings
/skill best-practices-review          # Review best practices

# Git Status
git status --short                    # Quick status
git log -3 --oneline                  # Recent commits
git diff origin/main                  # What's not pushed

# Deployment Checks
curl https://the-number-budget.fly.dev/health    # Backend health
flyctl logs                                      # Backend logs
ls -lh frontend/dist/                           # Local build status

# Testing
cd frontend && npm run preview        # Test frontend build
cd api && pytest                      # Run backend tests
```

---

## 🚨 Red Flags - Stop and Clarify

**STOP and read DEPLOYMENT_STATUS.md if:**
- You're about to deploy something
- You're confused about which code is in production
- You're making changes to files you haven't verified locally
- You see unexpected errors in production URLs

**STOP and read UX_OVERHAUL_PLAN.md if:**
- You're making UI/UX changes
- You're adjusting colors, spacing, or layout
- You're working on navigation components
- You need to understand the mobile-first strategy

**STOP and ask the user if:**
- You're adding features during "Production Deployment" phase
- You're about to make breaking changes
- You're unclear about deployment urgency
- Multiple approaches seem equally valid
- You want to deploy UX changes in a different order than planned

**STOP and run `/skill error-lessons` if:**
- You encounter any error
- You made a mistake
- You deployed something that broke
- You missed checking a file before deploying

---

## 💡 Tips for Effective Sessions

### From Past Retrospectives

1. **"Trust the docs, not your memory"** - Always verify deployment state
2. **"Build locally, test, commit, then deploy"** - Never skip steps
3. **"One deployment at a time"** - Don't batch multiple fixes without testing
4. **"Version pins matter"** - Check requirements.txt/package.json for compatibility issues
5. **"Update docs immediately"** - Context decays fast, document while fresh

### Common Mistakes to Avoid

- ❌ Assuming local code matches production
- ❌ Deploying without updating DEPLOYMENT_STATUS.md
- ❌ Forgetting to commit before deploying
- ❌ Not checking retrospectives before repeating past mistakes
- ❌ Working on low-priority items during critical phases

---

## 🎬 Session Start Workflow (Recommended)

```
1. Hook runs automatically → Shows deployment status summary
2. Read DEPLOYMENT_STATUS.md → Understand what's live
3. Read PROJECT_PHASE.md → Understand priorities
4. Run /skill retro → Load learnings
5. User provides request
6. Create TodoWrite plan → Break down work
7. Start work → Mark first todo as in_progress
... work happens ...
N. Session ends → Ralph Wiggum stop-hook updates docs
```

---

**This checklist evolves with the project. Update it when you discover new patterns or better workflows!**
