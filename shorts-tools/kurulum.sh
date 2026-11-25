#!/usr/bin/env bash
# shorts-tools kurulumu. Bulut oturumunda ya da kendi bilgisayarında bir kez çalıştır.
# Modeller GitHub sürümlerinden iner (Hugging Face bulut proxy'sinde engelli olduğu için).
set -euo pipefail

MODEL_DIR="${SHORTS_TOOLS_MODELS:-$HOME/.cache/shorts-tools}"
WHISPER="${WHISPER_SIZE:-small}"   # tiny | base | small (small: Türkçe için önerilen)
mkdir -p "$MODEL_DIR"

echo "[1/4] Python paketleri"
pip install --break-system-packages -q \
  sherpa-onnx numpy scenedetect opencv-python-headless librosa soundfile \
  "rembg[cpu]" pillow pyloudnorm 2>&1 | grep -viE "warning|dependency resolver|requires" || true

echo "[2/4] Çevrimdışı Whisper ($WHISPER) ve Silero VAD"
if [ ! -f "$MODEL_DIR/sherpa-onnx-whisper-$WHISPER/$WHISPER-encoder.int8.onnx" ]; then
  curl -sSL --retry 3 -o "$MODEL_DIR/w.tar.bz2" \
    "https://github.com/k2-fsa/sherpa-onnx/releases/download/asr-models/sherpa-onnx-whisper-$WHISPER.tar.bz2"
  tar xjf "$MODEL_DIR/w.tar.bz2" -C "$MODEL_DIR" \
    "sherpa-onnx-whisper-$WHISPER/$WHISPER-encoder.int8.onnx" \
    "sherpa-onnx-whisper-$WHISPER/$WHISPER-decoder.int8.onnx" \
    "sherpa-onnx-whisper-$WHISPER/$WHISPER-tokens.txt"
  rm -f "$MODEL_DIR/w.tar.bz2"
fi
[ -f "$MODEL_DIR/silero_vad.onnx" ] || curl -sSL --retry 3 -o "$MODEL_DIR/silero_vad.onnx" \
  "https://github.com/k2-fsa/sherpa-onnx/releases/download/asr-models/silero_vad.onnx"

echo "[3/4] Arka plan kaldırma modeli (rembg isnet-general-use)"
python3 -c "from rembg import new_session; new_session('isnet-general-use')" >/dev/null 2>&1 || echo "  rembg modeli ilk kullanımda inecek"

echo "[4/4] earshot (çevrimdışı ses efekti üretici)"
command -v earshot >/dev/null || pip install --break-system-packages -q "earshot @ git+https://github.com/Leonxlnx/earshot" 2>&1 | grep -viE "warning|dependency resolver|requires" || true

echo "Hazır. Modeller: $MODEL_DIR"
