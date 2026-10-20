"""Erzeugt site/data/analyse.json: je Lead Befunde (gemessen + Sichtprüfung), Score, Nutzen und Rechner-Vorgaben.
Aufruf: python3 wave/analyse.py"""
import json, os, glob, math, re, datetime

B = "/home/claude/nk/wave"
TOP = json.load(open("/home/claude/site/data/top10.json", encoding="utf-8"))
VTXT = json.load(open("/home/claude/site/data/vorschau_texte.json", encoding="utf-8"))
PROF = json.load(open(f"{B}/profile.json", encoding="utf-8"))
YEAR = datetime.date.today().year
GENERIC_TITLES = {"index", "home", "startseite", "start", "willkommen", "my cms", "untitled", "homepage", "neue seite", "website"}
SEV_W = {"hoch": 14, "mittel": 7, "niedrig": 3}

def lieferando(k, t):
    if "Lieferando" in t.get("hebel", ""): return True
    c = f"{B}/content/{k}.json"
    if os.path.exists(c):
        s = json.load(open(c)).get("slug")
        r = f"{B}/raw/{s}.json"
        if s and os.path.exists(r) and "verwaltet durch" in json.load(open(r)).get("text", "")[:400]: return True
    return False

def findings(k, t, a):
    F = []
    def add(id, sev, titel, beleg, folge, fix):
        F.append(dict(id=id, sev=sev, titel=titel, beleg=beleg, folge=folge, fix=fix))
    d, m = a.get("desk", {}), a.get("mob", {})
    if not d.get("ok") and not m.get("ok"):
        add("down", "hoch", "Website war beim Test nicht erreichbar", d.get("error", "")[:90],
            "Wer Sie sucht, landet auf einer Fehlerseite und ruft den nächsten Anbieter an.", "Stabiles Hosting mit Überwachung")
        return F
    if lieferando(k, t):
        add("portal", "hoch", "Ihre eigene Domain zeigt eine Lieferando-Seite",
            "Oben auf der Seite steht: 'Diese Website wird betrieben und verwaltet durch Lieferando.de'",
            "Gäste, die Ihre Adresse schon kennen, bestellen dort mit Provision. Diese Stammkunden-Bestellungen kosten Sie Geld, obwohl Sie sie selbst gewonnen haben.",
            "Eigene Seite auf Ihrer Domain mit Bestellung per Telefon und WhatsApp, Lieferando nur noch als Zusatzkanal")
    w = max(m.get("scrollW", 0) or 0, m.get("innerW", 0) or 0)
    if w > 430:
        add("mobil", "hoch", "Auf dem Handy nicht lesbar",
            f"Die Seite ist {w} Pixel breit, ein Handy zeigt rund 390. Alles wird auf etwa {round(390 / w * 100)} % verkleinert oder man muss seitlich wischen.",
            "Die meisten Kunden suchen einen Betrieb in der Nähe am Handy. Wer zoomen muss, geht zurück zu Google und ruft den Nächsten an.",
            "Seite für Handys gebaut, große Schrift, Knöpfe zum Antippen")
    elif m.get("total", 0) >= 8 and m.get("small", 0) / max(m.get("total", 1), 1) > 0.35:
        add("schrift", "mittel", "Schrift auf dem Handy zu klein",
            f"{round(m['small'] / m['total'] * 100)} % der Textstellen sind kleiner als 12 Pixel.",
            "Kleine Schrift wird überlesen, besonders von älteren Kunden.", "Gut lesbare Schriftgrößen ab 16 Pixel")
    if (m.get("tel", 0) or 0) == 0 and t.get("tel"):
        add("tel", "hoch", "Telefonnummer lässt sich nicht antippen",
            "Auf der Startseite gibt es keinen Anruf-Link (tel:).",
            "Am Handy muss die Nummer abgeschrieben werden. Jeder zusätzliche Schritt kostet Anrufe.",
            "Anrufen-Knopf, der am Handy immer sichtbar bleibt")
    fin = (d.get("final") or a.get("url", ""))
    if fin.startswith("http://"):
        add("ssl", "hoch", "Seite ist nicht verschlüsselt",
            f"Die Seite läuft unter {fin[:60]} ohne https.",
            "Browser zeigen 'Nicht sicher'. Das schreckt ab, und Formulare dürfen so keine Daten übertragen.",
            "Kostenloses SSL-Zertifikat, alles auf https")
    elif a.get("http_redirects_to_https") is False:
        add("https_redirect", "mittel", "Ohne 'https' eingetippt erscheint 'Nicht sicher'",
            f"Die Adresse http://{re.sub(r'^https?://', '', a['url']).split('/')[0]} leitet nicht auf die sichere Version weiter.",
            "Wer die Adresse von Visitenkarte oder Auto abtippt, sieht im Browser eine Warnung.",
            "Automatische Weiterleitung auf https")
    title = (d.get("title") or "").strip()
    if not title or title.lower() in GENERIC_TITLES or len(title) < 12 or any(p in title.lower() for p in ["my cms", "holzland", "pension-neunkirchens"]):
        add("titel", "hoch", "Google zeigt einen nichtssagenden Titel",
            f"Seitentitel: '{title or '(leer)'}'",
            "Der Titel ist die blaue Überschrift in den Google-Ergebnissen. Ohne Ort und Leistung klickt dort kaum jemand.",
            "Titel mit Leistung und Ort, z. B. 'Ihr Betrieb in Neunkirchen | Leistung'")
    if not (d.get("desc") or "").strip():
        add("desc", "mittel", "Keine Beschreibung für Google",
            "Die Seite hat keine Meta-Beschreibung.",
            "Google zeigt dann zufällige Textschnipsel, oft Cookie-Hinweise oder Menüpunkte.",
            "Beschreibung mit Angebot, Ort und Telefonnummer")
    words = d.get("words", 0) or 0
    if words < 120:
        add("text", "hoch" if words < 50 else "mittel", "Zu wenig Text für Google",
            f"Auf der Startseite stehen nur {words} lesbare Wörter.",
            "Google kann nur finden, was als Text dasteht. Leistungen, Ort und Zeiten in Bildern sind für die Suche unsichtbar.",
            "Leistungen, Ort und Öffnungszeiten als echter Text")
    for b in [x for x in (d.get("broken") or []) if str(x.get("src","") if isinstance(x,dict) else x).rstrip("/").count("/")>2 and not re.search(r"counter|activities|pixel|track|stat\.|zaehler|livepages|/i\.gif|spacer|blank\.gif", str(x), re.I)][:2]:
        add("bild_kaputt", "hoch", "Ein Bild lädt nicht",
            f"Nicht geladen: {b.get('alt') or b.get('src', '')[-60:]}",
            "Leere Kästen oder fehlende Logos wirken, als sei der Betrieb nicht mehr aktiv.",
            "Alle Bilder geprüft und neu eingebunden")
        break
    ph = [p for p in (d.get("placeholders") or []) if p not in ("im aufbau",)]
    if ph:
        add("platzhalter", "hoch", "Platzhalter aus der Vorlage sind sichtbar",
            "Gefunden: " + ", ".join(f"'{p}'" for p in ph[:3]),
            "Platzhalter zeigen Besuchern, dass die Seite nie fertig gemacht wurde.",
            "Alle Texte fertig und geprüft")
    yrs = [y for y in (d.get("years") or []) if 1995 <= y <= YEAR]
    if yrs and max(yrs) <= YEAR - 3:
        add("jahr", "mittel", f"Copyright {max(yrs)}: wirkt nicht gepflegt",
            f"Im Fußbereich steht das Jahr {max(yrs)}.",
            "Ein altes Jahr lässt Besucher zweifeln, ob Angaben wie Öffnungszeiten oder Preise noch stimmen.",
            "Aktuelle Seite, die Sie selbst pflegen können")
    if (d.get("bytes") or 0) > 6_000_000 or (m.get("load_s") or 0) > 9:
        mb = round((d.get("bytes") or 0) / 1e6, 1)
        add("speed", "mittel", "Seite lädt langsam",
            (f"Die Startseite lädt {str(mb).replace('.', ',')} MB Daten." if mb > 6 else f"Gemessene Ladezeit am Handy: {m.get('load_s')} s (Richtwert)."),
            "Jede Sekunde Wartezeit kostet Besucher, besonders im Mobilfunknetz.",
            "Optimierte Bilder, schnelles Hosting")
    if not (d.get("forms") or d.get("wa") or d.get("mail") or m.get("wa")):
        add("anfrage", "mittel", "Keine direkte Anfrage möglich",
            "Kein Formular, keine E-Mail-Verlinkung und kein WhatsApp-Knopf auf der Startseite.",
            "Wer abends sucht, kann nicht anrufen und schreibt dann dem Mitbewerber.",
            "Anfrage per Formular und WhatsApp, rund um die Uhr")
    if d.get("http_res"):
        add("mixed", "mittel", "Unsichere Inhalte auf der Seite",
            (f"{len(d['http_res'])} Dateien werden" if len(d['http_res']) != 1 else "1 Datei wird") + " unverschlüsselt (http) geladen.",
            "Browser blockieren solche Inhalte teilweise oder warnen.", "Alle Inhalte über https")
    if not d.get("localbiz"):
        add("schema", "niedrig", "Google erkennt Adresse und Öffnungszeiten nicht automatisch",
            "Keine strukturierten Firmendaten (LocalBusiness) gefunden.",
            "Diese Daten helfen Google, Sie in der Kartensuche und mit Öffnungszeiten anzuzeigen.",
            "Strukturierte Daten für Adresse, Telefon, Öffnungszeiten")
    if not d.get("ogimg"):
        add("og", "niedrig", "Beim Teilen per WhatsApp erscheint kein Vorschaubild",
            "Kein Vorschaubild (og:image) hinterlegt.",
            "Empfehlungen per WhatsApp oder Facebook sehen leer aus und werden seltener geöffnet.",
            "Vorschaubild mit Logo oder Foto für jede Seite")
    errs = d.get("errors") or []
    if len(errs) >= 2:
        add("js", "niedrig", "Technische Fehler im Hintergrund",
            f"{len(errs)} Fehlermeldungen beim Laden der Startseite.",
            "Fehler können Formulare, Karten oder Menüs unbemerkt lahmlegen.", "Saubere, geprüfte Technik")
    if not d.get("favicon"):
        add("favicon", "niedrig", "Kein Symbol im Browser-Tab", "Kein Favicon hinterlegt.",
            "In Tabs und Lesezeichen fehlt Ihr Logo, die Seite wirkt unfertig.", "Favicon aus Ihrem Logo")
    return F

