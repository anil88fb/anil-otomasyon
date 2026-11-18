import sys; sys.path.insert(0, "/home/claude/shorts")
from lib import *
D = "/home/claude/shorts/v2"
LINES = ["What if the Moon came twice as close?",
         "It would look four times bigger in the night sky.",
         "But its pull on the oceans would be about eight times stronger.",
         "Tides would rise many meters higher, flooding coastal cities twice a day.",
         "That extra pull would squeeze the Earth itself, so we could get more earthquakes and volcanoes.",
         "Good news: the Moon is actually drifting away, about four centimeters every year."]
tl = Timeline(D)
PA, PA2, INK, SOFT = "#F0EBDE", "#E6E0CE", "#1F2BE0", "#5560E5"
NO = Ink()
CAP = dict(font="hanken-grotesk-800", size=84, col=SOFT, hi=INK, plate=PA, y=1520, outline=INK, ow=3, radius=0)

def paper(f, t):
    f[:] = bgr(PA)
    g = bgr("#d9d4f0")
    for x in range(0, W, 54): cv2.line(f, (x, 0), (x, H), g, 1)
    for y in range(0, H, 54): cv2.line(f, (0, y), (W, y), g, 1)
    cv2.line(f, (40, 60), (W - 40, 60), bgr(INK), 2); cv2.line(f, (40, H - 60), (W - 40, H - 60), bgr(INK), 2)

def chrome(f, num, label):
    text(f, f"FIG. {num}", 50, 74, "dm-mono-500", 30, INK, track=0.08)
    paste(f, text_img(label.upper(), "dm-mono-500", 30, INK, 0.08), W - 50, 74, 1, "rt")

def glitch(f, x, y, t, n=6):
    rng = np.random.default_rng(int(t * 6))
    for k in range(n):
        if rng.random() < 0.6:
            xx, yy = x + rng.integers(0, 6) * 18, y + rng.integers(0, 3) * 18
            cv2.rectangle(f, (int(xx), int(yy)), (int(xx + 16), int(yy + 16)), bgr(INK), -1)

def moon(f, x, y, r, t, mood="smile"):
    NO.circle(f, x, y, r, INK)
    for cx, cy, cr in ((-0.45, -0.35, 0.18), (0.4, 0.3, 0.14), (0.1, 0.55, 0.1), (0.5, -0.4, 0.09)):
        cv2.circle(f, (int(x + cx * r), int(y + cy * r)), int(cr * r), bgr(SOFT), -1, cv2.LINE_AA)
    face(f, x, y - r * 0.05, r / 55, eye=PA, mouth=mood, blink=blink_at(t, 2), t=t)

def earth(f, x, y, r, t, stretch=0.0, ang=0.0):
    cv2.ellipse(f, (int(x), int(y)), (int(r * (1 + stretch)), int(r * (1 - stretch * 0.4))), ang, 0, 360, bgr(PA), -1, cv2.LINE_AA)
    cv2.ellipse(f, (int(x), int(y)), (int(r * (1 + stretch)), int(r * (1 - stretch * 0.4))), ang, 0, 360, bgr(INK), 6, cv2.LINE_AA)
    # continents as hatched blobs (rotate with t)
    for k, (a, rr, s) in enumerate(((0.3, 0.5, 0.32), (2.2, 0.45, 0.28), (4.0, 0.55, 0.22))):
        aa = a + t * 0.3
        cx, cy = x + math.cos(aa) * r * rr, y + math.sin(aa) * r * rr * 0.6
        if math.cos(aa) > -0.2:
            cv2.ellipse(f, (int(cx), int(cy)), (int(s * r * max(0.2, math.cos(aa) * 0.5 + 0.5)), int(s * r * 0.8)), 20, 0, 360, bgr(SOFT), -1, cv2.LINE_AA)

def dashed_circle(f, x, y, r, col, w=3):
    for k in range(0, 360, 8):
        cv2.ellipse(f, (int(x), int(y)), (int(r), int(r)), 0, k, k + 4, bgr(col), w, cv2.LINE_AA)

def arrow(f, a, b, w=8, col=INK):
    cv2.arrowedLine(f, (int(a[0]), int(a[1])), (int(b[0]), int(b[1])), bgr(col), w, cv2.LINE_AA, tipLength=0.18)

