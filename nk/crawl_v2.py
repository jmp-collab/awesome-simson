"""Crawl neue Leads: IN (pipe: name|branch|street|plz|url|tel) -> OUT json + Screenshots"""
import asyncio, json, os, re, sys, time
from playwright.async_api import async_playwright
PROXY=os.environ.get("HTTPS_PROXY"); JS=open("crawl_js.txt").read()
rows=[l.rstrip("\n").split("|") for l in open(sys.argv[1],encoding="utf-8") if l.count("|")==5]
async def one(br,r,sem):
    name,branch,street,plz,url,tel=[x.strip() for x in r]
    slug=re.sub(r"[^a-z0-9]+","-",name.lower()).strip("-")[:40]
    res=dict(name=name,branch=branch,addr=f"{street}, {plz} Neunkirchen".strip(", "),plz=plz,url=url,tel=tel,slug=slug)
    async with sem:
        ctx=await br.new_context(viewport={"width":1366,"height":850},locale="de-DE",user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0 Safari/537.36")
        pg=await ctx.new_page()
        try:
            t0=time.time()
            resp=await pg.goto(re.sub(r"^http://","https://",url),timeout=30000,wait_until="load")
            res["load_s"]=round(time.time()-t0,1); await pg.wait_for_timeout(1500)
            res["status"]=resp.status if resp else None; res["final"]=pg.url
            res["https"]=pg.url.startswith("https"); res["lastmod"]=(resp.headers.get("last-modified") if resp else "") or ""
            res.update(await pg.evaluate(JS))
            await pg.screenshot(path=f"shots/{slug}_desk.png")
            await pg.set_viewport_size({"width":390,"height":844}); await pg.wait_for_timeout(700)
            res["mob_scrollW"]=await pg.evaluate("document.documentElement.scrollWidth")
            await pg.screenshot(path=f"shots/{slug}_mob.png")
        except Exception as e:
            res["error"]=str(e)[:160]
        await ctx.close()
    print(("ERR " if "error" in res else "ok  ")+name,flush=True); return res
async def main():
    async with async_playwright() as p:
        br=await p.chromium.launch(proxy={"server":PROXY} if PROXY else None)
        sem=asyncio.Semaphore(10)
        out=await asyncio.gather(*[one(br,r,sem) for r in rows]); await br.close()
    json.dump(out,open(sys.argv[2],"w"),ensure_ascii=False,indent=1)
asyncio.run(main())
