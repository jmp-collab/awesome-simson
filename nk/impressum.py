"""Zieht Kontakt-E-Mail und Inhaber/Geschäftsführer aus dem Impressum.
Aufruf: python3 impressum.py IN.json OUT.json   (IN: Liste von {name,url})"""
import asyncio, json, os, re, sys
from playwright.async_api import async_playwright

PROXY = os.environ.get("HTTPS_PROXY")
EMAIL = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
ROLE = re.compile(r"(Inhaber(?:in)?|Geschäftsführer(?:in)?|Geschäftsführung|Vertreten durch|Vertretungsberechtigt(?:e[rn]?)?|Verantwortlich(?:er)?(?: für den Inhalt)?(?: nach [^\n:]{0,30})?|Betreiber(?:in)?|Praxisinhaber(?:in)?)\s*[:\-]?\s*\n?\s*([^\n]{3,80})", re.I)
BAD_MAIL = ("example", "sentry", "wixpress", "domain.", "email.com", "ihre-", "@2x", ".png", ".jpg", "lieferando", "jimdo", "ionos", "strato", "wordpress", "datenschutz-generator")

def deob(t):
    t = re.sub(r"\s*[\(\[\{]\s*(?:at|ät|@)\s*[\)\]\}]\s*", "@", t, flags=re.I)
    t = re.sub(r"\s+(?:at)\s+", "@", t)
    t = re.sub(r"\s*[\(\[\{]\s*(?:dot|punkt)\s*[\)\]\}]\s*", ".", t, flags=re.I)
    return t

def clean_name(s):
    s = re.split(r"\s{2,}|,|\||Tel|Telefon|Fax|E-?Mail|Anschrift|Straße|Str\.|USt|Steuer|Register|HRB|Amtsgericht", s)[0].strip(" .:-")
    if len(s) < 4 or re.search(r"\d", s) or s.lower() in ("die geschäftsführung", "siehe oben"): return ""
    return s[:60]

async def one(br, r, sem):
    out = {"name": r["name"], "imp_url": "", "emails": [], "owner": ""}
    async with sem:
        ctx = await br.new_context(locale="de-DE", ignore_https_errors=False)
        pg = await ctx.new_page()
        try:
            await pg.goto(r["url"], timeout=30000, wait_until="domcontentloaded")
            await pg.wait_for_timeout(1500)
            home_txt = await pg.evaluate("document.body?document.body.innerText:''")
            home_html = await pg.content()
            links = await pg.evaluate("""[...document.querySelectorAll('a[href]')].map(a=>({t:(a.innerText||'').trim().toLowerCase(),h:a.href}))""")
            imp = next((l["h"] for l in links if "impressum" in l["t"] or "impressum" in l["h"].lower()), "")
            if not imp:
                imp = next((l["h"] for l in links if l["t"] in ("kontakt", "contact") or "kontakt" in l["h"].lower()), "")
            txt, html = home_txt, home_html
            if imp and imp.startswith("http"):
                try:
                    await pg.goto(imp, timeout=30000, wait_until="domcontentloaded"); await pg.wait_for_timeout(1200)
                    txt = (await pg.evaluate("document.body?document.body.innerText:''")) + "\n" + home_txt
                    html = await pg.content() + home_html
                    out["imp_url"] = imp
                except Exception:
                    pass
            mails = re.findall(r"mailto:([^\"'?>\s]+)", html) + EMAIL.findall(deob(txt))
            seen = []
            for m in mails:
                m = m.strip().strip(".").lower()
                if any(b in m for b in BAD_MAIL) or m in seen: continue
                seen.append(m)
            dom = re.sub(r"^https?://(www\.)?", "", r["url"]).split("/")[0].lower()
            seen.sort(key=lambda m: (0 if dom.split(".")[-2] in m else 1, 0 if m.startswith(("info@", "kontakt@", "praxis@", "post@", "mail@")) else 1))
            out["emails"] = seen[:3]
            for m in ROLE.finditer(txt):
                n = clean_name(m.group(2))
                if n:
                    out["owner"] = n; out["owner_role"] = m.group(1); break
        except Exception as e:
            out["error"] = str(e)[:120]
        await ctx.close()
    print(("ok  " if out["emails"] else "--  ") + r["name"], flush=True)
    return out

async def main():
    rows = json.load(open(sys.argv[1]))
    async with async_playwright() as p:
        br = await p.chromium.launch(proxy={"server": PROXY} if PROXY else None)
        sem = asyncio.Semaphore(8)
        res = await asyncio.gather(*[one(br, r, sem) for r in rows])
        await br.close()
    json.dump(res, open(sys.argv[2], "w"), ensure_ascii=False, indent=1)

asyncio.run(main())
