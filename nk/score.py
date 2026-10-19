import json
m = json.load(open("data/merged.json"))

# Manueller visueller Score 0-25 (Anker siehe Briefing Anhang A)
VIS = {"Asia Wok Bistro":23,"Cems Imbiss":8,"Coyote Café":10,"Spencer's Sportsbar":6,"Stumm's Brauhaus":6,"Cinetower Neunkirchen":12,
"Training Center Wasserturm":10,"Wirtshaus Römer Steakhaus":21,"Damaskus Haus":13,"Grill au Bois":13,"LU'S Pinsa Romana":2,"Hotel Zum Ellenfeld":20,
"Volkssonnengarten":8,"Pizza Heimservice Gondoliere":21,"Balkan Bäckerei Prizreni":13,"Deniz Gemüse Döner":8,"La Campanella":13,"Pizza Heimservice Da Enzo":13,
"Pizzeria Piccobello":13,"Indian Tadka":6,"Scheiber Hof":12,"Pension am Stummplatz":14,"Hotel am Zoo":6,"Imbiss an der Falknerei":12,"aqua bar lounge club":25,
"TuS 1860 Gaststätte":18,"AC-1 Sport- und Freizeitpark":15,"Essence Sports- & Wellnessclub":4,"Tanzwerkstatt Susanne Sprung":16,"Tanzschule Hinsberger":8,
"Lux Play Casino":14,"Markt Apotheke":24,"Saarpark-Apotheke":4,"Alte Hütten-Apotheke":6,"Kempf KFZ-Technik":8,"OSIRIS Bestattungen":8,
"Bestattungsinstitut Flunkert":6,"Bestattungen Schneider":6,"Wichelhaus Typografik":12,"Hifi Zenit":14,"Jürgen's Fahrschule":6,"BellaVie Hair und Beauty":2,
"Coiffeur Team Lieb":4,"Haircenter Pusse":4,"Kurt Ludwig Heizung Sanitär":4,"Schröder Heizung Sanitär":6,"Lena Seller Kosmetik":10,"Beauty Nails Ornella":25,
"Physio Dahlem Vojta":6,"Deubel Reha":6,"Therapie Neunkirchen Ergotherapie":14,"Krankengymnastik Rutz":25,"MALWERK":10,"Schirra Raumausstattung":10,
"Opticland Die Brille":8,"JLS Rechtsanwälte":12,"1A Rechtsanwälte":12,"RA Joachim Brunke":14,"Fried & Müller":10,"RA Schmidt-Jochum":6,
"Holiday Land Reisebüro":8,"Reisecenter Holiday World":8,"Infinitysteps":6,"TV-Sat-Service Zaffino":10,"R & F Steuerberatung":2,"A/M Steuerberatung":8,
"Arminia Steuerberatung":20,"Heitschmidt Steuerberater":10,"Holanda Steuerberaterin":12,"Schneller Steuerberater":10,"Treuhand Saar":6,"Westermann Steuerberater":8,
"Tierarztpraxis am Storchenplatz":8,"Zahnarzt Dr. Höhne":6,"Zahnarztpraxis am Markt":16,"KFO Haßdenteufel":12,"KFO Dr. Weyrich":10,
"Blumen Rebel":16,"Schlüssel Thielen":25,"ZMZ Dr. Eisinger":12}

# Google-Profil (Places-Abfrage 09.10.2026): (Schnitt, Anzahl); None = nicht abgefragt / nicht eindeutig
GBP = {"Asia Wok Bistro":(4.4,230),"Wirtshaus Römer Steakhaus":(4.1,364),"Hotel Zum Ellenfeld":(4.2,149),"Pizza Heimservice Gondoliere":(4.0,174),
"Schlüssel Thielen":(4.6,15),"Krankengymnastik Rutz":(5.0,2),"Markt Apotheke":(4.8,56),"Lux Play Casino":(4.8,20),"Arminia Steuerberatung":(5.0,1),
"aqua bar lounge club":(None,0),"TuS 1860 Gaststätte":(4.3,142),"Zahnarztpraxis am Markt":(4.0,93),"Tanzwerkstatt Susanne Sprung":(5.0,11),
"AC-1 Sport- und Freizeitpark":(4.7,218),"Grill au Bois":(4.8,1343),"Blumen Rebel":(4.4,89),"Orient Grill":(4.2,616),"Damaskus Haus":(3.7,165),
"Hifi Zenit":(5.0,195),"Pension am Stummplatz":(3.5,157),"Therapie Neunkirchen Ergotherapie":(4.8,5),"Cinetower Neunkirchen":(3.8,921),
"Deniz Gemüse Döner":(3.5,72),"Cems Imbiss":(3.8,165),"Balkan Bäckerei Prizreni":(4.6,5),"Wichelhaus Typografik":(4.7,3),"KFO Haßdenteufel":(4.0,46),
"RA Joachim Brunke":(4.4,19)}

