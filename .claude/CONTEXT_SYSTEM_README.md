# Claude Code Context Management System

**A comprehensive, scalable system for maintaining context across sessions throughout a project lifecycle.**

---

## Overview

This system solves the problem of context loss between Claude Code sessions by:
1. **Automatically loading context** at session start
2. **Tracking deployment state** in living documents
3. **Capturing learnings** at session end
4. **Scaling with project phases** from idea to production

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    SESSION LIFECYCLE                         │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  1. SessionStart Hook                                        │
│     ├─> .claude/hooks/session-start.sh                      │
│     ├─> Shows deployment status                             │
│     ├─> Shows git state                                     │
│     ├─> Reminds to read key docs                            │
│     └─> Loads last session summary                          │
│                                                              │
│  2. During Work                                              │
│     ├─> Use TodoWrite for task tracking                     │
│     ├─> Update DEPLOYMENT_STATUS.md after deployments       │
│     ├─> Run /skill retro before major work                  │
│     └─> Commit frequently                                   │
│                                                              │
│  3. Stop Hook (Session End)                                  │
│     ├─> Prompts for session summary                         │
│     ├─> Reviews deployment state                            │
│     └─> Updates PROJECT_PHASE.md handoff notes              │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## Components

### 1. Hook Configuration (`.claude/settings.local.json`)

**Purpose:** Defines automated hooks that run at session start/end

**What it does:**
- `SessionStart` hook → Runs `.claude/hooks/session-start.sh`
- `Stop` hook → Prompts Claude to capture session summary

**Location:** `.claude/settings.local.json`

### 2. Session Start Script (`.claude/hooks/session-start.sh`)

**Purpose:** Automatically loads context at the beginning of every session

