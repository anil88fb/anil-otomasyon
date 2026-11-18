import sys; sys.path.insert(0, "/home/claude/shorts")
from lib import *
D = "/home/claude/shorts/v11"
LINES = ["What if the Sun suddenly disappeared?",
         "For about eight minutes, nothing. That's how long sunlight takes to reach us.",
         "Then, darkness. And with no Sun to circle, Earth drifts off in a straight line.",
         "Without sunlight, plants stop making food.",
         "And within about a week, the whole surface would drop below freezing.",
         "Good thing our Sun has billions of years left!"]
tl = Timeline(D)
GR, GRD, GRL, PK, PKD, CR, CR2, INK = "#2e4a2a", "#243a21", "#3a5a36", "#e89cb1", "#d27e96", "#efe7d4", "#e6dcc4", "#1a1a17"
NO = Ink(); L = Ink(INK, 4)
CAP_L = dict(font="source-serif-4-700", size=72, col=GR, hi=PKD, plate=CR, y=1530, outline=GR, ow=3)
CAP_D = dict(font="source-serif-4-700", size=72, col=CR, hi=PK, plate=GRD, y=1530, outline=CR, ow=3)

def chrome(f, num, label, dark=False):
    c = CR if dark else GR
    paste(f, text_img(f"{num} / {label.upper()}", "jetbrains-mono-500", 28, c, 0.18), 70, 80)
    cv2.line(f, (70, 128), (W - 70, 128), bgr(c), 2, cv2.LINE_AA)

def title(f, s, y, lt, col, size=118, delay=0.0): text(f, s, 70, y, "source-serif-4-500", size, col, lt, delay)

def sun(f, x, y, r, t, mood="smile", a=1.0):
    if a <= 0: return
    ov = f.copy()
    for k in range(12):
        ang = k / 12 * 2 * math.pi + t * 0.4
        cv2.line(ov, (int(x + math.cos(ang) * (r + 20)), int(y + math.sin(ang) * (r + 20))), (int(x + math.cos(ang) * (r + 70)), int(y + math.sin(ang) * (r + 70))), bgr(PKD), 12, cv2.LINE_AA)
    cv2.circle(ov, (int(x), int(y)), int(r), bgr(PK), -1, cv2.LINE_AA)
    cv2.circle(ov, (int(x), int(y)), int(r), bgr(INK), 4, cv2.LINE_AA)
    face(ov, x, y - r * 0.05, r / 60, eye=INK, mouth=mood, blink=blink_at(t, 10), t=t)
    cv2.addWeighted(ov, a, f, 1 - a, 0, f)

def earth(f, x, y, r, t, ice=0.0, dark=False):
    L.circle(f, x, y, r, "#6f9fc7" if not dark else "#3d5a75")
    for a0, rr, s in ((0.4, 0.4, 0.35), (2.6, 0.5, 0.3), (4.3, 0.35, 0.25)):
        cv2.ellipse(f, (int(x + math.cos(a0 + t * 0.3) * r * rr), int(y + math.sin(a0) * r * rr * 0.6)), (int(r * s), int(r * s * 0.7)), 15, 0, 360, bgr(GRL if not dark else GRD), -1, cv2.LINE_AA)
    if ice > 0:
        ov = f.copy(); cv2.circle(ov, (int(x), int(y)), int(r), bgr("#f4f6f8"), -1, cv2.LINE_AA); cv2.addWeighted(ov, ice * 0.8, f, 1 - ice * 0.8, 0, f)
    cv2.circle(f, (int(x), int(y)), int(r), bgr(INK), 4, cv2.LINE_AA)

def dashed(f, x, y, r, col, w=3):
    for k in range(0, 360, 8): cv2.ellipse(f, (int(x), int(y)), (int(r), int(r)), 0, k, k + 4, bgr(col), w, cv2.LINE_AA)

def plant(f, x, y, s, wilt, t):
    cv2.line(f, (int(x), int(y)), (int(x + 40 * wilt * s), int(y - 260 * s + 120 * wilt * s)), bgr(GR), int(14 * s), cv2.LINE_AA)
    tip = (x + 40 * wilt * s, y - 260 * s + 120 * wilt * s)
    for sgn in (-1, 1):
        ang = -50 * sgn + wilt * 80 * sgn
        L.ellipse(f, x + sgn * 60 * s + 20 * wilt * s, y - 150 * s + 60 * wilt * s, 70 * s, 28 * s, GRL if wilt < 0.5 else "#8a8a5a", ang)
    L.circle(f, tip[0], tip[1], 40 * s, PK if wilt < 0.5 else "#a88a70")
    face(f, tip[0], tip[1] - 4, 0.8 * s, eye=INK, mouth="smile" if wilt < 0.4 else "flat", blink=wilt > 0.6, t=t)
    NO.rect(f, x - 90 * s, y, x + 90 * s, y + 120 * s, "#a5603f", 18)

