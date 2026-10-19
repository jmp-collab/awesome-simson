# Outreach-Bausteine. Platzhalter in {geschweiften Klammern} werden in Excel per SUBSTITUTE ersetzt.
# Regel: keine langen Gedankenstriche, nur '-'.

import re as _re
_SEGRX = [
 ("spielhalle", r"spielothek|spielhalle|casino|wettbüro"),
 ("liefer", r"pizzeria|lieferdienst|heimservice|döner|doener|imbiss|kebab|kebap|grill\b|grillhaus"),
 ("beauty", r"friseur|barber|kosmetik|nagel|nails|beauty|tattoo|piercing|massage|sonnenstudio|wimpern|haarstudio|hair"),
 ("gastro", r"restaurant|brauhaus|\bbar\b|kneipe|gaststätte|café|\bcafe|eiscafé|eisdiele|gelateria|pinseria|bistro|catering|partyservice|steakhaus|steak-house|brauerei|biergarten|shisha|lounge|gasthaus|gastronomie|pasta"),
 ("lebensmittel", r"bäckerei|baeckerei|konditor|metzger|fleischerei|geflügel|feinkost|hofladen|weinhandel|weinfach|getränke"),
 ("hotel", r"hotel|pension|ferienwohnung|ferienapartment|gästehaus|monteurzimmer"),
 ("apotheke", r"apotheke"),
 ("praxis", r"arzt|ärzt|zahn|kiefer|physio|ergo|logopäd|osteo|heilprakti|naturheil|podolog|fußpflege|krankengym|therapie|praxis|tierarzt|pflege|sanitätshaus|orthopädie|hörakust|hörgerät|psycho|radiolog|urolog|neurolog|onkolog|kardiolog|gastroent|internist|chirurg|gynäk|dermatolog|psychiat|nephrolog|dialyse|allgemeinmed|medizin|hno"),
 ("freizeit", r"fitness|tanz|kampfsport|boxen|box-club|boxclub|karate|ju-jutsu|judo|yoga|pilates|kino|bowling|kegel|reit|escape|sportverein|freizeit|musikschule|musikunterricht|hundeschule|pole|verein"),
 ("kfz", r"kfz|auto|reifen|lackier|abschlepp|motorrad|zweirad|fahrrad|fahrräder|trucks|nutzfahrzeug"),
 ("beratung", r"steuer|anwalt|rechtsanw|notar|versicherung|finanz|makler|immobil|hausverwalt|architekt|ingenieur|buchhalt|sachverständ"),
 ("bestatter", r"bestatt"),
 ("handwerk", r"elektr|heizung|sanitär|shk|dach|zimmerei|schreiner|tischler|maler|fliesen|boden|raumausst|garten|landschaft|glaser|fenster|metallbau|schlosser|rollladen|reinigung|umzug|entrümpel|schädling|bau|handwerk|sat-anlag|fernseh|küche|stuck|gerüst|trockenbau|hausmeister|montage|installat|licht- und ton"),
]
def segment(branch):
    b = (branch or "").lower()
    for seg, rx in _SEGRX:
        if _re.search(rx, b): return seg
    return "handel"

