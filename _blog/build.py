#!/usr/bin/env python3
"""Build the per-app blogs from the post sources in _blog/posts/<app>/.

    python3 _blog/build.py            # build every app
    python3 _blog/build.py canada     # build one app

For each app this writes, from scratch every time:
  - one page per post        <blog_dir>/<slug>/index.html
  - the app's blog page      <blog_dir>/index.html
  - the app's RSS feed       <blog_dir>/feed.xml
and updates, between marker comments:
  - sitemap.xml              <!-- blog:<app>:start --> ... <!-- blog:<app>:end -->
  - the app's landing page   <!-- blog-latest:start --> ... <!-- blog-latest:end -->

The nav, footer and launch state (is-prelaunch / is-live) are copied from the
app's landing page, so the blog always matches it. Cover images are made by
_blog/covers.js. Only the standard library is used. This folder starts with
an underscore, so GitHub Pages (Jekyll) does not publish it.

Post source format (_blog/posts/<app>/<slug>.html):

    ---
    title: Headline shown on the page (H1)
    seo_title: Shorter title for search results (<= ~60 chars)
    description: Meta description (~150 chars), also the card excerpt
    category: Test prep        (one of the app's categories in APPS below)
    kicker: TEST FORMAT        (optional label above the title; defaults to the category)
    date: 2026-11-24
    updated: 2026-11-24
    cover_line: Short text for the cover card (optional; defaults to title)
    related: other-slug, another-slug
    ---
    <div class="post-tldr"><p><strong>In short:</strong> ...</p></div>
    <p>Body HTML. Put <!-- cta --> where the mid-article app box goes.</p>
    <!-- faq -->
    Q: Question?
    A: Answer.
"""
import html
import json
import math
import os
import re
import sys
from datetime import date, datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = "https://macwanapps.com"
AUTHOR = {"@type": "Person", "@id": f"{SITE}/profile/#person", "name": "Jobin Macwan",
          "url": f"{SITE}/profile/"}
PUBLISHER = {"@type": "Organization", "@id": f"{SITE}/#org", "name": "Macwan Apps",
             "logo": {"@type": "ImageObject", "url": f"{SITE}/images/ma-apple-touch-icon.png"}}