def score(F):
    return max(5, 100 - sum(SEV_W[f["sev"]] for f in F))

def preis_lo(t):
    n = [int(x.replace(".", "")) for x in re.findall(r"\d[\d.]*", t["p"][0])]
    return max(n[0], 690)

def rechner(k, t):
    typ, wert, einheit, anzahl = PROF.get(k, ["auftrag", 500, "Auftrag", 4])
    p = preis_lo(t)
    r = dict(typ=typ, wert=wert, einheit=einheit, anzahl=anzahl, preis=p)
    if typ == "auftrag":
        r["breakeven"] = math.ceil(p / wert)
        r["jahr"] = wert * anzahl
    elif typ == "portal":
        r["prov"] = 13
        r["jahr"] = round(anzahl * wert * 0.13 * 12)
        r["breakeven_m"] = math.ceil(p / max(anzahl * wert * 0.13, 1))
    elif typ == "unterkunft":
        r["prov"] = 15
        r["jahr"] = round(anzahl * wert * 0.15 * 12)
        r["breakeven_m"] = math.ceil(p / max(anzahl * wert * 0.15, 1))
    elif typ == "gast":
        r["jahr"] = wert * anzahl * 12
        r["breakeven_m"] = math.ceil(p / max(wert * anzahl, 1))
    elif typ == "abo":
        r["jahr"] = wert * 12 * anzahl
        r["breakeven"] = math.ceil(p / (wert * 12))
    elif typ == "zeit":
        r["min"] = 2; r["satz_h"] = 25
        h = anzahl * 2 * 21 / 60
        r["stunden_m"] = round(h, 1); r["jahr"] = round(h * 25 * 12)
    return r

