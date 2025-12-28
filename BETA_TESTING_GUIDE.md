# Beta Testing Guide for The Number

**Welcome Beta Tester!** Thank you for helping test The Number before public launch.

---

## What is The Number?

The Number is a budgeting app that calculates your daily spending limit based on your income and expenses. Instead of complex budgets, you get one simple number: how much you can spend today.

---

## Beta Details

- **Duration**: 1 week
- **Purpose**: Find UX issues and bugs before public launch
- **Your Data**: Please use real financial data (but understand data loss is possible)
- **Reward**: Lifetime free access when we launch paid version
- **Support**: Dedicated support channel, response within 4 hours

---

## Getting Started

### 1. Account Setup
1. Visit: `https://your-app-url.railway.app`
2. Click "Register"
3. Choose username and password (min 8 characters)
4. Optional: Add email (for future password reset feature)

### 2. Onboarding Flow
You'll be guided through setup:
1. **Choose Budget Mode**:
   - **Paycheck Mode**: Living paycheck to paycheck
   - **Fixed Pool**: Have money saved up
2. **Configure Your Budget**:
   - Enter monthly income (Paycheck) or total savings (Fixed Pool)
   - Set timeframe (days until paycheck or target date)
3. **Add Expenses**:
   - Fixed expenses (rent, subscriptions, etc.)
   - Variable expenses (groceries, entertainment)
4. **See Your Number**:
   - Your daily spending limit appears!

### 3. Daily Use
- **Dashboard**: See "The Number" - your spending limit for today
- **Record Spending**: Log purchases to track against your limit
- **Money In**: Record unexpected income (gifts, freelance, etc.)
- **Check History**: See recent transactions

---

## Testing Focus Areas

Please specifically test these areas and provide feedback:

### Critical: Core Workflow
1. **Onboarding**:
   - Was it clear what to do?
   - Any confusing steps?
   - Did you understand both budget modes?

2. **The Number Calculation**:
   - Does the number make sense?
   - Does it update when you record spending?
   - Does it adjust after recording income?

3. **Recording Transactions**:
   - Easy to log a purchase?
   - Can you edit/delete mistakes?
   - Do transactions show up in history?

### Important: UX/Design
1. **Navigation**:
   - Can you find all features easily?
   - Is the menu clear?
   - Any dead ends or confusion?

2. **Visual Design**:
   - Is the interface pleasant to use?
   - Text readable on your device?
   - Colors/contrast acceptable?

3. **Mobile Experience**:
   - Works on your phone?
   - Touch targets easy to hit?
   - Forms easy to fill on mobile?

### Nice to Have: Edge Cases
1. **Error Handling**:
   - What happens if you enter negative numbers?
   - What if you exceed your daily limit?
   - What about very large amounts?

2. **Data Persistence**:
   - Close app and reopen - data still there?
   - Logout and login - everything intact?
   - Multiple days - does calculation adjust?

---

## How to Report Issues

### Bug Report Template
When you find a bug, please include:

1. **What you were trying to do**:
   Example: "I was trying to record a $50 grocery purchase"

2. **What happened**:
   Example: "The form submitted but the transaction didn't appear in my history"

3. **What you expected**:
   Example: "I expected to see the transaction in my recent transactions list"

4. **Steps to reproduce**:
   1. Go to Dashboard
   2. Click "Record Spending"
   3. Enter $50 for "Groceries"
   4. Click Submit
   5. Check transaction history - transaction missing

5. **Device/Browser**:
   Example: "iPhone 12, Safari" or "Windows 11, Chrome"

6. **Screenshot** (if relevant):
   Attach or describe what you see

### UX Feedback Template
When you have UX feedback:

1. **What confused you**:
   Example: "I didn't understand the difference between Fixed and Variable expenses"

2. **What you expected**:
   Example: "I expected a tooltip or explanation"

3. **Suggested improvement**:
   Example: "Add a small (i) icon with explanation text"

4. **Priority** (your opinion):
   - Critical: Can't complete core workflow
   - Important: Annoying but can work around
   - Nice to have: Would improve experience

---

## Feedback Form

[Link to Google Form or Typeform]

**Categories**:
- Bugs (something broken)
- Confusing UX (something unclear)
- Feature Requests (something missing)
- General Feedback (overall impressions)

