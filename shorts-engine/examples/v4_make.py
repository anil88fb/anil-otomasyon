import sys; sys.path.insert(0, "/home/claude/shorts")
from lib import *
D = "/home/claude/shorts/v4"
LINES = ["How do you stay warm in a house made of snow?",
         "First, cut blocks of hard packed snow, and stack them in a spiral that leans inward.",
         "The dome holds itself up. No frame needed.",
         "Dig the entrance lower than the floor, so cold air sinks and stays out.",
         "Snow is full of trapped air, so it's a great insulator. Your body heat warms the inside.",
         "Outside: minus forty. Inside: above freezing!"]
tl = Timeline(D)
BG, CB, TX, MU, LI, RED = "#fdfae7", "#1e2bfa", "#111111", "#6b6b6b", "#9a9a9a", "#dc2626"
SNOW, SNOW2, CARD = "#ffffff", "#dfe4f2", "#eef0fe"
NO = Ink(); OL = Ink("#c7cce0", 3)
CAP = dict(font="space-grotesk-700", size=80, col=TX, hi=CB, plate=SNOW, y=1520, outline=CB, ow=0, shadow="#dfe2fb", sh=(0, 10), radius=26)

def snowfall(f, t, n=60):
    rng = np.random.default_rng(1)
    for k in range(n):
        x = (rng.uniform(0, W) + math.sin(t + k) * 20) % W; y = (rng.uniform(0, H) + t * (40 + k % 5 * 15)) % H
        cv2.circle(f, (int(x), int(y)), 4 + k % 3, bgr("#d8dcf0"), -1, cv2.LINE_AA)

def chrome(f, num, label):
    NO.rect(f, 60, 70, 60 + 18, 70 + 18, CB)
    text(f, f"{num} / 06", 95, 62, "space-grotesk-500", 32, TX)
    paste(f, text_img(label, "inter-600", 30, MU), W - 60, 66, 1, "rt")

def card(f, x0, y0, x1, y1, col=CARD): NO.rect(f, x0, y0 + 10, x1, y1 + 10, "#dfe2fb", 30); NO.rect(f, x0, y0, x1, y1, col, 30)

def igloo(f, cx, base, R, rows_done=99.0, t=0.0, door=True):
    """dome made of rows of blocks; rows_done can be fractional"""
    nrows = 7
    for r in range(nrows):
        if r >= rows_done: break
        frac = min(1, rows_done - r)
        a0 = math.asin(r / nrows); a1 = math.asin(min(1, (r + 1) / nrows))
        y0, y1 = base - R * math.sin(a0), base - R * math.sin(a1)
        w0, w1 = R * math.cos(a0), R * math.cos(a1)
        nb = max(2, int(9 - r))
        for b in range(int(nb * frac + 0.999)):
            u0, u1 = b / nb, (b + 1) / nb
            pts = [(cx - w0 + 2 * w0 * u0, y0), (cx - w0 + 2 * w0 * u1, y0), (cx - w1 + 2 * w1 * u1, y1), (cx - w1 + 2 * w1 * u0, y1)]
            OL.poly(f, pts, SNOW if (r + b) % 2 else "#f4f6fc")
    if rows_done >= nrows:
        cv2.ellipse(f, (int(cx), int(base - R * 0.99)), (int(R * 0.12), int(R * 0.06)), 0, 0, 360, bgr(SNOW), -1, cv2.LINE_AA)
    if door and rows_done >= 2:
        NO.ellipse(f, cx + R * 0.55, base, R * 0.32, R * 0.32, "#f4f6fc", 0, 180, 360)
        NO.ellipse(f, cx + R * 0.55, base, R * 0.2, R * 0.22, "#2a2f45", 0, 180, 360)

def person(f, x, y, s, t, warm=0.0):
    if warm > 0:
        ov = f.copy(); cv2.circle(ov, (int(x), int(y - 60 * s)), int(170 * s), bgr("#ffd2c4"), -1, cv2.LINE_AA); cv2.addWeighted(ov, 0.5 * warm, f, 1 - 0.5 * warm, 0, f)
    NO.rect(f, x - 60 * s, y - 80 * s, x + 60 * s, y + 60 * s, CB, int(40 * s))
    NO.circle(f, x, y - 110 * s, 62 * s, CB)
    NO.circle(f, x, y - 105 * s, 44 * s, "#f5d3b5")
    face(f, x, y - 112 * s, 0.75 * s, blink=blink_at(t, 4), mouth="smile")

