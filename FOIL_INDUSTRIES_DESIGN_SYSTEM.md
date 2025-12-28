# FOIL Industries Design System Rules
**For Figma Integration via Model Context Protocol**

Last Updated: December 2025
Codebase: FOIL Industries v2 (Astro) + The Number Brand Guidelines

---

## Table of Contents
1. [Project Overview](#project-overview)
2. [Design Tokens](#design-tokens)
3. [Typography System](#typography-system)
4. [Color System](#color-system)
5. [Spacing & Layout](#spacing--layout)
6. [Component Library](#component-library)
7. [Frameworks & Architecture](#frameworks--architecture)
8. [Asset Management](#asset-management)
9. [Icon System](#icon-system)
10. [Styling Approach](#styling-approach)
11. [Responsive Design](#responsive-design)
12. [Brand Relationships](#brand-relationships)
13. [Accessibility Standards](#accessibility-standards)
14. [Implementation Patterns](#implementation-patterns)

---

## Project Overview

### Dual Brand System

FOIL Industries operates two distinct but related brands:

1. **FOIL Industries** (Parent Brand)
   - Industrial, sophisticated, dark aesthetic
   - Photographic grain textures and tinfoil backgrounds
   - Slate blue and mustard accent colors
   - Space Grotesk typography
   - Target: Professional tools, B2B, maker community

2. **The Number** (Product Brand)
   - Light, calm, approachable aesthetic
   - Sage green and warm white palette
   - Scope One serif + Inter sans-serif typography
   - Target: Consumer budgeting app, personal finance

**Relationship**: "If FOIL Industries is a master craftsman's workshop, The Number is the one perfect tool from that workshop."

---

## Design Tokens

### FOIL Industries Tokens (Primary)

Located in: `foil-industries-v2/src/styles/global.css`

#### Color Tokens

```css
/* Primary Blues (FOIL Heritage) */
--color-slate-blue: #4a5f7a;        /* Primary interactive elements */
--color-steel-blue: #5b7d99;        /* Lighter variant */
--color-dusty-blue: #6b8ea8;        /* Lightest variant */

/* Background Hierarchy */
--color-deep-charcoal: #1a1d21;     /* Darkest background */
--color-charcoal: #2b2e33;          /* Primary background */
--color-dark-grey: #35383d;         /* Secondary surface */
--color-surface-grey: #3f4247;      /* Elevated surface */

/* Text Colors */
--color-off-white: #f5f5f5;         /* Primary text */
--color-light-grey: #d1d1d1;        /* Secondary text */
--color-medium-grey: #9a9a9a;       /* Tertiary text */
--color-cool-grey: #7a7d82;         /* Metadata, disabled */

/* Accent Colors (FOIL Signature) */
--color-mustard: #d4a017;           /* Primary accent, CTAs, highlights */
--color-gold: #c9a961;              /* Hover states, warmth */
--color-ochre: #cc8800;             /* Darker mustard variant */

/* Warmth & Support */
--color-terracotta: #c96a5a;        /* Warmth, badges, alerts */
--color-terracotta-light: #d48577;  /* Lighter warmth */

/* Card System (Light Cards on Dark Backgrounds) */
--color-card-light: #f5f5f5;        /* Light card backgrounds */
--color-card-dark-text: #2b2e33;    /* Text on light cards */
```

#### Spacing Tokens (8px Grid)

```css
--spacing-2xs: 4px;    /* Micro spacing */
--spacing-xs: 8px;     /* Element spacing */
--spacing-sm: 16px;    /* Component padding */
--spacing-md: 24px;    /* Section spacing */
--spacing-lg: 36px;    /* Major section breaks */
--spacing-xl: 54px;    /* Page-level separation */
--spacing-2xl: 75px;   /* Large section padding */
--spacing-3xl: 110px;  /* Extra large sections */
--spacing-4xl: 140px;  /* Hero sections */
```

#### Transition Tokens

```css
--transition-fast: 150ms;
--transition-base: 250ms;
--transition-slow: 370ms;
--transition-spring: cubic-bezier(0.34, 1.56, 0.64, 1);  /* Bouncy easing */
```

### The Number Tokens (Product Brand)

Source: `docs/THE_NUMBER_BRAND_GUIDELINES.md`

#### Color Tokens

```css
/* Primary Palette */
--tn-sage-green: #E9F5DB;           /* Brand foundation, success states */
--tn-warm-white: #FAFAF8;           /* Primary background (80% of screen) */
--tn-charcoal: #2B2E33;             /* Primary text, headers */

/* FOIL Accent Colors (Inherited) */
--tn-slate-blue: #4A5F7A;           /* Secondary CTAs, interactive elements */
--tn-mustard: #D4A017;              /* Achievement, attention, highlighted numbers */
--tn-terracotta: #C96A5A;           /* Gentle errors, warmth, alerts */

/* Functional Colors */
--tn-success-green: #7CAF5C;        /* Confirmations, positive feedback */
--tn-soft-gray: #D4D8DC;            /* Disabled states, placeholders */
```

**Color Usage Ratios (Mobile Screen)**:
- Warm White: 70% (breathing room)
- Sage Green: 15% (strategic highlighting)
- Charcoal: 10% (text, navigation)
- FOIL Accents: 5% (surgical precision)

#### Typography Tokens

```css
/* The Number Typography */
--tn-font-primary: 'Scope One', Georgia, 'Times New Roman', serif;
--tn-font-secondary: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;

/* Type Scale */
--tn-hero-size: 72pt;      /* Mobile, 96pt tablet - "The Number" display */
--tn-h2-size: 28pt;        /* Mobile, 36pt tablet - Section headers */
--tn-h3-size: 16pt;        /* Subheads, CTAs */
--tn-body-size: 16pt;      /* Body text (never smaller on mobile) */
--tn-meta-size: 14pt;      /* Metadata, timestamps */
--tn-amount-size: 20pt;    /* Financial figures minimum */
```

---

## Typography System

### FOIL Industries Typography

**Primary Typeface**: Space Grotesk (Google Fonts)

```css
font-family: 'Space Grotesk', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
```

**Loaded in**: `foil-industries-v2/src/layouts/BaseLayout.astro:50`

```html
<link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;600;700&display=swap" rel="stylesheet" />
```

**Weights Used**:
- 400 (Regular): Body text, descriptions
- 600 (Semi-bold): Subheads, important labels
- 700 (Bold): Headings, CTAs, logo

**Hierarchy** (from `global.css:146-173`):

```css
h1 {
  font-size: clamp(46px, 5.2vw, 80px);
  font-weight: 700;
  letter-spacing: -0.03em;
  line-height: 1.08;
  color: #f5f5f5;
}

h2 {
  font-size: clamp(40px, 4.2vw, 60px);
  font-weight: 700;
  letter-spacing: -0.02em;
  line-height: 1.15;
}

h3 {
  font-size: 30px;
  font-weight: 700;
  letter-spacing: -0.01em;
  line-height: 1.25;
}

p {
  line-height: 1.8;
  color: #d1d1d1;
}
```

**Special Typography Patterns**:

1. **Eyebrow Text** (Section labels):
```css
.section-eyebrow {
  font-size: 12px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 3px;
  color: #c9a961;  /* Gold */
  opacity: 0.9;
}
```

2. **Hero Eyebrow**:
```css
.hero-eyebrow {
  font-size: 13px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 4px;
  color: rgba(201, 169, 97, 0.9);
}
```

### The Number Typography

**Primary**: Scope One (Serif, warmth & trust)
**Secondary**: Inter (Sans-serif, UI clarity)

**Font Loading Strategy**:

```css
/* Priority 1 (Inline Critical CSS) */
@import url('https://fonts.googleapis.com/css2?family=Scope+One&display=swap');
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap');
```

**Fallback Stacks**:
```css
font-family: 'Scope One', Georgia, 'Times New Roman', serif;
font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
```

**Usage Rules**:

| Element | Font | Size | Weight | Usage |
|---------|------|------|--------|-------|
| The Number (Hero) | Scope One | 72pt (mobile) / 96pt (tablet) | 400 | Daily budget display |
| Section Headers | Scope One | 28pt / 36pt | 400 | "Your Expenses", "Recent Transactions" |
| Subheads / CTAs | Inter | 16pt | 600 | Button labels, form labels |
| Body Text | Inter | 16pt | 400 | Explanatory text, settings |
| Metadata | Inter | 14pt | 400 | Timestamps, helper text |
| Financial Amounts | Inter | 20pt+ | 500/600 | Currency amounts |

**Number Formatting**:
- Format: `$1,234.56` (comma separators, always 2 decimals)
- Font: Inter with tabular figures enabled
- Currency symbol: Same size as figures, leading position
- Color: Always Charcoal (never red/green for accessibility)

---

## Color System

### FOIL Industries Color Philosophy

**"Slate & Mustard"** - Industrial sophistication with warm accents

**Primary Applications**:

```css
/* Dark backgrounds with light text */
body {
  background-color: #2b2e33;  /* Charcoal */
  color: #d1d1d1;             /* Light Grey */
}

/* Light cards on dark backgrounds */
.tool-card {
  background-color: #f5f5f5;  /* Card Light */
  color: #2b2e33;             /* Card Dark Text */
}

/* Interactive elements */
.cta-button {
  background-color: #d4a017;  /* Mustard */
  color: #2b2e33;             /* Charcoal */
}

.cta-button:hover {
  background-color: #c9a961;  /* Gold */
}
```

**Layered Background System**:

Three layers create depth and photographic quality:

1. **Tinfoil Texture** (`body::before`):
```css
background-image: url('/images/tinfoil.webp');
opacity: 0.08;
z-index: -2;
```

2. **Dark Gradient + Vignette** (`body::after`):
```css
background:
  /* Vignette (darker at edges) */
  radial-gradient(ellipse at center,
    transparent 0%,
    transparent 30%,
    rgba(0, 0, 0, 0.15) 70%,
    rgba(0, 0, 0, 0.35) 100%
  ),
  /* Base gradient */
  linear-gradient(135deg,
    rgba(43, 46, 51, 0.86) 0%,
    rgba(26, 29, 33, 0.88) 100%
  );
z-index: -1;
```

3. **Photographic Grain** (`html::before`):
```css
background-image: url("data:image/svg+xml,...");  /* Noise filter */
opacity: 0.035;
z-index: 9999;
mix-blend-mode: overlay;
```

**Light Explosion Effect** (Hero section):

```css
main::before {
  /* Positioned bottom-left - photographic lens flare */
  background: radial-gradient(
    ellipse at center,
    rgba(212, 160, 23, 0.65) 0%,      /* Mustard core */
    rgba(201, 169, 97, 0.5) 20%,       /* Gold mid */
    rgba(212, 133, 0, 0.35) 35%,       /* Ochre */
    rgba(74, 95, 122, 0.18) 50%,       /* Slate blue fade */
    transparent 75%
  );
  filter: blur(120px);
  animation: pulse-glow 8s ease-in-out infinite;
}
```

### The Number Color Philosophy

**"Light Touch, Heavy Impact"** - Restrained palette, strategic accents

**Contrast Requirements** (WCAG 2.1 AA):

```
✓ Charcoal on Warm White: 12.6:1 (excellent)
✓ Slate Blue on Warm White: 5.8:1 (good for UI)
✗ Sage Green on Warm White: 1.3:1 (decorative only, never text)
✓ Mustard on Charcoal: 4.9:1 (acceptable for large text)
```

**Color Blind Accessibility**:
- Never rely on Sage Green alone to convey information
- Always pair color with icons, position, or text labels

---

## Spacing & Layout

### 8px Grid System

All spacing uses multiples of 8px for consistency:

```css
/* FOIL Industries Spacing Scale */
4px   → --spacing-2xs  (micro)
8px   → --spacing-xs   (tight element spacing)
16px  → --spacing-sm   (component padding)
24px  → --spacing-md   (section spacing)
36px  → --spacing-lg   (major breaks)
54px  → --spacing-xl   (page separation)
75px  → --spacing-2xl  (large sections)
110px → --spacing-3xl  (extra large)
140px → --spacing-4xl  (hero sections)
```

**Responsive Adjustments**:

```css
@media (max-width: 1023px) {
  --spacing-3xl: 75px;   /* Reduced from 110px */
  --spacing-4xl: 90px;   /* Reduced from 140px */
}

@media (max-width: 767px) {
  --spacing-2xl: 50px;   /* Reduced from 75px */
  --spacing-3xl: 60px;   /* Reduced from 75px */
}
```

### The Number Spacing Scale

```css
/* Spacing Scale (8px base) */
xs: 8px   (tight element spacing)
sm: 16px  (default component padding)
md: 24px  (between sections)
lg: 40px  (major section breaks)
xl: 64px  (page-level separation)
```

### Container System

**FOIL Industries**:

```css
.container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 5%;
}

.section {
  padding: var(--spacing-3xl) 5%;  /* 110px vertical, 5% horizontal */
  position: relative;
}
```

**The Number** (Mobile-First):

```css
.container {
  width: 100%;
  padding: 0 16px;
  max-width: 480px;  /* Center on larger screens */
}
```

---

## Component Library

### FOIL Industries Components

#### 1. Header Component

**Location**: `foil-industries-v2/src/components/Header.astro`

**Structure**:
```html
<header class="site-header">
  <div class="header-container">
    <div class="logo">
      <span class="logo-foil">FOIL</span>
      <span class="logo-industries">Industries</span>
    </div>
  </div>
</header>
```

**Styling**:
```css
.site-header {
  position: fixed;
  top: 0;
  height: 90px;  /* 70px on mobile */
  background-color: rgba(43, 46, 51, 0.92);
  backdrop-filter: blur(16px) saturate(180%);
  border-bottom: 1px solid rgba(74, 95, 122, 0.2);
  z-index: 1000;
}

/* Accent bar at bottom */
.site-header::after {
  height: 2px;
  background: linear-gradient(90deg,
    transparent 0%,
    rgba(74, 95, 122, 0.4) 30%,
    rgba(74, 95, 122, 0.6) 50%,
    rgba(74, 95, 122, 0.4) 70%,
    transparent 100%
  );
}

.logo {
  font-size: 30px;  /* 24px on mobile */
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: -0.015em;
}

.logo-foil {
  color: #d4a017;  /* Mustard */
}

.logo-industries {
  color: #f5f5f5;  /* Off-white */
}
```

#### 2. Sidebar Navigation

**Desktop Only** (hidden < 1024px):

```css
.sidebar-nav {
  position: fixed;
  left: 5%;
  top: 50%;
  transform: translateY(-50%);
  z-index: 100;
}

.sidebar-nav a {
  font-size: 16px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 2px;
  color: rgba(209, 209, 209, 0.7);
}

/* Underline animation */
.sidebar-nav a::after {
  content: '';
  width: 0;
  height: 2px;
  background-color: #d4a017;  /* Mustard */
  transition: width 250ms ease;
}

.sidebar-nav a:hover::after,
.sidebar-nav a.active::after {
  width: 70%;
}
```

**Active State Logic**:
```javascript
// Scroll-based active state (Header.astro:162-189)
function updateActiveNav() {
  const scrollY = window.scrollY + 100;
  sections.forEach((section) => {
    if (scrollY >= sectionTop && scrollY < sectionTop + sectionHeight) {
      navLinks.forEach((link) => {
        link.classList.remove('active');
        if (link.getAttribute('href') === `#${sectionId}`) {
          link.classList.add('active');
        }
      });
    }
  });
}
```

#### 3. Tool Cards (Solutions Grid)

**Pattern**: Light cards on dark background with gradient accent

```css
.tool-card {
  background-color: #f5f5f5;  /* Card light */
  padding: 36px 24px;
  border-radius: 12px;
  border: 1px solid rgba(74, 95, 122, 0.12);
  box-shadow: 0 12px 35px rgba(0, 0, 0, 0.4);
  transition: all 370ms cubic-bezier(0.34, 1.56, 0.64, 1);
}

/* Top gradient accent (hidden by default) */
.card-gradient-top {
  position: absolute;
  top: 0;
  height: 4px;
  background: linear-gradient(90deg,
    #4a5f7a 0%,       /* Slate Blue */
    #c96a5a 100%      /* Terracotta */
  );
  transform: scaleX(0);
  transition: transform 370ms ease;
}

.tool-card:hover .card-gradient-top {
  transform: scaleX(1);
}

.tool-card:hover {
  transform: translateY(-9px);
  box-shadow: 0 24px 55px rgba(0, 0, 0, 0.5);
  border-color: #4a5f7a;
}

/* Radial glow on hover */
.tool-card::before {
  background: radial-gradient(circle,
    rgba(74, 95, 122, 0.08) 0%,
    transparent 70%
  );
  opacity: 0;
  transition: opacity 370ms ease;
}

.tool-card:hover::before {
  opacity: 1;
}
```

**Card Structure**:
```html
<article class="tool-card">
  <div class="card-gradient-top"></div>
  <div class="card-header">
    <div>
      <h3 class="card-title">Product Management</h3>
      <p class="card-tagline">Strategy meets execution</p>
    </div>
    <div class="card-number">01</div>
  </div>
  <p class="card-description">...</p>
  <div class="card-footer">
    <a href="#contact" class="card-link">Learn More</a>
  </div>
</article>
```

#### 4. CTA Buttons

**Primary CTA** (Mustard with glow):

```css
.cta-button {
  padding: 26px 68px;  /* 20px 50px on tablet, mobile */
  background-color: #d4a017;  /* Mustard */
  color: #2b2e33;             /* Charcoal */
  font-size: 16px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 1px;
  border-radius: 8px;
  box-shadow:
    0 7px 28px rgba(212, 160, 23, 0.3),
    0 0 30px rgba(212, 160, 23, 0.25);
  transition: all 320ms cubic-bezier(0.34, 1.56, 0.64, 1);
}

/* Halo glow effect */
.cta-button::before {
  content: '';
  position: absolute;
  inset: -3px;
  background: radial-gradient(circle,
    rgba(212, 160, 23, 0.3) 0%,
    transparent 70%
  );
  opacity: 0;
  filter: blur(8px);
  transition: opacity 320ms ease;
}

.cta-button:hover::before {
  opacity: 1;
}

.cta-button:hover {
  background-color: #c9a961;  /* Gold */
  transform: translateY(-3px) scale(1.02);
  box-shadow: 0 14px 45px rgba(212, 160, 23, 0.45);
}
```

**Secondary CTA** (Card links):

```css
.card-link {
  padding: 14px 32px;
  border: 2px solid #4a5f7a;  /* Slate Blue */
  background-color: transparent;
  color: #4a5f7a;
  font-size: 13px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 1px;
  border-radius: 6px;
  transition: all 250ms ease;
}

.card-link:hover {
  background-color: #d4a017;  /* Mustard */
  border-color: #d4a017;
  color: #2b2e33;             /* Charcoal */
  transform: translateX(7px);
  box-shadow: 0 4px 16px rgba(212, 160, 23, 0.3);
}
```

### The Number Components

#### 1. Buttons

**Primary CTA**:
```css
.primary-button {
  background: #2b2e33;      /* Charcoal */
  color: #fafaf8;           /* Warm White */
  padding: 14px 24px;
  border-radius: 8px;
  min-height: 48px;         /* Accessible touch target */
  font: 600 16px 'Inter', sans-serif;
}

.primary-button:hover {
  background: #4a5f7a;      /* Slate Blue */
}

.primary-button:active {
  transform: scale(0.98);
}

.primary-button:disabled {
  background: #d4d8dc;      /* Soft Gray */
  opacity: 0.5;
}
```

**Secondary CTA**:
```css
.secondary-button {
  background: transparent;
  border: 2px solid #4a5f7a;  /* Slate Blue */
  color: #4a5f7a;
  /* Same spacing as primary */
}
```

**Destructive Action**:
```css
.destructive-button {
  background: transparent;
  border: 2px solid #c96a5a;  /* Terracotta */
  color: #c96a5a;
  /* Outline trash icon (never solid) */
}
```

#### 2. Input Fields

```css
.input-field {
  background: #fafaf8;      /* Warm White */
  border: 2px solid #d4d8dc;  /* Soft Gray */
  border-radius: 8px;
  padding: 12px;
  height: 48px;
  font: 400 18px 'Inter', sans-serif;  /* Larger for accuracy */
}

.input-field::placeholder {
  color: rgba(43, 46, 51, 0.4);  /* Charcoal at 40% */
}

.input-field:focus {
  border-color: #4a5f7a;  /* Slate Blue */
  box-shadow: 0 0 0 4px rgba(74, 95, 122, 0.1);  /* Subtle glow */
}

.input-field.error {
  border-color: #c96a5a;  /* Terracotta */
}

.input-field.error + .error-text {
  color: #c96a5a;
  font: 400 14px 'Inter', sans-serif;
  margin-top: 4px;
}
```

#### 3. The Number Display (Hero Element)

```css
.number-display {
  position: relative;
  top: 33.33%;              /* Top third of screen */
  background: #e9f5db;      /* Sage Green */
  padding: 40px 24px;
  border-radius: 16px;
  box-shadow: 0 4px 12px rgba(43, 46, 51, 0.08);
  text-align: center;
}

.number-label {
  font: 400 16px 'Inter', sans-serif;
  color: rgba(43, 46, 51, 0.7);  /* Charcoal at 70% */
}

.number-value {
  font: 400 72px 'Scope One', serif;
  color: #2b2e33;           /* Charcoal */
  line-height: 1.1;
  letter-spacing: -0.02em;
  margin: 8px 0;
}
```

#### 4. Toggle Switches

```css
.toggle {
  width: 48px;
  height: 28px;
  border-radius: 14px;
  transition: all 200ms ease-out;
}

.toggle[aria-checked="false"] {
  background: #d4d8dc;  /* Soft Gray */
}

.toggle[aria-checked="true"] {
  background: #e9f5db;  /* Sage Green */
}

.toggle::before {
  content: '';
  width: 24px;
  height: 24px;
  background: #fafaf8;  /* Warm White */
  border-radius: 50%;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
  transition: transform 200ms ease-out;
}

.toggle[aria-checked="true"]::before {
  transform: translateX(20px);
}
```

#### 5. Cards (Transactions, Settings)

```css
.card {
  background: #fafaf8;      /* Warm White */
  border: 1px solid #e8eae6;  /* Barely visible structure */
  border-radius: 12px;
  padding: 16px;
  box-shadow: none;         /* Flat, content creates depth */
}

.card:hover,
.card:focus-within {
  border-color: #4a5f7a;    /* Slate Blue */
}
```

---

## Frameworks & Architecture

### Tech Stack

**Framework**: Astro 5.16.6
**Type**: Static Site Generator (SSG) with island architecture
**Language**: TypeScript (optional, configured)
**Build System**: Vite (bundled with Astro)

### Project Structure

```
foil-industries-v2/
├── src/
│   ├── components/        # Reusable Astro components
│   │   └── Header.astro   # Fixed header with sidebar nav
│   ├── layouts/           # Page layouts
│   │   └── BaseLayout.astro  # Master layout with SEO
│   ├── pages/             # File-based routing
│   │   └── index.astro    # Homepage (hero, solutions, about, contact)
│   └── styles/            # Global styles
│       └── global.css     # Design tokens + base styles
├── public/                # Static assets
│   ├── images/
│   │   └── tinfoil.webp   # Background texture
│   └── favicon.svg
├── astro.config.mjs       # Astro configuration
├── tsconfig.json          # TypeScript config
└── package.json
```

### Astro Component Pattern

**Component Structure** (`.astro` files):

```astro
---
// Frontmatter (JavaScript/TypeScript)
interface Props {
  title?: string;
  description?: string;
}

const { title = 'Default Title' } = Astro.props;
---

<!-- Template (HTML) -->
<div class="component">
  <h1>{title}</h1>
</div>

<style>
  /* Scoped CSS (default) or global with is:global */
  .component {
    padding: var(--spacing-md);
  }
</style>

<script>
  // Client-side JavaScript (optional)
  document.addEventListener('DOMContentLoaded', () => {
    // Interactive behavior
  });
</script>
```

**Global Styles Import** (BaseLayout.astro:55-57):

```html
<style is:global>
  @import '../styles/global.css';
</style>
```

### Build Configuration

**Astro Config** (`astro.config.mjs`):

```javascript
import { defineConfig } from 'astro/config';

export default defineConfig({});  // Default configuration
```

**Scripts** (`package.json`):

```json
{
  "scripts": {
    "dev": "astro dev",        // Development server (localhost:4321)
    "build": "astro build",    // Production build → dist/
    "preview": "astro preview" // Preview production build
  }
}
```

---

## Asset Management

### Asset Storage

```
public/
├── images/
│   └── tinfoil.webp       # Photographic texture
├── favicon.svg            # Site favicon
└── og-image.png           # Social media preview (inferred)
```

### Asset Optimization

**Images**:
- Format: WebP (modern, efficient compression)
- Background texture: 8% opacity overlay
- Loading: Direct reference from `/public/` directory

**Usage Pattern**:

```css
/* Background images */
body::before {
  background-image: url('/images/tinfoil.webp');
  background-size: cover;
  background-position: center;
  background-attachment: fixed;  /* Parallax effect */
  opacity: 0.08;
}
```

**Inline SVG** (Noise grain):

```css
/* Data URI for small, repeating textures */
html::before {
  background-image: url("data:image/svg+xml,%3Csvg...%3C/svg%3E");
  opacity: 0.035;
  mix-blend-mode: overlay;
}
```

### Font Loading

**Strategy**: Preconnect + display=swap

```html
<link rel="preconnect" href="https://fonts.googleapis.com" />
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
<link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;600;700&display=swap" rel="stylesheet" />
```

**Performance**:
- `display=swap`: Show fallback immediately, swap when loaded
- Preconnect: Reduce DNS/TLS latency
- No FOIT (Flash of Invisible Text)

---

## Icon System

### Current Icons (Minimal)

**FOIL Industries**: No icon system currently implemented
**The Number**: Outlined icons, 24x24px base

**Recommended Library**: Heroicons (outline set) or custom-drawn

### The Number Icon Specifications

```css
.icon {
  width: 24px;
  height: 24px;
  stroke: #2b2e33;        /* Charcoal default */
  stroke-width: 2px;
  fill: none;
  border-radius: 2px;     /* Interior corners */
}

/* Contextual colors */
.icon.expense { stroke: #4a5f7a; }  /* Slate Blue */
.icon.success { stroke: #7caf5c; }  /* Success Green */
.icon.alert   { stroke: #c96a5a; }  /* Terracotta */
```

**Icon Set**:

| Icon | Meaning | Color | Usage |
|------|---------|-------|-------|
| House | Expenses, fixed costs | Slate Blue | Expense category header |
| Dollar Sign | Transactions, money | Charcoal | Transaction list, add button |
| Calendar | Recurring expenses | Charcoal | Recurring expense indicator |
| Pie Chart | Spending insights | Charcoal | Analytics section |
| Shield | Privacy settings | Slate Blue | Privacy messaging |
| User Circle | Account/profile | Charcoal | Account section |
| Plus Circle | Add transaction | Sage Green | Add action (not just "+") |
| Checkmark Circle | Success, goal | Success Green | Confirmations |
| Eye Slash | Privacy, no tracking | Charcoal | Privacy features |

**Usage Rules**:
1. **Never use icons alone** - always pair with text label
2. **8px spacing** between icon and label
3. **Vertical alignment**: Center icon with text cap height

---

## Styling Approach

### CSS Methodology

**Strategy**: Component-scoped CSS with global design tokens

1. **Global Tokens** (`src/styles/global.css`):
   - CSS Custom Properties for design system
   - Reset/base styles
   - Utility classes

2. **Scoped Component Styles** (Astro `<style>` blocks):
   - Default: Scoped to component (Astro magic)
   - Override: `<style is:global>` for global styles

3. **No CSS-in-JS**: Pure CSS/PostCSS (Astro default)

### Global Styles Structure

**Location**: `foil-industries-v2/src/styles/global.css`

**Sections**:
```css
/* 1. CSS Variables (lines 8-58) */
:root { ... }

/* 2. Reset & Base Styles (lines 64-141) */
* { box-sizing: border-box; }
html { ... }
body { ... }

/* 3. Typography (lines 146-183) */
h1, h2, h3, p, a { ... }

/* 4. Accessibility (lines 189-225) */
*:focus-visible { ... }
@media (prefers-reduced-motion) { ... }

/* 5. Utility Classes (lines 231-287) */
.container, .section, .section-header { ... }

/* 6. Responsive Breakpoints (lines 292-308) */
@media (max-width: 1023px) { ... }
@media (max-width: 767px) { ... }
```

### Scoped Component CSS Pattern

**Example** (Header.astro:24-159):

```astro
<header class="site-header">...</header>

<style>
  /* Scoped by default - only affects this component */
  .site-header {
    position: fixed;
    background-color: rgba(43, 46, 51, 0.92);
  }

  /* Pseudo-elements for effects */
  .site-header::after {
    /* Accent bar */
  }

  /* Responsive */
  @media (max-width: 1023px) {
    .site-header {
      height: 70px;
    }
  }
</style>
```

### Animation Patterns

**Micro-interactions** (global.css:54-56):

```css
/* Smooth, purposeful transitions */
--transition-fast: 150ms;    /* Button press */
--transition-base: 250ms;    /* Hover states, color changes */
--transition-slow: 370ms;    /* Complex transforms */
--transition-spring: cubic-bezier(0.34, 1.56, 0.64, 1);  /* Bouncy */
```

**Usage**:

```css
/* Button press */
.button:active {
  transform: scale(0.98);
  transition: transform var(--transition-fast) ease-out;
}

/* Hover lift */
.card:hover {
  transform: translateY(-9px);
  transition: all var(--transition-slow) var(--transition-spring);
}

/* Pulse glow (keyframes) */
@keyframes pulse-glow {
  0%, 100% { opacity: 0.95; transform: scale(1); }
  50% { opacity: 1; transform: scale(1.08); }
}

main::before {
  animation: pulse-glow 8s ease-in-out infinite;
}
```

**The Number Motion**:

```css
/* Button Press */
.button:active {
  transform: scale(0.98);
  transition: 100ms ease-out;
}

/* Screen Transitions */
.page-transition {
  transition: transform 250ms cubic-bezier(0.4, 0, 0.2, 1);
}

/* Number Update */
.number-value {
  transition: opacity 400ms ease-in-out;
}

/* Loading States */
@keyframes skeleton-pulse {
  0%, 100% { opacity: 0.6; }
  50% { opacity: 1; }
}

.skeleton {
  background: #d4d8dc;
  animation: skeleton-pulse 1s ease-in-out infinite;
}
```

**Motion Accessibility**:

```css
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    transition-duration: 0.01ms !important;
  }
}
```

---

## Responsive Design

### Breakpoint System

**FOIL Industries**:

```css
/* Mobile (default): 0-767px */
/* Tablet: 768px-1023px */
@media (max-width: 1023px) { ... }

/* Desktop: 1024px+ */
@media (min-width: 1024px) {
  .sidebar-nav { display: block; }  /* Show sidebar */
}

/* Mobile: 0-767px */
@media (max-width: 767px) { ... }
```

**The Number** (Mobile-First):

```css
/* Mobile (Primary): 375px-767px */
/* Tablet: 768px-1023px */
/* Desktop (Rare): 1024px+ */

/* Design for 375px first (iPhone SE), enhance larger */
```

### Responsive Typography

**Fluid Scaling** (clamp):

```css
h1 {
  font-size: clamp(46px, 5.2vw, 80px);
  /* Min: 46px, Ideal: 5.2vw, Max: 80px */
}

h2 {
  font-size: clamp(40px, 4.2vw, 60px);
}

.hero-subtitle {
  font-size: clamp(19px, 1.9vw, 26px);
}
```

### Touch Target Accessibility

**Minimum Sizes**:
- FOIL Industries: 48px (implicit from button heights)
- The Number: 48px (explicit requirement)

```css
.cta-button {
  min-height: 48px;  /* Accessible touch target */
  padding: 14px 24px;
}

.input-field {
  height: 48px;
}
```

### Responsive Layout Adjustments

**Hero Section**:

```css
/* Desktop */
.hero-section {
  padding: 140px 18% 100px 24%;  /* Asymmetric for sidebar */
  margin-top: 90px;              /* Header height */
}

/* Tablet */
@media (max-width: 1023px) {
  .hero-section {
    padding: 75px 5% 75px;       /* Symmetric */
    margin-top: 70px;            /* Smaller header */
  }
}

/* Mobile */
@media (max-width: 767px) {
  .hero-section {
    padding: 60px 5% 60px;
    min-height: 90vh;            /* Shorter */
  }
}
```

**Card Stacking**:

```css
/* Desktop/Tablet: Vertical stack */
.solutions-grid {
  display: flex;
  flex-direction: column;
  gap: 32px;
}

/* Mobile: Tighter spacing */
@media (max-width: 767px) {
  .tool-card {
    padding: 24px 16px;          /* Reduced from 36px 24px */
  }

  .card-header {
    flex-direction: column;      /* Stack title and number */
  }
}
```

---

## Brand Relationships

### FOIL Industries ↔ The Number Hierarchy

**Analogy**: Apple (parent) ↔ iPhone (product)

### Visibility Guidelines

#### High FOIL Visibility (Credibility Moments)

**Splash Screen** (The Number app):

```html
<div class="splash">
  <div class="the-number-logo">The Number</div>
  <p class="foil-lockup">A FOIL Industries Product</p>
</div>
```

```css
.the-number-logo {
  font: 400 36pt 'Scope One', serif;
  color: #2b2e33;
}

.foil-lockup {
  font: 400 12pt 'Inter', sans-serif;
  color: rgba(43, 46, 51, 0.6);
  margin-top: 12px;
}
```

**About / Settings Page**:

```html
<section class="about">
  <h2>About The Number</h2>
  <p>
    The Number is built by <strong>FOIL Industries</strong>—a company that makes tools
    to help you be better. We believe complex problems deserve simple solutions.
    <a href="https://foilindustries.com">Learn more at foilindustries.com</a>
  </p>
  <img src="/foil-logo-mono.svg" alt="FOIL Industries" width="40" height="40">
</section>
```

#### Low FOIL Visibility (Day-to-Day Use)

- **Main Dashboard**: No FOIL branding
- **Transaction Screens**: Zero FOIL presence
- **Onboarding**: Mention once on welcome screen, then focus on product

### Co-Branding Lockup

**Primary Lockup** (Marketing, splash screen):

```
┌─────────────────────────┐
│   THE NUMBER            │  ← Scope One, 36pt, Charcoal
│   ─────────             │  ← 2px line, Mustard #D4A017, 40px wide
│   A FOIL Industries     │  ← Inter 400, 12pt, Charcoal at 60%
│   Product               │
└─────────────────────────┘

Spacing: 8px between title and line, 4px between line and FOIL text
Alignment: Left-aligned
Background: Warm White or Sage Green (never Charcoal)
```

**Minimal Lockup** (Settings, footers):

```html
<p class="built-by">Built by FOIL Industries</p>
```

```css
.built-by {
  font: 400 12pt 'Inter', sans-serif;
  color: rgba(43, 46, 51, 0.5);
}
```

### Shared Brand Elements

**Allowed** (The Number may use):
- ✓ Charcoal color (#2B2E33)
- ✓ Slate Blue / Mustard / Terracotta accents
- ✓ "A FOIL Industries Product" text lockup
- ✓ Small monochrome FOIL logo in About section

**Restricted** (Permission required):
- ⚠ FOIL tinfoil texture (too industrial for calm budgeting app)
- ⚠ Space Grotesk font (only if Inter can't handle a use case)
- ⚠ "Tools that make you better" tagline (too broad)

**Forbidden**:
- ✗ Full FOIL wordmark replacing "The Number" branding
- ✗ FOIL's slate/mustard as The Number's primary colors
- ✗ Corporate FOIL messaging in user-facing copy

---

## Accessibility Standards

### WCAG 2.1 Level AA Compliance

#### Color Contrast

**Tested Combinations**:

```
FOIL Industries:
✓ Off-white (#f5f5f5) on Charcoal (#2b2e33): 12.6:1 (AAA)
✓ Light Grey (#d1d1d1) on Charcoal: 8.2:1 (AAA)
✓ Mustard (#d4a017) on Charcoal: 4.9:1 (AA Large Text)
✓ Slate Blue (#4a5f7a) on Card Light (#f5f5f5): 5.8:1 (AA)

The Number:
✓ Charcoal (#2b2e33) on Warm White (#fafaf8): 12.6:1 (AAA)
✓ Slate Blue (#4a5f7a) on Warm White: 5.8:1 (AA)
✗ Sage Green (#e9f5db) on Warm White: 1.3:1 (Decorative only)
✓ Mustard (#d4a017) on Charcoal: 4.9:1 (AA Large Text)
```

**Requirements**:
- Body text: 4.5:1 minimum
- Large text (18pt+): 3:1 minimum
- UI components: 3:1 minimum

#### Focus States

**Global Focus Styling** (global.css:189-197):

```css
*:focus-visible {
  outline: 2px solid #d4a017;  /* Mustard (FOIL) or Slate Blue (The Number) */
  outline-offset: 3px;
  border-radius: 4px;
}

*:focus:not(:focus-visible) {
  outline: none;  /* Remove focus for mouse users */
}
```

**The Number Focus**:

```css
*:focus-visible {
  outline: 2px solid #4a5f7a;  /* Slate Blue */
  outline-offset: 2px;
}

/* 3:1 contrast requirement against background */
```

#### Skip to Main Content

**Implementation** (BaseLayout.astro:61, global.css:211-225):

```html
<a href="#main-content" class="skip-to-main">Skip to main content</a>

<main id="main-content">...</main>
```

```css
.skip-to-main {
  position: absolute;
  top: -100px;
  left: 0;
  background: #d4a017;    /* Mustard */
  color: #2b2e33;         /* Charcoal */
  padding: 12px 24px;
  font-weight: 700;
  z-index: 1000;
  transition: top 150ms ease;
}

.skip-to-main:focus {
  top: 0;  /* Slide in when focused */
}
```

#### Semantic HTML

**Structure** (index.astro):

```html
<header>...</header>
<nav aria-label="Main navigation">...</nav>
<main id="main-content">
  <section id="hero">...</section>
  <section id="solutions">...</section>
  <article class="tool-card">...</article>
</main>
<footer>...</footer>
```

**Not** (avoid):
```html
<div class="header">...</div>
<div onclick="">...</div>
```

#### ARIA Labels (The Number)

```html
<!-- The Number Display -->
<div role="region" aria-label="Today's available spending amount">
  <p aria-hidden="true">You have</p>
  <p class="the-number" aria-label="$127.50">$127.50</p>
  <p aria-hidden="true">to spend today</p>
</div>

<!-- Icon Buttons -->
<button aria-label="Add new transaction">
  <svg aria-hidden="true"><!-- plus icon --></svg>
</button>
```

#### Motion Preferences

**Respect User Settings** (global.css:200-208):

```css
@media (prefers-reduced-motion: reduce) {
  *,
  *::before,
  *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}
```

#### Touch Accessibility

**Minimum Touch Targets**: 48x48px

```css
/* Buttons */
.cta-button {
  min-height: 48px;
  padding: 14px 24px;
}

/* Inputs */
.input-field {
  height: 48px;
}

/* Spacing between tappable elements */
.button-group > * + * {
  margin-left: 8px;  /* Minimum spacing */
}
```

**Gestures**:
- No swipe-only interactions (provide button alternative)
- No multi-finger gestures
- No timeout constraints (user controls pace)

#### Screen Reader Testing

**Before Launch**:
- [ ] Test with VoiceOver (iOS/macOS)
- [ ] Test with TalkBack (Android)
- [ ] Test with NVDA (Windows)
- [ ] Navigate entire app using keyboard only (Tab, Enter, Esc)

---

## Implementation Patterns

### File Naming Conventions

```
Components:
  Header.astro (PascalCase)
  TheNumberDisplay.astro
  SolutionCard.astro

Layouts:
  BaseLayout.astro

Styles:
  global.css (lowercase)

Assets:
  the-number-logo-light.svg (kebab-case)
  the-number-logo-dark.svg
  foil-lockup-horizontal.svg
  foil-lockup-stacked.svg
  icon-house-24.svg (size suffix)
  illustration-empty-state-transactions.svg
  tinfoil.webp
```

### Component Creation Pattern

**New Astro Component**:

1. Create file: `src/components/ComponentName.astro`

2. Structure:
```astro
---
// TypeScript interface for props
interface Props {
  title: string;
  description?: string;
  variant?: 'primary' | 'secondary';
}

const {
  title,
  description,
  variant = 'primary'
} = Astro.props;
---

<div class={`component component--${variant}`}>
  <h2>{title}</h2>
  {description && <p>{description}</p>}
  <slot />  <!-- Named slots for flexible content -->
</div>

<style>
  .component {
    padding: var(--spacing-md);
    border-radius: 12px;
  }

  .component--primary {
    background: var(--color-card-light);
  }

  .component--secondary {
    background: var(--color-surface-grey);
  }
</style>
```

3. Import in page:
```astro
---
import ComponentName from '../components/ComponentName.astro';
---

<ComponentName title="Hello" variant="primary">
  <p>Slotted content here</p>
</ComponentName>
```

### Adding Design Tokens

**Process**:

1. Add token to `src/styles/global.css`:
```css
:root {
  /* New token */
  --color-new-accent: #hexcode;
  --spacing-new: 42px;
}
```

2. Use in components:
```css
.element {
  color: var(--color-new-accent);
  padding: var(--spacing-new);
}
```

3. Document in this file (design system rules)

### Responsive Image Pattern

**WebP with Fallback**:

```html
<picture>
  <source srcset="/images/hero.webp" type="image/webp">
  <source srcset="/images/hero.jpg" type="image/jpeg">
  <img src="/images/hero.jpg" alt="Description" loading="lazy">
</picture>
```

**Optimization Checklist**:
- [ ] Convert to WebP format
- [ ] Add `loading="lazy"` for below-fold images
- [ ] Provide alt text (descriptive or empty `alt=""` for decorative)
- [ ] Consider responsive images with `srcset` for different screen sizes

### Animation Implementation

**CSS-only Animations** (Preferred):

```css
/* Keyframes */
@keyframes slide-in {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Usage */
.element {
  animation: slide-in var(--transition-base) ease-out;
}
```

**JavaScript Animations** (When necessary):

```javascript
// In <script> tag of .astro component
const element = document.querySelector('.element');

element.addEventListener('click', () => {
  element.animate([
    { transform: 'scale(1)' },
    { transform: 'scale(0.95)' },
    { transform: 'scale(1)' }
  ], {
    duration: 150,
    easing: 'ease-out'
  });
});
```

### Form Validation Pattern (The Number)

**HTML5 Validation**:

```html
<form class="transaction-form">
  <label for="amount">Amount</label>
  <input
    type="number"
    id="amount"
    name="amount"
    min="0.01"
    step="0.01"
    required
    aria-describedby="amount-error"
  >
  <span id="amount-error" class="error-text" role="alert"></span>

  <button type="submit">Save Transaction</button>
</form>
```

**JavaScript Enhancement**:

```javascript
const form = document.querySelector('.transaction-form');
const amountInput = form.querySelector('#amount');
const errorSpan = form.querySelector('#amount-error');

amountInput.addEventListener('invalid', (e) => {
  e.preventDefault();
  amountInput.classList.add('error');
  errorSpan.textContent = 'Please enter a valid amount';
});

amountInput.addEventListener('input', () => {
  if (amountInput.validity.valid) {
    amountInput.classList.remove('error');
    errorSpan.textContent = '';
  }
});
```

### Loading State Pattern

**Skeleton Screens** (The Number):

```html
<div class="transaction-list">
  {isLoading ? (
    <div class="skeleton-transaction" aria-busy="true" aria-label="Loading transactions">
      <div class="skeleton-line skeleton-line--short"></div>
      <div class="skeleton-line skeleton-line--long"></div>
    </div>
  ) : (
    transactions.map(t => <Transaction data={t} />)
  )}
</div>
```

```css
.skeleton-line {
  height: 16px;
  background: #d4d8dc;  /* Soft Gray */
  border-radius: 4px;
  animation: skeleton-pulse 1s ease-in-out infinite;
}

.skeleton-line--short { width: 40%; }
.skeleton-line--long { width: 80%; }

@keyframes skeleton-pulse {
  0%, 100% { opacity: 0.6; }
  50% { opacity: 1; }
}
```

---

## Quick Reference

### Color Variables Quick Copy

```css
/* FOIL Industries */
--color-slate-blue: #4a5f7a;
--color-charcoal: #2b2e33;
--color-off-white: #f5f5f5;
--color-mustard: #d4a017;
--color-terracotta: #c96a5a;
--color-card-light: #f5f5f5;

/* The Number */
--tn-sage-green: #E9F5DB;
--tn-warm-white: #FAFAF8;
--tn-charcoal: #2B2E33;
--tn-slate-blue: #4A5F7A;
--tn-mustard: #D4A017;
--tn-success-green: #7CAF5C;
```

### Typography Quick Copy

```css
/* FOIL Industries */
font-family: 'Space Grotesk', sans-serif;
h1: clamp(46px, 5.2vw, 80px) / 700 / -0.03em
h2: clamp(40px, 4.2vw, 60px) / 700 / -0.02em
h3: 30px / 700 / -0.01em
body: 16px / 400 / 1.8 line-height

/* The Number */
hero: 'Scope One' 72pt / 400
headers: 'Scope One' 28pt / 400
ui: 'Inter' 16pt / 600
body: 'Inter' 16pt / 400
amounts: 'Inter' 20pt / 500-600
```

### Spacing Quick Copy

```css
/* FOIL: 4, 8, 16, 24, 36, 54, 75, 110, 140 */
--spacing-xs: 8px;
--spacing-sm: 16px;
--spacing-md: 24px;
--spacing-lg: 36px;

/* The Number: 8, 16, 24, 40, 64 */
xs: 8px, sm: 16px, md: 24px, lg: 40px, xl: 64px
```

### Responsive Breakpoints

```css
/* Mobile: 0-767px (default) */
@media (max-width: 767px) { ... }

/* Tablet: 768-1023px */
@media (max-width: 1023px) { ... }

/* Desktop: 1024px+ */
@media (min-width: 1024px) { ... }
```

---

## Using This Guide with Figma MCP

### Workflow for Implementing Figma Designs

1. **Extract Design Tokens from Figma**:
   - Use `get_design_context` to fetch component code
   - Map Figma variables to CSS custom properties in this doc

2. **Match Typography**:
   - Figma text styles → Typography System section
   - FOIL: Space Grotesk only
   - The Number: Scope One (display) + Inter (UI)

3. **Apply Color System**:
   - Figma fill colors → Color Tokens
   - Verify WCAG contrast ratios (Accessibility Standards section)

4. **Implement Components**:
   - Follow Component Library patterns
   - Use Astro component structure
   - Apply scoped CSS with design tokens

5. **Ensure Responsive Behavior**:
   - Use clamp() for fluid typography
   - Apply breakpoint adjustments
   - Test touch targets (48px minimum)

6. **Verify Accessibility**:
   - Check color contrast
   - Add ARIA labels
   - Test keyboard navigation
   - Implement focus states

### Design Token Mapping

**From Figma Variables to CSS**:

```javascript
// Figma variable → CSS custom property
{
  "colors/primary/blue": "--color-slate-blue: #4a5f7a",
  "colors/accent/mustard": "--color-mustard: #d4a017",
  "spacing/md": "--spacing-md: 24px",
  "typography/heading/size": "clamp(46px, 5.2vw, 80px)"
}
```

---

## Version History

**v1.0** — December 26, 2025
- Initial comprehensive design system documentation
- FOIL Industries v2 implementation patterns
- The Number brand guidelines integration
- Component library with code examples
- Accessibility standards and testing checklist

---

## Contact & Governance

**Design System Owner**: Watson Mulkey (FOIL Industries)
**Email**: watson@foil.engineering
**Repository**: `foil-industries-v2/`

**Approval Required For**:
- Changes to core color palette
- Typography substitutions
- New design tokens
- Component pattern modifications
- Brand relationship changes

---

*"Complex problems deserve simple solutions."*
— FOIL Industries
