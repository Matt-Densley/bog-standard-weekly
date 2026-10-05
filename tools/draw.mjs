// Draws last week's Bog Standard sheets as pictures for the Monday carousel.
//
// It opens the live site's own pages (bogstandard.uk/week?only=sheet for the cover, and
// bogstandard.uk/company/<slug>/week/<Monday>?only=sheet for each company), photographs the
// sheet each one draws, and pads it to Instagram's 4:5 (1080 x 1350) on the paper colour.
// So a picture can never disagree with the site: it IS the site, photographed.
//
// Nothing here works a figure out. The captions are filled in by the site's own formatting
// code (js/week-core.js, loaded from the site), and the week's reports are saved beside the
// pictures exactly as the API sent them.
//
// What it writes:
//   weeks/<Monday>/01-cover.png, 02-<company>.png ...   the slides, in ranking order
//   weeks/<Monday>/index.json                           every slide's address and description, the captions
//   weeks/<Monday>/caption-instagram.txt, caption-x.txt the same captions as plain text
//   weeks/<Monday>/data/*.json                          the reports, as sent
//   latest.json                                         which week is the newest
//   last-run.json                                       how the last run went (also written when it fails)
//
// Run:  node tools/draw.mjs
// For testing without the API or the web fonts (a saved set of reports, a local copy of the site):
//   SITE=http://localhost:8080 FIXTURES=/path/to/reports FONTS=/path/to/@fontsource node tools/draw.mjs
import { chromium } from 'playwright';
import sharp from 'sharp';
import fs from 'node:fs/promises';
import { existsSync } from 'node:fs';
import path from 'node:path';

const SITE = (process.env.SITE || 'https://bogstandard.uk').replace(/\/$/, '');
const API = (process.env.API || 'https://api.bogstandard.uk').replace(/\/$/, '');
const RAW = (process.env.RAW || 'https://raw.githubusercontent.com/Matt-Densley/bog-standard-weekly/main').replace(/\/$/, '');
const FIXTURES = process.env.FIXTURES || '';
const FONTS = process.env.FONTS || '';
const OUT = process.env.OUT || process.cwd();
const PAPER = '#E7DFC6';
const WIDTH = 1080, HEIGHT = 1350;
const AGENT = 'bog-standard-weekly (github.com/Matt-Densley/bog-standard-weekly)';

const now = () => new Date().toISOString();
const two = n => String(n).padStart(2, '0');

// ---------- the reports ----------
function fixtureFor(pathAndQuery){
  const u = new URL(pathAndQuery, 'https://x');
  if(u.pathname === '/weekly/list') return path.join(FIXTURES, 'list.json');
  if(u.pathname === '/weekly') return path.join(FIXTURES, `${u.searchParams.get('company')}.json`);
  return null;
}

// The text of one API answer, exactly as sent (so it can be saved as sent), and parsed.
async function getReport(pathAndQuery){
  if(FIXTURES){
    const file = fixtureFor(pathAndQuery);
    if(!file || !existsSync(file)) throw new Error(`no saved report for ${pathAndQuery}`);
    const text = await fs.readFile(file, 'utf8');
    return { text, json: JSON.parse(text) };
  }
  let last;
  for(let attempt = 1; attempt <= 3; attempt++){
    try{
      const res = await fetch(`${API}${pathAndQuery}`, { headers: { 'user-agent': AGENT, accept: 'application/json' }, signal: AbortSignal.timeout(30000) });
      if(!res.ok) throw new Error(`${pathAndQuery} answered ${res.status}`);
      const text = await res.text();
      return { text, json: JSON.parse(text) };
    } catch(err){
      last = err;
      if(attempt < 3) await new Promise(done => setTimeout(done, attempt * 4000));
    }
  }
  throw last;
}

