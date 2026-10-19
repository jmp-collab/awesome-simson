"""Druckbarer Website-Check (A4, 2 Seiten) je Lead als Leave-behind fuer den Besuch.
Aufruf: python3 wave/check_pdf.py [KURZ ...]  -> /home/claude/nk/out/checks/NN_<k>_Website-Check.pdf"""
import json, os, sys, math, base64, hashlib, datetime, html
from playwright.sync_api import sync_playwright

SITE = "/home/claude/site"; OUT = "/home/claude/nk/out/checks"; os.makedirs(OUT, exist_ok=True)
TOP = json.load(open(f"{SITE}/data/top10.json", encoding="utf-8"))
ANA = json.load(open(f"{SITE}/data/analyse.json", encoding="utf-8"))
C = json.load(open(f"{SITE}/config.json", encoding="utf-8"))
E = lambda s: html.escape(str(s or ""))
FONT = f"{SITE}/assets/fonts"

def code_for(k):
    salt = C.get("code_salt", "saarseiten-2026")
    h = hashlib.sha256(f"{salt}:{k}".encode()).digest()
    return base64.b32encode(h).decode().lower()[:6]

def small(p, w=900):
    from PIL import Image
    import io
    if not os.path.exists(p): return ""
    im = Image.open(p).convert("RGB"); im.thumbnail((w, w * 2))
    buf = io.BytesIO(); im.save(buf, "JPEG", quality=72, optimize=True)
    return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()

def b64(p, mime):
    return f"data:{mime};base64," + base64.b64encode(open(p, "rb").read()).decode() if os.path.exists(p) else ""

PL = {"Auftrag": "Aufträge", "Termin": "Termine", "Einkauf": "Einkäufe", "Behandlung": "Behandlungen", "Vermietung": "Vermietungen", "Neukunde": "Neukunden", "Gastronomie-Kunde": "Gastronomie-Kunden", "Auftrag (Schlüssel, Schloss, Tresor)": "Aufträge"}
PLD = {"Auftrag": "Aufträgen", "Termin": "Terminen", "Einkauf": "Einkäufen", "Behandlung": "Behandlungen", "Vermietung": "Vermietungen", "Neukunde": "Neukunden", "Gastronomie-Kunde": "Gastronomie-Kunden"}
def eur(n): return f"{int(round(n)):,}".replace(",", ".") + " €"

def beispiel(r):
    t, n, w, p = r["typ"], r["anzahl"], r["wert"], r["preis"]
    if t == "portal":
        m = n * w * r["prov"] / 100
        return f"Bei {n} Bestellungen im Monat über Ihre Domain zu je {w} € und {r['prov']} % Provision sparen Sie rund {eur(m)} im Monat, {eur(m * 12)} im Jahr. Die Website ist nach etwa {max(1, math.ceil(p / max(m, 1)))} Monaten bezahlt."
    if t == "unterkunft":
        m = n * w * r["prov"] / 100 * 0.5
        return f"Wenn von {n} Portal-Nächten im Monat zu {w} € die Hälfte direkt bucht, sparen Sie bei {r['prov']} % Provision rund {eur(m)} im Monat, {eur(m * 12)} im Jahr."
    if t == "gast":
        return f"{n} zusätzliche Gäste im Monat zu je {w} € bringen {eur(n * w)} im Monat, {eur(n * w * 12)} im Jahr. Der Website-Preis entspricht {math.ceil(p / w)} Gästen."
    if t == "abo":
        return f"{n} zusätzliche Anmeldungen im Jahr zu {w} € monatlich bringen {eur(n * w * 12)} im ersten Jahr. Die Website ist mit {math.ceil(p / (w * 12))} Anmeldungen bezahlt."
    if t == "zeit":
        h = n * 2 * 21 / 60 * 0.5
        return f"Wenn die Website die Hälfte von {n} Standardanrufen am Tag beantwortet, gewinnt Ihr Team rund {h:.1f} Stunden im Monat.".replace(".", ",", 1)
    be = math.ceil(p / w); ein = r["einheit"].split(" (")[0]
    return f"{n} zusätzliche {PL.get(ein, ein)} im Jahr zu je {eur(w)} sind {eur(n * w)} Mehrumsatz. Der Website-Preis entspricht {be} {ein if be == 1 else PLD.get(ein, ein)}."

