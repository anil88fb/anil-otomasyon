#!/usr/bin/env python3
"""Görsellerin arka planını kaldırır (rembg); karakter, ürün ya da kullanıcı fotoğrafını sahneye koymak için.

Kullanım:
  python3 dekupe.py <görsel veya klasör> [--cikti klasör] [--model isnet-general-use|u2net|u2net_human_seg] [--kenar 0]

Çıktı: aynı adla şeffaf PNG (ör. araba.png -> araba_dekupe.png).
  --kenar N : nesnenin etrafına N piksellik beyaz kontur ekler (çıkartma/sticker görünümü, Shorts'ta iyi okunur)
Modeller ilk kullanımda GitHub'dan iner (bulut proxy'sinde açık).
"""
import argparse, glob, os
from PIL import Image, ImageFilter


def sticker(img, px):
    a = img.split()[-1].filter(ImageFilter.MaxFilter(px * 2 + 1))
    white = Image.new("RGBA", img.size, (255, 255, 255, 255)); white.putalpha(a)
    return Image.alpha_composite(white, img)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("girdi"); ap.add_argument("--cikti"); ap.add_argument("--model", default="isnet-general-use"); ap.add_argument("--kenar", type=int, default=0)
    a = ap.parse_args()
    from rembg import new_session, remove
    sess = new_session(a.model)
    files = sorted(glob.glob(os.path.join(a.girdi, "*"))) if os.path.isdir(a.girdi) else [a.girdi]
    files = [f for f in files if f.lower().endswith((".png", ".jpg", ".jpeg", ".webp"))]
    for f in files:
        img = remove(Image.open(f).convert("RGBA"), session=sess)
        bb = img.getbbox()
        if bb: img = img.crop(bb)
        if a.kenar:
            pad = a.kenar * 2; c = Image.new("RGBA", (img.width + pad * 2, img.height + pad * 2), (0, 0, 0, 0)); c.paste(img, (pad, pad)); img = sticker(c, a.kenar)
        out = os.path.join(a.cikti or os.path.dirname(os.path.abspath(f)), os.path.splitext(os.path.basename(f))[0] + "_dekupe.png")
        os.makedirs(os.path.dirname(out), exist_ok=True); img.save(out); print(out, img.size)


if __name__ == "__main__":
    main()
