import sys; sys.path.insert(0, "/home/claude/shorts")
from lib import *
D = "/home/claude/shorts/v6"
LINES = ["How do you build a submarine?",
         "Step one: a sealed metal tube. But... it just floats.",
         "So add ballast tanks. Let water in, and down you go!",
         "Deeper down, the water pressure starts crushing it! So make the hull thick, round steel.",
         "To come back up, blow compressed air into the tanks and push the water out.",
         "Add a periscope, and congrats, you built a submarine!"]
tl = Timeline(D)
BK, WH, OW, PK, BL, GN, YE, CM = "#000000", "#FFFFFF", "#FFFDF5", "#FE90E8", "#C0F7FE", "#99E885", "#F7CB46", "#FFDC8B"
SEA, DEEP = "#5ec8e0", "#1f5f8a"
B = Ink(BK, 6, BK, (14, 14))
B2 = Ink(BK, 5)
CAP = dict(font="inter-900", size=66, col=BK, hi="#e0249a", plate=WH, y=1530, outline=BK, ow=6, shadow=BK, sh=(12, 12), upper=True)

def chrome(f, num, label, col=YE):
    B.rect(f, 60, 70, 300, 140, col)
    paste(f, text_img(f"STEP {num}", "space-grotesk-700", 44, BK, 0.06), 180, 80, 1, "ct")
    B.rect(f, 330, 70, 330 + text_img(label.upper(), "space-grotesk-700", 34, BK, 0.06).shape[1] + 50, 140, WH)
    paste(f, text_img(label.upper(), "space-grotesk-700", 34, BK, 0.06), 355, 88)

def title(f, s, x, y, col, lt, delay=0.0, size=120, box=None):
    p = ease((lt - delay) / 0.35)
    if p <= 0: return
    img = text_img(s, "inter-900", size, BK, -0.02)
    if box:
        B.rect(f, x - 26, y + (1 - p) * 40 - 14, x + img.shape[1] + 26, y + (1 - p) * 40 + img.shape[0] + 14, box)
    paste(f, img, x, y + (1 - p) * 40, p)

def sub(f, x, y, s, t, fill=0.0, dent=0.0, thick=False, peri=0.0, mood="smile"):
    L, Hh = 300 * s, 120 * s
    sq = 1 - 0.25 * dent
    hh = Hh * sq
    if thick: B.rect(f, x - L - 14 * s, y - hh - 14 * s, x + L + 14 * s, y + hh + 14 * s, "#8a8a8a", int(hh + 14 * s))
    B.rect(f, x - L, y - hh, x + L, y + hh, YE, int(hh))
    # tanks (bottom) cutaway
    for side in (-1, 1):
        tx0, tx1 = x + side * L * 0.15, x + side * L * 0.7
        a, b = min(tx0, tx1), max(tx0, tx1)
        B2.rect(f, a, y + hh * 0.05, b, y + hh * 0.85, OW, 10)
        if fill > 0: cv2.rectangle(f, (int(a + 5), int(y + hh * 0.85 - (hh * 0.8 - 5) * fill)), (int(b - 5), int(y + hh * 0.85 - 5)), bgr(SEA), -1)
    # tower + periscope
    B.rect(f, x - 70 * s, y - hh - 90 * s, x + 70 * s, y - hh + 10, YE, 16)
    if peri > 0:
        ph = 160 * s * ease(peri)
        B2.rect(f, x - 12 * s, y - hh - 90 * s - ph, x + 12 * s, y - hh - 90 * s, "#8a8a8a")
        B2.rect(f, x - 12 * s, y - hh - 90 * s - ph - 10, x + 50 * s, y - hh - 90 * s - ph + 25 * s, "#8a8a8a")
    # portholes
    for k in (-0.5, 0.0):
        B2.circle(f, x + k * L, y - hh * 0.35, 26 * s, BL)
    # face front
    B2.circle(f, x + L * 0.62, y - hh * 0.25, 52 * s, OW)
    face(f, x + L * 0.62, y - hh * 0.3, 0.9 * s, mouth=mood, blink=blink_at(t, 6), t=t)
    # propeller
    for k in range(3):
        a = t * 12 + k * 2.09
        cv2.ellipse(f, (int(x - L - 20 * s), int(y)), (int(14 * s), int(50 * s * abs(math.cos(a)) + 6)), 0, 0, 360, bgr(PK), -1, cv2.LINE_AA)
    B2.rect(f, x - L - 30 * s, y - 10 * s, x - L, y + 10 * s, BK)

def bubbles(f, x, y, t, n=8, spread=60, col=WH):
    for k in range(n):
        q = (t * 0.8 + k / n) % 1
        cv2.circle(f, (int(x + math.sin(k * 3 + t * 3) * spread * 0.4), int(y - q * 300)), int(8 + k % 3 * 5), bgr(col), 3, cv2.LINE_AA)

def seabg(f, top, t, col=SEA):
    f[:] = bgr(OW)
    cv2.rectangle(f, (0, int(top)), (W, H), bgr(col), -1)
    pts = [(x, int(top + math.sin(x / 60 + t * 3) * 10)) for x in range(0, W + 20, 20)]
    cv2.polylines(f, [np.array(pts)], False, bgr(BK), 6, cv2.LINE_AA)

