# FOIL Engineering Blog Guide

## Overview

The blog is built using Astro Content Collections, providing a simple, file-based system for managing blog posts. No database required - just drop markdown files in a folder!

## How to Add a New Blog Post

### 1. Create a New Markdown File

Navigate to `src/content/blog/` and create a new `.md` file:

```
src/content/blog/my-new-post.md
```

**Naming Convention:**
- Use lowercase with hyphens: `my-blog-post.md`
- The filename becomes the URL slug: `/blog/my-blog-post/`
- Keep it short and descriptive

### 2. Add Frontmatter

Start your markdown file with frontmatter (metadata between `---` markers):

```markdown
---
title: 'Building Elegant Tools: A Design Philosophy'
description: 'How thoughtful design amplifies human capability rather than replacing it.'
pubDate: 2025-01-15
author: 'Watson Mulkey'
tags: ['Design Systems', 'Product Management', 'Philosophy']
featured: false
draft: false
heroImage: '/images/blog/elegant-tools.jpg'  # Optional
---

# Your blog post content starts here...
```

### 3. Write Your Content

Use standard markdown syntax:

```markdown
## Headings

Use ## for main sections, ### for subsections.

## Lists

- Bullet point one
- Bullet point two

1. Numbered item
2. Another item

## Links and Images

[Link text](https://example.com)

![Alt text](/images/blog/my-image.jpg)

## Code

Inline `code` or code blocks:

\`\`\`javascript
const example = 'Hello World';
console.log(example);
\`\`\`

## Emphasis

**Bold text** and *italic text*

## Quotes

> This is a blockquote
> - Author Name
```

### 4. Build and Preview

```bash
npm run dev
```

Visit `http://localhost:4321/blog/` to see your blog listing and `http://localhost:4321/blog/your-post/` to see the individual post.

### 5. Publish

When ready to publish:

```bash
# Build the site
npm run build

# Deploy (Fly.io)
flyctl deploy
```

## Frontmatter Fields Reference

| Field | Required | Type | Description |
|-------|----------|------|-------------|
| `title` | ✅ Yes | string | Post title (used as h1 and in meta tags) |
| `description` | ✅ Yes | string | Short description for cards and SEO |
| `pubDate` | ✅ Yes | date | Publication date (YYYY-MM-DD format) |
| `author` | No | string | Author name (defaults to "Watson Mulkey") |
| `tags` | No | array | Topic tags (e.g., `['Design', 'PWA']`) |
| `featured` | No | boolean | Show in featured section (defaults to false) |
| `draft` | No | boolean | Hide from site if true (defaults to false) |
| `heroImage` | No | string | Path to hero image (defaults to none) |
| `updatedDate` | No | date | Last updated date (optional) |

## Draft Workflow

To work on a post without publishing:

1. Set `draft: true` in frontmatter
2. The post won't appear on the live site
3. You can still preview it locally
4. When ready, set `draft: false`

## Featured Posts

Featured posts appear at the top of the blog page in larger cards:

```markdown
---
title: 'Important Announcement'
featured: true
---
```

**Best Practice:** Limit to 1-2 featured posts at a time.

## Adding Images

### 1. Add Images to Public Folder

```
public/images/blog/my-image.jpg
```

### 2. Reference in Markdown

```markdown
![Description of image](/images/blog/my-image.jpg)
```

### 3. Hero Images (Optional)

```markdown
---
heroImage: '/images/blog/my-hero.jpg'
---
```

Hero images appear at the top of blog posts and in social share cards.

## SEO Best Practices

### Title
- Keep under 60 characters
- Front-load important keywords
- Make it compelling and specific

### Description
- 120-160 characters optimal
- Include primary keyword naturally
- Write for humans, not just search engines

### Example:
```markdown
---
title: 'PWA Design Patterns for 2025'
description: 'Practical design patterns for building Progressive Web Apps that users love. Real examples from The Number.'
---
```

## File Organization

```
src/content/blog/
├── 2025/                           # Organize by year (optional)
│   ├── january/
│   │   ├── new-year-roadmap.md
│   │   └── design-systems-101.md
│   └── february/
│       └── pwa-best-practices.md
└── example-post.md
```

**Note:** File organization doesn't affect URLs. The filename determines the URL slug.

## Quick Start Checklist

- [ ] Create `.md` file in `src/content/blog/`
- [ ] Add required frontmatter (title, description, pubDate)
- [ ] Write content in markdown
- [ ] Add images to `public/images/blog/` if needed
- [ ] Preview locally with `npm run dev`
- [ ] Set `draft: false` when ready
- [ ] Build and deploy

## Example Post Template

Copy this template for new posts:

```markdown
---
title: 'Your Post Title Here'
description: 'A compelling description that makes people want to read.'
pubDate: 2025-01-15
author: 'Watson Mulkey'
tags: ['Tag1', 'Tag2', 'Tag3']
featured: false
draft: false
heroImage: '/images/blog/your-hero-image.jpg'
---

# Introduction

Start with a compelling opening that hooks the reader.

## Main Section

Your main content goes here. Break it into logical sections.

### Subsection

Use subsections to organize complex topics.

## Key Takeaways

- Bullet point one
- Bullet point two
- Bullet point three

## Conclusion

Wrap up with a clear conclusion or call to action.

---

*Questions or feedback? [Contact me](/contact)*
```

## Advanced: Future CMS Integration

This file-based system is designed to be compatible with headless CMS options:

- **Decap CMS** (formerly Netlify CMS) - Git-based CMS that commits to your repo
- **Tina CMS** - Visual editing with markdown files
- **Forestry** - Git-based CMS for static sites

All work with the existing content collection structure - no migration needed!

## Support

Need help? Questions about blog setup?
- Check the [Astro Content Collections docs](https://docs.astro.build/en/guides/content-collections/)
- Review the example post in `src/content/blog/example-post.md`
