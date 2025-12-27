# The Number - PWA Implementation Plan

**Goal:** Build a Progressive Web App that allows users to track daily spending and view their budget number, with the foundation to add email receipt processing later.

---

## Architecture Overview

### Technology Stack

**Frontend (PWA):**
- HTML5 + CSS3 (responsive design)
- Vanilla JavaScript (or lightweight framework like Alpine.js/Preact)
- Service Worker for offline support
- Web Push API for notifications
- IndexedDB for local storage
- Manifest.json for installability

**Backend (Python):**
- FastAPI or Flask (lightweight REST API)
- Existing SQLite + encryption for database
- Existing calculator.py for budget logic
- JWT tokens for authentication
- Web Push notifications (pywebpush library)

**Hosting:**
- Frontend: Vercel or Netlify (FREE tier)
- Backend: Railway, Render, or fly.io (FREE tier)
- Database: User-specific SQLite files on backend

---

## Project Structure

```
Dev/
├── src/                      # Existing Python backend
│   ├── calculator.py         # Already exists
│   ├── database.py           # Already exists
│   └── api.py               # NEW: REST API endpoints
│
├── web/                      # NEW: PWA frontend
│   ├── index.html           # Main app page
│   ├── login.html           # Login page
│   ├── signup.html          # Signup page
│   ├── css/
│   │   └── styles.css       # Responsive styles
│   ├── js/
│   │   ├── app.js           # Main application logic
│   │   ├── api.js           # API client
│   │   └── sw.js            # Service worker
│   ├── manifest.json        # PWA manifest
│   └── icons/               # App icons (192x192, 512x512)
│
├── tests/
│   └── test_api.py          # NEW: API tests
│
└── deploy/
    ├── vercel.json          # Vercel deployment config
    └── railway.toml         # Railway deployment config
```

---

## Phase 1: Core Web Dashboard (Week 1-2)

### Features:
1. **Authentication**
   - Sign up / Log in
   - JWT token-based auth
   - Secure password hashing

2. **Dashboard**
   - Display "The Number" prominently
   - Show remaining budget
   - List today's transactions
   - Add new transaction form

3. **Expense Management**
   - View all expenses
   - Add/edit/delete expenses
   - Mark as fixed or variable

4. **Settings**
   - Choose budget mode (paycheck vs fixed pool)
   - Set income/total money
   - Set days until paycheck

### API Endpoints Needed:

```python
# Authentication
POST   /api/auth/signup
POST   /api/auth/login
POST   /api/auth/logout
GET    /api/auth/me

# Budget
GET    /api/budget/number         # Get today's daily budget
GET    /api/budget/summary        # Get full budget breakdown

# Transactions
GET    /api/transactions          # List transactions
POST   /api/transactions          # Add transaction
DELETE /api/transactions/:id     # Delete transaction

# Expenses
GET    /api/expenses              # List expenses
POST   /api/expenses              # Add expense
PUT    /api/expenses/:id          # Update expense
DELETE /api/expenses/:id          # Delete expense

# Settings
GET    /api/settings              # Get user settings
PUT    /api/settings              # Update settings
```

### UI Components:

```
┌─────────────────────────────────────┐
│  The Number                    ☰   │
├─────────────────────────────────────┤
│                                     │
│         Your Daily Budget           │
│                                     │
│            $47.50                   │
│                                     │
│   Income: $3000 | Expenses: $2000   │
│   Days Left: 15 | Remaining: $1000  │
│                                     │
├─────────────────────────────────────┤
│  Today's Spending                   │
│                                     │
│  [$12.00] Coffee - Starbucks        │
│  [$8.50]  Lunch - Chipotle          │
│                                     │
│  [+ Add Spending]                   │
│                                     │
├─────────────────────────────────────┤
│  Monthly Expenses                   │
│                                     │
│  [$1500] Rent (Fixed)               │
│  [$300]  Groceries (Variable)       │
│  [$200]  Utilities (Fixed)          │
│                                     │
│  [+ Add Expense]                    │
│                                     │
└─────────────────────────────────────┘
```

---

## Phase 2: PWA Features (Week 3)

### 1. Make It Installable

**manifest.json:**
```json
{
  "name": "The Number - Daily Budget Tracker",
  "short_name": "The Number",
  "description": "Know your daily spending limit instantly",
  "start_url": "/",
  "display": "standalone",
  "theme_color": "#2563eb",
  "background_color": "#ffffff",
  "orientation": "portrait",
  "icons": [
    {
      "src": "/icons/icon-192.png",
      "sizes": "192x192",
      "type": "image/png",
      "purpose": "any maskable"
    },
    {
      "src": "/icons/icon-512.png",
      "sizes": "512x512",
      "type": "image/png",
      "purpose": "any maskable"
    }
  ]
}
```

