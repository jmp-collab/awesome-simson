"""Neue Leads aus Gelbe Seiten (Kategorie x Ort) mit Website-Link.
Aufruf: python3 wave/harvest_gs.py ORT1,ORT2 BRANCHE1,BRANCHE2 > wave/new_leads.jsonl
Gibt nur Betriebe aus, deren Domain noch nicht in data/all_v2.json steht."""
import sys, re, json, base64, html, subprocess, urllib.parse
ALL = json.load(open("/home/claude/nk/data/all_v2.json"))
known = {re.sub(r"^https?://(www\.)?", "", (r.get("final") or r.get("url") or "")).split("/")[0].lower() for r in ALL}
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0 Safari/537.36"
SKIP = re.compile(r"(lidl|netto|aldi|rewe|edeka|kaufland|dm-|rossmann|sparkasse|volksbank|deutsche|telekom|vodafone|allianz|ergo|huk|debeka|lvm|provinzial|mcdonald|burger king|subway|fressnapf|obi|hornbach|globus|bauhaus|toom|tedi|kik|takko|fielmann|apollo|jet |shell|aral|esso|wasgau)", re.I)
def get(url):
    r = subprocess.run(["curl", "-sL", "--max-time", "25", "-A", UA, url], capture_output=True)
    return r.stdout.decode("utf-8", "ignore")
seen = set()
orte = sys.argv[1].split(","); branchen = sys.argv[2].split(",")
for ort in orte:
    for br in branchen:
        s = get(f"https://www.gelbeseiten.de/branchen/{urllib.parse.quote(br)}/{ort}")
        for b in s.split("<article")[1:]:
            m = re.search(r'data-wipe-name="Titel">([^<]+)</h2>', b)
            w = re.search(r'data-webseiteLink="([^"]+)"', b)
            if not m or not w: continue
            name = html.unescape(m.group(1)).strip()
            try: web = base64.b64decode(w.group(1) + "==").decode("utf-8", "ignore").strip()
            except Exception: continue
            dom = re.sub(r"^https?://(www\.)?", "", web).split("/")[0].lower()
            if not dom or dom in known or dom in seen or SKIP.search(name) or SKIP.search(dom): continue
            seen.add(dom)
            addr = re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", (re.search(r'mod-AdresseKompakt__adress-text">(.*?)</div>', b, re.S) or [None, ""])[1]))).strip()
            addr = re.sub(r"\s*\d+[.,]\d+\s*km.*$", "", addr).strip()
            tel = re.search(r'mod-TelefonnummerKompakt__phoneNumber[^>]*>([^<]+)<', b)
            tel = tel.group(1).strip() if tel else ""
            bb = re.search(r'besteBranche">\s*([^<]+?)\s*<', b)
            slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")[:40]
            print(json.dumps(dict(name=name, branch=(bb.group(1) if bb else br), addr=addr, tel=tel, url=web, slug=slug, ort=ort, q=br), ensure_ascii=False), flush=True)
