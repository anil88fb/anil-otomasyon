import sys; sys.path.insert(0, "/home/claude/shorts")
from lib import *
D = "/home/claude/shorts/v3"
LINES = ["Why do your fingers get wrinkly in the bath?",
         "It's not water soaking in. It's your nerves!",
         "After about five minutes in water, your body shrinks the tiny blood vessels under your fingertips.",
         "The skin on top gets pulled down, and folds into wrinkles.",
         "Some scientists think they work like tire treads, helping you grip wet things.",
         "So your wrinkly fingers might be a built-in grip upgrade!"]
tl = Timeline(D)
CR, TQ, PK, BU, MI, LA, PE, SK, CO, TX, MU, WH = "#F5F0E6", "#7ECDC0", "#F7C8D4", "#FDE68A", "#A8E6CF", "#D4A5E8", "#FFCBA4", "#A8D8F0", "#F8635F", "#2D2D2D", "#6B6B6B", "#FFFFFF"
K = Ink(TX, 6, TX, (12, 10))
K2 = Ink(TX, 5, None)
CAP = dict(font="fredoka-700", size=86, col=TX, hi=CO, plate=WH, y=1500, outline=TX, ow=5, shadow=TX, sh=(10, 8), radius=40)

def bg(f, col, t, dots=True):
    f[:] = bgr(col)
    if dots:
        for y in range(40, H, 120):
            for x in range(40 + (y // 120 % 2) * 60, W, 120):
                cv2.circle(f, (x, y), 7, bgr(WH), -1, cv2.LINE_AA)

def daisy(f, x, y, s, t):
    for k in range(8):
        a = k / 8 * 2 * math.pi + t * 0.5
        K2.ellipse(f, x + math.cos(a) * 30 * s, y + math.sin(a) * 30 * s, 22 * s, 13 * s, WH, math.degrees(a))
    K2.circle(f, x, y, 18 * s, BU)

def chrome(f, num, label):
    K.rect(f, 60, 70, 200, 140, BU, 34)
    paste(f, text_img(num, "fredoka-700", 54, TX), 130, 76, 1, "ct")
    text(f, label, 225, 82, "quicksand-700", 44, TX)

def hand(f, x, y, s, wr, t, wave=0.0, face_on=True):
    """palm centered at (x,y). wr 0..1 wrinkle amount"""
    ang = math.sin(t * 3) * 6 * wave
    # fingers
    for k, (dx, L) in enumerate(((-75, 210), (-25, 240), (25, 230), (75, 190))):
        fx = x + dx * s; top = y - (110 + L) * s + math.sin(t * 4 + k) * 6 * wave
        K.rect(f, fx - 22 * s, top, fx + 22 * s, y - 60 * s, PE, int(22 * s))
        for j in range(3):
            yy = top + (22 + j * 15) * s
            if wr > 0.05:
                amp = 5 * s * wr
                pts = [(int(fx - 16 * s + u * s), int(yy + math.sin(u / 4) * amp)) for u in range(0, 33, 3)]
                cv2.polylines(f, [np.array(pts)], False, bgr("#d98b6a"), max(2, int(3 * s)), cv2.LINE_AA)
    # thumb
    K.ellipse(f, x - 135 * s, y + 10 * s, 30 * s, 75 * s, PE, -35)
    K.rect(f, x - 110 * s, y - 90 * s, x + 110 * s, y + 130 * s, PE, int(60 * s))
    if face_on: face(f, x, y + 10 * s, 1.6 * s, blink=blink_at(t, 3), mouth="smile", t=t)

def drop(f, x, y, s, col=SK):
    K2.poly(f, [(x, y - 40 * s), (x + 26 * s, y), (x - 26 * s, y)], col)
    K2.circle(f, x, y + 4 * s, 27 * s, col)

def frame(t):
    i, lt, dur = tl.which(t)
    f = np.zeros((H, W, 3), np.uint8)
    if i == 0:
        bg(f, SK, t)
        # tub
        K.rect(f, 80, 1060, 1000, 1400, WH, 90)
        cv2.rectangle(f, (140, 1060), (940, 1110), bgr("#9fd5ea"), -1)
        for k in range(14):
            bx = 140 + (k * 61) % 800; by = 1060 + math.sin(t * 2 + k) * 10
            K2.circle(f, bx, by, 26 + (k % 3) * 10, WH)
        K2.rect(f, 180, 1400, 230, 1460, TX); K2.rect(f, 850, 1400, 900, 1460, TX)
        up = ease((lt - 0.3) / 0.6)
        hand(f, 560, int(lerp(1300, 960, up)), 1.25, wr=min(1, lt / 1.5), t=t, wave=1)
        # duck
        dx = 250 + math.sin(t) * 20
        K.ellipse(f, dx, 1030, 70, 45, BU); K.circle(f, dx + 45, 975, 35, BU); K2.poly(f, [(dx + 75, 975), (dx + 110, 985), (dx + 75, 995)], PE)
        cv2.circle(f, (int(dx + 55), 965), 6, bgr(TX), -1)
        text(f, "why do fingers", 70, 190, "fredoka-700", 110, TX, lt)
        K.rect(f, 60, 330, 880, 480, CO, 40); text(f, "get WRINKLY?", 95, 340, "fredoka-700", 110, WH, lt, 0.2)
        chrome(f, "1", "bath time")
    elif i == 1:
        bg(f, MI, t)
        hand(f, 540, 1150, 1.4, wr=1, t=t, face_on=True)
        for k in range(5):
            q = (lt * 0.9 + k / 5) % 1
            x = 330 + k * 110; y = lerp(500, 840, q)
            if q < 0.85: drop(f, x, y, 0.8)
            else: K2.circle(f, x, 860, 10, SK)
        if lt > 1.4:
            # nerve lightning
            p = ease((lt - 1.4) / 0.4)
            for k in range(3):
                pts = [(380 + k * 160, 1500), (420 + k * 160, 1420), (360 + k * 160, 1360), (430 + k * 160, 1280)]
                cv2.polylines(f, [np.array(pts[:max(2, int(len(pts) * p))])], False, bgr(BU), 14, cv2.LINE_AA)
                cv2.polylines(f, [np.array(pts[:max(2, int(len(pts) * p))])], False, bgr(TX), 4, cv2.LINE_AA)
        text(f, "not water...", 70, 190, "fredoka-700", 120, TX, lt)
        if lt > 1.3:
            K.rect(f, 60, 340, 740, 500, LA, 40); text(f, "NERVES!", 100, 350, "fredoka-700", 130, TX, lt, 1.3, pop=True)
        chrome(f, "2", "plot twist")
    elif i == 2:
        bg(f, PK, t)
        # fingertip cross-section
        cx, cy = 540, 1000
        K.rect(f, 180, 640, 900, 1320, PE, 300)
        cv2.ellipse(f, (cx, 1000), (300, 260), 0, 0, 360, bgr("#ffd9bf"), -1, cv2.LINE_AA)
        shrink = eio((lt - 1.2) / 2.5)
        for k in range(4):
            yy = 860 + k * 85
            w = int(lerp(30, 10, shrink))
            pts = [(x, int(yy + math.sin(x / 60 + k) * 18)) for x in range(260, 830, 15)]
            cv2.polylines(f, [np.array(pts)], False, bgr("#c2304a"), w + 8, cv2.LINE_AA)
            cv2.polylines(f, [np.array(pts)], False, bgr(CO), w, cv2.LINE_AA)
        # timer
        K.circle(f, 880, 560, 95, WH)
        a = -90 + 360 * min(1, lt / 1.5)
        cv2.ellipse(f, (880, 560), (70, 70), 0, -90, a, bgr(TQ), 22, cv2.LINE_AA)
        paste(f, text_img("5 min", "fredoka-700", 42, TX), 880, 680, 1, "ct")
        text(f, "vessels", 70, 190, "fredoka-700", 130, TX, lt)
        K.rect(f, 60, 360, 620, 510, TQ, 40); text(f, "shrink!", 100, 368, "fredoka-700", 120, TX, lt, 0.4)
        chrome(f, "3", "inside a fingertip")
    elif i == 3:
        bg(f, BU, t)
        p = eio((lt - 0.3) / 1.8)
        top = 820
        pts = [(x, int(top + math.sin(x / 45) * 55 * p)) for x in range(120, 961, 8)]
        poly = pts + [(960, 1350), (120, 1350)]
        K.poly(f, poly, PE)
        cv2.polylines(f, [np.array(pts)], False, bgr(TX), 8, cv2.LINE_AA)
        for k in range(5):
            x = 200 + k * 170; yy = 1150 - 40 * p
            cv2.line(f, (x - 30, int(yy)), (x + 30, int(yy)), bgr(CO), 14, cv2.LINE_AA)
            cv2.arrowedLine(f, (x, int(top - 160)), (x, int(top - 40 + 30 * p)), bgr(TX), 9, cv2.LINE_AA, tipLength=0.3)
        text(f, "skin gets", 70, 190, "fredoka-700", 120, TX, lt)
        K.rect(f, 60, 340, 730, 490, CO, 40); text(f, "pulled down", 95, 350, "fredoka-700", 110, WH, lt, 0.3)
        chrome(f, "4", "wrinkle time")
    elif i == 4:
        bg(f, LA, t)
        # tire
        tx, ty = 300, 900
        K.circle(f, tx, ty, 200, TX); cv2.circle(f, (tx, ty), 95, bgr("#bdbdbd"), -1, cv2.LINE_AA); cv2.circle(f, (tx, ty), 40, bgr(TX), -1, cv2.LINE_AA)
        for k in range(18):
            a = k / 18 * 2 * math.pi + lt * 1.5
            cv2.line(f, (int(tx + math.cos(a) * 150), int(ty + math.sin(a) * 150)), (int(tx + math.cos(a) * 196), int(ty + math.sin(a) * 196)), bgr("#555555"), 12, cv2.LINE_AA)
        paste(f, text_img("=", "fredoka-700", 160, TX), 540, 820, 1, "ct")
        hand(f, 790, 1050, 0.95, wr=1, t=t, face_on=False)
        # wet marble grabbed
        g = ease((lt - 1.2) / 0.6)
        K.circle(f, 790, lerp(1300, 760, g), 55, TQ)
        cv2.circle(f, (775, int(lerp(1300, 760, g) - 18)), 14, bgr(WH), -1, cv2.LINE_AA)
        text(f, "like tire", 70, 190, "fredoka-700", 120, TX, lt)
        K.rect(f, 60, 340, 560, 490, BU, 40); text(f, "treads", 100, 348, "fredoka-700", 120, TX, lt, 0.3)
        if lt > 2.2: K.rect(f, 620, 1250, 980, 1370, CO, 40); text(f, "GRIP!", 800, 1258, "fredoka-700", 96, WH, lt, 2.2, anchor="ct", pop=True)
        chrome(f, "5", "the theory")
    else:
        bg(f, TQ, t)
        for k, (x, y) in enumerate(((160, 700), (920, 760), (180, 1300), (900, 1250))): daisy(f, x, y, 1.6, t + k)
        hand(f, 540, 1180, 1.4, wr=1, t=t, wave=1)
        text(f, "built-in", 70, 190, "fredoka-700", 130, TX, lt)
        K.rect(f, 60, 360, 920, 520, CO, 40); text(f, "GRIP UPGRADE", 95, 370, "fredoka-700", 120, WH, lt, 0.4, pop=True)
        if lt > dur - 1.8:
            K.rect(f, 200, 1690, 880, 1800, WH, 50)
            paste(f, text_img("follow for more why's", "quicksand-700", 52, TX), 540, 1715, ease((lt - dur + 1.8) / 0.4), "ct")
        chrome(f, "6", "you're welcome")
    captions(f, t, tl, LINES, CAP, skip=(0,))
    return f

run(D, tl, frame, "wrinkly_fingers_daisy", "bubbly", 112, [(0.6, "splash"), (tl.starts[1] + 1.4, "pop"), (tl.starts[4] + 2.2, "pop"), (tl.starts[5] + 0.4, "ding")])