---

## Known Issues

We're aware of these limitations in the beta:

1. **No password reset (yet)**:
   - If you forget password, message us for admin reset
   - Self-service coming in next version

2. **No offline mode**:
   - Requires internet connection
   - PWA offline features coming post-beta

3. **Basic error messages**:
   - Some errors may not be super helpful
   - We're improving these based on your feedback

4. **No mobile app (yet)**:
   - Web-only for now
   - Works on mobile browsers
   - Mobile app planned for future

---

## Testing Checklist

Use this to ensure you've tested all core features:

### Day 1: Setup
- [ ] Register account
- [ ] Complete onboarding
- [ ] Configure budget (try one mode)
- [ ] Add at least 5 expenses
- [ ] See "The Number" calculate

### Day 2: Daily Use
- [ ] Record at least 3 spending transactions
- [ ] Check that "The Number" decreases
- [ ] Try recording "Money In"
- [ ] View transaction history

### Day 3: Adjustments
- [ ] Add or remove an expense
- [ ] See if "The Number" recalculates
- [ ] Try the other budget mode (Settings)
- [ ] Record a large purchase (test limits)

### Day 4: Edge Cases
- [ ] Try entering $0.00 (should fail)
- [ ] Try entering $1,000,000 (test max)
- [ ] Try very long expense names
- [ ] Test on different device/browser

### Day 5: Data Integrity
- [ ] Log out and log back in
- [ ] Verify all data still there
- [ ] Close browser and reopen
- [ ] Check calculations still accurate

### Day 6: Final Testing
- [ ] Try to break something intentionally
- [ ] Test any previously reported bugs (see if fixed)
- [ ] Export your data (Settings → Backup)
- [ ] Complete feedback form

### Day 7: Wrap-up
- [ ] Final impressions
- [ ] Would you recommend to friends?
- [ ] One thing you'd improve most?

---

## Support & Communication

### Where to Get Help
- **Support Channel**: [Discord/Slack link]
- **Email**: watson@foil.engineering
- **Response Time**: Within 4 hours (usually faster)

### Office Hours
Two live Q&A sessions during beta week:
- **Mid-week Check-in**: Wednesday 7-8pm [timezone]
- **Final Feedback Session**: Saturday 2-3pm [timezone]

### What to Expect
- Quick fixes for critical bugs (within 24 hours)
- UX improvements after beta (based on patterns)
- Feature requests prioritized for post-beta roadmap

---

## Privacy & Data

### What We Track
- Account info (username, email if provided)
- Expenses and transactions (encrypted)
- Budget configuration
- Usage patterns (anonymized)

### What We Don't Track
- Specific financial amounts (not sent to analytics)
- Personal identifiable info beyond username
- Your actual spending habits (that's private)

### Data Retention
- Beta data will be migrated to production
- You can export or delete anytime
- Lifetime free access means your account stays active

### Backup Your Data
We recommend:
1. Export data weekly (Settings → Backup)
2. Save export file somewhere safe
3. Beta is stable, but better safe than sorry

---

## Frequently Asked Questions

### What if I find a critical bug?
Message us immediately in the support channel. We'll fix it ASAP.

### Can I invite others to beta?
Please ask first - we want to keep beta small and manageable.

### What happens after beta?
- We'll fix issues you found
- Launch public version (with Gumroad payment)
- Your account stays free forever (thank you gift)

### Will my data be deleted?
No! Beta data migrates to production. You keep everything.

### Can I use this as my primary budgeting tool?
Absolutely! We're confident in the core features. Just know we're still polishing.

### What if I have feature ideas?
We'd love to hear them! Use the "Feature Requests" category in the feedback form.

### How technical do I need to be?
Not at all! We want feedback from regular people. Tell us if something's confusing.

### What's the best way to give feedback?
Honest and specific. "This confused me" is more helpful than "looks good!"

---

## Thank You!

Your feedback will directly shape The Number before launch. We're grateful for your time and honest input.

**Remember**: There are no wrong answers. If something confused YOU, it will confuse others. We want to know!

Happy testing! 🎉

---

**Beta Coordinator**: [Your Name]
**Beta Dates**: [Start] - [End]
**Version**: 0.9.0 (Beta)
