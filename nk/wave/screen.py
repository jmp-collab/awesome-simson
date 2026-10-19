"""Schnell-Screening neuer Leads: Alterssignale je Website. Aufruf: python3 wave/screen.py wave/new_near.json -> wave/screen.json"""
import asyncio, json, os, re, sys, time
from playwright.async_api import async_playwright
PROXY = os.environ.get("HTTPS_PROXY")
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0 Safari/537.36"
JS = r"""()=>{const t=(document.body?document.body.innerText:'')||'';const h=document.documentElement.innerHTML;
const y=(t.match(/(?:©|copyright|\(c\))\s*(?:\d{4}\s*[-–]\s*)?(\d{4})/ig)||[]).map(m=>+(m.match(/(\d{4})(?!.*\d{4})/)||[0,0])[1]);
const gen=(document.querySelector('meta[name=generator]')||{}).content||'';
return {title:document.title,words:(t.match(/[A-Za-zÄÖÜäöüß]{2,}/g)||[]).length,years:y,gen,
vp:!!document.querySelector('meta[name=viewport]'),tables:document.querySelectorAll('table').length,frames:document.querySelectorAll('frame,iframe[src*=".htm"]').length,
font:document.querySelectorAll('font,center,marquee').length,flash:/\.swf/i.test(h),jquery_old:/jquery[-.]1\.[0-9]\./i.test(h),
tel:document.querySelectorAll('a[href^="tel:"]').length,https:location.protocol==='https:',
lieferando:/verwaltet durch\s*Lieferando/i.test(t),text0:t.slice(0,300)}}"""
async def one(sem, b, r, out):
    async with sem:
        ctx = await b.new_context(viewport={"width": 390, "height": 844}, user_agent=UA, locale="de-DE", ignore_https_errors=True)
        pg = await ctx.new_page(); d = {"slug": r["slug"]}
        try:
            u = "https://" + re.sub(r"^https?://", "", r["url"])
            resp = await pg.goto(u, timeout=30000, wait_until="load"); await pg.wait_for_timeout(1500)
            d.update(await pg.evaluate(JS)); d["final"] = pg.url; d["status"] = resp.status if resp else None
            d["scrollW"] = await pg.evaluate("Math.max(document.documentElement.scrollWidth, window.innerWidth)")
        except Exception as e:
            d["error"] = str(e)[:120]
        await ctx.close(); out.append(d)
async def main():
    L = json.load(open(sys.argv[1])); out = []
    async with async_playwright() as p:
        b = await p.chromium.launch(proxy={"server": PROXY} if PROXY else None)
        sem = asyncio.Semaphore(6)
        await asyncio.gather(*(one(sem, b, r, out) for r in L))
        await b.close()
    json.dump(out, open("/home/claude/nk/wave/screen.json", "w"), ensure_ascii=False, indent=0)
    print("gescreent", len(out))
asyncio.run(main())