def frame(t):
    i, lt, dur = tl.which(t)
    f = np.zeros((H, W, 3), np.uint8); paper(f, t)
    if i == 0:
        ex, ey = 540, 1050
        dashed_circle(f, ex, ey, 420, SOFT); dashed_circle(f, ex, ey, 210, INK)
        earth(f, ex, ey, 120, t)
        d = lerp(420, 210, eio((lt - 0.4) / 1.6)); a = -0.9 + lt * 0.5
        moon(f, ex + math.cos(a) * d, ey + math.sin(a) * d, 55, t, "o" if lt > 1.2 else "smile")
        text(f, "What if the Moon", 70, 220, "newsreader-600", 104, INK, lt)
        text(f, "came twice", 70, 340, "newsreader-600", 104, INK, lt, 0.15)
        text(f, "as close?", 70, 460, "newsreader-600", 104, INK, lt, 0.3)
        glitch(f, 830, 250, t)
        chrome(f, "1", "orbit / 2")
    elif i == 1:
        # city skyline line art
        base = 1380
        for k, (x0, w, h) in enumerate(((60, 140, 260), (220, 110, 380), (350, 170, 200), (540, 120, 330), (680, 160, 240), (860, 160, 300))):
            cv2.rectangle(f, (x0, base - h), (x0 + w, base), bgr(PA), -1)
            cv2.rectangle(f, (x0, base - h), (x0 + w, base), bgr(INK), 4)
            for wy in range(base - h + 30, base - 20, 50):
                for wx in range(x0 + 20, x0 + w - 20, 40): cv2.rectangle(f, (wx, wy), (wx + 16, wy + 22), bgr(SOFT), -1)
        cv2.line(f, (0, base), (W, base), bgr(INK), 4)
        g = eio((lt - 0.3) / 1.4)
        r = lerp(90, 180, g)
        dashed_circle(f, 540, 760, 90, SOFT)
        moon(f, 540, 760, r, t)
        text(f, "×4", 70, 200, "newsreader-600", 300, INK, lt, 0.8)
        text(f, "bigger in the sky", 75, 520, "hanken-grotesk-800", 60, INK, lt, 1.0)
        chrome(f, "2", "apparent size")
    elif i == 2:
        ex, ey, mx, my = 380, 980, 900, 980
        s = 0.28 * eio((lt - 0.5) / 1.5)
        # ocean bulge
        cv2.ellipse(f, (ex, ey), (int(170 * (1 + s)), int(170 * (1 - s * 0.4))), 0, 0, 360, bgr("#c9cdf6"), -1, cv2.LINE_AA)
        earth(f, ex, ey, 150, t)
        moon(f, mx, my, 80, t, "talk")
        for k in range(3):
            q = (lt * 1.2 + k / 3) % 1
            arrow(f, (lerp(mx - 100, ex + 200, q), my - 60 + k * 60), (lerp(mx - 100, ex + 200, q) - 60, my - 60 + k * 60), 8)
        text(f, "×8", 70, 200, "newsreader-600", 300, INK, lt, 0.3)
        text(f, "tidal pull", 75, 520, "hanken-grotesk-800", 60, INK, lt, 0.5)
        if lt > 1.6:
            NO.rect(f, 600, 1240, 1010, 1330, INK); paste(f, text_img("PULL ~ 1 / d³", "dm-mono-500", 44, PA, 0.04), 805, 1262, ease((lt - 1.6) / 0.4), "ct")
        chrome(f, "3", "tides")
    elif i == 3:
        base = 1300
        lvl = base - 60 - 260 * (0.5 - 0.5 * math.cos(lt * 2 * math.pi / (dur / 2))) * ease(lt / 0.6)
        for k, (x0, w, h) in enumerate(((80, 140, 300), (260, 120, 420), (420, 170, 240), (630, 120, 360), (790, 180, 280))):
            cv2.rectangle(f, (x0, base - h), (x0 + w, base), bgr(PA), -1); cv2.rectangle(f, (x0, base - h), (x0 + w, base), bgr(INK), 4)
        ov = f.copy(); cv2.rectangle(ov, (0, int(lvl)), (W, base + 20), bgr("#7f87ee"), -1); cv2.addWeighted(ov, 0.55, f, 0.45, 0, f)
        pts = [(x, int(lvl + math.sin(x / 50 + t * 4) * 10)) for x in range(0, W + 20, 20)]
        cv2.polylines(f, [np.array(pts)], False, bgr(INK), 5, cv2.LINE_AA)
        cv2.line(f, (0, base + 20), (W, base + 20), bgr(INK), 4)
        # ruler
        cv2.line(f, (1000, base), (1000, base - 400), bgr(INK), 4)
        for k in range(9): cv2.line(f, (985, base - k * 50), (1015, base - k * 50), bgr(INK), 3)
        text(f, "flooded", 70, 220, "newsreader-600", 170, INK, lt)
        text(f, "twice a day", 75, 430, "hanken-grotesk-800", 70, INK, lt, 0.4)
        glitch(f, 800, 230, t)
        chrome(f, "4", "coastline")
    elif i == 4:
        cx, cy = 540, 1000
        shake = math.sin(t * 40) * 6 * (lt > 1.0)
        cx += shake
        cv2.circle(f, (int(cx), cy), 300, bgr(PA), -1, cv2.LINE_AA)
        cv2.circle(f, (int(cx), cy), 300, bgr(INK), 6, cv2.LINE_AA)
        cv2.circle(f, (int(cx), cy), 190, bgr("#c9cdf6"), -1, cv2.LINE_AA); cv2.circle(f, (int(cx), cy), 190, bgr(INK), 4, cv2.LINE_AA)
        cv2.circle(f, (int(cx), cy), 90, bgr(INK), -1, cv2.LINE_AA)
        # squeeze arrows
        for a in (0, 180):
            ra = math.radians(a); p = 1 - 0.15 * abs(math.sin(lt * 3))
            arrow(f, (cx + math.cos(ra) * 460 * p, cy), (cx + math.cos(ra) * 330, cy), 12)
        # cracks
        rng = np.random.default_rng(5)
        for k in range(int(min(6, lt * 2))):
            a = rng.uniform(0, 6.28); x0, y0 = cx + math.cos(a) * 300, cy + math.sin(a) * 300
            pts = [(x0, y0)]
            for s in range(4): pts.append((pts[-1][0] - math.cos(a) * 30 + rng.uniform(-20, 20), pts[-1][1] - math.sin(a) * 30 + rng.uniform(-20, 20)))
            cv2.polylines(f, [np.array(pts, np.int32)], False, bgr(INK), 5, cv2.LINE_AA)
        # volcano on top
        vx, vy = cx + 0, cy - 300
        NO.poly(f, [(vx - 70, vy + 20), (vx + 70, vy + 20), (vx + 25, vy - 70), (vx - 25, vy - 70)], INK)
        if lt > 1.5:
            for k in range(8):
                q = ((lt * 1.5 + k / 8) % 1)
                cv2.circle(f, (int(vx + (k - 4) * 14 * q), int(vy - 80 - 160 * q)), int(16 * (1 - q) + 4), bgr(SOFT), -1, cv2.LINE_AA)
        text(f, "more quakes", 70, 200, "newsreader-600", 130, INK, lt)
        text(f, "+ volcanoes", 70, 345, "newsreader-600", 130, SOFT, lt, 0.8)
        chrome(f, "5", "crust stress")
    else:
        ex, ey = 260, 1000
        earth(f, ex, ey, 130, t)
        mxp = lerp(560, 900, eio(lt / dur))
        moon(f, mxp, 1000, 70, t, "smile")
        cv2.line(f, (ex + 140, 1160), (int(mxp), 1160), bgr(INK), 3)
        for k in range(0, int(mxp - ex - 140), 40): cv2.line(f, (ex + 140 + k, 1145), (ex + 140 + k, 1175), bgr(INK), 3)
        text(f, "~4 cm", 70, 220, "newsreader-600", 220, INK, lt, 0.6)
        text(f, "every year", 75, 470, "hanken-grotesk-800", 70, INK, lt, 0.9)
        if lt > dur - 1.9:
            NO.rect(f, 160, 1700, 920, 1800, INK)
            paste(f, text_img("FOLLOW FOR MORE WHAT IFs", "dm-mono-500", 40, PA, 0.06), 540, 1728, ease((lt - dur + 1.9) / 0.4), "ct")
        chrome(f, "6", "drift")
    captions(f, t, tl, LINES, CAP)
    if lt < 0.1 and i > 0: f[:] = np.clip(f.astype(np.int16) - int(60 * (1 - lt / 0.1)), 0, 255).astype(np.uint8)
    return f

run(D, tl, frame, "moon_closer_cobalt", "mystic", 84, [(0.2, "boom"), (tl.starts[4] + 1.0, "boom"), (tl.starts[3] + 0.5, "splash")])
