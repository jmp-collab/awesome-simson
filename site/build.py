#!/usr/bin/env python3
"""Baut die statische Website nach dist/.
Aufruf:  python3 build.py            Vorschau-Build (fehlende Impressumsdaten erlaubt)
         python3 build.py --live     Live-Build, bricht ab, wenn Pflichtangaben fehlen
"""
import json, os, re, sys, shutil, hashlib, base64, html, datetime
from urllib.parse import quote

ROOT = os.path.dirname(os.path.abspath(__file__))
C = json.load(open(os.path.join(ROOT, "config.json")))
LIVE = "--live" in sys.argv
DIST = os.path.join(ROOT, "dist")
TODAY = datetime.date.today()
STAND = "19.10.2026"
E = html.escape

REQUIRED = ["full_name", "street", "zip_city", "email", "phone"]
missing = [k for k in REQUIRED if not C.get(k)]
if LIVE and missing:
    sys.exit("Live-Build abgebrochen, in config.json fehlen: " + ", ".join(missing))

# ---------- Daten ----------
PAKETE = [
    dict(id="start", name="Start", preis="ab 690 €", fuer="Handel, Beauty, kleine Dienstleister",
         items=["Eine Seite, gebaut fürs Smartphone", "HTTPS, Impressum und Datenschutzerklärung inklusive", "Anruf per Fingertipp, Anfahrt, Öffnungszeiten", "Mit Ihrem Google-Profil verbunden", "Online nach rund 2 Wochen"]),
    dict(id="betrieb", name="Betrieb", preis="ab 1.190 €", fuer="Handwerk, Praxen, Gastronomie", feat=True,
         items=["Bis zu 6 Unterseiten", "Eine Funktion für Ihre Branche, etwa Speisekarte, Kursplan oder Terminanfrage", "Ich fotografiere bei Ihnen im Betrieb", "Strukturierte Daten und die Suchbegriffe, die Leute hier wirklich eintippen", "Dazu alles aus Start"]),
    dict(id="umsatz", name="Umsatz", preis="ab 1.990 €", fuer="Lieferdienste, Restaurants, Hotels",
         items=["Bestellen, reservieren oder buchen direkt bei Ihnen", "Weniger Gebühren an Liefer- und Buchungsportale", "Karte oder Zimmer ändern Sie selbst", "Übersicht, wie viele Anrufe, Anfragen und Bestellungen reinkommen", "Dazu alles aus Betrieb"]),
]
BAUSTEINE = [
    ("Betreuung", "Server, Updates und Sicherungen, dazu bis 30 Minuten Änderungen pro Monat", "ab 29 € / Monat"),
    ("Google-Profil", "Profil anlegen, Kategorien setzen, Fotos hochladen, Bewertungen beantworten", "ab 190 € einmalig, ab 49 € / Monat"),
    ("Social Media", "2 bis 3 Beiträge die Woche nach festem Plan, kurze Videos mit Untertiteln", "ab 290 € / Monat"),
    ("KI im Betrieb", "Zwei Stunden bei Ihnen im Betrieb: Angebote, Antworten auf Bewertungen, Texte und Übersetzungen mit KI", "ab 290 €"),
    ("KI-Assistenten", "Fertige Vorlagen für Mails und Bewertungen, Karten in mehreren Sprachen, alles, was Sie immer wieder schreiben", "ab 49 € / Monat"),
    ("Lokale Sichtbarkeit", "Gleiche Daten in allen Verzeichnissen, Verweise von Vereinen, Partnern und der Lokalpresse", "ab 290 €"),
]
BRANCHEN = {
    "gastronomie": dict(t="Gastronomie und Lieferdienste", kurz="Gastronomie", h1="Bestellungen landen bei Ihnen, nicht beim Lieferportal",
        lead="Für Restaurants, Pizzerien, Imbisse, Dönerläden und Lieferdienste in Neunkirchen. Wer Hunger hat, entscheidet am Handy und braucht dafür ein paar Sekunden.",
        prob=["Die Karte liegt als PDF oder Foto vor, am Handy kann man sie kaum lesen", "Bestellt wird über ein Portal, das an jeder Bestellung mitverdient", "Website, Google und Facebook nennen unterschiedliche Öffnungszeiten", "Auf neue Bewertungen antwortet niemand"],
        loes=["Die Karte als richtige Seite, schnell geladen, mit Fotos und Allergenangaben", "Ein Tipp, und der Gast ruft an oder schreibt per WhatsApp. Wer mag, bekommt einen eigenen Bestellweg", "Öffnungszeiten an einer Stelle ändern, Google und Website ziehen mit", "KI-Vorlagen für Bewertungsantworten, die nach Ihnen klingen"],
        paket="umsatz", extra="eine mehrsprachige Karte und Kurzvideos für Instagram",
        kw="Website für Restaurant, Pizzeria und Imbiss in Neunkirchen"),
    "handwerk": dict(t="Handwerk und Dienstleister", kurz="Handwerk", h1="Aufträge über Google, während Sie auf der Baustelle stehen",
        lead="Für Elektriker, Maler, Dachdecker, Sanitärbetriebe, Schlüsseldienste und Werkstätten. Gesucht wird nach Leistung plus Ort, oft dann, wenn es brennt.",
        prob=["Welche Arbeiten Sie machen und wie weit Sie fahren, steht nirgends", "Anfragen kommen ohne Fotos und Maße, also wird erst mal telefoniert", "Ihre gute Arbeit aus vielen Jahren sieht man online nicht", "Die Nummer lässt sich am Handy nicht antippen"],
        loes=["Für jede Hauptleistung eine eigene Seite, die Google genau dieser Suche zuordnet", "Anfrage mit Foto-Upload, damit Sie vorher wissen, was Sie erwartet", "Eine Bildergalerie Ihrer Arbeiten, die Sie vom Handy aus füllen", "Oben auf jeder Seite: antippen, anrufen"],
        paket="betrieb", extra="ein Google-Profil mit Fotos und Leistungen sowie ein QR-Code für Bewertungen auf der Rechnung",
        kw="Website für Handwerker in Neunkirchen"),
    "praxen": dict(t="Praxen, Apotheken und Gesundheit", kurz="Praxen", h1="Weniger Telefonate am Empfang, mehr Ruhe für die Behandlung",
        lead="Für Physiotherapie, Arzt- und Zahnarztpraxen, Apotheken und Heilpraktiker. Patienten suchen drei Dinge: Sprechzeiten, Leistungen und einen einfachen Weg zum Termin.",
        prob=["Sprech- und Urlaubszeiten stimmen nicht mehr, also klingelt das Telefon", "Die Leistungen stehen in Fachbegriffen da", "Für ältere Patienten ist die Seite schwer zu bedienen", "Offene Stellen findet kaum jemand"],
        loes=["Sprechzeiten und Hinweise ändern Sie selbst, in einer Minute", "Leistungen verständlich erklärt, in großer Schrift mit kräftigem Kontrast", "Terminanfrage direkt auf der Seite oder Ihr vorhandenes Buchungssystem eingebunden", "Eine Karriereseite, über die Bewerber Ihre Stellen bei Google finden"],
        paket="betrieb", extra="ein KI-Workshop fürs Team, damit Briefe, Antworten und Infotexte schneller fertig sind",
        kw="Website für Praxis und Apotheke in Neunkirchen"),
    "handel": dict(t="Handel, Beauty und Freizeit", kurz="Handel", h1="Gefunden werden, bevor die Kundschaft in die Stadt fährt",
        lead="Für Läden, Friseure, Nagel- und Kosmetikstudios, Tanzschulen, Hotels und Freizeitangebote in Neunkirchen.",
        prob=["Auf Instagram passiert viel, auf der Website seit Jahren nichts", "Termine gibt es nur am Telefon, nach Feierabend also gar nicht", "Von Aktionen erfahren nur die Stammkunden", "Bei Google stehen alte Bilder und falsche Zeiten"],
        loes=["Website und Instagram passen zusammen, neue Posts tauchen von selbst auf", "Termin online oder per WhatsApp anfragen, zu jeder Uhrzeit", "Eine Seite pro Saison-Aktion, zum Teilen per Link oder QR-Code", "Ein Google-Profil mit frischen Bildern und Beiträgen"],
        paket="start", extra="Social Media nach Plan und ein Bewertungs-QR an der Kasse",
        kw="Website für Geschäfte und Studios in Neunkirchen"),
}
STATS = [("374", "Websites Neunkirchener Betriebe habe ich geprüft"), ("1 von 5", "der erreichbaren Seiten funktioniert am Handy nicht richtig"),
         ("89 %", "geben Google Adresse und Öffnungszeiten nicht maschinenlesbar mit"), ("72 %", "haben keinen Link zu Instagram oder Facebook")]
