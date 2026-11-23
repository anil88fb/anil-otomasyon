"""Skor tahmin botu: iddaa bültenindeki bugünün maçlarını Maçkolik geçmişiyle tahmin edip Telegram'a gönderir.

Kullanım:
  python run.py                    # bugünün bülteni (İstanbul saati), Telegram'a gönderir
  python run.py --dry-run          # göndermeden ekrana yazar, out/ klasörüne HTML bırakır
  python run.py --backfill 300     # bu çalıştırmada en çok kaç geçmiş gün indirilsin
Ortam değişkenleri: TELEGRAM_TOKEN, TELEGRAM_CHAT_ID (virgülle birden çok sohbet/kanal)
"""
from __future__ import annotations

import argparse
import json
import logging
import os
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

from skorbotu import bulletin, engine, iddaa, mackolik, telegram

ROOT = Path(__file__).parent
HISTORY_START = date(2024, 7, 1)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--backfill", type=int, default=250, help="bir çalıştırmada indirilecek en çok geçmiş gün")
    ap.add_argument("--no-sidelined", action="store_true", help="eksik oyuncu sayfalarını çekme")
    args = ap.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    day = datetime.now(mackolik.TZ).date()
    warnings: list[str] = []

    store = mackolik.Store(ROOT / "data" / "mackolik")
    missing = store.update(day, HISTORY_START, args.backfill)
    if missing > 30:
        warnings.append(f"Geçmiş maç arşivi henüz tamamlanmadı ({missing} gün eksik); sonraki çalıştırmalarda tamamlanacak.")
    rows, comps = store.load(day - timedelta(days=730))
    logging.info("Arşivde %d bitmiş maç", len(rows))

    events = [ev for ev in iddaa.program() if mackolik.local_day(ev["ts"]) == day]
    mk = {}
    for d in (day, day + timedelta(days=1)):
        ms, cs = mackolik.parse_day(mackolik.fetch_day(d))
        comps.update(cs)
        mk.update({m["iddaa"]: m for m in ms if m["iddaa"]})
    linked = sum(1 for ev in events if ev["id"] in mk)
    logging.info("Bugün bültende %d maç, %d tanesi Maçkolik ile eşleşti", len(events), linked)

    hist = engine.History(rows, comps, day)
    recs = engine.analyse(events, mk, hist, with_sidelined=not args.no_sidelined)

    out = ROOT / "data" / "tahminler"
    out.mkdir(parents=True, exist_ok=True)
    keep = ("id", "ts", "comp", "hn", "an", "ms", "ou25", "kg", "model", "market", "notes")
    (out / f"{day.isoformat()}.json").write_text(
        json.dumps([{k: r.get(k) for k in keep} for r in recs], ensure_ascii=False, separators=(",", ":")), "utf-8")

    text = bulletin.message(recs, day, warnings)
    parts = bulletin.split(text)
    doc_name = f"tahmin-bulteni-{day.isoformat()}.html"
    doc = bulletin.report(recs, day).encode("utf-8")
    (ROOT / "out").mkdir(exist_ok=True)
    (ROOT / "out" / doc_name).write_bytes(doc)

    token, chats = os.environ.get("TELEGRAM_TOKEN"), os.environ.get("TELEGRAM_CHAT_ID", "")
    if args.dry_run or not token or not chats:
        if not args.dry_run:
            logging.warning("TELEGRAM_TOKEN / TELEGRAM_CHAT_ID yok; bülten yalnızca yazdırılıyor.")
        print("\n\n=====\n\n".join(parts))
        return 0
    telegram.send(token, [c.strip() for c in chats.split(",") if c.strip()], parts, (doc_name, doc))
    logging.info("%d mesaj ve bülten dosyası gönderildi", len(parts))
    return 0


if __name__ == "__main__":
    sys.exit(main())
