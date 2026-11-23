"""Bülten maçlarını Maçkolik geçmişiyle eşleştirip tahmin üretir."""
from __future__ import annotations

import logging
import warnings
from collections import Counter, defaultdict
from datetime import date, timedelta

from . import mackolik, model

log = logging.getLogger(__name__)
MIN_MATCHES = 5  # takım başına modelin güvenmesi için gereken en az maç (son 1 yıl)
LEAGUE = "Domestic league"


def devig(odds: list[float] | None) -> list[float] | None:
    """iddaa oranlarından kâr payını çıkarıp gerçek olasılığı bulur (penaltyblog, Shin yöntemi)."""
    if not odds or any(not o or o <= 1 for o in odds):
        return None
    try:
        import penaltyblog as pb
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            return list(pb.implied.calculate_implied(list(odds), method="shin").probabilities)
    except Exception:  # penaltyblog yoksa ya da hesaplayamazsa basit oransal yöntem
        inv = [1 / o for o in odds]
        return [x / sum(inv) for x in inv]


POS = {"kaleci": "G", "defans": "D", "orta saha": "M", "forvet": "F"}


def absence(players: list[dict], games: int, goals: int) -> tuple[float, float, list[str]]:
    """Eksik oyuncuların etkisi: (hücum çarpanı, savunma çarpanı, kısa açıklamalar).

    Oyuncunun oynadığı maç oranı ve attığı gollerin takım içindeki payı ile ağırlıklandırılır.
    Kaba bir tahmindir: kilit forvet en çok %25 hücum düşüşü, kaleci/defans en çok %25 savunma zayıflaması.
    """
    att = dfn = 0.0
    notes = []
    for p in players:
        s = min(1.0, (p.get("apps") or 0) / max(8, games))
        g = (p.get("goals") or 0) / max(5, goals)
        pos = POS.get(p.get("pos", "").lower(), p.get("pos", "")[:1].upper())
        if pos == "F":
            att += 0.05 * s + 0.5 * g
        elif pos == "M":
            att += 0.03 * s + 0.4 * g; dfn += 0.01 * s
        elif pos == "D":
            dfn += 0.04 * s; att += 0.3 * g
        elif pos == "G":
            dfn += 0.08 * s
        if s >= 0.4 or g >= 0.1:  # yalnızca önemli eksikleri yaz
            notes.append(f"{p['name']} ({pos}, {p.get('apps') or 0} maç {p.get('goals') or 0} gol)")
    return 1 - min(0.25, att), 1 + min(0.25, dfn), notes


class History:
    def __init__(self, rows: list[list], comps: dict, today: date):
        self.comps = comps
        self.today = today
        self.by_comp: dict[str, list] = defaultdict(list)
        self.by_team: dict[str, list] = defaultdict(list)
        for r in rows:
            d = mackolik.local_day(r[0]).toordinal()
            t = (d, r[2], r[3], r[4], r[5], r[1])
            self.by_comp[r[1]].append(t)
            self.by_team[r[2]].append(t)
            self.by_team[r[3]].append(t)
        self._fits: dict = {}
        self._main: dict = {}

    def main_league(self, team: str) -> str | None:
        """Takımın son bir yılda en çok oynadığı lig (kupa ve Avrupa maçları hariç)."""
        if team not in self._main:
            since = self.today.toordinal() - 365
            c = Counter(t[5] for t in self.by_team.get(team, []) if t[0] >= since and self.comps.get(t[5], ["", "", ""])[2] == LEAGUE)
            self._main[team] = c.most_common(1)[0][0] if c else None
        return self._main[team]

    def fit(self, comp: str, home: str, away: str):
        """Maçın kendi turnuvası + iki takımın ligleri birlikte: kupa/Avrupa maçlarında ligler arası güç karşılaştırılır."""
        pool = frozenset(x for x in (comp, self.main_league(home), self.main_league(away)) if x)
        if pool not in self._fits:
            ms = sorted(t[:5] for c in pool for t in self.by_comp.get(c, []))
            self._fits[pool] = model.fit(ms, self.today.toordinal()) if ms else None
        return self._fits[pool]

    def recent(self, team: str, days: int = 365) -> list:
        since = self.today.toordinal() - days
        return [t for t in self.by_team.get(team, []) if t[0] >= since]

    def season_stats(self, team: str) -> tuple[int, int]:
        lg = self.main_league(team)
        ms = [t for t in self.recent(team, 150) if t[5] == lg] or self.recent(team, 150)
        goals = sum(t[3] if t[1] == team else t[4] for t in ms)
        return len(ms), goals

    def form(self, team: str, n: int = 5) -> str:
        return model.form([t[:5] for t in self.by_team.get(team, [])], team, n)

    def h2h(self, home: str, away: str, n: int = 3) -> list[str]:
        out = []
        for t in reversed(self.by_team.get(home, [])):
            if {t[1], t[2]} == {home, away}:
                d = date.fromordinal(t[0])
                out.append(f"{d:%d.%m.%y} {'E' if t[1] == home else 'D'} {t[3]}-{t[4]}" if t[1] == home else f"{d:%d.%m.%y} D {t[4]}-{t[3]}")
                if len(out) == n:
                    break
        return out