APPS = {
    "canada": {
        "name": "Canadian Citizenship Test Ace",
        "landing": "apps/canada-citizenship/en/index.html",
        "landing_url": "/apps/canada-citizenship/en/",
        "blog_dir": "apps/canada-citizenship/en/blog",
        "lang": "en-CA",
        "locale": "en_CA",
        "itunes_id": "6806622124",
        # pt/ct are App Store Connect campaign tokens: downloads from the blog show up as "web-en-blog".
        "store_url": "https://apps.apple.com/ca/app/id6806622124?pt=128156141&ct=web-en-blog&mt=8",
        "blog_title": "Canadian Citizenship Blog",
        "short_name": "Test Ace",
        "hub_title": "Canadian Citizenship Blog: Test, Ceremony and Study Tips",
        "hub_h1": "The Canadian citizenship blog",
        "hub_subtitle": "Test tips, help with <em>Discover Canada</em>, the interview, the ceremony and "
                        "the oath, and life as a new Canadian, from the maker of Canadian Citizenship Test Ace.",
        "hub_note": "Every fact links to its official source on canada.ca. This is an independent blog, "
                    "not affiliated with the Government of Canada or IRCC.",
        "hub_description": "The Canadian citizenship blog: test tips, Discover Canada study help, the "
                           "interview, ceremony and oath, each checked against canada.ca.",
        "categories": ["Test prep", "Discover Canada", "Citizenship process", "Life in Canada", "App news"],
        # Pillar pages the blog points to first: they cover the whole subject, posts go deep on one question.
        "start_here": [
            ("/apps/canada-citizenship/en/test-guide/", "The Canadian citizenship test in 2026",
             "How the test works, start to finish: format, pass mark, online rules, results."),
            ("/apps/canada-citizenship/en/practice-test/", "Free practice test",
             "20 questions from Discover Canada, scored like the real test. No sign-up."),
        ],
        "nav_links": [
            ("/apps/canada-citizenship/en/", "The app", ""),
            ("/apps/canada-citizenship/en/practice-test/", "Practice test", ""),
            ("/apps/canada-citizenship/en/blog/", "Blog", "blog"),
            ("/apps/canada-citizenship/en/support/", "Support", ""),
            ("/apps/canada-citizenship/fr/", "Français", ' hreflang="fr-CA" lang="fr"'),
        ],
        "nav_cta": ("https://apps.apple.com/ca/app/id6806622124?pt=128156141&ct=web-en-blog-nav&mt=8", "Get the app"),
        "cta_title": "Practise for the real test with Canadian Citizenship Test Ace",
        "cta_text": "800+ questions checked against <em>Discover Canada</em>, lessons you can read or "
                    "listen to in English or French, and 20-question mock exams with the real pass mark.",
        "mid_cta": "Want to check where you stand? <strong>Canadian Citizenship Test Ace</strong> has "
                   "20-question mock exams with the real pass mark and a question set for every "
                   "province and territory.",
        "legacy": {},
        "latest_heading": "From the blog",
    },
    "walkfirst": {
        "name": "WalkFirst",
        "landing": "apps/walkfirst/index.html",
        "landing_url": "/apps/walkfirst/",
        "blog_dir": "apps/walkfirst/blog",
        "lang": "en",
        "locale": "en_US",
        "itunes_id": "6758828207",
        "store_url": "https://apps.apple.com/app/walkfirst-earn-screen-time/id6758828207",
        "blog_title": "WalkFirst Blog",
        "short_name": "WalkFirst",
        "hub_title": "WalkFirst Blog: Walking, Steps and Screen Time",
        "categories": ["Walking", "Weight loss", "Screen time", "Habits", "App news"],
        "start_here": [],
        "hub_h1": "Walking, screen time and habits that stick",
        "hub_subtitle": "Honest, research-backed writing on walking, steps and getting your time back "
                        "from your phone, from the developer of WalkFirst.",
        "hub_note": "Every post answers a question people genuinely ask. When a claim needs research "
                    "behind it, the post links to it. This blog is general information, not medical advice.",
        "hub_description": "The WalkFirst blog: research-backed posts on walking, daily steps, screen "
                           "time and habits, from the developer of the WalkFirst app.",
        "nav_links": [
            ("/apps/walkfirst/", "The app", ""),
            ("/apps/walkfirst/blog/", "Blog", "blog"),
            ("/support/", "Support", ""),
        ],
        "nav_cta": ("https://apps.apple.com/app/walkfirst-earn-screen-time/id6758828207", "Get WalkFirst"),
        "cta_title": "WalkFirst turns your steps into screen time",
        "cta_text": "Your most distracting apps stay locked until you walk. Hit part of your step goal "
                    "to earn minutes, or all of it to unlock them for the day.",
        "mid_cta": "Struggling to fit the walk in? <strong>WalkFirst</strong> keeps your most "
                   "distracting apps locked until you've walked, so the walk comes first.",
        # Older posts that live at /blog/<slug>/ keep their URLs; the hub lists them too.
        "legacy": {"block-instagram-iphone": "Screen time", "friction-habit-hack": "Habits",
                   "morning-routine-you-will-keep": "Habits", "phone-in-bed-morning": "Screen time",
                   "steps-per-day-by-goal": "Walking", "stop-doomscrolling": "Screen time",
                   "healthy-daily-schedule-desk-job": "Habits",
                   "how-much-screen-time-is-too-much": "Screen time",
                   "walking-30-minutes-a-day": "Walking", "10000-steps-myth": "Walking",
                   "introducing-walkfirst": "App news"},
        "latest_heading": "From the WalkFirst blog",
    },
}

esc = html.escape


def read(path):
    with open(os.path.join(ROOT, path), encoding="utf-8") as f:
        return f.read()


