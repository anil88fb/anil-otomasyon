#!/usr/bin/env python3
"""Bitmiş bir Shorts MP4'ünü yüklemeden önce denetler; istenirse ses seviyesini YouTube standardına çeker.

Kullanım:
  python3 kontrol.py <video.mp4> [--duzelt] [--sikistir] [--json rapor.json]

Bakılanlar:
  - çözünürlük 1080x1920 (9:16), fps, süre (Shorts için ≤ 60 sn, kanal hedefi 20-45 sn)
  - ses yüksekliği (LUFS). YouTube -14 LUFS'a göre normalleştirir; çok kısık video kaybeder.
    --duzelt: sesi -14 LUFS / -1 dBTP'ye iki geçişte çeker, görüntüye dokunmaz (video kopyalanır).
  --sikistir: H.264 CRF 23 ile yeniden kodlar (Shorts'ta gözle fark edilmez, dosya genelde 3-5 kat küçülür)
  - kesme sıklığı (PySceneDetect): ilk 3 sn'de en az bir hareket/kesme olmalı, ortalama 1,5-4 sn'de bir değişim
  - başta sessizlik: konuşma 0,5 sn'den geç başlıyorsa uyarı (izleyici kaydırıp geçer)
  - dosya boyutu: 100 MB üstü GitHub'a yüklenemez
"""
import argparse, json, os, re, shutil, subprocess, sys

FF = shutil.which("ffmpeg") or "ffmpeg"; FP = shutil.which("ffprobe") or "ffprobe"


def probe(p):
    r = subprocess.run([FP, "-v", "error", "-show_streams", "-show_format", "-of", "json", p], capture_output=True, text=True, check=True)
    return json.loads(r.stdout)


def loudness(p):
    r = subprocess.run([FF, "-hide_banner", "-nostats", "-i", p, "-vn", "-af", "loudnorm=I=-14:TP=-1:LRA=11:print_format=json", "-f", "null", "-"],
                       capture_output=True, text=True)
    m = re.search(r"\{[^{}]*\"input_i\"[^{}]*\}", r.stderr, re.S)
    return json.loads(m.group(0)) if m else None


def first_sound(p):
    r = subprocess.run([FF, "-hide_banner", "-nostats", "-i", p, "-vn", "-af", "silencedetect=n=-35dB:d=0.3", "-f", "null", "-"], capture_output=True, text=True)
    starts = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", r.stderr)]
    ends = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", r.stderr)]
    return ends[0] if starts and starts[0] < 0.05 and ends else 0.0


def cuts(p):
    try:
        from scenedetect import detect, ContentDetector
    except ImportError:
        return None
    return [s[0].seconds for s in detect(p, ContentDetector(threshold=27))][1:]


def fix(p, L):
    out = os.path.splitext(p)[0] + "_seviye.mp4"
    af = (f"loudnorm=I=-14:TP=-1:LRA=11:measured_I={L['input_i']}:measured_TP={L['input_tp']}:"
          f"measured_LRA={L['input_lra']}:measured_thresh={L['input_thresh']}:offset={L['target_offset']}:linear=true")
    subprocess.run([FF, "-v", "error", "-y", "-i", p, "-c:v", "copy", "-af", af, "-ar", "48000", "-c:a", "aac", "-b:a", "192k", out], check=True)
    return out


def compress(p):
    out = os.path.splitext(p)[0] + "_kucuk.mp4"
    subprocess.run([FF, "-v", "error", "-y", "-i", p, "-c:v", "libx264", "-preset", "veryfast", "-crf", "23", "-pix_fmt", "yuv420p",
                    "-movflags", "+faststart", "-c:a", "copy", out], check=True)
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("video"); ap.add_argument("--duzelt", action="store_true"); ap.add_argument("--sikistir", action="store_true"); ap.add_argument("--json")
    a = ap.parse_args()
    info = probe(a.video)
    v = next((s for s in info["streams"] if s["codec_type"] == "video"), None)
    au = next((s for s in info["streams"] if s["codec_type"] == "audio"), None)
    dur = float(info["format"]["duration"]); size = int(info["format"]["size"]) / 1e6
    fps = eval(v["avg_frame_rate"]) if v else 0
    rep = {"sure": round(dur, 2), "boyut_mb": round(size, 1), "cozunurluk": f"{v['width']}x{v['height']}" if v else None, "fps": round(fps, 2), "uyarilar": []}
    W = rep["uyarilar"]
    if not v or (v["width"], v["height"]) != (1080, 1920): W.append(f"çözünürlük {rep['cozunurluk']}, Shorts için 1080x1920 olmalı")
    if dur > 60: W.append(f"süre {dur:.1f} sn: 60 sn üstü Shorts sayılmayabilir")
    if size > 80: W.append(f"dosya {size:.0f} MB: GitHub 100 MB üstünü kabul etmez; --sikistir ile küçült")
    if au:
        L = loudness(a.video)
        if L:
            rep["lufs"] = float(L["input_i"]); rep["tepe_dbtp"] = float(L["input_tp"])
            if rep["lufs"] < -16: W.append(f"ses kısık ({rep['lufs']} LUFS); hedef -14. --duzelt ile çek")
            if rep["lufs"] > -12 or rep["tepe_dbtp"] > -0.5: W.append(f"ses çok yüksek/patlıyor ({rep['lufs']} LUFS, tepe {rep['tepe_dbtp']} dBTP). --duzelt ile çek")
        rep["ses_baslangic_sn"] = round(first_sound(a.video), 2)
        if rep["ses_baslangic_sn"] > 0.5: W.append(f"ses {rep['ses_baslangic_sn']} sn'de başlıyor; kancayı ilk yarım saniyeye çek")
    else:
        W.append("ses yok")
    c = cuts(a.video)
    if c is not None:
        rep["kesme_sayisi"] = len(c); rep["kesmeler"] = [round(t, 2) for t in c]
        rep["ort_sahne_sn"] = round(dur / (len(c) + 1), 2)
        if not any(t < 3 for t in c): W.append("ilk 3 sn'de kesme yok (karede hareket varsa sorun değil, yoksa kanca zayıf)")
        if rep["ort_sahne_sn"] > 5: W.append(f"sahneler ortalama {rep['ort_sahne_sn']} sn; 1,5-4 sn arası tutunmayı artırır")
    if a.duzelt and au and rep.get("lufs") is not None:
        rep["duzeltilmis"] = fix(a.video, L)
    if a.sikistir:
        src = rep.get("duzeltilmis", a.video); rep["sikistirilmis"] = compress(src)
        rep["sikistirilmis_mb"] = round(os.path.getsize(rep["sikistirilmis"]) / 1e6, 1)
    for k, val in rep.items():
        if k not in ("uyarilar", "kesmeler"): print(f"{k:18s} {val}")
    print("uyarılar:" if W else "uyarı yok ✓"); [print("  -", w) for w in W]
    if a.json: json.dump(rep, open(a.json, "w"), ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
