"""Eski sezon verisini (football-data.co.uk, TFF) Maçkolik takımlarıyla eşleştirir.

Kaynaklarda takım adları farklı yazılır ("Man City" / "Man. City", "ALAGÖZ HOLDİNG IĞDIR FUTBOL KULÜBÜ" /
"Iğdır FK"). Eşleştirme, son haftalarda iki tarafta da bulunan ortak maçlarla yapılır: aynı gün, aynı
skor ve benzer adlar. Böylece bir kaynağın tüm geçmişi Maçkolik kimlikleriyle modele eklenir.
Eşleşmeyen takımlar (ör. küme düşenler) kaynak kimliğiyle kalır; geçmiş maçlarda rakip olarak yine işe yarar.
"""
from __future__ import annotations

import logging
import re
import unicodedata
from collections import Counter, defaultdict
from datetime import date, datetime, timedelta
from difflib import SequenceMatcher

from . import mackolik

log = logging.getLogger(__name__)
_STOP = {"fc", "sk", "fk", "as", "ac", "cf", "sc", "club", "kulubu", "futbol", "spor", "kulubu", "the", "de",
         "afc", "ss", "us", "cd", "ud", "sd", "rc", "ca", "if", "bk", "ik", "aik", "sv", "vfb", "vfl", "tsg",
         "belediye", "belediyesi", "belediyespor", "holding", "insaat", "bld"}


def norm(s: str) -> str:
    s = s.replace("İ", "i").replace("I", "ı").lower().replace("ı", "i")
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9 ]+", " ", s)


def tokens(s: str) -> set[str]:
    return {t for t in norm(s).split() if t not in _STOP and len(t) > 1}


def sim(a: str, b: str) -> float:
    """0-1 arası ad benzerliği."""
    ta, tb = tokens(a), tokens(b)
    if not ta or not tb:
        return 0.0
    jac = len(ta & tb) / len(ta | tb)
    contain = len(ta & tb) / min(len(ta), len(tb))
    prefix = max((1.0 for x in ta for y in tb if len(x) >= 4 and len(y) >= 4 and (x.startswith(y[:4]) or y.startswith(x[:4]))), default=0.0)
    seq = SequenceMatcher(None, " ".join(sorted(ta)), " ".join(sorted(tb))).ratio()
    return max(jac, 0.8 * contain, 0.6 * prefix, seq * 0.9)


def noon_ts(d: date) -> int:
    return int(datetime(d.year, d.month, d.day, 12, tzinfo=mackolik.TZ).timestamp() * 1000)


def link(source: str, matches: list[dict], archive: list[list], names: dict[str, str]) -> tuple[dict, str | None]:
    """Bir kaynak ligin takımlarını Maçkolik kimliklerine bağlar.

    matches: kaynak maçları {'date','h','a','hn','an','hg','ag'}; h/a kaynaktaki takım anahtarı.
    archive: Maçkolik satırları [ts, lig, ev, dep, evGol, depGol, ...].
    Dönüş: ({kaynak_takım: maçkolik_takım}, maçkolik_lig | None)
    """
    by_day: dict[date, list] = defaultdict(list)
    for r in archive:
        by_day[mackolik.local_day(r[0])].append(r)
    if not by_day:
        return {}, None
    days = set(by_day)
    votes: dict[tuple, float] = defaultdict(float)
    comp_votes: Counter = Counter()
    src_name = {}
    for m in matches:
        src_name[m["h"]], src_name[m["a"]] = m["hn"], m["an"]
        d = date.fromisoformat(m["date"])
        if d not in days and d - timedelta(days=1) not in days:
            continue
        cands = []
        for dd in (d, d - timedelta(days=1), d + timedelta(days=1)):
            for r in by_day.get(dd, []):
                if r[4] == m["hg"] and r[5] == m["ag"]:
                    s = sim(m["hn"], names.get(r[2], "")) + sim(m["an"], names.get(r[3], ""))
                    if s >= 0.7:
                        cands.append((s, r))
        if not cands:
            continue
        top = max(c[0] for c in cands)
        cands = [c for c in cands if c[0] >= top - 0.15]
        for s, r in cands:
            w = 1.0 / len(cands)
            votes[(m["h"], r[2])] += w
            votes[(m["a"], r[3])] += w
            comp_votes[r[1]] += w

    # açgözlü atama: en güçlü kanıttan başla, bir Maçkolik takımı tek kaynağa bağlanır
    scored = sorted(((v + sim(src_name.get(s, ""), names.get(t, "")), v, s, t) for (s, t), v in votes.items()), reverse=True)
    mapping, used = {}, set()
    for score, v, s, t in scored:
        if s in mapping or t in used:
            continue
        if v >= 1.5 or (v >= 0.9 and sim(src_name.get(s, ""), names.get(t, "")) >= 0.45):
            mapping[s] = t
            used.add(t)
    comp = comp_votes.most_common(1)[0][0] if comp_votes else None
    log.info("%s: %d/%d takım eşleşti (lig %s)", source, len(mapping), len(src_name), comp)
    return mapping, comp


def archive_keys(archive: list[list]) -> tuple[set, set]:
    """(gün, ev, dep) ve (gün, lig) kümeleri: kaynak maçı arşivde zaten var mı diye bakmak için."""
    games, comp_days = set(), set()
    for r in archive:
        d = mackolik.local_day(r[0])
        games.add((d, r[2], r[3]))
        comp_days.add((d, r[1]))
    return games, comp_days


def to_rows(source: str, matches: list[dict], mapping: dict, comp: str | None, keys: tuple[set, set]) -> list[list]:
    """Kaynak maçlarını Maçkolik satır biçimine çevirir; arşivde zaten olan maçlar atlanır (çift sayılmasın)."""
    games, comp_days = keys
    cid = comp or f"src:{source}"
    out = []
    for m in matches:
        d = date.fromisoformat(m["date"])
        h, a = mapping.get(m["h"]), mapping.get(m["a"])
        if h and a and any((d + timedelta(days=k), h, a) in games for k in (-1, 0, 1)):
            continue
        if not (h and a) and comp and (d, comp) in comp_days:
            continue
        out.append([noon_ts(d), cid, h or f"{source}:{m['h']}", a or f"{source}:{m['a']}",
                    m["hg"], m["ag"], m.get("hth"), m.get("hta")])
    return out
