#!/usr/bin/env bash
# One-time setup in a fresh cloud session. Run from viral-factory-3d/.
set -euo pipefail
cd "$(dirname "$0")"
M=${VF_MODELS:-/home/claude/vf-models}; mkdir -p "$M"
[ -s "$M/kokoro.onnx" ] || curl -sSL -o "$M/kokoro.onnx" https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/kokoro-v1.0.onnx
[ -s "$M/voices.bin" ] || curl -sSL -o "$M/voices.bin" https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/voices-v1.0.bin
pip install --break-system-packages -q kokoro-onnx soundfile scipy playwright 2>/dev/null
[ -d node_modules/@fontsource/baloo-2 ] || npm i --no-save three@0.170 @fontsource/montserrat @fontsource/bebas-neue @fontsource/space-grotesk @fontsource/fredoka @fontsource/oswald @fontsource/jetbrains-mono @fontsource/baloo-2 >/dev/null 2>&1
echo "setup ok"
