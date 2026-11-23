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


class Blocked(RuntimeError):
    """Maçkolik istekleri reddediyor (çok sık istek)."""


def _get(url: str, params=None, delay: float = 1.0, tries: int = 3) -> requests.Response:
    last = None
    for attempt in range(tries):
        try:
            r = _s.get(url, params=params, timeout=40)
            if r.status_code == 200:
                time.sleep(delay)
                return r
            last = f"HTTP {r.status_code}"
        except requests.RequestException as e:
            last = e
        time.sleep(15 * (attempt + 1))
    raise Blocked(f"Maçkolik alınamadı ({last})")


def fetch_day(d: date, delay: float = 1.0) -> dict:
    r = _get(LIVESCORES, {"sports[]": "Soccer", "matchDate": d.isoformat()}, delay=delay)
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

    def missing(self, today: date, start: date) -> list[date]:
        return [d for d in (today - timedelta(days=i) for i in range(1, (today - start).days + 1)) if not self.has(d)]

    def update(self, today: date, start: date, minutes: float, delay: float = 5.0, refresh: bool = True) -> int:
        """Son 3 günü yeniler, sonra eksik geçmiş günleri yeniden eskiye doğru indirir.

        Maçkolik sık isteği engellediği için istekler aralıklı yapılır, süre sınırı aşılınca ya da
        art arda 3 hata alınınca durulur; kalan günler sonraki çalıştırmalarda tamamlanır.
        """
        t_end = time.monotonic() + minutes * 60
        n = fails = 0
        todo = self.missing(today, start)
        if refresh:
            todo = [today - timedelta(days=k) for k in range(1, 4)] + [d for d in todo if (today - d).days > 3]
        for d in todo:
            if time.monotonic() > t_end or fails >= 3:
                break
            try:
                self.save(d, fetch_day(d, delay=delay)); n += 1; fails = 0
            except Exception as e:  # sonraki çalıştırmada tekrar denenir
                fails += 1
                log.warning("%s indirilemedi: %s", d, e)
        left = len(self.missing(today, start))
        log.info("Maçkolik: %d gün indirildi, arşivde eksik %d gün", n, left)
        return left

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


_sidelined_fails = 0


def sidelined(match: dict) -> dict[str, list[dict]] | None:
    """{'home': [...], 'away': [...]} — eşleşmezse sırayla (ilk kutu ev sahibi).
    Sayfa alınamazsa None; art arda 3 hatadan sonra o gün başka sayfa denenmez."""
    global _sidelined_fails
    if _sidelined_fails >= 3:
        return None
    try:
        html = _get(MATCH_URL.format(slug=match["slug"], id=match["id"]), delay=1.5, tries=2).text
        _sidelined_fails = 0
    except Blocked as e:
        _sidelined_fails += 1
        log.warning("Eksik oyuncu sayfası alınamadı: %s", e)
        return None
    boxes = parse_sidelined(html)
    res = {"home": [], "away": []}
    for i, b in enumerate(boxes[:2]):
        side = "home" if b["team"] == match["home"] else "away" if b["team"] == match["away"] else ("home" if i == 0 else "away")
        res[side] = b["players"]
    return res
