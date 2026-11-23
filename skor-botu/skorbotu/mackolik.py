"""Maçkolik: dünyadaki tüm futbol maçlarının sonuçları, fikstürü ve sakat/cezalı oyuncular.

Günlük sonuç listesi Maçkolik'in kendi canlı sonuç servisinden (JSON) alınır. Her maçta
iddaa kodu da bulunur; böylece iddaa bülteniyle birebir eşleşir.
Bitmiş günler data/mackolik/GGGG-AA-GG.json.gz dosyalarında saklanır, bir kez indirilir.
"""
from __future__ import annotations

import gzip
import json
import logging
import re
import sys
import time
from datetime import date, datetime, timedelta, timezone  # noqa: F401 (testlerde kullanılır)
from pathlib import Path
from zoneinfo import ZoneInfo

import requests
from bs4 import BeautifulSoup

LIVESCORES = "https://www.mackolik.com/perform/p0/ajax/components/competition/livescores/json"
MATCH_URL = "https://www.mackolik.com/mac/{slug}/{id}"
TZ = ZoneInfo("Europe/Istanbul")
FINISHED = {"fullTime"}  # uzatma/penaltı sonuçları normal süre skoru değildir, modele katılmaz
log = logging.getLogger(__name__)

_s = requests.Session()
_s.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36",
    "Accept-Language": "tr-TR,tr;q=0.9",
})


def _get(url: str, params=None, delay: float = 0.3) -> requests.Response:
    last = None
    for attempt in range(4):
        try:
            r = _s.get(url, params=params, timeout=40)
            if r.status_code == 200:
                time.sleep(delay)
                return r
            last = f"HTTP {r.status_code}"
        except requests.RequestException as e:
            last = e
        time.sleep(3 * (attempt + 1))
    raise RuntimeError(f"Maçkolik alınamadı {url}: {last}")


def fetch_day(d: date) -> dict:
    r = _get(LIVESCORES, {"sports[]": "Soccer", "matchDate": d.isoformat()})
    return r.json()["data"]


def local_day(ts_ms: int) -> date:
    return datetime.fromtimestamp(ts_ms / 1000, tz=timezone.utc).astimezone(TZ).date()


def _int(v):
    try:
        return int(v)
    except (TypeError, ValueError):
        return None


def parse_day(data: dict) -> tuple[list[dict], dict]:
    """Ham günlük veriyi maç listesine çevirir. comps: {id: [ad, ülke, biçim]}."""
    comps = {
        cid: [c.get("name", ""), (c.get("country") or {}).get("name", ""), c.get("competitionFormat", "")]
        for cid, c in (data.get("competitions") or {}).items()
    }
    out = []
    for m in (data.get("matches") or {}).values():
        sc = m.get("score") or {}
        ht = sc.get("ht") or {}
        out.append({
            "id": m["id"],
            "ts": m.get("mstUtc") or 0,
            "comp": m.get("competitionId", ""),
            "home": m["homeTeam"]["id"], "away": m["awayTeam"]["id"],
            "hn": m["homeTeam"]["name"], "an": m["awayTeam"]["name"],
            "hg": _int(sc.get("home")), "ag": _int(sc.get("away")),
            "hth": _int(ht.get("home")), "hta": _int(ht.get("away")),
            "state": m.get("state", ""), "sub": m.get("substate", ""),
            "iddaa": m.get("iddaaCode"),
            "slug": m.get("matchSlug", ""),
        })
    return out, comps


def finished_rows(matches: list[dict]) -> list[list]:
    """Modele girecek bitmiş maçlar: [ts, lig, ev, dep, evGol, depGol, iyEv, iyDep]."""
    return [
        [m["ts"], m["comp"], m["home"], m["away"], m["hg"], m["ag"], m["hth"], m["hta"]]
        for m in matches
        if m["state"] == "post" and m["sub"] in FINISHED and m["hg"] is not None and m["ag"] is not None
    ]


