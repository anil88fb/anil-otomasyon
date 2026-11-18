import sys; sys.path.insert(0, "/home/claude/shorts")
from lib import *
D = "/home/claude/shorts/v10"
LINES = ["Why can't you tickle yourself?",
         "Go on, try it. It just doesn't work!",
         "Your brain predicts what every move you make will feel like, before you even make it.",
         "So when your own fingers touch you, it already knows, and turns the feeling down.",
         "But when someone else does it, it's a surprise. And surprise is what makes it tickle.",
         "Your brain is basically spoiling the joke!"]
tl = Timeline(D)
PA, PD, SUN, SUNS, HZ, INK, EM = "#E9E5DB", "#DCD6C4", "#F1EE2E", "#F8F39B", "#F0DA7C", "#1B2566", "#E26B4A"
NO = Ink(); L = Ink(INK, 4)
CAP = dict(font="archivo-800", size=72, col=INK, hi=EM, plate=SUN, y=1530, radius=0)

def bloom(f, x, y, r, a=0.9):
    ov = f.copy(); cv2.circle(ov, (int(x), int(y)), int(r), bgr(SUN), -1, cv2.LINE_AA)
    cv2.addWeighted(ov, a, f, 1 - a, 0, f)

def chrome(f, num, label):
    paste(f, text_img(f"{num:02d}", "jetbrains-mono-500", 30, INK, 0.08), 70, 80)
    paste(f, text_img(label.upper(), "archivo-600", 26, INK, 0.3), 140, 84)
    cv2.line(f, (70, 130), (W - 70, 130), bgr(INK), 2, cv2.LINE_AA)
    cv2.line(f, (70, H - 90), (W - 70, H - 90), bgr(INK), 2, cv2.LINE_AA)

def kid(f, x, y, s, t, mood="smile", laugh=0.0, arm=None):
    shake = math.sin(t * 30) * 8 * laugh
    x += shake
    L.rect(f, x - 120 * s, y, x + 120 * s, y + 330 * s, PA, int(110 * s))
    L.circle(f, x, y - 90 * s, 120 * s, SUNS)
    if laugh > 0.3:
        for sx in (-1, 1): cv2.ellipse(f, (int(x + sx * 42 * s), int(y - 105 * s)), (int(20 * s), int(12 * s)), 0, 200, 340, bgr(INK), max(3, int(7 * s)), cv2.LINE_AA)
        L.ellipse(f, x, y - 50 * s, 45 * s, 34 * s, EM, 0, 0, 180)
    else:
        face(f, x, y - 105 * s, 1.6 * s, eye=INK, mouth=mood, blink=blink_at(t, 8), t=t)
    if arm is not None:
        ax, ay = arm
        cv2.line(f, (int(x + 100 * s), int(y + 60 * s)), (int(ax), int(ay)), bgr(INK), int(26 * s), cv2.LINE_AA)
        cv2.circle(f, (int(ax), int(ay)), int(24 * s), bgr(SUNS), -1, cv2.LINE_AA); cv2.circle(f, (int(ax), int(ay)), int(24 * s), bgr(INK), 4, cv2.LINE_AA)

def feather(f, x, y, ang, s=1.0):
    a = math.radians(ang); dx, dy = math.cos(a), math.sin(a)
    tip = (x + dx * 200 * s, y + dy * 200 * s)
    cv2.line(f, (int(x), int(y)), (int(tip[0]), int(tip[1])), bgr(INK), 5, cv2.LINE_AA)
    for k in range(10):
        u = 0.25 + k * 0.075; px, py = x + dx * 200 * s * u, y + dy * 200 * s * u
        for sgn in (-1, 1):
            cv2.line(f, (int(px), int(py)), (int(px - dy * 50 * s * sgn + dx * 20), int(py + dx * 50 * s * sgn + dy * 20)), bgr(EM), 4, cv2.LINE_AA)

def brain(f, x, y, s, t, mood="smile"):
    L.ellipse(f, x, y, 230 * s, 170 * s, "#f2c6d0")
    for k in range(5): cv2.ellipse(f, (int(x - 160 * s + k * 80 * s), int(y - 30 * s)), (int(40 * s), int(70 * s)), 0, 200, 340, bgr(INK), 4, cv2.LINE_AA)
    cv2.line(f, (int(x), int(y - 160 * s)), (int(x), int(y + 160 * s)), bgr(INK), 4, cv2.LINE_AA)
    face(f, x, y + 40 * s, 1.5 * s, eye=INK, mouth=mood, blink=blink_at(t, 9), t=t)

