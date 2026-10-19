import os,sys,json
from playwright.sync_api import sync_playwright
P=os.environ.get("HTTPS_PROXY")
with sync_playwright() as p:
    b=p.chromium.launch(proxy={"server":P})
    for url in sys.argv[1:]:
        pg=b.new_page(locale="de-DE")
        try:
            pg.goto(url,timeout=40000,wait_until="load"); pg.wait_for_timeout(3000)
            txt=[]
            for fr in pg.frames:
                try: txt.append(fr.evaluate("document.body?document.body.innerText:''"))
                except Exception: pass
            links=[]
            for fr in pg.frames:
                try: links+=fr.evaluate("[...document.querySelectorAll('a[href]')].map(a=>(a.innerText||'').trim()+' -> '+a.href).slice(0,40)")
                except Exception: pass
            print("=====",url,pg.url); print("\n".join(t for t in txt if t.strip())[:2500]); print("LINKS",links[:30])
        except Exception as e: print("ERR",url,str(e)[:120])
        pg.close()
    b.close()
