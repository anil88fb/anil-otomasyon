"""Avrupa ligleri: football-data.co.uk ücretsiz CSV dosyaları (haftada iki kez güncellenir)."""
from __future__ import annotations

import csv
import io
import logging
from datetime import date, datetime

import requests

# Sezonluk dosyalar (mmz4281/<sezon>/<kod>.csv)
LEAGUES = ["E0", "E1", "E2", "E3", "EC", "SC0", "SC1", "SC2", "SC3", "D1", "D2", "I1", "I2",
           "SP1", "SP2", "F1", "F2", "N1", "B1", "P1", "T1", "G1"]
# Tüm sezonları tek dosyada olan ek ligler (new/<kod>.csv)
EXTRA = ["ARG", "AUT", "BRA", "CHN", "DNK", "FIN", "IRL", "JPN", "MEX", "NOR", "POL", "ROU",
         "SWE", "SWZ", "USA"]
URL = "https://www.football-data.co.uk/mmz4281/{season}/{code}.csv"
EXTRA_URL = "https://www.football-data.co.uk/new/{code}.csv"
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
        h = (row.get("HomeTeam") or row.get("Home") or "").strip()
        a = (row.get("AwayTeam") or row.get("Away") or "").strip()
        if not d or not h or not a:
            continue
        hg, ag = row.get("FTHG") or row.get("HG") or "", row.get("FTAG") or row.get("AG") or ""
        hth, hta = row.get("HTHG", ""), row.get("HTAG", "")
        played = hg.strip().isdigit() and ag.strip().isdigit()
        out.append({
            "div": (row.get("Div") or "").strip(),
            "date": d.isoformat(),
            "time": (row.get("Time") or "").strip(),
            "h": h, "a": a, "hn": h, "an": a,
            "hg": int(hg) if played else None,
            "ag": int(ag) if played else None,
            "hth": int(hth) if hth.strip().isdigit() else None,
            "hta": int(hta) if hta.strip().isdigit() else None,
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


def load(today: date, since: date) -> dict[str, list[dict]]:
    """{kod: [oynanmış maçlar]}: `since` tarihinden bu yana."""
    out = {}
    jobs = [(c, [URL.format(season=s, code=c) for s in season_codes(today, 3)]) for c in LEAGUES]
    jobs += [(c, [EXTRA_URL.format(code=c)]) for c in EXTRA]
    for code, urls in jobs:
        ms = []
        for u in urls:
            t = _fetch(u)
            if t:
                ms += [m for m in parse_csv(t) if m["hg"] is not None and m["date"] >= since.isoformat()]
        if ms:
            out[code] = sorted(ms, key=lambda m: m["date"])
    log.info("football-data: %d lig, %d maç", len(out), sum(len(v) for v in out.values()))
    return out