FAQ = [
    ("Was kostet mich die Vorschau?", "Gar nichts. Sie bekommen Ihre neue Startseite als Vorschau, mit Ihren Inhalten. Wenn sie Ihnen nicht zusagt, war es das."),
    ("Wann zahle ich?", "50 % bei Auftrag. Den Rest erst, wenn die Seite online ist und Sie zufrieden sind. Dafür gibt es eine ordentliche Rechnung."),
    ("Wie kann ich bezahlen?", "Ganz normal per Überweisung. Jede Rechnung hat außerdem einen Zahllink: Karte, SEPA-Lastschrift, Apple Pay oder Google Pay. Über denselben Link geht auch die Kryptowährung USDC. Die Betreuung buche ich per Lastschrift ab."),
    ("Muss ich Texte schreiben?", "Nein. Ich nehme, was auf Ihrer Seite schon steht, stelle ein paar Fragen und schreibe den Rest selbst. Sie lesen und geben frei."),
    ("Gehört mir die Website?", "Ja. Domain, Texte und Bilder sind Ihr Eigentum. Wechseln Sie irgendwann, nehmen Sie alles mit."),
    ("Kann ich selbst etwas ändern?", "Öffnungszeiten, Karte, Hinweise und Bilder schon. Für den Rest reicht eine kurze Nachricht an mich, das deckt die Betreuung ab."),
    ("Was hat KI damit zu tun?", "Mit KI arbeite ich schneller, das drückt den Preis. Im Betrieb hilft sie bei Bewertungsantworten, Angeboten und Übersetzungen. Ich zeige Ihnen, was davon bei Ihnen tatsächlich Zeit spart."),
    ("Arbeiten Sie nur in Neunkirchen?", "Hauptsächlich Neunkirchen samt Wiebelskirchen und Wellesweiler, außerdem Spiesen-Elversberg, Ottweiler, Schiffweiler und Illingen. Besprochen wird bei Ihnen im Betrieb, ich komme vorbei."),
]
KONZEPTE = [
    dict(slug="imbiss-glutstueck", name="Imbiss Glutstück", art="Imbiss mit Lieferservice", paket="Umsatz",
         ziel="Mehr Direktbestellungen per Telefon und WhatsApp statt Plattform", farbe="#c2410c", bg="#1b1410", ink="#fff3e8",
         claim="Frisch vom Grill. In 25 Minuten bei Ihnen.", cta="Jetzt anrufen und bestellen", top="Bestellen",
         panel=("Heute beliebt", [("Glut-Burger, Rind, Cheddar", "9,50 €"), ("Grillteller mit Pommes und Salat", "12,90 €"), ("Halloumi-Bowl (vegetarisch)", "10,50 €"), ("Mittagstisch Mo bis Fr", "ab 7,90 €")]),
         chips=["Mo bis Sa 11 bis 22 Uhr", "Lieferung ab 15 €", "Abholung 10 % günstiger"],
         teile=[("Speisekarte", "Burger, Grillteller, Bowls, vegetarisch markiert, Allergene auf einen Blick"), ("Bestellen", "Anruf oder WhatsApp mit einem Fingertipp, Liefergebiet mit Mindestbestellwert"), ("Mittagstisch", "Wochenkarte, die das Team per Handy selbst einträgt")]),
    dict(slug="dachbau-ferrum", name="Dachbau Ferrum", art="Dachdecker und Spengler", paket="Betrieb",
         ziel="Qualifizierte Anfragen mit Fotos, Einsatzgebiet klar", farbe="#2563eb", bg="#0f172a", ink="#e2e8f0",
         claim="Dicht. Sauber. Pünktlich.", cta="Dach-Check anfragen", top="Anfragen",
         panel=("Dach-Check in 3 Schritten", [("1. Zwei Handyfotos hochladen", "2 Minuten"), ("2. Rückruf vom Meister", "in 24 Stunden"), ("3. Festpreisangebot", "nach Besichtigung"), ("Einsatzgebiet", "30 km um Neunkirchen")]),
         chips=["Meisterbetrieb", "Notdienst bei Sturmschäden", "Fördermittel-Beratung"],
         teile=[("Leistungen", "Steildach, Flachdach, Dachfenster, Spenglerarbeiten, jeweils mit eigener Seite"), ("Anfrage mit Foto", "Kunde lädt zwei Handyfotos hoch, Rückruf innerhalb von 24 Stunden"), ("Referenzen", "Vorher und nachher aus der Region, vom Team selbst gepflegt")]),
    dict(slug="physio-lindwerk", name="Physio Lindwerk", art="Praxis für Physiotherapie", paket="Betrieb",
         ziel="Weniger Anrufe am Empfang, Stellen schneller besetzen", farbe="#0f766e", bg="#f0fdfa", ink="#0b2b28",
         claim="Wieder schmerzfrei bewegen.", cta="Terminanfrage senden", top="Termin",
         panel=("Sprechzeiten", [("Montag bis Donnerstag", "7:30 bis 19:00"), ("Freitag", "7:30 bis 14:00"), ("Hausbesuche", "nach Vereinbarung"), ("Hinweis", "Praxis vom 23.12. bis 1.1. geschlossen")]),
         chips=["Alle Kassen und privat", "Barrierefrei im Erdgeschoss", "Parkplätze am Haus"],
         teile=[("Leistungen", "Krankengymnastik, Manuelle Therapie, Lymphdrainage, in klarer Sprache erklärt"), ("Sprechzeiten", "Aktuelle Zeiten und Urlaubshinweise, in einer Minute geändert"), ("Karriere", "Stellen für Therapeuten mit Google-Jobdaten")]),
]

# ---------- Hilfen ----------
def code_for(k):
    h = hashlib.sha256((C.get("code_salt", "saarseiten-2026") + ":" + k).encode()).digest()
    return base64.b32encode(h).decode().lower()[:6]

def tel_href(n):
    d = re.sub(r"[^\d+]", "", n or "")
    if d.startswith("0"): d = "+49" + d[1:]
    return "tel:" + d

def wa_href(text):
    n = re.sub(r"\D", "", C.get("whatsapp") or "")
    if not n: return ""
    if n.startswith("0"): n = "49" + n[1:]
    return f"https://wa.me/{n}?text={quote(text)}"

LOGO = '<svg viewBox="0 0 32 32" aria-hidden="true"><rect width="32" height="32" rx="8" fill="var(--rust)"/><path d="M8 22h16M8 17h10M8 12h16" stroke="var(--rust-ink)" stroke-width="2.6" stroke-linecap="round"/></svg>'
NAV = [("index", "Start", ""), ("leistungen", "Leistungen", ""), ("branchen", "Branchen", ""), ("portfolio", "Arbeiten", ""), ("check", "Website-Check", ""), ("ueber-mich", "Über mich", "")]

def umami():
    if C.get("umami_src") and C.get("umami_id"):
        return f'<script defer src="{E(C["umami_src"])}" data-website-id="{E(C["umami_id"])}"></script>'
    return ""

PREVIEW_JS = "" if LIVE else 'document.querySelectorAll("form[data-netlify]").forEach(function(f){f.addEventListener("submit",function(e){e.preventDefault();var d=document.createElement("div");d.className="pv";d.setAttribute("role","status");d.textContent="Vorschau: Das Formular sendet erst auf der Live-Seite. Auf Netlify landet die Anfrage dann in Ihrem Postfach.";document.body.appendChild(d);setTimeout(function(){d.remove()},6000)})});'

