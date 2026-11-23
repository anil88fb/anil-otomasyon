import json
from datetime import date, timedelta
from pathlib import Path

from skorbotu import bulletin, engine, iddaa, mackolik, model

FX = Path(__file__).parent / "fixtures"


def load(name):
    return json.loads((FX / name).read_text("utf-8"))


def test_mackolik_parse_day():
    ms, comps = mackolik.parse_day(load("mackolik_2026-11-22.json")["data"])
    b = next(m for m in ms if m["hn"] == "Bursaspor")
    assert (b["hg"], b["ag"], b["hth"], b["hta"], b["iddaa"]) == (2, 0, 2, 0, 3319146)
    assert comps[b["comp"]][0] == "Trendyol 1. Lig"
    rows = mackolik.finished_rows(ms)
    assert rows and all(r[4] is not None for r in rows)


def test_store_roundtrip(tmp_path):
    st = mackolik.Store(tmp_path)
    st.save(date(2026, 11, 22), load("mackolik_2026-11-22.json")["data"])
    rows, comps = st.load(date(2026, 1, 1))
    assert any(r[2] == "86aq9jbei8h8p1ftxbmy8y2kk" and r[4] == 2 for r in rows)
    assert "2o9svokc5s7diish3ycrzk7jm" in comps


def test_iddaa_parse():
    ev = iddaa.parse_events(load("iddaa_events.json")["data"], {46194: "UEFA Şampiyonlar Ligi"})
    gs = next(e for e in ev if e["hn"] == "Galatasaray")
    assert gs["comp"] == "UEFA Şampiyonlar Ligi" and len(gs["ms"]) == 3 and all(o > 1 for o in gs["ms"])
    assert gs["ou25"] and gs["kg"]


def test_sidelined():
    boxes = mackolik.parse_sidelined((FX / "mackolik_sidelined.html").read_text("utf-8"))
    assert len(boxes) == 2
    p = boxes[0]["players"][0]
    assert p["name"] == "A. Fayzullayev" and p["pos"] == "Orta Saha" and p["apps"] == 8 and p["goals"] == 1
    assert "Sakatlığı" in p["reason"]


def test_absence_and_devig():
    att, dfn, notes = engine.absence([{"name": "X", "pos": "Forvet", "apps": 12, "goals": 8}], 12, 20)
    assert 0.75 <= att < 0.8 and dfn == 1 and notes
    att, dfn, _ = engine.absence([{"name": "K", "pos": "Kaleci", "apps": 12, "goals": 0}], 12, 20)
    assert att == 1 and abs(dfn - 1.08) < 1e-9
    p = engine.devig([2.6, 3.53, 2.05])
    assert abs(sum(p) - 1) < 1e-6 and p[2] > p[0]


def _synthetic_history(day):
    rows = []
    teams = ["A", "B", "C", "D"]
    base = int((mackolik.datetime(day.year, day.month, day.day, tzinfo=mackolik.TZ)).timestamp() * 1000)
    k = 0
    for w in range(30):
        for i, h in enumerate(teams):
            a = teams[(i + 1 + w) % 4]
            if a == h:
                continue
            hg = 3 if h == "A" else 1
            ag = 0 if h == "A" else (2 if a == "A" else 1)
            rows.append([base - (w * 7 + i + 1) * 86400000, "L1", h, a, hg, ag, 0, 0])
            k += 1
    rows.sort()
    return rows, {"L1": ["Test Lig", "Türkiye", "Domestic league"]}


def test_engine_end_to_end():
    day = date(2026, 11, 24)
    rows, comps = _synthetic_history(day)
    hist = engine.History(rows, comps, day)
    ts = int(mackolik.datetime(2026, 11, 24, 20, 0, tzinfo=mackolik.TZ).timestamp() * 1000)
    ev = [{"id": 1, "ts": ts, "comp": "Türkiye Test Lig", "hn": "Alfa", "an": "Beta", "mbs": 1,
           "ms": [1.4, 4.5, 7.0], "ou25": [2.0, 1.8], "kg": [1.9, 1.85]},
          {"id": 2, "ts": ts, "comp": "Başka Lig", "hn": "X", "an": "Y", "mbs": 1, "ms": [2, 3, 3], "ou25": None, "kg": None}]
    mk = {1: {"id": "m1", "comp": "L1", "home": "A", "away": "C", "slug": "a-vs-c"}}
    recs = engine.analyse(ev, mk, hist, with_sidelined=False)
    assert recs[0]["model"]["p"][0] > 0.6 and recs[1]["model"] is None
    assert recs[0]["form"][0]
    text = bulletin.message(recs, day, ["uyarı"])
    assert "Alfa – Beta" in text and "Türkiye maçları" in text and "24.11.2026 Salı" in text
    html = bulletin.report(recs, day)
    assert html.startswith("<!DOCTYPE html>") and "yetersiz veri" in html
    assert all(len(p) <= 3900 for p in bulletin.split(text * 30))


def test_model_sane():
    ms = []
    d0 = date(2026, 8, 1).toordinal()
    for k in range(30):
        ms += [(d0 + k * 3, "A", "C", 3, 0), (d0 + k * 3 + 1, "B", "A", 0, 2), (d0 + k * 3 + 2, "C", "B", 1, 1)]
    F = model.fit(ms, d0 + 100)
    P = model.predict(F, "A", "C")
    assert P.p1 > 0.7 and abs(P.p1 + P.px + P.p2 - 1) < 1e-9 and P.pick[0] > P.pick[1]
    P2 = model.predict(F, "A", "C", (0.75, 1, 1, 1))
    assert P2.lh < P.lh