CSS = """
@font-face{font-family:H;src:url(%(h)s)}@font-face{font-family:B;src:url(%(b)s)}
@page{size:A4;margin:14mm 14mm 14mm 14mm}
*{box-sizing:border-box}body{font-family:B,system-ui,sans-serif;color:#1c1f22;font-size:10.2pt;line-height:1.42;margin:0}
h1,h2,h3{font-family:H,system-ui,sans-serif;margin:0}
.top{display:flex;justify-content:space-between;align-items:center;border-bottom:2px solid #b4441c;padding-bottom:6px;margin-bottom:12px}
.brand{font:700 13pt H;color:#b4441c}.muted{color:#5c6066}
.head{display:flex;gap:16px;align-items:center}
.dial{width:96px;height:96px;border-radius:50%%;background:conic-gradient(%(col)s calc(%(s)s*1%%),#ddd 0);display:grid;place-items:center;flex:none}
.dial div{width:76px;height:76px;border-radius:50%%;background:#fff;display:grid;place-items:center;text-align:center}
.dial b{font:700 22pt/1 H}.dial small{display:block;font-size:7.5pt}
h1{font-size:18pt;line-height:1.15}
.f{border:1px solid #d6d2ca;border-left:5px solid var(--c);border-radius:8px;padding:7px 10px;margin:6px 0;break-inside:avoid}
.f h3{font-size:10.8pt;margin-bottom:2px}.chip{font:700 7pt monospace;color:#fff;background:var(--c);padding:2px 6px;border-radius:10px;margin-right:6px;vertical-align:1px}
.f p{margin:1px 0}.bel{font-family:monospace;font-size:8.3pt;color:#444}.fix{color:#2f6b3f;font-weight:700}
.imgs{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin:10px 0}.imgs figure{margin:0}.imgs img{width:100%%;border:1px solid #ccc;border-radius:6px}
.imgs figcaption{font-size:8pt;color:#5c6066}
.box{background:#f6efe9;border-radius:8px;padding:10px 12px;margin-top:10px;break-inside:avoid}
ul{margin:4px 0 0 16px;padding:0}li{margin:2px 0}
.foot{display:flex;gap:14px;align-items:center;margin-top:12px;border-top:1px solid #ddd;padding-top:10px;break-inside:avoid}
.foot img{width:84px;height:84px}
.pb{break-before:page}
"""