def page(path, title, desc, body, active="", noindex=False, mcta=True, schema=None, canonical=True, cta=None):
    depth = path.count("/")
    pre = "../" * depth
    slug = path[:-5] if path.endswith(".html") else path
    url = C["base_url"] + "/" + ("" if slug == "index" else slug)
    nav = "".join(f'<a href="{pre}{k}.html"{" aria-current=\"page\"" if k == active else ""}>{t}</a>' for k, t, _ in NAV[1:])
    wa = wa_href("Hallo Jean, ich interessiere mich für eine neue Website.")
    m = ""
    if mcta:
        b2 = f'<a class="btn btn-wa" href="{wa}" data-umami-event="wa-sticky">WhatsApp</a>' if wa else (f'<a class="btn btn-s" href="{tel_href(C["phone"])}" data-umami-event="tel-sticky">Anrufen</a>' if C.get("phone") else "")
        c1 = cta or (f"{pre}kontakt.html", "Kostenlose Vorschau")
        m = f'<div class="mcta"><a class="btn btn-p" href="{c1[0]}" data-umami-event="vorschau-sticky">{c1[1]}</a>{b2}</div>'
    contact = []
    if C.get("phone"): contact.append(f'<li><a href="{tel_href(C["phone"])}">{E(C.get("phone_display") or C["phone"])}</a></li>')
    if C.get("email"): contact.append(f'<li><a href="mailto:{E(C["email"])}">{E(C["email"])}</a></li>')
    if wa: contact.append(f'<li><a href="{wa}">WhatsApp</a></li>')
    contact.append(f'<li><a href="{pre}kontakt.html">Kontaktformular</a></li>')
    sch = f'<script type="application/ld+json">{json.dumps(schema, ensure_ascii=False)}</script>' if schema else ""
    robots = '<meta name="robots" content="noindex,nofollow">' if noindex else ""
    can = f'<link rel="canonical" href="{url}">' if canonical and not noindex else ""
    return f"""<!doctype html>
<html lang="de">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>{E(title)}</title>
<meta name="description" content="{E(desc)}">
{robots}{can}
<meta property="og:title" content="{E(title)}"><meta property="og:description" content="{E(desc)}"><meta property="og:type" content="website"><meta property="og:locale" content="de_DE">
<meta name="theme-color" content="#b4441c">
<link rel="icon" href="{pre}assets/favicon.svg" type="image/svg+xml">
<link rel="preload" href="{pre}assets/fonts/familjen-grotesk-latin-700-normal.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="{pre}assets/style.css">
{sch}{umami()}
<script>try{{var t=localStorage.getItem("theme");if(t)document.documentElement.dataset.theme=t}}catch(e){{}}</script>
</head>
<body class="{'has-mcta' if mcta else ''}">
<a class="skip" href="#main">Zum Inhalt</a>
<header class="top"><div class="wrap">
<a class="brand" href="{pre}index.html">{LOGO}<span>{E(C["brand"])}</span></a>
<button class="menu-btn" aria-expanded="false" aria-controls="nav">Menü</button>
<nav class="nav" id="nav">{nav}<a class="btn btn-p" href="{pre}kontakt.html" data-umami-event="vorschau-nav">Kostenlose Vorschau</a></nav>
</div></header>
<main id="main">
{body}
</main>
<footer><div class="wrap">
<div class="cols">
<div><a class="brand" href="{pre}index.html">{LOGO}<span>{E(C["brand"])}</span></a>
<p class="mt muted" style="color:#b4b8bd">Websites, Google-Profile und KI für Betriebe in {E(C["region"])}. Persönlich betreut, zum Festpreis, mit kostenloser Vorschau vorab.</p></div>
<div><h3>Kontakt</h3><ul>{''.join(contact)}</ul></div>
<div><h3>Seiten</h3><ul><li><a href="{pre}leistungen.html">Leistungen und Preise</a></li><li><a href="{pre}check.html">Website-Check</a></li><li><a href="{pre}impressum.html">Impressum</a></li><li><a href="{pre}datenschutz.html">Datenschutz</a></li></ul></div>
</div>
<div class="base"><span>© {TODAY.year} {E(C["brand"])}</span><button class="theme-btn" id="theme">Hell / Dunkel</button></div>
</div></footer>
{m}
<script>
(function(){{var b=document.querySelector(".menu-btn"),n=document.getElementById("nav");if(b)b.onclick=function(){{var o=n.classList.toggle("open");b.setAttribute("aria-expanded",o)}};
var t=document.getElementById("theme");if(t)t.onclick=function(){{var d=document.documentElement,c=d.dataset.theme||(matchMedia("(prefers-color-scheme: dark)").matches?"dark":"light"),x=c==="dark"?"light":"dark";d.dataset.theme=x;try{{localStorage.setItem("theme",x)}}catch(e){{}}}};
{PREVIEW_JS}document.querySelectorAll(".ba input").forEach(function(r){{var f=function(){{r.parentNode.style.setProperty("--pos",r.value+"%")}};r.addEventListener("input",f);f()}});
}})();
</script>
</body>
</html>
"""

def contact_form(name, pre, hidden=None, button="Kostenlose Vorschau anfordern", url_field=True, msg_label="Worum geht es? (optional)"):
    hid = "".join(f'<input type="hidden" name="{E(k)}" value="{E(v)}">' for k, v in (hidden or {}).items())
    urlf = '<div class="f"><label for="f-web">Ihre Website (falls vorhanden)</label><input id="f-web" name="website" type="text" inputmode="url" autocomplete="url" placeholder="www.ihr-betrieb.de"></div>' if url_field else ""
    return f"""<form name="{name}" method="POST" action="{pre}danke.html" data-netlify="true" netlify-honeypot="bot-field">
<input type="hidden" name="form-name" value="{name}">{hid}
<p class="hp"><label>Nicht ausfüllen <input name="bot-field" tabindex="-1" autocomplete="off"></label></p>
<div class="grid g2">
<div class="f"><label for="f-name">Name</label><input id="f-name" name="name" required autocomplete="name"></div>
<div class="f"><label for="f-firma">Betrieb</label><input id="f-firma" name="betrieb" autocomplete="organization"></div>
<div class="f"><label for="f-tel">Telefon</label><input id="f-tel" name="telefon" type="tel" autocomplete="tel"></div>
<div class="f"><label for="f-mail">E-Mail</label><input id="f-mail" name="email" type="email" required autocomplete="email"></div>
</div>
{urlf}
<div class="f"><label for="f-msg">{msg_label}</label><textarea id="f-msg" name="nachricht" rows="3"></textarea></div>
<label class="consent"><input type="checkbox" name="einwilligung" value="ja" required><span>Sie dürfen mich zu meiner Anfrage per E-Mail und Telefon kontaktieren. Ich kann das jederzeit widerrufen. Details in der <a href="{pre}datenschutz.html">Datenschutzerklärung</a>.</span></label>
<button class="btn btn-p" type="submit">{button}</button>
</form>"""

def cta_band(pre, h="Sehen, bevor Sie zahlen", p="Sie bekommen Ihre neue Startseite als Vorschau, mit Ihren Inhalten. Kostenlos, ohne Verpflichtung, und ich bringe sie persönlich vorbei."):
    wa = wa_href("Hallo Jean, ich hätte gern eine kostenlose Vorschau für meinen Betrieb.")
    b2 = f'<a class="btn btn-wa" href="{wa}" data-umami-event="wa-band">Per WhatsApp</a>' if wa else ""
    return f"""<section class="steel cta-band"><div class="wrap"><div><span class="kicker">Nächster Schritt</span><h2>{h}</h2><p class="muted">{p}</p></div>
<div class="btns"><a class="btn btn-p" href="{pre}kontakt.html" data-umami-event="vorschau-band">Vorschau anfordern</a>{b2}<a class="btn btn-s" style="border-color:var(--steel-ink);color:var(--steel-ink)" href="{pre}check.html">Erst den Check machen</a></div></div></section>"""

def price_cards(pre, highlight=None):
    out = []
    for p in PAKETE:
        feat = (highlight == p["id"]) if highlight else p.get("feat")
        tag = '<span class="tag">Passt meistens</span>' if feat else ""
        out.append(f"""<div class="card price{' feat' if feat else ''}">{tag}<h3>{p['name']}</h3><p class="muted" style="margin:0">{p['fuer']}</p>
<div class="amt">{p['preis']}</div><ul class="check">{''.join(f'<li>{i}</li>' for i in p['items'])}</ul>
<a class="btn {'btn-p' if feat else 'btn-s'}" href="{pre}kontakt.html?paket={p['id']}" data-umami-event="paket-{p['id']}">Vorschau für {p['name']}</a></div>""")
    return '<div class="grid g3">' + "".join(out) + "</div>"

PAY_NOTE = "Bevor Sie zahlen, sehen Sie eine kostenlose Vorschau. Die zweite Hälfte wird erst fällig, wenn die Seite online ist."
KU = "Alle Preise sind Endpreise. Gemäß § 19 UStG wird keine Umsatzsteuer berechnet." if C.get("kleinunternehmer") else "Alle Preise zuzüglich gesetzlicher Umsatzsteuer."

