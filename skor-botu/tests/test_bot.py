from datetime import date
from pathlib import Path

from skorbotu import bulletin, footballdata, model, tff

FX = Path(__file__).parent / "fixtures"


def test_parse_lig1_week():
    ms = tff.parse_week((FX / "lig1_hafta15.html").read_text("utf-8"))
    assert len(ms) == 10
    m = ms[0]
    assert (m["date"], m["h"], m["a"], m["hg"], m["ag"]) == ("2026-11-20", "9387", "3661", 2, 2)
    assert m["time"] == "20:00"
    assert ms[-1]["hg"] is None  # Bodrum - Van oynanmamış


def test_parse_grouped_week():
    ms = tff.parse_week((FX / "lig2_beyaz_hafta13.html").read_text("utf-8"))
    assert len(ms) == 9
    assert (ms[0]["hn"], ms[0]["hg"], ms[0]["ag"]) == ("SOMASPOR", 1, 4)


def test_parse_groups():
    g = tff.parse_groups((FX / "lig3_ana.html").read_text("utf-8"), 971)
    assert [x[1] for x in g] == ["01", "02", "03"]


def test_csv():
    txt = "Div,Date,Time,HomeTeam,AwayTeam,FTHG,FTAG\nE0,20/09/2026,16:30,Fulham,Man United,1,1\nE0,28/11/26,15:00,Arsenal,Man City,,\n"
    ms = footballdata.parse_csv(txt)
    assert ms[0]["hg"] == 1 and ms[1]["hg"] is None and ms[1]["date"] == "2026-11-28"
    assert footballdata.season_codes(date(2026, 11, 23)) == ["2627", "2526"]


def test_model_sane():
    ms = []
    d0 = date(2026, 8, 1).toordinal()
    for k in range(30):  # A güçlü, C zayıf
        ms += [(d0 + k * 3, "A", "C", 3, 0), (d0 + k * 3 + 1, "B", "A", 0, 2), (d0 + k * 3 + 2, "C", "B", 1, 1)]
    F = model.fit(ms, d0 + 100)
    P = model.predict(F, "A", "C")
    assert P.p1 > 0.7 and abs(P.p1 + P.px + P.p2 - 1) < 1e-9
    assert P.pick[0] > P.pick[1]
    assert model.form(ms, "A") == "GGGGG"


def test_short_name():
    assert bulletin.short_name("MANİSA FUTBOL KULÜBÜ") == "Manisa"
    assert bulletin.short_name("İSTANBULSPOR A.Ş.") == "İstanbulspor"
    assert bulletin.short_name("KIRIKKALE FK SPOR KULÜBÜ") == "Kırıkkale"
    assert bulletin.short_name("Man United") == "Man United"


def test_bulletin_and_split():
    day = date(2026, 11, 28)
    ms = []
    for k in range(12):
        d = date.fromordinal(day.toordinal() - 7 * (k + 1)).isoformat()
        ms += [{"date": d, "time": "", "h": "1", "a": "2", "hn": "ALFA SPOR", "an": "BETA FK", "hg": 2, "ag": 0},
               {"date": d, "time": "", "h": "2", "a": "3", "hn": "BETA FK", "an": "GAMA", "hg": 1, "ag": 1},
               {"date": d, "time": "", "h": "3", "a": "1", "hn": "GAMA", "an": "ALFA SPOR", "hg": 0, "ag": 1}]
    ms.append({"date": day.isoformat(), "time": "19:00", "h": "1", "a": "3", "hn": "ALFA SPOR", "an": "GAMA", "hg": None, "ag": None})
    text = bulletin.build([{"name": "Test Lig", "flag": "🇹🇷", "matches": ms}] * 40, day, ["deneme uyarısı"])
    assert "Alfa – Gama" in text and "28.11.2026 Cumartesi" in text and "40 maç" in text
    parts = bulletin.split(text)
    assert len(parts) > 1 and all(len(p) <= 3900 for p in parts)
    assert "".join(parts).count("Alfa – Gama") == text.count("Alfa – Gama")
