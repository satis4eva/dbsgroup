#!/usr/bin/env python3
"""Build the dbsgroup.io blog.

Posts live in content/posts/YYYY-MM-DD-slug.md with front matter:
    ---
    title: Post title
    date: 2026-11-19
    category: Company news
    excerpt: One-sentence summary.
    ---
    Markdown body...

Run:  python3 scripts/build_blog.py
Then commit and push. Output: blog/index.html, blog/<slug>/index.html,
the "Latest news" block on index.html, and sitemap.xml.
The header and footer are copied from index.html, so edit them there.
"""
import datetime, html, os, re, shutil
import markdown, yaml

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
POSTS_DIR = os.path.join(ROOT, "content", "posts")
BLOG_DIR = os.path.join(ROOT, "blog")
INDEX = os.path.join(ROOT, "index.html")
SITE = "https://dbsgroup.io"
START, END = "<!-- LATEST_POSTS_START -->", "<!-- LATEST_POSTS_END -->"
ASSET_V = ""


def load_posts():
    posts = []
    for name in sorted(os.listdir(POSTS_DIR)):
        if not name.endswith(".md"):
            continue
        raw = open(os.path.join(POSTS_DIR, name), encoding="utf-8").read()
        m = re.match(r"^---\n(.*?)\n---\n(.*)$", raw, re.S)
        if not m:
            raise SystemExit(f"{name}: missing front matter")
        meta = yaml.safe_load(m.group(1)) or {}
        slug = re.sub(r"^\d{4}-\d{2}-\d{2}-", "", name[:-3])
        date = meta.get("date")
        if isinstance(date, str):
            date = datetime.date.fromisoformat(date)
        posts.append({
            "slug": slug,
            "title": str(meta["title"]),
            "date": date,
            "category": str(meta.get("category", "News")),
            "excerpt": str(meta.get("excerpt", "")),
            "body": markdown.markdown(m.group(2), extensions=["extra", "sane_lists"]),
        })
    posts.sort(key=lambda p: p["date"], reverse=True)
    return posts


def fmt(d):
    return f"{d.day} {d.strftime('%B %Y')}"


def shared_parts():
    src = open(INDEX, encoding="utf-8").read()
    header = re.search(r'<header class="nav".*?</header>', src, re.S).group(0)
    footer = re.search(r'<footer class="footer">.*?</footer>', src, re.S).group(0)
    fix = lambda s: re.sub(r'href="#', 'href="/#', s)
    header = fix(header).replace('href="/#top" class="logo"', 'href="/" class="logo"')
    header = header.replace('<a href="/blog/">Blog</a>', '<a href="/blog/" class="active">Blog</a>')
    head = re.search(r'(<link rel="icon".*?<link rel="stylesheet" href=")(css/style\.css[^"]*)(">)', src, re.S)
    return header, fix(footer), head.group(1) + "/" + head.group(2) + head.group(3)


def page(title, desc, url, head_links, header, footer, body, og_type="website"):
    e = html.escape
    return f"""<!DOCTYPE html>
<html lang="en-GB">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:url" content="{url}">
<meta property="og:type" content="{og_type}">
<link rel="canonical" href="{url}">
{head_links}
</head>
<body class="page-blog">
{header}
<main>
{body}
</main>
{footer}
<script src="/js/main.js?v={ASSET_V}"></script>
</body>
</html>
"""


def card(p):
    e = html.escape
    return f"""<a class="post-card reveal" href="/blog/{p['slug']}/">
        <p class="card-tag">{e(p['category'])} · {fmt(p['date'])}</p>
        <h3>{e(p['title'])}</h3>
        <p>{e(p['excerpt'])}</p>
        <span class="card-link">Read article <span>→</span></span>
      </a>"""