### 2. Add Service Worker for Offline Support

**sw.js:**
```javascript
const CACHE_NAME = 'the-number-v1';
const urlsToCache = [
  '/',
  '/css/styles.css',
  '/js/app.js',
  '/js/api.js',
  '/icons/icon-192.png'
];

// Install - cache resources
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => cache.addAll(urlsToCache))
  );
});

// Fetch - serve from cache, fallback to network
self.addEventListener('fetch', (event) => {
  event.respondWith(
    caches.match(event.request)
      .then((response) => response || fetch(event.request))
  );
});
```

### 3. Add Install Prompt

**app.js:**
```javascript
let deferredPrompt;

window.addEventListener('beforeinstallprompt', (e) => {
  // Prevent default install prompt
  e.preventDefault();
  deferredPrompt = e;

  // Show custom install button
  document.getElementById('installButton').style.display = 'block';
});

document.getElementById('installButton').addEventListener('click', async () => {
  if (deferredPrompt) {
    deferredPrompt.prompt();
    const { outcome } = await deferredPrompt.userChoice;
    console.log(`Install outcome: ${outcome}`);
    deferredPrompt = null;
  }
});
```

---

## Phase 3: Push Notifications (Week 4)

### 1. Request Permission

**app.js:**
```javascript
async function subscribeToPushNotifications() {
  const permission = await Notification.requestPermission();

  if (permission === 'granted') {
    const registration = await navigator.serviceWorker.ready;

    const subscription = await registration.pushManager.subscribe({
      userVisibleOnly: true,
      applicationServerKey: urlBase64ToUint8Array(PUBLIC_VAPID_KEY)
    });

    // Send subscription to backend
    await fetch('/api/push/subscribe', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(subscription)
    });
  }
}
```

### 2. Backend Push Service

**api.py:**
```python
from pywebpush import webpush
import json

def send_daily_budget_notification(user):
    """Send daily budget notification to user."""
    budget = get_daily_budget(user)

    payload = json.dumps({
        "title": "The Number",
        "body": f"Your daily budget: ${budget:.2f}",
        "icon": "/icons/icon-192.png",
        "badge": "/icons/badge-72.png",
        "data": {
            "url": "/"
        }
    })

    webpush(
        subscription_info=user.push_subscription,
        data=payload,
        vapid_private_key=VAPID_PRIVATE_KEY,
        vapid_claims={"sub": "mailto:support@thenumber.app"}
    )
```

### 3. Schedule Daily Notifications

**scheduler.py:**
```python
from apscheduler.schedulers.background import BackgroundScheduler

scheduler = BackgroundScheduler()

def send_daily_notifications():
    """Send notifications to all users at their preferred time."""
    users = get_all_active_users()

    for user in users:
        if user.notification_time_utc == current_hour():
            send_daily_budget_notification(user)

# Run every hour, check if it's user's notification time
scheduler.add_job(send_daily_notifications, 'cron', hour='*')
scheduler.start()
```

---

## Phase 4: Polish & Deployment (Week 4)

### 1. Responsive Design

**Mobile-first CSS:**
```css
/* Mobile (default) */
.container {
  max-width: 100%;
  padding: 1rem;
}

.budget-number {
  font-size: 3rem;
  font-weight: bold;
  color: #2563eb;
}

/* Tablet */
@media (min-width: 768px) {
  .container {
    max-width: 720px;
    margin: 0 auto;
  }
}

/* Desktop */
@media (min-width: 1024px) {
  .container {
    max-width: 960px;
  }

  .dashboard {
    display: grid;
    grid-template-columns: 2fr 1fr;
    gap: 2rem;
  }
}
```

### 2. Performance Optimization

- Lazy load images
- Minify CSS/JS
- Enable gzip compression
- Use CDN for static assets
- Implement code splitting

### 3. Deployment

**Vercel (Frontend):**
```bash
# Install Vercel CLI
npm install -g vercel

# Deploy
cd web
vercel --prod
```

**Railway (Backend):**
```bash
# Install Railway CLI
npm install -g @railway/cli

# Deploy
railway up
```

---

## Future Enhancements (Backlog)

### High Priority

1. **Email Receipt Processing** ⭐
   - Users get dedicated email address: `user123@receipts.thenumber.app`
   - Forward receipts to this address
   - Parse email for amount and merchant
   - Auto-log transaction
   - Send confirmation email

2. **Charts & Analytics**
   - Spending trends over time
   - Category breakdown pie chart
   - Monthly comparison

3. **Multi-Device Sync**
   - Real-time sync across devices
   - Conflict resolution

### Medium Priority

4. **Budget Templates**
   - "College Student" preset
   - "Family of 4" preset
   - "Retiree" preset

5. **Recurring Transactions**
   - Mark transactions as recurring
   - Auto-add monthly subscriptions

