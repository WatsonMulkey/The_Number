# The Number - Feature Backlog

**Last Updated:** 2025-12-15

This document tracks all planned features, organized by priority and implementation complexity.

---

## Current Sprint: PWA MVP

**Status:** In Progress
**Target:** 4 weeks
**Goal:** Launch installable PWA with core budgeting functionality

- [x] Plan PWA architecture
- [ ] Set up Astro.js project structure
- [ ] Design Figma mockups (User working on this)
- [ ] Build responsive UI from mockups
- [ ] Implement REST API (FastAPI)
- [ ] Add authentication (JWT)
- [ ] Implement PWA manifest + service worker
- [ ] Add push notifications
- [ ] Deploy to production

---

## High Priority Backlog

### 1. Email Receipt Processing ⭐⭐⭐
**Status:** Planned
**Complexity:** Medium
**Time Estimate:** 2 weeks
**Dependencies:** PWA MVP completed, 100+ active users

**User Story:**
As a user, I want to forward receipts to a dedicated email address so that my spending is automatically logged without manual entry.

**Implementation:**
- Give each user unique email: `user123@receipts.thenumber.app`
- Set up email webhook (Mailgun/SendGrid)
- Parse email body for amount and merchant
- Auto-create transaction
- Send confirmation email to user

**Acceptance Criteria:**
- [ ] User can enable email receipts in settings
- [ ] User gets unique email address
- [ ] Forwarded receipts are parsed correctly (80% accuracy)
- [ ] Transaction is auto-created
- [ ] User receives confirmation email
- [ ] User can correct via email reply

**Cost Estimate:**
- Free tier: Up to 5,000 emails/month
- Paid tier (if >5k/month): $15-20/month

**Notes:**
- Start with simple text parsing
- Add image/PDF OCR later if needed
- Edge cases: international formats, multiple items, tips/taxes

---

### 2. Charts & Spending Analytics ⭐⭐⭐
**Status:** Planned
**Complexity:** Medium
**Time Estimate:** 1 week

**User Story:**
As a user, I want to see visual charts of my spending trends so I can understand my habits better.

**Features:**
- Daily spending line chart (last 30 days)
- Category breakdown pie chart
- Monthly comparison bar chart
- Spending vs budget gauge

**Tech Stack:**
- Chart.js or Recharts (lightweight)
- Store historical data in database

**Acceptance Criteria:**
- [ ] User can view spending trends
- [ ] Charts are responsive on mobile
- [ ] Data updates in real-time
- [ ] User can filter by date range

---

### 3. Recurring Transactions ⭐⭐
**Status:** Planned
**Complexity:** Low
**Time Estimate:** 3 days

**User Story:**
As a user, I want to mark transactions as recurring so I don't have to manually log my Netflix subscription every month.

**Implementation:**
- Add `is_recurring` flag to transactions
- Add `recurrence_pattern` (daily, weekly, monthly)
- Cron job auto-creates recurring transactions

**Acceptance Criteria:**
- [ ] User can mark transaction as recurring
- [ ] User can set recurrence pattern
- [ ] Transactions auto-create on schedule
- [ ] User can edit/delete recurring transaction

---

## Medium Priority Backlog

### 4. Budget Templates ⭐⭐
**Status:** Backlog
**Complexity:** Low
**Time Estimate:** 2 days

**User Story:**
As a new user, I want to start with a budget template so I don't have to enter all expenses manually.

**Templates:**
- College Student (rent, groceries, textbooks, etc.)
- Young Professional (rent, 401k, car, dining)
- Family of 4 (mortgage, groceries, kids, utilities)
- Retiree (fixed income, healthcare, leisure)

**Acceptance Criteria:**
- [ ] User can select template during onboarding
- [ ] Template pre-fills common expenses
- [ ] User can customize after selecting

---

### 5. Multi-Device Sync ⭐⭐
**Status:** Backlog
**Complexity:** Medium
**Time Estimate:** 1 week

**User Story:**
As a user, I want my budget to sync across all my devices so I can access it from phone, tablet, and computer.

**Implementation:**
- Already handled by backend (all data server-side)
- Add real-time updates via WebSockets
- Conflict resolution if offline edits on multiple devices

**Acceptance Criteria:**
- [ ] Changes on one device appear on others
- [ ] Offline edits sync when reconnected
- [ ] No data loss from conflicts

---

### 6. Export & Reports ⭐⭐
**Status:** Backlog
**Complexity:** Low
**Time Estimate:** 2 days

**User Story:**
As a user, I want to export my budget data so I can analyze it in Excel or share with my accountant.

**Export Formats:**
- CSV (transactions + expenses)
- PDF (monthly report with charts)
- JSON (full data export)

**Acceptance Criteria:**
- [ ] User can export to CSV/PDF/JSON
- [ ] Export includes all transactions and expenses
- [ ] PDF includes charts and summary

---

### 7. Shared Budgets (Couples/Families) ⭐
**Status:** Backlog
**Complexity:** High
**Time Estimate:** 2 weeks

