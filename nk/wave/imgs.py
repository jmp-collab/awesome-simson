"""Sammelt Fotos von mehreren Seiten eines Betriebs. Aufruf: python3 wave/imgs.py KEY MAX URL1 URL2 ..."""
import os,sys,re,hashlib
from playwright.sync_api import sync_playwright
k,mx,urls=sys.argv[1],int(sys.argv[2]),sys.argv[3:]
B="/home/claude/nk/mock/img"; P=os.environ.get("HTTPS_PROXY")
seen=set(); n=0; out=[]
with sync_playwright() as p:
    b=p.chromium.launch(proxy={"server":P}); ctx=b.new_context(ignore_https_errors=True); pg=ctx.new_page()
    for u in urls:
        try:
            pg.goto(u,timeout=40000,wait_until="load"); pg.wait_for_timeout(1500)
            srcs=[]
            for fr in pg.frames:
                try: srcs+=fr.evaluate(("[...document.images].filter(i=>i.naturalWidth>=MINW&&i.naturalHeight>=MINH).map(i=>[i.currentSrc||i.src,i.naturalWidth*i.naturalHeight])").replace("MINW",os.environ.get("MINW","200")).replace("MINH",os.environ.get("MINH","140")))
                except Exception: pass
            for s,a in sorted(srcs,key=lambda x:-x[1]):
                if n>=mx or s in seen or re.search(r"logo|icon|button|counter|banner_|lieferando",s,re.I): continue
                seen.add(s)
                r=ctx.request.get(s,timeout=20000)
                if not r.ok: continue
                body=r.body(); h=hashlib.md5(body).hexdigest()
                if len(body)<12000 or h in seen: continue
                seen.add(h); ext=(re.search(r"\.(jpe?g|png|webp|gif)",s.lower()) or [None,"jpg"])[1]
                fn=f"{k}_{n}.{ext}"; open(f"{B}/{fn}","wb").write(body); out.append((fn,a,s[-60:])); n+=1
        except Exception as e: print("ERR",u,str(e)[:80])
    b.close()
for o in out: print(o)
