"""Skor tahmin botu: verileri günceller, bugünün maçlarını tahmin eder, Telegram'a gönderir.

Kullanım:
  python run.py                 # bugünün bülteni (İstanbul saati), Telegram'a gönderir
  python run.py --dry-run       # göndermeden ekrana yazar
  python run.py --date 2026-11-28
Ortam değişkenleri: TELEGRAM_TOKEN, TELEGRAM_CHAT_ID (virgülle birden çok sohbet/kanal)
"""
from __future__ import annotations

import argparse
import logging
import os
import sys
from datetime import date, datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from skorbotu import bulletin, footballdata, telegram, tff

ROOT = Path(__file__).parent
FLAGS = {"E0": "🏴", "E1": "🏴", "SP1": "🇪🇸", "D1": "🇩🇪", "I1": "🇮🇹", "F1": "🇫🇷",
         "N1": "🇳🇱", "P1": "🇵🇹", "B1": "🇧🇪", "SC0": "🏴", "G1": "🇬🇷"}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--date", help="YYYY-AA-GG (varsayılan: bugün, İstanbul)")
    ap.add_argument("--dry-run", action="store_true", help="Telegram'a göndermeden yazdır")
    ap.add_argument("--no-tff", action="store_true")
    ap.add_argument("--no-eu", action="store_true")
    args = ap.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")

    day = date.fromisoformat(args.date) if args.date else datetime.now(ZoneInfo("Europe/Istanbul")).date()
    leagues, warnings = [], []

    if not args.no_tff:
        for key, name, page in tff.LEAGUES:
            try:
                groups = tff.update_league(key, page, ROOT / "data" / "tff", day)
                for g in groups.values():
                    label = f"{name} {g['group']} Grubu" if g["group"] else name
                    leagues.append({"name": label, "flag": "🇹🇷", "matches": g["matches"]})
            except Exception as e:  # bir lig bozulursa diğerleri yine gönderilir
                logging.exception("TFF %s başarısız", name)
                warnings.append(f"{name} verisi alınamadı ({type(e).__name__}).")

    if not args.no_eu:
        try:
            eu = footballdata.load(day)
            for code, name in footballdata.LEAGUES:
                if code in eu:
                    leagues.append({"name": name, "flag": FLAGS.get(code, "⚽"), "matches": eu[code]["matches"]})
            if not eu:
                warnings.append("Avrupa ligleri verisi alınamadı.")
        except Exception as e:
            logging.exception("football-data başarısız")
            warnings.append(f"Avrupa ligleri verisi alınamadı ({type(e).__name__}).")

    if not leagues:
        logging.error("Hiçbir lig verisi alınamadı")
        return 1

    text = bulletin.build(leagues, day, warnings)
    parts = bulletin.split(text)
    token, chats = os.environ.get("TELEGRAM_TOKEN"), os.environ.get("TELEGRAM_CHAT_ID", "")
    if args.dry_run or not token or not chats:
        if not args.dry_run:
            logging.warning("TELEGRAM_TOKEN / TELEGRAM_CHAT_ID yok; bülten yalnızca yazdırılıyor.")
        print("\n\n=====\n\n".join(parts))
        return 0
    telegram.send(token, [c.strip() for c in chats.split(",") if c.strip()], parts)
    logging.info("%d mesaj gönderildi", len(parts))
    return 0


if __name__ == "__main__":
    sys.exit(main())
