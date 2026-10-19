"""Playwright-Hilfe fuer Seiten ohne https.
Der Browser-Proxy der Arbeitsumgebung lehnt http:// ab (405/502). Diese Routen holen http-Anfragen
per requests (laeuft ueber denselben Proxy, aber als normaler Forward-Request) und liefern sie dem Browser aus.
Einbinden: sync:  ctx.route("http://**/*", httpfix.sync_handler)
           async: await ctx.route("http://**/*", httpfix.async_handler)"""
import asyncio, time
import requests

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0 Safari/537.36"
DROP = {"content-encoding", "transfer-encoding", "content-length", "connection"}


def _fetch(route):
    req = route.request
    KEEP = ("user-agent", "accept", "accept-language", "cookie", "referer", "content-type")
    h = {k: v for k, v in req.headers.items() if k.lower() in KEEP}
    if "Headless" in h.get("user-agent", "Headless"): h["user-agent"] = UA  # manche Server sperren HeadlessChrome
    for i in range(4):  # Proxy liefert gelegentlich 502/503 'upstream ...': kurz warten und erneut
        r = requests.request(req.method, req.url, headers=h, data=req.post_data_buffer, timeout=25,
                             allow_redirects=False, verify="/root/.ccr/ca-bundle.crt")
        if not (r.status_code >= 500 and b"upstream" in r.content[:300]): break
        time.sleep(2 + 2 * i)
    hdr = {k: v for k, v in r.headers.items() if k.lower() not in DROP}
    return dict(status=r.status_code, headers=hdr, body=r.content)


def sync_handler(route):
    try:
        route.fulfill(**_fetch(route))
    except Exception:
        try: route.abort()
        except Exception: pass


async def async_handler(route):
    try:
        res = await asyncio.get_running_loop().run_in_executor(None, _fetch, route)
        await route.fulfill(**res)
    except Exception:
        try: await route.abort()
        except Exception: pass
