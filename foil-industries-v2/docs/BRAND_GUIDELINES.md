# FOIL Industries Brand Guidelines
**Visual Identity System - December 2025**

---

## Primary Visual Direction

**Approved Design:** Slate & Mustard (Earthy Refined)
**Design System:** Sophisticated industrial aesthetic with tinfoil texture background
**File:** `hybrid-2-slate-mustard.html`

---

## Executive Summary

FOIL Industries' visual identity balances **professional sophistication** with **approachable warmth**. The design system uses earthy slate blues as the foundation, neutral greys for hierarchy, and muted mustard/gold accents for energy—all anchored by a subtle metallic tinfoil texture that reinforces the brand name and industrial quality positioning.

### Core Brand Pillars
1. **Trustworthy** - Established through muted blues and professional restraint
2. **Modern** - Conveyed via clean typography and thoughtful interactions
3. **Sophisticated** - Demonstrated by refined color palette and attention to detail

---

## Color System

### Primary Colors (Earthy Blues)

#### Slate Blue
- **Hex:** `#4a5f7a`
- **RGB:** 74, 95, 122
- **Usage:** Primary brand color, borders, UI elements
- **Personality:** Professional, trustworthy, calm
- **Application:** Navigation elements, card hover states, accent bars

#### Steel Blue
- **Hex:** `#5b7d99`
- **RGB:** 91, 125, 153
- **Usage:** Secondary brand color, mid-tone applications
- **Personality:** Approachable, stable, confident

#### Dusty Blue
- **Hex:** `#6b8ea8`
- **RGB:** 107, 142, 168
- **Usage:** Lighter applications, subtle backgrounds
- **Personality:** Soft, sophisticated, refined

---

### Background Colors (Neutral Greys)

#### Deep Charcoal
- **Hex:** `#1a1d21`
- **RGB:** 26, 29, 33
- **Usage:** Darkest backgrounds (footer, deep sections)
- **Personality:** Grounded, substantial, premium

#### Charcoal Grey (Primary Background)
- **Hex:** `#2b2e33`
- **RGB:** 43, 46, 51
- **Usage:** Main page background
- **Personality:** Professional, neutral, sophisticated
- **Overlay Opacity:** 86% over tinfoil texture

#### Dark Grey
- **Hex:** `#35383d`
- **RGB:** 53, 56, 61
- **Usage:** Secondary section backgrounds
- **Personality:** Subtle, refined, organized
- **Overlay Opacity:** 88% over tinfoil texture

#### Surface Grey
- **Hex:** `#3f4247`
- **RGB:** 63, 66, 71
- **Usage:** Elevated surfaces, section variations
- **Personality:** Layered, dimensional, structured

---

### Text Colors (Refined Greys)

#### Off-White (Primary Text)
- **Hex:** `#f5f5f5`
- **RGB:** 245, 245, 245
- **Usage:** Headlines, primary body text on dark backgrounds
- **Contrast:** 12.5:1 on charcoal grey (WCAG AAA)

#### Light Grey (Secondary Text)
- **Hex:** `#d1d1d1`
- **RGB:** 209, 209, 209
- **Usage:** Subheadings, secondary text, body copy
- **Contrast:** 9.2:1 on charcoal grey (WCAG AAA)

#### Medium Grey (Tertiary Text)
- **Hex:** `#9a9a9a`
- **RGB:** 154, 154, 154
- **Usage:** Metadata, captions, less important text
- **Contrast:** 4.8:1 on charcoal grey (WCAG AA)

#### Cool Grey (Subtle Text)
- **Hex:** `#7a7d82`
- **RGB:** 122, 125, 130
- **Usage:** Footer text, very subtle elements
- **Contrast:** 3.2:1 on charcoal grey (WCAG AA for large text)

---

### Accent Colors (Mustard & Gold)

#### Mustard Yellow (Primary Accent)
- **Hex:** `#d4a017`
- **RGB:** 212, 160, 23
- **Usage:** CTAs, logo accent, primary interactive elements
- **Personality:** Warm, energetic, sophisticated
- **Application:** Buttons, active states, emphasis
- **Contrast:** 7.1:1 on charcoal grey (WCAG AAA)

#### Antique Gold (Secondary Accent)
- **Hex:** `#c9a961`
- **RGB:** 201, 169, 97
- **Usage:** Hover states, secondary interactions, eyebrows
- **Personality:** Refined, warm, elegant
- **Application:** Section labels, subtle accents

#### Ochre (Deep Mustard)
- **Hex:** `#cc8800`
- **RGB:** 204, 136, 0
- **Usage:** Card taglines, deeper accent applications
- **Personality:** Grounded, warm, substantial

---

### Warmth & Support Colors (Terracotta Family)

#### Terracotta (Supportive Accent)
- **Hex:** `#c96a5a`
- **RGB:** 201, 106, 90
- **Usage:** Success states, supportive messaging, "In Your Corner" moments
- **Personality:** Warm, approachable, encouraging
- **Application:** Badges, success confirmations, supportive UI elements
- **Contrast:** 4.2:1 on charcoal grey (WCAG AA)
- **Strategic Role:** Addresses brand warmth sentiment; balances cool blues

