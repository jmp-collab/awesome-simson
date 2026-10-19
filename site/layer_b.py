"""Layer B: Umformulierung der sichtbaren Werbetexte in build.py. Rechtstexte (Impressum, Datenschutz) bleiben unverändert."""
p = "build.py"
s = open(p, encoding="utf-8").read()
R = [
# Pakete
('"Onepager, auf das Handy ausgelegt"', '"Eine Seite, gebaut fürs Smartphone"'),
('"Verschlüsselt (HTTPS), Impressum und Datenschutz"', '"HTTPS, Impressum und Datenschutzerklärung inklusive"'),
('"Klick zum Anrufen, Route, Öffnungszeiten"', '"Anruf per Fingertipp, Anfahrt, Öffnungszeiten"'),
('"Google-Profil verknüpft", ', '"Mit Ihrem Google-Profil verbunden", '),
('"Live in etwa 2 Wochen"', '"Online nach rund 2 Wochen"'),
('"Bis 6 Seiten"', '"Bis zu 6 Unterseiten"'),
('"Eine Branchenfunktion: Terminanfrage, Speisekarte oder Kursplan"', '"Eine Funktion für Ihre Branche, etwa Speisekarte, Kursplan oder Terminanfrage"'),
('"Fotos vor Ort in Neunkirchen"', '"Ich fotografiere bei Ihnen im Betrieb"'),
('"Lokale Suchbegriffe und strukturierte Daten für Google"', '"Strukturierte Daten und die Suchbegriffe, die Leute hier wirklich eintippen"'),
('"Alles aus Start"', '"Dazu alles aus Start"'),
('"Eigener Bestellweg, Reservierung oder Buchung"', '"Bestellen, reservieren oder buchen direkt bei Ihnen"'),
('"Weniger Provision an Plattformen"', '"Weniger Gebühren an Liefer- und Buchungsportale"'),
('"Speisekarte oder Zimmer pflegen Sie selbst"', '"Karte oder Zimmer ändern Sie selbst"'),
('"Auswertung: Anrufe, Anfragen, Bestellungen"', '"Übersicht, wie viele Anrufe, Anfragen und Bestellungen reinkommen"'),
('"Alles aus Betrieb"', '"Dazu alles aus Betrieb"'),
# Bausteine
('"Hosting, Updates, Backups, bis 30 Minuten Änderungen im Monat"', '"Server, Updates und Sicherungen, dazu bis 30 Minuten Änderungen pro Monat"'),
('"Einrichten, Kategorien, Fotos, Antworten auf Bewertungen"', '"Profil anlegen, Kategorien setzen, Fotos hochladen, Bewertungen beantworten"'),
('"Redaktionsplan, 2 bis 3 Beiträge pro Woche, Kurzvideos mit Untertiteln"', '"2 bis 3 Beiträge die Woche nach festem Plan, kurze Videos mit Untertiteln"'),
('"2 Stunden Workshop vor Ort: Angebote, Bewertungsantworten, Texte und Übersetzungen mit KI"', '"Zwei Stunden bei Ihnen im Betrieb: Angebote, Antworten auf Bewertungen, Texte und Übersetzungen mit KI"'),
('"Antwortvorlagen für Mails und Bewertungen, Speisekarten in mehreren Sprachen, wiederkehrende Texte"', '"Fertige Vorlagen für Mails und Bewertungen, Karten in mehreren Sprachen, alles, was Sie immer wieder schreiben"'),
('"Einträge in Verzeichnissen vereinheitlichen, Links von Vereinen, Partnern und lokalen Medien"', '"Gleiche Daten in allen Verzeichnissen, Verweise von Vereinen, Partnern und der Lokalpresse"'),
# Gastronomie
('h1="Mehr Bestellungen direkt bei Ihnen, weniger an die Plattform"', 'h1="Bestellungen landen bei Ihnen, nicht beim Lieferportal"'),
('lead="Für Restaurants, Pizzerien, Imbisse, Döner und Lieferdienste in Neunkirchen. Gäste entscheiden auf dem Handy, in Sekunden."', 'lead="Für Restaurants, Pizzerien, Imbisse, Dönerläden und Lieferdienste in Neunkirchen. Wer Hunger hat, entscheidet am Handy und braucht dafür ein paar Sekunden."'),
('"Die Speisekarte ist ein PDF oder ein Foto und auf dem Handy nicht lesbar"', '"Die Karte liegt als PDF oder Foto vor, am Handy kann man sie kaum lesen"'),
('"Bestellungen laufen über eine Plattform, die bei jeder Bestellung Provision nimmt"', '"Bestellt wird über ein Portal, das an jeder Bestellung mitverdient"'),
('"Öffnungszeiten auf Website, Google und Facebook widersprechen sich"', '"Website, Google und Facebook nennen unterschiedliche Öffnungszeiten"'),
('"Neue Bewertungen bleiben unbeantwortet"', '"Auf neue Bewertungen antwortet niemand"'),
('"Speisekarte als echte Seite, schnell, mit Fotos und Allergenen"', '"Die Karte als richtige Seite, schnell geladen, mit Fotos und Allergenangaben"'),
('"Bestellen per Telefon oder WhatsApp mit einem Fingertipp, auf Wunsch eigener Bestellweg"', '"Ein Tipp, und der Gast ruft an oder schreibt per WhatsApp. Wer mag, bekommt einen eigenen Bestellweg"'),
('"Ein Ort für Öffnungszeiten, der Google und Website gleich hält"', '"Öffnungszeiten an einer Stelle ändern, Google und Website ziehen mit"'),
('"Antwortvorlagen für Bewertungen mit KI, in Ihrem Ton"', '"KI-Vorlagen für Bewertungsantworten, die nach Ihnen klingen"'),
('extra="Speisekarte in mehreren Sprachen, Social Media mit Kurzvideos"', 'extra="eine mehrsprachige Karte und Kurzvideos für Instagram"'),
# Handwerk
('h1="Aufträge aus Google, ohne dass Sie am Rechner sitzen"', 'h1="Aufträge über Google, während Sie auf der Baustelle stehen"'),
('lead="Für Elektriker, Maler, Dachdecker, Sanitär, Schlüsseldienste und Kfz-Betriebe. Kunden suchen nach Leistung und Ort, meist im Notfall."', 'lead="Für Elektriker, Maler, Dachdecker, Sanitärbetriebe, Schlüsseldienste und Werkstätten. Gesucht wird nach Leistung plus Ort, oft dann, wenn es brennt."'),
('"Die Seite zeigt nicht, welche Leistungen Sie in welchem Umkreis anbieten"', '"Welche Arbeiten Sie machen und wie weit Sie fahren, steht nirgends"'),
('"Anfragen kommen ohne Fotos und Maße, Sie telefonieren hinterher"', '"Anfragen kommen ohne Fotos und Maße, also wird erst mal telefoniert"'),
('"Referenzen fehlen, obwohl Sie seit Jahren gute Arbeit machen"', '"Ihre gute Arbeit aus vielen Jahren sieht man online nicht"'),
('"Auf dem Handy ist die Telefonnummer nicht anklickbar"', '"Die Nummer lässt sich am Handy nicht antippen"'),
('"Eine Seite pro Hauptleistung, damit Google Sie für genau diese Suche zeigt"', '"Für jede Hauptleistung eine eigene Seite, die Google genau dieser Suche zuordnet"'),
('"Anfrageformular mit Foto-Upload, Sie sehen vorab, worum es geht"', '"Anfrage mit Foto-Upload, damit Sie vorher wissen, was Sie erwartet"'),
('"Referenzgalerie, die Sie per Handy selbst ergänzen"', '"Eine Bildergalerie Ihrer Arbeiten, die Sie vom Handy aus füllen"'),
('"Anruf mit einem Fingertipp, oben auf jeder Seite"', '"Oben auf jeder Seite: antippen, anrufen"'),
('extra="Google-Profil mit Fotos und Leistungen, Bewertungs-QR für die Rechnung"', 'extra="ein Google-Profil mit Fotos und Leistungen sowie ein QR-Code für Bewertungen auf der Rechnung"'),
# Praxen
('h1="Weniger Anrufe am Empfang, mehr Zeit für Patienten"', 'h1="Weniger Telefonate am Empfang, mehr Ruhe für die Behandlung"'),
('lead="Für Physiotherapie, Arzt- und Zahnarztpraxen, Apotheken und Heilpraktiker. Patienten wollen Sprechzeiten, Leistungen und einen einfachen Weg zum Termin."', 'lead="Für Physiotherapie, Arzt- und Zahnarztpraxen, Apotheken und Heilpraktiker. Patienten suchen drei Dinge: Sprechzeiten, Leistungen und einen einfachen Weg zum Termin."'),
('"Sprechzeiten und Urlaubszeiten sind veraltet, das Telefon klingelt"', '"Sprech- und Urlaubszeiten stimmen nicht mehr, also klingelt das Telefon"'),
('"Leistungen sind in Fachsprache beschrieben"', '"Die Leistungen stehen in Fachbegriffen da"'),
('"Die Seite ist nicht barrierearm, Ältere tun sich schwer"', '"Für ältere Patienten ist die Seite schwer zu bedienen"'),
('"Stellenanzeigen für Fachkräfte gehen unter"', '"Offene Stellen findet kaum jemand"'),
('"Sprechzeiten und Hinweise, die Sie selbst in einer Minute ändern"', '"Sprechzeiten und Hinweise ändern Sie selbst, in einer Minute"'),
('"Leistungen in klarer Sprache, mit großen Schriften und hohem Kontrast"', '"Leistungen verständlich erklärt, in großer Schrift mit kräftigem Kontrast"'),
('"Terminanfrage oder Anbindung an Ihr Buchungssystem"', '"Terminanfrage direkt auf der Seite oder Ihr vorhandenes Buchungssystem eingebunden"'),
('"Karriereseite, die bei Google für Ihre Stellen gefunden wird"', '"Eine Karriereseite, über die Bewerber Ihre Stellen bei Google finden"'),
('extra="KI-Workshop für Praxisteam: Briefe, Antworten und Infotexte schneller schreiben"', 'extra="ein KI-Workshop fürs Team, damit Briefe, Antworten und Infotexte schneller fertig sind"'),
# Handel
('h1="Damit Laufkundschaft Sie findet, bevor sie in die Stadt fährt"', 'h1="Gefunden werden, bevor die Kundschaft in die Stadt fährt"'),
('lead="Für Geschäfte, Friseure, Nagel- und Kosmetikstudios, Tanzschulen, Hotels und Freizeitbetriebe in Neunkirchen."', 'lead="Für Läden, Friseure, Nagel- und Kosmetikstudios, Tanzschulen, Hotels und Freizeitangebote in Neunkirchen."'),
('"Instagram ist aktiv, die Website seit Jahren nicht"', '"Auf Instagram passiert viel, auf der Website seit Jahren nichts"'),
('"Termine laufen nur per Telefon, auch nach Feierabend"', '"Termine gibt es nur am Telefon, nach Feierabend also gar nicht"'),
('"Angebote und Aktionen erreichen nur Stammkunden"', '"Von Aktionen erfahren nur die Stammkunden"'),
('"Google zeigt alte Fotos und falsche Öffnungszeiten"', '"Bei Google stehen alte Bilder und falsche Zeiten"'),
('"Website und Instagram aus einem Guss, neue Beiträge erscheinen automatisch"', '"Website und Instagram passen zusammen, neue Posts tauchen von selbst auf"'),
('"Online-Termin oder Anfrage per WhatsApp, rund um die Uhr"', '"Termin online oder per WhatsApp anfragen, zu jeder Uhrzeit"'),
('"Aktionsseite pro Saison, teilbar per Link und QR"', '"Eine Seite pro Saison-Aktion, zum Teilen per Link oder QR-Code"'),
('"Google-Profil mit aktuellen Fotos und Beiträgen"', '"Ein Google-Profil mit frischen Bildern und Beiträgen"'),
('extra="Social Media mit Redaktionsplan, Bewertungs-QR an der Kasse"', 'extra="Social Media nach Plan und ein Bewertungs-QR an der Kasse"'),
# Stats
('"Websites von Betrieben aus Neunkirchen geprüft"', '"Websites Neunkirchener Betriebe habe ich geprüft"'),
('"erreichbaren Seiten ist nicht für das Handy angepasst"', '"der erreichbaren Seiten funktioniert am Handy nicht richtig"'),
('"liefern Google keine strukturierten Daten zu Adresse und Öffnungszeiten"', '"geben Google Adresse und Öffnungszeiten nicht maschinenlesbar mit"'),
('"verlinken weder Instagram noch Facebook"', '"haben keinen Link zu Instagram oder Facebook"'),
# FAQ
('"Nichts. Ich baue Ihnen eine Vorschau Ihrer neuen Startseite mit Ihren Inhalten. Gefällt sie Ihnen nicht, ist die Sache erledigt."', '"Gar nichts. Sie bekommen Ihre neue Startseite als Vorschau, mit Ihren Inhalten. Wenn sie Ihnen nicht zusagt, war es das."'),
('"Die Hälfte bei Auftrag, die zweite Hälfte erst, wenn die Seite online ist und Ihnen gefällt. Sie erhalten eine ordentliche Rechnung."', '"50 % bei Auftrag. Den Rest erst, wenn die Seite online ist und Sie zufrieden sind. Dafür gibt es eine ordentliche Rechnung."'),
('"Per Überweisung. Auf jeder Rechnung steht zusätzlich ein Zahllink für Karte, SEPA-Lastschrift, Apple Pay oder Google Pay. Wer möchte, kann über denselben Link auch mit der Kryptowährung USDC zahlen. Die Betreuung läuft bequem per Lastschrift."', '"Ganz normal per Überweisung. Jede Rechnung hat außerdem einen Zahllink: Karte, SEPA-Lastschrift, Apple Pay oder Google Pay. Über denselben Link geht auch die Kryptowährung USDC. Die Betreuung buche ich per Lastschrift ab."'),
('"Nein. Ich übernehme Ihre bisherigen Inhalte, frage ein paar Dinge ab und schreibe den Rest. Sie geben nur frei."', '"Nein. Ich nehme, was auf Ihrer Seite schon steht, stelle ein paar Fragen und schreibe den Rest selbst. Sie lesen und geben frei."'),
('"Ja. Domain, Inhalte und Fotos gehören Ihnen. Wenn Sie wechseln wollen, bekommen Sie alles mit."', '"Ja. Domain, Texte und Bilder sind Ihr Eigentum. Wechseln Sie irgendwann, nehmen Sie alles mit."'),
('"Öffnungszeiten, Speisekarte, Hinweise und Fotos ja. Für alles andere schreiben Sie mir kurz, das ist in der Betreuung enthalten."', '"Öffnungszeiten, Karte, Hinweise und Bilder schon. Für den Rest reicht eine kurze Nachricht an mich, das deckt die Betreuung ab."'),
('"KI hilft mir, schneller und günstiger zu arbeiten, und Ihnen im Alltag: Antworten auf Bewertungen, Angebote, Übersetzungen. Ich zeige Ihnen, was davon in Ihrem Betrieb wirklich Zeit spart."', '"Mit KI arbeite ich schneller, das drückt den Preis. Im Betrieb hilft sie bei Bewertungsantworten, Angeboten und Übersetzungen. Ich zeige Ihnen, was davon bei Ihnen tatsächlich Zeit spart."'),
('"Schwerpunkt ist Neunkirchen mit Wiebelskirchen, Wellesweiler, Spiesen-Elversberg, Ottweiler, Schiffweiler und Illingen. Ich komme vorbei, das Gespräch findet bei Ihnen im Betrieb statt."', '"Hauptsächlich Neunkirchen samt Wiebelskirchen und Wellesweiler, außerdem Spiesen-Elversberg, Ottweiler, Schiffweiler und Illingen. Besprochen wird bei Ihnen im Betrieb, ich komme vorbei."'),
# Startseite
('<h1>Ihre Website, so gut wie Ihr Betrieb.</h1>', '<h1>Ihr Betrieb ist gut. Ihre Website sollte es auch sein.</h1>'),
('Ich baue Websites für Betriebe in Neunkirchen, die auf dem Handy funktionieren, bei Google gefunden werden und Anrufe bringen. Bevor Sie einen Euro zahlen, sehen Sie eine Vorschau.', 'Ich mache Websites für Neunkirchener Betriebe: am Handy gut bedienbar, bei Google auffindbar, mit Anrufen als Ergebnis. Eine Vorschau sehen Sie, bevor Sie irgendetwas bezahlen.'),
('Ich habe die Websites von 374 Betrieben aus Neunkirchen aufgerufen, auf dem Handy und am Rechner. Das Ergebnis zeigt, wie viel Kundschaft heute an der ersten Hürde hängen bleibt.', '374 Websites von Betrieben aus Neunkirchen habe ich am Handy und am Rechner geöffnet. Die Zahlen zeigen, wie oft Kunden schon beim ersten Klick scheitern.'),
('<h2>Vom ersten Blick bis online in etwa zwei Wochen</h2>', '<h2>Rund zwei Wochen vom Entwurf bis zur fertigen Seite</h2>'),
('<p>Ich baue Ihre neue Startseite mit Ihren Texten und Fotos. Kostenlos.</p>', '<p>Ihre neue Startseite, gebaut aus Ihren Texten und Bildern. Kostet nichts.</p>'),
('<p>Ich komme vorbei, wir gehen die Vorschau auf Ihrem Handy durch.</p>', '<p>Ich schaue vorbei und wir sehen uns die Vorschau zusammen am Handy an.</p>'),
('<p>Sie bekommen ein Angebot mit festem Preis. Die Hälfte bei Auftrag.</p>', '<p>Sie erhalten ein Angebot zum Festpreis. Bei Auftrag wird die Hälfte fällig.</p>'),
('<p>Seite geht live, Google-Profil passt dazu. Erst dann zahlen Sie den Rest.</p>', '<p>Die Seite ist online, das Google-Profil stimmt. Jetzt erst kommt die zweite Hälfte.</p>'),
('<h2>Jede Branche hat einen anderen Hebel</h2>', '<h2>Was in Ihrer Branche den Unterschied macht</h2>'),
('<p>Antworten auf Google-Bewertungen, Angebote, Speisekarten in drei Sprachen, Texte für Instagram: Vieles davon erledigt KI heute in Minuten. Ich richte das so ein, dass es zu Ihrem Betrieb passt, und zeige Ihrem Team, wie es geht.</p>', '<p>Bewertungen beantworten, Angebote schreiben, die Karte in drei Sprachen, Posts für Instagram. So etwas schafft KI inzwischen in Minuten. Ich stelle es passend für Ihren Betrieb ein und erkläre Ihrem Team die Handgriffe.</p>'),
('<h3>Typische Zeitfresser, die wegfallen</h3>', '<h3>Was Sie sich künftig sparen</h3>'),
('<li>Jede Bewertung einzeln beantworten</li><li>Angebote aus alten Vorlagen zusammenkopieren</li><li>Speisekarte oder Aushang übersetzen</li><li>Woche für Woche überlegen, was auf Instagram soll</li>', '<li>Bewertungen einzeln von Hand beantworten</li><li>Angebote aus alten Dateien zusammenstückeln</li><li>Karte oder Aushang selbst übersetzen</li><li>Jede Woche grübeln, was auf Instagram kommt</li>'),
('<h2>Was Inhaber mich zuerst fragen</h2>', '<h2>Das fragen mich Inhaber am häufigsten</h2>'),
# CTA
('Ich baue Ihnen eine Vorschau Ihrer neuen Startseite mit Ihren Inhalten. Kostenlos, unverbindlich und persönlich vorbeigebracht.', 'Sie bekommen Ihre neue Startseite als Vorschau, mit Ihren Inhalten. Kostenlos, ohne Verpflichtung, und ich bringe sie persönlich vorbei.'),
# Leistungen
('<h1>Feste Preise. Erst sehen, dann zahlen.</h1>', '<h1>Festpreise. Und gezahlt wird erst nach dem Hinsehen.</h1>'),
('<p>Ich arbeite hauptberuflich im Online-Marketing und setze KI dort jeden Tag ein. Diese Erfahrung bringe ich in kleine Betriebe: kein Großprojekt, sondern konkrete Abläufe, die ab der ersten Woche Zeit sparen.</p>', '<p>Im Hauptberuf mache ich Online-Marketing und nutze KI dabei täglich. Kleine Betriebe brauchen davon kein Großprojekt. Sie brauchen ein paar feste Abläufe, die schon in der ersten Woche Zeit sparen.</p>'),
('<p>Datenschutz gehört dazu. Ich zeige, welche Daten in welches Werkzeug dürfen und welche nicht.</p>', '<p>Auch der Datenschutz kommt nicht zu kurz: Sie erfahren, welche Daten in welches Werkzeug gehören und welche draußen bleiben.</p>'),
('<p>2 Stunden mit Ihrem Team. Danach schreibt jeder Bewertungsantworten, Angebote und Infotexte mit KI. Ab 290 €.</p>', '<p>Zwei Stunden mit Ihrem Team. Hinterher kann jeder Bewertungsantworten, Angebote und Infotexte mit KI erstellen. Ab 290 €.</p>'),
('<p>Vorlagen und Abläufe für Ihre wiederkehrenden Texte, laufend gepflegt. Ab 49 € im Monat.</p>', '<p>Vorlagen und Abläufe für alles, was Sie regelmäßig schreiben, von mir aktuell gehalten. Ab 49 € im Monat.</p>'),
('<h2>So einfach wie beim Bäcker</h2>', '<h2>Bezahlen ohne Umstände</h2>'),
('<p>Sie erhalten eine Rechnung und überweisen wie gewohnt. Auf der Rechnung steht zusätzlich ein Zahllink: Damit zahlen Sie per Karte, SEPA-Lastschrift, Apple Pay oder Google Pay. Über denselben Link ist auch eine Zahlung mit der Kryptowährung USDC möglich.</p>', '<p>Es gibt eine Rechnung, und Sie überweisen wie immer. Wer lieber anders zahlt, nutzt den Zahllink auf der Rechnung: Karte, SEPA-Lastschrift, Apple Pay oder Google Pay. Derselbe Link nimmt auch die Kryptowährung USDC an.</p>'),
('<p>Die monatliche Betreuung läuft per Lastschrift, monatlich kündbar nach den ersten 12 Monaten.</p>', '<p>Die Betreuung wird monatlich abgebucht. Nach den ersten 12 Monaten können Sie zu jedem Monatsende kündigen.</p>'),
('<li>Vorschau ansehen, kostenlos</li><li>Angebot mit Festpreis per Mail, Antwort "Einverstanden" genügt</li><li>Rechnung über 50 %</li><li>Livegang, dann Restrechnung</li><li>Betreuung startet im Folgemonat</li>', '<li>Kostenlose Vorschau anschauen</li><li>Festpreisangebot per Mail, ein "Einverstanden" reicht</li><li>Erste Rechnung über 50 %</li><li>Seite geht online, danach die Restrechnung</li><li>Die Betreuung beginnt im Monat darauf</li>'),
('<h2>Alles Wichtige zu Preis und Ablauf</h2>', '<h2>Fragen zu Preis und Ablauf</h2>'),
# Branchen-Übersicht
('<h1>Websites, die zu Ihrem Geschäft passen</h1>', '<h1>Eine Website, die zu Ihrem Geschäft passt</h1>'),
('<p class="lead">Ein Restaurant braucht etwas anderes als ein Dachdecker. Wählen Sie Ihre Branche.</p>', '<p class="lead">Ein Restaurant braucht andere Dinge als ein Dachdecker. Suchen Sie Ihre Branche aus.</p>'),
# Portfolio
('<p class="lead">Drei Konzepte für erfundene Betriebe aus typischen Branchen. Echte Kundenprojekte zeige ich hier nur mit Freigabe der Inhaber, mit Vorher, Nachher und echten Zahlen.</p>', '<p class="lead">Hier sehen Sie drei Konzepte für ausgedachte Betriebe aus typischen Branchen. Echte Projekte kommen nur mit Zustimmung der Inhaber auf diese Seite, und dann mit Vorher, Nachher und echten Zahlen.</p>'),
('<h2>Der Standard, nicht das Extra</h2>', '<h2>Bei jeder Seite dabei</h2>'),
('<li>Ausgelegt auf das Handy, dann auf den Rechner</li><li>Lädt in unter 2 Sekunden, ohne Baukasten und Plugins</li>', '<li>Zuerst fürs Handy gebaut, danach für den Rechner</li><li>In unter 2 Sekunden geladen, ganz ohne Baukasten und Plugins</li>'),
('<li>Barrierearm: große Schrift, hoher Kontrast, per Tastatur bedienbar</li><li>Statistik ohne Cookie-Banner</li>', '<li>Barrierearm mit großer Schrift, starkem Kontrast und Tastaturbedienung</li><li>Besucherstatistik, für die kein Cookie-Banner nötig ist</li>'),
('"Die Vorschau zeigt Ihre eigene Startseite, nicht ein Beispiel von anderen."', '"In der Vorschau sehen Sie Ihre eigene Startseite statt eines fremden Beispiels."'),
# Check
('<h1>Wie gut ist Ihre Website auf dem Handy?</h1>', '<h1>Wie schlägt sich Ihre Website am Handy?</h1>'),
('<p class="lead">Adresse eingeben, in etwa 20 Sekunden sehen Sie eine Ampel für die wichtigsten Punkte. Ohne Anmeldung.</p>', '<p class="lead">Geben Sie die Adresse ein. Nach etwa 20 Sekunden zeigt eine Ampel, wo es hakt. Anmelden müssen Sie sich nicht.</p>'),
('<p class="muted">Ich schaue mir Ihre Seite zusätzlich von Hand an und schicke Ihnen den Bericht per Mail, kostenlos.</p>', '<p class="muted">Zusätzlich sehe ich mir Ihre Seite selbst an und schicke Ihnen kostenlos einen Bericht per Mail.</p>'),
# Über mich
('<p class="lead">Ich arbeite hauptberuflich als SEO-Manager im Online-Handel. Ich weiß also, wie Google Seiten liest und warum Kunden auf dem Handy nach drei Sekunden wieder weg sind.</p>', '<p class="lead">Hauptberuflich bin ich SEO-Manager im Online-Handel. Wie Google eine Seite liest und warum Leute am Handy nach drei Sekunden abspringen, ist mein Tagesgeschäft.</p>'),
('wissen zu den Betrieben in Neunkirchen, die sonst keine Agentur bezahlen würden: der Imbiss an der Ecke, der Elektriker, die Praxis im Erdgeschoss. Ich arbeite persönlich, komme vorbei und baue Ihnen erst eine Vorschau, bevor wir über Geld reden.', 'wissen zu Betrieben in Neunkirchen, für die eine Agentur nie infrage käme: zum Imbiss an der Ecke, zum Elektriker, zur Praxis im Erdgeschoss. Ich komme persönlich vorbei, und über Geld reden wir erst, wenn Sie Ihre Vorschau gesehen haben.'),
('<h3>Woran Sie mich messen können</h3>', '<h3>Darauf können Sie mich festnageln</h3>'),
('<li>Feste Preise, auf dieser Seite veröffentlicht</li><li>Vorschau vor dem ersten Euro</li><li>Zweite Hälfte erst nach Livegang</li><li>Domain und Inhalte gehören Ihnen</li><li>Antwort innerhalb eines Werktags</li>', '<li>Festpreise, öffentlich auf dieser Seite</li><li>Erst die Vorschau, dann der erste Euro</li><li>Zweite Rate erst, wenn die Seite online ist</li><li>Domain und Inhalte bleiben Ihre</li><li>Antwort spätestens am nächsten Werktag</li>'),
# Kontakt
('<p class="lead">Sagen Sie mir, um welchen Betrieb es geht. Ich melde mich innerhalb eines Werktags und baue Ihnen eine Vorschau Ihrer neuen Startseite.</p>', '<p class="lead">Nennen Sie mir Ihren Betrieb. Spätestens am nächsten Werktag melde ich mich, danach entsteht Ihre Vorschau.</p>'),
('<li>Kostenlos und unverbindlich</li><li>Mit Ihren eigenen Inhalten</li>', '<li>Kostet nichts, verpflichtet zu nichts</li><li>Gebaut aus Ihren eigenen Inhalten</li>'),
# Danke
('<p class="lead">Ich melde mich innerhalb eines Werktags bei Ihnen. Wenn es eilt, rufen Sie mich einfach an.</p>', '<p class="lead">Spätestens am nächsten Werktag hören Sie von mir. Falls es eilt, rufen Sie einfach an.</p>'),
# Vorschau-Seite
('<p class="lead">Diesen Entwurf habe ich mit Ihren eigenen Texten und Fotos gebaut. Ziehen Sie den Regler, um Ihre Seite heute mit dem Entwurf zu vergleichen.</p>', '<p class="lead">Der Entwurf besteht aus Ihren eigenen Texten und Bildern. Mit dem Regler vergleichen Sie ihn direkt mit Ihrer heutigen Seite.</p>'),
('<h3>Was mir aufgefallen ist</h3>', '<h3>Das ist mir aufgefallen</h3>'),
('<h3>Was der Entwurf ändert</h3>', '<h3>Das ändert sich mit dem Entwurf</h3>'),
('<p>Für genau diesen Entwurf, fertig online, mit Impressum, Datenschutz und Google-Profil verknüpft. Betreuung danach ab 29 € im Monat.</p>', '<p>Gilt für genau diesen Entwurf, fertig online, samt Impressum, Datenschutz und Verbindung zum Google-Profil. Die Betreuung kostet danach ab 29 € im Monat.</p>'),
('<p class="muted">Ein kurzes Ja genügt. Ich melde mich und wir gehen ihn in 15 Minuten bei Ihnen durch.</p>', '<p class="muted">Ein Ja reicht. Ich melde mich, und wir sprechen ihn in 15 Minuten bei Ihnen durch.</p>'),
# gemeinsame Sätze
('PAY_NOTE = "Sie sehen eine kostenlose Vorschau, bevor Sie zahlen. Die zweite Hälfte zahlen Sie erst nach dem Livegang."', 'PAY_NOTE = "Bevor Sie zahlen, sehen Sie eine kostenlose Vorschau. Die zweite Hälfte wird erst fällig, wenn die Seite online ist."'),
('Websites, Google-Profile und KI für Betriebe in {E(C["region"])}. Persönlich, mit festen Preisen und einer kostenlosen Vorschau vor dem ersten Euro.', 'Websites, Google-Profile und KI für Betriebe in {E(C["region"])}. Persönlich betreut, zum Festpreis, mit kostenloser Vorschau vorab.'),
]
miss = []
for a, b in R:
    n = s.count(a)
    if n != 1: miss.append((n, a[:70])); continue
    s = s.replace(a, b)
open(p, "w", encoding="utf-8").write(s)
print("ersetzt:", len(R) - len(miss), "von", len(R))
for m in miss: print("FEHLT/MEHRFACH", m)
