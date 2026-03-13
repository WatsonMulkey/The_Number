# Curtis Park Proposal: Double-Agent Verification Reconciliation

**Date**: 2026-02-12
**Agents**: Agent A (27 claims) and Agent B (19 claims)
**Purpose**: Compare independent audits of curtispark.org to establish ground truth before committing to deliverables

---

## Agreement Matrix

### BOTH VERIFIED (High Confidence — Safe to Promise)

| # | Claim | Agent A | Agent B | Evidence |
|---|-------|---------|---------|----------|
| 1 | Meta description = WordPress theme boilerplate | VERIFIED | VERIFIED | Exact string: "Homepage content is primarily handled through the customize panel. Learn more here: https://wordpress.com/theme/prosperity" |
| 2 | No JSON-LD/schema.org structured data | VERIFIED | VERIFIED | Both: zero `<script type="application/ld+json">` elements |
| 3 | 3 empty heading tags on homepage | VERIFIED | VERIFIED | Both: 2 empty H2 + 1 empty H3 from Jetpack carousel |
| 4 | OG description is weak | VERIFIED | N/A | Content: "RNO and Historic District" — meaningless to outsiders |
| 5 | Sitemap stale | VERIFIED | PARTIALLY | Both found June 2025 dates. Agent B notes this reflects content staleness, not sitemap mechanism |
| 6 | No Google Search Console tag | VERIFIED | N/A | No `<meta name="google-site-verification">` found |
| 7 | ~91% images missing alt text | VERIFIED | VERIFIED | Agent A: 10/11. Agent B: 9/10 content images (excluding tracking pixel). Substantively identical. |
| 8 | Copy/paste error: ADU text on "Maintaining Historic Homes" card | VERIFIED | VERIFIED | Both confirmed character-for-character identical text on wrong card |
| 9 | Resources card image links to /character-defining-features/ instead of /resources/ | VERIFIED | VERIFIED | Both confirmed mismatch between image link and Learn More button |
| 10 | "Maintaining Historic Homes" Learn More is non-functional | VERIFIED | VERIFIED | Both: `<a>` tag without `href`. Visually styled as button but does nothing. |
| 11 | Donation redirects to squareup.com | VERIFIED | VERIFIED | Both: links to `https://squareup.com/store/curtisparkneighbors/` |
| 12 | Mailing lists use Google Groups mailto: links | VERIFIED | VERIFIED | Both: 4 subscription addresses, all `mailto:` |
| 13 | No web-based email signup form | VERIFIED | VERIFIED | Both: no embedded form on any page |
| 14 | "Powered by WordPress.com" in footer | VERIFIED | VERIFIED | Both: present on every page tested |
| 15 | WordPress.com managed hosting (Atomic) | N/A | VERIFIED | `hp=atomic` in tracking pixel, `wpcomsh` plugin, wp.com CDN |
| 16 | No Google Analytics (only Jetpack Stats) | VERIFIED | VERIFIED | Both: only `stats.wp.com` and `pixel.wp.com` |
| 17 | Homepage dominated by Historic Homes section | VERIFIED | VERIFIED | Agent A: 53.1%. Agent B: 49.4%. Both ~50%. |
| 18 | Card layouts inconsistent | VERIFIED | N/A | 5 specific inconsistencies documented by Agent A |
| 19 | Skip to Content link present | VERIFIED | N/A | Functional on all pages tested |

### BOTH REFUTED (Must Remove from Proposal)

| # | Claim | Agent A | Agent B | What's Actually True |
|---|-------|---------|---------|---------------------|
| 20 | Form labels are implicit/not explicit | REFUTED | REFUTED | Both confirmed explicit `<label for="">` associations. Only exception: textarea label shows "(required)" without descriptive name. |
| 21 | Events page uses hardcoded HTML | REFUTED | REFUTED | Both found embedded Google Calendar iframe. Site has been updated since original analysis. |

### BOTH PARTIALLY VERIFIED (Needs Careful Framing)

| # | Claim | Agent A | Agent B | Nuance |
|---|-------|---------|---------|--------|
| 22 | Green/tan color contrast fails WCAG AA | PARTIALLY | PARTIALLY | CSS source has `#10a510` green but it's overridden by Customizer. Actual rendered colors are blue/navy on white. Buttons appear to PASS WCAG AA at ~5:1 ratio. The specific color claim is outdated. |
| 23 | No CAPTCHA on contact form | PARTIALLY | PARTIALLY | Both: No visible CAPTCHA. Both: Akismet honeypot IS present. Should say "no user-facing CAPTCHA" not "no spam protection." |

