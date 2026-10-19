"""Rendert eine Welle: Entwurf-HTML, Screenshots, Vorher/Nachher-Druckbild, Vorschau-Seiten, Excel und ZIP.
Aufruf: python3 wave/render.py WELLENNR KEY1 KEY2 ...   (KEY = Dateiname in wave/content ohne .json)"""
import json, os, sys, shutil, datetime, zipfile, subprocess
from jinja2 import Template
from PIL import Image, ImageDraw, ImageFont
from playwright.sync_api import sync_playwright

B = "/home/claude/nk"; S = "/home/claude/site"
WAVE = int(sys.argv[1]); KEYS = sys.argv[2:]
TODAY = datetime.date.today().strftime("%d.%m.%Y")
THEMES = {
 "doener": dict(fontlink="Bricolage+Grotesque:wght@500;700;800&family=Inter:wght@400;500;700", body="Inter,sans-serif",
   bg="#fbf6ef", ink="#1d1410", mut="#6f5d52", acc="#e8452c", acc_ink="#fff", hero="#1d1410", hero_ink="#fff7ee", card="#ffffff", line="#ecdccb",
   logo="800 25px 'Bricolage Grotesque'", h1="800 60px/1.0 'Bricolage Grotesque'", h1m="40px", h2="800 34px 'Bricolage Grotesque'", badge="800 34px 'Bricolage Grotesque'", deco="800 300px 'Bricolage Grotesque'", radius="999px"),
 "gelato": dict(fontlink="Fraunces:opsz,wght@9..144,600;9..144,800&family=DM+Sans:wght@400;500;700", body="'DM Sans',sans-serif",
   bg="#fff8f1", ink="#2a1b14", mut="#7a6355", acc="#d9485f", acc_ink="#fff", hero="#f6d9c4", hero_ink="#2a1b14", card="#ffffff", line="#f0dccd",
   logo="800 25px Fraunces", h1="800 60px/1.02 Fraunces", h1m="40px", h2="800 34px Fraunces", badge="800 34px Fraunces", deco="800 280px Fraunces", radius="14px"),
 "papier": dict(fontlink="Literata:opsz,wght@7..72,600;7..72,800&family=Work+Sans:wght@400;500;700", body="'Work Sans',sans-serif",
   bg="#f7f5f0", ink="#1f2a36", mut="#5f6b77", acc="#2f6fdf", acc_ink="#fff", hero="#1f2a36", hero_ink="#f7f5f0", card="#ffffff", line="#e2ded4",
   logo="800 24px Literata", h1="800 56px/1.05 Literata", h1m="38px", h2="800 32px Literata", badge="800 32px Literata", deco="800 260px Literata", radius="10px"),
 "metall": dict(fontlink="Archivo:wght@500;700;800;900&family=Inter:wght@400;500;600", body="Inter,sans-serif",
   bg="#f2f3f4", ink="#14181c", mut="#5c6670", acc="#f2a900", acc_ink="#14181c", hero="#1b2128", hero_ink="#ffffff", card="#ffffff", line="#dde1e5",
   logo="900 24px Archivo", h1="900 56px/1.02 Archivo", h1m="38px", h2="800 34px Archivo", badge="900 36px Archivo", deco="900 280px Archivo", radius="6px"),
 "beauty": dict(fontlink="Cormorant+Garamond:wght@600;700&family=Jost:wght@400;500;600", body="Jost,sans-serif",
   bg="#fbf5f3", ink="#2b1f22", mut="#7d6a6e", acc="#b24d6b", acc_ink="#fff", hero="#efdcd6", hero_ink="#2b1f22", card="#ffffff", line="#eedfdb",
   logo="700 28px 'Cormorant Garamond'", h1="700 62px/1.0 'Cormorant Garamond'", h1m="42px", h2="700 36px 'Cormorant Garamond'", badge="700 36px 'Cormorant Garamond'", deco="700 260px 'Cormorant Garamond'", radius="999px"),
 "praxis": dict(fontlink="Outfit:wght@500;700;800&family=Atkinson+Hyperlegible:wght@400;700", body="'Atkinson Hyperlegible',sans-serif",
   bg="#f3f8f7", ink="#13302c", mut="#4f6a66", acc="#0f8b74", acc_ink="#fff", hero="#13302c", hero_ink="#ffffff", card="#ffffff", line="#d7e7e3",
   logo="800 24px Outfit", h1="800 56px/1.04 Outfit", h1m="38px", h2="800 32px Outfit", badge="800 34px Outfit", deco="800 260px Outfit", radius="12px"),
 "event": dict(fontlink="Unbounded:wght@600;800&family=Inter:wght@400;500;700", body="Inter,sans-serif",
   bg="#0e0e14", ink="#f1effa", mut="#a4a1b8", acc="#b06cff", acc_ink="#0e0e14", hero="#07070b", hero_ink="#ffffff", card="#171722", line="#2a2a3a",
   logo="800 22px Unbounded", h1="800 52px/1.05 Unbounded", h1m="34px", h2="800 30px Unbounded", badge="800 32px Unbounded", deco="800 240px Unbounded", radius="8px"),
 "spa": dict(fontlink="Marcellus&family=Nunito+Sans:wght@400;600;800", body="'Nunito Sans',sans-serif",
   bg="#f7f3ea", ink="#25321f", mut="#6a7462", acc="#a8742a", acc_ink="#fff", hero="#25321f", hero_ink="#f7f3ea", card="#fffdf8", line="#e6dfcf",
   logo="400 26px Marcellus", h1="400 56px/1.05 Marcellus", h1m="38px", h2="400 34px Marcellus", badge="400 34px Marcellus", deco="400 240px Marcellus", radius="999px"),
}
TPL = Template(open(f"{B}/wave/mock_tpl.html", encoding="utf-8").read())

