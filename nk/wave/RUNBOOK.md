# Stündliche Lead-Welle (Runbook für Claude)
Ziel: Jede Stunde 5 neue Leads aus der Queue mit Vorher/Nachher, Preis, Zusatzleistungen und Vorschau-Seite.
1. `cat wave/state.json` -> nächste 5 Slugs aus `queue` (Reihenfolge = Ranking). Domain-Kaperungen/geparkte Seiten nur nehmen, wenn sich der Betrieb sicher identifizieren lässt.
2. `python3 wave/fetch.py SLUG...` (Vorher-Screenshots, Text). Danach `python3 wave/deep.py URL...` und `python3 wave/imgs.py KURZ MAX URL...` für Inhalte und Fotos. Fehlende Fakten per WebSearch/WebFetch (Das Örtliche, Gelbe Seiten, speisekarte.menu, Lieferando-Verzeichnisse). Nichts erfinden: unbekannte Zeiten/Preise weglassen.
3. Pro Lead `wave/content/KURZ.json` schreiben (Felder wie wave/content/heil.json; Themes: doener, gelato, papier, metall, beauty, praxis). Preise nie unter 690 €.
4. `python3 wave/render.py WELLE KURZ...` -> out/welle_NN/, out/Welle_NN_Vorher-Nachher.zip, site/dist neu gebaut.
5. Kontrollblatt rendern und ansehen (Mobil-Überlauf, leere Bereiche), ggf. korrigieren und neu rendern.
6. Artifact-Vorschau neu veröffentlichen: Artifact mit file_path=/home/claude/site/artifact/index.html (vorher aus dist/index.html erzeugen, siehe Welle 1), files-Pfade relativ zu /home/claude/site (z. B. "dist/v/xyz.html"), nur neue v/*.html und assets/v/*.webp.
7. ZIP per SendUserFile schicken, kurze Nachricht (welche Betriebe, wichtigster Hebel je Betrieb).
8. Nächste Welle mit send_later in 60 Minuten planen.