# ---------- Seiten ----------
def p_index():
    pre = ""
    stats = "".join(f'<div class="card stat"><div class="num">{n}</div><p>{t}</p></div>' for n, t in STATS)
    br = "".join(f'<a class="card" href="branchen/{k}.html"><span class="kicker">{v["kurz"]}</span><h3>{v["h1"]}</h3><p class="muted">{v["lead"].split(".")[0]}.</p></a>' for k, v in BRANCHEN.items())
    faq = "".join(f"<details><summary>{q}</summary><p>{a}</p></details>" for q, a in FAQ[:5])
    schema = {"@context": "https://schema.org", "@type": "ProfessionalService", "name": C["brand"], "url": C["base_url"],
              "areaServed": ["Neunkirchen (Saar)", "Spiesen-Elversberg", "Ottweiler", "Schiffweiler", "Illingen"],
              "description": "Webdesign, Google-Profile und KI-Beratung für lokale Betriebe in Neunkirchen (Saar).",
              "priceRange": "690 € bis 1.990 €"}
    if C.get("phone"): schema["telephone"] = C["phone"]
    if C.get("street"): schema["address"] = {"@type": "PostalAddress", "streetAddress": C["street"], "addressLocality": C["zip_city"], "addressCountry": "DE"}
    body = f"""
<section class="hero"><div class="stripe"></div><div class="wrap hero-grid">
<div><span class="kicker">Webdesign aus Neunkirchen (Saar)</span>
<h1>Ihr Betrieb ist gut. Ihre Website sollte es auch sein.</h1>
<p class="lead">Ich mache Websites für Neunkirchener Betriebe: am Handy gut bedienbar, bei Google auffindbar, mit Anrufen als Ergebnis. Eine Vorschau sehen Sie, bevor Sie irgendetwas bezahlen.</p>
<div class="btns"><a class="btn btn-p" href="kontakt.html" data-umami-event="vorschau-hero">Kostenlose Vorschau anfordern</a><a class="btn btn-s" href="check.html" data-umami-event="check-hero">Website in 20 Sekunden prüfen</a></div>
<p class="mono muted mt">Feste Preise ab 690 € · Zahlung erst zur Hälfte, Rest nach Livegang</p></div>
<div class="mock" aria-label="Beispiel eines Website-Checks">
<div class="mono muted" style="margin-bottom:6px">Website-Check · beispiel-pizzeria.de</div>
<div class="row"><span>Auf dem Handy lesbar</span><span class="pill bad">nein, 986 px breit</span></div>
<div class="row"><span>Verschlüsselt (HTTPS)</span><span class="pill bad">nein</span></div>
<div class="row"><span>Telefon anklickbar</span><span class="pill warn">nur auf Unterseite</span></div>
<div class="row"><span>Öffnungszeiten für Google</span><span class="pill bad">fehlen</span></div>
<div class="row"><span>Nach der Überarbeitung</span><span class="pill ok">alles grün</span></div>
</div></div></section>

<section class="band"><div class="wrap">
<span class="kicker">Eigene Messung, Stand {STAND}</span><h2>Was ich in Neunkirchen gemessen habe</h2>
<p class="muted prose">374 Websites von Betrieben aus Neunkirchen habe ich am Handy und am Rechner geöffnet. Die Zahlen zeigen, wie oft Kunden schon beim ersten Klick scheitern.</p>
<div class="grid g4 mt">{stats}</div></div></section>

<section><div class="wrap">
<span class="kicker">So läuft es ab</span><h2>Rund zwei Wochen vom Entwurf bis zur fertigen Seite</h2>
<div class="steps mt">
<div class="card"><h3>Vorschau</h3><p>Ihre neue Startseite, gebaut aus Ihren Texten und Bildern. Kostet nichts.</p></div>
<div class="card"><h3>15 Minuten bei Ihnen</h3><p>Ich schaue vorbei und wir sehen uns die Vorschau zusammen am Handy an.</p></div>
<div class="card"><h3>Festpreis und Start</h3><p>Sie erhalten ein Angebot zum Festpreis. Bei Auftrag wird die Hälfte fällig.</p></div>
<div class="card"><h3>Online</h3><p>Die Seite ist online, das Google-Profil stimmt. Jetzt erst kommt die zweite Hälfte.</p></div>
</div></div></section>

<section class="band"><div class="wrap">
<span class="kicker">Für Ihre Branche</span><h2>Was in Ihrer Branche den Unterschied macht</h2>
<div class="grid g2 mt">{br}</div></div></section>

<section><div class="wrap">
<span class="kicker">Preise</span><h2>Drei Pakete, feste Preise</h2>
<p class="muted">{PAY_NOTE}</p>
<div class="mt">{price_cards(pre)}</div>
<p class="mt"><a href="leistungen.html">Alle Leistungen, Bausteine und Betreuung ansehen</a></p></div></section>

<section class="band"><div class="wrap grid g2" style="align-items:start">
<div><span class="kicker">Mehr als eine Website</span><h2>KI, die im Betrieb Zeit spart</h2>
<p>Bewertungen beantworten, Angebote schreiben, die Karte in drei Sprachen, Posts für Instagram. So etwas schafft KI inzwischen in Minuten. Ich stelle es passend für Ihren Betrieb ein und erkläre Ihrem Team die Handgriffe.</p>
<a class="btn btn-s" href="leistungen.html#ki">KI-Leistungen ansehen</a></div>
<div class="card"><h3>Was Sie sich künftig sparen</h3><ul class="check"><li>Bewertungen einzeln von Hand beantworten</li><li>Angebote aus alten Dateien zusammenstückeln</li><li>Karte oder Aushang selbst übersetzen</li><li>Jede Woche grübeln, was auf Instagram kommt</li></ul></div>
</div></section>

<section><div class="wrap faq prose"><span class="kicker">Häufige Fragen</span><h2>Das fragen mich Inhaber am häufigsten</h2>{faq}<p class="mt"><a href="leistungen.html#faq">Alle Fragen</a></p></div></section>
{cta_band(pre)}"""
    return page("index.html", f"Webdesign Neunkirchen (Saar) | {C['brand']}", "Websites für Betriebe in Neunkirchen (Saar): auf das Handy ausgelegt, bei Google sichtbar, mit festen Preisen ab 690 € und kostenloser Vorschau.", body, "index", schema=schema)

def p_leistungen():
    pre = ""
    bs = "".join(f"<tr><td><strong>{a}</strong></td><td>{b}</td><td style='white-space:nowrap'>{c}</td></tr>" for a, b, c in BAUSTEINE)
    faq = "".join(f"<details><summary>{q}</summary><p>{a}</p></details>" for q, a in FAQ)
    fs = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in FAQ]}
    body = f"""
<section class="hero"><div class="wrap"><span class="kicker">Leistungen und Preise</span><h1>Festpreise. Und gezahlt wird erst nach dem Hinsehen.</h1>
<p class="lead">{PAY_NOTE}</p></div></section>
<section style="padding-top:0"><div class="wrap">{price_cards(pre)}<p class="muted mt">{KU}</p></div></section>
<section class="band"><div class="wrap"><span class="kicker">Bausteine</span><h2>Was dazukommen kann</h2>
<div class="tscroll card mt" style="padding:6px 16px"><table class="t"><thead><tr><th>Baustein</th><th>Inhalt</th><th>Preis</th></tr></thead><tbody>{bs}</tbody></table></div></div></section>
<section id="ki"><div class="wrap grid g2" style="align-items:start">
<div><span class="kicker">KI-Beratung</span><h2>KI im Betrieb, ohne Fachchinesisch</h2>
<p>Im Hauptberuf mache ich Online-Marketing und nutze KI dabei täglich. Kleine Betriebe brauchen davon kein Großprojekt. Sie brauchen ein paar feste Abläufe, die schon in der ersten Woche Zeit sparen.</p>
<p>Auch der Datenschutz kommt nicht zu kurz: Sie erfahren, welche Daten in welches Werkzeug gehören und welche draußen bleiben.</p></div>
<div class="grid">
<div class="card"><h3>Workshop vor Ort</h3><p>Zwei Stunden mit Ihrem Team. Hinterher kann jeder Bewertungsantworten, Angebote und Infotexte mit KI erstellen. Ab 290 €.</p></div>
<div class="card"><h3>Fertige Assistenten</h3><p>Vorlagen und Abläufe für alles, was Sie regelmäßig schreiben, von mir aktuell gehalten. Ab 49 € im Monat.</p></div>
</div></div></section>
<section class="band"><div class="wrap grid g2" style="align-items:start">
<div><span class="kicker">Bezahlung</span><h2>Bezahlen ohne Umstände</h2>
<p>Es gibt eine Rechnung, und Sie überweisen wie immer. Wer lieber anders zahlt, nutzt den Zahllink auf der Rechnung: Karte, SEPA-Lastschrift, Apple Pay oder Google Pay. Derselbe Link nimmt auch die Kryptowährung USDC an.</p>
<p>Die Betreuung wird monatlich abgebucht. Nach den ersten 12 Monaten können Sie zu jedem Monatsende kündigen.</p></div>
<div class="card"><h3>Ablauf</h3><ul class="check"><li>Kostenlose Vorschau anschauen</li><li>Festpreisangebot per Mail, ein "Einverstanden" reicht</li><li>Erste Rechnung über 50 %</li><li>Seite geht online, danach die Restrechnung</li><li>Die Betreuung beginnt im Monat darauf</li></ul></div>
</div></section>
<section id="faq"><div class="wrap faq prose"><span class="kicker">Fragen</span><h2>Fragen zu Preis und Ablauf</h2>{faq}</div></section>
{cta_band(pre)}"""
    return page("leistungen.html", f"Leistungen und Preise | {C['brand']}", "Website-Pakete ab 690 €, Betreuung ab 29 € im Monat, Google-Profil, Social Media und KI-Beratung für Betriebe in Neunkirchen (Saar).", body, "leistungen", schema=fs)