def frame(t):
    i, lt, dur = tl.which(t)
    f = np.zeros((H, W, 3), np.uint8)
    if i == 0:
        seabg(f, 1150, t)
        sub(f, 540, 1300 + math.sin(t * 2) * 15, 1.2, t, fill=0.5, peri=1)
        bubbles(f, 860, 1300, t)
        title(f, "HOW TO", 70, 230, BK, lt, 0, 150, PK)
        title(f, "BUILD A", 70, 440, BK, lt, 0.15, 150, BL)
        title(f, "SUBMARINE?", 70, 650, BK, lt, 0.3, 150, GN)
    elif i == 1:
        seabg(f, 1000, t)
        bob = math.sin(t * 2.5) * 14
        sub(f, 540, 990 + bob, 1.1, t, fill=0, mood="flat" if lt > 1.8 else "smile")
        title(f, "SEALED TUBE", 70, 260, BK, lt, 0, 120, YE)
        if lt > 1.8: title(f, "IT FLOATS :(", 70, 440, BK, lt, 1.8, 120, PK)
        chrome(f, "1", "the hull")
    elif i == 2:
        seabg(f, 700, t)
        fill = eio((lt - 0.3) / 1.6)
        y = lerp(760, 1220, eio((lt - 1.0) / 2.0))
        sub(f, 540, y, 1.1, t, fill=fill, mood="o" if lt > 1 else "smile")
        bubbles(f, 820, y - 100, t, 6)
        title(f, "BALLAST TANKS", 70, 260, BK, lt, 0, 110, BL)
        if lt > 1.2: title(f, "DOWN WE GO!", 70, 440, BK, lt, 1.2, 110, GN)
        chrome(f, "2", "sink")
    elif i == 3:
        seabg(f, 0, t, DEEP)
        fixed = lt > 2.4
        dent = 0 if fixed else min(1, max(0, (lt - 0.4) / 1.4)) * (0.6 + 0.2 * math.sin(t * 20))
        sub(f, 540, 1050, 1.0, t, fill=1, dent=dent, thick=fixed, mood="o" if not fixed else "smile")
        for k in range(10):
            a = k / 10 * 2 * math.pi; r0 = 520 - 60 * abs(math.sin(lt * 3 + k))
            cv2.arrowedLine(f, (int(540 + math.cos(a) * r0), int(1050 + math.sin(a) * r0 * 0.7)), (int(540 + math.cos(a) * 380), int(1050 + math.sin(a) * 380 * 0.62)), bgr(WH), 10, cv2.LINE_AA, tipLength=0.3)
        # depth meter
        B.rect(f, 820, 520, 1010, 640, WH)
        d = int(min(300, lt * 140))
        paste(f, text_img(f"{d}m", "space-grotesk-700", 40, BK), 915, 548, 1, "ct")
        title(f, "PRESSURE!", 70, 260, BK, lt, 0, 130, PK)
        if fixed: title(f, "THICK ROUND STEEL", 70, 1290, BK, lt, 2.4, 80, YE)
        chrome(f, "3", "go deeper")
    elif i == 4:
        seabg(f, 500, t)
        fill = 1 - eio((lt - 0.6) / 1.8)
        y = lerp(1250, 800, eio((lt - 1.2) / 2.0))
        sub(f, 540, y, 1.1, t, fill=fill)
        if lt > 0.6:
            for side in (-1, 1): bubbles(f, 540 + side * 140, y + 60, t * 2, 7, 40)
        B.rect(f, 820, 280, 1010, 420, WH); paste(f, text_img("AIR", "inter-900", 70, BK), 915, 305, 1, "ct")
        title(f, "BLOW AIR IN", 70, 280, BK, lt, 0, 110, GN)
        chrome(f, "4", "surface")
    else:
        seabg(f, 1100, t)
        sub(f, 540, 1150 + math.sin(t * 2) * 10, 1.15, t, fill=0.3, peri=(lt - 0.5) / 0.6)
        rng = np.random.default_rng(7)
        if lt > 1.5:
            for k in range(30):
                q = (lt - 1.5) * 0.6 + rng.uniform(0, 1)
                x = rng.uniform(0, W); y = (q * 900) % 1100
                cv2.rectangle(f, (int(x), int(y)), (int(x + 22), int(y + 22)), bgr([PK, BL, GN, YE][k % 4]), -1)
        title(f, "YOU BUILT A", 70, 280, BK, lt, 1.2, 120, WH)
        title(f, "SUBMARINE!", 70, 470, BK, lt, 1.5, 150, YE)
        if lt > dur - 1.8:
            B.rect(f, 160, 1700, 920, 1800, PK)
            paste(f, text_img("FOLLOW FOR THE NEXT BUILD", "space-grotesk-700", 44, BK, 0.04), 540, 1726, ease((lt - dur + 1.8) / 0.4), "ct")
        chrome(f, "5", "done")
    captions(f, t, tl, LINES, CAP, skip=(0,))
    return f

run(D, tl, frame, "submarine_blockframe", "march", 118, [(tl.starts[2] + 0.4, "splash"), (tl.starts[3] + 2.4, "boom"), (tl.starts[5] + 0.6, "pop"), (tl.starts[5] + 1.5, "ding")])