NUTZEN_FIX = {
    "portal": "Stammkunden bestellen direkt bei Ihnen, ohne Provision",
    "mobil": "Am Handy sofort lesbar: Leistungen, Zeiten und Telefon ohne Zoomen",
    "tel": "Ein Tipp genügt, und das Telefon klingelt bei Ihnen",
    "titel": "Bei Google mit Leistung und Ort sichtbar statt mit '{t}'",
    "text": "Google versteht, was Sie anbieten, und zeigt Sie bei passenden Suchen",
    "anfrage": "Anfragen auch abends und am Wochenende, per Formular oder WhatsApp",
    "ssl": "Keine 'Nicht sicher'-Warnung mehr im Browser",
    "https_redirect": "Keine 'Nicht sicher'-Warnung mehr im Browser",
    "platzhalter": "Eine fertige, gepflegte Seite statt sichtbarer Vorlagenreste",
    "bild_kaputt": "Alle Bilder und das Logo laden zuverlässig",
    "jahr": "Aktuelle Seite, die Vertrauen schafft",
}

def main():
    out = {}
    for t in TOP:
        k = t["k"]
        af = f"{B}/audit/{k}.json"
        a = json.load(open(af)) if os.path.exists(af) else {}
        d, m = a.get("desk") or {}, a.get("mob") or {}
        if d.get("status") == 403 and m.get("status") == 200:  # Bot-Sperre nur fuer Desktop-UA: Inhaltswerte vom Handy-Abruf nehmen
            for x, v in m.items():
                if x not in ("scrollW", "innerW", "small", "taps", "total"): d[x] = v
        F = findings(k, t, a) if a else []
        order = {"hoch": 0, "mittel": 1, "niedrig": 2}
        F.sort(key=lambda f: order[f["sev"]])
        vt = VTXT.get(k, {})
        nutzen = []
        for f in F:
            if f["id"] in NUTZEN_FIX and len(nutzen) < 3:
                tt = (a.get("desk", {}).get("title") or "").strip()
                if len(tt) > 32: tt = tt[:32].rsplit(" ", 1)[0] + " ..."
                s = NUTZEN_FIX[f["id"]].replace("statt mit '{t}'", f"statt mit '{tt}'" if tt else "statt ganz ohne Titel")
                if s not in nutzen: nutzen.append(s)
        def sim(a, b):
            wa, wb = {w[:6] for w in re.findall(r"\w{4,}", a.lower())}, {w[:6] for w in re.findall(r"\w{4,}", b.lower())}
            return len(wa & wb) / max(1, min(len(wa), len(wb)))
        for s in vt.get("neu", []):
            if len(nutzen) < 5 and all(sim(s, x) < 0.5 for x in nutzen): nutzen.append(s)
        sicht = vt.get("obs", t.get("audit", []))
        out[k] = dict(score=max(15, score(F) - 7 * len(sicht)) if a else None, datum=a.get("date"), befunde=F,
                      sicht=sicht, nutzen=nutzen,
                      hebel=t.get("hebel", ""), extra=t.get("svc", []), rechner=rechner(k, t),
                      gemessen=dict(load_m=a.get("mob", {}).get("load_s"), mb=round((a.get("desk", {}).get("bytes") or 0) / 1e6, 1),
                                    breite_m=max(a.get("mob", {}).get("scrollW", 0) or 0, a.get("mob", {}).get("innerW", 0) or 0),
                                    woerter=a.get("desk", {}).get("words"), titel=a.get("desk", {}).get("title")) if a else {})
    txt = json.dumps(out, ensure_ascii=False).replace("\u2013", "-").replace("\u2014", "-").replace("–", "-").replace("—", "-")
    out = json.loads(txt)
    json.dump(out, open("/home/claude/site/data/analyse.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    n = sum(1 for v in out.values() if v["score"] is not None)
    print("Analysen:", n, "von", len(out))

if __name__ == "__main__":
    main()
