# Sprint Plan: Beta Launch Preparation

**Sprint Duration**: 5 days
**Sprint Goal**: Ship beta-ready version to 5-10 trusted testers
**Team Velocity**: ~7 story points/day (solo developer)

---

## Sprint Backlog (Priority Order)

### Day 1: Data Safety Foundation (13 points)

#### Morning (4 hours) - Task 1.1.2: Encryption Key Persistence (3 pts)
**Order: FIRST** - Prevents catastrophic key loss

**Subtasks**:
1. Update `.env.example`:
```bash
# REQUIRED: Database encryption key
# Generate: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
DB_ENCRYPTION_KEY=REQUIRED_CHANGE_THIS

# REQUIRED: JWT secret for authentication
# Generate: python -c "import secrets; print(secrets.token_urlsafe(32))"
JWT_SECRET_KEY=REQUIRED_CHANGE_THIS
```

2. Add startup validation in `api/main.py`:
```python
# Add at app startup (after imports)
@app.on_event("startup")
async def validate_environment():
    required_vars = ["DB_ENCRYPTION_KEY", "JWT_SECRET_KEY"]
    missing = [var for var in required_vars if not os.getenv(var)]
    if missing:
        raise RuntimeError(
            f"Missing required environment variables: {', '.join(missing)}\n"
            f"Copy .env.example to .env and fill in all values."
        )
```

3. Update health check to verify keys:
```python
@app.get("/health")
async def health_check():
    # Verify critical env vars exist
    has_db_key = bool(os.getenv("DB_ENCRYPTION_KEY"))
    has_jwt_key = bool(os.getenv("JWT_SECRET_KEY"))

    return {
        "status": "healthy" if (has_db_key and has_jwt_key) else "degraded",
        "encryption_configured": has_db_key,
        "auth_configured": has_jwt_key
    }
```

4. Create `SETUP_GUIDE.md`:
```markdown
# Setup Guide for The Number

## Initial Setup

1. Clone repository
2. Copy `.env.example` to `.env`
3. Generate encryption key:
   python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
4. Generate JWT secret:
   python -c "import secrets; print(secrets.token_urlsafe(32))"
5. Paste both into `.env`
6. BACKUP YOUR .env FILE SECURELY

## Critical: Key Backup
- Without these keys, ALL USER DATA IS LOST
- Store `.env` in password manager
- Keep offline backup
```

**Acceptance Test**:
```bash
# Should fail without keys
rm .env
python -m uvicorn api.main:app
# Should show clear error about missing keys

# Should succeed with keys
cp .env.example .env
# (add real keys)
python -m uvicorn api.main:app
curl http://localhost:8000/health
# Should return: {"status": "healthy", ...}
```

---

#### Afternoon (4 hours) - Task 1.1.3: JWT Secret Persistence (5 pts)

**Subtasks**:
1. Update `api/auth.py` line 21:
```python
# BEFORE:
SECRET_KEY = os.getenv("JWT_SECRET_KEY", secrets.token_urlsafe(32))

# AFTER:
SECRET_KEY = os.getenv("JWT_SECRET_KEY")
if not SECRET_KEY:
    raise RuntimeError(
        "JWT_SECRET_KEY not found in environment variables. "
        "Generate one with: python -c \"import secrets; print(secrets.token_urlsafe(32))\""
    )
```

2. Test session persistence:
```python
# Create test script: tests/test_session_persistence.py
import requests
import subprocess
import time

API_URL = "http://localhost:8000"

# Register user
resp = requests.post(f"{API_URL}/api/auth/register", json={
    "username": "testuser",
    "password": "testpass123",
    "email": "test@example.com"
})
token = resp.json()["access_token"]
print(f"Token: {token[:20]}...")

# Verify token works
headers = {"Authorization": f"Bearer {token}"}
resp = requests.get(f"{API_URL}/api/auth/me", headers=headers)
print(f"User: {resp.json()['username']}")

# Restart server
print("Restarting server...")
subprocess.run(["pkill", "-f", "uvicorn"])
time.sleep(2)
subprocess.Popen(["python", "-m", "uvicorn", "api.main:app"])
time.sleep(3)

# Token should still work
resp = requests.get(f"{API_URL}/api/auth/me", headers=headers)
assert resp.status_code == 200, "Token invalid after restart!"
print("SUCCESS: Token persisted across restart")
```

