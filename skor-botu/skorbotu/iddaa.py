"""iddaa.com futbol bülteni: maçlar ve oranlar (maç sonucu, 2.5 alt/üst, karşılıklı gol)."""
from __future__ import annotations

import logging
import time

import requests

EVENTS = "https://sportsbookv2.iddaa.com/sportsbook/events"
COMPETITIONS = "https://sportsbookv2.iddaa.com/sportsbook/competitions"
log = logging.getLogger(__name__)
_H = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36",
    "Accept-Language": "tr-TR,tr;q=0.9",
    "Origin": "https://www.iddaa.com",
    "Referer": "https://www.iddaa.com/",
}


def _json(url: str, params=None) -> dict:
    last = None
    for attempt in range(4):
        try:
            r = requests.get(url, params=params, headers=_H, timeout=40)
            if r.status_code == 200:
                j = r.json()
                if j.get("isSuccess"):
                    return j["data"]
                last = j.get("message")
            else:
                last = f"HTTP {r.status_code}"
        except (requests.RequestException, ValueError) as e:
            last = e
        time.sleep(3 * (attempt + 1))
    raise RuntimeError(f"iddaa alınamadı: {last}")


def _odds(m: dict) -> list[float]:
    return [o.get("odd") for o in sorted(m.get("o", []), key=lambda o: o.get("no", 0))]


def parse_events(data: dict, comps: dict[int, str]) -> list[dict]:
    out = []
    for e in data.get("events", []):
        if e.get("sid") != 1:
            continue
        ms = ou25 = kg = None
        for m in e.get("m", []):
            t, st = m.get("t"), m.get("st")
            if t == 1 and st == 1:
                ms = _odds(m)
            elif st == 101 and str(m.get("sov")) == "2.5":
                ou25 = _odds(m)  # [alt, üst]
            elif st == 89:
                kg = _odds(m)  # [var, yok]
        out.append({
            "id": e["i"], "ts": e.get("d", 0) * 1000, "comp": comps.get(e.get("ci"), ""),
            "hn": e.get("hn", ""), "an": e.get("an", ""), "mbs": e.get("mbc"),
            "ms": ms, "ou25": ou25, "kg": kg,
        })
    return out


def program() -> list[dict]:
    """Bültendeki (canlı olmayan) tüm futbol maçları."""
    comps = {c["i"]: c["n"] for c in _json(COMPETITIONS)}
    events = parse_events(_json(EVENTS, {"st": 1, "type": 0, "version": 0}), comps)
    log.info("iddaa bülteni: %d futbol maçı", len(events))
    return events
