"""Telegram mesajı ve tam bülten (HTML dosyası) üretimi."""
from __future__ import annotations

import html
from datetime import date

from . import mackolik
from .engine import value_bets

GUNLER = ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma", "Cumartesi", "Pazar"]
RES = ["1", "X", "2"]
RES_TXT = {"1": "ev sahibi kazanır", "X": "beraberlik", "2": "deplasman kazanır"}
e = html.escape


def pct(p: float | None) -> str:
    return "–" if p is None else f"%{round(p * 100)}"


def hhmm(ts_ms: int) -> str:
    from datetime import datetime, timezone
    return datetime.fromtimestamp(ts_ms / 1000, tz=timezone.utc).astimezone(mackolik.TZ).strftime("%H:%M")


def best(r: dict) -> tuple[str, float, float | None]:
    p = r["model"]["p"]
    k = max(range(3), key=lambda i: p[i])
    return RES[k], p[k], (r["ms"][k] if r.get("ms") else None)


def is_turkish(r: dict) -> bool:
    return (r.get("comp") or "").startswith("Türkiye") or (r.get("league") or "").startswith(("Trendyol", "Nesine"))


def message(recs: list[dict], day: date, warnings: list[str]) -> str:
    modeled = [r for r in recs if r.get("model")]
    lines = [
        f"⚽ <b>Günün tahminleri · {day:%d.%m.%Y} {GUNLER[day.weekday()]}</b>",
        f"Bültende {len(recs)} futbol maçı, {len(modeled)} tanesi için yeterli veri var. Tamamı ekteki dosyada.",
    ]
    strong = sorted(modeled, key=lambda r: -best(r)[1])[:10]
    if strong:
        lines.append("\n⭐ <b>En net tahminler</b>")
        for r in strong:
            res, p, odd = best(r)
            lines.append(f"{hhmm(r['ts'])} {e(r['hn'])} – {e(r['an'])}: <b>{res}</b> {pct(p)}" + (f" · oran {odd:.2f}" if odd else ""))
    vb = value_bets(recs)[:8]
    if vb:
        lines.append("\n💎 <b>Oranı modelden yüksek olanlar</b>")
        for ev, r, name, p, odd in vb:
            lines.append(f"{e(r['hn'])} – {e(r['an'])}: {name} oran {odd:.2f}, model {pct(p)} (beklenen +%{round(ev * 100)})")
    tr = sorted((r for r in recs if is_turkish(r)), key=lambda r: r["ts"])
    if tr:
        lines.append("\n🇹🇷 <b>Türkiye maçları</b>")
        for r in tr:
            head = f"{hhmm(r['ts'])} <b>{e(r['hn'])} – {e(r['an'])}</b>"
            if r.get("model"):
                M = r["model"]
                res, p, _ = best(r)
                lines.append(f"{head}\nSkor {M['score'][0]}-{M['score'][1]} · 1 {pct(M['p'][0])} X {pct(M['p'][1])} 2 {pct(M['p'][2])} · 2.5Ü {pct(M['o25'])} · KG {pct(M['btts'])}")
                miss = r["notes"]["home"] + r["notes"]["away"]
                if miss:
                    lines.append("Eksik: " + e(", ".join(miss[:4])))
            else:
                lines.append(f"{head}\n<i>yetersiz veri</i>")
    for w in warnings:
        lines.append(f"\n⚠️ {e(w)}")
    lines.append("\n<i>Tahminler olasılıktır, kesin sonuç değildir.</i>")
    return "\n".join(lines)


def split(text: str, limit: int = 3900) -> list[str]:
    parts, cur = [], ""
    for line in text.split("\n"):
        if len(cur) + len(line) + 1 > limit and cur:
            parts.append(cur)
            cur = line
        else:
            cur = f"{cur}\n{line}" if cur else line
    if cur:
        parts.append(cur)
    return parts