def frame(t):
    i, lt, dur = tl.which(t)
    f = np.zeros((H, W, 3), np.uint8)
    if i == 0:
        f[:] = bgr(CR)
        gone = lt > 1.4
        dashed(f, 540, 1000, 330, GR)
        a = lt * 0.8
        earth(f, 540 + math.cos(a) * 330, 1000 + math.sin(a) * 330, 60, t)
        if not gone: sun(f, 540, 1000, 140, t, "o" if lt > 0.9 else "smile")
        else:
            p = ease((lt - 1.4) / 0.4)
            for k in range(10):
                ang = k / 10 * 2 * math.pi
                cv2.circle(f, (int(540 + math.cos(ang) * 200 * p), int(1000 + math.sin(ang) * 200 * p)), int(18 * (1 - p) + 2), bgr(PK), -1, cv2.LINE_AA)
            dashed(f, 540, 1000, 140, PKD)
        title(f, "What if the Sun", 180, lt, GR, 112)
        title(f, "disappeared?", 320, lt, PKD, 130, 0.2)
    elif i == 1:
        f[:] = bgr(CR)
        dashed(f, 200, 1000, 120, PKD)
        p = min(1, lt / dur)
        for k in range(5):
            x = 330 + p * 520 - k * 70
            if x > 330: cv2.line(f, (int(x - 40), 1000 + (k - 2) * 30), (int(x), 1000 + (k - 2) * 30), bgr(PKD), 8, cv2.LINE_AA)
        earth(f, 900, 1000, 80, t)
        mins = 8.3 * min(1, lt / (dur * 0.9))
        paste(f, text_img(f"{int(mins)}:{int((mins % 1) * 60):02d}", "jetbrains-mono-500", 150, GR), 540, 1150, 1, "ct")
        title(f, "8 minutes", 180, lt, GR, 150)
        title(f, "of nothing.", 350, lt, PKD, 120, 0.3)
        chrome(f, "02", "light delay")
    elif i == 2:
        f[:] = bgr(GRD)
        rng = np.random.default_rng(5)
        for k in range(60): cv2.circle(f, (int(rng.uniform(0, W)), int(rng.uniform(150, 1450))), 2, bgr(CR), -1)
        dashed(f, 430, 1000, 330, GRL)
        a0 = -0.5; sx, sy = 430 + math.cos(a0) * 330, 1000 + math.sin(a0) * 330
        tx, ty = -math.sin(a0), math.cos(a0)
        p = eio((lt - 0.8) / 3.5)
        ex, ey = sx + tx * 600 * p, sy + ty * 600 * p
        for k in range(1, 8):
            q = p * k / 8
            cv2.circle(f, (int(sx + tx * 600 * q), int(sy + ty * 600 * q)), 4, bgr(PK), -1, cv2.LINE_AA)
        earth(f, ex, ey, 60, t, dark=True)
        title(f, "Darkness.", 180, lt, CR, 150)
        title(f, "Earth drifts off.", 360, lt, PK, 110, 0.6)
        chrome(f, "03", "no orbit", dark=True)
    elif i == 3:
        f[:] = bgr(CR2)
        wilt = eio((lt - 0.5) / 2.0)
        plant(f, 540, 1250, 1.6, wilt, t)
        dashed(f, 880, 560, 80, PKD)
        title(f, "No light,", 180, lt, GR, 140)
        title(f, "no food.", 340, lt, PKD, 140, 0.3)
        chrome(f, "04", "plants")
    elif i == 4:
        f[:] = bgr(GRD)
        ice = eio((lt - 0.5) / 3.0)
        earth(f, 380, 1000, 220, t, ice=ice, dark=True)
        # thermometer
        tx = 860
        L.rect(f, tx - 34, 620, tx + 34, 1260, CR, 34); L.circle(f, tx, 1290, 62, CR)
        temp = lerp(15, -18, ice)
        lvl = lerp(1240, 640, (temp + 30) / 60)
        cv2.rectangle(f, (tx - 18, int(lvl)), (tx + 18, 1270), bgr(PKD if temp > 0 else "#6f9fc7"), -1)
        cv2.circle(f, (tx, 1290), 46, bgr(PKD if temp > 0 else "#6f9fc7"), -1, cv2.LINE_AA)
        y0 = lerp(1240, 640, 30 / 60); cv2.line(f, (tx - 70, int(y0)), (tx + 70, int(y0)), bgr(CR), 3)
        paste(f, text_img(f"{temp:+.0f}°C", "jetbrains-mono-500", 64, CR), tx, 520, 1, "ct")
        title(f, "Below", 180, lt, CR, 150)
        title(f, "freezing.", 350, lt, PK, 150, 0.3)
        chrome(f, "05", "one week later", dark=True)
    else:
        f[:] = bgr(CR)
        sun(f, 540, 1000, 200, t, "smile", ease(lt / 0.6))
        dashed(f, 540, 1000, 420, GR); a = t * 0.4
        earth(f, 540 + math.cos(a) * 420, 1000 + math.sin(a) * 420, 60, t)
        title(f, "Billions of years", 180, lt, GR, 110)
        title(f, "left. Relax.", 320, lt, PKD, 130, 0.4)
        if lt > dur - 1.8:
            paste(f, text_img("FOLLOW FOR MORE WHAT IFs", "jetbrains-mono-500", 40, GR, 0.14), 540, 1720, ease((lt - dur + 1.8) / 0.4), "ct")
        chrome(f, "06", "good news")
    captions(f, t, tl, LINES, CAP_D if i in (2, 4) else CAP_L, skip=(0,))
    return f

run(D, tl, frame, "sun_disappears_forest", "drama", 88, [(tl.starts[0] + 1.3, "boom"), (tl.starts[2], "boom"), (tl.starts[5] + 0.2, "ding")])