def slider(f, x, y, val, label):
    cv2.line(f, (x, y), (x + 600, y), bgr(INK), 6, cv2.LINE_AA)
    cv2.rectangle(f, (x, y - 14), (int(x + 600 * val), y + 14), bgr(EM), -1)
    L.circle(f, x + 600 * val, y, 34, SUN)
    paste(f, text_img(label, "jetbrains-mono-500", 30, INK, 0.08), x, y - 80)
    paste(f, text_img(f"{int(val * 100)}%", "jetbrains-mono-500", 44, INK), x + 620, y - 30)

def title(f, s, x, y, lt, size=130, delay=0.0, col=INK): text(f, s, x, y, "instrument-serif-400", size, col, lt, delay)

def frame(t):
    i, lt, dur = tl.which(t)
    f = np.zeros((H, W, 3), np.uint8); f[:] = bgr(PA)
    if i == 0:
        bloom(f, 540, 1050, 420)
        kid(f, 540, 1000, 1.3, t, laugh=0.0, mood="o")
        feather(f, 830, 1280, 200 + math.sin(t * 8) * 12, 1.2)
        title(f, "Why can't you", 70, 180, lt, 140)
        title(f, "tickle yourself?", 70, 340, lt, 140, 0.2)
    elif i == 1:
        bloom(f, 540, 1050, 330, 0.6)
        wig = math.sin(t * 14) * 30
        kid(f, 540, 950, 1.2, t, mood="flat", arm=(560 + wig, 1240))
        title(f, "Try it.", 70, 200, lt, 160)
        title(f, "…nothing.", 70, 380, lt, 160, 1.4, EM)
        chrome(f, 1, "experiment")
    elif i == 2:
        brain(f, 540, 650, 1.0, t)
        # prediction timeline
        y = 1180
        cv2.line(f, (120, y), (960, y), bgr(INK), 3, cv2.LINE_AA)
        p = ease((lt - 0.6) / 2.0)
        bloom(f, 330, y - 90, 90, 0.9); paste(f, text_img("PREDICT", "archivo-800", 36, INK, 0.1), 330, y - 110, 1, "ct")
        if p > 0.5:
            bloom(f, 760, y - 90, 90, 0.6); paste(f, text_img("TOUCH", "archivo-800", 36, INK, 0.1), 760, y - 110, 1, "ct")
        cv2.circle(f, (int(lerp(120, 960, p)), y), 14, bgr(EM), -1, cv2.LINE_AA)
        cv2.line(f, (540, 820), (330, y - 180), bgr(INK), 2, cv2.LINE_AA)
        title(f, "It knows first.", 70, 180, lt, 130)
        chrome(f, 2, "prediction")
    elif i == 3:
        kid(f, 300, 900, 0.9, t, mood="flat", arm=(380 + math.sin(t * 14) * 20, 1120))
        v = lerp(1.0, 0.15, eio((lt - 1.0) / 2.0))
        slider(f, 200, 1330, v, "TICKLE FEELING")
        brain(f, 780, 760, 0.6, t, "smile")
        title(f, "Volume: down.", 70, 180, lt, 130)
        chrome(f, 3, "turned down")
    elif i == 4:
        bloom(f, 540, 1000, 450)
        surprise = lt > 1.2
        kid(f, 420, 950, 1.1, t, laugh=1.0 if surprise else 0.0, mood="o")
        fx = lerp(1200, 760, ease((lt - 0.3) / 0.8))
        feather(f, fx, 1250, 200 + math.sin(t * 10) * 15, 1.3)
        slider(f, 200, 1420, 1.0 if surprise else 0.15, "TICKLE FEELING")
        if surprise:
            for k in range(3):
                paste(f, text_img("ha!", "instrument-serif-400", 90 + k * 20, EM), 700 + k * 90, 650 - k * 90 + math.sin(t * 8 + k) * 10)
        title(f, "Surprise!", 70, 180, lt, 160)
        chrome(f, 4, "someone else")
    else:
        bloom(f, 540, 950, 380)
        brain(f, 540, 950, 1.1, t, "talk")
        NO.rect(f, 620, 680, 960, 770, EM)
        paste(f, text_img("SPOILER", "archivo-800", 54, PA, 0.14), 790, 695, 1, "ct")
        title(f, "Your brain", 70, 180, lt, 140)
        title(f, "spoils the joke.", 70, 330, lt, 140, 0.3, EM)
        if lt > dur - 1.8:
            paste(f, text_img("FOLLOW FOR A NEW WHY EVERY DAY", "archivo-800", 36, INK, 0.12), 540, 1720, ease((lt - dur + 1.8) / 0.4), "ct")
        chrome(f, 5, "verdict")
    captions(f, t, tl, LINES, CAP, skip=(0,))
    return f

run(D, tl, frame, "tickle_biennale", "lofi", 104, [(tl.starts[4] + 1.2, "pop"), (tl.starts[4] + 1.5, "pop"), (tl.starts[5] + 0.3, "ding")])