// ---------- the browser ----------
async function openBrowser(){
  const browser = await chromium.launch();
  const context = await browser.newContext({ viewport: { width: 794, height: 1123 }, deviceScaleFactor: 2, userAgent: undefined });
  if(FIXTURES){
    await context.route(u => u.href.startsWith(`${API}/`), async route => {
      const u = new URL(route.request().url());
      const file = fixtureFor(u.pathname + u.search);
      if(file && existsSync(file)) return route.fulfill({ contentType: 'application/json', body: await fs.readFile(file), headers: { 'access-control-allow-origin': '*' } });
      return route.abort();
    });
  }
  if(FONTS){
    // The same four families from local copies, where Google Fonts can't be reached.
    const families = { 'Big Shoulders Display': ['big-shoulders-display', [600, 800, 900]], Caveat: ['caveat', [400, 600, 700]], 'IBM Plex Mono': ['ibm-plex-mono', [400, 500, 600]], 'IBM Plex Sans': ['ibm-plex-sans', [400, 500, 600]] };
    let css = '';
    for(const [family, [pkg, weights]] of Object.entries(families)) for(const w of weights) css += `@font-face{font-family:'${family}';font-style:normal;font-weight:${w};src:url(https://fonts.gstatic.com/local/${pkg}/${pkg}-latin-${w}-normal.woff2) format('woff2');}\n`;
    await context.route(/^https:\/\/fonts\.googleapis\.com\//, route => route.fulfill({ contentType: 'text/css', body: css, headers: { 'access-control-allow-origin': '*' } }));
    await context.route(/^https:\/\/fonts\.gstatic\.com\/local\//, async route => {
      const m = /local\/([\w-]+)\/([\w.-]+)$/.exec(route.request().url());
      const file = path.join(FONTS, m[1], 'files', m[2]);
      return existsSync(file) ? route.fulfill({ contentType: 'font/woff2', body: await fs.readFile(file), headers: { 'access-control-allow-origin': '*' } }) : route.abort();
    });
  }
  return { browser, context };
}

// Opens one sheet-only page and photographs the sheet. `mustSay` are pieces of text the sheet
// has to carry (the week's dates, the company's name): a check that it is the right sheet.
async function photograph(context, address, mustSay){
  const page = await context.newPage();
  const problems = [];
  page.on('pageerror', err => problems.push(String(err).slice(0, 200)));
  try{
    await page.goto(address, { waitUntil: 'load', timeout: 60000 });
    await page.waitForFunction(() => document.documentElement.dataset.sheet === 'drawn', null, { timeout: 60000 })
      .catch(() => { throw new Error(`the sheet was never drawn at ${address}${problems.length ? ` (${problems[0]})` : ''}`); });
    const state = await page.evaluate(async () => {
      if(document.fonts && document.fonts.ready) await document.fonts.ready;
      await Promise.all([...document.images].map(img => (img.complete ? null : new Promise(done => { img.onload = img.onerror = done; }))));
      const fit = document.querySelector('.ws-fit');
      return {
        only: document.documentElement.classList.contains('wk-only'),
        said: fit ? fit.querySelector('.ws-paper').textContent.replace(/\s+/g, ' ') : '',
        alt: fit ? fit.getAttribute('aria-label') : '',
        strokes: fit ? fit.querySelectorAll('.ws-draw > *').length : 0,
        fonts: !!document.fonts && document.fonts.check('700 20px Caveat') && document.fonts.check('900 52px "Big Shoulders Display"'),
        images: [...document.images].every(img => img.naturalWidth > 0),
      };
    });
    if(!state.only) throw new Error('the page fell back to its full view, so there is no sheet to photograph');
    if(state.strokes < 20) throw new Error(`the sheet looks empty (${state.strokes} pen strokes)`);
    const said = state.said.toLowerCase();
    for(const text of mustSay) if(!said.includes(text.toLowerCase())) throw new Error(`the sheet doesn't say "${text}", so it may be the wrong sheet`);
    if(!state.images) throw new Error('the logo on the sheet did not load');
    const shot = await page.locator('.ws-fit').screenshot({ type: 'png' });
    const picture = await sharp(shot).resize({ width: WIDTH, height: HEIGHT, fit: 'contain', background: PAPER }).flatten({ background: PAPER }).png({ compressionLevel: 9 }).toBuffer();
    return { picture, alt: state.alt, fonts: state.fonts, page };
  } catch(err){
    await page.close();
    throw err;
  }
}