SEG = {
 # Nutzenwinkel (1 Satz), Extra-Leistung, Preisanker einmalig, Monatsanker, Ziel-Aktion des Kunden
 "liefer": ("Bei einem Lieferdienst zählt jede Bestellung, die direkt bei Ihnen landet statt über ein Portal mit Provision.",
            "ein eigenes Bestellsystem ohne Provision", "ab 990 €", "ab 49 €", "mehr Direktbestellungen"),
 "gastro": ("Gäste suchen abends auf dem Handy nach Speisekarte, Öffnungszeiten und einem Platz für heute.",
            "eine Online-Reservierung und eine Seite für Feiern und Gruppen", "ab 990 €", "ab 39 €", "mehr Reservierungen"),
 "lebensmittel": ("Viele Kunden prüfen vor dem Weg zu Ihnen kurz Öffnungszeiten und Angebote auf dem Handy.",
            "eine Vorbestellung für Feiertage und Platten", "ab 690 €", "ab 29 €", "mehr Vorbestellungen"),
 "hotel": ("Jede Buchung direkt über Ihre eigene Seite spart die Provision der Buchungsportale.",
            "eine Zimmeranfrage mit zwei Klicks", "ab 990 €", "ab 39 €", "mehr Direktbuchungen"),
 "apotheke": ("E-Rezept und Vorbestellung gehen heute über das Handy, und dort entscheidet sich, ob das Rezept zu Ihnen oder zur Versandapotheke geht.",
            "E-Rezept-Anleitung und Vorbestellung direkt auf der Startseite", "ab 990 €", "ab 49 €", "mehr Rezepte vor Ort"),
 "praxis": ("Patienten und vor allem Bewerberinnen und Bewerber schauen sich Ihre Praxis zuerst online an.",
            "eine Karriereseite für neue Fachkräfte und eine Terminanfrage", "ab 790 €", "ab 29 €", "Bewerbungen und Terminanfragen"),
 "beauty": ("Neukundinnen und Neukunden suchen auf dem Handy und buchen dort, wo es am schnellsten geht.",
            "eine Online-Terminbuchung mit Erinnerung", "ab 690 €", "ab 29 €", "mehr gebuchte Termine"),
 "freizeit": ("Interessenten entscheiden oft abends am Handy, ob sie zum Probetraining kommen.",
            "einen Kursplan mit Anmeldung zur Probestunde", "ab 990 €", "ab 39 €", "mehr Probestunden"),
 "spielhalle": ("Gäste suchen Öffnungszeiten und Anfahrt, und neue Servicekräfte schauen sich Ihren Betrieb vorher online an.",
            "eine rechtssichere Infoseite mit Jugend- und Spielerschutz und eine Karriereseite", "ab 690 €", "ab 29 €", "Personal und Laufkundschaft"),
 "kfz": ("Wer eine Werkstatt sucht, will auf dem Handy in Sekunden sehen: Was machen die, wann haben sie offen, wie komme ich an einen Termin.",
            "eine Terminanfrage für Inspektion und Reifenwechsel", "ab 790 €", "ab 29 €", "mehr Werkstattaufträge"),
 "handwerk": ("Aufträge und vor allem Azubis und Gesellen finden Sie heute über eine Seite, die auf dem Handy überzeugt.",
            "eine Karriereseite und ein Anfrageformular mit Foto-Upload", "ab 790 €", "ab 29 €", "Anfragen und Bewerbungen"),
 "beratung": ("Mandanten und Bewerber vergleichen Kanzleien heute zuerst online, oft auf dem Handy.",
            "eine Karriereseite und einen sicheren Upload für Unterlagen", "ab 1.190 €", "ab 39 €", "Mandanten und Nachwuchs"),
 "bestatter": ("Angehörige suchen in einer schweren Situation schnell auf dem Handy nach Hilfe, oft auch abends oder nachts.",
            "eine ruhige, klare Seite mit Notfallnummer und Vorsorge-Infos", "ab 990 €", "ab 29 €", "Vertrauen im ersten Moment"),
 "handel": ("Kunden prüfen vor dem Weg in die Stadt kurz auf dem Handy, ob Sie haben, was sie suchen.",
            "eine Sortiments- und Aktionsseite, die Sie selbst pflegen", "ab 690 €", "ab 29 €", "mehr Laufkundschaft"),
}