def analyse(events: list[dict], mk_matches: dict, hist: History, with_sidelined: bool = True) -> list[dict]:
    """Her bülten maçı için tahmin kaydı üretir."""
    out = []
    for e in events:
        rec = {**e, "model": None, "market": devig(e.get("ms")), "notes": {"home": [], "away": []}}
        m = mk_matches.get(e["id"])
        if m is None:
            out.append(rec)
            continue
        rec["league"] = hist.comps.get(m["comp"], [e["comp"]])[0] or e["comp"]
        rec["form"] = (hist.form(m["home"]), hist.form(m["away"]))
        rec["h2h"] = hist.h2h(m["home"], m["away"])
        n_h, n_a = len(hist.recent(m["home"])), len(hist.recent(m["away"]))
        F = hist.fit(m["comp"], m["home"], m["away"])
        if F is None or min(F.cnt.get(m["home"], 0), F.cnt.get(m["away"], 0)) < 1 or min(n_h, n_a) < MIN_MATCHES:
            out.append(rec)
            continue
        adj = (1.0, 1.0, 1.0, 1.0)
        side = mackolik.sidelined(m) if with_sidelined else None
        if side is not None:
            ha, hd, hn = absence(side["home"], *hist.season_stats(m["home"]))
            aa, ad, an = absence(side["away"], *hist.season_stats(m["away"]))
            adj = (ha, hd, aa, ad)
            rec["notes"] = {"home": hn, "away": an}
            rec["absent"] = {"home": len(side["home"]), "away": len(side["away"])}
        P = model.predict(F, m["home"], m["away"], adj)
        rec["model"] = {
            "p": [P.p1, P.px, P.p2], "score": list(P.pick), "xg": [P.lh, P.la],
            "o25": P.over25, "btts": P.btts, "top": [list(s) for s in P.top], "ht": list(P.ht),
        }
        out.append(rec)
    return out


def value_bets(recs: list[dict], min_ev: float = 0.08) -> list[tuple]:
    """Model olasılığı × iddaa oranı - 1 ≥ min_ev olan seçenekler (beklenen kazanç)."""
    out = []
    for r in recs:
        M = r.get("model")
        if not M:
            continue
        opts = []
        if r.get("ms"):
            opts += [("MS 1", M["p"][0], r["ms"][0]), ("MS 0", M["p"][1], r["ms"][1]), ("MS 2", M["p"][2], r["ms"][2])]
        if r.get("ou25"):
            opts += [("2.5 Alt", 1 - M["o25"], r["ou25"][0]), ("2.5 Üst", M["o25"], r["ou25"][1])]
        if r.get("kg"):
            opts += [("KG Var", M["btts"], r["kg"][0]), ("KG Yok", 1 - M["btts"], r["kg"][1])]
        for name, p, odd in opts:
            if odd and p >= 0.3 and p * odd - 1 >= min_ev:
                out.append((p * odd - 1, r, name, p, odd))
    out.sort(key=lambda x: -x[0])
    return out
