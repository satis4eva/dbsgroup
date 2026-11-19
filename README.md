# dbsgroup.io

Static website for DBS Group (HTML, CSS, JS: no build step).

## Files
- `index.html`: all page content (sections: hero, about, companies, platforms, services, why, contact, footer)
- `css/style.css`: styling; brand colours and fonts are in `:root` at the top
- `js/main.js`: mobile menu, scroll effects, contact form (opens email to hello@dbsgroup.io)

## Editing
- Change text: edit `index.html`, commit and push.
- Add a company or platform: copy an existing `<article class="card">` or `<div class="platform">` block.
- Contact form: currently uses mailto. To receive submissions without the visitor's email app, set up a form service (e.g. Formspree) and point the form's `action` at it.

## Deploy (GitHub → Hostinger)
1. Push this folder to a GitHub repo (e.g. `satis4eva/dbsgroup`).
2. Hostinger hPanel → dbsgroup.io → Advanced → Git: add the repo, branch `main`, install path `public_html` (empty).
3. Turn on auto-deployment (webhook) so every push goes live.
4. Back up or disable the current Horizons site before switching the domain over.