def page(nr, t):
    k = t["k"]; a = ANA[k]; code = code_for(k)
    s = a["score"]; col = "#a3271b" if s < 50 else "#a86a00" if s < 75 else "#2f6b3f"
    sev = {"hoch": ("Wichtig", "#a3271b"), "mittel": ("Mittel", "#a86a00"), "niedrig": ("Gering", "#2b3238")}
    F = [f for f in a["befunde"] if f["sev"] != "niedrig"][:6]
    low = [f for f in a["befunde"] if f["sev"] == "niedrig"]
    fx = "".join(f'<div class="f" style="--c:{sev[f["sev"]][1]}"><h3><span class="chip">{sev[f["sev"]][0]}</span>{E(f["titel"])}</h3>'
                 f'<p class="bel">Gemessen: {E(f["beleg"])}</p><p><b>Was Sie das kostet:</b> {E(f["folge"])}</p><p class="fix">Lösung: {E(f["fix"])}</p></div>' for f in F)
    lows = ", ".join(E(f["titel"]) for f in low)
    sicht = "".join(f"<li>{E(x)}</li>" for x in a.get("sicht", [])[:3])
    nutzen = "".join(f"<li>{E(x)}</li>" for x in a.get("nutzen", []))
    vd = small(f"{SITE}/dist/assets/v/{k}-vorher-desk.webp"); nd = small(f"{SITE}/dist/assets/v/{k}-nachher-desk.webp")
    qr = next((f"{SITE}/qr/{q}" for q in os.listdir(f"{SITE}/qr") if q.startswith(k + "_")), "")
    qri = b64(qr, "image/png") if qr else ""
    url = f"{C['base_url'].replace('https://', '')}/v/{code}"
    datum = datetime.date.fromisoformat(a["datum"]).strftime("%d.%m.%Y")
    preis = t["p"][0]
    css = CSS % dict(h=f"file://{FONT}/familjen-grotesk-latin-700-normal.woff2", b=f"file://{FONT}/atkinson-hyperlegible-latin-400-normal.woff2", col=col, s=s)
    body = f"""<div class="top"><span class="brand">{E(C['brand'])}</span><span class="muted">Website-Check vom {datum} · persönlich für {E(t['name'])}</span></div>
<div class="head"><div class="dial"><div><div><b>{s}</b><small>von 100</small></div></div></div>
<div><h1>Ihr Website-Check: {E(t['name'])}</h1><p class="muted" style="margin:4px 0 0">{E(t.get('url', ''))} · gemessen am Handy und am Computer, dazu persönliche Durchsicht. {len(F)} wichtige Punkte{', ' + str(len(low)) + ' kleinere' if low else ''}.</p></div></div>
<h2 style="font-size:12.5pt;margin:12px 0 2px">Was an Ihrer Seite heute Kunden kostet</h2>{fx}
{f'<p class="muted" style="font-size:8.6pt;margin-top:4px">Kleinere Punkte: {lows}.</p>' if lows else ''}
<div class="pb"></div>
<div class="top"><span class="brand">{E(C['brand'])}</span><span class="muted">{E(t['name'])} · Seite 2</span></div>
{f'<h2 style="font-size:12.5pt">Bei der Durchsicht aufgefallen</h2><ul>{sicht}</ul>' if sicht else ''}
<div class="imgs"><figure><img src="{vd}"><figcaption>Heute</figcaption></figure><figure><img src="{nd}"><figcaption>Entwurf mit Ihren eigenen Inhalten</figcaption></figure></div>
<div class="box"><h2 style="font-size:12.5pt">Was Sie konkret davon haben</h2><ul>{nutzen}</ul>
<p style="margin:8px 0 0"><b>Rechenbeispiel:</b> {E(beispiel(a['rechner']))}</p>
<p class="muted" style="font-size:8pt;margin:4px 0 0">Beispielwerte, keine Zusage. Auf Ihrer Vorschauseite können Sie mit Ihren eigenen Zahlen rechnen.</p></div>
<div class="box" style="background:#eef3ef"><b>Ihr Preis für genau diesen Entwurf:</b> {E(preis)} einmalig, fertig online inklusive Impressum, Datenschutz und Google-Profil. Betreuung danach ab 29 € im Monat.</div>
<div class="foot">{f'<img src="{qri}">' if qri else ''}<div><b>Ihre persönliche Vorschau ansehen</b><br>QR-Code scannen oder {E(url)} öffnen.<br>Mit Regler zum Vergleich heute und Entwurf, und einem Rechner für Ihre eigenen Zahlen.<br><span class="muted">Jean · Webdesign aus Neunkirchen</span></div></div>"""
    return f"<!doctype html><html lang=de><head><meta charset=utf-8><style>{css}</style></head><body>{body}</body></html>"

def main():
    want = set(sys.argv[1:])
    nums = {}
    for i, t in enumerate(TOP, 1): nums[t["k"]] = i
    with sync_playwright() as p:
        b = p.chromium.launch(); ctx = b.new_context(); pg = ctx.new_page()
        n = 0
        for t in TOP:
            k = t["k"]
            if want and k not in want: continue
            if not ANA.get(k) or ANA[k].get("score") is None: continue
            fn = f"{OUT}/{nums[k]:02d}_{k}_Website-Check.pdf"
            tmp = f"/tmp/claude-0/wc_{k}.html"; os.makedirs("/tmp/claude-0", exist_ok=True)
            open(tmp, "w", encoding="utf-8").write(page(nums[k], t))
            pg.goto(f"file://{tmp}"); pg.wait_for_timeout(300)
            pg.pdf(path=fn, format="A4", print_background=True)
            from pypdf import PdfReader, PdfWriter
            rd = PdfReader(fn); w = PdfWriter()
            for pp in rd.pages: w.add_page(pp)
            w.add_metadata({"/Title": f"Website-Check {t['name']}", "/Author": "Saarseiten", "/Creator": "Saarseiten", "/Producer": "Saarseiten"})
            w.write(fn)
            n += 1
        b.close()
    print("PDFs:", n)

if __name__ == "__main__":
    main()