def write(path, text):
    full = os.path.join(ROOT, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w", encoding="utf-8") as f:
        f.write(text)


def fmt_date(d):
    return f"{d.strftime('%B')} {d.day}, {d.year}"


def strip_tags(s):
    return html.unescape(re.sub(r"<[^>]+>", "", s))


def parse_post(app, path):
    raw = open(path, encoding="utf-8").read()
    m = re.match(r"---\n(.*?)\n---\n(.*)$", raw, re.S)
    if not m:
        sys.exit(f"{path}: missing front matter")
    meta = {}
    for line in m.group(1).splitlines():
        if line.strip():
            k, _, v = line.partition(":")
            meta[k.strip()] = v.strip()
    body = m.group(2)
    faq = []
    if "<!-- faq -->" in body:
        body, faq_raw = body.split("<!-- faq -->", 1)
        q = None
        for line in faq_raw.splitlines():
            if line.startswith("Q:"):
                q = line[2:].strip()
            elif line.startswith("A:") and q:
                faq.append((q, line[2:].strip()))
                q = None
    for key in ("title", "description", "category", "date"):
        if key not in meta:
            sys.exit(f"{path}: front matter needs '{key}'")
    slug = os.path.splitext(os.path.basename(path))[0]
    if meta["category"] not in APPS[app]["categories"]:
        sys.exit(f"{path}: category must be one of {APPS[app]['categories']}")
    words = len(strip_tags(body).split()) + sum(len(strip_tags(q + " " + a).split()) for q, a in faq)
    cfg = APPS[app]
    return {
        "slug": slug,
        "title": meta["title"],
        "seo_title": meta.get("seo_title", meta["title"]),
        "description": meta["description"],
        "kicker": meta.get("kicker", meta["category"]).upper(),
        "category": meta["category"],
        "date": date.fromisoformat(meta["date"]),
        "updated": date.fromisoformat(meta.get("updated", meta["date"])),
        "related": [s.strip() for s in meta.get("related", "").split(",") if s.strip()],
        "body": body.strip(),
        "faq": faq,
        "minutes": max(1, math.ceil(words / 220)),
        "url": f"/{cfg['blog_dir']}/{slug}/",
        "image": f"/images/blog/{app}-{slug}.png",
        "legacy": False,
    }


def parse_legacy(slug, category):
    s = read(f"blog/{slug}/index.html")
    title = strip_tags(re.search(r"<h1[^>]*>(.*?)</h1>", s, re.S).group(1)).strip()
    desc = html.unescape(re.search(r'<meta name="description" content="([^"]*)"', s).group(1))
    img = re.search(r'<meta property="og:image" content="https://macwanapps.com([^"]*)"', s)
    pub = re.search(r'"datePublished":\s*"([\d-]+)"', s).group(1)
    kicker = re.search(r'class="row-kicker[^"]*">([^<]*)<', s)
    meta = re.search(r'(\d+) min read', s)
    return {"slug": slug, "title": title, "description": desc, "kicker": kicker.group(1) if kicker else "",
            "category": category,
            "date": date.fromisoformat(pub), "updated": date.fromisoformat(pub),
            "minutes": int(meta.group(1)) if meta else 4, "url": f"/blog/{slug}/",
            "image": img.group(1) if img else "", "legacy": True}


def landing_parts(cfg):
    """Return (body_class, nav_brand_html, footer_and_after_html) from the landing page."""
    s = read(cfg["landing"])
    body_class = re.search(r'<body class="([^"]*)"', s).group(1)
    if "is-prelaunch" not in body_class.split() and "is-live" not in body_class.split():
        body_class += " is-live"  # an app with no launch switch is already on the App Store
    brand = re.search(r'<span class="brand-group">.*?class="brand".*?</a>\s*</span>', s, re.S).group(0)
    tail = s[s.index("</main>") + len("</main>"):]
    blog_url = f"/{cfg['blog_dir']}/"
    tail = tail.replace('<a href="/blog/">Blog</a>', f'<a href="{blog_url}">Blog</a>')
    return body_class, brand, tail


def nav_html(cfg, brand, active):
    links = []
    for href, label, extra in cfg["nav_links"]:
        cls = ' class="active" aria-current="page"' if extra == "blog" and active == "hub" else \
              ' class="active"' if extra == "blog" else ""
        attrs = extra if extra != "blog" else ""
        links.append(f'      <a href="{href}"{cls}{attrs}>{label}</a>')
    cta_href, cta_label = cfg["nav_cta"]
    links.append(f'      <a href="{esc(cta_href)}" class="nav-cta" data-ph-event="blog_cta_click" '
                 f'data-ph-label="nav">{cta_label}</a>')
    return f"""<nav>
  <div class="nav-inner">
    {brand}
    <button class="hamburger" onclick="this.classList.toggle('open');document.querySelector('.nav-links').classList.toggle('open');" aria-label="Menu">
      <span></span><span></span><span></span>
    </button>
    <div class="nav-links">
{chr(10).join(links)}
    </div>
  </div>
</nav>"""


def store_buttons(cfg, label):
    """Prelaunch pill + live badge; the landing's body class decides which one shows."""
    return (f'<span class="coming-soon-pill store-prelaunch">Coming soon to the App Store</span>'
            f'<a href="{esc(cfg["store_url"])}" class="appstore-badge-link store-live" '
            f'data-ph-event="appstore_badge_click" data-ph-label="{label}">'
            f'<img src="/images/app-store-badge.svg" alt="Download on the App Store" width="150" height="50"></a>')


def head(cfg, *, title, description, canonical, og_type, image, jsonld, feed_url):
    img_meta = ""
    if image:
        img_meta = (f'<meta property="og:image" content="{SITE}{image}">\n'
                    f'<meta property="og:image:width" content="1200">\n'
                    f'<meta property="og:image:height" content="630">\n'
                    f'<meta name="twitter:image" content="{SITE}{image}">\n')
    ld = "\n".join(f'<script type="application/ld+json">\n{json.dumps(j, indent=2, ensure_ascii=False)}\n</script>'
                   for j in jsonld)
    return f"""<!DOCTYPE html>
<html lang="{cfg['lang']}">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="apple-itunes-app" content="app-id={cfg['itunes_id']}">
<title>{esc(title)}</title>
<meta name="description" content="{esc(description)}">
<meta name="robots" content="max-image-preview:large">
<link rel="canonical" href="{SITE}{canonical}">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(description)}">
<meta name="twitter:card" content="summary_large_image">
<meta property="og:site_name" content="Macwan Apps">
<meta property="og:locale" content="{cfg['locale']}">
<meta property="og:type" content="{og_type}">
<meta property="og:url" content="{SITE}{canonical}">
{img_meta}<link rel="alternate" type="application/rss+xml" title="{esc(cfg['blog_title'])}" href="{feed_url}">
<link rel="icon" type="image/png" sizes="32x32" href="/images/ma-favicon-32x32.png">
<link rel="icon" type="image/png" sizes="16x16" href="/images/ma-favicon-16x16.png">
<link rel="apple-touch-icon" sizes="180x180" href="/images/ma-apple-touch-icon.png">
<link rel="preload" as="font" type="font/woff2" href="/fonts/inter-600.woff2" crossorigin>
<link rel="preload" as="font" type="font/woff2" href="/fonts/inter-400.woff2" crossorigin>
<link rel="stylesheet" href="/css/site.css">
<noscript><style>.fade-in, .fade-in-left {{ opacity: 1; transform: none; filter: none; }}</style></noscript>
{ld}
<script src="/js/analytics.js" defer></script>
</head>"""


def breadcrumb_ld(items):
    return {"@context": "https://schema.org", "@type": "BreadcrumbList",
            "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": n, "item": SITE + u}
                                for i, (n, u) in enumerate(items)]}