def frame(t):
    i, lt, dur = tl.which(t)
    f = np.zeros((H, W, 3), np.uint8); f[:] = bgr(BG)
    if i == 0:
        cv2.rectangle(f, (0, 1250), (W, H), bgr(SNOW), -1)
        igloo(f, 540, 1250, 330, 99, t)
        person(f, 880, 1300, 0.9, t)
        snowfall(f, t)
        text(f, "A house", 70, 220, "space-grotesk-700", 150, TX, lt)
        text(f, "made of snow", 70, 380, "space-grotesk-700", 150, CB, lt, 0.2)
        text(f, "...and warm inside?", 75, 560, "inter-600", 56, MU, lt, 0.6)
        chrome(f, "01", "igloo")
    elif i == 1:
        cv2.rectangle(f, (0, 1250), (W, H), bgr(SNOW), -1)
        rows = 7 * eio((lt - 0.4) / (dur - 1.0))
        igloo(f, 540, 1250, 330, rows, t, door=False)
        # flying block
        nb = (rows % 1)
        if rows < 7:
            bx = lerp(980, 540 + 300 * math.cos(nb * 3), nb); by = lerp(1150, 1250 - 330 * (int(rows) + 0.5) / 7, nb)
            OL.rect(f, bx - 50, by - 25, bx + 50, by + 25, SNOW)
        # spiral arrow
        card(f, 60, 580, 600, 740)
        paste(f, text_img("STEP 1", "space-grotesk-700", 40, CB), 100, 600)
        paste(f, text_img("cut blocks, spiral in", "inter-600", 44, TX), 100, 660)
        text(f, "Cut. Stack.", 70, 220, "space-grotesk-700", 150, TX, lt)
        text(f, "Spiral.", 70, 380, "space-grotesk-700", 150, CB, lt, 0.2)
        chrome(f, "02", "build")
    elif i == 2:
        cv2.rectangle(f, (0, 1250), (W, H), bgr(SNOW), -1)
        igloo(f, 540, 1250, 330, 99, t)
        p = ease((lt - 0.3) / 1.2)
        for sd in (-1, 1):
            for R in (370, 300):
                a_end = 90 - 85 * p
                if sd < 0: cv2.ellipse(f, (540, 1250), (R, R), 0, -90 - 4, -90 - (90 - a_end), bgr(CB), 7, cv2.LINE_AA)
                else: cv2.ellipse(f, (540, 1250), (R, R), 0, -90 + 4, -90 + (90 - a_end), bgr(CB), 7, cv2.LINE_AA)
                ang = math.radians(-90 + sd * (90 - a_end))
                tipx, tipy = 540 + math.cos(ang) * R, 1250 + math.sin(ang) * R
                if p > 0.1: cv2.fillPoly(f, [np.array([(tipx - 18, tipy - 10), (tipx + 18, tipy - 10), (tipx, tipy + 18)], np.int32)], bgr(CB), cv2.LINE_AA)
        # crossed scaffold card
        card(f, 640, 560, 1010, 820, SNOW)
        for k in range(4): cv2.line(f, (690 + k * 80, 600), (690 + k * 80, 780), bgr(LI), 8)
        cv2.line(f, (690, 600), (930, 600), bgr(LI), 8)
        q = ease((lt - 1.4) / 0.4)
        if q > 0:
            cv2.line(f, (670, 590), (int(lerp(670, 990, q)), int(lerp(590, 800, q))), bgr(RED), 14, cv2.LINE_AA)
        text(f, "No frame.", 70, 220, "space-grotesk-700", 150, TX, lt)
        text(f, "Just a dome.", 70, 380, "space-grotesk-700", 150, CB, lt, 0.2)
        chrome(f, "03", "structure")
    elif i == 3:
        # cross-section
        cv2.rectangle(f, (0, 1100), (W, H), bgr(SNOW2), -1)
        cv2.ellipse(f, (420, 1100), (340, 340), 0, 180, 360, bgr(SNOW), -1, cv2.LINE_AA)
        cv2.ellipse(f, (420, 1100), (340, 340), 0, 180, 360, bgr("#c7cce0"), 6, cv2.LINE_AA)
        cv2.ellipse(f, (420, 1100), (290, 290), 0, 180, 360, bgr("#fff1e8"), -1, cv2.LINE_AA)
        NO.rect(f, 160, 1040, 640, 1100, "#e7e9f5")  # sleeping platform
        # tunnel lower
        NO.rect(f, 640, 1130, 1080, 1260, SNOW); NO.rect(f, 600, 1100, 700, 1260, "#2a2f45")
        NO.rect(f, 700, 1150, 1080, 1240, "#2a2f45")
        person(f, 380, 1040, 0.8, t, warm=0.6)
        for k in range(10):
            q = (lt * 0.5 + k / 10) % 1
            x = lerp(1060, 720, q); y = 1195 + math.sin(q * 9 + k) * 18
            cv2.circle(f, (int(x), int(y)), 12, bgr("#9fb4ff"), -1, cv2.LINE_AA)
        cv2.arrowedLine(f, (900, 980), (900, 1120), bgr(CB), 8, cv2.LINE_AA, tipLength=0.2)
        paste(f, text_img("cold air sinks", "inter-600", 40, CB), 900, 920, ease((lt - 0.8) / 0.4), "ct")
        text(f, "Low door.", 70, 220, "space-grotesk-700", 150, TX, lt)
        text(f, "Cold stays out.", 70, 380, "space-grotesk-700", 130, CB, lt, 0.2)
        chrome(f, "04", "cross-section")
    elif i == 4:
        # magnified snow block with air bubbles
        card(f, 90, 640, 990, 1360, SNOW)
        rng = np.random.default_rng(2)
        for k in range(70):
            x, y = rng.uniform(140, 940), rng.uniform(690, 1310); r = rng.uniform(10, 34)
            cv2.circle(f, (int(x), int(y + math.sin(t + k) * 4)), int(r), bgr("#dfe6ff"), -1, cv2.LINE_AA)
            cv2.circle(f, (int(x), int(y + math.sin(t + k) * 4)), int(r), bgr("#b9c4f5"), 2, cv2.LINE_AA)
        if lt > 2.6:
            person(f, 540, 1200, 1.1, t, warm=ease((lt - 2.6) / 0.6))
        paste(f, text_img("×100 zoom", "space-grotesk-500", 34, MU), 120, 600)
        text(f, "Trapped air", 70, 220, "space-grotesk-700", 150, TX, lt)
        text(f, "= insulation", 70, 380, "space-grotesk-700", 150, CB, lt, 0.2)
        chrome(f, "05", "material")
    else:
        for k, (lab, val, col, x0) in enumerate((("OUTSIDE", -40, CB, 70), ("INSIDE", 2, RED, 560))):
            card(f, x0, 620, x0 + 450, 1180, SNOW)
            paste(f, text_img(lab, "space-grotesk-700", 46, MU), x0 + 40, 660)
            q = ease((lt - k * 1.4) / 1.0)
            v = int(round(val * q)) if k == 0 else int(round(lerp(-40, val, q)))
            if q > 0:
                paste(f, text_img(f"{v:+d}°", "space-grotesk-700", 170, col), x0 + 40, 760)
            paste(f, text_img("°C", "inter-600", 40, LI), x0 + 40, 1100)
        igloo(f, 540, 1500, 150, 99, t)
        text(f, "Snow house.", 70, 220, "space-grotesk-700", 150, TX, lt)
        text(f, "Warm inside.", 70, 380, "space-grotesk-700", 150, CB, lt, 0.2)
        if lt > dur - 1.8:
            NO.rect(f, 200, 1700, 880, 1800, CB, 50)
            paste(f, text_img("Follow for the next build", "inter-600", 46, SNOW), 540, 1724, ease((lt - dur + 1.8) / 0.4), "ct")
        chrome(f, "06", "result")
    captions(f, t, tl, LINES, CAP, skip=(0,))
    return f

run(D, tl, frame, "igloo_blue", "icy", 92, [(tl.starts[2] + 1.4, "pop"), (tl.starts[5] + 0.2, "ding"), (tl.starts[5] + 1.6, "ding")])