ICONS = {
    "linkedin": ("LinkedIn", '<path d="M4.98 3.5a2.5 2.5 0 1 1 0 5 2.5 2.5 0 0 1 0-5zM3 9h4v12H3zM9 9h3.8v1.7h.05c.53-1 1.83-2.05 3.77-2.05C20.6 8.65 21 11.3 21 14.4V21h-4v-5.8c0-1.4 0-3.2-1.95-3.2S12.8 13.5 12.8 15.1V21H9z"/>'),
    "facebook": ("Facebook", '<path d="M13.5 21v-8h2.7l.4-3.2h-3.1V7.8c0-.9.25-1.5 1.55-1.5H16.7V3.4A22 22 0 0 0 14.3 3.3c-2.4 0-4 1.45-4 4.1v2.4H7.6V13h2.7v8z"/>'),
    "instagram": ("Instagram", '<path d="M12 7.3A4.7 4.7 0 1 0 12 16.7 4.7 4.7 0 0 0 12 7.3zm0 7.7a3 3 0 1 1 0-6 3 3 0 0 1 0 6zm4.9-8.95a1.1 1.1 0 1 1 0 2.2 1.1 1.1 0 0 1 0-2.2zM12 4.6c2.4 0 2.7 0 3.65.05 2.45.1 3.6 1.27 3.7 3.7.05.95.05 1.25.05 3.65s0 2.7-.05 3.65c-.1 2.43-1.25 3.6-3.7 3.7-.95.05-1.24.05-3.65.05s-2.7 0-3.65-.05c-2.46-.1-3.6-1.28-3.7-3.7C4.6 14.7 4.6 14.4 4.6 12s0-2.7.05-3.65c.1-2.43 1.25-3.6 3.7-3.7C9.3 4.6 9.6 4.6 12 4.6zM12 3c-2.45 0-2.75 0-3.7.05C5 3.2 3.2 5 3.05 8.3 3 9.25 3 9.55 3 12s0 2.75.05 3.7C3.2 19 5 20.8 8.3 20.95c.95.05 1.25.05 3.7.05s2.75 0 3.7-.05c3.3-.15 5.1-1.95 5.25-5.25.05-.95.05-1.25.05-3.7s0-2.75-.05-3.7C20.8 5 19 3.2 15.7 3.05 14.75 3 14.45 3 12 3z"/>'),
    "x": ("X", '<path d="M17.75 3h3.07l-6.7 7.65L22 21h-6.17l-4.83-6.3L5.47 21H2.4l7.17-8.18L2 3h6.33l4.37 5.77zm-1.08 16.17h1.7L7.4 4.73H5.58z"/>'),
    "youtube": ("YouTube", '<path d="M21.6 7.2a2.5 2.5 0 0 0-1.76-1.77C18.27 5 12 5 12 5s-6.27 0-7.84.43A2.5 2.5 0 0 0 2.4 7.2 26 26 0 0 0 2 12a26 26 0 0 0 .4 4.8 2.5 2.5 0 0 0 1.76 1.77C5.73 19 12 19 12 19s6.27 0 7.84-.43a2.5 2.5 0 0 0 1.76-1.77A26 26 0 0 0 22 12a26 26 0 0 0-.4-4.8zM10 15V9l5.2 3z"/>'),
    "tiktok": ("TikTok", '<path d="M16.6 3h-3.1v12.2a2.7 2.7 0 1 1-2.7-2.7c.27 0 .53.04.78.11V9.45a5.8 5.8 0 1 0 5.02 5.75V9.1A7.4 7.4 0 0 0 21 10.5V7.4a4.4 4.4 0 0 1-4.4-4.4z"/>'),
}
SOC_START, SOC_END = "<!-- SOCIAL_START -->", "<!-- SOCIAL_END -->"


def social_block():
    path = os.path.join(ROOT, "content", "settings.yml")
    social = (yaml.safe_load(open(path, encoding="utf-8")) or {}).get("social", {}) if os.path.exists(path) else {}
    links = []
    for key, (label, svg) in ICONS.items():
        url = (social.get(key) or "").strip()
        if url:
            links.append(f'<a href="{html.escape(url)}" target="_blank" rel="noopener" aria-label="{label}"><svg viewBox="0 0 24 24" width="17" height="17" fill="#9AA6B6">{svg}</svg></a>')
    inner = f'<div class="social">{"".join(links)}</div>' if links else ""
    return f"{SOC_START}{inner}{SOC_END}"