#### Terracotta Light (Subtle Support)
- **Hex:** `#d48577`
- **RGB:** 212, 133, 119
- **Usage:** Hover states on terracotta, lighter supportive text
- **Personality:** Gentle, reassuring, friendly
- **Application:** Hover states, secondary support messaging

**Usage Guidelines:**
- Use terracotta for **success states** and **positive confirmations** (e.g., "Saved!", "Success!")
- Apply to **"In Your Corner" messaging** that emphasizes support (e.g., badges like "We've got you")
- Use in **gradient accents** with slate blue for card hover states
- **Never use as primary CTA** — mustard remains the main action color
- Reserve for moments that require warmth and encouragement
- Complements, not competes with, mustard/gold accent family

---

### Card/Surface Colors

#### Card Light (On Dark Sections)
- **Hex:** `#f5f5f5`
- **RGB:** 245, 245, 245
- **Usage:** Light-colored cards on dark backgrounds
- **Personality:** Clean, prominent, elevated

#### Card Dark Text
- **Hex:** `#2b2e33`
- **RGB:** 43, 46, 51
- **Usage:** Text on light cards
- **Contrast:** 12.5:1 on card light (WCAG AAA)

---

## Typography System

### Primary Typeface: Space Grotesk

**Rationale:** Modern geometric sans-serif with slightly industrial character. Clean, technical, and sophisticated without being cold.

**Weights Used:**
- Regular (400): Body text, descriptions
- Semi-Bold (600): Subheadings, navigation
- Bold (700): Headlines, CTAs, emphasis

**Fallback Stack:**
```css
font-family: 'Space Grotesk', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
```

---

### Type Scale (Fluid Responsive)