3. Update documentation in `SETUP_GUIDE.md`

**Acceptance Test**:
- User logs in → Server restarts → User still authenticated

---

#### Evening (2 hours) - Task 1.1.1 Prep: Backup System Design (2 pts of 5)

**Subtasks**:
1. Create backup directory structure:
```bash
mkdir -p backups/manual
mkdir -p backups/automatic
```

2. Design backup script:
```python
# scripts/backup_database.py
import shutil
import sqlite3
from datetime import datetime
from pathlib import Path

def backup_database(
    db_path: str = "api/budget.db",
    backup_dir: str = "backups/automatic"
) -> str:
    """Create timestamped database backup."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"budget_backup_{timestamp}.db"
    backup_path = Path(backup_dir) / backup_name

    # Use SQLite's backup API for safe hot backup
    src = sqlite3.connect(db_path)
    dst = sqlite3.connect(str(backup_path))

    with dst:
        src.backup(dst)

    src.close()
    dst.close()

    print(f"Backup created: {backup_path}")
    return str(backup_path)

if __name__ == "__main__":
    backup_database()
```

---

### Day 2: Complete Backups + UX Fixes (10 points)

#### Morning (3 hours) - Task 1.1.1 Complete: Backup System (3 pts remaining)

**Subtasks**:
1. Add backup endpoints to `api/main.py`:
```python
from scripts.backup_database import backup_database

@app.post("/api/admin/backup")
async def create_backup(user_id: int = Depends(get_current_user_id)):
    """Create manual database backup (admin only)."""
    # TODO: Add admin role check
    backup_path = backup_database(backup_dir="backups/manual")
    return {"backup_path": backup_path}

@app.get("/api/admin/backups")
async def list_backups(user_id: int = Depends(get_current_user_id)):
    """List available backups."""
    backups = sorted(Path("backups").glob("**/*.db"), reverse=True)
    return {
        "backups": [
            {
                "filename": b.name,
                "path": str(b),
                "size": b.stat().st_size,
                "created": b.stat().st_mtime
            }
            for b in backups[:20]  # Most recent 20
        ]
    }
```

2. Add Settings UI for backups (frontend):
```vue
<!-- frontend/src/views/Settings.vue -->
<v-card>
  <v-card-title>Data Backup</v-card-title>
  <v-card-text>
    <p>Protect your financial data with regular backups.</p>
    <v-btn @click="createBackup" color="primary">
      Create Backup Now
    </v-btn>
    <v-list v-if="backups.length">
      <v-list-item v-for="backup in backups" :key="backup.filename">
        <v-list-item-title>{{ backup.filename }}</v-list-item-title>
        <v-list-item-subtitle>
          {{ formatDate(backup.created) }} - {{ formatSize(backup.size) }}
        </v-list-item-subtitle>
      </v-list-item>
    </v-list>
  </v-card-text>
</v-card>
```

3. Setup automated backups (platform-specific):
```bash
# Linux/Railway: Use cron
0 2 * * * cd /app && python scripts/backup_database.py

# Windows: Task Scheduler
# Action: python C:\path\to\scripts\backup_database.py
# Trigger: Daily at 2:00 AM
```

4. Test restore process:
```bash
# Create test restore script
python scripts/restore_database.py backups/manual/budget_backup_20231226_120000.db
```

**Acceptance Test**:
- Manual backup creates file in `backups/manual/`
- Automated backup runs (verify with test trigger)
- Restore script successfully restores database
- Settings page shows backup list

---

#### Afternoon (5 hours) - Task 1.2.1: Fix "Money In" Feature (5 pts)

