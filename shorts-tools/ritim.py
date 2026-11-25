#!/usr/bin/env python3
"""Fon müziğinin vuruşlarını (beat) ve güçlü vurguları bulur; sahne geçişlerini müziğe oturtmak için.

Kullanım:
  python3 ritim.py <müzik dosyası> [--fps 30] [--cikti beats.json]

Çıktı (JSON):
  {"tempo": 112.3, "sure": 31.2, "beats": [0.52, 1.06, ...], "vurgular": [2.13, 6.40, ...],
   "beat_kareleri": [16, 32, ...], "vurgu_kareleri": [...]}
  - beats: her vuruşun saniyesi
  - vurgular: enerjinin en çok sıçradığı vuruşlar (sahne kesmek, "GÜMM" efekti, zoom için en iyi anlar)

Kural önerisi: sahne değişimlerini en yakın beat'e kaydır (±3 kare), büyük olayları vurgulara koy.
"""
import argparse, json
import numpy as np


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("muzik"); ap.add_argument("--fps", type=int, default=30); ap.add_argument("--cikti")
    ap.add_argument("--vurgu-sayisi", type=int, default=8)
    a = ap.parse_args()
    import librosa
    y, sr = librosa.load(a.muzik, sr=22050, mono=True)
    tempo, frames = librosa.beat.beat_track(y=y, sr=sr, units="frames")
    beats = librosa.frames_to_time(frames, sr=sr)
    onset = librosa.onset.onset_strength(y=y, sr=sr)
    strength = onset[np.clip(frames, 0, len(onset) - 1)] if len(frames) else np.array([])
    # vurgular: güçlü ve birbirinden en az 1.5 sn uzak vuruşlar
    order = np.argsort(-strength); picked = []
    for i in order:
        t = float(beats[i])
        if all(abs(t - p) >= 1.5 for p in picked):
            picked.append(t)
        if len(picked) >= a.vurgu_sayisi:
            break
    picked.sort()
    out = {"tempo": round(float(np.atleast_1d(tempo)[0]), 1), "sure": round(len(y) / sr, 2),
           "beats": [round(float(t), 3) for t in beats], "vurgular": [round(t, 3) for t in picked],
           "beat_kareleri": [int(round(t * a.fps)) for t in beats], "vurgu_kareleri": [int(round(t * a.fps)) for t in picked]}
    if a.cikti:
        json.dump(out, open(a.cikti, "w"), indent=1)
    print(f"tempo {out['tempo']} BPM · {len(beats)} vuruş · {out['sure']} sn")
    print("vurgular (sn):", ", ".join(f"{t:.2f}" for t in picked))


if __name__ == "__main__":
    main()