// ---------- the captions ----------
// Filled in from the cover's own model (coverModel in the site's js/week-core.js), so every
// figure reads exactly as it does on the cover. The words around them are fixed.
function captions(cover){
  const status = cover.stamp === 'Part week'
    ? 'Part week: our record of the live feeds has gaps in this week, so the figures are minimums.'
    : cover.stamp
      ? 'Provisional figures, from our record of the water companies’ live feeds.'
      : 'Final figures for the week, from our record of the water companies’ live feeds.';
  const lines = cover.rows.map(r => `${r.rank}. ${r.company} · ${r.per == null ? r.perText : `${r.perText} per overflow`} · ${r.rain == null ? r.rainText : `${r.rainText} of rain`}`);
  const instagram = [
    `Last week, company by company: ${cover.range}.`,
    '',
    'Swipe for each water company’s week: the rain in its area, and the hours its storm overflows reported discharging.',
    '',
    'Ranked by time per overflow monitor each company runs:',
    ...lines,
    '',
    'Wetter areas see more spills, so read the rain and the hours together. Heavy rain is when storm overflows are allowed to operate.',
    '',
    `${status} Hours, not volume: monitors record how long, not how much. A discharge report is not by itself proof of a permit breach. England only.`,
    '',
    'Every company’s week: bogstandard.uk/week (link in bio)',
    '',
    '#StormOverflows #BogStandard #Rivers #WaterCompanies',
  ].join('\n');

  const top = cover.rows[0];
  const head = `Last week’s storm overflows, company by company (${cover.shortRange}).`;
  const first = top && top.per != null ? `Most time per overflow: ${top.company}, ${top.perText}${top.rain == null ? '' : `, with ${top.rainText} of rain in its area`}.` : '';
  const small = `${cover.stamp === 'Part week' ? 'Part week' : cover.stamp ? 'Provisional' : 'Final for the week'}. Hours, not volume. Not by itself proof of a permit breach.`;
  const link = 'bogstandard.uk/week';
  let x = [head, first, small, link].filter(Boolean).join('\n\n');
  if(x.length > 280) x = [head, small, link].join('\n\n');   // never trimmed mid-sentence: the middle line is dropped whole
  return { instagram, x };
}

