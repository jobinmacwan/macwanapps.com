# Per-app blogs

Two app blogs are built from this folder. GitHub Pages does not publish it,
because the name starts with an underscore.

| App | Blog page | Post sources |
|---|---|---|
| Canadian Citizenship Test Ace | `/apps/canada-citizenship/en/blog/` | `_blog/posts/canada/` |
| WalkFirst | `/apps/walkfirst/blog/` | `_blog/posts/walkfirst/` |

WalkFirst's older posts stay at `/blog/<slug>/` (their URLs rank; don't move
them). The WalkFirst blog page lists them alongside the new ones.

## Add a post

1. Write `_blog/posts/<app>/<slug>.html`. Front matter and format are
   described at the top of `build.py`; copy an existing post.
2. `node _blog/covers.js` makes the 1200x630 cover for any post without one.
3. `python3 _blog/build.py` regenerates the post pages, the blog page, the
   RSS feed, the sitemap entries and the "From the blog" block on the landing
   page.
4. Preview: `python3 -m http.server 8000`, then open the blog page.
5. Open a pull request. **Merging it publishes the post.** Nothing goes live
   without Jobin's approval.

Never edit the generated `index.html` / `feed.xml` files under the blog
folders by hand; edit the source and rebuild.

## Rules for every post

- **Answer first.** The `post-tldr` "In short" box answers the title's
  question in 2 to 3 sentences. Search engines and AI answers quote it.
- **Title like a search.** `seo_title` 60 characters or fewer, worded the way
  people type the question. `description` about 140 to 155 characters.
- **800 to 1,200 words**, question-style `<h2>`s, a "Sources" list and 3 to 5
  FAQs at the end.
- **Every fact links to its source.** Canada: canada.ca (IRCC, Discover
  Canada) only. WalkFirst: CDC, WHO, peer-reviewed studies (PubMed).
  No invented statistics. If a fact can't be verified, leave it out.
- **Never imply the app or blog is official.** The Canada app is independent
  of the Government of Canada and IRCC.
- **Health posts are general information, not medical advice.** Say when to
  check with a doctor.
- **Link internally:** 2+ links to related posts, plus the `<!-- cta -->`
  marker for the mid-article app box. The end box and the App Store badge
  are added by the builder.
- **Photos:** the default cover is the generated card. To use a stock photo
  instead, save it as `images/blog/<app>-<slug>.png` (1200x630) and credit the
  photographer in the post.
- Plain, friendly English; Canadian spelling on the Canada blog ("practise"
  as a verb, "licence").

## Schedule

Three posts a week per app, each drafted by a scheduled Claude session as a
pull request for approval:

- Canada: Monday, Wednesday, Friday
- WalkFirst: Tuesday, Thursday, Saturday

Topics come from `_blog/topics.md`. The writer takes the first unchecked
topic, checks it off in the same pull request, and skips anything already
covered.

## Launch day (Canada)

The blog copies the landing page's `is-prelaunch` / `is-live` state. After
the launch switch in `apps/canada-citizenship/LAUNCH.md`, run
`python3 _blog/build.py` so the blog's App Store buttons switch too.