def font(sz, bold=True):
    for f in ["/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"]:
        if os.path.exists(f): return ImageFont.truetype(f, sz)
    return ImageFont.load_default()

def composite(c, vor, nach, out):
    W, H = 2852, 1060; im = Image.new("RGB", (W, H), "#f3f1ec"); d = ImageDraw.Draw(im)
    d.text((40, 28), f"{c['name']}  ·  {c['addr']}", fill="#1c1c1c", font=font(32))
    d.text((40, 76), f"VORHER: aktuelle Website (Screenshot {TODAY})", fill="#b3261e", font=font(22))
    d.text((1446, 76), "NACHHER: Entwurf / Vorschau", fill="#1f7a3d", font=font(22))
    for src, x in ((vor, 40), (nach, 1446)):
        s = Image.open(src).convert("RGB"); s = s.crop((0, 0, s.width, min(s.height, int(s.width * 850 / 1366))))
        s = s.resize((1366, int(s.height * 1366 / s.width))); im.paste(s, (x, 110))
    d.text((40, 990), "Vorschau mit echten Inhalten des Betriebs. Nicht veröffentlicht.", fill="#666", font=font(20, False))
    im.save(out, "JPEG", quality=88)

def main():
    st = json.load(open(f"{B}/wave/state.json"))
    top = json.load(open(f"{S}/data/top10.json", encoding="utf-8"))
    vt = json.load(open(f"{S}/data/vorschau_texte.json", encoding="utf-8"))
    nr0 = len([t for t in top if t.get("welle", 0) < WAVE])
    pitch_dir = f"{B}/out/welle_{WAVE:02d}"; os.makedirs(pitch_dir, exist_ok=True)
    rows = []
    with sync_playwright() as p:
        b = p.chromium.launch(proxy={"server": os.environ["HTTPS_PROXY"]})
        for i, k in enumerate(KEYS):
            c = json.load(open(f"{B}/wave/content/{k}.json", encoding="utf-8")); c["k"] = k
            html = TPL.render(c=c, t=THEMES[c["theme"]])
            open(f"{B}/mock/{k}.html", "w", encoding="utf-8").write(html)
            for vw, vh, suf, full, dsf in [(1366, 850, "desk", False, 1), (1366, 850, "full", True, 1), (390, 844, "mob", False, 2)]:
                pg = b.new_page(viewport={"width": vw, "height": vh}, device_scale_factor=dsf)
                pg.goto(f"file://{B}/mock/{k}.html"); pg.wait_for_timeout(2200)
                pg.screenshot(path=f"{B}/mock/after_{k}_{suf}.png", full_page=full); pg.close()
            nr = nr0 + i + 1; pre = f"{pitch_dir}/{nr:02d}_{k}"
            raw = f"{B}/wave/raw/{c['slug']}"
            for st_, src in (("vorher_desk", f"{raw}_vorher_desk.png"), ("vorher_mob", f"{raw}_vorher_mob.png"),
                             ("nachher_desk", f"{B}/mock/after_{k}_desk.png"), ("nachher_mob", f"{B}/mock/after_{k}_mob.png"), ("nachher_full", f"{B}/mock/after_{k}_full.png")):
                Image.open(src).convert("RGB").save(f"{pre}_{st_}.jpg", "JPEG", quality=85)
            composite(c, f"{raw}_vorher_desk.png", f"{B}/mock/after_{k}_desk.png", f"{pre}_VORHER-NACHHER.jpg")
            # Webp für Vorschau-Seiten
            for state, dev, src in (("vorher", "desk", f"{raw}_vorher_desk.png"), ("vorher", "mob", f"{raw}_vorher_mob.png"),
                                    ("nachher", "desk", f"{B}/mock/after_{k}_desk.png"), ("nachher", "mob", f"{B}/mock/after_{k}_mob.png")):
                im = Image.open(src).convert("RGB"); w = 1280 if dev == "desk" else 480
                if im.width > w: im = im.resize((w, int(im.height * w / im.width)), Image.LANCZOS)
                im = im.crop((0, 0, im.width, min(im.height, int(im.width * (10 / 16 if dev == "desk" else 17 / 9)))))
                im.save(f"{S}/assets/v/{k}-{state}-{dev}.webp", "WEBP", quality=78, method=6)
            entry = {x: c[x] for x in ("name", "branche", "url", "g", "label", "visit", "audit", "hebel", "p", "paket", "svc", "open", "obj")}
            entry.update(k=k, addr=c["addr"].split(" · ")[0], tel=c["tel"], welle=WAVE)
            top = [t for t in top if t["k"] != k] + [entry]
            vt[k] = {"obs": c["obs"], "neu": c["neu"]}
            rows.append((nr, c, entry))
            print("gerendert", k, flush=True)
        b.close()
    json.dump(top, open(f"{S}/data/top10.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    json.dump(vt, open(f"{S}/data/vorschau_texte.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    subprocess.run(["python3", f"{S}/build.py"], check=True)
    codes = {l.split(";")[1]: l.split(";")[0] for l in open(f"{S}/vorschau-codes.csv", encoding="utf-8").read().splitlines()[1:]}
    # Pitch-Blatt als Markdown pro Welle
    md = [f"# Welle {WAVE}: {len(rows)} neue Leads ({TODAY})\n"]
    for nr, c, e in rows:
        code = codes.get(c["name"], "")
        md += [f"## {nr:02d} {c['name']}", f"- Branche: {c['branche']} · {c['addr']} · Tel. {c['tel']}", f"- Website: {c['url']} · Google: {c['g']} · Einordnung: {c['label']}",
               f"- Vorschau-Code: `{code}` · QR: site/qr/{c['k']}_{code}.png", f"- Besuchszeit: {c['visit']}", "", "**Befund**"] + [f"- {a}" for a in c["audit"]] + [
               "", f"**Hebel:** {c['hebel']}", "", f"**Preis:** Website {c['p'][0]} · Paket mit Branchenfunktion {c['p'][1]} · Betreuung {c['p'][2]} im Monat",
               f"**Paket:** {c['paket']}", "", "**Passende Zusatzleistungen**"] + [f"- {s}" for s in c["svc"]] + [
               "", f"**Einstieg im Laden:** {c['open']}", f"**Einwand und Antwort:** {c['obj']}", ""]
    open(f"{pitch_dir}/Welle_{WAVE:02d}_Gespraechsmappe.md", "w", encoding="utf-8").write("\n".join(md))
    for nr, c, e in rows:
        code = codes.get(c["name"], "")
        q = f"{S}/qr/{c['k']}_{code}.png"
        if os.path.exists(q): shutil.copy(q, f"{pitch_dir}/{nr:02d}_{c['k']}_QR_{code}.png")
    z = f"{B}/out/Welle_{WAVE:02d}_Vorher-Nachher.zip"
    with zipfile.ZipFile(z, "w", zipfile.ZIP_DEFLATED) as zf:
        for f in sorted(os.listdir(pitch_dir)): zf.write(f"{pitch_dir}/{f}", f"Welle_{WAVE:02d}/{f}")
        for nr, c, e in rows: zf.write(f"{B}/mock/{c['k']}.html", f"Welle_{WAVE:02d}/Entwurf-HTML/{c['k']}.html")
    st["wave"] = WAVE; st["done"] += [c["slug"] for _, c, _ in rows]
    st["queue"] = [q for q in st["queue"] if q not in st["done"]]
    json.dump(st, open(f"{B}/wave/state.json", "w"), indent=1)
    print("ZIP", z)

if __name__ == "__main__":
    main()