**Investigation Steps**:
1. Test transaction endpoint directly:
```bash
# First, get auth token
TOKEN=$(curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"test","password":"test"}' \
  | jq -r '.access_token')

# Create "Money In" transaction
curl -X POST http://localhost:8000/api/transactions \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 50.00,
    "description": "Freelance payment",
    "category": "income",
    "date": "2025-12-26T10:00:00"
  }'

# Verify it appears in list
curl -X GET http://localhost:8000/api/transactions \
  -H "Authorization: Bearer $TOKEN"
```

2. Check frontend integration:
```typescript
// frontend/src/views/Dashboard.vue
// Find the recordMoneyIn method - likely missing or broken

async function recordMoneyIn() {
  try {
    const response = await axios.post('/api/transactions', {
      amount: moneyInAmount.value,
      description: moneyInDescription.value,
      category: 'income',
      date: new Date().toISOString()
    }, {
      headers: {
        Authorization: `Bearer ${authStore.token}`
      }
    })

    // Refresh the number after recording income
    await fetchTheNumber()

    // Clear form
    moneyInAmount.value = 0
    moneyInDescription.value = ''

    // Show success message
    snackbar.value = {
      show: true,
      message: 'Money recorded successfully!',
      color: 'success'
    }
  } catch (error) {
    console.error('Failed to record money:', error)
    snackbar.value = {
      show: true,
      message: 'Failed to record money. Please try again.',
      color: 'error'
    }
  }
}
```

3. Verify calculation update:
   - Does "The Number" increase after recording income?
   - Check `get_the_number` endpoint logic
   - May need to adjust calculation to include income transactions

**Key Question**: Should "Money In" transactions:
- A) Increase total_money in Fixed Pool mode? OR
- B) Extend days_until_paycheck in Paycheck mode? OR
- C) Just be recorded but not affect budget?

**Recommended**: Option A for Fixed Pool, Option C for Paycheck (matches real-world budgeting)

**Acceptance Test**:
- User can enter amount + description for income
- Transaction saves to database
- Transaction appears in transaction list
- "The Number" updates appropriately
- Error handling shows helpful messages

---

### Day 3: Security + Validation (8 points)

#### Morning (3 hours) - Task 1.4.1: Remove Debug Logging (2 pts)

**Search Strategy**:
```bash
# Find all debug logging
grep -r "print(" api/ src/
grep -r "sys.stderr" api/ src/
grep -r "DEBUG" api/ src/
```

**Files to Clean**:
1. `api/main.py` lines 151-159 (remove budget calculation debug)
2. `api/main.py` line 193 (remove configure_budget debug)
3. Any other `print()` statements

**Replace with Proper Logging**:
```python
import logging

# Configure at app startup
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Replace debug prints
# BEFORE:
sys.stderr.write(f"[DEBUG] Budget calculation for user {user_id}:\n")

# AFTER:
logger.info(f"Budget calculated for user {user_id}")
# Don't log sensitive amounts in production
```

**Acceptance Test**:
```bash
# Set production log level
export LOG_LEVEL=INFO
python -m uvicorn api.main:app

# Should NOT see detailed user data in logs
# Should still see INFO/ERROR messages
```

---

#### Afternoon (5 hours) - Task 1.2.2 + 1.4.2: Validation + Password Reset (6 pts)

**Part 1: Frontend Validation (3 hours)**

Add validation rules to all forms:

```typescript
// Common validation rules
const rules = {
  required: (v: any) => !!v || 'This field is required',
  positive: (v: number) => v > 0 || 'Must be greater than 0',
  maxLength: (max: number) => (v: string) =>
    !v || v.length <= max || `Maximum ${max} characters`,
  email: (v: string) =>
    !v || /.+@.+\..+/.test(v) || 'Invalid email address',
  minPassword: (v: string) =>
    !v || v.length >= 8 || 'Password must be at least 8 characters'
}

// Apply to forms
<v-text-field
  v-model="amount"
  label="Amount"
  type="number"
  :rules="[rules.required, rules.positive]"
  required
/>

<v-text-field
  v-model="description"
  label="Description"
  :rules="[rules.required, rules.maxLength(200)]"
  counter="200"
  required
/>
```