def p_branchen_index():
    pre = ""
    br = "".join(f'<a class="card" href="branchen/{k}.html"><span class="kicker">{v["t"]}</span><h3>{v["h1"]}</h3><p class="muted">{v["lead"]}</p></a>' for k, v in BRANCHEN.items())
    body = f"""<section class="hero"><div class="wrap"><span class="kicker">Branchen</span><h1>Eine Website, die zu Ihrem Geschäft passt</h1>
<p class="lead">Ein Restaurant braucht andere Dinge als ein Dachdecker. Suchen Sie Ihre Branche aus.</p></div></section>
<section style="padding-top:0"><div class="wrap grid g2">{br}</div></section>{cta_band(pre)}"""
    return page("branchen.html", f"Branchen | {C['brand']}", "Webdesign für Gastronomie, Handwerk, Praxen und Handel in Neunkirchen (Saar).", body, "branchen")

def p_branche(k, v):
    pre = "../"
    pk = next(p for p in PAKETE if p["id"] == v["paket"])
    body = f"""
<section class="hero"><div class="wrap"><span class="kicker">{v['t']} in Neunkirchen</span><h1>{v['h1']}</h1><p class="lead">{v['lead']}</p>
<div class="btns"><a class="btn btn-p" href="{pre}kontakt.html?branche={k}" data-umami-event="vorschau-branche-{k}">Kostenlose Vorschau anfordern</a><a class="btn btn-s" href="{pre}check.html">Website prüfen</a></div></div></section>
<section class="band"><div class="wrap grid g2" style="align-items:start">
<div class="card"><span class="kicker">Was ich oft sehe</span><ul class="check">{''.join(f'<li>{x}</li>' for x in v['prob'])}</ul></div>
<div class="card"><span class="kicker">Was ich daraus mache</span><ul class="check">{''.join(f'<li>{x}</li>' for x in v['loes'])}</ul></div>
</div></section>
<section><div class="wrap"><span class="kicker">Empfehlung</span><h2>Paket {pk['name']}, {pk['preis']}</h2>
<p class="prose">Für {v['kurz']} passt meistens das Paket {pk['name']}. Dazu lohnt sich oft: {v['extra']}.</p>
<div class="mt">{price_cards(pre, v['paket'])}</div><p class="muted mt">{PAY_NOTE} {KU}</p></div></section>
{cta_band(pre)}"""
    return page(f"branchen/{k}.html", f"{v['kw']} | {C['brand']}", f"{v['h1']}. {v['lead']}", body, "branchen")

def p_portfolio():
    pre = ""
    cards = "".join(f"""<a class="card" href="konzepte/{c['slug']}.html"><div class="shot"><img src="assets/concepts/{c['slug']}.webp" alt="Startseite des Konzepts {c['name']}" loading="lazy" width="1280" height="800"></div>
<span class="badge">Konzept · fiktiver Betrieb</span><h3 style="margin-top:.6em">{c['name']}</h3><p class="muted">{c['art']} · Paket {c['paket']}</p><p>{c['ziel']}</p></a>""" for c in KONZEPTE)
    body = f"""<section class="hero"><div class="wrap"><span class="kicker">Arbeiten</span><h1>So arbeite ich</h1>
<p class="lead">Hier sehen Sie drei Konzepte für ausgedachte Betriebe aus typischen Branchen. Echte Projekte kommen nur mit Zustimmung der Inhaber auf diese Seite, und dann mit Vorher, Nachher und echten Zahlen.</p></div></section>
<section style="padding-top:0"><div class="wrap grid g3">{cards}</div></section>
<section class="band"><div class="wrap grid g2" style="align-items:start"><div><span class="kicker">Was jede Seite mitbringt</span><h2>Bei jeder Seite dabei</h2></div>
<ul class="check"><li>Zuerst fürs Handy gebaut, danach für den Rechner</li><li>In unter 2 Sekunden geladen, ganz ohne Baukasten und Plugins</li><li>Verschlüsselt, mit Impressum und Datenschutz</li><li>Strukturierte Daten für Google: Adresse, Öffnungszeiten, Leistungen</li><li>Barrierearm mit großer Schrift, starkem Kontrast und Tastaturbedienung</li><li>Besucherstatistik, für die kein Cookie-Banner nötig ist</li></ul></div></section>
{cta_band(pre, "Ihr Betrieb als nächstes Beispiel?", "In der Vorschau sehen Sie Ihre eigene Startseite statt eines fremden Beispiels.")}"""
    return page("portfolio.html", f"Arbeiten und Konzepte | {C['brand']}", "Konzepte für Imbiss, Dachdecker und Physiotherapie: so sehen Websites von Saarseiten aus.", body, "portfolio")

def p_konzept(c):
    teile = "".join(f'<div class="k-card"><h3>{a}</h3><p>{b}</p></div>' for a, b in c["teile"])
    return f"""<!doctype html><html lang="de"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{E(c['name'])} (Konzept)</title><meta name="robots" content="noindex">
<link rel="stylesheet" href="../assets/style.css">
<style>
body{{background:{c['bg']};color:{c['ink']}}}
.k-top{{display:flex;justify-content:space-between;align-items:center;padding:18px 0}}
.k-top b{{font:700 1.3rem var(--f-head)}}
.k-top a{{background:{c['farbe']};color:#fff;text-decoration:none;padding:10px 16px;border-radius:999px;font:700 .95rem var(--f-head)}}
.k-hero{{padding:48px 0 40px;display:grid;gap:36px;align-items:center}}@media(min-width:860px){{.k-hero{{grid-template-columns:1.2fr 1fr}}}}
.k-chips{{display:flex;flex-wrap:wrap;gap:8px;margin-top:22px}}.k-chips span{{border:1px solid color-mix(in srgb,{c['ink']} 25%,transparent);border-radius:999px;padding:6px 12px;font-size:.9rem}}
.k-panel{{background:color-mix(in srgb,{c['ink']} 7%,{c['bg']});border:1px solid color-mix(in srgb,{c['ink']} 18%,transparent);border-top:6px solid {c['farbe']};border-radius:18px;padding:24px;box-shadow:0 24px 60px -24px rgba(0,0,0,.45)}}
.k-row{{display:flex;justify-content:space-between;gap:14px;padding:12px 0;border-bottom:1px dashed color-mix(in srgb,{c['ink']} 22%,transparent)}}.k-row:last-child{{border:0}}.k-row b{{white-space:nowrap;color:{c['farbe']}}}
.k-hero h1{{font-size:clamp(2.4rem,7vw,4.6rem);max-width:13ch}}
.k-hero p{{font-size:1.2rem;opacity:.85;max-width:44ch}}
.k-btn{{display:inline-block;background:{c['farbe']};color:#fff;text-decoration:none;padding:16px 22px;border-radius:12px;font:700 1.05rem var(--f-head);margin-top:10px}}
.k-grid{{display:grid;gap:14px;padding:20px 0 60px}}@media(min-width:760px){{.k-grid{{grid-template-columns:repeat(3,1fr)}}}}
.k-card{{border:1px solid color-mix(in srgb,{c['ink']} 20%,transparent);border-radius:16px;padding:22px;background:color-mix(in srgb,{c['ink']} 5%,transparent)}}
.k-art{{height:180px;border-radius:18px;margin-top:30px;background:linear-gradient(120deg,{c['farbe']},color-mix(in srgb,{c['farbe']} 40%,{c['bg']}) 60%,transparent),repeating-linear-gradient(90deg,transparent 0 22px,color-mix(in srgb,{c['ink']} 8%,transparent) 22px 24px)}}
.k-note{{position:fixed;bottom:12px;right:12px;background:#111;color:#fff;font:500 .72rem var(--f-mono);padding:6px 10px;border-radius:6px;opacity:.85}}
</style></head><body>
<div class="wrap"><div class="k-top"><b>{E(c['name'])}</b><a href="#">{E(c['top'])}</a></div>
<div class="k-hero"><div><span class="kicker" style="color:{c['farbe']}">{E(c['art'])} · Neunkirchen</span><h1>{E(c['claim'])}</h1>
<a class="k-btn" href="#">{E(c['cta'])}</a><div class="k-chips">{''.join(f'<span>{E(x)}</span>' for x in c['chips'])}</div></div>
<div class="k-panel"><h3>{E(c['panel'][0])}</h3>{''.join(f'<div class="k-row"><span>{E(a)}</span><b>{E(b)}</b></div>' for a, b in c['panel'][1])}</div></div>
<div class="k-grid">{teile}</div>
<p style="opacity:.7;padding-bottom:40px"><a href="../portfolio.html">Zurück zu den Arbeiten</a></p></div>
<div class="k-note">Konzept · fiktiver Betrieb</div></body></html>"""