### ONE REFUTED, ONE NOT CHECKED (Must Correct)

| # | Claim | Agent A | Agent B | Resolution |
|---|-------|---------|---------|------------|
| 24 | Contact form lacks message body (only 3 fields) | REFUTED | REFUTED | Both found 4 fields including textarea. Label shows only "(required)" — the field EXISTS but is poorly labeled. This is a UX issue, not a missing-field issue. |

---

## CORRECTED GROUND TRUTH

### What We Can Honestly Claim as Problems:

**SEO (All verified):**
- Meta description is theme boilerplate (search results show WordPress setup instructions)
- No structured data / schema markup
- 3 empty heading tags (Jetpack carousel artifacts)
- Weak OG description ("RNO and Historic District")
- No Google Analytics or Search Console
- Stale sitemap

**Accessibility (Verified with correction):**
- 91% of images missing alt text
- Contact form textarea has empty label (shows only "(required)")
- ~~Color contrast fails~~ → CORRECTED: Current rendered colors appear to pass WCAG AA. Need fresh assessment.

**Content Bugs (All verified):**
- Copy/paste error: "Maintaining Historic Homes" shows ADU text
- Broken image link: Resources card image → wrong page
- Non-functional Learn More button on Maintaining Historic Homes card
- Inconsistent card layouts (5 specific inconsistencies)

**Events System (CORRECTED):**
- ~~Hardcoded HTML events~~ → CORRECTED: Now uses Google Calendar iframe
- Still valid: No WordPress-native event management, sidebar may still be manual
- No iCal feed from curtispark.org directly

**Donation Flow (Verified):**
- Entire donation process redirects off-site to squareup.com
- No on-site payment form, no donation analytics

**Mailing Lists (Verified):**
- All 4 lists use Google Groups mailto: subscription only
- No web-based signup form anywhere on the site

**Contact Form (CORRECTED):**
- ~~Only 3 fields, no message body~~ → CORRECTED: Has 4 fields including textarea
- Still valid: Textarea label is empty (poor UX)
- No visible CAPTCHA (has Akismet honeypot but no user-facing challenge)

**Design/UX (Verified):**
- "Powered by WordPress.com" visible in footer on every page
- Homepage: Historic Homes section = ~50% of total page height
- No Google Analytics for understanding visitor behavior

---

## IMPLEMENTATION PLANS (Per Verified Deliverable)

### CRITICAL PLATFORM CONSTRAINT

Both agents confirmed: site runs on WordPress.com managed hosting (Atomic tier). This means:
- Cannot install arbitrary plugins (only WP.com approved)
- No direct PHP/server access
- Limited theme customization
- Several deliverables REQUIRE either a plan upgrade or platform migration

**Plan upgrade options:**
- Business ($25/mo): Plugins, custom themes, remove WP.com branding
- eCommerce ($45/mo): + WooCommerce, payment processing
- Migration to self-hosted WordPress.org (~$5-15/mo hosting): Full control

**This platform decision must be discussed with CPN before committing to scope.**

---

### Plan 1: Fix Meta Description
- **How**: WordPress admin → Appearance → Customize → Site Identity, or install Yoast SEO (requires Business plan)
- **Difficulty**: Easy (if Customizer supports it), Medium (if need plugin)
- **Platform constraint**: May be doable in Customizer on current plan. If not, need Yoast → Business plan.
- **Hangups**: Need CPN to approve the description text. Must also fix OG description.
- **Verification**: View page source → check `<meta name="description">` content. Share Google search preview via Google Search Console.
- **Time estimate**: 15 minutes once text is approved

### Plan 2: Add Schema Markup (JSON-LD)
- **How**: Install Yoast SEO (auto-generates Organization, WebSite, BreadcrumbList schema) or manually add via Custom HTML widget/Code Snippets plugin
- **Difficulty**: Medium
- **Platform constraint**: REQUIRES Business plan for Yoast or code injection. Cannot be done on current plan.
- **Hangups**:
  - Plan upgrade required ($25/mo cost discussion with CPN)
  - Event schema would need manual setup since events are in Google Calendar, not WordPress
  - Yoast auto-schema may not cover all desired types
