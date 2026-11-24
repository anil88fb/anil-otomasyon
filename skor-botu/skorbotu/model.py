"""Skor tahmin modeli.

Zaman ağırlıklı Poisson: her takımın hücum ve savunma gücü, yakın tarihli maçlar
daha ağır sayılarak hesaplanır. Düşük skorlar için Dixon-Coles düzeltmesi uygulanır.
Maç: (gün_sırası, ev_id, dep_id, ev_gol, dep_gol)
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from datetime import date

HALF_LIFE = 300  # gün
PRIOR = 5.0
ITERS = 40
RHO = -0.08
PRIOR_ATT, PRIOR_DEF = 0.9, 1.12  # az maçı olan takım hafif zayıf varsayılır
HT_SHARE = 0.44  # gollerin ilk yarıdaki payı


@dataclass
class Fitted:
    mu_h: float
    mu_a: float
    att: dict
    defe: dict
    cnt: dict
    matches: list = field(default_factory=list)


def fit(matches: list[tuple], cutoff: int) -> Fitted:
    ms = [m for m in matches if m[0] < cutoff]
    w = [0.5 ** ((cutoff - m[0]) / HALF_LIFE) for m in ms]
    sw = sum(w) or 1.0
    mu_h = sum(wi * m[3] for wi, m in zip(w, ms)) / sw if ms else 1.45
    mu_a = sum(wi * m[4] for wi, m in zip(w, ms)) / sw if ms else 1.15
    teams = {t for m in ms for t in (m[1], m[2])}
    att = {t: 1.0 for t in teams}
    defe = {t: 1.0 for t in teams}
    cnt = {t: 0.0 for t in teams}
    for wi, m in zip(w, ms):
        cnt[m[1]] += wi
        cnt[m[2]] += wi
    k = PRIOR * (mu_h + mu_a) / 2
    for _ in range(ITERS):
        gs = dict.fromkeys(teams, 0.0); es = dict.fromkeys(teams, 0.0)
        gc = dict.fromkeys(teams, 0.0); ec = dict.fromkeys(teams, 0.0)
        for wi, (_, h, a, hg, ag) in zip(w, ms):
            gs[h] += wi * hg; es[h] += wi * mu_h * defe[a]
            gs[a] += wi * ag; es[a] += wi * mu_a * defe[h]
            gc[h] += wi * ag; ec[h] += wi * mu_a * att[a]
            gc[a] += wi * hg; ec[a] += wi * mu_h * att[h]
        for t in teams:
            att[t] = (gs[t] + k * PRIOR_ATT) / (es[t] + k)
            defe[t] = (gc[t] + k * PRIOR_DEF) / (ec[t] + k)
        if teams:
            ma = sum(att.values()) / len(teams)
            md = sum(defe.values()) / len(teams)
            for t in teams:
                att[t] /= ma
                defe[t] /= md
    return Fitted(mu_h, mu_a, att, defe, cnt, ms)


def _pois(lam: float, k: int) -> float:
    return math.exp(-lam) * lam ** k / math.factorial(k)


def _grid(lh: float, la: float, rho: float, mx: int = 9):
    g = [[0.0] * (mx + 1) for _ in range(mx + 1)]
    s = 0.0
    for i in range(mx + 1):
        for j in range(mx + 1):
            tau = 1.0
            if i == 0 and j == 0:
                tau = 1 - lh * la * rho
            elif i == 0 and j == 1:
                tau = 1 + lh * rho
            elif i == 1 and j == 0:
                tau = 1 + la * rho
            elif i == 1 and j == 1:
                tau = 1 - rho
            g[i][j] = max(0.0, _pois(lh, i) * _pois(la, j) * tau)
            s += g[i][j]
    return [[v / s for v in row] for row in g]


@dataclass
class Prediction:
    lh: float
    la: float
    p1: float
    px: float
    p2: float
    over15: float
    over25: float
    over35: float
    btts: float
    pick: tuple  # en olası sonuca uyan en olası skor
    top: list  # [(ev, dep, olasılık), ...]
    ht: tuple  # ilk yarı (1, X, 2)

    @property
    def best(self) -> tuple[str, float]:
        return max((("1", self.p1), ("X", self.px), ("2", self.p2)), key=lambda x: x[1])


def predict(F: Fitted, h, a, adj: tuple = (1.0, 1.0, 1.0, 1.0)) -> Prediction:
    """adj: (ev hücum, ev savunma, dep hücum, dep savunma) çarpanları; savunma >1 = daha çok gol yer."""
    h_att, h_def, a_att, a_def = adj
    lh = F.mu_h * F.att.get(h, PRIOR_ATT) * h_att * F.defe.get(a, PRIOR_DEF) * a_def
    la = F.mu_a * F.att.get(a, PRIOR_ATT) * a_att * F.defe.get(h, PRIOR_DEF) * h_def
    g = _grid(lh, la, RHO)
    p1 = px = p2 = btts = o15 = o25 = o35 = 0.0
    scores = []
    for i, row in enumerate(g):
        for j, p in enumerate(row):
            if i > j: p1 += p
            elif i == j: px += p
            else: p2 += p
            if i and j: btts += p
            if i + j > 1: o15 += p
            if i + j > 2: o25 += p
            if i + j > 3: o35 += p
            scores.append((i, j, p))
    scores.sort(key=lambda x: -x[2])
    best = max((0, p1), (1, px), (2, p2), key=lambda x: x[1])[0]
    match = {0: lambda s: s[0] > s[1], 1: lambda s: s[0] == s[1], 2: lambda s: s[0] < s[1]}[best]
    pick = next(s for s in scores if match(s))
    hg = _grid(lh * HT_SHARE, la * HT_SHARE, 0.0, 6)
    h1 = sum(p for i, r in enumerate(hg) for j, p in enumerate(r) if i > j)
    hx = sum(p for i, r in enumerate(hg) for j, p in enumerate(r) if i == j)
    return Prediction(lh, la, p1, px, p2, o15, o25, o35, btts, pick[:2], scores[:5], (h1, hx, 1 - h1 - hx))


def form(matches: list[tuple], team, n: int = 5) -> str:
    """Son n maç: G/B/M (en yenisi sağda)."""
    out = []
    for m in [m for m in matches if team in (m[1], m[2])][-n:]:
        f, g = (m[3], m[4]) if m[1] == team else (m[4], m[3])
        out.append("G" if f > g else "B" if f == g else "M")
    return "".join(out)


def day_index(d: date) -> int:
    return d.toordinal()