def p_check():
    pre = ""
    body = f"""<section class="hero"><div class="wrap" style="max-width:820px"><span class="kicker">Kostenloser Website-Check</span>
<h1>Wie schlägt sich Ihre Website am Handy?</h1>
<p class="lead">Geben Sie die Adresse ein. Nach etwa 20 Sekunden zeigt eine Ampel, wo es hakt. Anmelden müssen Sie sich nicht.</p>
<form id="chk" class="card" style="margin-top:20px"><div class="f"><label for="chk-url">Adresse Ihrer Website</label>
<input id="chk-url" name="url" required inputmode="url" placeholder="www.ihr-betrieb.de" autocomplete="url"></div>
<button class="btn btn-p" type="submit" data-umami-event="check-start">Jetzt prüfen</button>
<p class="muted mono" id="chk-status" style="margin:12px 0 0"></p></form>
<div class="check-out card" id="chk-out"><h2 style="font-size:1.4rem" id="chk-title">Ergebnis</h2><div id="chk-list"></div>
<div class="mt"><h3>Ausführlicher Bericht mit Lösungsvorschlägen</h3><p class="muted">Zusätzlich sehe ich mir Ihre Seite selbst an und schicke Ihnen kostenlos einen Bericht per Mail.</p>
{contact_form("check-bericht", pre, {"geprueft": ""}, "Bericht anfordern", url_field=False, msg_label="Was ist Ihnen an Ihrer Seite wichtig? (optional)")}</div></div>
<p class="muted mt" style="font-size:.92rem">Der Check ruft Ihre Startseite einmal auf und misst Verschlüsselung, Handy-Darstellung, Ladezeit und die Angaben für Google. Ihre Eingabe wird dafür an meinen Server und, für die Ladezeit, an Google PageSpeed Insights übermittelt und nicht gespeichert.</p>
</div></section>
<script>
(function(){{var f=document.getElementById("chk"),s=document.getElementById("chk-status"),o=document.getElementById("chk-out"),l=document.getElementById("chk-list");
f.addEventListener("submit",function(e){{e.preventDefault();var u=document.getElementById("chk-url").value.trim();if(!u)return;
s.textContent="Prüfe "+u+" ...";o.classList.remove("show");
fetch("/api/check?url="+encodeURIComponent(u)).then(function(r){{if(!r.ok)throw new Error(r.status);return r.json()}}).then(function(d){{
if(d.error){{s.textContent=d.error;return}}
s.textContent="Fertig. Geprüft: "+d.final;document.getElementById("chk-title").textContent="Ergebnis für "+d.host;
l.innerHTML="";d.checks.forEach(function(c){{var x=document.createElement("div");x.className="light";
x.innerHTML='<span class="dot '+c.state+'"></span><div><strong></strong><div class="muted"></div></div>';
x.querySelector("strong").textContent=c.label;x.querySelector(".muted").textContent=c.detail;l.appendChild(x)}});
var h=document.querySelector('#chk-out input[name="geprueft"]');if(h)h.value=d.final;o.classList.add("show");
}}).catch(function(){{s.textContent="Der Check ist gerade nicht erreichbar. Schreiben Sie mir Ihre Adresse über das Formular, ich prüfe sie von Hand.";
var h=document.querySelector('#chk-out input[name="geprueft"]');if(h)h.value=u;l.innerHTML="";o.classList.add("show")}});
}});}})();
</script>"""
    return page("check.html", f"Kostenloser Website-Check | {C['brand']}", "Prüfen Sie in 20 Sekunden, ob Ihre Website auf dem Handy funktioniert, verschlüsselt ist und Google die richtigen Angaben liefert.", body, "check")

def p_ueber():
    pre = ""
    body = f"""<section class="hero"><div class="wrap grid g2" style="align-items:center">
<div><span class="kicker">Über mich</span><h1>Ich bin {E(C['first_name'])}.</h1>
<p class="lead">Hauptberuflich bin ich SEO-Manager im Online-Handel. Wie Google eine Seite liest und warum Leute am Handy nach drei Sekunden abspringen, ist mein Tagesgeschäft.</p>
<p>Mit {E(C['brand'])} bringe ich dieses Wissen zu Betrieben in Neunkirchen, für die eine Agentur nie infrage käme: zum Imbiss an der Ecke, zum Elektriker, zur Praxis im Erdgeschoss. Ich komme persönlich vorbei, und über Geld reden wir erst, wenn Sie Ihre Vorschau gesehen haben.</p>
<div class="btns mt"><a class="btn btn-p" href="kontakt.html">Kostenlose Vorschau anfordern</a></div></div>
<div class="card"><h3>Darauf können Sie mich festnageln</h3><ul class="check"><li>Festpreise, öffentlich auf dieser Seite</li><li>Erst die Vorschau, dann der erste Euro</li><li>Zweite Rate erst, wenn die Seite online ist</li><li>Domain und Inhalte bleiben Ihre</li><li>Antwort spätestens am nächsten Werktag</li></ul></div>
</div></section>{cta_band(pre)}"""
    return page("ueber-mich.html", f"Über mich | {C['brand']}", f"{C['first_name']}, Webdesigner und KI-Berater in Neunkirchen (Saar), hauptberuflich SEO-Manager im Online-Handel.", body, "ueber-mich")

def p_kontakt():
    pre = ""
    wa = wa_href("Hallo Jean, ich hätte gern eine kostenlose Vorschau für meinen Betrieb.")
    ways = []
    if wa: ways.append(f'<a class="btn btn-wa" href="{wa}" data-umami-event="wa-kontakt">WhatsApp schreiben</a>')
    if C.get("phone"): ways.append(f'<a class="btn btn-s" href="{tel_href(C["phone"])}" data-umami-event="tel-kontakt">{E(C.get("phone_display") or C["phone"])} anrufen</a>')
    if C.get("cal_link"): ways.append(f'<a class="btn btn-s" href="{E(C["cal_link"])}" data-umami-event="termin-kontakt">15-Minuten-Termin buchen</a>')
    alt = f'<div class="card"><h3>Lieber direkt?</h3><div class="btns">{"".join(ways)}</div></div>' if ways else ""
    body = f"""<section class="hero"><div class="wrap grid g2" style="align-items:start">
<div><span class="kicker">Kontakt</span><h1>Ihre kostenlose Vorschau</h1>
<p class="lead">Nennen Sie mir Ihren Betrieb. Spätestens am nächsten Werktag melde ich mich, danach entsteht Ihre Vorschau.</p>
<ul class="check"><li>Kostet nichts, verpflichtet zu nichts</li><li>Gebaut aus Ihren eigenen Inhalten</li><li>Persönlich vorbeigebracht in {E(C['region'])}</li></ul>{alt}</div>
<div class="card">{contact_form("kontakt", pre)}</div></div></section>
<script>(function(){{var q=new URLSearchParams(location.search),m=document.getElementById("f-msg");if(m&&(q.get("paket")||q.get("branche")))m.value="Interesse: "+(q.get("paket")?"Paket "+q.get("paket"):"Branche "+q.get("branche"))}})();</script>"""
    return page("kontakt.html", f"Kontakt und kostenlose Vorschau | {C['brand']}", "Fordern Sie eine kostenlose Vorschau Ihrer neuen Website an. Persönlich in Neunkirchen (Saar).", body, "", mcta=False)

