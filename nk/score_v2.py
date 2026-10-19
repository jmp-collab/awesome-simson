"""Vereinheitlichtes Scoring über alte und neue Leads -> data/all_v2.json"""
import json, re, os
from outreach_text import segment, hooks, SEG
OM = json.load(open("data/old_manual.json"))
exec(open("data/vis_v2.py").read())  # V, WHY, SPECIAL
GBP_NEW = json.load(open("data/gbp_new.json")) if os.path.exists("data/gbp_new.json") else {}
VIS3, SP3, WHY3 = {}, {}, {}
if os.path.exists("data/vis_b3.py"): exec(open("data/vis_b3.py").read())
IMP = {}
for f in ("data/imp_old.json", "data/imp_b12.json", "data/imp_b3.json"):
    if os.path.exists(f):
        for x in json.load(open(f)): IMP[x["name"]] = x

CORE = ["Stummstr","Stummplatz","Bahnhofstr","Hüttenbergstr","Lindenallee","Marienstr","Oberer Markt","Unterer Markt","Max-Braun","Brückenstr",
        "Lutherstr","Goethestr","Hebbelstr","Kleiststr","Irrgartenstr","Saarbrücker Str","Storchenplatz","Pasteurstr","Bürgermeister-Ludwig","Wilhelmstr","Boxbergweg","Wellesweilerstr"]
EASE = dict(liefer=16,gastro=15,lebensmittel=16,hotel=14,freizeit=15,spielhalle=15,beauty=17,praxis=13,apotheke=13,kfz=16,handwerk=16,handel=16,bestatter=15,beratung=12)
VAL = dict(liefer=12,gastro=11,lebensmittel=9,hotel=9,freizeit=9,spielhalle=9,beauty=10,praxis=8,apotheke=8,kfz=9,handwerk=9,handel=8,bestatter=7,beratung=6)

def kind(r):
    st = r.get("status")
    t = (r.get("text") or "")
    if st == 200: return "live"
    if st == 403 and "Sicherheits" in t: return "bot"
    if st in (502, 405) or (r.get("error") and ("TUNNEL" in r["error"] or "CERT" in r["error"] or "SSL" in r["error"] or "Timeout" in r["error"])) or "agent-proxy relay" in t:
        return "http"
    if st in (500, 503, 404): return "defekt"
    return "http"

BADOWN = ("entertainment","ltd","limited","n.v.","b.v.","s.r.o","holding","marketing","media","hosting","godaddy","plesk")
def owner_ok(o):
    if not o: return ""
    if any(b in o.lower() for b in BADOWN): return ""
    o = re.sub(r"^.*?(Geschäftsführer(in)?|Inhaber(in)?|Meister(in)?|Dachdeckermeister|Elektromeister|Malermeister|Vertreten durch)\s*:?\s*", "", o)
    o = re.sub(r"^(Frau|Herrn|Herr|Apotheker(in)?|Dr\.? med\.?( dent\.?| vet\.?)?|Dipl\.-?\w+\.?|Rechtsanwalt|Rechtsanwältin|Steuerberater(in)?|Inhaber(in)?|Zahnärztin|Zahnarzt)\s+", "", o.strip())
    o = re.sub(r"\s+(e\.\s?K(fr|fm)?\.?|e\.K\.|GmbH.*|\(.*)$", "", o).strip(" ,.;:")
    w = o.split()
    if not (2 <= len(w) <= 4): return ""
    if not all(x[:1].isupper() for x in w): return ""
    if any(x.lower() in ("gmbh","ug","kg","verantwortlich","betreiber","geschäftsführung","sgesellschaft","website","seiten","der","die","und","inhalt") for x in w): return ""
    return o

def gender(role, raw):
    t = f"{role} {raw}".lower()
    if re.search(r"\bfrau\b|inhaberin|geschäftsführerin|apothekerin|betreiberin|ärztin|beraterin", t): return "f"
    if re.search(r"\bherrn?\b", t): return "m"
    return ""

def pick_mail(imp, url):
    ms = [m for m in (imp.get("emails", []) if imp else []) if m.count("@") == 1 and "." in m.split("@")[1]]
    dom = re.sub(r"^https?://(www\.)?", "", url or "").split("/")[0].lower()
    base = dom.rsplit(".", 1)[0].split(".")[-1] if dom else ""
    own = [m for m in ms if base and base in m.split("@")[1]]
    generic = [m for m in ms if any(p in m.split("@")[1] for p in ("t-online","gmx","web.de","outlook","gmail","yahoo","online.de","arcor","freenet"))]
    return (own or generic or [""])[0]