def asset_version():
    import hashlib
    h = hashlib.md5()
    for f in ("css/style.css", "js/main.js"):
        h.update(open(os.path.join(ROOT, f), "rb").read())
    return h.hexdigest()[:8]


def bust(s, v):
    """Add ?v=<hash> to CSS/JS links so browsers load the latest version after each change."""
    s = re.sub(r'(css/style\.css)(\?v=\w+)?', rf'\1?v={v}', s)
    return re.sub(r'(js/main\.js)(\?v=\w+)?', rf'\1?v={v}', s)


def build():
    global ASSET_V
    posts = load_posts()
    v = ASSET_V = asset_version()

    # Update the homepage first (social links + latest news), then copy its header/footer.
    src = bust(open(INDEX, encoding="utf-8").read(), v)
    src = re.sub(re.escape(SOC_START) + r".*?" + re.escape(SOC_END), social_block(), src, flags=re.S)
    latest = "\n      ".join(card(p) for p in posts[:3])
    src = re.sub(re.escape(START) + r".*?" + re.escape(END),
                 f"{START}\n      {latest}\n      {END}", src, flags=re.S)
    open(INDEX, "w", encoding="utf-8").write(src)

    header, footer, head_links = shared_parts()

    if os.path.isdir(BLOG_DIR):
        shutil.rmtree(BLOG_DIR)
    os.makedirs(BLOG_DIR)

    cards = "\n      ".join(card(p) for p in posts) or '<p class="lead">No articles yet. Check back soon.</p>'
    listing = f"""<section class="page-hero">
  <div class="wrap">
    <p class="eyebrow">Blog</p>
    <h1>News &amp; <em>articles</em></h1>
    <p class="lead">Company news, product updates and practical insight on automation, telecoms, payments and software.</p>
  </div>
</section>
<section class="section section-tight">
  <div class="wrap">
    <div class="post-grid">
      {cards}
    </div>
  </div>
</section>"""
    open(os.path.join(BLOG_DIR, "index.html"), "w", encoding="utf-8").write(
        page("Blog | DBS Group", "News, product updates and articles from DBS Group.",
             f"{SITE}/blog/", head_links, header, footer, listing))

    for i, p in enumerate(posts):
        e = html.escape
        newer = posts[i - 1] if i > 0 else None
        older = posts[i + 1] if i + 1 < len(posts) else None
        nav = '<nav class="post-nav">'
        nav += f'<a href="/blog/{older["slug"]}/"><small>← Older</small>{e(older["title"])}</a>' if older else "<span></span>"
        nav += f'<a class="post-nav-next" href="/blog/{newer["slug"]}/"><small>Newer →</small>{e(newer["title"])}</a>' if newer else "<span></span>"
        nav += "</nav>"
        body = f"""<article class="post">
  <div class="wrap wrap-narrow">
    <a href="/blog/" class="back-link">← All articles</a>
    <p class="eyebrow">{e(p['category'])} · <time datetime="{p['date'].isoformat()}">{fmt(p['date'])}</time></p>
    <h1>{e(p['title'])}</h1>
    <p class="post-excerpt">{e(p['excerpt'])}</p>
    <div class="prose">
{p['body']}
    </div>
    {nav}
  </div>
</article>"""
        d = os.path.join(BLOG_DIR, p["slug"])
        os.makedirs(d)
        open(os.path.join(d, "index.html"), "w", encoding="utf-8").write(
            page(f"{p['title']} | DBS Group", p["excerpt"], f"{SITE}/blog/{p['slug']}/",
                 head_links, header, footer, body, "article"))

    # Sitemap
    urls = [f"{SITE}/", f"{SITE}/blog/"] + [f"{SITE}/blog/{p['slug']}/" for p in posts]
    sm = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    sm += "".join(f"  <url><loc>{u}</loc></url>\n" for u in urls) + "</urlset>\n"
    open(os.path.join(ROOT, "sitemap.xml"), "w", encoding="utf-8").write(sm)

    print(f"Built {len(posts)} posts")


if __name__ == "__main__":
    build()
