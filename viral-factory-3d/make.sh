#!/usr/bin/env bash
# Build one video: ./make.sh <video-folder>  (folder holds script.json + index.html)
set -euo pipefail
cd "$(dirname "$0")"; V=$1
python3 tts.py "$V/script.json" "$V"
python3 render.py "$V" video
mv "$V/video_tmp.mp4" "$V/video.mp4"
python3 sfx.py "$V" "$RANDOM"
ffmpeg -y -loglevel error -i "$V/video.mp4" -i "$V/mix.wav" -map 0:v -map 1:a -c:v copy -c:a aac -b:a 160k -shortest "$V/final.mp4"
echo "built $V/final.mp4"