**Files to Update**:
- `frontend/src/components/Onboarding.vue` (all steps)
- `frontend/src/views/Dashboard.vue` (transaction form)
- `frontend/src/views/Settings.vue` (expense forms)
- `frontend/src/components/AuthModal.vue` (login/register)

**Part 2: Password Reset Script (2 hours)**

```python
# scripts/reset_user_password.py
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.database import EncryptedDatabase
from api.auth import hash_password
from dotenv import load_dotenv
import getpass

load_dotenv()

def reset_password():
    db = EncryptedDatabase(
        db_path="api/budget.db",
        encryption_key=os.getenv("DB_ENCRYPTION_KEY")
    )

    username = input("Enter username to reset: ").strip()
    user = db.get_user_by_username(username)

    if not user:
        print(f"User '{username}' not found.")
        return

    print(f"Found user: {user['username']} (ID: {user['id']})")
    confirm = input("Reset password for this user? (yes/no): ")

    if confirm.lower() != 'yes':
        print("Cancelled.")
        return

    new_password = getpass.getpass("Enter new password: ")
    confirm_password = getpass.getpass("Confirm new password: ")

    if new_password != confirm_password:
        print("Passwords don't match.")
        return

    if len(new_password) < 8:
        print("Password must be at least 8 characters.")
        return

    # Update password
    password_hash = hash_password(new_password)

    import sqlite3
    with sqlite3.connect("api/budget.db") as conn:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE users SET password_hash = ? WHERE id = ?",
            (password_hash, user['id'])
        )
        conn.commit()

    print(f"Password reset successful for {username}")

if __name__ == "__main__":
    reset_password()
```

**Documentation** (`ADMIN_GUIDE.md`):
```markdown
# Admin Operations Guide

## Resetting User Passwords (Beta)

During beta, use the admin script for password resets:

```bash
python scripts/reset_user_password.py
```

Follow the prompts to:
1. Enter username
2. Confirm user identity
3. Enter new password
4. User can now log in with new password
```

**Acceptance Test**:
- All forms show validation errors before submission
- Invalid input prevents form submission
- Password reset script successfully resets password
- User can log in with new password

---

### Day 4: Deployment Ready (8 points)

#### Morning (3 hours) - Task 1.3.1: Production CORS (3 pts)

**Implementation**:

```python
# api/main.py - Update CORS configuration

# Add to .env
CORS_ORIGINS=http://localhost:5173,https://your-app.railway.app

# Update CORS middleware
allowed_origins = os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**Testing**:
```bash
# Test from different origins
curl -H "Origin: http://localhost:5173" \
  -H "Access-Control-Request-Method: POST" \
  -X OPTIONS http://localhost:8000/api/auth/login

# Should return CORS headers
```

---

#### Afternoon (5 hours) - Task 1.3.2: Deployment Guide (5 pts)

**Create Comprehensive Guide**:

```markdown
# DEPLOYMENT_GUIDE.md

# Deploying The Number to Railway (Recommended)

## Prerequisites
- GitHub account
- Railway account (sign up at railway.app)
- Code pushed to GitHub repository

## Step 1: Prepare Environment Variables

Create `.env.production` (DO NOT COMMIT):

```
DB_ENCRYPTION_KEY=<generate with: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())">
JWT_SECRET_KEY=<generate with: python -c "import secrets; print(secrets.token_urlsafe(32))">
CORS_ORIGINS=https://your-frontend.railway.app
LOG_LEVEL=INFO
```

## Step 2: Create Railway Project

1. Go to railway.app/new
2. Click "Deploy from GitHub repo"
3. Select your repository
4. Railway auto-detects Python app

## Step 3: Configure Service

### Environment Variables
In Railway dashboard:
- Click your service
- Go to "Variables" tab
- Add each variable from `.env.production`
- Click "Add Variable" for each

