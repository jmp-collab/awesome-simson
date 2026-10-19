# Stündliche Lead-Welle (Runbook für Claude)
Ziel: Jede Stunde 5 neue Leads aus der Queue mit Vorher/Nachher, Preis, Zusatzleistungen und Vorschau-Seite.
1. `cat wave/state.json` -> nächste 5 Slugs aus `queue` (Reihenfolge = Ranking). Domain-Kaperungen/geparkte Seiten nur nehmen, wenn sich der Betrieb sicher identifizieren lässt.
2. `python3 wave/fetch.py SLUG...` (Vorher-Screenshots, Text). Danach `python3 wave/deep.py URL...` und `python3 wave/imgs.py KURZ MAX URL...` für Inhalte und Fotos. Fehlende Fakten per WebSearch/WebFetch (Das Örtliche, Gelbe Seiten, speisekarte.menu, Lieferando-Verzeichnisse). Nichts erfinden: unbekannte Zeiten/Preise weglassen.
3. Pro Lead `wave/content/KURZ.json` schreiben (Felder wie wave/content/heil.json; Themes: doener, gelato, papier, metall, beauty, praxis). Preise nie unter 690 €.
4. `python3 wave/render.py WELLE KURZ...` -> out/welle_NN/, out/Welle_NN_Vorher-Nachher.zip, site/dist neu gebaut.
4b. `bash wave/post_wave.sh WELLE KURZ...` -> Technik-Check (audit2.py, gemessen), Befunde und Nutzen (analyse.py, profile.json: Typ, Beispielwert, Anzahl je Lead ergänzen!), Vorschauseiten mit Website-Check und Rechner, druckbarer Website-Check je Betrieb (out/checks/*.pdf), Analyse-Mappe und Prioritätenliste; alles in die Wellen-ZIP.
5. Kontrollblatt rendern und ansehen (Mobil-Überlauf, leere Bereiche), ggf. korrigieren und neu rendern.
6. Artifact-Vorschau neu veröffentlichen: Artifact mit file_path=/home/claude/site/artifact/index.html (vorher aus dist/index.html erzeugen), root="/home/claude/site", files-Quellen "dist/...", nur neue v/*.html und assets/v/*.webp.
7. ZIP per SendUserFile schicken, kurze Nachricht (welche Betriebe, wichtigster Hebel je Betrieb).
8. Nächste Welle mit send_later in 60 Minuten planen.
9. Nach jeder Welle sichern: `/home/claude/store/sync.sh "Welle NN: Betriebe ..."` (GitHub jmp-collab/neu, Branch saarseiten-akquise). Kein Google Drive: Das verbundene Drive ist das Firmenkonto (racing-planet.de), dort keine Daten der Selbstständigkeit ablegen.

## Wiederherstellen nach Container-Neustart
Wenn /home/claude/nk fehlt:
1. `git clone --depth 1 -b saarseiten-akquise https://github.com/jmp-collab/neu /home/claude/store` (Repo vorher mit add_repo, access push, anhängen)
2. `cp -r /home/claude/store/nk /home/claude/nk && cp -r /home/claude/store/site /home/claude/site`
3. `cd /home/claude/site && npm i @fontsource/familjen-grotesk @fontsource/atkinson-hyperlegible @fontsource/jetbrains-mono` ist nicht nötig (Fonts liegen in assets/fonts). `pip install qrcode jinja2 --break-system-packages` falls fehlend.
4. `cd /home/claude/store && git checkout -B saarseiten-akquise` und sync.sh liegt bereits im Repo.