6. **Export Data**
   - CSV export
   - PDF reports

### Low Priority

7. **Dark Mode**
8. **Multiple Currencies**
9. **Shared Budgets** (for couples/families)
10. **Savings Goals Tracker**

---

## Email Receipt Feature Design (Future)

### How It Works:

1. **User Setup:**
   - User enables email receipt feature in settings
   - App generates unique email: `john123@receipts.thenumber.app`
   - User adds this to contacts, sets up auto-forward rules

2. **Email Processing:**
   ```
   User → Forwards receipt email
        ↓
   receipts.thenumber.app (Mailgun/SendGrid webhook)
        ↓
   Parse email body/subject for:
   - Amount: $12.50
   - Merchant: "Starbucks"
   - Date: Today or from email
        ↓
   POST /api/transactions (auto-created)
        ↓
   Send confirmation email to user
   ```

3. **Email Parsing:**
   ```python
   def parse_receipt_email(email_body, subject):
       """Extract transaction from receipt email."""
       # Regex patterns for common amounts
       amount_patterns = [
           r'\$\s?(\d+\.\d{2})',           # $12.50
           r'Total:\s?\$?(\d+\.\d{2})',    # Total: $12.50
           r'Amount:\s?\$?(\d+\.\d{2})',   # Amount: 12.50
       ]

       # Find merchant (common patterns)
       merchant_patterns = [
           r'From:\s+(.+)',                # From: Starbucks
           r'Thank you for .*at\s+(.+)',   # Thank you for shopping at Walmart
       ]

       # Extract and create transaction
       amount = extract_first_match(email_body, amount_patterns)
       merchant = extract_first_match(email_body, merchant_patterns)

       return {
           'amount': amount,
           'description': merchant or 'Email receipt',
           'date': datetime.now()
       }
   ```

4. **Confirmation Email:**
   ```
   Subject: ✓ Transaction added: $12.50

   Hey John,

   We logged a transaction from your receipt:

   Amount: $12.50
   Merchant: Starbucks
   Date: Dec 15, 2025

   Your updated daily budget: $35.00

   Not correct? Reply to this email with corrections.

   - The Number
   ```

### Implementation Complexity:

- **Easy:** Basic email receiving (Mailgun/SendGrid webhook)
- **Medium:** Email parsing (regex + heuristics)
- **Hard:** Handling edge cases (receipts in images, PDFs, various formats)

### Cost Estimate:

- Mailgun: 5,000 emails/month FREE
- SendGrid: 100 emails/day FREE
- For 1,000 users × 3 receipts/day = 3,000 emails/day
  - Need paid tier: ~$15-20/month

**Decision:** Implement after user base proves demand (100+ active users)

---

## Success Metrics

### Week 1-2 (MVP):
- [ ] User can sign up and log in
- [ ] User can see their daily budget number
- [ ] User can add/view expenses
- [ ] User can log transactions
- [ ] All 192 existing tests still pass

### Week 3 (PWA):
- [ ] App is installable on iOS and Android
- [ ] App works offline
- [ ] Install prompt shows on first visit
- [ ] Service worker caches static assets

### Week 4 (Notifications):
- [ ] User can enable push notifications
- [ ] User receives daily budget notification
- [ ] Notifications work on both iOS and Android
- [ ] User can customize notification time

### Deployment:
- [ ] Frontend deployed to Vercel/Netlify
- [ ] Backend deployed to Railway/Render
- [ ] HTTPS enabled (SSL certificate)
- [ ] Custom domain configured
- [ ] Performance: <3s initial load, <100ms API responses

---

## Risk Mitigation

### Technical Risks:

1. **iOS Push Notification Limitations**
   - MITIGATION: Test on iOS 16.4+ (has full PWA support)
   - FALLBACK: Email notifications if push fails

2. **Service Worker Bugs**
   - MITIGATION: Comprehensive testing on multiple browsers
   - FALLBACK: App still works without service worker (degrades gracefully)

3. **Database Scaling**
   - MITIGATION: Start with SQLite, migrate to PostgreSQL if needed
   - THRESHOLD: >1,000 concurrent users

### Security Risks:

1. **JWT Token Theft**
   - MITIGATION: Short expiration (1 hour), refresh tokens, HTTPS only

2. **API Rate Limiting**
   - MITIGATION: Implement rate limiting (100 req/minute/user)

3. **XSS Attacks**
   - MITIGATION: Sanitize all user inputs, use CSP headers

---

## Next Steps

1. **Review this plan** - Does this align with your vision?
2. **Choose tech stack details** - FastAPI vs Flask? Pure JS vs Alpine.js?
3. **Create wireframes** - Sketch out the UI in more detail?
4. **Start implementation** - Begin with API endpoints?

**Ready to start building? Which part should I tackle first?**
