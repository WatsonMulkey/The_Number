---
name: qa
description: Run a standardized QA audit on a project. Generates a structured report covering functionality, accessibility, performance, and cross-browser testing.
---

# QA Audit

Run a comprehensive QA audit on a project and generate a structured report.

## Instructions

### 1. Detect Project

Determine which project to audit based on context or user input:
- **Foil Engineering**: `foil-industries-v2/`
- **The Number**: `frontend/` or root `Dev/`
- **Resume Tailor**: `resume-tailor/`

### 2. Functional Testing

Test core user flows for the project:

**Foil Engineering:**
- [ ] Homepage loads without errors
- [ ] All navigation links scroll to correct sections
- [ ] Accordion cards expand/collapse correctly
- [ ] Contact form (if present) validates and submits
- [ ] All images load (check for 404s in network tab)
- [ ] External links open in new tabs
- [ ] Blog posts render correctly

**The Number:**
- [ ] Login/signup flow works
- [ ] Dashboard loads with budget number
- [ ] Add/edit/delete expense works
- [ ] Record transaction works
- [ ] Pool feature: accept/decline/toggle/add
- [ ] Onboarding flow (new user)
- [ ] Logout clears state and badge
- [ ] PWA install prompt appears on mobile

**Resume Tailor:**
- [ ] CLI: `--job` flag reads file correctly
- [ ] CLI: `--trace` generates provenance document
- [ ] CLI: `--no-trace` disables tracing
- [ ] GUI: Job description input works
- [ ] GUI: Progress bar shows during generation
- [ ] GUI: Generated files appear in output directory

### 3. Accessibility Audit

Check against WCAG 2.1 AA standards:

- [ ] All images have alt text
- [ ] Color contrast meets 4.5:1 minimum (text) and 3:1 (large text/UI)
- [ ] Keyboard navigation works for all interactive elements
- [ ] Focus indicators are visible (3px solid outline)
- [ ] Skip-to-content link works
- [ ] Form inputs have associated labels
- [ ] Error messages are announced to screen readers (`aria-live`)
- [ ] No content is conveyed by color alone
- [ ] Touch targets are at least 44x44px on mobile

### 4. Responsive Testing

Test at these breakpoints:
- **Mobile**: 375px (iPhone SE)
- **Tablet**: 768px (iPad)
- **Desktop**: 1440px
- **Wide**: 1920px

Check:
- [ ] Layout doesn't break at any breakpoint
- [ ] Text is readable without horizontal scrolling
- [ ] Navigation adapts (bottom nav on mobile, side rail on desktop for The Number)
- [ ] Images scale appropriately
- [ ] Touch targets are adequately sized on mobile

### 5. Performance Check

- [ ] Lighthouse score > 90 (Performance)
- [ ] Lighthouse score > 90 (Accessibility)
- [ ] No console errors on page load
- [ ] Images are optimized (WebP where possible, lazy loaded)
- [ ] No unnecessary network requests
- [ ] Bundle size within acceptable limits

### 6. Security Check

- [ ] Security headers present (HSTS, X-XSS-Protection, Referrer-Policy)
- [ ] No sensitive data in console logs
- [ ] No API keys or tokens in source code
- [ ] Forms have CSRF protection (if applicable)
- [ ] Auth tokens stored securely (httpOnly cookies or secure localStorage)

### 7. Generate Report

Output a structured markdown report:

```markdown
# QA Report: [Project Name]
**Date**: [YYYY-MM-DD]
**Environment**: [Production / Staging / Local]
**Tester**: Claude Code

## Summary
- **Total Checks**: [N]
- **Passed**: [N]
- **Failed**: [N]
- **Warnings**: [N]

## Critical Issues
[List any blocking issues]

## Warnings
[List non-blocking concerns]

## Functional Testing
[Checklist results]

## Accessibility
[Checklist results]

## Responsive
[Checklist results]

## Performance
[Lighthouse scores and notes]

## Security
[Checklist results]

## Recommendations
[Prioritized list of improvements]
```

Save the report to `QA_REPORT_{PROJECT}_{DATE}.md` in the project root.

## When to Use

- Before deployments (run /qa then /deploy)
- After significant feature additions
- Periodic audits (monthly recommended)
- After dependency updates
- When users report issues