def render_post(app, cfg, post, posts, parts):
    body_class, brand, tail = parts
    blog_url = f"/{cfg['blog_dir']}/"
    feed_url = blog_url + "feed.xml"
    crumbs = [("Home", "/"), (cfg["name"], cfg["landing_url"]), ("Blog", blog_url), (post["title"], post["url"])]
    jsonld = [
        {"@context": "https://schema.org", "@type": "BlogPosting",
         "mainEntityOfPage": {"@type": "WebPage", "@id": SITE + post["url"]},
         "headline": post["title"], "description": post["description"],
         "image": SITE + post["image"], "datePublished": post["date"].isoformat(),
         "dateModified": post["updated"].isoformat(), "inLanguage": cfg["lang"],
         "articleSection": post["category"],
         "url": SITE + post["url"], "author": AUTHOR, "publisher": PUBLISHER,
         "isPartOf": {"@type": "Blog", "@id": SITE + blog_url, "name": cfg["blog_title"]}},
        breadcrumb_ld(crumbs),
    ]
    if post["faq"]:
        jsonld.append({"@context": "https://schema.org", "@type": "FAQPage",
                       "mainEntity": [{"@type": "Question", "name": strip_tags(q),
                                       "acceptedAnswer": {"@type": "Answer", "text": strip_tags(a)}}
                                      for q, a in post["faq"]]})
    mid = (f'<aside class="post-inline-cta" aria-label="{esc(cfg["name"])}">'
           f'<p>{cfg["mid_cta"]}</p><a href="{cfg["landing_url"]}" data-ph-event="blog_cta_click" '
           f'data-ph-label="inline">See the app &rarr;</a></aside>')
    body = post["body"].replace("<!-- cta -->", mid)
    faq_html = ""
    if post["faq"]:
        items = "\n".join(f"""  <details class="faq-item">
    <summary>{q}</summary>
    <div class="faq-answer">{a}</div>
  </details>""" for q, a in post["faq"])
        faq_html = f"\n  <h2>Frequently asked questions</h2>\n{items}\n"
    updated = ""
    if post["updated"] != post["date"]:
        updated = f'\n    <span>&middot;</span>\n    <span>Updated {fmt_date(post["updated"])}</span>'
    # Read next: explicit related posts first, then the newest others.
    by_slug = {p["slug"]: p for p in posts}
    nxt = [by_slug[s] for s in post["related"] if s in by_slug and s != post["slug"]]
    nxt += [p for p in posts if p["slug"] != post["slug"] and p not in nxt]
    cards = "\n".join(f"""  <a href="{p['url']}">
    <img src="{p['image']}" alt="" width="132" height="74" loading="lazy">
    <div>
      <h3>{esc(p['title'])}</h3>
      <span class="post-date">{fmt_date(p['date'])}</span>
    </div>
  </a>""" for p in nxt[:2])
    return f"""{head(cfg, title=page_title(post['seo_title'], cfg), description=post['description'],
                 canonical=post['url'], og_type='article', image=post['image'], jsonld=jsonld, feed_url=feed_url)}
<body class="{body_class} blog-page">
<a class="skip-link" href="#main">Skip to content</a>

{nav_html(cfg, brand, 'post')}

<main id="main">

<article>
<header class="hero hero-sub post-hero">
  <div class="post-breadcrumb hero-anim stagger-1"><a href="{cfg['landing_url']}">{esc(cfg['name'])}</a><span aria-hidden="true">/</span><a href="{blog_url}">Blog</a></div>
  <div class="row-kicker hero-anim stagger-1">{esc(post['kicker'])}</div>
  <h1 class="hero-anim stagger-2">{esc(post['title'])}</h1>
  <div class="post-hero-meta hero-anim stagger-3">
    <span><time datetime="{post['date'].isoformat()}">{fmt_date(post['date'])}</time></span>
    <span>&middot;</span>
    <span><a href="/profile/" rel="author">Jobin Macwan</a></span>
    <span>&middot;</span>
    <span>{post['minutes']} min read</span>{updated}
  </div>
</header>

<figure class="post-cover-figure is-card">
  <img src="{post['image']}" alt="{esc(post['title'])}" width="1200" height="630" fetchpriority="high">
</figure>

<div class="prose-section">

{body}
{faq_html}
  <div class="post-cta">
    <p><strong>{cfg['cta_title']}</strong><br>{cfg['cta_text']}</p>
    <div class="post-cta-actions">{store_buttons(cfg, 'post-end')}<a href="{cfg['landing_url']}" class="btn-secondary" data-ph-event="blog_cta_click" data-ph-label="post-end">Learn more</a></div>
  </div>

  <div class="author-card">
    <div class="hero-avatar">JM</div>
    <div>
      <div class="author-name">Jobin Macwan</div>
      <p>Indie iOS developer and founder of Macwan Apps. I build {esc(cfg['name'])} and write these guides from official and published sources. <a href="/profile/">More about me</a></p>
    </div>
  </div>

</div>
</article>

<section class="read-next" aria-label="Read next">
  <div class="all-posts-label">Read next</div>
{cards}
  <p class="read-next-all"><a href="{blog_url}">All posts &rarr;</a></p>
</section>

</main>
{tail}"""


