# Keyword research: how topics are chosen

Last run: 25 Nov 2026, with `python3 _blog/keywords.py canada` (Google
autocomplete, Canada) and `python3 _blog/keywords.py walkfirst` (US).
About 1,200 Canada phrases and 2,400 WalkFirst phrases came back.

## Method

1. **Autocomplete expansion.** For each seed ("canadian citizenship test",
   "walking for weight loss", ...) ask Google for completions of the seed,
   the seed + each letter a-z, and question forms ("how ...", "can ...").
   A phrase that appears for many prompts and near the top is one people
   type a lot. Autocomplete shows the exact wording people use, but not
   volumes.
2. **Cluster.** Group phrases by intent (ceremony, interview, oath, weight
   loss, app blockers, ...). Clusters with the most and highest-ranked
   phrases go first. One post per intent, so pages don't compete with each
   other.
3. **Check the competition.** Look at who ranks now. Government pages and
   Wikipedia own head terms ("canadian citizenship test"); specific
   questions ("what to bring to citizenship ceremony") are winnable.
4. **Match a page type to the intent.**
   - Pillar pages answer the whole subject: `/en/test-guide/`,
     `/en/practice-test/`.
   - Blog posts go deep on one question and link back to the pillar.
5. **Write to the phrase.** Title and H1 use the searched words; the
   "In short" box answers it in the first 100 words; H2s and FAQs use the
   other phrasings from the same cluster.
6. **Measure and adjust.** Once pages are live, Google Search Console and
   Bing Webmaster Tools show real impressions, clicks and positions. Every
   month: rewrite titles of pages with impressions but few clicks, then
   add posts for queries that show up but have no page yet.

## Canada clusters (biggest first)

| Cluster | Example phrases people type | Page |
|---|---|---|
| Ceremony | how long is the canadian citizenship ceremony; documents required for oath ceremony; citizenship ceremony dress code; virtual citizenship ceremony | `canadian-citizenship-ceremony` (done) |
| Discover Canada | discover canada pdf; discover canada summary; discover canada important dates; discover canada audio | `discover-canada-study-plan` (done); more posts below |
| Practice questions | canadian citizenship test questions and answers pdf 2026; citizenship test canada practice free | `/en/practice-test/` (pillar) |
| Oath | what is the oath to become a canadian citizen; oath king charles; swear or affirm | to write |
| Interview | is there an interview for canadian citizenship; citizenship interview questions; what happens after the interview | to write |
| Online test | can you take the test online; does the test record audio / your screen; how does the test look | `/en/test-guide/` (pillar); a focused post later |
| After the ceremony | what happens after the ceremony; passport after citizenship; citizenship certificate | to write |
| Requirements | who is exempt from the test; age 55; language requirement | to write |
| Hard / fail | is the canadian citizenship test hard; what happens if you fail | `fail-canadian-citizenship-test` (done) |
| Timeline | how long after the test for the oath; test to oath timeline | to write |

## WalkFirst clusters (biggest first)

| Cluster | Example phrases | Page |
|---|---|---|
| Walking for weight loss | walking for weight loss plan; steps a day to lose weight; is walking better than running for weight loss | to write (top priority) |
| Phone addiction | phone addiction symptoms; phone addiction help; does phone addiction cause anxiety | to write |
| App blockers | do app blockers work; app blocker iphone; free app blocker | to write (closest to a download) |
| Steps a day | steps a day for health; average steps a day; does 10k steps count as exercise | older posts cover this; refresh them |
| Stop scrolling | how to stop scrolling on social media; stop scrolling app | `stop-doomscrolling` (older post) |
| Walking after eating | walking after eating benefits; how long after eating should you walk; digestion | `walking-after-eating-blood-sugar` (done) |
| Screen time | screen time iphone; what screen time is healthy | older posts; refresh |

Noise to ignore: TV shows ("walking dead", "screen time" films), memes,
unrelated products.