- **Verification**: Google Rich Results Test (https://search.google.com/test/rich-results)
- **Time estimate**: 1-2 hours

### Plan 3: Fix Empty Heading Tags
- **How**: These come from Jetpack carousel plugin. Options:
  a) Disable Jetpack carousel if not actively used
  b) Custom CSS to hide the empty headings (cosmetic, not structural fix)
  c) Report to WP.com support as a Jetpack bug
- **Difficulty**: Easy (disable carousel) to Unknown (if carousel is needed)
- **Platform constraint**: Jetpack is core to WP.com — some modules may not be individually disableable
- **Hangups**:
  - Need to confirm carousel is not actively used on the site
  - If it IS used, removing it may break existing image galleries
  - WP.com support may or may not prioritize fixing empty heading output
- **Verification**: View source, search for empty `<h2>` and `<h3>` tags
- **Time estimate**: 30 minutes (if carousel unused), Unknown (if carousel needed)

### Plan 4: Add Alt Text to All Images
- **How**: WordPress admin → Media Library → Edit each image → Fill in alt text field. Then re-save pages that use those images.
- **Difficulty**: Easy
- **Platform constraint**: None — available on all WP.com plans
- **Hangups**:
  - Need descriptive, context-appropriate text for each of 10 images
  - Some images may be background images set via CSS, which can't have alt text (need ARIA labels instead)
  - WordPress tracking pixel should have empty alt (it's decorative)
- **Verification**: View source → check all `<img>` elements. Run axe accessibility tool. Test with screen reader.
- **Time estimate**: 30-45 minutes

### Plan 5: Fix Content Bugs (3 items)
- **5a: Fix copy/paste error** — Edit "Maintaining Historic Homes" card, replace ADU text with appropriate content about home maintenance resources
- **5b: Fix broken image link** — Edit Resources card, change image link from /character-defining-features/ to /resources/
- **5c: Fix non-functional button** — Add href to Learn More `<a>` tag on Maintaining Historic Homes card
- **Difficulty**: Easy (all three)
- **Platform constraint**: None — basic WordPress block editor
- **Hangups**:
  - Need to write new description for "Maintaining Historic Homes" (CPN may want to review)
  - Need to determine correct destination URL for the Learn More button
- **Verification**: Visual inspection + click testing of all cards
- **Time estimate**: 20 minutes (+ content review time with CPN)

### Plan 6: On-Site Donation Processing
- **How**: Options:
  a) **Square Web Payments SDK embed** — Embed Square's payment form directly on /donate/ page
  b) **Stripe + WooCommerce** — WP.com eCommerce plan, WooCommerce Payments
  c) **GiveWP plugin** — Dedicated WordPress donation plugin (Business plan)
  d) **Square Online Checkout embed** — Square offers embeddable checkout links that stay in an iframe
- **Difficulty**: HIGH
- **Platform constraint**: MAJOR
  - Options a/c require Business plan minimum
  - Option b requires eCommerce plan ($45/mo)
  - All options that keep payments on-site require plan upgrade
  - Alternative: Keep Square but use their embeddable checkout (may still redirect)
- **Hangups**:
  - PCI compliance: Handling payments on-site has security implications
  - CPN's existing Square account and transaction history
  - Cost: New platform/plan costs + potential payment processing fee changes
  - Tax receipt/nonprofit reporting implications
  - Testing: Need live payment testing before launch
  - RISK: Square's embed options may still pop out to a new window/tab, not truly "on-site"
- **Verification**: Complete a test donation without leaving curtispark.org
- **Time estimate**: 4-8 hours (depends on approach chosen)
- **RECOMMENDATION**: Discuss with CPN whether the off-site redirect is actually a problem they care about. If Square works and donations are coming in, this may not be worth the complexity.

### Plan 7: Modern Mailing List Signup
- **How**:
  a) Create Mailchimp free account (up to 500 contacts)
  b) Design embedded signup form for each list
  c) Embed via WP.com's Mailchimp block (available on all plans)
  d) Migrate existing Google Groups subscribers (if possible)
- **Difficulty**: Medium
- **Platform constraint**: LOW — WP.com has native Mailchimp embed support
- **Hangups**:
  - Google Groups subscriber lists may not be exportable (need admin access)
  - CPN may want to keep Google Groups for internal discussion AND have Mailchimp for announcements
  - Ongoing cost: Mailchimp free tier has sending limits
  - Need CPN to decide on email platform preference
  - Open rate tracking requires proper SPF/DKIM DNS setup
