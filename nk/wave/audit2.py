"""Technik-Check je Lead (gemessen, mit Belegen).
Aufruf: python3 wave/audit2.py [KURZ ...]   (ohne Argumente: alle aus site/data/top10.json ohne vorhandenes Audit)
Ergebnis: wave/audit/<k>.json"""
import asyncio, json, os, re, sys, time, subprocess
from playwright.async_api import async_playwright
sys.path.insert(0, "/home/claude/nk/wave"); import httpfix

B = "/home/claude/nk/wave"
OUT = f"{B}/audit"; os.makedirs(OUT, exist_ok=True)
TOP = json.load(open("/home/claude/site/data/top10.json", encoding="utf-8"))
PROXY = os.environ.get("HTTPS_PROXY")
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36"
UA_M = "Mozilla/5.0 (iPhone; CPU iPhone OS 17_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Mobile/15E148 Safari/604.1"

JS = r"""() => {
 const q=s=>[...document.querySelectorAll(s)];
 const meta=n=>{const m=document.querySelector(`meta[name="${n}"],meta[property="${n}"]`);return m?(m.getAttribute('content')||''):null};
 const txt=(document.body?document.body.innerText:'')||'';
 const words=(txt.match(/[A-Za-zÄÖÜäöüß]{2,}/g)||[]).length;
 const imgs=q('img');
 const broken=imgs.filter(i=>i.complete&&i.naturalWidth===0&&(i.currentSrc||i.src)).map(i=>({src:(i.currentSrc||i.src).slice(0,140),alt:(i.alt||'').slice(0,80)}));
 const noalt=imgs.filter(i=>i.naturalWidth>80&&!(i.getAttribute('alt')||'').trim()).length;
 const big=imgs.filter(i=>i.naturalWidth>=1800&&i.clientWidth>0&&i.naturalWidth>i.clientWidth*2.5).map(i=>({src:(i.currentSrc||i.src).slice(0,120),nat:i.naturalWidth,shown:Math.round(i.clientWidth)}));
 const ld=q('script[type="application/ld+json"]').map(s=>s.textContent||'').join(' ');
 const years=(txt.match(/(?:©|copyright|\(c\))\s*(?:\d{4}\s*[-–]\s*)?(\d{4})/ig)||[]).map(m=>+m.match(/(\d{4})(?!.*\d{4})/)[1]);
 let small=0,total=0;
 for(const el of q('p,li,td,span,a,div')){ if(!el.childNodes.length) continue; const own=[...el.childNodes].some(n=>n.nodeType===3&&n.textContent.trim().length>2); if(!own) continue; const r=el.getBoundingClientRect(); if(r.width===0||r.height===0) continue; total++; if(parseFloat(getComputedStyle(el).fontSize)<12) small++; }
 const taps=q('a,button').filter(a=>{const r=a.getBoundingClientRect();return r.width>0&&r.height>0&&(r.height<24||r.width<24)&&(a.innerText||'').trim()}).length;
 const placeholders=[];
 for(const p of ['lorem ipsum','beispielüberschrift','my cms','[#','holzland','hier steht ihr text','musterfirma','your text here','platzhalter','under construction','im aufbau','umbauphase','coming soon','seite befindet sich']){ if(txt.toLowerCase().includes(p)||document.title.toLowerCase().includes(p)||document.documentElement.innerHTML.toLowerCase().includes(p)&&p.startsWith('[#')) placeholders.push(p); }
 return {
  title:document.title, desc:meta('description'), viewport:meta('viewport'), ogimg:meta('og:image'), ogtitle:meta('og:title'),
  generator:meta('generator'), h1:q('h1').map(h=>(h.innerText||'').trim().slice(0,80)).filter(Boolean),
  words, tel:q('a[href^="tel:"]').length, mail:q('a[href^="mailto:"]').map(a=>a.getAttribute('href').slice(7).split('?')[0]).slice(0,3),
  wa:q('a[href*="wa.me"],a[href*="whatsapp"]').length, forms:q('form').length,
  maps:!!document.querySelector('iframe[src*="google.com/maps"],iframe[src*="openstreetmap"],iframe[src*="maps.google"]'),
  localbiz:/LocalBusiness|Restaurant|Store|Organization|Dentist|AutoRepair|HomeAndConstructionBusiness|LodgingBusiness|FoodEstablishment|ProfessionalService/i.test(ld),
  favicon:!!document.querySelector('link[rel*="icon"]'),
  imgs:imgs.length, broken, noalt, big, years, small, total, taps, placeholders,
  scrollW:document.documentElement.scrollWidth, innerW:window.innerWidth,
  http_res:performance.getEntriesByType('resource').map(r=>r.name).filter(n=>n.startsWith('http:')).slice(0,5),
  impressum:q('a').some(a=>/impressum/i.test(a.innerText||a.href)),
  datenschutz:q('a').some(a=>/datenschutz/i.test(a.innerText||a.href)),
 };
}"""

