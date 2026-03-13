# ADR 003: Buyer Mode — Architecture Decisions

**Status:** Accepted
**Date:** 2026-03-09
**Decision Makers:** Watson Mulkey, Claude (with socratic-architect, senior-dev-skeptic, and research-orchestrator review)

---

## Context

Watson wants to build a browser extension that inverts the online advertising model. Instead of brands tracking users, users browse privately by default and optionally declare purchase intent when they're ready to buy. Brands compete to present offers through a closed marketplace. The user evaluates options and makes a purchase based on quality, aesthetics, and discount.

Key constraints:
- Proof of concept / MVP — demo-ready for investors and partners
- Privacy-first: users must remain anonymous to brands
- Extremely low barrier to entry for both users AND brands
- No integration with Google Ads / Meta APIs (research confirmed these require PII, which breaks the privacy promise)
- Closed marketplace where the platform acts as broker

Three agents contributed to this design:
- **Socratic Architect**: Full system architecture, data models, API design, phased roadmap
- **Senior Dev Skeptic**: Identified re-identification risks, ad platform incompatibility, legal concerns, UX friction
- **Research Orchestrator**: Surveyed Brave/BAT, Permission.io, Gener8, Swash; confirmed Google Privacy Sandbox death (Oct 2025); validated MV3 capabilities; confirmed ad platform APIs require PII

## Decisions

### 1. Chrome Extension (MV3) over standalone browser or web app

**Decision:** Build as a Chrome Extension using Manifest V3

**Options Considered:**
- Full browser (Chromium fork) — millions of LOC, years of work
- Chrome Extension (MV3) — shippable, focused, proven distribution channel
- Web app simulation — lower fidelity, doesn't demonstrate the real UX
- Firefox/Safari extension — defer to post-POC

**Why:** An extension is the smallest artifact that demonstrates the full concept. MV3 is Chrome's current standard. The extension can be sideloaded for demos and published to Chrome Web Store ($5 fee) when ready.

**Risk:** MV3 service workers die after 30 seconds of inactivity. Offer polling uses the Alarms API (5-min intervals) as a workaround. MV3's declarativeNetRequest has a 30K static rule limit (uBlock uses 300K+), but a curated 5-10K rule subset covers major trackers.

### 2. Closed marketplace over ad platform integration

**Decision:** Build a self-contained marketplace. Brands interact exclusively through our API/dashboard. No Google Ads, Meta, or HubSpot integration.

**Options Considered:**
- Path A: PII Relay — users consent to share hashed email, push Custom Audiences to ad platforms
- Path B: Closed Marketplace — brands come to our platform, never see individual user data

**Why:** Research confirmed all major ad platforms (Google, Meta, HubSpot) require PII-based matching. There is no API endpoint that accepts anonymous cohort data. Google/Meta would re-identify users using their own data graphs. Path A fundamentally breaks the privacy promise. Path B is more defensible, keeps the privacy model honest, and creates a moat.

**Risk:** Cold start — marketplace needs both buyers and sellers. Mitigated for POC with mock data. Real traction requires Watson's go-to-market work.

### 3. Cohort-based anonymization over individual-level data

**Decision:** Users are never exposed individually. Every user is assigned to a cohort based on coarse demographic bands. Brands see cohort attributes + intent, never individual identity.

**How it works:**
- Cohort hash: `SHA-256(ageRange + "|" + incomeRange + "|" + region + "|" + housing)`
- Demographics are collected as broad ranges (10-year age bands, income quartiles, state-level location)
- Gender excluded from cohort hash to increase cohort sizes
- k-anonymity threshold: k=100 (intent signals only surface when cohort has 100+ members)
- Ephemeral intent IDs: brands cannot correlate two signals from the same user
- PII scrubbing on intent descriptions (regex for emails, phones, addresses)

**Options Considered:**
- Individual-level encrypted data — encryption doesn't prevent re-identification
- Differential privacy noise injection — gold standard, but adds complexity for POC
- Cohort-based with k-anonymity — structural anonymization, simple to implement, scales to production

**Why:** The skeptic review identified that 99.98% of Americans can be re-identified with 15 demographic attributes. Coarse ranges + cohort thresholds make re-identification impractical. The architecture logs when signals would be suppressed (POC bypasses enforcement with a feature flag).

**Risk:** Cohort-level data is less precise for brands. This is an intentional tradeoff — privacy over precision. Post-POC can add differential privacy noise injection for mathematical guarantees.

### 4. Anonymous user auth (token-only, no PII)

**Decision:** Users have no email, no password. On first install, the extension generates a UUID, registers with the backend, and receives a bearer token stored in `chrome.storage.local`.

**Why:** The product promises privacy. Collecting emails or passwords would undermine the core value proposition. Users who care about privacy (the target market) would not trust an extension that asks for PII. Token-based auth is frictionless — zero onboarding steps.

**Risk:** If the user uninstalls the extension, the token is lost and the profile is orphaned. Acceptable for POC. Post-POC could add optional encrypted backup/restore.

### 5. Node.js + Express + PostgreSQL + Prisma for backend

**Decision:** TypeScript backend with Express, PostgreSQL for data, Prisma ORM

**Options Considered:**
- Python + FastAPI + SQLite — Watson's existing stack for The Number
- Node.js + Express + PostgreSQL — same language as extension, relational integrity for user-intent-offer relationships
- Serverless (Lambda/Vercel Functions) — cold starts degrade offer polling UX

**Why:** The extension is JavaScript. Sharing the language reduces context-switching. PostgreSQL handles the relational model (users → intents → offers → engagements) better than SQLite. Prisma provides type-safe queries and easy migrations. Fly.io and Vercel are Watson's existing deployment targets.

### 6. Email-first brand onboarding

**Decision:** Brands sign up with Company Name, Email, Website, and Categories of Interest. Verify email, immediately start receiving intent alerts.

**Why:** Watson's explicit requirement: "as easy as submitting an email address." Every additional field or step reduces brand signup conversion. For POC, manual admin approval of brand accounts prevents abuse. Post-POC, add domain verification.

### 7. Offer polling over WebSockets or push notifications

**Decision:** Extension polls for offers via Alarms API every 5 minutes

**Options Considered:**
- WebSockets — MV3 kills service workers, cannot maintain persistent connections
- Push API — requires visible notification (intrusive), needs a push service
- Polling via Alarms API — reliable, simple, 5-min interval is acceptable for "this week" urgency

**Why:** MV3's service worker lifecycle makes real-time delivery impossible without a persistent connection. Polling is the only reliable mechanism. 5-minute intervals balance freshness with API load. For "today" urgency intents, could reduce to 1-minute intervals post-POC.

## Consequences

### What becomes easier:
- Privacy model is structurally sound — not dependent on encryption or policy alone
- Brand onboarding is dead simple — email signup + category selection
- Extension is self-contained — no dependency on third-party ad platforms
- Architecture supports real anonymization at scale (k-anonymity thresholds)

### What becomes harder:
- No leverage from existing ad platform audiences — must build demand from scratch
- Brands must learn a new platform (the dashboard) rather than using tools they know
- Cohort-level targeting is less precise than individual-level — some brands may find this insufficient
- Legal review needed before public launch (CCPA data broker classification, GDPR)

### Follow-up work needed:
- Privacy attorney review of cohort model + data broker classification
- Chrome Web Store submission process (when ready for public distribution)
- Payment integration (Stripe) for brand billing on engagements
- Differential privacy layer for production-grade anonymization guarantees