**What it shows:**
- Current project phase
- Deployment status (what's live vs local)
- Git status (commits ahead, uncommitted changes)
- Backend health check
- Required reading reminders
- Last session summary

**Output:** Formatted context display in the terminal

### 3. Deployment Status Document (`docs/DEPLOYMENT_STATUS.md`)

**Purpose:** Single source of truth for what's actually deployed

**Sections:**
- **Quick Status** - At-a-glance table of deployment state
- **Production Details** - What's live on frontend/backend
- **Local Changes** - What's built but not deployed
- **Deployment Procedures** - Step-by-step deploy instructions
- **Testing Checklists** - Before/after deployment verification
- **Issues Log** - Active and resolved production issues
- **Change History** - Deployment timeline

**Update Frequency:** After every deployment

### 4. Project Phase Document (`docs/PROJECT_PHASE.md`)

**Purpose:** Defines current project phase and priorities

**Sections:**
- **Current Phase Focus** - What matters most right now
- **Phase History** - Journey from idea to current state
- **Success Criteria** - What needs to be true to move forward
- **Next Session Priorities** - What to work on next
- **Context Handoff Notes** - Session-to-session knowledge transfer
- **Phase-Specific Guidelines** - Rules for current phase

**Update Frequency:**
- When priorities shift
- At end of each session (handoff notes)
- When transitioning to new phase

### 5. Session Start Checklist (`docs/SESSION_START.md`)

**Purpose:** Comprehensive checklist for starting work

**Sections:**
- **Pre-Session Verification** - What to verify before starting
- **Session Start Actions** - Required steps every session
- **Context Management Strategy** - How to stay oriented
- **Quick Reference** - Key files and commands
- **Red Flags** - When to stop and clarify

**Usage:** Auto-displayed by session-start hook, reference as needed

### 6. Session End Script (`.claude/hooks/session-end.sh`)

**Purpose:** Optional manual script for capturing session context

**What it does:**
- Prompts for session summary
- Checks if anything was deployed
- Warns about uncommitted/unpushed changes
- Saves summary to `.claude/last-session-summary.txt`
- Reminds to update documentation

**Usage:** Can be run manually or integrated with other workflows

---

## Workflow

### Every Session Start (Automatic)

```bash
1. Hook runs → session-start.sh executes
2. Context displayed:
   ✓ Project phase
   ✓ Deployment status
   ✓ Git state
   ✓ Backend health
   ✓ Last session summary

3. Claude sees output as <system-reminder>
4. Claude knows current state before user even speaks
```

### During Work (Manual)

```bash
1. User makes request
2. Claude creates TodoWrite plan
3. Work proceeds with frequent commits
4. If deploying → Update DEPLOYMENT_STATUS.md immediately
5. If priorities shift → Update PROJECT_PHASE.md
```

### Session End (Automatic + Manual)

```bash
1. Stop hook runs → Claude prompted for summary
2. Claude provides 2-3 sentence handoff summary
3. (Optional) Run .claude/hooks/session-end.sh for detailed capture
4. Update PROJECT_PHASE.md handoff notes section
5. Commit all documentation updates
```

---

## Scaling with Project Phases

This system adapts as your project evolves:

### Idea Phase
**Focus:** Requirements, design decisions
**Key Files:** PROJECT_PHASE.md (what we're building, why)
**Hook Value:** Reminds what was decided in previous sessions

### Development Phase
**Focus:** Building features, testing
**Key Files:** All docs, emphasis on git state
**Hook Value:** Shows what's built vs tested vs committed

### Deployment Phase (CURRENT)
**Focus:** Getting to production, fixing bugs
**Key Files:** DEPLOYMENT_STATUS.md is critical
**Hook Value:** Prevents deploying wrong version, tracks state

### Production Phase
**Focus:** User feedback, stability, features
**Key Files:** DEPLOYMENT_STATUS.md, issue tracking
**Hook Value:** Ensures fixes go to right places, rollback info

### Maintenance Phase
**Focus:** Bug fixes, optimization, minor features
**Key Files:** Light touch on all docs
**Hook Value:** Quick context loading for quick fixes

---

## Key Benefits

### 1. **No More "What's Deployed?" Confusion**

**Before:**
- "Wait, did we upload the PWA build?"
- "Is the onboarding fix live?"
- "Which version is in production?"

**After:**
- Session hook shows exact deployment state
- DEPLOYMENT_STATUS.md is single source of truth
- Always know what's local vs live

### 2. **Prevents Repeating Past Mistakes**

**Before:**
- Forgot to check retrosp
ectives
- Repeated bcrypt version error
- Missed PWA requirements despite docs

**After:**
- Session start reminds to run /skill retro
- Past mistakes in DEPLOYMENT_STATUS.md issues log
- PROJECT_PHASE.md highlights current phase requirements

### 3. **Smooth Session Handoffs**

**Before:**
- "What was I working on last time?"
- No memory of blockers or decisions
- Context reconstruction takes 10+ minutes

**After:**
- Last session summary auto-displayed
- PROJECT_PHASE.md handoff notes show decisions
- Ready to work in 30 seconds

### 4. **Scales with Project Complexity**

**Before:**
- Simple projects → overhead seems unnecessary
- Complex projects → drowning in context

**After:**
- Early phases → lightweight docs, quick reads
- Later phases → comprehensive tracking pays off
- System grows naturally with project

---

## File Structure

```
C:\Users\watso\Dev\
├── .claude/
│   ├── settings.local.json          # Hook configuration
│   ├── hooks/
│   │   ├── session-start.sh         # Auto-runs at session start
│   │   └── session-end.sh           # Optional manual session end
│   ├── last-session-summary.txt     # Auto-generated summary
│   └── CONTEXT_SYSTEM_README.md     # This file
│
└── docs/
    ├── DEPLOYMENT_STATUS.md         # Single source of truth for deployments
    ├── PROJECT_PHASE.md             # Current phase and priorities
    ├── SESSION_START.md             # Comprehensive session checklist
    ├── PWA_DEPLOYMENT_HANDOFF.md    # Original PWA context (historical)
    ├── BEST_PRACTICES.md            # Project-specific best practices
    └── ROADMAP.md                   # Long-term feature backlog
```

---

## Usage Examples

### Example 1: Starting a Session

```bash
# User opens Claude Code
# Hook runs automatically:

═══════════════════════════════════════════════════════════
         The Number - Session Start Context
═══════════════════════════════════════════════════════════

📋 Current Phase:
  Production Deployment & Stabilization

🚀 Deployment Status:
  Production Frontend: Old build (pre-532f649)
  Production Backend: Includes bcrypt fix
  Local Changes: frontend/dist/ has onboarding fix (not deployed)

📁 Git Status:
  Latest commit: 532f649 Fix onboarding flow
  ⚠️  6 commits ahead of origin/main
  ⚠️  0 uncommitted changes

🌐 Production Status:
  Backend: "status":"healthy"
  Frontend: https://foil.engineering/TheNumber (check manually)

📚 REQUIRED READING:
  1. docs/DEPLOYMENT_STATUS.md
  2. docs/SESSION_START.md
  3. docs/PROJECT_PHASE.md

📝 Last Session Summary:
  Last Session: Dec 28, 2024 11:00 PM
  Summary: Fixed onboarding flow, committed but not deployed
  Deployed: No

═══════════════════════════════════════════════════════════
✅ Context loaded. Ready to work!
═══════════════════════════════════════════════════════════

# Claude now knows EXACTLY what state the project is in
# User can immediately continue work
```

### Example 2: During Deployment

```bash
# Claude builds and deploys frontend
# Claude IMMEDIATELY updates DEPLOYMENT_STATUS.md:

## Quick Status
| Component | Status | Version/Commit | Notes |
|-----------|--------|----------------|-------|
| Production Frontend | ✅ Live | 532f649 | Onboarding fix deployed |
| Production Backend | ✅ Live | Includes bcrypt fix | Healthy |
| Local Changes | ✅ Clean | - | All deployed |

# Next session will show this updated state
```

### Example 3: Session End

```bash
# User ends session
# Stop hook runs automatically:

Capturing session context...

Session ending. Reviewing:
1. Accomplished: Fixed onboarding flow, committed (532f649), discussed but did not deploy
2. Deployment state: Frontend has old build, backend current, onboarding fix ready in dist/
3. Next session focus: Address additional issues, then deploy all fixes together
4. Blockers: User wants to fix more issues before deployment

Handoff Summary:
"Fixed onboarding authentication skip (532f649). User requested additional fixes before deploying updated build. PWA infrastructure confirmed working in production. Next session: address remaining issues, deploy comprehensive update, test mobile PWA installation."

✅ Update docs/PROJECT_PHASE.md with this summary

# Claude updates PROJECT_PHASE.md handoff notes
# Next session starts with full context
```

---

## Best Practices

### 1. Update DEPLOYMENT_STATUS.md Religiously

**After EVERY deployment:**
- Update timestamps
- Update commit hashes
- Update "Quick Status" table
- Add entry to "Change History"

**Why:** This is the single source of truth. If it's wrong, everything breaks.

### 2. Keep PROJECT_PHASE.md Current

**Update "Context Handoff Notes" after every session:**
- What was accomplished
- What's blocked
- What's next

**Why:** Next session needs to know decisions and blockers.

### 3. Trust the Hooks

**Don't skip reading the session start output:**
- It's designed to be concise
- It shows the critical state
- It prevents costly mistakes

**Why:** 30 seconds reading = hours saved fixing deployment mistakes.

### 4. Use TodoWrite During Work

**Create todo plan at start of every user request:**
- Break down work into tasks
- Mark in_progress/completed as you go
- Shows progress to user

**Why:** Complements the hooks - hooks for session-level, todos for task-level.

### 5. Commit Documentation with Code

**When committing code changes:**
- Also update DEPLOYMENT_STATUS.md if deployed
- Also update PROJECT_PHASE.md if priorities shifted
- Commit docs and code together

**Why:** Keeps documentation in sync with code state.

---

## Maintenance

### Weekly Cleanup

- Review DEPLOYMENT_STATUS.md → Move resolved issues to "Resolved" section
- Review PROJECT_PHASE.md → Update phase if transitioning
- Review git → Push unpushed commits

### Phase Transitions

When moving to new phase (e.g., Deployment → Production):

1. Update PROJECT_PHASE.md:
   - Mark old phase complete
   - Update "Current Phase Focus"
   - Define new "Success Criteria"

2. Update DEPLOYMENT_STATUS.md:
   - Archive old issues
   - Reset for new phase priorities

3. Update SESSION_START.md:
   - Adjust checklist for new phase
   - Update "Red Flags" section

### Document Evolution

These documents should evolve:
- Add new sections as project grows
- Remove outdated information
- Refine checklists based on what works

**Golden Rule:** If you found yourself confused, update the docs so it doesn't happen again.

---

## Troubleshooting

### Hook Not Running

**Symptom:** Session starts but no context output

**Fix:**
```bash
# Check hook configuration
cat .claude/settings.local.json | grep -A 10 hooks

# Test hook manually
bash .claude/hooks/session-start.sh

# Check hook has execute permission
chmod +x .claude/hooks/session-start.sh
```

### Wrong Context Displayed

**Symptom:** Hook shows outdated information

**Fix:**
1. Check DEPLOYMENT_STATUS.md "Last Updated" timestamp
2. If old → You forgot to update it after deploying
3. Update DEPLOYMENT_STATUS.md NOW
4. Next session will show correct state

### Documents Out of Sync

**Symptom:** DEPLOYMENT_STATUS.md says one thing, production shows another

**Fix:**
1. Check production manually (visit URLs, run health checks)
2. Update DEPLOYMENT_STATUS.md to match reality
3. Add note to "Issues Log" about the sync problem
4. Figure out why sync was lost and fix the process

---

## Integration with Other Tools

### Ralph Wiggum Skill

Ralph Wiggum's stop-hook is for its reflection loop, not session-end. Our Stop hook is separate and complementary.

**Workflow:**
- Session Start → Our hook loads context
- Ralph loop runs → Continuous improvement
- Session End → Our Stop hook captures summary

### Best Practices Skill

**Workflow:**
```bash
# Session start
1. Hook loads context automatically
2. Run /skill retro (load retrospective learnings)
3. Run /skill best-practices-review (before major decisions)
4. Work proceeds
5. Run /skill error-lessons (after errors)
6. Session end → Stop hook captures summary
```

### Supermemory

**Workflow:**
```bash
# Session start
1. Hook loads context
2. /skill retro searches supermemory for learnings

# During work
3. Save important decisions to supermemory
4. Document deployment outcomes

# Session end
5. Hook prompts summary → can save to supermemory
```

---

## Advanced: Customization

### Add Pre-Deployment Verification Hook

```json
"PreToolUse": [
  {
    "matcher": "Write",
    "hooks": [
      {
        "type": "agent",
        "prompt": "Before deploying, verify docs/DEPLOYMENT_STATUS.md has been reviewed. Check if this Write operation is for deployment files. If deploying without updating docs, block and remind user."
      }
    ]
  }
]
```

### Add Notification Hook

```json
"Notification": [
  {
    "hooks": [
      {
        "type": "command",
        "command": "echo 'Remember to update DEPLOYMENT_STATUS.md after deployments!' >> deployment-reminders.log"
      }
    ]
  }
]
```

### Add Project-Specific Checks

Edit `.claude/hooks/session-start.sh` to add:
- Custom health checks
- Dependency version checks
- License compliance checks
- Security vulnerability scans

---

## Future Enhancements

**Possible additions as project grows:**

1. **Automated DEPLOYMENT_STATUS.md Updates**
   - Parse git commits for deployment info
   - Auto-update after flyctl deploy / file uploads

2. **Deployment History Visualization**
   - Generate timeline from Change History
   - Show what was deployed when

3. **Context Diff Tool**
   - Compare current session context to last session
   - Highlight what changed

4. **Integration Tests in Hooks**
   - Run smoke tests before allowing deployment
   - Verify production health after deployment

5. **Multi-Project Support**
   - Template this system for new projects
   - Shared hooks with project-specific configs

---

## Credits

**Created:** December 28, 2024
**For Project:** The Number (Budget Tracker PWA)
**Created By:** Claude & Watson (collaborative design)
**Purpose:** Solve context loss between sessions, scale from idea to production

---

## License

This context management system is part of The Number project. Adapt freely for your own Claude Code projects!

---

**Questions? Improvements? Update this README!**
