import asyncio, os, json
from playwright.async_api import async_playwright
T={"asia":"https://asia-wok-neunkirchen.de/","roemer":"https://www.wirtshaus-roemer.de/","gondoliere":"https://gondoliere-neunkirchen.de/","damaskus":"https://www.damaskus-haus-neunkirchen.de","ellenfeld":"https://hotel-ellenfeld.de/","luxplay":"https://www.lux-play.de/","thielen":"https://www.schluessel-thielen.de/","marktapo":"https://www.markt-apotheke-nk.de/","rutz":"https://www.krankengymnastik-rutz.de/","tanzwerkstatt":"https://die-tanzwerkstatt.de/"}
JS="""()=>[...document.images].filter(i=>i.naturalWidth>=350&&i.naturalHeight>=200).map(i=>({src:i.currentSrc||i.src,w:i.naturalWidth,h:i.naturalHeight}))
.concat([...document.querySelectorAll('*')].map(e=>getComputedStyle(e).backgroundImage).filter(b=>b&&b.startsWith('url(')).map(b=>({src:b.slice(5,-2),w:0,h:0})))"""
async def go(p,k,u):
    b=await p.chromium.launch(proxy={"server":os.environ["HTTPS_PROXY"]})
    c=await b.new_context(viewport={"width":1366,"height":850}); pg=await c.new_page()
    out=[]
    try:
        await pg.goto(u,timeout=40000,wait_until="load"); await pg.wait_for_timeout(2500)
        await pg.evaluate("window.scrollTo(0,document.body.scrollHeight)"); await pg.wait_for_timeout(1500)
        imgs=await pg.evaluate(JS); seen=set(); n=0
        for im in sorted(imgs,key=lambda x:-x['w']*x['h']):
            s=im['src']
            if s in seen or not s.startswith('http') or s.endswith('.svg') or 'logo' in s.lower() and n>0: continue
            seen.add(s)
            try:
                r=await c.request.get(s,timeout=20000)
                if r.ok:
                    body=await r.body()
                    if len(body)>15000:
                        ext=s.split('?')[0].rsplit('.',1)[-1].lower()[:4]
                        fn=f"mock/img/{k}_{n}.{ext if ext in ('jpg','jpeg','png','webp','gif') else 'jpg'}"
                        open(fn,'wb').write(body); out.append({"file":fn,"src":s,"w":im['w'],"h":im['h']}); n+=1
            except Exception as e: pass
            if n>=8: break
    except Exception as e: out.append({"err":str(e)[:100]})
    await b.close(); return k,out
async def main():
    async with async_playwright() as p:
        res=await asyncio.gather(*[go(p,k,u) for k,u in T.items()])
    json.dump(dict(res),open('data/imgs.json','w'),indent=1)
    for k,v in res: print(k,len(v),[x.get('file',x.get('err')) for x in v][:8])
asyncio.run(main())
