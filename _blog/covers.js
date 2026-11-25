// Make 1200x630 cover cards for blog posts that don't have one yet.
//
//   node _blog/covers.js            # every post missing a cover
//   node _blog/covers.js --force    # redraw them all
//
// Reads _blog/posts/<app>/<slug>.html (cover_line, kicker), writes
// images/blog/<app>-<slug>.png. Uses Playwright's Chromium. A post can use a
// photo instead: drop images/blog/<app>-<slug>.png in by hand (and credit the
// photographer in the post), and this script leaves it alone.
const fs = require('fs');
const path = require('path');
const { chromium } = require('playwright');

const ROOT = path.dirname(__dirname);
const FORCE = process.argv.includes('--force');

const THEMES = {
  canada: {
    brand: 'Canadian Citizenship Test Ace · Blog',
    accent: '#b8202d',
    bg: 'linear-gradient(160deg, #fbe9e7 0%, #fdf6f4 55%, #ffffff 100%)',
    art: 'images/canada-citizenship-beaver-reading.png',
    artWidth: 400,
  },
  walkfirst: {
    brand: 'WalkFirst · Blog',
    accent: '#b45309',
    bg: 'linear-gradient(160deg, #fdecd2 0%, #fff7ec 55%, #ffffff 100%)',
    art: 'images/walkfirst-icon.png',
    artWidth: 300,
  },
};

function frontMatter(file) {
  const raw = fs.readFileSync(file, 'utf8');
  const m = raw.match(/^---\n([\s\S]*?)\n---\n/);
  const meta = {};
  for (const line of m[1].split('\n')) {
    const i = line.indexOf(':');
    if (i > 0) meta[line.slice(0, i).trim()] = line.slice(i + 1).trim();
  }
  return meta;
}

const esc = (s) => s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');

function page(t, meta) {
  const art = 'data:image/png;base64,' + fs.readFileSync(path.join(ROOT, t.art)).toString('base64');
  const font = (w) => 'data:font/woff2;base64,' + fs.readFileSync(path.join(ROOT, `fonts/inter-${w}.woff2`)).toString('base64');
  const line = meta.cover_line || meta.title;
  const size = line.length > 48 ? 62 : 72;
  return `<!doctype html><html><head><style>
@font-face { font-family: Inter; font-weight: 400; src: url(${font(400)}); }
@font-face { font-family: Inter; font-weight: 600; src: url(${font(600)}); }
html, body { margin: 0; width: 1200px; height: 630px; }
body { font-family: Inter, sans-serif; background: ${t.bg}; display: flex; align-items: center;
  box-sizing: border-box; padding: 0 72px; gap: 56px; position: relative; overflow: hidden; }
body::before { content: ''; position: absolute; inset: 0;
  background-image: radial-gradient(rgba(0,0,0,0.05) 1.5px, transparent 1.5px); background-size: 26px 26px; }
.text { position: relative; flex: 1; }
.kicker { color: ${t.accent}; font-weight: 600; font-size: 24px; letter-spacing: 0.06em; text-transform: uppercase; margin-bottom: 22px; }
h1 { margin: 0; font-weight: 600; font-size: ${size}px; line-height: 1.08; letter-spacing: -0.03em; color: #17171a; }
.brand { position: absolute; left: 72px; bottom: 44px; font-size: 22px; color: #55555c; }
.url { position: absolute; right: 56px; bottom: 44px; font-size: 22px; color: #55555c; }
img { position: relative; width: ${t.artWidth}px; height: auto; flex: none; border-radius: ${t.artWidth < 350 ? '64px' : '0'};
  ${t.artWidth < 350 ? 'box-shadow: 0 20px 50px rgba(180,83,9,0.25);' : ''} }
</style></head><body>
<div class="text"><div class="kicker">${esc(meta.kicker)}</div><h1>${esc(line)}</h1></div>
<img src="${art}" alt="">
<div class="brand">${esc(t.brand)}</div><div class="url">macwanapps.com</div>
</body></html>`;
}

(async () => {
  const browser = await chromium.launch();
  const tab = await browser.newPage({ viewport: { width: 1200, height: 630 } });
  fs.mkdirSync(path.join(ROOT, 'images/blog'), { recursive: true });
  for (const app of Object.keys(THEMES)) {
    const dir = path.join(ROOT, '_blog/posts', app);
    if (!fs.existsSync(dir)) continue;
    for (const f of fs.readdirSync(dir).filter((f) => f.endsWith('.html'))) {
      const slug = f.replace(/\.html$/, '');
      const out = path.join(ROOT, 'images/blog', `${app}-${slug}.png`);
      if (fs.existsSync(out) && !FORCE) continue;
      await tab.setContent(page(THEMES[app], frontMatter(path.join(dir, f))), { waitUntil: 'load' });
      await tab.screenshot({ path: out });
      console.log('cover', path.relative(ROOT, out));
    }
  }
  await browser.close();
})();