# Branchenwert lokal (0-12) und Einfachheit (0-20)
def branch_val(b):
    b=b.lower()
    if any(k in b for k in ["döner","imbiss","pizzeria","lieferdienst"]): return 12,16
    if any(k in b for k in ["restaurant","brauhaus","bar","gaststätte","bäckerei","pinseria","grill"]): return 11,15
    if any(k in b for k in ["hotel","pension"]): return 9,14
    if any(k in b for k in ["spielothek","kino","fitness","tanz"]): return 9,15
    if any(k in b for k in ["kosmetik","nagel","friseur"]): return 10,17
    if any(k in b for k in ["apotheke","physio","ergo","osteo","zahnarzt","kiefer","tierarzt"]): return 8,13
    if any(k in b for k in ["schlüssel","optiker","blumen","schuhe","hifi","metzgerei","tv/sat","kfz","reise"]): return 8,16
    if any(k in b for k in ["handwerk","maler","raumaus","druckerei","bestatter"]): return 6,15
    if any(k in b for k in ["steuer","rechtsanwalt","versicherung"]): return 5,12
    return 6,14

CORE = ["Stummstr","Stummplatz","Bahnhofstr","Hüttenbergstr","Lindenallee","Marienstr","Oberer Markt","Unterer Markt","Max-Braun","Brückenstr",
        "Lutherstr","Goethestr","Hebbelstr","Kleiststr","Irrgartenstr","Saarbrücker Str","Storchenplatz","Pasteurstr","Bürgermeister-Ludwig","Wilhelmstr"]

NOTE = {
"Asia Wok Bistro":"Speisekarte als Liste ohne mobile Ansicht (kein Viewport-Tag), Gestaltung vor 2012, 230 Google-Bewertungen werden nicht genutzt",
"Wirtshaus Römer Steakhaus":"Joomla-Seite mit Bildcollage-Kopf, 5,9 s Ladezeit, starke Fotos vorhanden, 364 Bewertungen, keine Online-Reservierung",
"Pizza Heimservice Gondoliere":"Besucherzähler, Wordart-Optik, 21,8 s Ladezeit, kein eigener Bestellweg trotz 40 Jahren Lieferdienst",
"Damaskus Haus":"Website wird von Lieferando betrieben (Plattform-Template), Google-Schnitt 3,7: Reputations- und Direktbestell-Hebel",
"Hotel Zum Ellenfeld":"23,7 s Ladezeit, Stammessen als Fließtext zwischen Strichlinien, keine Zimmerbilder oberhalb der Falz",
"Lux Play Casino":"IONOS-Baukasten mit generischen Gewinn-Stockbildern, Text teils Englisch ('Gambling Expertise'), Rechts-Check GlüStV sinnvoll",
"Schlüssel Thielen":"Tabellenlayout mit feste Breite, mobil 986 px breit (seitliches Wischen), Inhalt fast nur Bild, Text nicht indexierbar",
"Markt Apotheke":"Platzhalter 'Ihr Name Ihr Slogan' im Kopf, Strichlinien als Trenner, jQuery 1.7, Startseite optisch leer",
"Krankengymnastik Rutz":"Sonnenblumen-Design, kein Viewport, mobil 977 px breit, zuletzt 2021 geändert, nur 2 Google-Bewertungen",
"Tanzwerkstatt Susanne Sprung":"Divi-Slider mit Text auf Bild, 11,4 s Ladezeit, Kursplan unübersichtlich, tolle Bühnenfotos vorhanden",
"Beauty Nails Ornella":"Seit Mai 2012 unverändert, kein Viewport, mobil 920 px breit, italienisch-deutscher Mischtext",
"aqua bar lounge club":"Domain zeigt Plesk-Standardseite: faktisch keine Website",
"Arminia Steuerberatung":"Serifen-Text auf grauem Hintergrund, Optik um 2005",
"Zahnarztpraxis am Markt":"Unruhige Kopfzeile, Schmuckschrift, Bild-Stock-Motiv",
"Orient Grill":"Domain leitet von HTTPS auf unverschlüsseltes HTTP um: Browser warnt 'Nicht sicher', 616 Google-Bewertungen",
"TuS 1860 Gaststätte":"Vereins-Baukasten, Gaststätte und Kegelbahn kaum sichtbar",
}

