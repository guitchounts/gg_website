# guitchounts.com

Personal site of Grigori Guitchounts. Static site built with [Astro](https://astro.build),
deployed to GitHub Pages, custom domain via GoDaddy DNS. Replaces the old Squarespace site.

## Editing content

| What | Where | Notes |
|---|---|---|
| Home page intro, About text | `src/pages/index.astro`, `src/pages/about.astro` | Plain HTML/Astro. |
| Essays & journalism | `src/data/articles.json` | One object per piece: `title, venue, date, url, dek, note`. |
| Papers | `src/data/papers.json` | `title, authors, venue, year, url, pdf, abstract`. Host PDFs in `public/papers/pdf/`. |
| Art | `src/data/art.json` + `public/images/art/` | Regenerate with `python3 scripts/make_art.py` after adding originals to `raw/art/`. |
| Old blog posts | `content/blog/*.md` | Markdown with frontmatter (`title, date, categories, tags, excerpt, legacyUrl`). |
| Site-wide links, name, description | `src/data/site.json` | |
| Headshot | `public/images/gg.jpg` | Replace the file; ~675×900 works well. |
| Of Two Minds posts | fetched from the Substack RSS feed at build time | Snapshot in `src/data/otm_feed_fallback.xml` is used if the fetch fails. |

Of Two Minds appears on the home page and on `/of-two-minds`. Because the site is static,
new Substack posts show up when the site is rebuilt; the GitHub Action rebuilds daily and on
every push, and can be run by hand from the Actions tab.

## Design

Three themes share one component layer, switched with `data-theme` on `<html>`
(`src/styles/global.css`). With no attribute set, the site is `editorial` (light) and
follows the OS dark-mode preference automatically, using the `retro` palette. The Art page
is locked light via the `theme` prop on `Base.astro`. Force a theme for preview by appending
`?theme=notebook`, `?theme=retro`, or `?theme=editorial` to any URL (persists in
localStorage); `?theme=auto` clears the override.

Fonts are self-hosted via `@fontsource` packages: Newsreader (body), Fraunces (display),
IBM Plex Mono (labels), Inter (notebook theme body).

## Local development

```bash
npm install
npm run dev        # http://localhost:4321
npm run build      # static output in dist/
npm run preview
```

## Deployment (GitHub Pages)

1. Create a GitHub repository (e.g. `guitchounts/gg_website`) and push `main`.
2. In the repo: Settings → Pages → Source: **GitHub Actions**. The workflow in
   `.github/workflows/deploy.yml` builds and deploys on push, daily, or on demand.
3. Settings → Pages → Custom domain: `www.guitchounts.com`, then tick **Enforce HTTPS**
   once the certificate is issued. `public/CNAME` already contains the domain.

### GoDaddy DNS

In GoDaddy → My Products → guitchounts.com → DNS, replace the Squarespace records with:

| Type | Name | Value | TTL |
|---|---|---|---|
| CNAME | `www` | `guitchounts.github.io` | 1 hr |
| A | `@` | `185.199.108.153` | 1 hr |
| A | `@` | `185.199.109.153` | 1 hr |
| A | `@` | `185.199.110.153` | 1 hr |
| A | `@` | `185.199.111.153` | 1 hr |

Delete the existing Squarespace `A`/`CNAME` records for `@` and `www` first (Squarespace
uses `198.185.159.x` / `198.49.23.x` and `ext-cust.squarespace.com`). Leave MX/TXT records
for email alone. Propagation is usually under an hour. Verify with:

```bash
dig +short www.guitchounts.com CNAME
dig +short guitchounts.com A
```

Then cancel the Squarespace subscription (Settings → Billing). Keep the GoDaddy domain
registration; only DNS records change. The old Squarespace URLs (`/blog/2017/1/2/...`,
`/articles`) redirect to their new locations via `astro.config.mjs`.

## Migration

`scripts/extract_squarespace.py` pulled the original content from Squarespace's
`?format=json` endpoints (stored in `raw/`, gitignored). It has already been run; it is kept
for reference.
