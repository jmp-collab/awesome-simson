import asyncio, json, os, re, time
from playwright.async_api import async_playwright

PROXY = os.environ.get("HTTPS_PROXY")
import sys
rows = [l.rstrip("\n").split("|") for l in open("data/raw.txt", encoding="utf-8") if l.strip()]
only = sys.argv[1:]
if only: rows = [r for r in rows if r[3].startswith("http://") or r[0] in only]

JS = r"""
() => {
  const h = document.documentElement.outerHTML;
  const txt = document.body ? document.body.innerText : '';
  const q = s => document.querySelector(s);
  const links = [...document.querySelectorAll('a[href]')].map(a => a.href);
  const years = (txt.match(/(?:©|copyright|\(c\))\s*[^\n]{0,40}?((?:19|20)\d\d)/gi) || []).join(' ');
  const allyears = (txt.match(/\b(19[9]\d|20[0-2]\d)\b/g) || []).map(Number);
  return {
    title: document.title,
    desc: (q('meta[name="description"]') || {}).content || '',
    viewport: !!q('meta[name="viewport"]'),
    generator: (q('meta[name="generator"]') || {}).content || '',
    copyright: years,
    maxyear: allyears.length ? Math.max(...allyears) : null,
    tables: document.querySelectorAll('table').length,
    frames: document.querySelectorAll('frame,iframe[src*=".htm"]').length,
    fonttags: document.querySelectorAll('font,center,marquee').length,
    flash: /\.swf|shockwave/i.test(h),
    jquery: (h.match(/jquery[.-]?(\d\.\d+)/i) || [])[1] || '',
    wp: /wp-content|wp-includes/i.test(h),
    jimdo: /jimdo/i.test(h), wix: /wix\.com|wixstatic/i.test(h),
    ionos: /ionos|1und1|1&1|mywebsite|homepagebaukasten|website-builder/i.test(h),
    strato: /strato/i.test(h),
    facebook: links.find(l => /facebook\.com/.test(l)) || '',
    instagram: links.find(l => /instagram\.com/.test(l)) || '',
    tiktok: links.find(l => /tiktok\.com/.test(l)) || '',
    gmaps: /google\.[a-z.]+\/maps|maps\.google|goo\.gl\/maps/i.test(h),
    schema: /schema\.org/i.test(h),
    localbiz: /"@type"\s*:\s*"(LocalBusiness|Restaurant|Dentist|Attorney|Store|[A-Za-z]*Business|Hotel|FoodEstablishment)"/i.test(h),
    booking: /termin\s*online|online\s*buchen|jetzt\s*buchen|reservier|bestell|lieferando|opentable|doctolib|treatwell|shore|planity|warenkorb/i.test(txt + h),
    impressum: /impressum/i.test(txt),
    datenschutz: /datenschutz/i.test(txt),
    cookie: /cookie/i.test(txt),
    words: txt.split(/\s+/).length,
    imgs: document.images.length,
    h1: document.querySelectorAll('h1').length,
    scrollW: document.documentElement.scrollWidth,
    phoneLink: links.some(l => l.startsWith('tel:')),
    text: txt.slice(0, 1500)
  };
}
"""

async def one(br, r, sem):
    name, branch, addr, url, tel = r
    slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")[:40]
    res = {"name": name, "branch": branch, "addr": addr, "url": url, "tel": tel, "slug": slug}
    async with sem:
        try:
            ctx = await br.new_context(viewport={"width": 1366, "height": 850}, locale="de-DE",
                                       user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0 Safari/537.36")
            pg = await ctx.new_page()
            t0 = time.time()
            res["http_only"] = False
            res["source"] = "live"
            target = url.replace("http://", "https://", 1)
            try:
                resp = await pg.goto(target, timeout=30000, wait_until="load")
                if resp and resp.status >= 400 and resp.status != 403:
                    raise Exception(f"status {resp.status}")
            except Exception as e1:
                res["https_error"] = str(e1)[:160]
                res["http_only"] = True
                res["source"] = "wayback"
                t0 = time.time()
                resp = await pg.goto("https://web.archive.org/web/2026if_/" + url, timeout=60000, wait_until="load")
            res["load_s"] = round(time.time() - t0, 1)
            await pg.wait_for_timeout(1500)
            res["status"] = resp.status if resp else None
            res["final"] = pg.url
            res["https"] = pg.url.startswith("https") and not res["http_only"]
            res["lastmod"] = (resp.headers.get("last-modified") if resp else "") or ""
            res["server"] = (resp.headers.get("server") if resp else "") or ""
            res.update(await pg.evaluate(JS))
            await pg.screenshot(path=f"shots/{slug}_desk.png")
            await pg.set_viewport_size({"width": 390, "height": 844})
            await pg.wait_for_timeout(800)
            res["mob_scrollW"] = await pg.evaluate("document.documentElement.scrollWidth")
            await pg.screenshot(path=f"shots/{slug}_mob.png")
            await ctx.close()
        except Exception as e:
            res["error"] = str(e)[:200]
    print(("ERR " if "error" in res else "ok  ") + name, flush=True)
    return res

async def main():
    async with async_playwright() as p:
        br = await p.chromium.launch(proxy={"server": PROXY} if PROXY else None)
        sem = asyncio.Semaphore(8)
        out = await asyncio.gather(*[one(br, r, sem) for r in rows])
        await br.close()
    json.dump(out, open("data/crawl2.json" if only else "data/crawl.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)

asyncio.run(main())