- **Verification**: Submit email via signup form, receive confirmation email, verify subscriber appears in platform
- **Time estimate**: 2-4 hours (setup + migration planning)

### Plan 8: Google Analytics & Search Console
- **How**:
  a) GA4: Create property in Google Analytics, add tracking code
  b) Search Console: Verify via DNS TXT record (doesn't require site code changes)
  c) On WP.com: Use Jetpack's Google Analytics integration (Premium+ plan) or install Site Kit (Business plan)
- **Difficulty**: Easy-Medium
- **Platform constraint**: GA via Jetpack needs Premium plan. Site Kit needs Business plan. Search Console can be done via DNS on any plan.
- **Hangups**:
  - GA setup requires Google account with CPN admin access
  - Jetpack GA integration is limited compared to full GA4
  - Privacy policy may need updating to disclose analytics tracking
  - GDPR considerations if any EU visitors (cookie consent)
- **Verification**: Google Analytics real-time report shows live visitors. Search Console shows verification success.
- **Time estimate**: 1-2 hours

### Plan 9: Remove "Powered by WordPress.com"
- **How**:
  a) WP.com Business plan: Customize footer via Customizer or Custom CSS
  b) Migration off WP.com: Branding removed automatically
- **Difficulty**: Easy (once platform constraint resolved)
- **Platform constraint**: CANNOT be done on current plan. Requires Business ($25/mo) minimum.
- **Hangups**: This is a cosmetic issue tied to the larger platform decision
- **Verification**: Check footer on all pages
- **Time estimate**: 5 minutes (once on Business plan)

### Plan 10: Shorter, Focused Homepage
- **How**:
  a) Create dedicated "Historic Home Alterations" landing page
  b) Move all 7 card blocks to that page
  c) Replace with single summary card + link on homepage
  d) Restructure homepage to prioritize: upcoming events, donate CTA, newsletter signup, quick links
- **Difficulty**: Medium
- **Platform constraint**: None — content restructuring in block editor
- **Hangups**:
  - CPN may feel strongly about historic homes content being on homepage
  - Need to ensure SEO isn't lost by moving content to a subpage
  - Internal links pointing to homepage sections need updating
  - Need CPN input on homepage priority order
- **Verification**: Measure page height. Historic Homes should be <15% of homepage. All content accessible via subpage.
- **Time estimate**: 2-3 hours

### Plan 11: Consistent Card Layouts
- **How**: Standardize all cards in Historic Homes section:
  - All images should be links (or none should be)
  - All cards should have functional Learn More buttons
  - Remove duplicate inline "Learn More" text from ADU card
  - Consistent image sizes and aspect ratios
- **Difficulty**: Easy-Medium
- **Platform constraint**: None — block editor
- **Hangups**: WordPress block editor may limit layout consistency depending on block types used
- **Verification**: Visual audit of all cards for consistent structure
- **Time estimate**: 1-2 hours

### Plan 12: Image Optimization (WebP)
- **How**: WordPress.com CDN (Jetpack Photon / i0.wp.com) MAY already serve WebP automatically
- **Difficulty**: Possibly zero (if already happening)
- **Platform constraint**: Need to verify if WP.com CDN already handles WebP conversion
- **Hangups**:
  - If WP.com already serves WebP, this deliverable is a non-issue
  - If not, WP.com doesn't allow image optimization plugins on basic plans
  - Could manually convert and re-upload, but WP.com may reprocess
- **RISK**: We may be promising something that's already done. Need to verify before including in proposal.
- **Verification**: Open Network tab, check image Content-Type headers
- **Time estimate**: 15 minutes to verify, 0-2 hours to implement

### Plan 13: Volunteer Opportunities Board
- **How**:
  a) Simple: Create a page with WordPress blocks (list, columns, buttons) for volunteer listings
  b) Medium: Use a WordPress form plugin for volunteer signup
  c) Advanced: Embed SignUpGenius or similar tool
- **Difficulty**: Easy (simple page) to Medium (interactive)
- **Platform constraint**: Simple page = any plan. Form integration may need Business plan.
- **Hangups**:
  - Who manages/updates the volunteer listings? CPN needs ongoing process.
  - Need content from CPN about current volunteer opportunities
  - If interactive signup, needs form processing capability
