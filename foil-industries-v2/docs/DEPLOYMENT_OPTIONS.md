# Deployment Options for FOIL Engineering

**Last Updated:** January 5, 2026

## Current Manual Process (Immediate Solution)

### Upload via cPanel File Manager

1. Upload **foil-engineering-deployment.zip** to `/home/foilexyo/public_html/`
2. Extract the zip file in cPanel File Manager
3. Delete the zip file after extraction
4. Verify site at foil.engineering

**Zip file location:** `C:\Users\watso\Dev\foil-industries-v2\foil-engineering-deployment.zip`

---

## Automated Deployment Options

### Option 1: GitHub Actions + FTP (Recommended)

**Pros:**
- Free automation with GitHub
- Works with existing cPanel hosting
- Deploys on every push to main branch
- No additional hosting costs

**Setup:**

1. **Get FTP credentials from cPanel:**
   - Host: server230.web-hosting.com
   - Username: foilexyo
   - Password: (from cPanel FTP Accounts)
   - Port: 21 (or 22 for SFTP)

2. **Add GitHub Secrets:**
   - Go to GitHub repo → Settings → Secrets → Actions
   - Add these secrets:
     - `FTP_SERVER`: server230.web-hosting.com
     - `FTP_USERNAME`: foilexyo
     - `FTP_PASSWORD`: (your FTP password)

3. **Create workflow file:**
   - Create `.github/workflows/deploy.yml` in your repo:

```yaml
name: Deploy to cPanel via FTP

on:
  push:
    branches: [ master ]

jobs:
  deploy:
    runs-on: ubuntu-latest

    steps:
    - name: Checkout code
      uses: actions/checkout@v4

    - name: Setup Node.js
      uses: actions/setup-node@v4
      with:
        node-version: '20'

    - name: Install dependencies
      run: npm install

    - name: Build Astro site
      run: npm run build

    - name: Deploy to FTP
      uses: SamKirkland/FTP-Deploy-Action@v4.3.5
      with:
        server: ${{ secrets.FTP_SERVER }}
        username: ${{ secrets.FTP_USERNAME }}
        password: ${{ secrets.FTP_PASSWORD }}
        local-dir: ./dist/
        server-dir: /public_html/
```

**Result:** Every push to `master` branch automatically builds and deploys to your site.

**Resources:**
- [FTP Deploy Action](https://github.com/marketplace/actions/ftp-deploy)
- [SamKirkland/FTP-Deploy-Action](https://github.com/SamKirkland/FTP-Deploy-Action)
- [Setting up GitHub Actions FTP deployment](https://dev.to/varungujarathi9/setting-up-github-actions-to-deploy-your-website-via-ftp-3n3a)

---

### Option 2: Migrate to Modern Static Hosting

**Better long-term solution** - Move away from cPanel to a platform designed for static sites:

#### Netlify (Free Tier)
- **Pros:** Zero-config Astro support, automatic deployments, free SSL, CDN included
- **Setup:** Connect GitHub repo, auto-deploys on push
- **Cost:** Free for personal projects
- **Custom domain:** foil.engineering (easy DNS setup)

#### Vercel (Free Tier)
- **Pros:** Built by Next.js team, excellent Astro support, edge network
- **Setup:** Import from GitHub, instant deploys
- **Cost:** Free for hobby projects
- **Custom domain:** foil.engineering supported

#### Cloudflare Pages (Free)
- **Pros:** Fastest global CDN, unlimited bandwidth, direct GitHub integration
- **Setup:** Connect repo, automatic builds
- **Cost:** 100% free (no limits on hobby tier)
- **Custom domain:** foil.engineering (Cloudflare also offers free DNS)

#### GitHub Pages (Free)
- **Pros:** Already using GitHub, totally free, reliable
- **Cons:** Requires GitHub Actions workflow, CNAME setup for custom domain
- **Setup:** Enable Pages in repo settings, use deploy workflow

**Migration is simple:**
1. Sign up for chosen platform (Netlify/Vercel/Cloudflare)
2. Connect your GitHub repo
3. Set build command: `npm run build`
4. Set publish directory: `dist`
5. Update DNS for foil.engineering to point to new host
6. Cancel cPanel hosting once verified

---

### Option 3: Alternative Control Panels

If you want to keep traditional hosting but improve the experience:

#### CloudPanel (Free)
- **Pros:** Supports Node.js and static sites natively, modern UI, 100% free
- **Setup:** Requires VPS (DigitalOcean, Vultr, etc.)
- **Cost:** $5-10/month for VPS
- **Resources:** [CloudPanel alternatives](https://www.cloudpanel.io/blog/8-best-free-cpanel-open-source-alternatives/)

#### aaPanel (Free & Open Source)
- **Pros:** Lightweight, fast, modern interface, supports Node.js
- **Setup:** Install on VPS
- **Resources:** [aaPanel cPanel alternatives](https://www.aapanel.com/blog/top-10-cpanel-alternatives-in-2025/)

---

## Recommendation

**Immediate:** Use the manual zip upload method to get the rebrand live today.

**Next week:** Set up GitHub Actions FTP deployment (Option 1) - keeps existing hosting, adds automation, zero cost.

**Future:** Consider migrating to Netlify or Cloudflare Pages for better performance, simpler workflow, and no hosting costs.

---

## Why GitHub Actions FTP is the Best Next Step

1. **No migration needed** - keeps your current cPanel hosting
2. **Free** - GitHub Actions is free for public repos
3. **Automatic** - just push to master, site updates in ~2 minutes
4. **Reliable** - widely used, well-maintained action
5. **Easy setup** - 10 minutes of configuration, lifetime of convenience

After the manual upload today, I recommend setting up the GitHub Actions workflow this week.

---

**Sources:**
- [FTP Deploy Action](https://github.com/marketplace/actions/ftp-deploy)
- [SamKirkland/FTP-Deploy-Action](https://github.com/SamKirkland/FTP-Deploy-Action)
- [FTP Deployment Guide](https://dev.to/varungujarathi9/setting-up-github-actions-to-deploy-your-website-via-ftp-3n3a)
- [Best cPanel Alternatives 2026](https://openpanel.com/blog/best-cpanel-alternatives/)
- [CloudPanel Free Alternatives](https://www.cloudpanel.io/blog/8-best-free-cpanel-open-source-alternatives/)
- [aaPanel Comparison 2026](https://www.aapanel.com/blog/top-10-cpanel-alternatives-in-2025/)
