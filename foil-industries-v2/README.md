# FOIL Industries v2 - Slate & Mustard Edition

> Tools that make you better

A modern, sophisticated portfolio site showcasing tools built by Watson - Product Manager and builder of elegant solutions. Built with Astro and featuring the approved Slate & Mustard design system.

## 🎨 Design System

- **Color Palette:** Slate blues (#4a5f7a, #5b7d99, #6b8ea8) with Mustard/Gold accents (#d4a017, #c9a961, #cc8800)
- **Typography:** Space Grotesk (Google Fonts)
- **Background:** Charcoal with subtle tinfoil texture overlay
- **Style:** Sophisticated industrial aesthetic with refined warmth
- **Accessibility:** WCAG AA compliant

## 🚀 Quick Start

```bash
# Navigate to project
cd foil-industries-v2

# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

Visit `http://localhost:4321` to see your site!

## 📁 Project Structure

```
foil-industries-v2/
├── src/
│   ├── pages/
│   │   └── index.astro          # Main homepage with all sections
│   ├── components/
│   │   └── Header.astro          # Fixed header with logo & nav
│   ├── layouts/
│   │   └── BaseLayout.astro      # Base template with SEO
│   └── styles/
│       └── global.css            # Slate & Mustard design system
├── public/
│   └── images/
│       └── tinfoil.webp          # Background texture (to be added)
└── README.md
```

## 🎯 Features

- **Fully Responsive:** Mobile-first design that works beautifully on all devices
- **Vertical Sidebar Navigation:** Desktop-only fixed navigation (1024px+)
- **Sophisticated Design:** Slate & Mustard color palette with industrial refinement
- **Smooth Interactions:** Spring-based animations with subtle hover effects
- **SEO Optimized:** Complete meta tags, Open Graph, and Twitter Cards
- **Accessible:** WCAG AA compliant with keyboard navigation support
- **Performance:** Static site generation with Astro for blazing-fast load times

## 📋 Sections

1. **Hero** - Brand messaging with "Tools That Make You Better"
2. **Solutions** - Budget Manager and Resume Tailor cards
3. **About** - PM expertise, philosophy, and skills showcase
4. **Contact** - Email and availability information
5. **Footer** - Copyright and brand tagline

## 🎨 Color Reference

### Primary Blues
- Slate Blue: `#4a5f7a` - Primary brand color
- Steel Blue: `#5b7d99` - Secondary brand color
- Dusty Blue: `#6b8ea8` - Lighter applications

### Backgrounds
- Deep Charcoal: `#1a1d21` - Footer
- Charcoal Grey: `#2b2e33` - Main background
- Dark Grey: `#35383d` - Alternate sections

### Accents
- Mustard Yellow: `#d4a017` - Primary CTA & logo
- Antique Gold: `#c9a961` - Hover states & eyebrows
- Ochre: `#cc8800` - Card taglines

### Text
- Off-White: `#f5f5f5` - Primary text
- Light Grey: `#d1d1d1` - Secondary text
- Medium Grey: `#9a9a9a` - Tertiary text
- Cool Grey: `#7a7d82` - Footer text

## 📝 To-Do

- [ ] Add `tinfoil.webp` texture to `/public/images/` (currently using placeholder)
- [ ] Create favicon.svg
- [ ] Create og-image.png (1200x630px for social sharing)
- [ ] Update email address in Contact section
- [ ] Add actual project links for tool cards
- [ ] Configure `site` in `astro.config.mjs` for production URLs
- [ ] Add professional headshot/photo
- [ ] Create tool screenshots for Solutions cards

## 🛠️ Tech Stack

- **Framework:** Astro 5.x
- **Styling:** CSS with custom properties (no frameworks)
- **Font:** Space Grotesk via Google Fonts
- **Deployment:** Ready for Netlify, Vercel, or any static host

## 🌐 Browser Support

- Chrome/Edge (latest)
- Firefox (latest)
- Safari (latest)
- Mobile browsers (iOS Safari, Chrome)

## 📱 Responsive Breakpoints

- Mobile: < 768px
- Tablet: 768px - 1023px
- Desktop: 1024px+
- Large Desktop: 1440px+

## ⚡ Performance

- Static site generation for instant page loads
- Optimized fonts with preconnect
- Minimal JavaScript (only for nav active states)
- CSS only animations and transitions

## 🎓 Design Philosophy

**FOIL Industries** - Like a foil character in literature accentuates another character's traits, these tools are designed to make users look better and work smarter.

Every design decision follows: **Complex problems deserve simple solutions.**

## 📄 License

© 2025 FOIL Industries. All rights reserved.

---

**Status:** Phase 3 Complete - Production-ready Astro build with Slate & Mustard design system

**Built with:** Astro + Space Grotesk + Sophisticated Industrial Design
