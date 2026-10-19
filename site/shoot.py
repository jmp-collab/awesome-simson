import asyncio, sys, os
from playwright.async_api import async_playwright
from PIL import Image
D = os.path.dirname(os.path.abspath(__file__))
async def main(mode):
    async with async_playwright() as p:
        b = await p.chromium.launch()
        if mode == "concepts":
            for s in ["imbiss-glutstueck","dachbau-ferrum","physio-lindwerk"]:
                pg = await b.new_page(viewport={"width":1280,"height":800})
                await pg.goto(f"file://{D}/dist/konzepte/{s}.html"); await pg.wait_for_timeout(400)
                await pg.screenshot(path=f"/tmp/{s}.png")
                Image.open(f"/tmp/{s}.png").convert("RGB").save(f"{D}/assets/concepts/{s}.webp","WEBP",quality=80)
        else:
            out = sys.argv[2]; os.makedirs(out, exist_ok=True)
            for name in sys.argv[3:]:
                for dev, vp in (("desk",{"width":1366,"height":900}),("mob",{"width":390,"height":844})):
                    ctx = await b.new_context(viewport=vp, device_scale_factor=1 if dev=="desk" else 2)
                    pg = await ctx.new_page(); await pg.goto(f"file://{D}/dist/{name}"); await pg.wait_for_timeout(500)
                    await pg.screenshot(path=f"{out}/{name.replace('/','_')}_{dev}.png", full_page=True)
                    w = await pg.evaluate("document.documentElement.scrollWidth")
                    if w > vp["width"]: print("OVERFLOW", name, dev, w)
                    await ctx.close()
        await b.close()
asyncio.run(main(sys.argv[1]))
