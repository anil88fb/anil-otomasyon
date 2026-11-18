import sys; sys.path.insert(0, "/home/claude/shorts")
from lib import *
D = "/home/claude/shorts/v9"
LINES = ["How do you build a tunnel under the sea?",
         "Just dig through the seabed? The water floods right in.",
         "So engineers use a giant boring machine. It digs, and lines the walls with concrete rings as it goes.",
         "Or they build huge concrete tubes on land, float them out, and sink them into a trench.",
         "Seal the joints, pump the water out, and bury the tubes under rock.",
         "Now cars and trains can drive right under the waves!"]
tl = Timeline(D)
BG, BG2, TX, TX2, AC, LN = "#EDE8E0", "#E2DBD1", "#1A1A1A", "#5A5A5A", "#8A8178", "#B8B0A4"
WATER = "#d9d6cf"
CAP = dict(font="inter-600", size=70, col=TX2, hi=TX, plate=BG, y=1540, outline=LN, ow=3, radius=0)
SURF, BED = 760, 1180

def hl(f, a, b, col=TX, w=3): cv2.line(f, (int(a[0]), int(a[1])), (int(b[0]), int(b[1])), bgr(col), w, cv2.LINE_AA)

def chrome(f, num, label):
    paste(f, text_img(f"{num:02d} — {label.upper()}", "inter-600", 26, AC, 0.18), 70, 80)
    hl(f, (70, 125), (W - 70, 125), LN, 2)

def scene_base(f, t, trench=0.0):
    f[:] = bgr(BG)
    cv2.rectangle(f, (0, SURF), (W, BED), bgr(BG2), -1)
    pts = [(x, int(SURF + math.sin(x / 55 + t * 2) * 8)) for x in range(0, W + 20, 20)]
    cv2.polylines(f, [np.array(pts)], False, bgr(TX), 3, cv2.LINE_AA)
    bed = [(x, int(BED + math.sin(x / 140) * 18 + (trench * 120 if 300 < x < 780 else 0) * math.sin(min(1, max(0, (x - 300) / 480)) * math.pi))) for x in range(0, W + 20, 20)]
    cv2.fillPoly(f, [np.array(bed + [(W, H), (0, H)], np.int32)], bgr("#ddd5c8"), cv2.LINE_AA)
    cv2.polylines(f, [np.array(bed)], False, bgr(TX), 3, cv2.LINE_AA)
    for k in range(-H, W, 40):
        cv2.line(f, (k, H), (k + 400, H - 400), bgr("#d0c7b8"), 2, cv2.LINE_AA)
    cv2.rectangle(f, (0, 1450), (W, H), bgr("#ddd5c8"), -1)
    for x0 in range(0, W, 60):
        hl(f, (x0, 1300), (x0 + 30, 1300), LN, 2)

def ship(f, x, t):
    y = SURF - 10 + math.sin(t * 2) * 5
    pts = [(x - 90, y - 30), (x + 90, y - 30), (x + 65, y + 10), (x - 65, y + 10)]
    cv2.fillPoly(f, [np.array(pts, np.int32)], bgr(BG), cv2.LINE_AA); cv2.polylines(f, [np.array(pts, np.int32)], True, bgr(TX), 3, cv2.LINE_AA)
    cv2.rectangle(f, (int(x - 30), int(y - 70)), (int(x + 30), int(y - 30)), bgr(TX), 3, cv2.LINE_AA)

def fish(f, x, y, s, t):
    cv2.ellipse(f, (int(x), int(y)), (int(30 * s), int(14 * s)), 0, 0, 360, bgr(TX), 3, cv2.LINE_AA)
    cv2.line(f, (int(x - 30 * s), int(y)), (int(x - 48 * s), int(y - 12 * s)), bgr(TX), 3, cv2.LINE_AA)
    cv2.line(f, (int(x - 30 * s), int(y)), (int(x - 48 * s), int(y + 12 * s)), bgr(TX), 3, cv2.LINE_AA)
    cv2.circle(f, (int(x + 16 * s), int(y - 3 * s)), 3, bgr(TX), -1)

def tube(f, x0, x1, y, h=90, segs=6, fill=BG):
    cv2.rectangle(f, (int(x0), int(y - h / 2)), (int(x1), int(y + h / 2)), bgr(fill), -1)
    cv2.rectangle(f, (int(x0), int(y - h / 2)), (int(x1), int(y + h / 2)), bgr(TX), 3, cv2.LINE_AA)
    for k in range(1, segs): hl(f, (lerp(x0, x1, k / segs), y - h / 2), (lerp(x0, x1, k / segs), y + h / 2), AC, 2)

def car(f, x, y, s=1.0, col=TX):
    cv2.rectangle(f, (int(x - 40 * s), int(y - 18 * s)), (int(x + 40 * s), int(y + 10 * s)), bgr(col), 3, cv2.LINE_AA)
    cv2.circle(f, (int(x - 22 * s), int(y + 14 * s)), int(8 * s), bgr(col), 3, cv2.LINE_AA); cv2.circle(f, (int(x + 22 * s), int(y + 14 * s)), int(8 * s), bgr(col), 3, cv2.LINE_AA)

def title(f, lines, lt, y=190, size=92):
    for k, s in enumerate(lines):
        text(f, s, 70, y + k * int(size * 1.15), "playfair-display-400", size, TX, lt, k * 0.12)

