import sys; sys.path.insert(0, "/home/claude/shorts")
from lib import *
D = "/home/claude/shorts/v7"
LINES = ["How do you build a skyscraper that doesn't fall over?",
         "Start deep. Long piles are driven down until they reach solid rock.",
         "Then a steel skeleton carries the weight, not the walls.",
         "But the wind pushes the top sideways! So add a super strong concrete core.",
         "Still swaying? Hang a giant heavy ball near the top. It swings against the sway and calms the whole tower.",
         "Stack it floor by floor, and you've got a skyscraper!"]
tl = Timeline(D)
CR, CR2, INK, INK2, GN, PK, OR, YE = "#EFE9D9", "#E4DCC4", "#0F0F0F", "#2A2A2A", "#1F8A4C", "#F06CA8", "#E85A1F", "#F5C518"
GL = "#9fd3e6"
B = Ink(INK, 6, INK, (12, 12)); B2 = Ink(INK, 5)
CAP = dict(font="archivo-black-400", size=66, col=INK, hi=OR, plate=CR, y=1540, outline=INK, ow=6, shadow=INK, sh=(12, 12), upper=True)

def grid_bg(f):
    f[:] = bgr(CR)
    for x in range(0, W, 90): cv2.line(f, (x, 0), (x, H), bgr(CR2), 2)
    for y in range(0, H, 90): cv2.line(f, (0, y), (W, y), bgr(CR2), 2)

def chrome(f, num, tag):
    paste(f, text_img(f"// {num}_{tag.upper()}", "jetbrains-mono-700", 32, INK, 0.04), 60, 70)
    B2.rect(f, W - 200, 66, W - 60, 116, YE); paste(f, text_img("BUILD", "jetbrains-mono-700", 28, INK), W - 130, 74, 1, "ct")

def title(f, lines, x, y, lt, cols, size=120, delay=0.0):
    yy = y
    for k, (s, c) in enumerate(zip(lines, cols)):
        p = ease((lt - delay - k * 0.12) / 0.35)
        img = text_img(s, "archivo-black-400", size, c)
        if p > 0: paste(f, img, x + (1 - p) * -60, yy, p)
        yy += int(size * 1.0)

def worker(f, x, y, s, t, mood="smile", arm=0.0):
    B2.rect(f, x - 45 * s, y - 20 * s, x + 45 * s, y + 90 * s, OR, int(20 * s))
    B2.circle(f, x, y - 70 * s, 50 * s, "#f2c9a0")
    B2.ellipse(f, x, y - 105 * s, 60 * s, 35 * s, YE, 0, 180, 360); B2.rect(f, x - 70 * s, y - 108 * s, x + 70 * s, y - 96 * s, YE)
    face(f, x, y - 70 * s, 0.75 * s, mouth=mood, blink=blink_at(t, 7), t=t)
    a = math.sin(t * 6) * 30 * arm
    cv2.line(f, (int(x + 40 * s), int(y)), (int(x + 40 * s + 60 * s * math.cos(math.radians(-60 + a))), int(y + 60 * s * math.sin(math.radians(-60 + a)))), bgr(OR), int(22 * s), cv2.LINE_AA)

def tower(f, cx, base, w, h, floors, lean=0.0, core=False, damper=None, t=0.0, glass=True):
    """lean in px at top (shear); draws frame floors"""
    def P(x, y):  # y from base upward
        return (cx + x + lean * (y / h) ** 2, base - y)
    pts = [P(-w / 2, 0), P(w / 2, 0), P(w / 2, h), P(-w / 2, h)]
    B.poly(f, pts, GL if glass else CR2)
    for k in range(1, floors):
        y = h * k / floors
        a, b = P(-w / 2, y), P(w / 2, y)
        cv2.line(f, (int(a[0]), int(a[1])), (int(b[0]), int(b[1])), bgr(INK), 4, cv2.LINE_AA)
    for xx in (-w / 4, 0, w / 4):
        pl = [P(xx, y) for y in np.linspace(0, h, 12)]
        cv2.polylines(f, [np.array(pl, np.int32)], False, bgr(INK), 3, cv2.LINE_AA)
    if core:
        pl = [P(-w * 0.12, y) for y in np.linspace(0, h, 12)] + [P(w * 0.12, y) for y in np.linspace(h, 0, 12)]
        B2.poly(f, pl, "#b9b2a0")
    if damper is not None:
        top = P(0, h * 0.92); bx = top[0] + damper * 60; by = top[1] + 110
        cv2.line(f, (int(top[0]), int(top[1])), (int(bx), int(by)), bgr(INK), 6, cv2.LINE_AA)
        B2.circle(f, bx, by, 48, YE)
    return P

def wind(f, t, y0, y1, strength=1.0):
    for k in range(7):
        q = (t * 0.9 + k / 7) % 1
        x = -200 + q * 1400; y = y0 + (y1 - y0) * (k / 7)
        cv2.line(f, (int(x), int(y)), (int(x + 160 * strength), int(y)), bgr(INK2), 6, cv2.LINE_AA)
        cv2.ellipse(f, (int(x + 160 * strength), int(y - 18)), (18, 18), 0, 90, 360, bgr(INK2), 6, cv2.LINE_AA)

