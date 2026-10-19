#!/bin/bash
# Spiegelt Arbeitsstand nach GitHub (Branch saarseiten-akquise in jmp-collab/neu)
set -e
S=/home/claude/store
rm -rf $S/site $S/nk
mkdir -p $S/site $S/nk
tar -C /home/claude/site --exclude node_modules --exclude __pycache__ --exclude ./dist --exclude ./artifact -cf - . | tar -C $S/site -xf -
tar -C /home/claude/nk --exclude __pycache__ --exclude ./shots --exclude ./z --exclude './data/*.png' -cf - . | tar -C $S/nk -xf -
cd $S && git add -A && (git diff --cached --quiet || git commit -q -m "${1:-Sync Akquise-Stand}") && git push -q origin saarseiten-akquise
git log --oneline -1