async def measure(browser, url, mobile):
    ctx = await browser.new_context(
        viewport={"width": 390, "height": 844} if mobile else {"width": 1366, "height": 850},
        device_scale_factor=2 if mobile else 1, is_mobile=mobile, has_touch=mobile,
        user_agent=UA_M if mobile else UA, locale="de-DE", ignore_https_errors=False)
    await ctx.route("http://**/*", httpfix.async_handler)
    pg = await ctx.new_page()
    errs, sizes, reqs = [], [], []
    pg.on("pageerror", lambda e: errs.append(str(e)[:160]))
    pg.on("console", lambda m: errs.append(m.text[:160]) if m.type == "error" else None)
    async def onresp(r):
        try:
            reqs.append(r.url)
            h = await r.all_headers()
            cl = h.get("content-length")
            sizes.append((r.request.resource_type, int(cl) if cl and cl.isdigit() else 0))
        except Exception: pass
    pg.on("response", lambda r: asyncio.ensure_future(onresp(r)))
    res = {"ok": False}
    t0 = time.time()
    try:
        resp = await pg.goto(url, timeout=45000, wait_until="load")
        res["load_s"] = round(time.time() - t0, 1)
        res["status"] = resp.status if resp else None
        res["final"] = pg.url
        await pg.wait_for_timeout(2500)
        res.update(await pg.evaluate(JS))
        res["ok"] = True
    except Exception as e:
        res["error"] = str(e)[:200]
        # zweiter Versuch ohne Zertifikatspruefung, um Zertifikatsfehler zu belegen
        if "CERT" in str(e).upper() or "SSL" in str(e).upper():
            res["cert_error"] = True
    await asyncio.sleep(0.5)
    res["errors"] = errs[:8]
    res["requests"] = len(reqs)
    res["bytes"] = sum(s for _, s in sizes)
    res["img_bytes"] = sum(s for t, s in sizes if t == "image")
    await ctx.close()
    return res

async def http_check(browser, url):
    """Prueft per curl (ohne Browser, der Proxy verfaelscht http im Browser), ob http:// auf https:// umleitet."""
    import subprocess
    host = re.sub(r"^https?://", "", url).split("/")[0]
    out = {}
    try:
        r = subprocess.run(["curl", "-s", "-o", "/dev/null", "-L", "--max-time", "20", "-w", "%{http_code} %{url_effective}", f"http://{host}/"], capture_output=True, text=True, timeout=30)
        code, eff = (r.stdout.split(" ", 1) + [""])[:2]
        out["http_to"] = eff; out["http_code"] = code
        out["http_redirects_to_https"] = eff.startswith("https://") if code not in ("000", "") else None
    except Exception as e:
        out["http_error"] = str(e)[:120]
    return out

async def one(sem, browser, t):
    async with sem:
        k, url = t["k"], t["url"]
        if not url.startswith("http"): url = "https://" + url
        d = {"k": k, "url": url, "date": time.strftime("%Y-%m-%d")}
        murl = url
        if url.startswith("http://"):  # Browser-Proxy kann kein http: Ziel der Weiterleitung per curl holen
            r = subprocess.run(["curl", "-s", "-o", "/dev/null", "-L", "--max-time", "20", "-w", "%{url_effective}", url], capture_output=True, text=True, timeout=30)
            if r.stdout.startswith("https://"): murl = r.stdout.strip(); d["measured_url"] = murl
        d["desk"] = await measure(browser, murl, False)
        d["mob"] = await measure(browser, murl, True)
        d.update(await http_check(browser, url))
        json.dump(d, open(f"{OUT}/{k}.json", "w"), ensure_ascii=False, indent=1)
        print("ok", k, d["desk"].get("ok"), d["mob"].get("scrollW"), flush=True)

async def main():
    want = sys.argv[1:]
    todo = [t for t in TOP if (t["k"] in want) or (not want and not os.path.exists(f"{OUT}/{t['k']}.json"))]
    async with async_playwright() as p:
        browser = await p.chromium.launch(proxy={"server": PROXY} if PROXY else None)
        sem = asyncio.Semaphore(4)
        await asyncio.gather(*(one(sem, browser, t) for t in todo))
        await browser.close()

asyncio.run(main())
