"""Holt für die angegebenen Leads frische Vorher-Screenshots, Seitentext und Bilder.
Aufruf: python3 wave/fetch.py KEY1 KEY2 ...   (KEY = slug aus data/all_v2.json)"""
import json, os, sys, re, urllib.request, ssl
from playwright.sync_api import sync_playwright
sys.path.insert(0, "/home/claude/nk/wave"); import httpfix
B = "/home/claude/nk"
D = {r["slug"]: r for r in json.load(open(f"{B}/data/all_v2.json"))}
PROXY = os.environ.get("HTTPS_PROXY")
JS = """() => {
 const imgs=[...document.images].map(i=>({src:i.currentSrc||i.src,w:i.naturalWidth,h:i.naturalHeight})).filter(i=>i.w>=280&&i.h>=180&&!/logo|icon|sprite|lieferando/i.test(i.src));
 const bg=[...document.querySelectorAll('*')].slice(0,3000).map(e=>getComputedStyle(e).backgroundImage).filter(b=>b&&b.startsWith('url(')).map(b=>b.slice(5,-2));
 const tel=[...document.querySelectorAll('a[href^="tel:"]')].map(a=>a.getAttribute('href'));
 const mail=[...document.querySelectorAll('a[href^="mailto:"]')].map(a=>a.getAttribute('href'));
 const links=[...document.querySelectorAll('a[href]')].map(a=>({t:(a.innerText||'').trim().slice(0,40),h:a.href})).filter(l=>l.t).slice(0,80);
 return {title:document.title,text:(document.body?document.body.innerText:'').slice(0,6000),imgs,bg:[...new Set(bg)].slice(0,10),tel,mail,links};
}"""
def dl(url, path):
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        ctx = ssl.create_default_context(cafile="/root/.ccr/ca-bundle.crt")
        data = urllib.request.urlopen(req, timeout=20, context=ctx).read()
        if len(data) < 15000: return False
        open(path, "wb").write(data); return True
    except Exception: return False
with sync_playwright() as p:
    b = p.chromium.launch(proxy={"server": PROXY} if PROXY else None)
    for k in sys.argv[1:]:
        r = D[k]; url = r.get("final") or r["url"]
        out = {"key": k, "url": url}
        for vw, vh, suf, dsf in [(1366, 850, "desk", 1), (390, 844, "mob", 2)]:
            ctx = b.new_context(viewport={"width": vw, "height": vh}, device_scale_factor=dsf, locale="de-DE", ignore_https_errors=True, user_agent=os.environ.get("UA") or None)
            ctx.route("http://**/*", httpfix.sync_handler); pg = ctx.new_page()
            try:
                pg.goto(url, timeout=45000, wait_until="load"); pg.wait_for_timeout(2500)
                for sel in ["text=Alle akzeptieren", "text=Akzeptieren", "text=Alle zulassen", "text=Zustimmen", "text=Einverstanden", "text=OK"]:
                    try: pg.locator(sel).first.click(timeout=700); pg.wait_for_timeout(600); break
                    except Exception: pass
                pg.screenshot(path=f"{B}/wave/raw/{k}_vorher_{suf}.png")
                if suf == "desk": out.update(pg.evaluate(JS))
            except Exception as e:
                out["error_" + suf] = str(e)[:150]
            ctx.close()
        n = 0
        for u in [i["src"] for i in sorted(out.get("imgs", []), key=lambda i: -i["w"] * i["h"])] + out.get("bg", []):
            if n >= 5 or not u.startswith("http"): continue
            ext = (re.search(r"\.(jpe?g|png|webp|gif)", u.lower()) or [None, "jpg"])[1]
            if dl(u, f"{B}/mock/img/{k}_{n}.{ext}"): out.setdefault("saved", []).append(f"img/{k}_{n}.{ext}"); n += 1
        json.dump(out, open(f"{B}/wave/raw/{k}.json", "w"), ensure_ascii=False, indent=1)
        print(k, "ok" if "text" in out else "FEHLER", len(out.get("saved", [])), "Bilder", flush=True)
    b.close()