def p_danke():
    body = """<section class="hero"><div class="wrap prose"><span class="kicker">Danke</span><h1>Ist angekommen.</h1>
<p class="lead">Spätestens am nächsten Werktag hören Sie von mir. Falls es eilt, rufen Sie einfach an.</p>
<a class="btn btn-s" href="index.html">Zur Startseite</a></div></section>"""
    return page("danke.html", f"Danke | {C['brand']}", "Ihre Anfrage ist angekommen.", body, noindex=True, mcta=False)

def p_404():
    body = """<section class="hero"><div class="wrap prose"><span class="kicker">Fehler 404</span><h1>Diese Seite gibt es nicht.</h1>
<p class="lead">Vielleicht ein Tippfehler im Link. Hier geht es weiter:</p><div class="btns"><a class="btn btn-p" href="/index.html">Startseite</a><a class="btn btn-s" href="/kontakt.html">Kontakt</a></div></div></section>"""
    return page("404.html", f"Seite nicht gefunden | {C['brand']}", "Seite nicht gefunden.", body, noindex=True)

def addr_lines():
    parts = [C.get("full_name"), C.get("street"), C.get("zip_city")]
    if all(parts): return "<br>".join(E(p) for p in parts)
    return '<span class="muted">Name und ladungsfähige Anschrift werden vor dem Livegang aus config.json eingesetzt.</span>'

def p_impressum():
    kont = []
    if C.get("phone"): kont.append(f'Telefon: <a href="{tel_href(C["phone"])}">{E(C.get("phone_display") or C["phone"])}</a>')
    if C.get("email"): kont.append(f'E-Mail: <a href="mailto:{E(C["email"])}">{E(C["email"])}</a>')
    ust = f"<h2>Umsatzsteuer</h2><p>Umsatzsteuer-Identifikationsnummer gemäß § 27a UStG: {E(C['vat_id'])}</p>" if C.get("vat_id") else ("<h2>Umsatzsteuer</h2><p>Kleinunternehmer gemäß § 19 UStG, es wird keine Umsatzsteuer ausgewiesen.</p>" if C.get("kleinunternehmer") else "")
    body = f"""<section><div class="wrap prose"><h1>Impressum</h1>
<h2>Angaben gemäß § 5 DDG</h2><p>{addr_lines()}</p>
<h2>Kontakt</h2><p>{'<br>'.join(kont) if kont else '<span class="muted">Telefon und E-Mail werden vor dem Livegang aus config.json eingesetzt.</span>'}</p>
{ust}
<h2>Verantwortlich für den Inhalt nach § 18 Abs. 2 MStV</h2><p>{E(C.get('full_name') or C['first_name'])}, Anschrift wie oben</p>
<h2>Verbraucherstreitbeilegung</h2><p>Ich bin nicht bereit und nicht verpflichtet, an Streitbeilegungsverfahren vor einer Verbraucherschlichtungsstelle teilzunehmen.</p>
<h2>Haftung für Links</h2><p>Für Inhalte externer Seiten, auf die ich verlinke, sind deren Betreiber verantwortlich. Bei Bekanntwerden von Rechtsverletzungen entferne ich solche Links umgehend.</p>
</div></section>"""
    return page("impressum.html", f"Impressum | {C['brand']}", "Impressum", body, mcta=False)

def p_datenschutz():
    who = addr_lines()
    stat = ("<h2>Statistik</h2><p>Ich nutze Umami, eine Webanalyse ohne Cookies. Erfasst werden aufgerufene Seiten, Herkunftsseite, Gerätetyp, Land und Klicks auf Kontaktknöpfe, ohne Ihre IP-Adresse zu speichern und ohne Sie über Websites hinweg wiederzuerkennen. Rechtsgrundlage ist Art. 6 Abs. 1 lit. f DSGVO, mein berechtigtes Interesse an der Verbesserung dieser Website.</p>"
            if C.get("umami_src") else "<h2>Statistik</h2><p>Diese Website verwendet derzeit keine Statistik- oder Analysewerkzeuge und setzt keine Cookies.</p>")
    body = f"""<section><div class="wrap prose"><h1>Datenschutzerklärung</h1>
<p class="muted">Stand {STAND}</p>
<h2>Verantwortlicher</h2><p>{who}<br>{('E-Mail: ' + E(C['email'])) if C.get('email') else ''}</p>
<h2>Hosting</h2><p>Diese Website wird bei Netlify, Inc., 512 2nd Street, San Francisco, CA 94107, USA gehostet. Beim Aufruf verarbeitet Netlify technisch notwendige Daten wie IP-Adresse, Zeitpunkt, aufgerufene Seite und Browserkennung, um die Seite auszuliefern und vor Angriffen zu schützen. Rechtsgrundlage ist Art. 6 Abs. 1 lit. f DSGVO. Mit Netlify besteht ein Vertrag zur Auftragsverarbeitung; die Übermittlung in die USA stützt sich auf das EU-US Data Privacy Framework sowie Standardvertragsklauseln.</p>
<h2>Schriftarten</h2><p>Alle Schriftarten liegen auf diesem Server. Es werden keine Verbindungen zu Google Fonts oder anderen Schriftanbietern aufgebaut.</p>
<h2>Kontaktformulare</h2><p>Wenn Sie ein Formular absenden, verarbeite ich Ihre Angaben (Name, Betrieb, Telefon, E-Mail, Website, Nachricht), um Ihre Anfrage zu beantworten und Ihnen gegebenenfalls eine Vorschau und ein Angebot zu schicken. Rechtsgrundlage ist Ihre Einwilligung nach Art. 6 Abs. 1 lit. a DSGVO sowie Art. 6 Abs. 1 lit. b DSGVO für vorvertragliche Maßnahmen. Die Formulare werden über Netlify Forms verarbeitet. Ich lösche die Angaben, wenn die Anfrage abgeschlossen ist und keine gesetzlichen Aufbewahrungspflichten bestehen, spätestens nach 12 Monaten ohne Auftrag.</p>
<p>Ihre Einwilligung zur Kontaktaufnahme können Sie jederzeit mit Wirkung für die Zukunft widerrufen, eine kurze Nachricht genügt.</p>
<h2>Website-Check</h2><p>Für den Website-Check wird die von Ihnen eingegebene Adresse an eine Funktion auf meinem Server übermittelt. Diese ruft die Startseite der angegebenen Website auf und fragt bei Google PageSpeed Insights (Google Ireland Limited, Gordon House, Barrow Street, Dublin 4, Irland) die Ladezeit ab. Dabei wird nur die Website-Adresse übermittelt, keine Daten über Sie. Die Adresse wird nicht gespeichert. Rechtsgrundlage ist Art. 6 Abs. 1 lit. b DSGVO.</p>
<h2>WhatsApp und Terminbuchung</h2><p>Wenn Sie einen WhatsApp-Knopf nutzen, öffnet sich WhatsApp der WhatsApp Ireland Limited. Es gelten deren Datenschutzbestimmungen. Für die Terminbuchung verweise ich auf Cal.com; dort gelten deren Bedingungen. Beide Dienste werden erst geladen, wenn Sie den Knopf anklicken.</p>
{stat}
<h2>Bezahlung</h2><p>Zahlungen per Karte, Lastschrift oder USDC wickelt Stripe Payments Europe, Ltd., 1 Grand Canal Street Lower, Dublin, Irland ab. Dazu übermittle ich die für die Zahlung nötigen Daten aus der Rechnung. Rechtsgrundlage ist Art. 6 Abs. 1 lit. b DSGVO.</p>
<h2>Ihre Rechte</h2><p>Sie haben das Recht auf Auskunft, Berichtigung, Löschung, Einschränkung der Verarbeitung, Datenübertragbarkeit und Widerspruch (Art. 15 bis 21 DSGVO). Sie können sich bei einer Aufsichtsbehörde beschweren, im Saarland beim Unabhängigen Datenschutzzentrum Saarland, Fritz-Dobisch-Straße 12, 66111 Saarbrücken.</p>
<h2>Widerspruch gegen Werbung per Post</h2><p>Wenn Sie von mir Post erhalten haben und keine weitere möchten, genügt eine kurze Nachricht. Ich nehme Ihren Betrieb dann dauerhaft aus meiner Liste.</p>
</div></section>"""
    return page("datenschutz.html", f"Datenschutz | {C['brand']}", "Datenschutzerklärung", body, mcta=False)

