# Canadian Citizenship Test Ace — launch-day switch

(In French: Test citoyenneté Canada Ace. Until 18 Nov 2026 the pages said
"Canada Citizenship 2027" / "Citoyenneté canadienne 2027"; the names, the
four OG cards and content version 13 were brought up to date that day. Only
the switch below is left, and it waits for Apple's approval: before that the
App Store badge would open a page that does not exist.)

The pages are built in a "prelaunch" state. When Apple approves the app and
it is live at https://apps.apple.com/ca/app/id6806622124, do these, then
commit and push:

1. `apps/canada-citizenship/en/index.html` and `fr/index.html`: on `<body>`,
   replace `is-prelaunch` with `is-live`.
2. `index.html` (homepage): the hero chip reads "Canada Citizenship ·
   Coming soon" and the Canada app card's status is "Coming soon to the App
   Store" (`app-status-soon`). Change both to "Live" / "Live on the App
   Store", as WalkFirst's are, and add the App Store badge to the card.
3. OG cards: rename `images/canada-citizenship-og-card-live.png` over
   `images/canada-citizenship-og-card.png`, and the `-fr-live` one over
   `-fr`. (The live versions carry the App Store badge instead of
   "Coming soon".)
4. In both landing pages' MobileApplication JSON-LD, add
   `"installUrl": "https://apps.apple.com/ca/app/id6806622124"`.
5. Update `<lastmod>` for the changed pages in `sitemap.xml`.

Everything else (badge links, Smart App Banner, FAQ) is already in place
and only hidden by the CSS switch.
