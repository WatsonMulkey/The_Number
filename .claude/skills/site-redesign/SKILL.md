---
name: site-redesign
description: End-to-end site redesign workflow. Captures an existing website to Figma, analyzes its IA, proposes a redesigned architecture, builds HTML mockups, and captures them to Figma for side-by-side comparison. Repeatable process for client engagements.
---

# Site Redesign Workflow

A repeatable process for analyzing an existing website, proposing a redesigned information architecture, building mockup pages, and delivering everything in Figma for client review.

## Overview

This workflow produces a Figma file containing:
1. **Current site** — every page of the existing website captured as editable Figma layers
2. **Redesign proposal** — a sitemap/overview comparing old vs new IA
3. **Redesign mockups** — HTML mockups of every proposed page, captured to Figma

The client can compare old and new side-by-side in one Figma file.

## Prerequisites

- **Figma MCP** (`mcp__figma`) connected
- **Playwright MCP** (`mcp__playwright`) connected
- **Figma Desktop** open (for viewing)
- `/figma-capture` skill available (handles the capture mechanics)

## Workflow Steps

### Phase 1: Capture the Current Site

Use the `/figma-capture` skill with bulk capture mode.

1. **Create or identify the Figma file** for this client
2. **Discover all pages** on the current site (sitemap.xml, nav links, or manual list)
3. **Bulk capture** all pages into the Figma file using batches of 10-12
4. **Verify** all captures landed

**Output**: Figma file with all current pages as separate Figma pages/frames

### Phase 2: Analyze & Propose New IA

1. **Use the socratic-architect agent** to analyze the current site:
   - Review the sitemap and page structure
   - Identify content overlap and redundancy
   - Assess navigation complexity
   - Identify the top 3 user priorities (what do visitors actually need?)

2. **Propose a new information architecture**:
   - Consolidate redundant pages
   - Establish clear priority pages (highlighted in nav)
   - Define the page hierarchy
   - Map old pages to new pages (what merges, what stays, what's removed)

3. **Create visual sitemaps** for comparison:
   - **FigJam diagram** of current site structure using `mcp__figma__generate_diagram`
   - **FigJam diagram** of proposed redesign using `mcp__figma__generate_diagram`
   - Optionally: HTML comparison page captured to Figma

**Output**: Architect recommendation + visual sitemaps

### Phase 3: Build Redesign Mockups

Build static HTML mockups for every page in the proposed redesign.

#### 3a. Create the Design System

Create a shared `styles.css` with:
- CSS custom properties (colors, fonts, spacing, radii)
- Navigation component (sticky nav with priority buttons)
- Hero section
- Page headers with breadcrumbs
- Card system (grid layouts, hover states)
- Button variants (primary, green, amber, outline)
- Form components
- Footer
- Utility classes

**Design tokens to define**:
```css
:root {
  --color-primary: /* client brand color */;
  --color-accent-blue: /* CTA color */;
  --color-accent-green: /* donate/success */;
  --color-accent-amber: /* newsletter/warning */;
  --max-width: 1200px;
  --radius: 12px;
}
```

#### 3b. Build Each Page

For each page in the proposed IA, create an HTML file that:
- Uses the shared `styles.css`
- Includes the full nav with correct `active` class
- Has realistic content (pulled from the current site where possible)
- Includes the shared footer
- Uses semantic HTML and the component library from the CSS

**Naming convention**: `<page-slug>.html` (e.g., `index.html`, `events.html`, `donate.html`)

**Directory structure**:
```
site-assessor/redesign/
  styles.css
  index.html
  events.html
  donate.html
  newsletter.html
  about.html
  committees.html
  history.html
  ...
```

#### 3c. Serve Locally

Start a local HTTP server to serve the mockups:
```bash
npx -y http-server <parent-directory> -p 8092 --cors
```

Verify pages load:
```bash
curl -s -o /dev/null -w "%{http_code}" http://localhost:8092/redesign/index.html
```

### Phase 4: Capture Mockups to Figma

Use the `/figma-capture` bulk capture workflow:

1. **Generate capture IDs** — one per mockup page, all in parallel:
   ```
   For each page:
     mcp__figma__generate_figma_design(
       outputMode: "existingFile",
       fileKey: "<same-figma-file>"
     )
   ```

2. **Capture each page** sequentially (2 calls per page):
   - Navigate with hash params
   - Inject capture.js

3. **Verify** all captures by polling with captureId

**Output**: All redesign mockups added to the same Figma file as the current site captures

### Phase 5: Deliver & Review

The Figma file now contains:
- Current site pages (Phase 1)
- Redesign mockup pages (Phase 4)
- Sitemaps in FigJam (Phase 2)

Present to the client for review. They can:
- Compare any current page with its redesigned equivalent
- See the IA changes in the sitemap diagrams
- Provide feedback directly in Figma comments

## Timing Guide

| Phase | Pages | Estimated Effort |
|-------|-------|-----------------|
| Phase 1: Capture current site | 10-15 | 1 session |
| Phase 1: Capture current site | 30+ | 2-3 sessions |
| Phase 2: IA analysis | Any | 1 session |
| Phase 3: Build mockups | 10 pages | 1 session |
| Phase 4: Capture mockups | 10 pages | 1 session |

## Proven Results

This workflow was developed and proven with Curtis Park Neighbors (curtispark.org):
- **Current site**: 33 pages captured across 3 sessions
- **Proposed redesign**: 33 pages consolidated to 10
- **Mockup pages**: 10 HTML pages with shared design system
- **Figma delivery**: All 43 layers (33 current + 10 redesign) in one file
- **Figma file**: `SOCa5piffvvpfFsyEwqvH3`

## Key Lessons

1. **Start with capture, not design** — seeing the full current site in Figma reveals redundancy and problems that inform the redesign
2. **Use the architect agent** for IA analysis — it produces structured, evidence-based recommendations
3. **Build a shared CSS first** — one design system file makes all mockup pages consistent
4. **Realistic content matters** — pull actual text from the current site rather than using lorem ipsum
5. **Same Figma file for old + new** — side-by-side comparison is the whole point
6. **Batch captures of 10-12** — stays within context limits while being efficient
7. **Hash params + inject** — the only reliable capture method at scale

## Customization Per Client

When adapting for a new client:

1. **Colors**: Update CSS custom properties to match client brand
2. **Content**: Pull real content from the client's current site
3. **IA priorities**: Every client has different top-3 priorities — don't assume
4. **Nav structure**: The priority buttons (colored nav items) should reflect client needs
5. **Page count**: Not every site needs 10 pages — let the IA analysis drive the count

## Related Skills

- `/figma-capture` — the underlying capture mechanics
- `/qa` — run QA on the mockups before capturing
- `/proposal` — generate a client proposal that includes the redesign deliverable
