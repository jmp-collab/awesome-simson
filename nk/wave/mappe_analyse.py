"""Interne Analyse-Mappe (Markdown) + Prioritaeten-Liste (CSV) fuer alle Leads.
Aufruf: python3 wave/mappe_analyse.py"""
import json, csv, math, re, sys
sys.path.insert(0, "/home/claude/nk/wave")
from check_pdf import beispiel, code_for
TOP = json.load(open("/home/claude/site/data/top10.json", encoding="utf-8"))
ANA = json.load(open("/home/claude/site/data/analyse.json", encoding="utf-8"))
OUT = "/home/claude/nk/out"

def jahr(r):
    t, n, w = r["typ"], r["anzahl"], r["wert"]
    if t == "portal": return n * w * r["prov"] / 100 * 12
    if t == "unterkunft": return n * w * r["prov"] / 100 * 0.5 * 12
    if t == "gast": return n * w * 12
    if t == "abo": return n * w * 12
    if t == "zeit": return n * 2 * 21 / 60 * 0.5 * 25 * 12
    return n * w

rows = []
md = ["# Analyse-Mappe: Was bei jedem Betrieb kaputt ist und was er davon hat", "",
      "Stand: automatisch gemessen (Handy und Computer) plus Sichtprüfung. Rechenbeispiele sind vorsichtige Beispielwerte, keine Zusagen.", "",
      "Reihenfolge: nach Priorität (viele wichtige Mängel, hoher Nutzen im Verhältnis zum Preis).", ""]
for i, t in enumerate(TOP, 1):
    k = t["k"]; a = ANA[k]; r = a["rechner"]
    hi = [f for f in a["befunde"] if f["sev"] == "hoch"]; mi = [f for f in a["befunde"] if f["sev"] == "mittel"]
    nutzen_j = jahr(r)
    prio = round((len(hi) * 2 + len(mi) + len(a.get("sicht", []))) * (1 + min(nutzen_j / max(r["preis"], 1), 5)), 1)
    rows.append(dict(nr=i, k=k, name=t["name"], branche=t["branche"], score=a["score"], wichtig=len(hi) + len(a.get("sicht", [])), mittel=len(mi),
                     nutzen_jahr=round(nutzen_j), preis_ab=r["preis"], prio=prio, code=code_for(k), tel=t.get("tel", ""), besuch=t.get("visit", "")))
rows.sort(key=lambda x: -x["prio"])
with open(f"{OUT}/Prioritaeten_alle_Leads.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys()), delimiter=";"); w.writeheader(); w.writerows(rows)
for rank, row in enumerate(rows, 1):
    k = row["k"]; t = next(x for x in TOP if x["k"] == k); a = ANA[k]
    md += [f"## {rank}. {t['name']} (Lead {row['nr']:02d}, Score {a['score']}/100)", "",
           f"- {t['branche']} · Tel. {t.get('tel', '')} · Besuch: {t.get('visit', '')}",
           f"- Vorschau: webdesign-neunkirchen.de/v/{row['code']} · Website-Check-PDF: checks/{row['nr']:02d}_{k}_Website-Check.pdf", "",
           "**Was kaputt ist (gemessen):**"]
    for f in [f for f in a["befunde"] if f["sev"] != "niedrig"][:5]:
        md.append(f"- [{f['sev']}] {f['titel']}: {f['beleg']} → {f['folge']}")
    if a.get("sicht"):
        md += ["", "**Sichtprüfung:**"] + [f"- {x}" for x in a["sicht"]]
    md += ["", f"**Größter Hebel:** {a.get('hebel', '')}", "", "**Was der Betrieb davon hat:**"] + [f"- {x}" for x in a["nutzen"]]
    md += ["", f"**Rechenbeispiel:** {beispiel(a['rechner'])}", "", "**Zusatzleistungen zum Anbieten:**"] + [f"- {x}" for x in a.get("extra", [])] + [""]
txt = "\n".join(md).replace("–", "-").replace("—", "-")
open(f"{OUT}/Analyse-Mappe_alle_Leads.md", "w", encoding="utf-8").write(txt)
print("Top 12 nach Prioritaet:")
for r in rows[:12]: print(f"{r['nr']:02d} {r['name'][:38]:38} Score {r['score']:3} wichtig {r['wichtig']} Nutzen/J {r['nutzen_jahr']:>6} Preis ab {r['preis_ab']} Prio {r['prio']}")