def frame(t):
    i, lt, dur = tl.which(t)
    f = np.zeros((H, W, 3), np.uint8)
    if i == 0:
        scene_base(f, t); ship(f, 300 + lt * 40, t)
        for k in range(0, W, 40): hl(f, (k, 1330), (k + 20, 1330), TX, 3)
        car(f, (lt * 260) % (W + 200) - 100, 1310)
        fish(f, 700 + math.sin(t) * 40, 950, 1.2, t)
        title(f, ["How do you build", "a tunnel", "under the sea?"], lt)
    elif i == 1:
        scene_base(f, t)
        d = ease(lt / 1.0)
        cv2.rectangle(f, (480, BED - 5), (600, int(BED + 220 * d)), bgr(BG2), -1)
        cv2.rectangle(f, (480, BED - 5), (600, int(BED + 220 * d)), bgr(TX), 3)
        if lt > 1.0:
            for k in range(6):
                q = (lt * 1.2 + k / 6) % 1
                y = lerp(BED - 200, BED + 200, q)
                cv2.arrowedLine(f, (500 + k * 16, int(y)), (500 + k * 16, int(y + 50)), bgr(TX2), 3, cv2.LINE_AA, tipLength=0.4)
        if lt > 1.6:
            r = 140; c = (840, 520)
            cv2.circle(f, c, r, bgr(TX), 3, cv2.LINE_AA); hl(f, (c[0] - 90, c[1] - 90), (c[0] + 90, c[1] + 90), TX, 4); hl(f, (c[0] - 90, c[1] + 90), (c[0] + 90, c[1] - 90), TX, 4)
        title(f, ["Just dig?", "It floods."], lt)
        chrome(f, 1, "the problem")
    elif i == 2:
        scene_base(f, t)
        y = 1320; x = lerp(80, 860, eio(lt / dur))
        tube(f, 0, x - 70, y, 150, segs=max(1, int((x - 70) / 70)))
        for k, rr in enumerate((95, 70, 45)):
            cv2.circle(f, (int(x), y), rr, bgr(TX), 3, cv2.LINE_AA)
        for k in range(8):
            a = k / 8 * 2 * math.pi + lt * 3
            hl(f, (x, y), (x + math.cos(a) * 95, y + math.sin(a) * 95), TX, 3)
        for k in range(10):
            a = (k / 10) * 2 * math.pi
            cv2.circle(f, (int(x + 110 + (lt * 50 + k * 13) % 50), int(y + math.sin(a) * 60)), 4, bgr(AC), -1)
        title(f, ["The boring", "machine"], lt)
        paste(f, text_img("CUTS · LINES WITH CONCRETE RINGS", "inter-600", 26, AC, 0.18), 70, 480, ease((lt - 0.4) / 0.4))
        chrome(f, 2, "method one")
    elif i == 3:
        scene_base(f, t, trench=1.0)
        q = eio((lt - 0.4) / 1.6); s = eio((lt - 2.4) / 1.8)
        x0 = lerp(-500, 300, q); x1 = x0 + 480
        y = lerp(SURF - 20, BED + 75, s)
        tube(f, x0, x1, y, 90, 4)
        if s < 0.05:
            for k in range(3): hl(f, (x0 - 60 - k * 40, y - 20 + k * 20), (x0 - 20 - k * 40, y - 20 + k * 20), AC, 3)
        title(f, ["Float it.", "Sink it."], lt)
        chrome(f, 3, "method two")
    elif i == 4:
        scene_base(f, t, trench=1.0)
        y = BED + 75
        tube(f, 300, 780, y, 90, 4, fill=BG if lt > 1.6 else WATER)
        if lt < 1.6:
            for k in range(5):
                qq = (lt * 1.5 + k / 5) % 1
                cv2.circle(f, (int(340 + k * 90), int(y - qq * 200)), 8, bgr(TX2), 2, cv2.LINE_AA)
        r = eio((lt - 2.0) / 1.6)
        rng = np.random.default_rng(4)
        for k in range(int(70 * r)):
            xx, yy = rng.uniform(290, 790), rng.uniform(y - 80, y - 40)
            cv2.circle(f, (int(xx), int(yy)), int(rng.uniform(8, 16)), bgr(AC), -1, cv2.LINE_AA)
        title(f, ["Seal. Pump.", "Bury."], lt)
        chrome(f, 4, "finish")
    else:
        scene_base(f, t, trench=1.0)
        tube(f, -10, W + 10, BED + 75, 90, 12)
        for k in range(3): car(f, (lt * 300 + k * 380) % (W + 200) - 100, BED + 85, 0.9)
        for k in range(4): fish(f, (200 + k * 230 + lt * 60 * (1 if k % 2 else -1)) % W, 880 + k * 60, 1.0, t)
        ship(f, 760 - lt * 30, t)
        title(f, ["Drive under", "the waves."], lt)
        if lt > dur - 1.9:
            hl(f, (240, 1690), (840, 1690), TX, 2)
            paste(f, text_img("FOLLOW FOR THE NEXT BUILD", "inter-600", 36, TX, 0.16), 540, 1720, ease((lt - dur + 1.9) / 0.4), "ct")
        chrome(f, 5, "result")
    captions(f, t, tl, LINES, CAP, skip=(0,))
    return f

run(D, tl, frame, "underwater_tunnel_cartesian", "mystic", 80, [(tl.starts[1] + 1.0, "splash"), (tl.sc[3][0] + 2.4, "splash"), (tl.starts[4] + 2.0, "boom")])
