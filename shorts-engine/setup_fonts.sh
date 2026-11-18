#!/usr/bin/env bash
# Downloads the fonts used by the style presets into /home/claude/shorts/fonts as TTF.
set -euo pipefail
OUT=/home/claude/shorts/fonts; TMP=$(mktemp -d); mkdir -p "$OUT"; cd "$TMP"
for p in bebas-neue newsreader hanken-grotesk dm-mono fredoka quicksand space-grotesk shrikhand libre-baskerville archivo-black jetbrains-mono inter barlow ibm-plex-mono; do
  npm pack "@fontsource/$p" -q >/dev/null 2>&1 && tar xzf fontsource-$p-*.tgz && mv package "$p"
done
python3 - "$OUT" <<'EOF'
import sys, os
from fontTools.ttLib import TTFont
out = sys.argv[1]
want = {'bebas-neue':[400],'newsreader':[400,600],'hanken-grotesk':[500,800],'dm-mono':[500],'fredoka':[600,700],'quicksand':[600,700],
        'space-grotesk':[500,700],'shrikhand':[400],'libre-baskerville':[400,700],'archivo-black':[400],'jetbrains-mono':[500,700],
        'inter':[600,800,900],'barlow':[600,900],'ibm-plex-mono':[500]}
for p, ws in want.items():
    for w in ws:
        src = f'{p}/files/{p}-latin-{w}-normal.woff'
        if os.path.exists(src):
            f = TTFont(src); f.flavor = None; f.save(f'{out}/{p}-{w}.ttf')
print(sorted(os.listdir(out)))
EOF
