   # VinEstate Landing Page - Setup & Customization Guide

This is a premium, static, single-page business landing page built for **VinEstate**, Nashik's premier B2B Business Growth Systems partner.

The site is built using plain semantic **HTML5**, modern custom-property-driven **CSS3**, and clean **Vanilla JavaScript**. It has no heavy framework dependencies or build steps, allowing it to load instantly and deploy on zero-cost static hosting services.

## 📁 File Structure

The project has a lightweight and organized structure:
```text
├── index.html     # Semantic markup, inline SVGs, layout components, and form
├── styles.css     # Premium styling, typography, CSS design variables, and layout systems
├── script.js     # Responsive behaviors, tab-switch systems, animations, and AJAX submissions
├── README.md      # This installation and customization document
└── assets/
    ├── icons/     # Custom website logo/brand graphic assets
    └── images/    # Target directory for brand photography
```

---

## ⚡ Web3Forms Setup Guide

The website features an interactive lead capture form that runs entirely serverless using the free **Web3Forms** utility. 

To configure form submissions to deliver emails to your inbox:

1. Visit [Web3Forms](https://web3forms.com) and enter your target email address (e.g., `ai.solutionforstartups@gmail.com`) to generate a free Access Key.
2. Open `index.html` in a code editor.
3. Locate the form block (around line 720) and search for the access key input:
   ```html
   <input type="hidden" name="access_key" value="YOUR_ACCESS_KEY_HERE">
   ```
4. Replace `YOUR_ACCESS_KEY_HERE` with the Access Key received in your email.
5. Save the file. Form submissions will now automatically forward to your inbox with live sender details!

---

## 🎯 Placeholder Customization Index

To tailor the site for production, replace the following clearly marked placeholders inside `index.html` and `script.js`:

| Placeholder Token | Description | Location | Replacement Value |
| :--- | :--- | :--- | :--- |
| `YOUR_ACCESS_KEY_HERE` | Web3Forms Free API Key | `index.html` (Form section) | E.g. `24da3491-a20c-...` |
| `https://www.vinestate.in` | Meta Canonical Link & og:url | `index.html` (Head section) | Final production URL |
| `https://www.vinestate.in/assets/images/og-share.jpg` | Open Graph Social Preview Image | `index.html` (Head tags) | 1200x630px card image |
| `[HERO_IMAGE]` | Hero Background / Side Image | `index.html` | Place in `assets/images/` |
| `[ABOUT_IMAGE]` | About Us Operations Image | `index.html` | Team or winery photo |
| `[CASE_STUDY_IMAGE_1/2/3]` | Case study preview blocks | `index.html` | Case study references |
| `[TESTIMONIAL_PHOTO_1/2/3]` | Client avatar thumbnails | `index.html` | 100x100px square avatars |
| `9421445548` | Primary WhatsApp Link & Phone | `index.html` & `script.js` | `9421445548` (already set as default) |
| `ai.solutionforstartups@gmail.com` | Corporate Email | `index.html` & `script.js` | Email address (already set as default) |
| `Nashik, Maharashtra, India` | Company location | `index.html` | Office address |

*Note: All core placeholders are commented in the code source with `<!-- PLACEHOLDER: ... -->` labels for easy text searches.*

---

## 🚀 Deployment Instructions

### Option 1: GitHub Pages (Recommended - 100% Free)
1. Initialize a Git repository in this folder:
   ```bash
   git init
   git add .
   git commit -m "Initial commit - VinEstate site"
   ```
2. Create a repository on GitHub and push your local commits.
3. In your GitHub repository settings, navigate to the **Pages** tab.
4. Set the build and deployment source to **Deploy from a branch** and select your active branch (e.g. `main` / `master`), pointing to `/ (root)`.
5. Click Save. Your website will be live at `https://[username].github.io/[repo-name]/` in under a minute!

### Option 2: Netlify Drag & Drop
1. Open [Netlify App](https://app.netlify.com).
2. Drag and drop this project folder directly into the designated "Drag and drop your site folder here" box on the dashboard.
3. Your site is deployed instantly on a custom subdomain. Add custom domains and SSL configuration with a single click.

### Option 3: Vercel Static Deploy
1. Install Vercel CLI locally or connect your GitHub account to [Vercel](https://vercel.com).
2. Create a new project, select the repository or deploy directly via directory selection.
3. Vercel will auto-detect the project as a zero-configuration Static Site. Click **Deploy**.

---

## 📱 Responsive Testing Breakpoints

The site has been designed mobile-first and tested to render correctly across these breakpoints:
- **Mobile (360px - 480px)**: Compact vertical timeline, single-column package grids, and drawer hamburger navigation.
- **Tablet (768px - 991px)**: Dual-column grid layouts, 2x6 services grid, and side-scroll friendly features.
- **Desktop (1024px - 1440px+)**: Center-alternating vertical timeline, horizontal tabs for vertical Packages selection, full header layout, and hovering lift effects.
