"""Skor tahmin botu: iddaa bültenindeki bugünün maçlarını Maçkolik geçmişiyle tahmin edip Telegram'a gönderir.

Kullanım:
  python run.py                    # bugünün bülteni (İstanbul saati), Telegram'a gönderir
  python run.py --dry-run          # göndermeden ekrana yazar, out/ klasörüne HTML bırakır
  python run.py --dry-run --date 2026-11-24   # belirli bir günün bülteni
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

from skorbotu import bulletin, engine, footballdata, iddaa, linker, mackolik, telegram, tff

ROOT = Path(__file__).parent


def past_seasons(today, since, archive, comps, names, warnings) -> list[list]:
    """Eski sezonlar: football-data.co.uk (Avrupa + ek ligler) ve TFF (Türkiye ligleri).
    Takımlar son haftalardaki ortak maçlarla Maçkolik kimliklerine bağlanır."""
    sources: dict[str, list[dict]] = {}
    try:
        for code, ms in footballdata.load(today, since).items():
            sources[f"fd-{code}"] = [{**m, "h": m["hn"], "a": m["an"]} for m in ms]
    except Exception as e:
        logging.exception("football-data başarısız")
        warnings.append(f"Avrupa liglerinin eski sezonları alınamadı ({type(e).__name__}).")
    for key, name, page in tff.LEAGUES:
        try:
            for gkey, g in tff.update_league(key, page, ROOT / "data" / "tff", today).items():
                sources[gkey] = [m for m in g["matches"] if m["hg"] is not None]
        except Exception as e:
            logging.exception("TFF %s başarısız", name)
            warnings.append(f"TFF {name} verisi alınamadı ({type(e).__name__}).")
    keys = linker.archive_keys(archive)
    out, linked = [], 0
    for src, ms in sources.items():
        mapping, comp = linker.link(src, ms, archive, names)
        linked += len(mapping)
        if comp is None:
            comps.setdefault(f"src:{src}", [src, "", "Domestic league"])
        out += linker.to_rows(src, ms, mapping, comp, keys)
    logging.info("Eski sezonlar: %d kaynak lig, %d maç, %d takım Maçkolik ile eşleşti", len(sources), len(out), linked)
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--date", help="YYYY-AA-GG: bu günün bülteni (varsayılan bugün)")
    ap.add_argument("--no-sidelined", action="store_true", help="eksik oyuncu sayfalarını çekme")
    ap.add_argument("--no-history", action="store_true", help="eski sezon kaynaklarını (football-data, TFF) kullanma")
    args = ap.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    today = datetime.now(mackolik.TZ).date()
    day = date.fromisoformat(args.date) if args.date else today
    warnings: list[str] = []

    store = mackolik.Store(ROOT / "data" / "mackolik")
    # Önce bugünün eşleşmesi (en önemli adım), sonra kısa arşiv güncellemesi
    events = [ev for ev in iddaa.program() if mackolik.local_day(ev["ts"]) == day]
    mk, comps_today = {}, {}
    try:
        for d in (day, day + timedelta(days=1)):
            ms, cs = mackolik.parse_day(mackolik.fetch_day(d))
            comps_today.update(cs)
            mk.update({m["iddaa"]: m for m in ms if m["iddaa"]})
    except mackolik.Blocked as e:
        logging.error("Bugünün Maçkolik listesi alınamadı: %s", e)
        warnings.append("Maçkolik'e bugün ulaşılamadı; yalnızca iddaa oranları gösteriliyor.")
    linked = sum(1 for ev in events if ev["id"] in mk)
    logging.info("Bugün bültende %d maç, %d tanesi Maçkolik ile eşleşti", len(events), linked)

    store.update(today)
    since = today - timedelta(days=730)
    rows, comps, names = store.load(since)
    comps.update(comps_today)
    logging.info("Maçkolik arşivinde %d bitmiş maç", len(rows))
    if not args.no_history:
        rows += past_seasons(today, since, rows, comps, names, warnings)
        rows.sort(key=lambda r: r[0])
    logging.info("Modelde toplam %d geçmiş maç", len(rows))

    hist = engine.History(rows, comps, day)
    recs = engine.analyse(events, mk, hist, with_sidelined=not args.no_sidelined)
    if not args.no_sidelined and mackolik._sidelined_fails >= 3:
        warnings.append("Eksik oyuncu bilgisi bugün bir kısım maç için alınamadı.")

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
