# Canada Citizenship 2027 — launch-day switch

The pages are built in a "prelaunch" state. When Apple approves the app and
it is live at https://apps.apple.com/ca/app/id6806622124, do these, then
commit and push:

1. `apps/canada-citizenship/index.html` and `fr/index.html`: on `<body>`,
   replace `is-prelaunch` with `is-live`.
2. `index.html` (homepage): the Canada Citizenship app card and the hero
   chip both carry `is-prelaunch` — replace with `is-live`.
3. OG cards: rename `images/canada-citizenship-og-card-live.png` over
   `images/canada-citizenship-og-card.png`, and the `-fr-live` one over
   `-fr`. (The live versions carry the App Store badge instead of
   "Coming soon".)
4. In both landing pages' MobileApplication JSON-LD, add
   `"installUrl": "https://apps.apple.com/ca/app/id6806622124"`.
5. Update `<lastmod>` for the changed pages in `sitemap.xml`.

Everything else (badge links, Smart App Banner, FAQ) is already in place
and only hidden by the CSS switch.