CSS = """
:root{color-scheme:light dark;--bg:light-dark(#f4f5f1,#0c120e);--ink:light-dark(#121a15,#e8eee9);--mut:light-dark(#5b665f,#9aa89f);--line:light-dark(#dfe3dc,#25322a);--pitch:#0f5c3b;--yel:#f2c230}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:15px/1.45 system-ui,sans-serif}
header{background:var(--pitch);color:#f4f7f2;padding:18px 16px}h1{margin:0;font-size:24px}header p{margin:6px 0 0;color:#cfe3d6}
main{max-width:1100px;margin:0 auto;padding:8px 12px 40px}h2{font-size:17px;margin:22px 0 6px;border-bottom:2px solid var(--pitch);padding-bottom:4px}
input{width:100%;font:inherit;font-size:16px;padding:10px;border:1px solid var(--line);border-radius:8px;margin-top:12px;background:transparent;color:inherit}
.m{border-bottom:1px solid var(--line);padding:8px 2px}.t{display:flex;gap:8px;flex-wrap:wrap;align-items:baseline}.t b{font-size:16px}
.sc{background:var(--yel);color:#1b1a10;border-radius:6px;padding:1px 7px;font-weight:700}.mut{color:var(--mut);font-size:13px}
.g{display:grid;grid-template-columns:repeat(auto-fit,minmax(120px,1fr));gap:4px 12px;margin-top:4px;font-size:14px}
.v{color:light-dark(#16794a,#3fbf7f);font-weight:600}
"""


def report(recs: list[dict], day: date) -> str:
    groups: dict[str, list] = {}
    for r in sorted(recs, key=lambda r: (not is_turkish(r), r.get("comp", ""), r["ts"])):
        groups.setdefault(r.get("comp") or "Diğer", []).append(r)
    vb = {(id(x[1]), x[2]) for x in value_bets(recs)}
    body = []
    for comp, rs in groups.items():
        body.append(f"<h2>{e(comp)}</h2>")
        for r in rs:
            M = r.get("model")
            odds = r.get("ms") or [None] * 3
            cells = []
            for i, k in enumerate(RES):
                mp = pct(M["p"][i]) if M else "–"
                mk = pct(r["market"][i]) if r.get("market") else "–"
                cls = ' class="v"' if (id(r), "MS " + ("0" if k == "X" else k)) in vb else ""
                cells.append(f"<div{cls}>{k}: model {mp} · iddaa {odds[i] or '–'} ({mk})</div>")
            if M:
                cells.append(f"<div>2.5 Üst: {pct(M['o25'])}" + (f" · oran {r['ou25'][1]}" if r.get("ou25") else "") + "</div>")
                cells.append(f"<div>KG Var: {pct(M['btts'])}" + (f" · oran {r['kg'][0]}" if r.get("kg") else "") + "</div>")
                cells.append(f"<div>xG {M['xg'][0]:.2f} – {M['xg'][1]:.2f}</div>")
                cells.append(f"<div>İY 1/X/2: {pct(M['ht'][0])} {pct(M['ht'][1])} {pct(M['ht'][2])}</div>")
            extra = []
            if r.get("form"):
                extra.append(f"Form {r['form'][0] or '-'} / {r['form'][1] or '-'}")
            if r.get("h2h"):
                extra.append("Aralarında: " + ", ".join(r["h2h"]))
            for side, name in (("home", r["hn"]), ("away", r["an"])):
                if r["notes"][side]:
                    extra.append(f"{name} eksikleri: " + ", ".join(r["notes"][side]))
            if r.get("mbs"):
                extra.append(f"MBS {r['mbs']}")
            score = f'<span class="sc">{M["score"][0]}-{M["score"][1]}</span>' if M else '<span class="mut">yetersiz veri</span>'
            body.append(
                f'<div class="m" data-q="{e((r["hn"] + " " + r["an"] + " " + comp).lower())}"><div class="t">'
                f'<span class="mut">{hhmm(r["ts"])}</span><b>{e(r["hn"])} – {e(r["an"])}</b>{score}</div>'
                f'<div class="g">{"".join(cells)}</div><div class="mut">{e(" · ".join(extra))}</div></div>'
            )
    return f"""<!DOCTYPE html><html lang="tr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Tahmin bülteni {day:%d.%m.%Y}</title><style>{CSS}</style></head><body>
<header><h1>Tahmin bülteni · {day:%d.%m.%Y} {GUNLER[day.weekday()]}</h1><p>{len(recs)} maç · iddaa oranları ve model olasılıkları. Yeşil: oranı modelden yüksek seçenek. Parantez içi: orandan çıkan gerçek olasılık.</p></header>
<main><input id="q" type="search" placeholder="Takım ya da lig ara" aria-label="Takım ya da lig ara">{"".join(body)}
<p class="mut">Tahminler olasılıktır, kesin sonuç değildir. Kaynak: iddaa.com bülteni, Maçkolik sonuçları ve eksik oyuncu listeleri.</p></main>
<script>document.getElementById('q').addEventListener('input',e=>{{const q=e.target.value.toLowerCase();document.querySelectorAll('.m').forEach(m=>m.style.display=m.dataset.q.includes(q)?'':'none')}})</script>
</body></html>"""