#### Display / Hero Headlines
- **Desktop:** 80px (5.2vw clamped)
- **Mobile:** 46px minimum
- **Weight:** 700 (Bold)
- **Line Height:** 1.08
- **Letter Spacing:** -0.03em (tightened for large sizes)
- **Color:** Off-White (#f5f5f5)
- **Usage:** Hero section headline only

#### Section Titles (H2)
- **Desktop:** 60px (4.2vw clamped)
- **Mobile:** 40px minimum
- **Weight:** 700 (Bold)
- **Line Height:** 1.15
- **Letter Spacing:** -0.02em
- **Color:** Off-White (#f5f5f5)
- **Usage:** Section headings

#### Card Titles (H3)
- **Size:** 30px (fixed)
- **Weight:** 700 (Bold)
- **Line Height:** 1.25
- **Letter Spacing:** -0.01em
- **Color:** Card Dark Text (#2b2e33) on light cards
- **Usage:** Tool cards, article titles

#### Subheadlines / Intro Text
- **Desktop:** 26px (1.9vw clamped)
- **Mobile:** 19px minimum
- **Weight:** 400 (Regular)
- **Line Height:** 1.65
- **Color:** Light Grey (#d1d1d1, 85% opacity)
- **Usage:** Hero subheadline, section descriptions

#### Body Text (Large)
- **Size:** 20px
- **Weight:** 400 (Regular)
- **Line Height:** 1.8
- **Color:** Light Grey (#d1d1d1, 82% opacity)
- **Usage:** About section, contact text

#### Body Text (Standard)
- **Size:** 17-18px
- **Weight:** 400 (Regular)
- **Line Height:** 1.8
- **Color:** Medium Grey (#9a9a9a) or Card Dark Text (on cards)
- **Usage:** Card descriptions, general body copy

#### Small Text / Metadata
- **Size:** 14-16px
- **Weight:** 400-600 (Regular to Semi-Bold)
- **Line Height:** 1.5
- **Color:** Medium Grey (#9a9a9a) or Cool Grey (#7a7d82)
- **Usage:** Footer text, metadata, timestamps

#### Eyebrows / Labels
- **Size:** 12-13px
- **Weight:** 700 (Bold)
- **Text Transform:** UPPERCASE
- **Letter Spacing:** 3-4px (wide tracking)
- **Color:** Antique Gold (#c9a961)
- **Usage:** Section labels ("FOIL INDUSTRIES", "WHAT WE BUILD")

#### Navigation Links
- **Size:** 16px
- **Weight:** 600 (Semi-Bold)
- **Text Transform:** UPPERCASE
- **Letter Spacing:** 2px
- **Color:** Light Grey (#d1d1d1, 70% opacity default)
- **Active/Hover:** Mustard Yellow (#d4a017, 100% opacity)
- **Usage:** Vertical sidebar navigation

#### Button / CTA Text
- **Size:** 16-18px
- **Weight:** 700 (Bold)
- **Text Transform:** UPPERCASE
- **Letter Spacing:** 1px
- **Color:** Charcoal Grey (#2b2e33) on mustard background
- **Usage:** Primary CTAs, card links

---

## Background & Texture System

### Tinfoil Texture Background

**Image:** `tinfoil.webp`
**Opacity:** 8%
**Position:** Fixed (parallax effect)
**Size:** Cover
**Purpose:** Reinforces "FOIL" brand name, adds subtle industrial texture

**Implementation:**
```css
body::before {
    content: '';
    position: fixed;
    background-image: url('tinfoil.webp');
    background-size: cover;
    background-position: center;
    background-attachment: fixed;
    opacity: 0.08;
    z-index: -2;
}
```

### Dark Overlay Gradient

**Purpose:** Creates readable surface over tinfoil texture while maintaining subtle visibility

**Gradient:**
- **Top:** `rgba(43, 46, 51, 0.86)` - Charcoal Grey at 86% opacity
- **Bottom:** `rgba(26, 29, 33, 0.88)` - Deep Charcoal at 88% opacity
- **Direction:** 135deg (diagonal)

**Implementation:**
```css
body::after {
    content: '';
    position: fixed;
    background: linear-gradient(135deg,
        rgba(43, 46, 51, 0.86) 0%,
        rgba(26, 29, 33, 0.88) 100%);
    z-index: -1;
}
```

**Result:** The tinfoil texture is visible but subtle, creating depth without compromising readability.

---

## Layout System

### Grid Architecture

#### Desktop Layout (1024px+)
```
┌─────────────────────────────────────────────┐
│  Header (90px height)                       │
├─────┬───────────────────────────────────────┤
│     │                                       │
│  N  │    Primary Content Area               │
│  A  │    (60-65% width)                     │
│  V  │                                       │
│     │    Max-width: 950px for content       │
│  5  │                                       │
│  %  │    ┌─────────────────┐                │
│     │    │   Tool Card     │                │
│  L  │    └─────────────────┘                │
│  e  │                                       │
│  f  │    ┌─────────────────┐                │
│  t  │    │   Tool Card     │                │
│     │    └─────────────────┘                │
│     │                                       │
└─────┴───────────────────────────────────────┘
│            Footer                           │
└─────────────────────────────────────────────┘
```

**Content Margins:**
- Left: 24% (includes 5% nav space + breathing room)
- Right: 18%
- Max-width: 950px for text blocks, 850px for hero content

#### Mobile Layout (<1024px)
- Single column, full width
- Navigation moves to fixed bottom bar
- Margins: 5% left/right
- Cards stack vertically

---

### Spacing System (8px Grid)

**Base Unit:** 8px

```
--spacing-2xs: 4px     /* Tight elements, icon gaps */
--spacing-xs: 8px      /* Small gaps */
--spacing-sm: 16px     /* Input padding, small spacing */
--spacing-md: 24px     /* Standard element spacing */
--spacing-lg: 36px     /* Larger gaps */
--spacing-xl: 54px     /* Card padding, section spacing */
--spacing-2xl: 75px    /* Section header margins */
--spacing-3xl: 110px   /* Section padding vertical */
--spacing-4xl: 140px   /* Hero padding top */
```

**Application:**
- All spacing must be multiples of 4px (preferably 8px)
- Vertical rhythm: 24px base for text blocks
- Section padding: 110px top/bottom (desktop)
- Card padding: 54px all sides

---

### Section Structure

**Pattern: Alternating Backgrounds**
```
Hero:      Charcoal Grey (#2b2e33)
Solutions: Dark Grey (#35383d)
About:     Charcoal Grey (#2b2e33)
Contact:   Dark Grey (#35383d)
Footer:    Deep Charcoal (#1a1d21)
```

**Section Anatomy:**
```html
<section class="section-name">
  <div class="section-header">
    <div class="section-eyebrow">LABEL</div>
    <h2 class="section-title">Title</h2>
    <p class="section-subtitle">Description</p>
  </div>
  <div class="section-content">
    <!-- Content here -->
  </div>
</section>
```

**Separator Lines:**
- Height: 1px
- Color: Slate Blue (#4a5f7a) with gradient fade
- Opacity: 30-40%
- Placement: Top of each section

---

## Component Specifications

### 1. Header Component

**Dimensions:**
- Height: 90px (fixed)
- Width: 100%
- Position: Fixed top

**Background:**
- Color: Charcoal Grey (#2b2e33)
- Opacity: 92%
- Backdrop Filter: blur(16px) saturate(180%)

**Border:**
- Bottom: 1px solid Slate Blue (#4a5f7a, 20% opacity)
- Accent bar: 2px gradient (slate blue, center glow, fade)

**Logo:**
- Size: 30px
- Weight: 700 (Bold)
- Text Transform: UPPERCASE
- Color: Off-White (#f5f5f5)
- Accent: Mustard Yellow (#d4a017) for "FOIL"
- Spacing: -0.015em letter spacing

---

### 2. Navigation Component (Vertical Sidebar)

**Desktop Only (hidden on mobile < 1024px)**

**Position:**
- Fixed left at 5%
- Vertical center (top: 50%, translateY(-50%))
- Z-index: 100

**Links:**
- Font Size: 16px
- Font Weight: 600 (Semi-Bold)
- Text Transform: UPPERCASE
- Letter Spacing: 2px
- Line Height: 36px (creates spacing between links)
- Margin Bottom: 36px per link

**States:**
```css
Default:
  - Color: Light Grey (#d1d1d1, 70% opacity)

Hover:
  - Color: Mustard Yellow (#d4a017)
  - Opacity: 100%
  - Underline: 2px, 70% width, animates in

Active (Scroll-based via JavaScript):
  - Color: Mustard Yellow (#d4a017)
  - Opacity: 100%
  - Underline: 2px, 70% width, permanent
  - Font Weight: 700 (heavier than default 600)
  - Transition: None (state change, not animation)
```

---

### 3. Hero Section

**Layout:**
- Min-height: 100vh
- Display: Flex
- Align: Center
- Justify: Center
- Text-align: Center
- Padding: 140px 18% 100px 24%

**Background Effect:**
- Radial gradient glow (Slate Blue at 15% opacity)
- Size: 600x600px
- Position: 20% from top, 35% from left
- Blur: 100px
- Opacity: 60%

**Content Structure:**
```
Eyebrow (optional)
  ↓
Hero Headline
  ↓
Hero Subheadline
  ↓
CTA Button
```

**Eyebrow:**
- Size: 13px
- Weight: 700 (Bold)
- Transform: UPPERCASE
- Spacing: 4px letter spacing
- Color: Antique Gold (#c9a961, 90% opacity)
- Margin: 24px bottom

**Headline:**
- Size: 46-80px (fluid)
- Weight: 700 (Bold)
- Color: Off-White (#f5f5f5)
- Line Height: 1.08
- Margin: 32px bottom
- Highlight word: Mustard Yellow (#d4a017)

**Subheadline:**
- Size: 19-26px (fluid)
- Weight: 400 (Regular)
- Color: Light Grey (#d1d1d1, 85% opacity)
- Max-width: 700px
- Margin: 60px bottom

---

### 4. CTA Button (Primary)

**Dimensions:**
- Padding: 26px 68px
- Border Radius: 8px

**Typography:**
- Font Size: 16px
- Font Weight: 700 (Bold)
- Text Transform: UPPERCASE
- Letter Spacing: 1px

**Colors:**
```css
Default:
  - Background: Mustard Yellow (#d4a017)
  - Text: Charcoal Grey (#2b2e33)
  - Shadow: 0 7px 28px rgba(212, 160, 23, 0.3)

Hover:
  - Background: Antique Gold (#c9a961)
  - Transform: translateY(-3px) scale(1.02)
  - Shadow: 0 14px 45px rgba(212, 160, 23, 0.45)
```

**Transition:** 320ms cubic-bezier(0.34, 1.56, 0.64, 1) - spring effect

---

### 5. Tool Cards (Single Column)

**Container:**
- Background: Card Light (#f5f5f5)
- Padding: 54px
- Border Radius: 12px
- Border: 1px solid Slate Blue (#4a5f7a, 12% opacity)
- Shadow: 0 12px 35px rgba(0, 0, 0, 0.4)
- Max-width: 950px
- Margin: 44px gap between cards

**Top Border Gradient (Hidden by default):**
- Height: 4px
- Gradient: Slate Blue → Mustard Yellow
- Transform: scaleX(0) → scaleX(1) on hover
- Transform Origin: Left
- Transition: 370ms ease

**Hover State:**
```css
- Transform: translateY(-9px)
- Shadow: 0 24px 55px rgba(0, 0, 0, 0.5)
- Border: 1px solid Slate Blue (#4a5f7a)
- Top gradient: Reveals (scaleX(1))
- Radial glow: Slate Blue overlay fades in
```

**Card Header:**
- Display: Flex
- Justify: Space-between
- Margin-bottom: 24px

**Card Title:**
- Size: 30px
- Weight: 700 (Bold)
- Color: Card Dark Text (#2b2e33)
- Letter Spacing: -0.01em
- Margin-bottom: 10px

**Card Number:**
- Size: 72px
- Weight: 700 (Bold)
- Color: Slate Blue (#4a5f7a, 8% opacity)
- Position: Absolute right
- Line Height: 1

**Card Tagline:**
- Size: 16px
- Weight: 600 (Semi-Bold)
- Style: Italic
- Color: Ochre (#cc8800)
- Margin-bottom: 26px

**Card Description:**
- Size: 17px
- Weight: 400 (Regular)
- Color: Card Dark Text (#2b2e33, 75% opacity)
- Line Height: 1.8
- Margin-bottom: 36px

**Card Footer:**
- Padding-top: 28px
- Border-top: 1px solid Slate Blue (#4a5f7a, 15% opacity)

**Card Link:**
```css
Default:
  - Padding: 17px 36px
  - Border: 2px solid Slate Blue (#4a5f7a)
  - Background: Transparent
  - Color: Slate Blue (#4a5f7a)
  - Text Transform: UPPERCASE
  - Letter Spacing: 1px

Hover:
  - Background: Mustard Yellow (#d4a017)
  - Border: Mustard Yellow (#d4a017)
  - Color: Card Dark Text (#2b2e33)
  - Transform: translateX(7px)
  - Shadow: 0 4px 16px rgba(212, 160, 23, 0.3)
```

---

### 6. Section Patterns

**Section Eyebrow:**
- Size: 12px
- Weight: 700 (Bold)
- Transform: UPPERCASE
- Spacing: 3px letter spacing
- Color: Antique Gold (#c9a961, 90% opacity)
- Margin-bottom: 16px

**Section Title:**
- Size: 40-60px (fluid)
- Weight: 700 (Bold)
- Color: Off-White (#f5f5f5)
- Letter Spacing: -0.02em
- Margin-bottom: 18px

**Section Subtitle:**
- Size: 18px
- Weight: 400 (Regular)
- Color: Medium Grey (#9a9a9a)
- Max-width: 620px
- Margin: 0 auto
- Line Height: 1.7

---

### 7. Footer

**Background:** Deep Charcoal (#1a1d21)
**Border Top:** 1px solid Slate Blue (#4a5f7a, 15% opacity)
**Padding:** 55px 5%
**Text Align:** Center
**Font Size:** 14px
**Color:** Cool Grey (#7a7d82)

---

## Interactive States & Animations

### Transition Speeds

```css
--transition-fast: 150ms
--transition-base: 250ms
--transition-slow: 370ms
--transition-hero: 600ms
```

**Easing Functions:**
- Standard: `ease` or `cubic-bezier(0.4, 0, 0.2, 1)`
- Spring (hover): `cubic-bezier(0.34, 1.56, 0.64, 1)`
- Smooth: `ease-in-out`

---

### Motion Design Principles

**Philosophy:**

Every animation must serve a purpose—feedback, spatial orientation, or attention guidance. Gratuitous motion is prohibited. Motion should feel tasteful and smart, never flashy or distracting.

**Purposeful Motion Categories:**

**1. Feedback Motion** (User initiated an action)
- Duration: 150-250ms
- Easing: Spring (`cubic-bezier(0.34, 1.56, 0.64, 1)`)
- Examples: Button presses, card taps, form submissions
- Purpose: Confirms the interaction was registered

**2. Spatial Motion** (Object changes position or size)
- Duration: 250-370ms
- Easing: Ease-in-out
- Examples: Card lifts, panel reveals, navigation transitions
- Purpose: Helps user understand spatial relationships

**3. Attention Motion** (Drawing eye to something new)
- Duration: 370-600ms
- Easing: Ease-out (starts fast, ends slow)
- Examples: New content appearing, notification badges
- Purpose: Guides user's attention without being jarring

**Accessibility Requirement:**

Always respect `prefers-reduced-motion` media query. Users with vestibular disorders or motion sensitivity must have a non-animated experience.

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

**Motion Guidelines:**
- Subtle is better than dramatic
- One motion at a time (don't stack multiple animations)
- Motion should enhance, not distract
- Default to no motion; add only when it serves a clear purpose

---

### Hover Interactions

**Cards:**
- Lift: translateY(-9px)
- Shadow increase: 12px → 24px blur
- Border reveal
- Top gradient reveal
- Transition: 370ms spring

**Buttons:**
- Lift: translateY(-3px)
- Scale: 1.02
- Shadow increase
- Color shift (mustard → gold)
- Transition: 320ms spring

**Links:**
- Color shift
- Underline animation (width 0 → 70%)
- Transform: translateX(7px) for card links
- Transition: 250ms ease

**Navigation:**
- Color: grey → mustard
- Opacity: 70% → 100%
- Underline: animates in
- Transition: 250ms ease

---

### Focus States (Accessibility)

**All Interactive Elements:**
```css
*:focus-visible {
  outline: 2px solid Mustard Yellow (#d4a017);
  outline-offset: 3px;
  border-radius: 4px;
}
```

**Remove for Mouse Users:**
```css
*:focus:not(:focus-visible) {
  outline: none;
}
```

---

### Loading States

**Buttons During Async Operations:**
```css
Loading:
  - Cursor: wait
  - Opacity: 0.6
  - Content: "Processing..." or spinner icon
  - Pointer Events: none (disable click)
  - Animation: Subtle pulse or spinner rotation
```

**Card Placeholders (Skeleton Screens):**
```css
  - Background: Surface Grey (#3f4247)
  - Shimmer: Linear gradient animation (45deg, lighter grey traveling across)
  - Border Radius: Match component (12px for cards)
  - Height: Match expected content height
  - Margin: Match loaded card spacing
```

---

### Error States

**Form Validation Errors:**
```css
  - Border: 2px solid #d32f2f (red, not in primary palette)
  - Background: rgba(211, 47, 47, 0.08)
  - Error Text: 14px, Regular, #d32f2f
  - Icon: Alert triangle, 16px, #d32f2f
  - Message Position: Below input field
```

**General Error Messages:**
```css
  - Background: rgba(211, 47, 47, 0.1)
  - Border Left: 4px solid #d32f2f
  - Padding: 16px 24px
  - Text: 16px, Regular, Off-White (#f5f5f5)
  - Icon: X circle or alert, Mustard Yellow (to match brand)
  - Border Radius: 6px
```

**Inline Error Text:**
- Font Size: 14px
- Color: #d32f2f
- Margin Top: 8px
- Font Weight: 400 (Regular)

---

### Disabled States

**Buttons:**
```css
Disabled:
  - Background: Medium Grey (#9a9a9a, 20% opacity)
  - Text: Cool Grey (#7a7d82)
  - Cursor: not-allowed
  - Opacity: 0.4
  - No hover effects
  - Border: None or 1px solid Medium Grey (20% opacity)
```

**Form Inputs:**
```css
Disabled:
  - Background: rgba(154, 154, 154, 0.1)
  - Border: 1px solid rgba(154, 154, 154, 0.3)
  - Text: Cool Grey (#7a7d82)
  - Cursor: not-allowed
  - Placeholder: Invisible or very faint
```

**Navigation Links:**
```css
Disabled:
  - Color: Medium Grey (#9a9a9a, 40% opacity)
  - Cursor: not-allowed
  - No hover effects
  - Text Decoration: Line-through (optional, context-dependent)
```

---

### Empty States

**Card Grid with No Items:**
```css
  - Min Height: 400px
  - Display: Flex, align center, justify center
  - Flex Direction: Column
  - Icon: Muted illustration or icon (Medium Grey, 64px)
  - Text: "No solutions yet" (Light Grey, 20px, Semi-Bold)
  - Subtext: "Check back soon" (Cool Grey, 16px, Regular)
  - Margin Top (between icon and text): 24px
  - Margin Top (between text and subtext): 12px
```

**Empty Search Results:**
```css
  - Same as above, but:
  - Icon: Search icon with slash or magnifying glass
  - Text: "No results found"
  - Subtext: "Try adjusting your search"
```

**Empty State CTA (Optional):**
- Button: Secondary style (Slate Blue border)
- Text: "Browse All" or "Start Fresh"
- Margin Top: 32px from subtext

---

## Accessibility Standards

### WCAG Compliance

**Target:** WCAG AA minimum, AAA where possible

**Text Contrast Ratios Achieved:**
| Text | Background | Ratio | Standard |
|------|------------|-------|----------|
| Off-White | Charcoal Grey | 12.5:1 | AAA |
| Light Grey | Charcoal Grey | 9.2:1 | AAA |
| Medium Grey | Charcoal Grey | 4.8:1 | AA |
| Mustard Yellow | Charcoal Grey | 7.1:1 | AAA |
| Card Dark Text | Card Light | 12.5:1 | AAA |

**Minimum Touch Targets:**
- Mobile: 44x44px (Apple HIG, WCAG)
- Desktop: 32x32px minimum

**Keyboard Navigation:**
- All interactive elements must be keyboard accessible
- Tab order must be logical
- Focus indicators must be clearly visible
- Skip links provided for screen readers

---

## Brand Voice & Messaging

### Tone of Voice

**Attributes:**
- **Clear:** Simple language, no jargon
- **Confident:** Assertive without arrogance
- **Helpful:** Benefit-focused, user-centric
- **Sophisticated:** Intelligent, professional, refined

**Not:**
- Overly casual or playful
- Jargon-heavy or technical
- Apologetic or uncertain
- Pretentious or exclusive

---

### Brand Sentiments

**Primary Sentiments:**

FOIL Industries should feel:
- **Tasteful** - Refined design choices, understated elegance, quality over flash
- **Moral** - Ethical, trustworthy, doing the right thing even when no one's watching
- **Smart** - Intelligent solutions, thoughtful problem-solving, strategic thinking

**Secondary Sentiments:**
- **Modern** - Contemporary without being trendy, timeless with current sensibilities
- **Clever** - Witty when appropriate, creative problem-solving, unexpected solutions
- **In Your Corner** - Supportive ally, rooting for your success, on your side

**Experience Statement:**
> 10 years of software experience invested in your success

This statement reinforces credibility while maintaining the user-benefit focus. It's not about bragging—it's about what that experience means for the user.

---

### Messaging Framework

**Brand Tagline:**
> "Tools that make you better"

**Brand Promise:**
Like a foil character accentuates strengths, FOIL Industries creates products that amplify your capabilities and elevate your professional impact.

**Value Propositions:**
1. **Clarity** - Complex problems, simple solutions
2. **Efficiency** - Do more with less
3. **Quality** - Professional-grade tools, consumer-grade simplicity

---

### Boilerplate Descriptions

**Long Form (About Pages, Portfolio):**

FOIL Industries creates professional-grade tools with consumer-grade simplicity. Founded by a product manager who codes, we build solutions that amplify your capabilities without overshadowing them. Like a foil character in literature who makes the protagonist shine, our tools are designed to make you better—not to be the star of the show. 10 years of software experience invested in your success.

**Short Form (Directory Listings, Bios):**

FOIL Industries builds elegant tools that solve complex problems simply. Product management meets hands-on development.

**Elevator Pitch (30 seconds):**

I'm a product manager who builds. FOIL Industries is my portfolio of tools—like a budget tracker and resume optimizer—that follow one philosophy: complex problems deserve simple solutions. The name comes from literary theory: a foil character makes the hero look better. That's what these tools do for you.

**Social Media Bio:**

Product Manager & Builder | Creating tools that amplify your capabilities | Professional-grade functionality, consumer-grade simplicity

**Email Signature Tagline:**

Building tools that make you better
10 years of software experience invested in your success

**LinkedIn Headline:**

Product Manager & Builder | Creating Tasteful, Smart Tools That Amplify Your Capabilities

---

### Copywriting Patterns

**Headlines:**
- Short, declarative (3-7 words)
- Active voice
- Benefit-focused
- No punctuation unless necessary

**Examples:**
- "Tools That Make You Better" ✅
- "Empowering Your Journey to Success" ❌ (vague, cliché)

**Body Copy:**
- 60-80 characters per line
- Short paragraphs (2-4 sentences)
- Scannable (lists, bold key terms)
- Focus on user outcomes, not features

**CTAs:**
- Action-oriented verbs
- Specific, not generic
- 2-3 words maximum

**Examples:**
- "Explore Solutions" ✅
- "Try Budget Manager" ✅
- "Learn More" ❌ (generic)
- "Click Here" ❌ (vague)

---

## Implementation Guidelines

### File Structure

```
foil-industries/
├── assets/
│   ├── images/
│   │   └── tinfoil.webp (background texture)
│   ├── fonts/
│   │   └── space-grotesk/ (woff2, woff formats)
│   └── icons/
├── styles/
│   ├── variables.css (color tokens, spacing)
│   ├── typography.css (type scale, font faces)
│   ├── components.css (buttons, cards, nav)
│   └── global.css (base styles, layout)
├── components/
│   ├── Header/
│   ├── Navigation/
│   ├── Hero/
│   ├── ToolCard/
│   ├── Section/
│   └── Footer/
└── pages/
    └── index.html
```

---

### CSS Variable System

```css
:root {
  /* Colors - Primary Blues */
  --color-slate-blue: #4a5f7a;
  --color-steel-blue: #5b7d99;
  --color-dusty-blue: #6b8ea8;

  /* Colors - Backgrounds */
  --color-deep-charcoal: #1a1d21;
  --color-charcoal: #2b2e33;
  --color-dark-grey: #35383d;
  --color-surface-grey: #3f4247;

  /* Colors - Text */
  --color-off-white: #f5f5f5;
  --color-light-grey: #d1d1d1;
  --color-medium-grey: #9a9a9a;
  --color-cool-grey: #7a7d82;

  /* Colors - Accents */
  --color-mustard: #d4a017;
  --color-gold: #c9a961;
  --color-ochre: #cc8800;

  /* Colors - Cards */
  --color-card-light: #f5f5f5;
  --color-card-dark-text: #2b2e33;

  /* Spacing (8px grid) */
  --spacing-2xs: 4px;
  --spacing-xs: 8px;
  --spacing-sm: 16px;
  --spacing-md: 24px;
  --spacing-lg: 36px;
  --spacing-xl: 54px;
  --spacing-2xl: 75px;
  --spacing-3xl: 110px;
  --spacing-4xl: 140px;

  /* Typography */
  --font-family-primary: 'Space Grotesk', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;

  /* Transitions */
  --transition-fast: 150ms;
  --transition-base: 250ms;
  --transition-slow: 370ms;
  --transition-spring: cubic-bezier(0.34, 1.56, 0.64, 1);
}
```

---

### Responsive Breakpoints

```css
/* Mobile First Approach */

/* Small Mobile */
@media (min-width: 375px) { }

/* Large Mobile */
@media (min-width: 576px) { }

/* Tablet */
@media (min-width: 768px) { }

/* Desktop */
@media (min-width: 1024px) {
  /* Vertical sidebar nav appears */
  /* Single to multi-column layouts */
}

/* Large Desktop */
@media (min-width: 1440px) {
  /* Max widths enforced */
  /* Optimal reading line lengths */
}

/* XL Desktop */
@media (min-width: 1920px) {
  /* Container max-widths */
  /* Prevent over-stretching */
}
```

---

## Logo Usage

### Primary Logo

**Format:** Text-based logo (no symbol)
**Typography:** Space Grotesk Bold, 30px+
**Text:** "FOIL Industries"
**Treatment:** "FOIL" in Mustard Yellow, "Industries" in Off-White

**Minimum Size:**
- Digital: 120px width
- Print: 1.5 inches width

**Clear Space:**
- Minimum: Logo height × 0.5 on all sides

**Do's:**
- Use on dark backgrounds (charcoal to black)
- Maintain color ratio (mustard "FOIL" + white "Industries")
- Use approved color variations only

**Don'ts:**
- Don't place on light backgrounds without adjustment
- Don't rotate or distort
- Don't add effects (shadows, outlines, etc.)
- Don't change the font
- Don't separate "FOIL" from "Industries"

---

### Logo Color Variations

**Primary (Dark Backgrounds):**
- FOIL: Mustard Yellow (#d4a017)
- Industries: Off-White (#f5f5f5)

**Light Backgrounds (if necessary):**
- FOIL: Ochre (#cc8800)
- Industries: Charcoal Grey (#2b2e33)

**Monochrome:**
- Full logo: Single color based on context
- Use sparingly (embroidery, stamps, etc.)

---

## Design Principles

### 1. Sophistication Through Restraint

**Practice:**
- Use color sparingly (80% greys, 20% color)
- Generous whitespace (40-50% of viewport)
- Limited font weights (only 3: 400, 600, 700)
- Purposeful animations (every movement has meaning)

**Avoid:**
- Color overload
- Cluttered layouts
- Excessive font variation
- Gratuitous animations

---

### 2. Hierarchy Through Contrast

**Practice:**
- High contrast for important elements
- Reduced contrast for secondary elements
- Size, weight, and color work together
- Clear visual priority at all times

**Example:**
```
Hero Headline: 80px, Bold, Off-White = Maximum priority
Subheadline: 26px, Regular, Light Grey 85% = Secondary
CTA: 16px, Bold, Mustard BG = Action priority
```

---

### 3. Consistency Builds Trust

**Practice:**
- Reuse components exactly
- Maintain spacing rhythm (8px grid)
- Consistent interaction patterns
- Predictable color usage

**Avoid:**
- One-off components
- Random spacing
- Inconsistent hover states
- Ad-hoc color choices

---

### 4. Accessibility First

**Practice:**
- Design with contrast in mind from the start
- Test with keyboard navigation
- Provide clear focus indicators
- Use semantic HTML

**Checklist:**
- [ ] All text meets minimum contrast (4.5:1 for body, 3:1 for large)
- [ ] All interactive elements keyboard accessible
- [ ] Focus indicators visible on all focusable elements
- [ ] Meaningful alt text for all images
- [ ] Proper heading hierarchy (H1 → H2 → H3)

---

## Production Checklist

### Before Launch

**Design:**
- [ ] All colors match brand guidelines
- [ ] Typography scale implemented correctly
- [ ] Spacing follows 8px grid
- [ ] All components have hover/focus states
- [ ] Responsive breakpoints tested

**Performance:**
- [ ] Images optimized (WebP format)
- [ ] Fonts preloaded
- [ ] CSS minified
- [ ] No unused CSS
- [ ] Lighthouse score 90+

**Accessibility:**
- [ ] WCAG AA compliance verified
- [ ] Keyboard navigation tested
- [ ] Screen reader tested (NVDA or JAWS)
- [ ] Color contrast verified (tools: WebAIM, Stark)
- [ ] Skip links implemented

**SEO:**
- [ ] Meta tags complete
- [ ] Open Graph images (1200x630px)
- [ ] Semantic HTML structure
- [ ] Descriptive headings
- [ ] Alt text on all images

**Quality:**
- [ ] Cross-browser tested (Chrome, Firefox, Safari, Edge)
- [ ] Mobile tested (iOS, Android)
- [ ] Forms validated
- [ ] Links verified
- [ ] Console errors cleared

---

## File Deliverables

### Design System Files

1. **Brand Guidelines (this document)**
   - File: `FOIL_BRAND_GUIDELINES.md`
   - Format: Markdown

2. **Primary Design Reference**
   - File: `hybrid-2-slate-mustard.html`
   - Format: HTML/CSS (standalone mockup)

3. **Background Texture**
   - File: `tinfoil.webp`
   - Location: User desktop (to be moved to assets)
   - Format: WebP
   - Usage: Fixed background, 8% opacity

4. **Color Swatches**
   - Export from HTML as ASE/ACO for design tools
   - CSS variables file for development

---

## Revision History

**Version 1.0 - December 25, 2025**
- Initial brand guidelines created
- Slate & Mustard design system established
- Tinfoil texture background integrated (86-88% overlay opacity)
- Space Grotesk typography system defined
- Component library documented
- Accessibility standards set (WCAG AA minimum)

---

## Contact & Approvals

**Design System Owner:** Watson Mulkey
**Approved By:** [To be filled]
**Date Approved:** December 25, 2025
**Next Review:** Q2 2026

---

## Appendix A: Quick Reference

### Most Used Colors
```css
Background: #2b2e33 (Charcoal Grey)
Text: #f5f5f5 (Off-White)
Accent: #d4a017 (Mustard Yellow)
Primary Blue: #4a5f7a (Slate Blue)
```

### Most Used Spacing
```css
Section Padding: 110px vertical
Card Padding: 54px all sides
Element Gap: 24px
Card Gap: 44px
```

### Most Used Typography
```css
Headlines: 40-80px, Bold, Off-White
Body: 17-18px, Regular, Light Grey
Labels: 12-13px, Bold, UPPERCASE, Gold
Buttons: 16px, Bold, UPPERCASE, Mustard BG
```

---

**End of Brand Guidelines**

*This is a living document. Updates should be versioned and approved by the design system owner.*