// ---------- the run ----------
async function run(){
  const list = await getReport('/weekly/list');
  const weeks = Array.isArray(list.json.weeks) ? list.json.weeks.filter(w => w && w.company && w.slug && w.week) : [];
  if(!weeks.length) throw new Error('the API has no week to draw yet');
  const week = weeks[0].week;
  if(!/^\d{4}-\d{2}-\d{2}$/.test(week)) throw new Error(`the week's date looks wrong: ${week}`);
  const rows = weeks.filter(w => w.week === week);

  const dir = path.join(OUT, 'weeks', week);
  await fs.rm(dir, { recursive: true, force: true });
  await fs.mkdir(path.join(dir, 'data'), { recursive: true });
  await fs.writeFile(path.join(dir, 'data', 'list.json'), list.text);

  const { browser, context } = await openBrowser();
  const slides = [], skipped = [];
  let cover = null, fontsOk = true;
  try{
    // The cover first: it also hands back the site's own formatting of the ranking.
    const shot = await photograph(context, `${SITE}/week?only=sheet`, ['Company by company']);
    cover = await shot.page.evaluate(async rowsIn => {
      const core = await import('/js/week-core.js');
      const model = core.coverModel(rowsIn);
      return { ...model, range: core.weekRange(model.week, model.weekEnd), shortRange: `${core.shortDate(model.week)} to ${core.shortDate(model.weekEnd)}` };
    }, rows);
    const saidRange = await shot.page.evaluate(() => document.querySelector('.ws-paper').textContent);
    await shot.page.close();
    if(!saidRange.includes(cover.range)) throw new Error(`the cover on the site is for a different week than the API's latest (${cover.range})`);
    fontsOk = fontsOk && shot.fonts;
    await fs.writeFile(path.join(dir, '01-cover.png'), shot.picture);
    slides.push({ n: 1, file: '01-cover.png', what: 'cover', alt: shot.alt });

    for(const [i, row] of rows.entries()){
      const n = i + 2, file = `${two(n)}-${row.slug}.png`;
      try{
        const report = await getReport(`/weekly?company=${encodeURIComponent(row.slug)}&week=${week}`);
        if(report.json.week !== week || report.json.slug !== row.slug) throw new Error('the API sent a different report than the one asked for');
        await fs.writeFile(path.join(dir, 'data', `${row.slug}.json`), report.text);
        const s = await photograph(context, `${SITE}/company/${row.slug}/week/${week}?only=sheet`, [row.company, cover.range]);
        await s.page.close();
        fontsOk = fontsOk && s.fonts;
        await fs.writeFile(path.join(dir, file), s.picture);
        slides.push({ n, file, what: 'company', company: row.company, slug: row.slug, rank: i + 1, final: !!row.final, partWeek: !!row.incomplete, alt: s.alt });
      } catch(err){
        skipped.push({ company: row.company, slug: row.slug, reason: String(err.message || err).slice(0, 300) });
      }
    }
  } finally {
    await browser.close();
  }

  for(const s of slides) s.url = `${RAW}/weeks/${week}/${s.file}`;
  const text = captions(cover);
  const index = {
    week, weekEnd: cover.weekEnd, range: cover.range,
    status: cover.stamp === 'Part week' ? 'part week' : cover.stamp ? 'provisional' : 'final',
    drawnAt: now(), drawnFrom: SITE, figuresFrom: FIXTURES ? 'saved reports (a test run)' : API,
    webFontsLoaded: fontsOk,
    slides, skipped,
    captions: text,
    notes: [
      'Every picture is the site\'s own sheet, photographed. The captions are filled in by the site\'s own formatting code.',
      'Nothing is posted from here. Posts are queued for Matt to approve.',
    ],
  };
  await fs.writeFile(path.join(dir, 'index.json'), `${JSON.stringify(index, null, 2)}\n`);
  await fs.writeFile(path.join(dir, 'caption-instagram.txt'), `${text.instagram}\n`);
  await fs.writeFile(path.join(dir, 'caption-x.txt'), `${text.x}\n`);
  await fs.writeFile(path.join(OUT, 'latest.json'), `${JSON.stringify({ week, index: `${RAW}/weeks/${week}/index.json`, drawnAt: index.drawnAt, status: index.status, slides: slides.length, skipped: skipped.length }, null, 2)}\n`);
  return { week, drawn: slides.length, skipped, webFontsLoaded: fontsOk, status: index.status };
}

let result;
try{
  const r = await run();
  // A cover and at least one company is a carousel worth queuing; anything less is a failed run.
  const ok = r.drawn >= 2;
  result = { at: now(), ok, ...r, ...(ok ? {} : { error: 'too few sheets could be drawn' }) };
} catch(err){
  result = { at: now(), ok: false, error: String(err && err.message ? err.message : err).slice(0, 500) };
}
await fs.writeFile(path.join(OUT, 'last-run.json'), `${JSON.stringify(result, null, 2)}\n`);
console.log(JSON.stringify(result, null, 2));
process.exit(result.ok ? 0 : 1);
