import sys; sys.path.insert(0, "/home/claude/shorts")
from lib import *
D = "/home/claude/shorts/v8"
LINES = ["Why do we sneeze?",
         "Your nose is lined with tiny hairs and nerves that guard the way in.",
         "When dust, pollen or pepper tickles them, they send an alarm to your brain.",
         "Your brain fires back: a deep breath in, eyes shut, and then... achoo!",
         "Air blasts out of your nose and mouth, and shoots the intruders away.",
         "So a sneeze is your body's built-in dust cleaner. Bless you!"]
tl = Timeline(D)
CR, INK, WH, CO, LI, LA, SK, VI, YE, PE, MI = "#F5F5F0", "#1A1A1A", "#FFFFFF", "#E85D4E", "#C4D94E", "#C5B5E0", "#8BB4F7", "#A06CE8", "#F2D160", "#F5B895", "#A8E6CF"
P = Ink(INK, 5, INK, (8, 8)); P2 = Ink(INK, 4)
CAP = dict(font="space-grotesk-700", size=74, col=INK, hi=VI, plate=WH, y=1520, outline=INK, ow=5, shadow=INK, sh=(8, 8), radius=60)

def pill(f, x, y, s, col, font="space-grotesk-700", size=56, tcol=INK, lt=1.0, delay=0.0, anchor="lt"):
    p = ease((lt - delay) / 0.35)
    if p <= 0: return
    img = text_img(s, font, size, tcol)
    w, h = img.shape[1] + 70, img.shape[0] + 34
    if anchor == "ct": x -= w // 2
    yy = y + (1 - p) * 40
    P.rect(f, x, yy, x + w, yy + h, col, h // 2)
    paste(f, img, x + 35, yy + 14, p)

def chrome(f, num):
    for k in range(6):
        P2.rect(f, 70 + k * 50, 80, 70 + k * 50 + 34, 100, VI if k <= num else WH, 10)

def head(f, x, y, s, t, mood="smile", eyes_closed=False, nose_pulse=0.0, tilt=0.0):
    P.rect(f, x - 170 * s, y - 230 * s, x + 170 * s, y + 230 * s, SK, int(170 * s))
    for sx in (-1, 1):
        ex, ey = int(x + sx * 62 * s), int(y - 70 * s)
        if eyes_closed: cv2.ellipse(f, (ex, ey), (int(26 * s), int(14 * s)), 0, 200, 340, bgr(INK), max(3, int(8 * s)), cv2.LINE_AA)
        else:
            P2.circle(f, ex, ey, 30 * s, WH); cv2.circle(f, (ex + int(6 * s), ey), int(15 * s), bgr(INK), -1, cv2.LINE_AA)
    ns = 1 + 0.12 * nose_pulse
    P.ellipse(f, x, y + 20 * s, 60 * s * ns, 75 * s * ns, PE)
    for sx in (-1, 1): cv2.ellipse(f, (int(x + sx * 24 * s), int(y + 62 * s)), (int(12 * s), int(8 * s)), 0, 0, 360, bgr("#b9765a"), -1, cv2.LINE_AA)
    my = int(y + 140 * s)
    if mood == "smile": cv2.ellipse(f, (int(x), my), (int(40 * s), int(22 * s)), 0, 10, 170, bgr(INK), max(3, int(7 * s)), cv2.LINE_AA)
    elif mood == "o": P2.ellipse(f, x, my + 8 * s, 30 * s, 36 * s, INK)
    else: P2.ellipse(f, x, my + 8 * s, 70 * s, 40 * s, INK)

def bg(f, t, col=CR):
    f[:] = bgr(col)
    for k in range(8):
        y = 300 + k * 200
        cv2.line(f, (0, y), (W, y), bgr("#ebebe3"), 2)

rng = np.random.default_rng(11)
DUST = rng.uniform(0, 1, (40, 4))

def frame(t):
    i, lt, dur = tl.which(t)
    f = np.zeros((H, W, 3), np.uint8); bg(f, t)
    if i == 0:
        head(f, 540, 1080, 1.4, t, mood="o", nose_pulse=abs(math.sin(t * 6)))
        for x, y, c, s in DUST[:18]:
            xx = 200 + x * 680 + math.sin(t * 2 + s * 9) * 30; yy = 700 + y * 300 + math.cos(t * 2 + s * 9) * 30
            P2.circle(f, xx, yy, 10 + s * 12, [YE, LI, PE, LA][int(c * 4)])
        text(f, "Why do we", 70, 180, "bodoni-moda-900", 140, INK, lt)
        pill(f, 60, 360, "SNEEZE?", CO, "bodoni-moda-900", 130, WH, lt, 0.2)
    elif i == 1:
        # nostril cross-section
        P.rect(f, 160, 560, 920, 1360, PE, 380)
        cv2.ellipse(f, (540, 960), (250, 330), 0, 0, 360, bgr("#e79c79"), -1, cv2.LINE_AA)
        for k in range(14):
            a = k / 14 * 2 * math.pi; r0 = 250
            x0, y0 = 540 + math.cos(a) * r0 * 0.98, 960 + math.sin(a) * 330 * 0.98
            sw = math.sin(t * 6 + k) * 0.25
            x1, y1 = 540 + math.cos(a + sw) * r0 * 0.6, 960 + math.sin(a + sw) * 330 * 0.6
            cv2.line(f, (int(x0), int(y0)), (int(x1), int(y1)), bgr("#6b3b28"), 7, cv2.LINE_AA)
        for k in range(8):
            a = k / 8 * 2 * math.pi + 0.2
            P2.circle(f, 540 + math.cos(a) * 285, 960 + math.sin(a) * 375, 18, YE if math.sin(t * 5 + k) > 0 else WH)
        pill(f, 60, 200, "tiny hairs", LI, "bodoni-moda-900", 90, INK, lt)
        pill(f, 300, 350, "+ nerves", YE, "bodoni-moda-900", 90, INK, lt, 0.5)
        chrome(f, 1)
    elif i == 2:
        # brain top, nose bottom
        P.rect(f, 300, 300, 780, 620, LA, 160)
        for k in range(4): cv2.ellipse(f, (380 + k * 110, 460), (50, 90), 0, 200, 340, bgr(VI), 8, cv2.LINE_AA)
        alarm = lt > 2.0
        if alarm and int(lt * 6) % 2 == 0: pill(f, 540, 200, "ALERT!", CO, "space-grotesk-700", 70, WH, 1, 0, "ct")
        head(f, 540, 1150, 0.9, t, mood="o" if alarm else "smile", nose_pulse=1 if alarm else 0)
        for k, (x, y, c, s) in enumerate(DUST[:16]):
            q = min(1, max(0, (lt - k * 0.08) / 1.8))
            xx = lerp(-60 + x * 300, 540 + (x - 0.5) * 60, ease(q)); yy = lerp(900 + y * 500, 1170, ease(q))
            P2.circle(f, xx, yy, 9 + s * 10, [YE, LI, PE, CO][int(c * 4)])
        if lt > 1.6:
            p = ease((lt - 1.6) / 0.6)
            pts = [(540, 1040), (580, 900), (500, 800), (560, 700), (540, 630)]
            cv2.polylines(f, [np.array(pts[:max(2, int(5 * p))])], False, bgr(YE), 20, cv2.LINE_AA)
            cv2.polylines(f, [np.array(pts[:max(2, int(5 * p))])], False, bgr(INK), 5, cv2.LINE_AA)
        pill(f, 60, 680, "dust", YE, lt=lt); pill(f, 60, 790, "pollen", LI, lt=lt, delay=0.3); pill(f, 60, 900, "pepper", CO, tcol=WH, lt=lt, delay=0.6)
        chrome(f, 2)
    elif i == 3:
        ph = lt / dur
        inhale = ease(lt / 2.0)
        s = 1.2 + 0.12 * inhale if lt < 3.6 else 1.15
        closed = lt > 1.8
        head(f, 540, 1050 - 40 * inhale, s, t, mood="o" if lt < 3.6 else "big", eyes_closed=closed, nose_pulse=inhale, tilt=0)
        if lt < 3.6:
            pill(f, 70, 200, "ah...", WH, "bodoni-moda-900", 110, INK, lt, 0.3)
            if lt > 1.8: pill(f, 450, 200, "ah...", WH, "bodoni-moda-900", 110, INK, lt, 1.8)
        else:
            sc = back((lt - 3.6) / 0.3)
            img = text_img("ACHOO!", "bodoni-moda-900", 210, CO)
            paste(f, img, 540, 220, 1, "ct", scale=max(0.1, sc))
        chrome(f, 3)
    elif i == 4:
        head(f, 300, 1050, 0.95, t, mood="big", eyes_closed=True)
        for k, (x, y, c, s) in enumerate(DUST):
            q = ((lt * 1.3 + x) % 1)
            xx = 380 + q * 900; yy = 1080 + (y - 0.5) * 420 * q
            cv2.line(f, (int(xx - 80), int(yy)), (int(xx - 20), int(yy)), bgr(INK), 4, cv2.LINE_AA)
            P2.circle(f, xx, yy, 8 + s * 10, [YE, LI, PE, CO][int(c * 4)])
        pill(f, 60, 220, "WHOOSH!", SK, "bodoni-moda-900", 120, INK, lt)
        chrome(f, 4)
    else:
        head(f, 540, 1080, 1.25, t, mood="smile", nose_pulse=0.2 * math.sin(t * 3))
        # sparkles
        for k in range(8):
            a = k / 8 * 2 * math.pi + t * 0.6
            x, y = 540 + math.cos(a) * 380, 1080 + math.sin(a) * 430
            cv2.line(f, (int(x - 18), int(y)), (int(x + 18), int(y)), bgr(YE), 8, cv2.LINE_AA); cv2.line(f, (int(x), int(y - 18)), (int(x), int(y + 18)), bgr(YE), 8, cv2.LINE_AA)
        pill(f, 60, 200, "dust cleaner", MI, "bodoni-moda-900", 110, INK, lt)
        pill(f, 60, 380, "Bless you!", CO, "bodoni-moda-900", 110, WH, lt, 1.6)
        if lt > dur - 1.8: pill(f, 540, 1700, "follow for a new why every day", LA, "space-grotesk-700", 44, INK, lt, dur - 1.8, "ct")
        chrome(f, 5)
    captions(f, t, tl, LINES, CAP, skip=(0,))
    return f

run(D, tl, frame, "sneeze_capsule", "bubbly", 120, [(tl.starts[2] + 2.0, "ding"), (tl.sc[3][0] + 3.6, "boom"), (tl.starts[4], "splash")])