def page_title(title, cfg):
    """Keep <title> within what search results show (~60 characters)."""
    full = f"{title} | {cfg['short_name']}"
    return full if len(full) <= 62 else title


def card(p, cover_loading="lazy"):
    img = f'<img class="post-cover" src="{p["image"]}" alt="" width="1200" height="630" loading="{cover_loading}">' \
        if p["image"] else ""
    return f"""    <a href="{p['url']}" class="post-card fade-in" data-cat="{esc(p['category'])}">
      {img}
      <div class="post-card-body">
        <div class="row-kicker">{esc(p['category'])}</div>
        <h2>{esc(p['title'])}</h2>
        <p>{esc(p['description'])}</p>
        <div class="row-meta"><time datetime="{p['date'].isoformat()}">{fmt_date(p['date'])}</time> &middot; {p['minutes']} min read</div>
      </div>
    </a>"""


def render_hub(app, cfg, entries, parts):
    body_class, brand, tail = parts
    blog_url = f"/{cfg['blog_dir']}/"
    feed_url = blog_url + "feed.xml"
    jsonld = [
        {"@context": "https://schema.org", "@type": "Blog", "@id": SITE + blog_url, "url": SITE + blog_url,
         "name": cfg["blog_title"], "description": cfg["hub_description"], "inLanguage": cfg["lang"],
         "publisher": PUBLISHER,
         "blogPost": [{"@type": "BlogPosting", "headline": p["title"], "url": SITE + p["url"],
                       "datePublished": p["date"].isoformat()} for p in entries]},
        breadcrumb_ld([("Home", "/"), (cfg["name"], cfg["landing_url"]), ("Blog", blog_url)]),
    ]
    cards = "\n".join(card(p, "eager" if i < 3 else "lazy") for i, p in enumerate(entries))
    start = ""
    if cfg["start_here"]:
        links = "\n".join(f'''    <a href="{u}" class="start-here-link"><strong>{esc(t)}</strong><span>{esc(d)}</span></a>'''
                          for u, t, d in cfg["start_here"])
        start = f'''
  <div class="start-here fade-in" aria-label="Start here">
    <div class="all-posts-label">Start here</div>
    <div class="start-here-grid">
{links}
    </div>
  </div>
'''
    used = [c for c in cfg["categories"] if any(p["category"] == c for p in entries)]
    filters = ""
    if len(used) > 1:
        chips = "".join(f'<button type="button" class="blog-chip" data-cat="{esc(c)}" aria-pressed="false">{esc(c)}</button>'
                        for c in used)
        filters = f'''
  <div class="blog-filters" role="group" aria-label="Filter posts by topic">
    <button type="button" class="blog-chip" data-cat="" aria-pressed="true">All</button>{chips}
  </div>
  <script>
  document.querySelectorAll('.blog-chip').forEach(function (b) {{
    b.addEventListener('click', function () {{
      var cat = b.dataset.cat;
      document.querySelectorAll('.blog-chip').forEach(function (x) {{ x.setAttribute('aria-pressed', String(x === b)); }});
      document.querySelectorAll('.post-grid .post-card').forEach(function (c) {{ c.hidden = !!cat && c.dataset.cat !== cat; }});
    }});
  }});
  </script>'''
    return f"""{head(cfg, title=cfg['hub_title'], description=cfg['hub_description'],
                 canonical=blog_url, og_type='website', image=entries[0]['image'] if entries else '',
                 jsonld=jsonld, feed_url=feed_url)}
<body class="{body_class} blog-page">
<a class="skip-link" href="#main">Skip to content</a>

{nav_html(cfg, brand, 'hub')}

<main id="main">

<section class="hero hero-sub blog-head">
  <div class="post-breadcrumb hero-anim stagger-1"><a href="{cfg['landing_url']}">{esc(cfg['name'])}</a><span aria-hidden="true">/</span><span>Blog</span></div>
  <h1 class="hero-anim stagger-1">{esc(cfg['hub_h1'])}</h1>
  <p class="subtitle hero-anim stagger-2">{cfg['hub_subtitle']}</p>
  <p class="blog-note hero-anim stagger-2">{cfg['hub_note']}</p>
</section>

<section class="post-list" aria-label="All posts">{start}{filters}
  <div class="post-grid">
{cards}
  </div>

  <div class="blog-subscribe fade-in">
    <h2>Get new posts</h2>
    <p>New posts as they're published, straight to your feed reader.</p>
    <a href="{feed_url}" class="btn-primary subscribe-btn">Subscribe via RSS</a>
  </div>
</section>

</main>
{tail}"""