class Store:
    """Günlük sonuç arşivi (data/mackolik)."""

    def __init__(self, root: Path):
        self.root = root
        root.mkdir(parents=True, exist_ok=True)

    def path(self, d: date) -> Path:
        return self.root / f"{d.isoformat()}.json.gz"

    def has(self, d: date) -> bool:
        return self.path(d).exists()

    def save(self, d: date, data: dict) -> None:
        matches, comps = parse_day(data)
        rows = finished_rows(matches)
        used = {r[1] for r in rows}
        payload = {"comps": {k: v for k, v in comps.items() if k in used}, "rows": rows}
        with gzip.open(self.path(d), "wt", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, separators=(",", ":"))

    def update(self, today: date, start: date, budget: int) -> int:
        """Son 3 günü yeniler, sonra eksik geçmiş günleri yeniden eskiye `budget` kadar indirir."""
        n = 0
        for k in range(1, 4):
            d = today - timedelta(days=k)
            if d >= start:
                self.save(d, fetch_day(d)); n += 1
        d = today - timedelta(days=4)
        while d >= start and n < budget:
            if not self.has(d):
                try:
                    self.save(d, fetch_day(d)); n += 1
                except Exception as e:  # tek gün bozuksa atla, sonraki çalıştırmada tekrar denenir
                    log.warning("%s indirilemedi: %s", d, e)
            d -= timedelta(days=1)
        missing = sum(1 for i in range((today - start).days) if not self.has(start + timedelta(days=i)))
        log.info("Maçkolik: %d gün indirildi, arşivde eksik %d gün", n, missing)
        return missing

    def load(self, since: date) -> tuple[list[list], dict]:
        rows, comps = [], {}
        for p in sorted(self.root.glob("*.json.gz")):
            try:
                if date.fromisoformat(p.name[:10]) < since:
                    continue
                with gzip.open(p, "rt", encoding="utf-8") as f:
                    payload = json.load(f)
            except (ValueError, OSError, EOFError) as e:
                log.warning("Bozuk arşiv dosyası %s: %s", p.name, e)
                continue
            comps.update(payload["comps"])
            for r in payload["rows"]:
                r[1], r[2], r[3] = sys.intern(r[1]), sys.intern(r[2]), sys.intern(r[3])
                rows.append(r)
        rows.sort(key=lambda r: r[0])
        return rows, comps


_TEAM_IN_CREST = re.compile(r"/teams/([a-z0-9]+)")


def parse_sidelined(html: str) -> list[dict]:
    """Maç sayfasındaki 'Sakat ve Cezalılar' kutuları. Her kutu: {'team': id|None, 'players': [...]}."""
    soup = BeautifulSoup(html, "html.parser")
    out = []
    for w in soup.select(".widget-sidelined-players"):
        crest = w.select_one(".widget-sidelined-players__header-crest")
        m = _TEAM_IN_CREST.search(crest.get("src", "")) if crest else None
        players = []
        for li in w.select(".widget-sidelined-players__item"):
            name = li.select_one(".widget-sidelined-players__name")
            pos = li.select_one(".widget-sidelined-players__position")
            nums = [n.get_text(strip=True) for n in li.select(".widget-sidelined-players__number")]
            reason = li.select_one(".widget-sidelined-players__value")
            icon = li.select_one(".widget-sidelined-players__reason img")
            players.append({
                "name": name.get_text(" ", strip=True) if name else "?",
                "pos": (pos.get("title") or pos.get_text(strip=True)) if pos else "",
                "apps": _int(nums[0]) if nums else None,
                "goals": _int(nums[1]) if len(nums) > 1 else None,
                "reason": reason.get_text(" ", strip=True) if reason else "",
                "icon": (icon.get("src", "").rsplit("/", 1)[-1] if icon else ""),
            })
        out.append({"team": m.group(1) if m else None, "players": players})
    return out


def sidelined(match: dict) -> dict[str, list[dict]]:
    """{'home': [...], 'away': [...]} — eşleşmezse sırayla (ilk kutu ev sahibi)."""
    try:
        html = _get(MATCH_URL.format(slug=match["slug"], id=match["id"]), delay=0.4).text
    except RuntimeError as e:
        log.warning("Eksik oyuncu sayfası alınamadı: %s", e)
        return {"home": [], "away": []}
    boxes = parse_sidelined(html)
    res = {"home": [], "away": []}
    for i, b in enumerate(boxes[:2]):
        side = "home" if b["team"] == match["home"] else "away" if b["team"] == match["away"] else ("home" if i == 0 else "away")
        res[side] = b["players"]
    return res