### Start Command
In "Settings" tab:
- Custom Start Command: `uvicorn api.main:app --host 0.0.0.0 --port $PORT`

### Root Directory
If needed:
- Root Directory: `/` (or `/api` if structured differently)

## Step 4: Add Database Volume (Critical!)

Railway's filesystem is ephemeral. Database needs persistent storage:

1. In service settings, click "Volumes"
2. Click "New Volume"
3. Mount Path: `/app/data`
4. Update `api/main.py` to use volume:
   ```python
   db_path = os.getenv("DB_PATH", "/app/data/budget.db")
   ```

## Step 5: Deploy

1. Railway automatically deploys on git push
2. Wait for build to complete (3-5 minutes)
3. Get your URL: `your-app.railway.app`

## Step 6: Verify Deployment

```bash
# Health check
curl https://your-app.railway.app/health

# Should return:
{
  "status": "healthy",
  "encryption_configured": true,
  "auth_configured": true
}
```

## Step 7: Deploy Frontend

### Option A: Deploy to Railway (separate service)
1. Create new service in same project
2. Select frontend directory
3. Build command: `npm run build`
4. Start command: `npm run preview` (or use Caddy/nginx)

### Option B: Deploy to Vercel (simpler for static)
1. Go to vercel.com
2. Import from GitHub
3. Framework: Vite
4. Build command: `npm run build`
5. Output directory: `dist`
6. Environment variables:
   ```
   VITE_API_URL=https://your-backend.railway.app
   ```

## Troubleshooting

### "Module not found"
- Ensure `requirements.txt` includes all dependencies
- Railway auto-installs from requirements.txt

### Database errors
- Check volume is mounted at `/app/data`
- Verify DB_ENCRYPTION_KEY is set

