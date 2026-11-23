"""Avrupa ligleri: football-data.co.uk ücretsiz CSV dosyaları (haftada iki kez güncellenir)."""
from __future__ import annotations

import csv
import io
import logging
from datetime import date, datetime

import requests

LEAGUES = [
    # (CSV kodu, görünen ad)
    ("E0", "İngiltere Premier League"),
    ("E1", "İngiltere Championship"),
    ("SP1", "İspanya La Liga"),
    ("D1", "Almanya Bundesliga"),
    ("I1", "İtalya Serie A"),
    ("F1", "Fransa Ligue 1"),
    ("N1", "Hollanda Eredivisie"),
    ("P1", "Portekiz Liga"),
    ("B1", "Belçika Pro League"),
    ("SC0", "İskoçya Premiership"),
    ("G1", "Yunanistan Süper Lig"),
]
URL = "https://www.football-data.co.uk/mmz4281/{season}/{code}.csv"
FIXTURES = "https://www.football-data.co.uk/fixtures.csv"
log = logging.getLogger(__name__)


def season_codes(today: date, n: int = 2) -> list[str]:
    y = today.year if today.month >= 7 else today.year - 1
    return [f"{(y - i) % 100:02d}{(y - i + 1) % 100:02d}" for i in range(n)]


def _date(s: str) -> date | None:
    for fmt in ("%d/%m/%Y", "%d/%m/%y"):
        try:
            return datetime.strptime(s.strip(), fmt).date()
        except ValueError:
            pass
    return None


def parse_csv(text: str) -> list[dict]:
    """Sonuç ya da fikstür CSV'sini maç listesine çevirir (oynanmamışlarda hg/ag None)."""
    out = []
    for row in csv.DictReader(io.StringIO(text.lstrip("﻿"))):
        d = _date(row.get("Date", ""))
        h, a = (row.get("HomeTeam") or "").strip(), (row.get("AwayTeam") or "").strip()
        if not d or not h or not a:
            continue
        hg, ag = row.get("FTHG", ""), row.get("FTAG", "")
        played = hg.strip().isdigit() and ag.strip().isdigit()
        out.append({
            "div": (row.get("Div") or "").strip(),
            "date": d.isoformat(),
            "time": (row.get("Time") or "").strip(),
            "h": h, "a": a, "hn": h, "an": a,
            "hg": int(hg) if played else None,
            "ag": int(ag) if played else None,
        })
    return out


def _fetch(url: str) -> str | None:
    try:
        r = requests.get(url, timeout=30, headers={"User-Agent": "Mozilla/5.0 (skor-botu)"})
        if r.status_code != 200:
            return None
        return r.content.decode("utf-8-sig", errors="replace")
    except requests.RequestException as e:
        log.warning("İndirilemedi %s: %s", url, e)
        return None


def load(today: date) -> dict[str, dict]:
    """{kod: {'name', 'matches'}}: son iki sezonun sonuçları + yaklaşan maçlar."""
    fx_text = _fetch(FIXTURES)
    fixtures = parse_csv(fx_text) if fx_text else []
    out = {}
    for code, name in LEAGUES:
        ms = []
        for s in reversed(season_codes(today)):
            t = _fetch(URL.format(season=s, code=code))
            if t:
                ms += [m for m in parse_csv(t) if m["hg"] is not None]
        known = {(m["date"], m["h"], m["a"]) for m in ms}
        ms += [m for m in fixtures if m["div"] == code and (m["date"], m["h"], m["a"]) not in known]
        if ms:
            out[code] = {"name": name, "matches": sorted(ms, key=lambda m: (m["date"], m["time"]))}
            log.info("%s: %d maç", code, len(ms))
    return out