**User Story:**
As a user, I want to share my budget with my partner so we can track our finances together.

**Implementation:**
- Add "Share Budget" feature
- Invite via email
- Permissions: view-only or edit
- Each person can add transactions
- Collaborative expense management

**Acceptance Criteria:**
- [ ] User can invite others to budget
- [ ] Invited user can accept/decline
- [ ] Shared transactions visible to all
- [ ] Individual transactions stay private (optional)

---

## Low Priority Backlog

### 8. Dark Mode ⭐
**Status:** Backlog
**Complexity:** Low
**Time Estimate:** 1 day

**Implementation:**
- CSS variables for theme
- Toggle in settings
- Respect system preference by default

---

### 9. Multiple Currencies ⭐
**Status:** Backlog
**Complexity:** Medium
**Time Estimate:** 3 days

**Implementation:**
- User selects currency in settings
- All amounts formatted in chosen currency
- Optional: Exchange rate conversions

---

### 10. Savings Goals Tracker ⭐
**Status:** Backlog
**Complexity:** Medium
**Time Estimate:** 1 week

**User Story:**
As a user, I want to set savings goals so I can track progress toward large purchases or emergency funds.

**Features:**
- Set goal name and target amount
- Track progress
- Visualize with progress bar
- Allocate money toward goal

---

### 11. Bill Reminders
**Status:** Backlog
**Complexity:** Low
**Time Estimate:** 2 days

**User Story:**
As a user, I want reminders for upcoming bills so I never miss a payment.

**Implementation:**
- User sets bill due dates
- Push notification 3 days before
- Mark as paid

---

### 12. Spending Challenges
**Status:** Backlog
**Complexity:** Medium
**Time Estimate:** 1 week

**User Story:**
As a user, I want to participate in spending challenges (e.g., "No eating out for 30 days") to gamify saving money.

**Features:**
- Pre-set challenges
- Custom challenges
- Track streaks
- Badges/achievements

---

## Deferred / Won't Do

### SMS Notifications
**Reason:** Too expensive at scale ($9,480/month for 10k users)
**Alternative:** Email + PWA push notifications
**Status:** Deferred indefinitely

### Bank API Integration (Plaid)
**Reason:** Too expensive ($2,500-5,000/month) + extreme security requirements
**Alternative:** Manual entry + email receipts
**Status:** Deferred until revenue >$10k/month + security audit

### Native Mobile Apps (iOS/Android)
**Reason:** PWA provides 80% of benefits for 10% of effort
**Alternative:** PWA with install prompt
**Status:** Deferred until 10,000+ users prove demand

---

## Feature Prioritization Framework

We use the **RICE Score** to prioritize features:

**RICE = (Reach × Impact × Confidence) / Effort**

- **Reach:** How many users will this affect? (1-10 scale)
- **Impact:** How much will it improve the experience? (0.25, 0.5, 1, 2, 3)
- **Confidence:** How sure are we? (0.5 = low, 0.8 = medium, 1.0 = high)
- **Effort:** Person-weeks to implement

### Example Calculation:

**Email Receipt Processing:**
- Reach: 8 (80% of users will use it)
- Impact: 3 (massive time savings)
- Confidence: 0.8 (pretty sure we can build it)
- Effort: 2 weeks

RICE = (8 × 3 × 0.8) / 2 = **9.6** (Very High Priority!)

**Dark Mode:**
- Reach: 10 (all users see it)
- Impact: 0.5 (nice to have)
- Confidence: 1.0 (easy to implement)
- Effort: 0.2 weeks (1 day)

RICE = (10 × 0.5 × 1.0) / 0.2 = **25** (Actually high priority because so cheap!)

---

## How to Add to Backlog

1. **Describe the feature** with a user story
2. **Estimate complexity** (Low/Medium/High)
3. **Estimate time** in person-days/weeks
4. **Calculate RICE score**
5. **Add to appropriate priority section**
6. **Link related issues** (GitHub issues, user requests)

---

## Release Planning

### V1.0 (MVP) - Week 4
- PWA with core functionality
- User auth
- Add/view expenses and transactions
- See daily budget number
- Install on home screen
- Push notifications

### V1.1 - Week 8
- Email receipt processing
- Basic charts
- Recurring transactions
- Dark mode

### V1.2 - Week 12
- Budget templates
- Export/reports
- Multi-device sync improvements

### V2.0 - Month 6
- Shared budgets
- Savings goals
- Spending challenges
- Mobile app (if user base justifies)

---

## User-Requested Features

Track feature requests from users here:

| Feature | Requested By | Date | Votes | Status |
|---------|-------------|------|-------|--------|
| Email receipts | Watson | 2025-12-15 | 1 | Planned |
| (Add more as users request) | | | | |

---

## Feature Sunset Policy

Features may be deprecated if:
- Less than 5% of users use them
- Maintenance cost exceeds value
- Security concerns arise
- Better alternative exists

Deprecated features get 30-day notice to users before removal.

---

**Questions about the backlog? Want to propose a feature? Open a GitHub issue!**