rows=[]
for r in m:
    n=r["name"]; b=r["branch"]
    reach = r.get("status") in (200,) and r.get("words",0)>0 or n in VIS
    blocked = r.get("status")==403
    vis = VIS.get(n)
    a = 0
    if vis is None:
        status = "Bot-Schutz" if blocked else "nicht erreichbar / nur HTTP"
        a = 14 if not blocked else 10
    else:
        status = "live"
        a = vis
        if not r.get("viewport") or (r.get("mob_scrollW") or 390) > 400: a += 5
        if (r.get("load_s") or 0) > 8: a += 3
        if n in ("Markt Apotheke","aqua bar lounge club"): a += 5
    if r.get("http_only") or not r.get("https", False):
        if status != "Bot-Schutz": a += 8
    a = min(a, 40)
    bv, ease = branch_val(b)
    if "lieferando" in (r.get("text","").lower()): ease -= 2
    if (r.get("words") or 0) > 1500: ease -= 2
    g = GBP.get(n)
    c = bv + (6 if any(k in r["addr"] for k in CORE) else 2)
    if g and g[1]:
        c += 7 if g[1] >= 150 else 5 if g[1] >= 50 else 3 if g[1] >= 10 else 1
    else:
        c += 2
    c = min(c, 25)
    d = 0
    if not r.get("facebook") and not r.get("instagram"): d += 4
    if not r.get("localbiz"): d += 3
    if not r.get("booking"): d += 3
    if g and (g[1] < 20 or (g[0] or 5) < 4.0): d += 3
    if "lieferando" in (r.get("text","").lower()): d += 2
    d = min(d, 15)
    tot = a + ease + c + d
    lab = ("Nicht prüfbar" if status!="live" else
           "Umsatzhebel" if bv>=11 and a>=18 else
           "Quick Win" if a>=18 and ease>=14 else
           "Langläufer" if bv<=6 else "Solide Chance" if a>=12 else "Niedrige Priorität")
    rows.append(dict(name=n,branch=b,addr=r["addr"]+", 66538 Neunkirchen",tel=r["tel"],url=r["url"],final=r.get("final",""),status=status,
        https="ja" if r.get("https") else "nein",mobile="ja" if (r.get("viewport") and (r.get("mob_scrollW") or 390)<=400) else ("nein" if status=="live" else "?"),
        load=r.get("load_s"),cms=(r.get("generator") or ("WordPress" if r.get("wp") else "Jimdo" if r.get("jimdo") else "Wix" if r.get("wix") else ""))[:30],
        lastmod=r.get("lastmod",""),fb="ja" if r.get("facebook") else "nein",ig="ja" if r.get("instagram") else "nein",
        schema="ja" if r.get("localbiz") else "nein",booking="ja" if r.get("booking") else "nein",
        g_avg=g[0] if g else None,g_n=g[1] if g else None,A=a,B=ease,C=c,D=d,total=tot,label=lab,note=NOTE.get(n,""),slug=r["slug"]))
rows.sort(key=lambda x:(-x["total"],-x["A"]))
for i,x in enumerate(rows,1): x["rank"]=i
json.dump(rows,open("data/scored.json","w"),ensure_ascii=False,indent=1)
for x in rows[:35]: print(x["rank"],x["name"],x["total"],x["A"],x["B"],x["C"],x["D"],x["label"],x["status"])
