import sys,os
from playwright.sync_api import sync_playwright
names=sys.argv[1:]
with sync_playwright() as p:
    b=p.chromium.launch(proxy={"server":os.environ["HTTPS_PROXY"]})
    for n in names:
        for vw,vh,suf,full in [(1366,850,"desk",False),(1366,850,"full",True),(390,844,"mob",False)]:
            pg=b.new_page(viewport={"width":vw,"height":vh},device_scale_factor=1)
            pg.goto(f"file:///home/claude/nk/mock/{n}.html"); pg.wait_for_timeout(1800)
            pg.screenshot(path=f"/home/claude/nk/mock/after_{n}_{suf}.png",full_page=full); pg.close()
    b.close()
