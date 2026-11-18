# usage: grab.sh DIR N  -> copies newest N speko wavs (by blob ts) as l1..lN
cd /tmp/claude-tool-results/*/ && ls mcp-Speko-blob-*.wav | sort -t- -k4,4n | tail -$2 | awk '{print NR, $0}' | while read i f; do cp "$f" "$1/l$i.wav"; done
for f in $1/l*.wav; do printf "%s %.2f\n" $f $(ffprobe -v error -show_entries format=duration -of csv=p=0 $f); done
