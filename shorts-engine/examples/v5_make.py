import sys; sys.path.insert(0, "/home/claude/shorts")
from lib import *
D = "/home/claude/shorts/v5"
LINES = ["What if the Earth suddenly stopped spinning?",
         "Right now, at the equator, you're moving almost seventeen hundred kilometers an hour.",
         "Stop the planet, and everything not tied down keeps flying east.",
         "The oceans would slosh over the continents in giant waves.",
         "And one day would last a whole year: six months of sunlight, then six months of night.",
         "Relax. Earth is slowing down, but only by a couple of milliseconds per century."]
tl = Timeline(D)
WH, INK, RED, OFF = "#FFFFFF", "#1C1410", "#D8000F", "#F5F2EF"
NO = Ink(); OL = Ink(INK, 6)
CAP = dict(font="libre-baskerville-700", size=70, col=INK, hi=RED, plate=OFF, y=1530, outline=INK, ow=5, radius=0)

def tilt_text(f, s, x, y, size, col, ang, lt=1.0, delay=0.0, fname="shrikhand-400"):
    p = ease((lt - delay) / 0.35)
    if p <= 0: return
    img = text_img(s, fname, size, col)
    h, w = img.shape[:2]; pad = int(max(h, w) * 0.3)
    big = np.zeros((h + pad * 2, w + pad * 2, 4), np.uint8); big[pad:pad + h, pad:pad + w] = img
    M = cv2.getRotationMatrix2D((big.shape[1] / 2, big.shape[0] / 2), ang, back(p))
    big = cv2.warpAffine(big, M, (big.shape[1], big.shape[0]))
    paste(f, big, x - pad, y - pad, min(1, p * 2))

def chrome(f, num, label, dark=False):
    c = OFF if dark else INK
    paste(f, text_img(f"NO. {num}", "space-grotesk-700", 30, c, 0.12), 60, 70)
    paste(f, text_img(label.upper(), "space-grotesk-700", 30, c, 0.12), W - 60, 70, 1, "rt")
    cv2.line(f, (60, 120), (W - 60, 120), bgr(c), 3)

def earth(f, x, y, r, t, spin=1.0, face_on=True, mood="smile"):
    NO.circle(f, x, y, r + 8, INK); NO.circle(f, x, y, r, RED)
    rng = np.random.default_rng(9)
    for k in range(5):
        a = rng.uniform(0, 6.28) + t * spin
        cx = math.sin(a) * r * 0.6; vis = math.cos(a)
        if vis > 0:
            cv2.ellipse(f, (int(x + cx), int(y + rng.uniform(-0.5, 0.5) * r)), (int(r * 0.22 * vis + 4), int(r * 0.18)), 0, 0, 360, bgr(INK), -1, cv2.LINE_AA)
    if face_on:
        NO.ellipse(f, x, y + r * 0.05, r * 0.42, r * 0.3, OFF)
        face(f, x, y, r / 80, eye=INK, mouth=mood, blink=blink_at(t, 5), t=t)