### CORS errors
- Verify frontend URL in CORS_ORIGINS
- Include protocol (https://)
- No trailing slash

### Server won't start
- Check logs in Railway dashboard
- Verify all required env vars are set
- Test start command locally first

## Monitoring

### View Logs
Railway dashboard → Service → Deployments → View Logs

### Metrics
Railway provides basic metrics:
- CPU usage
- Memory
- Network

### Alerts
Set up alerts in Railway for:
- Deployment failures
- High memory usage
- Service restarts

## Backup Strategy

### Automated Backups
Railway doesn't auto-backup volumes. Options:

1. **Scheduled backup to Railway storage**:
   Add to `Procfile`:
   ```
   backup: python scripts/backup_database.py
   ```
   Configure Railway cron (if available) or use external cron service

2. **Export to cloud storage**:
   Use AWS S3, Google Cloud Storage, or similar
   Script to upload backups daily

3. **Manual backups**:
   Use Railway CLI to download volume:
   ```bash
   railway volume download
   ```

### Restore Process
1. Download backup file
2. Railway CLI: `railway volume upload`
3. Or use admin panel to restore

## Scaling Considerations

Free tier limits:
- $5 credit/month
- 512MB RAM
- Shared CPU
- Should handle 10-50 concurrent users

When to upgrade:
- More than 50 regular users
- Need more than 512MB RAM
- Want guaranteed uptime SLA

## Security Checklist

- [ ] All environment variables set
- [ ] CORS configured for production domain only
- [ ] HTTPS enforced (Railway does this automatically)
- [ ] Debug logging disabled (LOG_LEVEL=INFO)
- [ ] Database volume configured
- [ ] Backup system tested
- [ ] Health check endpoint accessible

## Cost Estimate

Railway pricing:
- Free: $5/month credit
- Hobby: $5/month (if you exceed free credit)
- Estimated for 10 beta users: Free tier sufficient

## Next Steps After Deployment

1. Test full user journey (register → onboard → use)
2. Create test account
3. Verify backup system
4. Document production URL for beta invites
5. Set up monitoring/alerting

## Getting Help

- Railway Discord: railway.app/discord
- Documentation: docs.railway.app
- GitHub Issues: (your repo)
```

**Acceptance Test**:
- Successfully deploy to Railway test instance
- Health check returns 200
- Can register user and log in
- Database persists across deployments

---

### Day 5: Testing & Buffer (Buffer Day)

#### Full System Testing (All Day)

**Test Scenarios**:

1. **New User Onboarding**:
   - Register account
   - Complete onboarding flow
   - Configure budget (both modes)
   - Add expenses
   - Record transaction
   - View "The Number"

2. **Data Persistence**:
   - Create data → Restart server → Verify data intact
   - Logout → Login → Verify session
   - Create backup → Simulate data loss → Restore

3. **Error Handling**:
   - Invalid inputs on all forms
   - Missing auth token
   - Expired token
   - Network failures

4. **Cross-Browser Testing**:
   - Chrome/Edge
   - Firefox
   - Safari (if available)
   - Mobile browsers

5. **Performance**:
   - Load time < 2 seconds
   - "The Number" calculation < 500ms
   - No console errors

**Bug Fixes**:
- Reserve this day for unexpected issues
- Don't start new features

**Pre-Beta Final Checklist**:
```markdown
- [ ] All 7 Tier 1 tasks complete
- [ ] Deployed to production
- [ ] Health check passing
- [ ] Test user successfully completes workflow
- [ ] Backup created and restore tested
- [ ] All validation working
- [ ] No critical console errors
- [ ] Documentation complete:
  - [ ] SETUP_GUIDE.md
  - [ ] DEPLOYMENT_GUIDE.md
  - [ ] ADMIN_GUIDE.md
  - [ ] USER_GUIDE.md (for beta testers)
- [ ] Beta invite email drafted
- [ ] Feedback form created
- [ ] Support channel set up
```

---

## Daily Standup Format

### Template (Solo Developer)
**Yesterday**:
- What I completed
- Blockers encountered
- Solutions found

**Today**:
- Priority tasks
- Expected completion
- Known risks

**Blockers**:
- Current blockers
- Help needed
- Workarounds

---

## Definition of Done

### Task Complete When:
- [ ] Code implemented
- [ ] Manual testing passed
- [ ] Acceptance criteria met
- [ ] Documentation updated
- [ ] No new critical bugs introduced
- [ ] Deployed to test environment (if applicable)

### Sprint Complete When:
- [ ] All tasks marked done
- [ ] Sprint goal achieved
- [ ] Production deployment successful
- [ ] Retrospective completed

---

## Risk Mitigation

### If Behind Schedule:
1. **Cut Scope**: Move lower priority items to Sprint 2
   - Example: Automated backups → Manual only for beta
2. **Simplify Solution**:
   - Example: Full PWA → Just manifest for now
3. **Ask for Help**:
   - Post in developer communities
   - Consult documentation

### If Deployment Fails:
1. Test locally first with production-like config
2. Use Railway's preview environments
3. Keep local backup of working state
4. Document rollback procedure

### If Critical Bug Found:
1. Assess severity: Can beta proceed?
2. If yes: Document known issue, plan fix for Sprint 2
3. If no: Delay beta, fix immediately

---

## Sprint Retrospective Template

**What Went Well**:
- Successes
- Efficient processes
- Learning moments

**What Could Improve**:
- Challenges faced
- Time estimation accuracy
- Tool/process improvements

**Action Items**:
- Concrete changes for next sprint
- Owner and deadline for each

---

## Tools & Resources

### Development
- VS Code with extensions: Python, Vue, SQLite Viewer
- Postman/Insomnia for API testing
- Browser DevTools

### Deployment
- Railway CLI: `npm install -g @railway/cli`
- Git for version control
- Environment variable management tool (e.g., dotenv-vault)

### Communication
- GitHub Issues for bug tracking
- Markdown for documentation
- Google Forms/Typeform for beta feedback

---

**Last Updated**: 2025-12-26
**Sprint Start**: TBD
**Sprint End**: TBD (5 working days from start)