def hooks(r):
    """Liefert verifizierbare Beobachtungen, stärkste zuerst."""
    H = []
    txt = (r.get("text") or "").lower()
    dom = (r.get("url") or "").replace("https://", "").replace("http://", "").replace("www.", "").split("/")[0]
    if "ihr name ihr slogan" in txt:
        H.append("Oben auf Ihrer Startseite steht noch der Vorlagentext 'Ihr Name Ihr Slogan'.")
    if "plesk" in txt and "default" in txt:
        H.append(f"Unter {dom} erscheint derzeit nur eine Standardseite des Hosters, keine Website.")
    if "betrieben und verwaltet durch lieferando" in txt:
        H.append("Ihre Website wird von Lieferando betrieben, nicht von Ihnen.")
    if r.get("status_kind") == "http":
        H.append(f"{dom} lässt sich nicht verschlüsselt aufrufen. Chrome und Safari zeigen Besuchern dann 'Nicht sicher' an.")
    mw = r.get("mob_scrollW") or 390
    if r.get("live") and not r.get("viewport"):
        H.append("Ihre Seite ist nicht für Smartphones angepasst. Auf dem Handy erscheint sie stark verkleinert, man muss zoomen, um etwas zu lesen.")
    elif r.get("live") and mw > 400:
        H.append("Auf dem Handy ist Ihre Seite breiter als der Bildschirm. Man muss seitlich wischen, um alles zu sehen.")
    ls = r.get("load_s") or 0
    if r.get("live") and ls >= 14.8:
        H.append("Ich habe über 350 Websites aus Neunkirchen unter gleichen Bedingungen geladen. Ihre Startseite gehörte zu den langsamsten zehn Prozent.")
    lm = r.get("lastmod") or ""
    import re
    y = re.search(r"(19|20)\d\d", lm)
    if r.get("live") and y and int(y.group(0)) <= 2021:
        H.append(f"Laut Server wurde Ihre Startseite zuletzt {y.group(0)} geändert.")
    if r.get("live") and (r.get("words") or 0) < 25:
        H.append("Auf Ihrer Startseite steht fast kein Text. Google kann dadurch kaum erkennen, was Sie anbieten.")
    gn, ga = r.get("g_n"), r.get("g_avg")
    if gn and gn >= 40 and ga and ga >= 4.0:
        H.append(f"Sie haben {gn} Google-Bewertungen mit {str(ga).replace('.',',')} Sternen. Auf Ihrer Website sieht man davon nichts.")
    if r.get("live") and not r.get("fb") and not r.get("ig"):
        H.append("Auf Ihrer Website gibt es keinen Link zu Instagram oder Facebook.")
    if r.get("live") and not r.get("booking") and segment(r.get("branch","")) in ("liefer","gastro","beauty","praxis","freizeit","hotel","kfz"):
        H.append("Auf Ihrer Startseite habe ich keine Möglichkeit gefunden, direkt online zu buchen, zu bestellen oder anzufragen.")
    return H

TIP = {
 "liefer": "Öffnen Sie Ihr Google-Unternehmensprofil und hinterlegen Sie Ihre aktuelle Speisekarte und einen direkten Bestelllink. Viele Gäste bestellen direkt aus Google Maps heraus.",
 "gastro": "Laden Sie im Google-Unternehmensprofil fünf aktuelle Fotos hoch: ein Gericht, den Gastraum, die Außenansicht, das Team, die Theke. Google empfiehlt selbst, Fotos regelmäßig zu erneuern.",
 "lebensmittel": "Tragen Sie Ihre Feiertagszeiten im Google-Profil als Sonderöffnungszeiten ein. Sonst zeigt Google Kunden womöglich 'geöffnet', obwohl Sie zu haben.",
 "hotel": "Antworten Sie in Ihrem Google-Profil auf die letzten fünf Bewertungen, auch auf die guten. Künftige Gäste lesen die Antworten mit.",
 "apotheke": "Prüfen Sie in Ihrem Google-Profil Mittagspause und Sonderöffnungszeiten. Falsche Zeiten führen schnell zu verärgerten Bewertungen.",
 "praxis": "Veröffentlichen Sie Ihre offene Stelle zusätzlich als Beitrag in Ihrem Google-Unternehmensprofil. Bewerber aus der Umgebung sehen ihn, wenn sie nach Ihrer Praxis suchen.",
 "beauty": "Fügen Sie in Ihrem Google-Profil Ihre Leistungen mit Preisen hinzu. Neukundinnen und Neukunden vergleichen genau das.",
 "freizeit": "Posten Sie diese Woche einen 15-Sekunden-Clip aus dem Training als Google-Beitrag und auf Instagram. Echte Einblicke überzeugen mehr als jedes Werbefoto.",
 "spielhalle": "Prüfen Sie die Öffnungszeiten in Ihrem Google-Profil und beantworten Sie die letzten Bewertungen sachlich. Das wirkt seriös und kostet nichts.",
 "kfz": "Hinterlegen Sie in Ihrem Google-Profil Ihre Leistungen, zum Beispiel Inspektion, Reifenwechsel und HU-Vorbereitung. Google zeigt sie bei passenden Suchen an.",
 "handwerk": "Laden Sie Vorher-Nachher-Fotos von drei aktuellen Aufträgen in Ihr Google-Profil. Nichts überzeugt neue Kunden schneller.",
 "beratung": "Prüfen Sie, ob Ihre Kanzlei bei Google unter der passenden Hauptkategorie steht. Sie entscheidet mit, bei welchen Suchen Sie erscheinen.",
 "bestatter": "Prüfen Sie, ob Ihre Notfallnummer im Google-Profil steht und die Erreichbarkeit rund um die Uhr eingetragen ist.",
 "handel": "Tragen Sie Ihre Samstags- und Feiertagszeiten im Google-Profil ein und laden Sie drei aktuelle Fotos vom Schaufenster hoch.",
}
