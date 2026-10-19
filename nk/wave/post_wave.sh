#!/bin/bash
# Nach render.py: Technik-Check, Analyse, Vorschauseiten, PDF-Checks und Mappe; PDFs in die Wellen-ZIP.
# Aufruf: bash wave/post_wave.sh WELLE KURZ1 KURZ2 ...
set -e
W=$(printf "%02d" $1); shift
cd /home/claude/nk
python3 wave/audit2.py "$@"
python3 wave/analyse.py
(cd /home/claude/site && python3 build.py | tail -1)
python3 wave/check_pdf.py "$@"
python3 wave/mappe_analyse.py > /dev/null
Z=out/Welle_${W}_Vorher-Nachher.zip
for k in "$@"; do f=$(ls out/checks/*_${k}_Website-Check.pdf); (cd out/checks && zip -q -j ../Welle_${W}_Vorher-Nachher.zip "$(basename $f)"); done
zip -q -j $Z out/Analyse-Mappe_alle_Leads.md out/Prioritaeten_alle_Leads.csv
echo "post_wave ok: $Z"