def rss_date(d):
    return datetime(d.year, d.month, d.day, 9, 0, tzinfo=timezone.utc).strftime("%a, %d %b %Y %H:%M:%S +0000")


def render_feed(cfg, entries):
    blog_url = f"{SITE}/{cfg['blog_dir']}/"
    items = "\n".join(f"""  <item>
    <title>{esc(p['title'])}</title>
    <link>{SITE}{p['url']}</link>
    <guid>{SITE}{p['url']}</guid>
    <pubDate>{rss_date(p['date'])}</pubDate>
    <description>{esc(p['description'])}</description>
  </item>""" for p in entries)
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
<channel>
  <title>{esc(cfg['blog_title'])}</title>
  <link>{blog_url}</link>
  <description>{esc(cfg['hub_description'])}</description>
  <language>{cfg['lang'].lower()}</language>
  <atom:link href="{blog_url}feed.xml" rel="self" type="application/rss+xml"/>
{items}
</channel>
</rss>
"""


def replace_block(text, start, end, new, where_missing=None):
    if start in text:
        a = text.index(start)
        b = text.index(end, a) + len(end)
        return text[:a] + new + text[b:]
    if where_missing is None:
        sys.exit(f"marker {start} not found")
    i = text.index(where_missing)
    return text[:i] + new + "\n" + text[i:]


def update_sitemap(app, cfg, posts):
    s = read("sitemap.xml")
    newest = max([p["updated"] for p in posts], default=date.today())
    urls = [(f"/{cfg['blog_dir']}/", newest, "weekly", "0.8")]
    urls += [(p["url"], p["updated"], "monthly", "0.7") for p in posts]
    block = f"  <!-- blog:{app}:start -->\n" + "".join(f"""  <url>
    <loc>{SITE}{u}</loc>
    <lastmod>{d.isoformat()}</lastmod>
    <changefreq>{c}</changefreq>
    <priority>{pr}</priority>
  </url>
