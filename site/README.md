# Saarseiten Website

Statische Website mit Build-Skript. Kein CMS, keine Plugins.

## Bauen
1. `config.json` ausfüllen: full_name, street, zip_city, phone, phone_display, whatsapp, email, cal_link (optional), umami_src und umami_id (optional), code_salt (einmal festlegen, danach nie ändern).
2. `pip install qrcode pillow`
3. `python3 build.py --live` erzeugt `dist/`, die QR-Codes in `qr/` und `vorschau-codes.csv`. Ohne `--live` entsteht ein Vorschau-Build, Formulare senden dann nicht.

## Veröffentlichen (Netlify)
- `dist/` als Site hochladen, Ordner `netlify/functions` als Functions (Website-Check unter `/api/check`).
- Umgebungsvariable `PSI_API_KEY` (Google PageSpeed Insights, kostenlos) setzen, dann misst der Check die mobile Ladezeit.
- Netlify Forms aktivieren, Benachrichtigung an die eigene Mail. Formulare: kontakt, vorschau-ja, check-bericht.

## Vorschau-Seiten für Briefe
- Texte pro Betrieb: `data/vorschau_texte.json`, Preise und Stammdaten: `data/top10.json`.
- Bilder: `assets/v/<kurzname>-vorher|nachher-desk|mob.webp`.
- Jede Seite liegt unter `/v/<code>`, ist `noindex` und läuft 60 Tage ab Build-Datum.
- `vorschau-codes.csv` verbindet Code, Betrieb und QR-Datei. Den Code in die Spalte Vorschau_Link des Outreach-Blatts übernehmen.