def frame(t):
    i, lt, dur = tl.which(t)
    f = np.zeros((H, W, 3), np.uint8); f[:] = bgr(WH)
    if i == 0:
        f[:] = bgr(OFF)
        stop = lt > 1.6
        spin = 6.0 if not stop else 0.0
        jitter = math.sin(t * 50) * 10 if 1.6 < lt < 2.0 else 0
        earth(f, 540 + jitter, 1050, 300, t if not stop else 1.6 + tl.sc[0][0], spin=spin if not stop else 0, mood="o" if stop else "smile")
        if not stop:
            for k in range(6):
                a = math.radians(200 + k * 12 + (t * 300) % 40)
                cv2.ellipse(f, (540, 1050), (360 + k * 14, 360 + k * 14), 0, math.degrees(a), math.degrees(a) + 30, bgr(INK), 6, cv2.LINE_AA)
        tilt_text(f, "What if", 60, 200, 150, INK, 6, lt)
        tilt_text(f, "it STOPPED?", 40, 360, 160, RED, 6, lt, 0.2)
        if stop:
            NO.poly(f, [(820 + 110 * math.cos(math.radians(22.5 + 45 * k)), 700 + 110 * math.sin(math.radians(22.5 + 45 * k))) for k in range(8)], RED)
            paste(f, text_img("STOP", "space-grotesk-700", 70, WH), 820, 668, 1, "ct")
        chrome(f, "01", "planet earth")
    elif i == 1:
        earth(f, 540, 1120, 260, t, spin=1.5)
        # gauge
        cx, cy = 540, 760
        cv2.ellipse(f, (cx, cy), (230, 230), 0, 180, 360, bgr(INK), 22, cv2.LINE_AA)
        v = ease((lt - 0.3) / 2.2)
        a = math.radians(180 + 175 * v)
        cv2.line(f, (cx, cy), (int(cx + math.cos(a) * 200), int(cy + math.sin(a) * 200)), bgr(RED), 14, cv2.LINE_AA)
        NO.circle(f, cx, cy, 24, INK)
        tilt_text(f, f"{int(1670 * v):,}", 120, 180, 210, RED, 3, lt)
        paste(f, text_img("KM / HOUR AT THE EQUATOR", "space-grotesk-700", 40, INK, 0.08), 540, 470, ease(lt / 0.5), "ct")
        chrome(f, "02", "your speed")
    elif i == 2:
        f[:] = bgr(OFF)
        cv2.rectangle(f, (0, 1350), (W, H), bgr(INK), -1)
        for k, (kind, x0, y0) in enumerate((("house", 160, 1240), ("tree", 420, 1260), ("cow", 640, 1280), ("car", 260, 1000), ("person", 760, 1000), ("house", 860, 1250))):
            dx = 750 * eio((lt - 0.5 - k * 0.15) / 3.4); rot = dx * 0.08
            x, y = x0 + dx, y0 - 160 * math.sin(min(1, dx / 750) * math.pi)
            for m in range(4):
                cv2.line(f, (int(x - 80 - m * 40), int(y - 40 + m * 25)), (int(x - 40 - m * 40), int(y - 40 + m * 25)), bgr(INK), 5, cv2.LINE_AA)
            if kind == "house":
                OL.rect(f, x - 60, y - 60, x + 60, y + 40, WH); OL.poly(f, [(x - 75, y - 60), (x + 75, y - 60), (x, y - 130)], RED)
            elif kind == "tree":
                OL.rect(f, x - 14, y - 40, x + 14, y + 40, INK); OL.circle(f, x, y - 80, 65, RED)
            elif kind == "cow":
                OL.ellipse(f, x, y, 80, 48, WH); OL.circle(f, x + 75, y - 30, 32, WH); cv2.circle(f, (int(x - 20), int(y)), 18, bgr(INK), -1)
            elif kind == "car":
                OL.rect(f, x - 85, y - 30, x + 85, y + 25, RED, 16); OL.circle(f, x - 45, y + 30, 22, INK); OL.circle(f, x + 45, y + 30, 22, INK)
            else:
                OL.circle(f, x, y - 70, 40, WH); face(f, x, y - 70, 0.7, mouth="o"); OL.rect(f, x - 30, y - 30, x + 30, y + 60, RED, 14)
        tilt_text(f, "WHOOSH", 70, 220, 165, RED, -4, lt)
        paste(f, text_img("EVERYTHING FLIES EAST >>", "space-grotesk-700", 44, INK, 0.08), 80, 520, ease((lt - 0.4) / 0.4))
        chrome(f, "03", "momentum")
    elif i == 3:
        # continent + wave
        OL.poly(f, [(0, 1250), (200, 1150), (420, 1180), (640, 1100), (W, 1200), (W, H), (0, H)], OFF)
        for k, x in enumerate((200, 420, 640)):
            NO.rect(f, x - 30, 1080 - k * 20, x + 30, 1160, RED)
        p = eio((lt - 0.2) / 2.5)
        cx = lerp(-300, 700, p); hh = 700
        pts = [(cx - 600, 1500)]
        for u in np.linspace(0, 1, 40):
            pts.append((cx - 600 + u * 900, 1500 - hh * math.sin(u * math.pi * 0.85) ** 1.5))
        pts += [(cx + 330, 1500 - hh * 0.5), (cx + 200, 1500 - hh * 0.7)]
        NO.poly(f, pts + [(cx + 300, H), (cx - 600, H)], INK)
        cv2.polylines(f, [np.array(pts, np.int32)], False, bgr(RED), 10, cv2.LINE_AA)
        cv2.ellipse(f, (int(cx + 220), int(1500 - hh * 0.62)), (90, 90), 0, 200, 450, bgr(WH), 14, cv2.LINE_AA)
        tilt_text(f, "Giant waves!", 60, 220, 128, RED, 4, lt)
        chrome(f, "04", "oceans")
    elif i == 4:
        # split day / night
        cv2.rectangle(f, (W // 2, 0), (W, H), bgr(INK), -1)
        cv2.rectangle(f, (0, 0), (W // 2, H), bgr(OFF), -1)
        rng = np.random.default_rng(3)
        for k in range(40): cv2.circle(f, (int(rng.uniform(W // 2 + 20, W)), int(rng.uniform(150, 1400))), 3, bgr(OFF), -1, cv2.LINE_AA)
        r = 150 + 10 * math.sin(t * 3)
        for k in range(12):
            a = k / 12 * 2 * math.pi + t * 0.5
            cv2.line(f, (int(270 + math.cos(a) * (r + 20)), int(800 + math.sin(a) * (r + 20))), (int(270 + math.cos(a) * (r + 70)), int(800 + math.sin(a) * (r + 70))), bgr(RED), 12, cv2.LINE_AA)
        NO.circle(f, 270, 800, r, RED); face(f, 270, 790, 1.6, eye=OFF, blink=blink_at(t, 2))
        NO.circle(f, 810, 800, 120, OFF); NO.circle(f, 860, 760, 110, INK)
        paste(f, text_img("6 MONTHS", "shrikhand-400", 76, INK), 270, 1080, ease((lt - 1.0) / 0.4), "ct")
        paste(f, text_img("6 MONTHS", "shrikhand-400", 76, OFF), 810, 1080, ease((lt - 2.8) / 0.4), "ct")
        paste(f, text_img("DAY", "space-grotesk-700", 50, RED, 0.1), 270, 1210, ease((lt - 1.0) / 0.4), "ct")
        paste(f, text_img("NIGHT", "space-grotesk-700", 50, OFF, 0.1), 810, 1210, ease((lt - 2.8) / 0.4), "ct")
        tilt_text(f, "1 day =", 60, 200, 130, INK, 3, lt)
        tilt_text(f, "1 year", 600, 200, 130, RED, 3, lt, 0.3)
        chrome(f, "05", "sunlight")
    else:
        f[:] = bgr(OFF)
        earth(f, 540, 1080, 280, t, spin=0.6)
        # tiny clock + text
        NO.circle(f, 860, 760, 90, WH); cv2.circle(f, (860, 760), 90, bgr(INK), 8, cv2.LINE_AA)
        a = t * 0.3
        cv2.line(f, (860, 760), (int(860 + math.sin(a) * 60), int(760 - math.cos(a) * 60)), bgr(RED), 8, cv2.LINE_AA)
        tilt_text(f, "Relax.", 60, 200, 200, INK, 5, lt)
        tilt_text(f, "+2 ms", 60, 420, 150, RED, 5, lt, 1.5)
        paste(f, text_img("PER CENTURY", "space-grotesk-700", 44, INK, 0.1), 80, 620, ease((lt - 1.8) / 0.4))
        if lt > dur - 1.9:
            NO.rect(f, 160, 1700, 920, 1800, RED)
            paste(f, text_img("FOLLOW FOR MORE WHAT IFs", "space-grotesk-700", 44, WH, 0.06), 540, 1726, ease((lt - dur + 1.9) / 0.4), "ct")
        chrome(f, "06", "the real news")
    captions(f, t, tl, LINES, CAP, skip=(0,))
    return f

run(D, tl, frame, "earth_stops_poster", "drama", 96, [(tl.starts[0] + 1.6 - 0.12, "boom"), (tl.starts[2] + 0.4, "splash"), (tl.starts[3] + 0.6, "splash")])
