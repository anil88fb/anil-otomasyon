"""TFF (tff.org) sitesinden Türkiye liglerinin maç sonuçlarını ve fikstürünü çeker.

Her lig sayfası (&hafta=N) o haftanın maçlarını tarih, kulüp kimliği ve skorla verir.
Gruplu liglerde (2. Lig, 3. Lig) gruplar sayfadaki grupID bağlantılarından bulunur.
Oynanmış haftalar data/tff/ altında saklanır; her gün yalnızca açık haftalar yeniden çekilir.
"""
from __future__ import annotations

import json
import logging
import re
import time
from datetime import date, datetime, timedelta
from pathlib import Path

import requests
from bs4 import BeautifulSoup

BASE = "https://www.tff.org/Default.aspx"
LEAGUES = [
    # (anahtar, görünen ad, TFF pageID)
    ("tr-super", "Süper Lig", 198),
    ("tr-1", "1. Lig", 142),
    ("tr-2", "2. Lig", 976),
    ("tr-3", "3. Lig", 971),
]
MAX_WEEKS = 46
log = logging.getLogger(__name__)

_session = requests.Session()
_session.headers["User-Agent"] = "Mozilla/5.0 (skor-botu; günlük tahmin bülteni)"


def _get(params: dict) -> str:
    last = None
    for attempt in range(4):
        try:
            r = _session.get(BASE, params=params, timeout=30)
            r.raise_for_status()
            r.encoding = "windows-1254"
            time.sleep(0.6)
            return r.text
        except requests.RequestException as e:  # geçici hata: bekle ve tekrar dene
            last = e
            time.sleep(3 * (attempt + 1))
    raise RuntimeError(f"TFF sayfası alınamadı {params}: {last}")


_CLUB = re.compile(r"kulupI[dD]=(\d+)", re.I)
_MAC = re.compile(r"macId=(\d+)", re.I)
_SCORE = re.compile(r"(\d+)\s*-\s*(\d+)")


def parse_week(html: str) -> list[dict]:
    """Bir hafta sayfasındaki maçları döndürür (oynanmamışlarda hg/ag None)."""
    soup = BeautifulSoup(html, "html.parser")
    out, seen = [], set()
    for span in soup.find_all("span", id=re.compile(r"lblTarih$")):
        tr = span.find_parent("tr")
        if tr is None:
            continue
        clubs = [a for a in tr.find_all("a", href=True) if _CLUB.search(a["href"])]
        if len(clubs) < 2:
            continue
        mac = next((_MAC.search(a["href"]).group(1) for a in tr.find_all("a", href=True) if _MAC.search(a["href"])), None)
        if mac in seen:
            continue
        seen.add(mac)
        hg = ag = None
        for a in tr.find_all("a", href=True):
            if _MAC.search(a["href"]):
                m = _SCORE.search(a.get_text(" ", strip=True))
                if m:
                    hg, ag = int(m.group(1)), int(m.group(2))
                    break
        saat = tr.find("span", id=re.compile(r"(lbl|lb)Saat$"))
        try:
            d = datetime.strptime(span.get_text(strip=True), "%d.%m.%Y").date()
        except ValueError:
            continue
        out.append({
            "id": mac,
            "date": d.isoformat(),
            "time": saat.get_text(strip=True) if saat else "",
            "h": _CLUB.search(clubs[0]["href"]).group(1),
            "a": _CLUB.search(clubs[1]["href"]).group(1),
            "hn": clubs[0].get_text(" ", strip=True),
            "an": clubs[1].get_text(" ", strip=True),
            "hg": hg,
            "ag": ag,
        })
    return out


def parse_groups(html: str, page_id: int) -> list[tuple[str, str]]:
    """Sayfadaki grup bağlantıları: [(grupID, grup adı)]. Grupsuz ligde boş liste."""
    soup = BeautifulSoup(html, "html.parser")
    groups = {}
    for a in soup.find_all("a", href=re.compile(r"grupID=\d+", re.I)):
        if f"pageID={page_id}" not in a["href"]:
            continue
        gid = re.search(r"grupID=(\d+)", a["href"], re.I).group(1)
        name = a.get_text(" ", strip=True)
        if name and len(name) < 30:
            groups.setdefault(gid, name)
    return list(groups.items())


def parse_season(html: str) -> str:
    m = re.search(r"(20\d\d-20\d\d) Sezonu", html)
    return m.group(1) if m else ""


def _week_open(week: list[dict], today: date) -> bool:
    """Yeniden çekilmesi gereken hafta: oynanmamış maç var ya da son 4 gün içinde."""
    recent = (today - timedelta(days=4)).isoformat()
    return any(m["hg"] is None or m["date"] >= recent for m in week)


def update_league(key: str, page_id: int, cache_dir: Path, today: date) -> dict[str, dict]:
    """Ligin (ve gruplarının) güncel verisini döndürür: {grup_anahtarı: {'name','season','matches'}}."""
    cache_dir.mkdir(parents=True, exist_ok=True)
    base_html = _get({"pageID": page_id})
    season = parse_season(base_html)
    groups = parse_groups(base_html, page_id) or [("", "")]
    result = {}
    for gid, gname in groups:
        gkey = f"{key}-{gid}" if gid else key
        path = cache_dir / f"{gkey}.json"
        cache = json.loads(path.read_text("utf-8")) if path.exists() else {}
        if cache.get("season") != season:
            cache = {"season": season, "weeks": {}, "total": None}
        weeks = cache["weeks"]
        n = 1
        while n <= MAX_WEEKS:
            if cache.get("total") and n > cache["total"]:
                break
            w = weeks.get(str(n))
            if w is not None and not _week_open(w, today):
                n += 1
                continue
            params = {"pageID": page_id, "hafta": n}
            if gid:
                params["grupID"] = gid
            ms = parse_week(_get(params))
            if not ms:
                if n > 1:
                    cache["total"] = n - 1
                break
            weeks[str(n)] = ms
            n += 1
        path.write_text(json.dumps(cache, ensure_ascii=False, indent=0), "utf-8")
        all_ms = [m for k in sorted(weeks, key=int) for m in weeks[k]]
        result[gkey] = {"group": gname, "season": season, "matches": all_ms}
        log.info("%s: %d maç (%d oynanmış)", gkey, len(all_ms), sum(m["hg"] is not None for m in all_ms))
    return result
