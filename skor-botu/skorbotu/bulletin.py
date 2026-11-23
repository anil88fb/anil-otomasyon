"""Günlük tahmin bültenini oluşturur (Telegram HTML biçiminde)."""
from __future__ import annotations

import html
import re
from datetime import date

from . import model

GUNLER = ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma", "Cumartesi", "Pazar"]
_SUFFIX = re.compile(r"\s+(FUTBOL|SPOR|KULÜBÜ|KULÜP|A\.Ş\.?|AŞ|FK|SK|F\.K\.|S\.K\.)$", re.I)


def tr_title(s: str) -> str:
    def word(w: str) -> str:
        low = w.replace("I", "ı").replace("İ", "i").lower()
        if not low:
            return w
        first = {"i": "İ", "ı": "I"}.get(low[0], low[0].upper())
        return first + low[1:]
    return " ".join(word(w) for w in s.split())


def short_name(name: str) -> str:
    """TFF adları büyük harf ve sponsorlu: sondaki şirket/kulüp eklerini atar, düzgün yazar."""
    if not name.isupper():
        return name
    n = name.strip()
    prev = None
    while prev != n:
        prev = n
        n2 = _SUFFIX.sub("", n)
        if len(n2) >= 4:
            n = n2
    return tr_title(n)


def pct(p: float) -> str:
    return f"%{round(p * 100)}"


def league_block(name: str, flag: str, matches: list[dict], day: date, picks: list) -> list[str]:
    """Bir ligin o günkü maçları için satırlar. picks listesine güçlü tahminleri ekler."""
    played, todays = [], []
    for m in matches:
        d = date.fromisoformat(m["date"])
        if m["hg"] is not None:
            played.append((d.toordinal(), m["h"], m["a"], m["hg"], m["ag"]))
        elif d == day:
            todays.append(m)
    if not todays:
        return []
    played.sort()
    F = model.fit(played, day.toordinal())
    season_start = day.toordinal() - 200
    lines = [f"\n{flag} <b>{html.escape(name)}</b>"]
    for m in sorted(todays, key=lambda x: x["time"] or "99"):
        P = model.predict(F, m["h"], m["a"])
        hn, an = short_name(m["hn"]), short_name(m["an"])
        n_h = sum(1 for x in played if x[0] >= season_start and m["h"] in (x[1], x[2]))
        n_a = sum(1 for x in played if x[0] >= season_start and m["a"] in (x[1], x[2]))
        thin = " <i>(az veri)</i>" if min(n_h, n_a) < 4 else ""
        fh, fa = model.form(played, m["h"]) or "-", model.form(played, m["a"]) or "-"
        lines.append(f"<b>{html.escape(m['time'] or '--:--')}  {html.escape(hn)} – {html.escape(an)}</b>{thin}")
        lines.append(
            f"Skor <b>{P.pick[0]}-{P.pick[1]}</b> · 1 {pct(P.p1)} · X {pct(P.px)} · 2 {pct(P.p2)}"
        )
        lines.append(f"2.5Ü {pct(P.over25)} · KG {pct(P.btts)} · form {fh} / {fa}")
        if not thin:
            picks.append((P.best[1], f"{html.escape(hn)} – {html.escape(an)}", P.best[0]))
    return lines


def build(leagues: list[dict], day: date, warnings: list[str]) -> str:
    """leagues: [{'name', 'flag', 'matches'}]."""
    picks: list = []
    body: list[str] = []
    for lg in leagues:
        body += league_block(lg["name"], lg["flag"], lg["matches"], day, picks)
    n = sum(1 for l in body if l.startswith("<b>"))
    head = [f"⚽ <b>Günün tahminleri · {day:%d.%m.%Y} {GUNLER[day.weekday()]}</b>"]
    if not n:
        head.append("Takip edilen liglerde bugün maç yok.")
    else:
        head.append(f"{n} maç")
    tail = []
    strong = sorted((p for p in picks if p[0] >= 0.55), reverse=True)[:5]
    if strong:
        tail.append("\n⭐ <b>Günün en net tahminleri</b>")
        names = {"1": "ev sahibi kazanır", "X": "beraberlik", "2": "deplasman kazanır"}
        tail += [f"{t}: {names[r]} ({pct(p)})" for p, t, r in strong]
    for w in warnings:
        tail.append(f"\n⚠️ {html.escape(w)}")
    tail.append("\n<i>Tahminler olasılıktır, kesin sonuç değildir.</i>")
    return "\n".join(head + body + tail)


def split(text: str, limit: int = 3900) -> list[str]:
    """Telegram 4096 karakter sınırı için mesajı lig bloklarından böler."""
    parts, cur = [], ""
    for block in text.split("\n\n"):
        piece = (("\n\n" if cur else "") + block)
        if len(cur) + len(piece) > limit and cur:
            parts.append(cur)
            cur = block
        else:
            cur += piece
    if cur:
        parts.append(cur)
    out = []
    for p in parts:  # tek blok sınırı aşarsa satırdan böl
        while len(p) > limit:
            cut = p.rfind("\n", 0, limit)
            cut = cut if cut > 0 else limit
            out.append(p[:cut])
            p = p[cut:].lstrip("\n")
        out.append(p)
    return out