def frame(t):
    i, lt, dur = tl.which(t)
    f = np.zeros((H, W, 3), np.uint8); grid_bg(f)
    if i == 0:
        cv2.rectangle(f, (0, 1420), (W, H), bgr(INK2), -1)
        lean = 120 * math.sin(t * 2.2)
        tower(f, 560, 1420, 260, 900, 14, lean, t=t)
        wind(f, t, 600, 1000)
        worker(f, 220, 1330, 1.0, t, mood="o")
        title(f, ["HOW DO", "SKYSCRAPERS", "NOT FALL?"], 60, 170, lt, [INK, OR, INK], 112)
    elif i == 1:
        layers = [(1000, "#c9a97a", "SOIL"), (1200, "#a0805a", "CLAY"), (1420, "#6d6d6d", "BEDROCK")]
        top = 860
        cv2.rectangle(f, (0, top), (W, 1000), bgr("#d8bf94"), -1)
        prev = top
        for yb, col, lab in layers:
            cv2.rectangle(f, (0, prev), (W, yb), bgr(col), -1); cv2.line(f, (0, prev), (W, prev), bgr(INK), 4)
            paste(f, text_img(lab, "jetbrains-mono-700", 30, INK), 40, prev + 20); prev = yb
        cv2.rectangle(f, (0, prev), (W, H), bgr("#6d6d6d"), -1)
        for k, x in enumerate((360, 540, 720)):
            d = eio((lt - 0.3 - k * 0.4) / 2.4)
            bot = lerp(top - 120, 1260, d)
            hit = abs(math.sin(lt * 10 + k)) * 20
            B2.rect(f, x - 26, bot - 420, x + 26, bot, GN)
            if d < 1: B.rect(f, x - 60, bot - 420 - 80 - hit, x + 60, bot - 420 - hit, YE)
        worker(f, 900, 780, 0.9, t, arm=1)
        title(f, ["DIG DEEP.", "HIT ROCK."], 60, 180, lt, [INK, GN], 140)
        chrome(f, "01", "piles")
    elif i == 2:
        cv2.rectangle(f, (0, 1420), (W, H), bgr(INK2), -1)
        p = lt / 1.8
        cx, base, w, h = 540, 1420, 520, 760
        nfl = 8
        for k in range(nfl + 1):
            if k / nfl > p: break
            y = base - h * k / nfl
            B2.rect(f, cx - w / 2, y - 10, cx + w / 2, y + 10, OR)
        for xx in (-w / 2, -w / 6, w / 6, w / 2):
            hh = h * min(1, p)
            B2.rect(f, cx + xx - 12, base - hh, cx + xx + 12, base, OR)
        if lt > 2.0:
            for xx in (-w / 2, -w / 6, w / 6, w / 2):
                q = (lt * 0.8) % 1
                cv2.arrowedLine(f, (int(cx + xx), int(base - h + q * (h - 120))), (int(cx + xx), int(base - h + q * (h - 120) + 100)), bgr(PK), 10, cv2.LINE_AA, tipLength=0.35)
        title(f, ["STEEL", "SKELETON"], 60, 180, lt, [INK, OR], 140)
        chrome(f, "02", "frame")
    elif i == 3:
        cv2.rectangle(f, (0, 1420), (W, H), bgr(INK2), -1)
        has_core = lt > 2.2
        k = 1 if not has_core else max(0.25, 1 - (lt - 2.2) * 0.6)
        lean = 140 * k * (0.6 + 0.4 * math.sin(t * 2.5))
        tower(f, 540, 1420, 300, 900, 14, lean, core=has_core, t=t)
        wind(f, t, 520, 900, 1.3)
        title(f, ["WIND!"], 60, 180, lt, [INK], 170)
        if has_core: title(f, ["+ CONCRETE CORE"], 60, 380, lt, [PK], 80, 2.2)
        chrome(f, "03", "wind load")
    elif i == 4:
        cv2.rectangle(f, (0, 1420), (W, H), bgr(INK2), -1)
        damp = min(1, max(0, (lt - 1.6) / 1.0))
        amp = 90 * (1 - 0.75 * eio((lt - 2.4) / 3.0))
        sway = amp * math.sin(t * 2.5)
        tower(f, 540, 1420, 340, 950, 15, sway, core=True, damper=(-math.sin(t * 2.5) * damp * 1.0) if damp > 0 else None, t=t)
        if damp > 0:
            top = (540 + sway, 1420 - 950)
            B.rect(f, 680, 470, 1010, 560, YE)
            paste(f, text_img("MASS DAMPER", "jetbrains-mono-700", 34, INK), 845, 494, damp, "ct")
        title(f, ["GIANT", "BALL"], 60, 180, lt, [INK, OR], 150)
        chrome(f, "04", "damper")
    else:
        cv2.rectangle(f, (0, 1420), (W, H), bgr(INK2), -1)
        nfl = int(4 + 12 * eio(lt / (dur * 0.7)))
        h = nfl * 52
        tower(f, 460, 1420, 280, h, nfl, 0, core=True, t=t)
        # crane
        cx = 800
        B2.rect(f, cx - 14, 1420 - h - 220, cx + 14, 1420, YE)
        B2.rect(f, cx - 380, 1420 - h - 240, cx + 160, 1420 - h - 210, YE)
        cv2.line(f, (cx - 300, 1420 - h - 210), (cx - 300, 1420 - h - 60), bgr(INK), 4)
        worker(f, 900, 1330, 0.9, t, arm=1)
        if lt > 1.0: title(f, ["SKYSCRAPER", "DONE."], 60, 180, lt, [INK, GN], 130, 1.0)
        if lt > dur - 1.8:
            B.rect(f, 160, 1700, 920, 1800, PK)
            paste(f, text_img("FOLLOW FOR THE NEXT BUILD", "jetbrains-mono-700", 38, INK), 540, 1728, ease((lt - dur + 1.8) / 0.4), "ct")
        chrome(f, "05", "stack")
    captions(f, t, tl, LINES, CAP, skip=(0,))
    return f

run(D, tl, frame, "skyscraper_creative", "lofi", 96, [(tl.starts[1] + 0.6, "boom"), (tl.starts[1] + 1.4, "boom"), (tl.starts[3] + 2.2, "pop"), (tl.starts[5] + 2.0, "ding")])