- **Verification**: Page exists with volunteer listings and signup mechanism
- **Time estimate**: 1-3 hours

### Plan 14: Curtis Park Times Upload & Distribution
- **How**:
  a) Create "Curtis Park Times" archive page
  b) Upload PDFs to WordPress Media Library
  c) List with download links, organized by date
  d) Optional: embed PDF viewer for in-browser reading
- **Difficulty**: Easy
- **Platform constraint**: Low — WP.com supports file uploads on all plans (with storage limits by plan tier)
- **Hangups**:
  - File size limits: WP.com Personal = 6GB total, Business = 50GB
  - PDF SEO: PDFs don't get indexed as well as HTML content
  - Historical archives: How many back issues need to be uploaded?
  - "Distribute everywhere": If this means auto-posting to social/email, that's a separate integration
- **Verification**: Upload a PDF, access it from the archive page
- **Time estimate**: 1-2 hours (page setup) + ongoing upload time

### Plan 15: Self-Service Content Editing (Training)
- **How**:
  a) Create documentation/guide for CPN team
  b) Hands-on training session (in person or video call)
  c) Cover: editing pages, posting events, uploading files, managing images
- **Difficulty**: Easy (it's training, not development)
- **Platform constraint**: None — WordPress already supports this
- **Hangups**:
  - CPN volunteers' technical comfort level
  - Staff turnover: need documentation that outlives the trained person
  - WordPress block editor has a learning curve
  - Need to identify who on CPN team will be trained
- **Verification**: CPN team member makes a content edit independently
- **Time estimate**: 2-3 hours (guide creation + training session)

### Plan 16: Contact Form Improvements
- **How**:
  a) Add proper label to textarea ("Message" or "How can we help?")
  b) Optionally: Add CAPTCHA (if Akismet honeypot isn't sufficient)
- **Difficulty**: Easy
- **Platform constraint**: Jetpack Forms should allow label customization
- **Hangups**: Minimal. Jetpack block editor for forms should support label editing.
- **Verification**: Check form displays proper labels. Test submission works.
- **Time estimate**: 15 minutes

---

## PLATFORM DECISION MATRIX

Several deliverables depend on WordPress.com plan tier:

| Deliverable | Free/Personal | Premium | Business ($25/mo) | eCommerce ($45/mo) |
|---|---|---|---|---|
| Fix meta description | Maybe | Maybe | ✅ (Yoast) | ✅ |
| Schema markup | ❌ | ❌ | ✅ (Yoast) | ✅ |
| Google Analytics | ❌ | ✅ (Jetpack) | ✅ (Site Kit) | ✅ |
| Remove WP.com branding | ❌ | ❌ | ✅ | ✅ |
| On-site donations | ❌ | ❌ | Partial (GiveWP) | ✅ (WooCommerce) |
| Custom code/plugins | ❌ | ❌ | ✅ | ✅ |

**Recommendation**: At minimum, CPN needs a Business plan ($25/mo = $300/yr) to unlock most deliverables. If on-site donations are important, eCommerce plan ($45/mo = $540/yr).

**Alternative**: Migrate to self-hosted WordPress.org ($5-15/mo hosting) for full control with lower ongoing costs.

---

## ITEMS TO REMOVE FROM PROPOSAL

1. ~~"Event calendar — now self-service"~~ — Events page ALREADY uses Google Calendar iframe. This is done.
2. ~~"Contact form with spam protection"~~ — Already has Akismet honeypot. Already has message field. Only issue is empty label.
3. ~~"91% accessibility score"~~ — Reframe: "91% of images missing alt text" (not an overall score)
4. ~~"Color contrast fails WCAG AA"~~ — Current rendered colors appear to pass. Need fresh assessment before claiming.
5. ~~"No message body on contact form"~~ — Field exists, just poorly labeled.

## ITEMS TO ADD OR REFRAME

1. ADD: Platform decision discussion (WP.com plan upgrade vs. migration)
2. ADD: Ongoing hosting cost implications
3. REFRAME: "Events" → "Events system is functional via Google Calendar but sidebar may need updating"
4. REFRAME: "Contact form" → "Contact form textarea needs proper label"
5. ADD: WebP verification (may already be handled by WP.com CDN)