# ---------- Vorschau-Seiten ----------
def load_top():
    return json.load(open(os.path.join(ROOT, "data", "top10.json"), encoding="utf-8"))

VTXT = json.load(open(os.path.join(ROOT, "data", "vorschau_texte.json"), encoding="utf-8"))

def clamp_price(s):
    nums = [int(x.replace(".", "")) for x in re.findall(r"[\d.]+", s)]
    lo = max(nums[0], 690); hi = max(nums[-1], lo + 200)
    f = lambda n: f"{n:,}".replace(",", ".")
    return f"{f(lo)} bis {f(hi)} €"

def p_vorschau(t, code):
    pre = "../"
    k = t["k"]
    name = t["name"]
    wa = wa_href(f"Hallo Jean, ich habe Ihren Brief zu {name} bekommen (Code {code}).")
    tel = f'<a class="btn btn-s" href="{tel_href(C["phone"])}" data-umami-event="tel-v-{code}">Anrufen</a>' if C.get("phone") else ""
    wab = f'<a class="btn btn-wa" href="{wa}" data-umami-event="wa-v-{code}">Per WhatsApp antworten</a>' if wa else ""
    cal = f'<a class="btn btn-s" href="{E(C["cal_link"])}" data-umami-event="termin-v-{code}">15 Minuten Termin</a>' if C.get("cal_link") else ""
    preis = clamp_price(t["p"][0])
    vt = VTXT.get(k, {})
    audit = "".join(f"<li>{E(a)}</li>" for a in vt.get("obs", t["audit"]))
    svc = "".join(f"<li>{E(s)}</li>" for s in vt.get("neu", []))
    body = f"""
<section class="hero" style="padding-bottom:32px"><div class="wrap"><span class="kicker">Persönliche Vorschau · Code {code}</span>
<h1>{E(name)}: so könnte Ihre Website aussehen.</h1>
<p class="lead">Der Entwurf besteht aus Ihren eigenen Texten und Bildern. Mit dem Regler vergleichen Sie ihn direkt mit Ihrer heutigen Seite.</p></div></section>
<section style="padding-top:0"><div class="wrap">
<div class="ba" style="--pos:50%"><img src="{pre}assets/v/{k}-vorher-desk.webp" alt="Ihre Website heute" width="1280" height="800">
<img class="after" src="{pre}assets/v/{k}-nachher-desk.webp" alt="Entwurf der neuen Website" width="1280" height="800">
<span class="bar"></span><span class="knob" aria-hidden="true">⇔</span><span class="lbl l1">Heute</span><span class="lbl l2">Entwurf</span>
<input type="range" min="0" max="100" value="50" aria-label="Vergleich heute und Entwurf"></div>
<div class="grid g2 mt" style="align-items:start">
<div><h2 style="font-size:1.5rem">Auf dem Handy</h2><div class="phones">
<figure style="margin:0"><div class="phone"><img src="{pre}assets/v/{k}-vorher-mob.webp" alt="Heute auf dem Handy" loading="lazy"></div><figcaption>Heute</figcaption></figure>
<figure style="margin:0"><div class="phone"><img src="{pre}assets/v/{k}-nachher-mob.webp" alt="Entwurf auf dem Handy" loading="lazy"></div><figcaption>Entwurf</figcaption></figure></div></div>
<div><div class="card"><h3>Das ist mir aufgefallen</h3><ul class="check">{audit}</ul></div>
<div class="card mt"><h3>Das ändert sich mit dem Entwurf</h3><ul class="check">{svc}</ul></div></div>
</div></div></section>
<section class="band"><div class="wrap grid g2" style="align-items:start">
<div><span class="kicker">Ihr Preis</span><h2>{preis}</h2><p>Gilt für genau diesen Entwurf, fertig online, samt Impressum, Datenschutz und Verbindung zum Google-Profil. Die Betreuung kostet danach ab 29 € im Monat.</p>
<p class="muted">{PAY_NOTE} {KU}</p></div>
<div class="card" id="ja"><h3>Gefällt Ihnen der Entwurf?</h3><p class="muted">Ein Ja reicht. Ich melde mich, und wir sprechen ihn in 15 Minuten bei Ihnen durch.</p>
<div class="btns" style="margin-bottom:18px">{wab}{tel}{cal}</div>
{contact_form("vorschau-ja", pre, {"code": code, "betrieb_vorschau": name}, "Ja, ich will das", url_field=False, msg_label="Wünsche oder Fragen (optional)")}</div>
</div></section>
<section><div class="wrap prose"><p class="muted">Diese Seite ist nur für {E(name)} gedacht und nicht bei Google zu finden. Sie bleibt bis zum {(TODAY + datetime.timedelta(days=60)).strftime('%d.%m.%Y')} online. Wenn Sie keine weitere Post von mir möchten, genügt eine kurze Nachricht.</p></div></section>"""
    return page(f"v/{code}.html", f"Vorschau für {name} | {C['brand']}", f"Persönliche Vorschau für {name}", body, noindex=True, cta=("#ja", "Ja, ich will das"))

# ---------- Ausgabe ----------
def write(path, content):
    full = os.path.join(DIST, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    open(full, "w", encoding="utf-8").write(content)

def main():
    if os.path.exists(DIST): shutil.rmtree(DIST)
    os.makedirs(DIST)
    shutil.copytree(os.path.join(ROOT, "assets"), os.path.join(DIST, "assets"))
    write("assets/favicon.svg", LOGO.replace('aria-hidden="true"', 'xmlns="http://www.w3.org/2000/svg"').replace("var(--rust)", "#b4441c").replace("var(--rust-ink)", "#fff"))
    write("index.html", p_index()); write("leistungen.html", p_leistungen()); write("branchen.html", p_branchen_index())
    for k, v in BRANCHEN.items(): write(f"branchen/{k}.html", p_branche(k, v))
    write("portfolio.html", p_portfolio())
    for c in KONZEPTE: write(f"konzepte/{c['slug']}.html", p_konzept(c))
    write("check.html", p_check()); write("ueber-mich.html", p_ueber()); write("kontakt.html", p_kontakt())
    write("danke.html", p_danke()); write("404.html", p_404()); write("impressum.html", p_impressum()); write("datenschutz.html", p_datenschutz())
    # Vorschau-Seiten + QR
    import qrcode
    rows = [("Code", "Betrieb", "Vorschau-URL", "QR-Datei")]
    os.makedirs(os.path.join(ROOT, "qr"), exist_ok=True)
    for t in load_top():
        code = code_for(t["k"])
        write(f"v/{code}.html", p_vorschau(t, code))
        url = f"{C['base_url']}/v/{code}"
        q = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_M, box_size=12, border=2)
        q.add_data(url); q.make(fit=True)
        img = q.make_image(fill_color="#1c1f22", back_color="white")
        qf = f"qr/{t['k']}_{code}.png"; img.save(os.path.join(ROOT, qf))
        rows.append((code, t["name"], url, qf))
    open(os.path.join(ROOT, "vorschau-codes.csv"), "w", encoding="utf-8").write("\n".join(";".join(r) for r in rows) + "\n")
    # SEO-Dateien
    pages = ["", "leistungen", "branchen", "portfolio", "check", "ueber-mich", "kontakt", "impressum", "datenschutz"] + [f"branchen/{k}" for k in BRANCHEN]
    sm = "".join(f"<url><loc>{C['base_url']}/{p}</loc><lastmod>{TODAY.isoformat()}</lastmod></url>" for p in pages)
    write("sitemap.xml", f'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{sm}</urlset>')
    write("_headers", "/*\n  X-Content-Type-Options: nosniff\n  Referrer-Policy: strict-origin-when-cross-origin\n  Strict-Transport-Security: max-age=31536000\n/v/*\n  X-Robots-Tag: noindex, nofollow\n  Cache-Control: no-store\n/konzepte/*\n  X-Robots-Tag: noindex\n/assets/*\n  Cache-Control: public, max-age=31536000, immutable\n")
    write("robots.txt", f"User-agent: *\nAllow: /\nSitemap: {C['base_url']}/sitemap.xml\n")
    print("Seiten gebaut:", sum(len(f) for _, _, f in os.walk(DIST) if True))
    if missing: print("Hinweis: Vorschau-Build, fehlend in config.json:", ", ".join(missing))

if __name__ == "__main__":
    main()