""" for u, d, c, pr in urls) + f"  <!-- blog:{app}:end -->"
    s = replace_block(s, f"  <!-- blog:{app}:start -->", f"<!-- blog:{app}:end -->", block, "</urlset>")
    write("sitemap.xml", s)


def update_landing(cfg, entries):
    s = read(cfg["landing"])
    start, end = "<!-- blog-latest:start -->", "<!-- blog-latest:end -->"
    if start not in s:
        return
    blog_url = f"/{cfg['blog_dir']}/"
    cards = "\n".join(card(p) for p in entries[:3])
    block = f"""{start}
<section class="post-list landing-blog" id="blog" aria-labelledby="landing-blog-title">
  <div class="section-label fade-in">From the blog</div>
  <h2 class="section-title fade-in delay-1" id="landing-blog-title">{esc(cfg['latest_heading'])}</h2>
  <div class="post-grid">
{cards}
  </div>
  <p class="landing-blog-all fade-in"><a href="{blog_url}" class="btn-secondary">All posts &rarr;</a></p>
</section>
{end}"""
    write(cfg["landing"], replace_block(s, start, end, block))


def build(app):
    cfg = APPS[app]
    src = os.path.join(ROOT, "_blog", "posts", app)
    posts = [parse_post(app, os.path.join(src, f)) for f in sorted(os.listdir(src)) if f.endswith(".html")] \
        if os.path.isdir(src) else []
    posts.sort(key=lambda p: (p["date"], p["slug"]), reverse=True)
    parts = landing_parts(cfg)
    for p in posts:
        write(f"{cfg['blog_dir']}/{p['slug']}/index.html", render_post(app, cfg, p, posts, parts))
    entries = posts + [parse_legacy(s, c) for s, c in cfg["legacy"].items()]
    entries.sort(key=lambda p: (p["date"], not p["legacy"]), reverse=True)
    write(f"{cfg['blog_dir']}/index.html", render_hub(app, cfg, entries, parts))
    write(f"{cfg['blog_dir']}/feed.xml", render_feed(cfg, entries))
    update_sitemap(app, cfg, posts)
    update_landing(cfg, entries)
    print(f"{app}: {len(posts)} posts, {len(entries)} on the blog page")


if __name__ == "__main__":
    for a in (sys.argv[1:] or APPS):
        build(a)