def score(r, vis, special, gbp, src):
    seg = segment(r["branch"]); k = kind(r)
    r.update(seg=seg, status_kind=k, live=(k == "live"), quelle=src)
    r["fb"] = bool(r.get("facebook")); r["ig"] = bool(r.get("instagram"))
    if gbp: r["g_avg"], r["g_n"] = gbp
    a = vis if vis is not None else (14 if k == "http" else 10 if k == "bot" else 18 if k == "defekt" else 10)
    if k == "live":
        if not r.get("viewport") or (r.get("mob_scrollW") or 390) > 400: a += 5
        if (r.get("load_s") or 0) >= 14.8: a += 3
    if k == "http": a += 8
    if special: a += 5
    a = min(a, 40)
    b = EASE[seg] - (2 if "lieferando" in (r.get("text") or "").lower() else 0) - (2 if (r.get("words") or 0) > 1500 else 0)
    plz = r.get("plz") or ("66538" if "66538" in r.get("addr", "") else "")
    c = VAL[seg] + (6 if any(x in r.get("addr", "") for x in CORE) else 4 if plz == "66538" else 2)
    gn = r.get("g_n")
    c += (7 if gn >= 150 else 5 if gn >= 50 else 3 if gn >= 10 else 1) if gn else 2
    c = min(c, 25)
    d = 0
    if k == "live":
        if not r["fb"] and not r["ig"]: d += 4
        if not r.get("localbiz"): d += 3
        if not r.get("booking"): d += 3
    else:
        d += 6
    ga = r.get("g_avg")
    if gn is not None and (gn < 20 or (ga or 5) < 4.0): d += 3
    if "lieferando" in (r.get("text") or "").lower(): d += 2
    d = min(d, 15)
    r.update(A=a, B=b, C=c, D=d, total=a + b + c + d)
    H = ([special] if special else []) + hooks(r)
    r["hook1"] = H[0] if H else ""
    r["hook2"] = H[1] if len(H) > 1 else (H[0] if H and not special else "")
    imp = IMP.get(r["name"], {})
    raw = imp.get("owner", ""); r["owner"] = owner_ok(raw); r["gender"] = gender(imp.get("owner_role", ""), raw)
    r["email"] = pick_mail(imp, r.get("url")); r["imp_url"] = imp.get("imp_url", "")
    if special and special.startswith("Unter Ihrer Domain"):
        r["owner"] = ""; r["gender"] = ""; r["email"] = ""; r["imp_url"] = ""
    if r["status_kind"] in ("http", "defekt") and not r["hook1"]:
        r["hook1"] = "Ihre Website ließ sich bei meinem Test nicht verschlüsselt aufrufen."
    return r

out = []
old = json.load(open("data/merged.json"))
for r in old:
    n = r["name"]
    sp = None
    if n == "Markt Apotheke": sp = "Oben auf Ihrer Startseite steht noch der Vorlagentext 'Ihr Name Ihr Slogan'."
    if n == "aqua bar lounge club": sp = "Unter aqua-nk.de erscheint derzeit nur eine Standardseite des Hosters, keine Website."
    if n == "Damaskus Haus": sp = "Ihre Website wird von Lieferando betrieben, nicht von Ihnen."
    r["plz"] = "66538"; r["addr"] = r["addr"] + ", 66538 Neunkirchen"
    out.append(score(r, OM["VIS"].get(n), sp, OM["GBP"].get(n) or GBP_NEW.get(n), "Liste 1"))
    out[-1]["note"] = OM["NOTE"].get(n, "")
okn = json.load(open("data/okorder_v2.json"))
idx = {n: i for i, n in enumerate(okn)}
for b in ("b1", "b2", "b3"):
    f = f"data/crawl_{b}.json"
    if not os.path.exists(f): continue
    for r in json.load(open(f)):
        i = idx.get(r["name"])
        vis = V[i] if i is not None and i < len(V) else None
        why = WHY.get(i) if i is not None else None
        if i is not None and vis is None and not why: why = "ausgeschlossen"
        if b == "b3" and r.get("status") == 200 and r["name"] in VIS3: vis = VIS3[r["name"]]
        sp = SPECIAL.get(i) if i is not None else None
        if b == "b3": sp = SP3.get(r["name"]); why = WHY3.get(r["name"])
        rr = score(r, vis, sp, GBP_NEW.get(r["name"]), "Liste 2")
        rr["excluded"] = why or ""
        out.append(rr)
for r in out: r.setdefault("excluded", "")
# Duplikate über Domain
seen = set()
for r in sorted(out, key=lambda x: -x["total"]):
    d = re.sub(r"^https?://(www\.)?", "", (r.get("final") or r["url"]).lower()).split("/")[0]
    if d in seen and not r["excluded"]: r["excluded"] = "Dublette"
    seen.add(d)
act = sorted([r for r in out if not r["excluded"]], key=lambda x: (-x["total"], -x["A"]))
for i, r in enumerate(act, 1): r["rank"] = i
def label(r):
    if r["excluded"]: return r["excluded"]
    if r["status_kind"] != "live": return "Nicht prüfbar"
    if VAL[r["seg"]] >= 11 and r["A"] >= 18: return "Umsatzhebel"
    if r["A"] >= 18 and r["B"] >= 14: return "Quick Win"
    if VAL[r["seg"]] <= 6: return "Langläufer"
    if r["A"] >= 12: return "Solide Chance"
    return "Niedrige Priorität"
for r in out: r["label"] = label(r)
for r in out: r["text"] = (r.get("text") or "")[:300]
json.dump(out, open("data/all_v2.json", "w"), ensure_ascii=False, indent=1)
print(len(out), "aktiv", len(act))
for r in act[:25]: print(r["rank"], r["name"][:40], r["total"], r["A"], r["label"], "|", r["hook1"][:70])
